# src/terminal_ai_co_agent/utils/types.py
"""Common type definitions shared across utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FileInfo:
    """Information about a file."""

    path: Path
    size: int
    modified: str
    hash: str = ""
    encoding: str = "utf-8"
    is_binary: bool = False

