# tests/conftest.py
"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator

import pytest


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_project_dir(temp_dir: Path) -> Path:
    """Create a minimal sample project."""
    project = temp_dir / "sample_project"
    project.mkdir()

    # Create a simple Python package
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text('"""Sample package."""\n')
    (src / "main.py").write_text(
        '"""Main module."""\n\n'
        'def hello(name: str = "World") -> str:\n'
        '    """Say hello."""\n'
        '    return f"Hello, {name}!"\n\n'
        'if __name__ == "__main__":\n'
        '    print(hello())\n'
    )

    # Tests directory
    tests = project / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("")
    (tests / "test_main.py").write_text(
        '"""Tests for main module."""\n\n'
        'from src.main import hello\n\n'
        'def test_hello_default():\n'
        '    assert hello() == "Hello, World!"\n\n'
        'def test_hello_name():\n'
        '    assert hello("Alice") == "Hello, Alice!"\n'
    )

    # Config
    (project / "pyproject.toml").write_text(
        '[project]\nname = "sample"\nversion = "0.1.0"\n'
    )
    (project / "README.md").write_text("# Sample Project\n")

    return project


@pytest.fixture
def mock_ollama_response() -> dict[str, Any]:
    """Mock Ollama API response."""
    return {
        "model": "qwen2.5:1.5b",
        "message": {
            "role": "assistant",
            "content": "This is a mocked response from the AI model.",
        },
        "done": True,
        "done_reason": "stop",
        "prompt_eval_count": 50,
        "eval_count": 25,
    }


@pytest.fixture
async def temp_coagent_config(temp_dir: Path) -> Path:
    """Create a temporary coagent config."""
    config_path = temp_dir / ".coagent.toml"
    config_path.write_text("""\
[general]
default_provider = "ollama"
single_model_mode = true
project_root = "."

[models.default]
provider = "ollama"
model = "qwen2.5:1.5b"
temperature = 0.0
max_tokens = 1024

[safety]
approval_mode = "none"
auto_rollback = true

[logging]
level = "DEBUG"
directory = ".coagent/logs"
audit = false
json_format = false
metrics = false

[memory]
backend = "file"
path = ".coagent/memory"

[rag]
enabled = false

[plugins]
enabled = false

[execution]
dry_run = false
command_timeout = 30
""")
    return config_path
