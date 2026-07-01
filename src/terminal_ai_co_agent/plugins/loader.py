"""Plugin discovery and loading."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from terminal_ai_co_agent.logging.logger import get_logger
from terminal_ai_co_agent.plugins.types import Plugin, PluginMetadata, PluginStatus

if TYPE_CHECKING:
    from terminal_ai_co_agent.config.types import PluginsConfig

logger = get_logger(__name__)


class PluginLoader:
    """Discovers and loads plugins from directories and entry points.

    Load order:
    1. Built-in plugins (from `plugins/` directory in package)
    2. User directory plugins (~/.config/coagent/plugins)
    3. Project-local plugins (./.coagent/plugins)
    4. Entry point plugins (installed packages)
    """

    def __init__(self, config: "PluginsConfig") -> None:
        self.config = config
        self._discovered: dict[str, Path] = {}
        self._loaded: dict[str, Plugin] = {}
        self._status: dict[str, PluginStatus] = {}

    # ── Discovery ───────────────────────────────────────────────

    async def discover_all(self) -> dict[str, Path]:
        """Discover all available plugins."""
        self._discovered.clear()

        # Search configured directories
        for directory in self.config.directories:
            expanded = Path(directory).expanduser().resolve()
            if expanded.exists():
                await self._discover_in_directory(expanded)

        # Search entry points
        await self._discover_entry_points()

        # Mark disabled plugins
        for name in self.config.disabled:
            if name in self._discovered:
                self._status[name] = PluginStatus.DISABLED

        logger.info("plugins.discovered", count=len(self._discovered), plugins=list(self._discovered.keys()))

        return dict(self._discovered)

    async def _discover_in_directory(self, directory: Path) -> None:
        """Discover plugins in a directory."""
        for entry in directory.iterdir():
            if entry.is_dir() and (entry / "plugin.py").exists():
                name = entry.name
                self._discovered[name] = entry / "plugin.py"
                self._status[name] = PluginStatus.DISCOVERED
                logger.debug("plugins.discovered_in_dir", name=name, path=str(entry))

    async def _discover_entry_points(self) -> None:
        """Discover plugins registered via entry points."""
        try:
            from importlib.metadata import entry_points

            eps = entry_points(group="coagent.plugins")
            for ep in eps:
                name = ep.name
                self._discovered[name] = Path(ep.value)  # Store as reference
                self._status[name] = PluginStatus.DISCOVERED
                logger.debug("plugins.discovered_entry_point", name=name)
        except Exception as exc:
            logger.warning("plugins.entry_points_error", error=str(exc))

    # ── Loading ─────────────────────────────────────────────────

    async def load_all(self) -> dict[str, Plugin]:
        """Load all discovered plugins."""
        for name in list(self._discovered.keys()):
            if name in self.config.disabled:
                continue
            try:
                await self.load(name)
            except Exception as exc:
                logger.error("plugins.load_error", name=name, error=str(exc))
                self._status[name] = PluginStatus.ERROR

        logger.info("plugins.loaded", count=len(self._loaded), plugins=list(self._loaded.keys()))
        return dict(self._loaded)

    async def load(self, name: str) -> Plugin:
        """Load a single plugin by name."""
        if name in self._loaded:
            return self._loaded[name]

        if name not in self._discovered:
            raise PluginNotFoundError(f"Plugin '{name}' not found. Run discover_all() first.")

        if name in self.config.disabled:
            raise PluginDisabledError(f"Plugin '{name}' is disabled.")

        source = self._discovered[name]
        self._status[name] = PluginStatus.LOADED

        # Determine loading method
        if isinstance(source, Path) and source.exists():
            plugin = await self._load_from_file(name, source)
        else:
            plugin = await self._load_from_entry_point(name, str(source))

        # Validate plugin
        if not isinstance(plugin, Plugin):
            raise PluginLoadError(f"Plugin '{name}' does not implement the Plugin protocol.")

        self._loaded[name] = plugin
        self._status[name] = PluginStatus.INITIALIZED

        logger.info("plugins.loaded_single", name=name, version=plugin.metadata.version)
        return plugin

    async def _load_from_file(self, name: str, path: Path) -> Plugin:
        """Load a plugin from a file path."""
        spec = importlib.util.spec_from_file_location(
            f"coagent_plugin_{name}",
            str(path),
        )
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"Could not load spec for plugin '{name}'")

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"coagent_plugin_{name}"] = module
        spec.loader.exec_module(module)

        # Find the plugin class
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and attr.__name__.endswith("Plugin")
                and hasattr(attr, "metadata")
            ):
                plugin_class = attr
                break

        if plugin_class is None:
            raise PluginLoadError(
                f"No plugin class found in {path}. "
                f"Create a class ending with 'Plugin' that has a 'metadata' property."
            )

        instance = plugin_class()
        await instance.initialize()
        return instance

    async def _load_from_entry_point(self, name: str, entry_point_ref: str) -> Plugin:
        """Load a plugin from an installed package entry point."""
        try:
            from importlib.metadata import entry_points

            eps = entry_points(group="coagent.plugins")
            for ep in eps:
                if ep.name == name:
                    plugin_class = ep.load()
                    instance = plugin_class()
                    await instance.initialize()
                    return instance

            raise PluginLoadError(f"Entry point '{name}' not found.")
        except Exception as exc:
            raise PluginLoadError(f"Failed to load entry point plugin '{name}': {exc}")

    # ── Management ──────────────────────────────────────────────

    async def unload(self, name: str) -> None:
        """Unload a plugin."""
        if name in self._loaded:
            plugin = self._loaded[name]
            await plugin.shutdown()
            del self._loaded[name]
            self._status[name] = PluginStatus.UNLOADED
            logger.info("plugins.unloaded", name=name)

    async def unload_all(self) -> None:
        """Unload all plugins."""
        for name in list(self._loaded.keys()):
            await self.unload(name)

    async def enable(self, name: str) -> None:
        """Enable a disabled plugin."""
        if name in self.config.disabled:
            self.config.disabled.remove(name)
            self._status[name] = PluginStatus.DISCOVERED
            await self.load(name)
            logger.info("plugins.enabled", name=name)

    async def disable(self, name: str) -> None:
        """Disable an active plugin."""
        if name in self._loaded:
            await self.unload(name)
        if name not in self.config.disabled:
            self.config.disabled.append(name)
        self._status[name] = PluginStatus.DISABLED
        logger.info("plugins.disabled", name=name)

    # ── Query ───────────────────────────────────────────────────

    def get(self, name: str) -> Plugin | None:
        """Get a loaded plugin by name."""
        return self._loaded.get(name)

    def get_all(self) -> dict[str, Plugin]:
        """Get all loaded plugins."""
        return dict(self._loaded)

    def get_status(self, name: str) -> PluginStatus:
        """Get the status of a plugin."""
        return self._status.get(name, PluginStatus.DISCOVERED)

    def list_available(self) -> list[dict[str, Any]]:
        """List all discovered plugins with status."""
        return [
            {
                "name": name,
                "status": self._status.get(name, PluginStatus.DISCOVERED).value,
                "loaded": name in self._loaded,
                "disabled": name in self.config.disabled,
            }
            for name in self._discovered
        ]

    @property
    def loaded_count(self) -> int:
        """Number of loaded plugins."""
        return len(self._loaded)

    @property
    def discovered_count(self) -> int:
        """Number of discovered plugins."""
        return len(self._discovered)


# ── Exceptions ───────────────────────────────────────────────────────


class PluginNotFoundError(Exception):
    """Plugin not found in discovered plugins."""
    pass


class PluginLoadError(Exception):
    """Failed to load a plugin."""
    pass


class PluginDisabledError(Exception):
    """Plugin is disabled."""
    pass
