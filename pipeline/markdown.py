"""Helpers that make untrusted feed text safe to drop into the README."""

from __future__ import annotations

import re

_SPECIAL = re.compile(r"([\\`*_\[\]<>|#])")


def text(value: object, limit: int = 120) -> str:
    """Collapse whitespace, trim to `limit` characters, and escape Markdown and HTML."""
    s = " ".join(str(value).split())
    if len(s) > limit:
        s = s[: limit - 1].rstrip() + "…"
    return _SPECIAL.sub(r"\\\1", s)


def link(label: object, url: str | None, limit: int = 120) -> str:
    if not url or not url.startswith(("https://", "http://")):
        return text(label, limit)
    return f"[{text(label, limit)}](<{url.replace('>', '%3E').replace(' ', '%20')}>)"


def number(value: float | int | None) -> str:
    """1234567 -> 1.2M, 12345 -> 12.3K."""
    if value is None:
        return "?"
    for size, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(value) >= size:
            return f"{value / size:.1f}{suffix}"
    return f"{value:g}"
