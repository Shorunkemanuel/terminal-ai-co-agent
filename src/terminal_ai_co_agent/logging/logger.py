"""Structured logging setup using structlog."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
from structlog.types import Processor

if TYPE_CHECKING:
    from terminal_ai_co_agent.logging.types import LogLevel


def configure_logging(
    level: "LogLevel | str" = "INFO",
    json_format: bool = False,
    log_directory: Path | None = None,
) -> None:
    """Configure structured logging.

    Args:
        level: Minimum log level.
        json_format: If True, emit JSON lines. If False, colored console.
        log_directory: If set, also write logs to this directory.
    """
    from terminal_ai_co_agent.logging.types import LogLevel

    if isinstance(level, str):
        level = LogLevel(level)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json_format:
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, level.value, logging.INFO)
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(sys.stderr),
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, level.value, logging.INFO)
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(sys.stderr),
            cache_logger_on_first_use=True,
        )

    if log_directory is not None:
        log_directory.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_directory / "coagent.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        if json_format:
            file_handler.setFormatter(
                logging.Formatter(
                    '{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}'
                )
            )
        else:
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
        root_logger = logging.getLogger("terminal_ai_co_agent")
        root_logger.addHandler(file_handler)


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name or "terminal_ai_co_agent")
