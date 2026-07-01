"""Terminal AI Co-Agent — CLI Application Entry Point."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from terminal_ai_co_agent import __version__
from terminal_ai_co_agent.config.loader import load_config, write_default_config
from terminal_ai_co_agent.config.types import CoAgentConfig
from terminal_ai_co_agent.logging.logger import configure_logging, get_logger
from terminal_ai_co_agent.logging.audit import init_audit

# ── CLI Application ──────────────────────────────────────────────────

app = typer.Typer(
    name="coagent",
    help="Terminal AI Co-Agent — Intelligent software engineering partner",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()
logger = get_logger(__name__)

# Global state
_config: CoAgentConfig | None = None


def get_config() -> CoAgentConfig:
    """Get the loaded configuration (initialized on first CLI invocation)."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


# ── Callbacks ────────────────────────────────────────────────────────


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", help="Show version and exit"),
    ] = False,
    config_path: Annotated[
        Optional[Path],
        typer.Option("--config", "-c", help="Path to configuration file"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress non-error output"),
    ] = False,
) -> None:
    """Terminal AI Co-Agent — Intelligent software engineering partner."""
    if version:
        console.print(f"coagent v{__version__}")
        raise typer.Exit()

    # Load configuration
    global _config
    _config = load_config(config_path=config_path)

    # Configure logging
    log_level = "DEBUG" if verbose else _config.logging.level.value
    configure_logging(
        level=log_level,  # type: ignore[arg-type]
        json_format=_config.logging.json_format,
        log_directory=_config.logging.directory,
    )

    # Initialize audit
    init_audit(
        audit_dir=_config.logging.directory if _config.logging.audit else None,
        enabled=_config.logging.audit,
    )

    logger.info("cli.start", version=__version__, config_source=str(config_path or "auto"))

    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None:
        _show_welcome()


def _show_welcome() -> None:
    """Display welcome panel."""
    config = get_config()
    provider = config.general.default_provider
    single = "single-model" if config.general.single_model_mode else "multi-model"

    panel = Panel.fit(
        f"[bold cyan]Terminal AI Co-Agent[/bold cyan] v{__version__}\n\n"
        f"[dim]Mode:[/dim] {single}\n"
        f"[dim]Provider:[/dim] {provider}\n"
        f"[dim]Orchestrator:[/dim] {'enabled' if config.orchestrator.enabled else 'disabled'}\n\n"
        f"[dim]Run[/dim] [bold]coagent --help[/bold] [dim]for available commands[/dim]",
        title="Welcome",
        border_style="cyan",
    )
    console.print(panel)


# ── Commands ─────────────────────────────────────────────────────────


@app.command()
def init(
    path: Annotated[
        Path,
        typer.Argument(help="Directory to initialize"),
    ] = Path("."),
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing config"),
    ] = False,
) -> None:
    """Initialize coagent in a project directory."""
    config_file = path / ".coagent.toml"

    if config_file.exists() and not force:
        console.print(f"[yellow]Config already exists: {config_file}[/yellow]")
        console.print("Use --force to overwrite.")
        raise typer.Exit(1)

    write_default_config(config_file)
    console.print(f"[green]✓[/green] Initialized coagent config at {config_file}")

    # Create supporting directories
    dirs_to_create = [
        path / ".coagent" / "cache",
        path / ".coagent" / "memory",
        path / ".coagent" / "logs",
        path / ".coagent" / "vectors",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created {d}")

    console.print("\n[bold]Next:[/bold] Run [cyan]coagent ask[/cyan] to start interacting.")


@app.command()
def ask(
    query: Annotated[
        str,
        typer.Argument(help="Natural language query or task description"),
    ],
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Model to use (overrides config)"),
    ] = None,
    files: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help="Specific files to include in context"),
    ] = None,
) -> None:
    """Ask the Co-Agent a question or request a task."""
    config = get_config()
    console.print(f"[bold cyan]Ask:[/bold cyan] {query}")

    if files:
        console.print("[dim]Including files:[/dim]")
        for f in files:
            console.print(f"  • {f}")

    # TODO: Integrate with orchestrator
    console.print("[yellow]Orchestrator integration pending...[/yellow]")
    logger.info("cli.ask", query=query, model=model, files=files)


@app.command()
def plan(
    task: Annotated[
        str,
        typer.Argument(help="Task to plan"),
    ],
    auto_approve: Annotated[
        bool,
        typer.Option("--auto-approve", "-y", help="Skip approval prompts"),
    ] = False,
) -> None:
    """Generate an execution plan for a task."""
    config = get_config()
    console.print(f"[bold cyan]Planning:[/bold cyan] {task}")

    if not auto_approve:
        console.print("[dim]Approval required. Use -y to auto-approve.[/dim]")

    # TODO: Integrate with planner
    console.print("[yellow]Planner integration pending...[/yellow]")
    logger.info("cli.plan", task=task, auto_approve=auto_approve)


