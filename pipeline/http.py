"""A small HTTP client on urllib: retries with backoff, a polite User-Agent, and GitHub auth."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from urllib.parse import urlencode

USER_AGENT = "open-data-pulse/1.0 (+https://github.com/Pranavmodem/open-data-pulse)"
RETRY_STATUSES = {429, 500, 502, 503, 504}


def get(url: str, params: dict | None = None, *, body: dict | None = None,
        retries: int = 3, timeout: float = 30) -> bytes:
    """GET `url` (or POST `body` as JSON) and return the raw response bytes.

    Retries rate limits, server errors and network errors with exponential backoff,
    honouring Retry-After when the server sends one.
    """
    if params:
        url = f"{url}?{urlencode(params)}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=data, headers=headers)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in RETRY_STATUSES or attempt == retries:
                raise
            delay = _retry_after(exc) or 2 ** (attempt + 1)
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries:
                raise
            delay = 2 ** (attempt + 1)
        time.sleep(delay)
    raise AssertionError("unreachable")


def get_json(url: str, params: dict | None = None, **kwargs):
    return json.loads(get(url, params, **kwargs))


def github_graphql(query: str, variables: dict) -> dict:
    """Run a GitHub GraphQL query. Needs GITHUB_TOKEN, which Actions provides."""
    if not os.environ.get("GITHUB_TOKEN"):
        raise RuntimeError("GITHUB_TOKEN is not set")
    payload = get_json("https://api.github.com/graphql", body={"query": query, "variables": variables})
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "GraphQL error"))
    return payload["data"]


def _retry_after(exc: urllib.error.HTTPError) -> float | None:
    value = exc.headers.get("Retry-After") if exc.headers else None
    try:
        return min(float(value), 60) if value else None
    except ValueError:
        return None
