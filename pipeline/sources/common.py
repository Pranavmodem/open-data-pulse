"""Shared fetch patterns: per-item collection and GitHub release lookups."""

from __future__ import annotations

import re
import urllib.error
from datetime import date, datetime
from typing import Callable, Iterable, TypeVar

from pipeline import http
from pipeline.markdown import link

T =TypeVar("T")

_PRERELEASE = re.compile(r"(rc|alpha|beta|preview|dev|snapshot|milestone)", re.IGNORECASE)

_TAGS_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    refs(refPrefix: "refs/tags/", first: 20, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {
      nodes {
        name
        target {
          ... on Commit { committedDate }
          ... on Tag { target { ... on Commit { committedDate } } }
        }
      }
    }
  }
}
"""


def collect(items: Iterable[T], fetch_one: Callable[[T], dict | None]) -> list[dict]:
    """Fetch each item on its own so one bad item is skipped; fail only if every item fails."""
    rows, errors = [], []
    for item in items:
        try:
            row = fetch_one(item)
        except Exception as exc:
            errors.append(f"{item}: {type(exc).__name__}: {exc}")
            continue
        if row:
            rows.append(row)
    if errors and not rows:
        raise RuntimeError("; ".join(errors)[:300])
    return rows


def latest_release(name: str, repo: str, day: date) -> dict:
    """The newest stable release of a GitHub repo, falling back to tags for projects without releases."""
    try:
        release = http.get_json(f"https://api.github.com/repos/{repo}/releases/latest")
        version, published, url = release["tag_name"], release["published_at"], release["html_url"]
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        version, published = _latest_stable_tag(repo)
        url = f"https://github.com/{repo}/releases/tag/{version}"
    return {
        "tool": name,
        "repo": repo,
        "version": version,
        "published_at": published,
        "days_since_release": (day - datetime.fromisoformat(published.replace("Z", "+00:00")).date()).days,
        "url": url,
    }


def _latest_stable_tag(repo: str) -> tuple[str, str]:
    owner, name = repo.split("/")
    refs = http.github_graphql(_TAGS_QUERY, {"owner": owner, "name": name})["repository"]["refs"]["nodes"]
    for ref in refs:
        target = ref["target"] or {}
        committed = target.get("committedDate") or (target.get("target") or {}).get("committedDate")
        if committed and not _PRERELEASE.search(ref["name"]):
            return ref["name"], committed
    raise LookupError(f"no stable tag in {repo}")


def release_highlight(rows: list[dict]) -> str:
    newest = min(rows, key=lambda r: r["days_since_release"])
    when = "today" if newest["days_since_release"] == 0 else f"{newest['days_since_release']}d ago"
    return f"Latest: {link(newest['tool'] + ' ' + newest['version'], newest['url'])} ({when})"
