"""Type definitions for deployment subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeploymentTarget(str, Enum):
    """Deployment target types."""

    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    CLOUD_RUN = "cloud_run"
    EC2 = "ec2"
    LAMBDA = "lambda"
    HEROKU = "heroku"
    LOCAL = "local"
    CUSTOM = "custom"


class DeploymentStatus(str, Enum):
    """Status of a deployment."""

    PREPARING = "preparing"
    BUILDING = "building"
    DEPLOYING = "deploying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentConfig:
    """Configuration for a deployment."""

    target: DeploymentTarget
    project_name: str
    environment: str = "production"
    region: str = ""
    resources: dict[str, Any] = field(default_factory=dict)
    env_vars: dict[str, str] = field(default_factory=dict)
    build_command: str = ""
    start_command: str = ""
    health_check_path: str = "/health"


@dataclass
class DeploymentResult:
    """Result of a deployment."""

    success: bool
    status: DeploymentStatus
    target: DeploymentTarget
    url: str = ""
    message: str = ""
    logs: str = ""
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
