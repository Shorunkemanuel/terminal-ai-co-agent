# src/terminal_ai_co_agent/utils/fs.py
"""Filesystem utilities."""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from typing import Any

from terminal_ai_co_agent.utils.types import FileInfo


def get_file_info(path: Path) -> FileInfo:
    """Get information about a file."""
    stat = path.stat()
    return FileInfo(
        path=path,
        size=stat.st_size,
        modified=str(stat.st_mtime),
        hash=hash_file(path) if path.is_file() else "",
        encoding="utf-8",
        is_binary=is_binary_file(path),
    )


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    """Compute the hash of a file."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def is_binary_file(path: Path) -> bool:
    """Check if a file is binary."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
        return b"\x00" in chunk
    except Exception:
        return True


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_copy(src: Path, dst: Path) -> Path:
    """Copy a file, creating parent directories if needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    return Path(shutil.copy2(str(src), str(dst)))


def find_files(
    directory: Path,
    pattern: str = "*",
    max_depth: int = 10,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """Find files matching a pattern."""
    import fnmatch

    exclude = exclude_patterns or []
    files: list[Path] = []

    for path in directory.rglob(pattern):
        # Check depth
        relative = path.relative_to(directory)
        if len(relative.parts) > max_depth:
            continue
        # Check exclusions
        if any(fnmatch.fnmatch(path.name, pat) for pat in exclude):
            continue
        if path.is_file():
            files.append(path)

    return files


def get_relative_path(path: Path, base: Path) -> Path:
    """Get a relative path, returning absolute if not under base."""
    try:
        return path.resolve().relative_to(base.resolve())
    except ValueError:
        return path.resolve()