@app.command()
def execute(
    plan_id: Annotated[
        Optional[str],
        typer.Argument(help="Plan ID to execute"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview changes without executing"),
    ] = False,
) -> None:
    """Execute an approved plan."""
    if dry_run:
        console.print("[bold yellow]DRY RUN — No changes will be made[/bold yellow]")

    # TODO: Integrate with executor
    console.print(f"[yellow]Executor integration pending... (plan_id={plan_id})[/yellow]")


@app.command()
def review(
    plan_id: Annotated[
        Optional[str],
        typer.Argument(help="Plan or commit to review"),
    ] = None,
) -> None:
    """Review recent changes or a specific plan."""
    # TODO: Integrate with review system
    console.print("[yellow]Review system pending...[/yellow]")


@app.command()
def rollback(
    steps: Annotated[
        int,
        typer.Argument(help="Number of steps to rollback", min=1),
    ] = 1,
    confirm: Annotated[
        bool,
        typer.Option("--confirm", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Rollback recent changes."""
    if not confirm:
        confirmed = typer.confirm(f"Rollback {steps} step(s)?")
        if not confirmed:
            console.print("[yellow]Rollback cancelled.[/yellow]")
            raise typer.Exit()

    # TODO: Integrate with rollback system
    console.print(f"[yellow]Rollback pending... ({steps} steps)[/yellow]")


@app.command()
def context(
    action: Annotated[
        str,
        typer.Argument(help="Action: show, refresh, clear"),
    ] = "show",
) -> None:
    """View and manage project context."""
    config = get_config()

    if action == "show":
        table = Table(title="Project Context")
        table.add_column("Source", style="cyan")
        table.add_column("Files", style="dim")
        table.add_row("Project Root", str(config.general.project_root))
        table.add_row("Config", "Loaded")
        # TODO: Show actual context
        console.print(table)
    elif action == "refresh":
        console.print("[green]✓[/green] Context refreshed")
    elif action == "clear":
        console.print("[green]✓[/green] Context cleared")
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show current project and agent status."""
    config = get_config()

    table = Table(title="Co-Agent Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")

    table.add_row("Version", __version__, "")
    table.add_row("Config", "Loaded", f"provider={config.general.default_provider}")
    table.add_row("Orchestrator", "Enabled" if config.orchestrator.enabled else "Disabled",
                  f"budget={config.orchestrator.context_budget}")
    table.add_row("Safety", f"mode={config.safety.approval_mode}",
                  f"rollback={'on' if config.safety.auto_rollback else 'off'}")
    table.add_row("Memory", config.memory.backend,
                  f"path={config.memory.path}")
    table.add_row("RAG", "Enabled" if config.rag.enabled else "Disabled",
                  f"chunk_size={config.rag.chunk_size}")

    console.print(table)


@app.command()
def config_cmd(
    action: Annotated[
        str,
        typer.Argument(help="Action: show, edit, path"),
    ] = "show",
) -> None:
    """View and manage coagent configuration."""
    config = get_config()

    if action == "show":
        import json
        console.print_json(json.dumps(config.model_dump(mode="json"), indent=2, default=str))
    elif action == "path":
        from terminal_ai_co_agent.config.loader import _find_config_file
        path = _find_config_file()
        if path:
            console.print(str(path))
        else:
            console.print("[yellow]No config file found — using defaults[/yellow]")
    elif action == "edit":
        from terminal_ai_co_agent.config.loader import _find_config_file
        path = _find_config_file()
        if path:
            console.print(f"Config file: {path}")
            console.print("[dim]Open this file in your editor to modify.[/dim]")
        else:
            console.print("[yellow]No config file found. Run 'coagent init' first.[/yellow]")
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        raise typer.Exit(1)


@app.command()
def plugin(
    action: Annotated[
        str,
        typer.Argument(help="Action: list, enable, disable"),
    ] = "list",
    plugin_name: Annotated[
        Optional[str],
        typer.Argument(help="Plugin name"),
    ] = None,
) -> None:
    """Manage coagent plugins."""
    # TODO: Integrate with plugin system
    if action == "list":
        console.print("[bold]Available plugins:[/bold]")
        console.print("  • code_review — Review code changes")
        console.print("  • lint_integration — Run linters")
        console.print("  • custom_commands — User-defined commands")
    elif action == "enable" and plugin_name:
        console.print(f"[green]✓[/green] Enabled plugin: {plugin_name}")
    elif action == "disable" and plugin_name:
        console.print(f"[yellow]Disabled plugin: {plugin_name}[/yellow]")
    else:
        console.print("[red]Invalid action or missing plugin name[/red]")
        raise typer.Exit(1)


@app.command()
def explain(
    target: Annotated[
        str,
        typer.Argument(help="File, function, or concept to explain"),
    ],
) -> None:
    """Explain code, architecture, or decisions."""
    config = get_config()
    console.print(f"[bold cyan]Explaining:[/bold cyan] {target}")
    # TODO: Integrate with explain engine
    console.print("[yellow]Explain engine pending...[/yellow]")


@app.command()
def docs_gen(
    target: Annotated[
        Optional[str],
        typer.Argument(help="Target: api, architecture, readme, changelog, all"),
    ] = "all",
) -> None:
    """Generate documentation."""
    console.print(f"[bold cyan]Generating docs:[/bold cyan] {target}")
    # TODO: Integrate with docs generator
    console.print("[yellow]Docs generation pending...[/yellow]")


@app.command()
def test_gen(
    target: Annotated[
        Optional[str],
        typer.Argument(help="File or module to generate tests for"),
    ] = None,
) -> None:
    """Generate tests for specified target."""
    console.print(f"[bold cyan]Generating tests:[/bold cyan] {target or 'all'}")
    # TODO: Integrate with test generator
    console.print("[yellow]Test generation pending...[/yellow]")


# ── Entry Point ──────────────────────────────────────────────────────


def main_cli() -> None:
    """Entry point for the CLI application."""
    try:
        app()
    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        sys.exit(130)
    except Exception as exc:
        logger.exception("cli.fatal_error", error=str(exc))
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
