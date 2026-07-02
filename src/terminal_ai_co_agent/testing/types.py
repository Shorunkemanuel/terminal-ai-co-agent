# src/terminal_ai_co_agent/testing/types.py
"""Type definitions for the testing subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class TestType(str, Enum):
    """Types of tests that can be generated."""

    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    EDGE_CASE = "edge_case"
    REGRESSION = "regression"


@dataclass
class TestCase:
    """A generated test case."""

    name: str
    description: str
    code: str
    type: TestType = TestType.UNIT
    target_function: str = ""
    expected_behavior: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    """A collection of generated tests for a module."""

    module_path: str
    test_file_path: Path
    test_cases: list[TestCase] = field(default_factory=list)
    imports: str = ""
    fixtures: list[str] = field(default_factory=list)
    framework: str = "pytest"
