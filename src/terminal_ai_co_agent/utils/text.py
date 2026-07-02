# src/terminal_ai_co_agent/utils/text.py
"""Text processing utilities."""

from __future__ import annotations

import re


def truncate(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text[:50]


def extract_keywords(text: str, min_length: int = 3) -> list[str]:
    """Extract meaningful keywords from text."""
    words = re.findall(r"\b\w+\b", text.lower())
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "can", "shall",
        "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "and", "or", "not", "but", "if", "then", "else", "when",
        "this", "that", "these", "those", "it", "its",
    }
    return [w for w in words if len(w) >= min_length and w not in stopwords]


def count_tokens_approx(text: str) -> int:
    """Rough token count (1 token ≈ 4 characters)."""
    return len(text) // 4


def indent(text: str, spaces: int = 4) -> str:
    """Indent each line of text."""
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line for line in text.splitlines())

