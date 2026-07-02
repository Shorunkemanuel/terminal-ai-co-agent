# src/terminal_ai_co_agent/ai/__init__.py
"""AI subsystem — provider abstraction, registry, and model management."""

from terminal_ai_co_agent.ai.registry import ProviderRegistry
from terminal_ai_co_agent.ai.types import AIProvider, CompletionRequest, CompletionResponse

__all__ = ["ProviderRegistry", "AIProvider", "CompletionRequest", "CompletionResponse"]
