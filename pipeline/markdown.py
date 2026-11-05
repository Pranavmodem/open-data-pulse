"""Helpers that make untrusted feed text safe to drop into the README."""

from __future__ import annotations

import re
from urllib.parse import quote, urlsplit

_SPECIAL = re.compile(r"([\\`*_\[\]<>|#])")
_URL_SAFE = ":/?#[]@!$&'()*+,;=%~-._"


def text(value: object, limit: int = 120) -> str:
    """Collapse whitespace, trim to `limit` characters, and escape Markdown and HTML."""
    s = " ".join(str(value).split())
    if len(s) > limit:
        s = s[: limit - 1].rstrip() + "…"
    return _SPECIAL.sub(r"\\\1", s)


def link(label: object, url: str | None, limit: int = 120) -> str:
    """A Markdown link, or plain text when the URL isn't an absolute http(s) URL.

    Every character outside the URL-safe set is percent-encoded, so a feed URL holding
    newlines, '<', '>' or '\\' can't close the link and inject Markdown or HTML.
    """
    parts = urlsplit(url or "")
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return text(label, limit)
    return f"[{text(label, limit)}](<{quote(url, safe=_URL_SAFE)}>)"


def number(value: float | int | None) -> str:
    """1234567 -> 1.2M, 12345 -> 12.3K."""
    if value is None:
        return "?"
    for size, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(value) >= size:
            return f"{value / size:.1f}{suffix}"
    return f"{value:g}"
