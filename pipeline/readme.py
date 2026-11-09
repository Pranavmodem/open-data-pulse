"""Rebuilds README.md from README.template.md and the run manifests."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from pipeline.core import Source, recent_manifests
from pipeline.markdown import text

STATUS = {"ok": "✅ ok", "partial": "⚠️ partial", "empty": "⚪ no rows", "failed": "❌ failed"}
HEALTH_DAYS = 14
_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def render(template: str, sources: Sequence[Source], data_dir: Path) -> str:
    manifests = recent_manifests(data_dir, HEALTH_DAYS)
    latest = manifests[0] if manifests else {}
    results = {r["source"]: r for r in latest.get("results", [])}
    replacements = {
        "source_count": str(len(sources)),
        "updated": _when(latest.get("finished_at")),
        "digest": _digest(sources, results) if results else "_Waiting for the first run._",
        "status": _status_table(sources, results),
        "health": _health(manifests),
    }
    # One pass over the template: a feed title that happens to contain "{{health}}" stays
    # literal instead of being expanded with the health table.
    return _PLACEHOLDER.sub(lambda match: replacements.get(match.group(1), match.group(0)), template)


def _digest(sources: Sequence[Source], results: dict) -> str:
    sections: dict[str, list[str]] = {}
    for source in sources:
        result = results.get(source.name, {})
        line = result.get("highlight") or "_no data today_"
        if result.get("errors"):
            line += f" _({_count(len(result['errors']), result.get('expected'))} items failed)_"
        sections.setdefault(source.category, []).append(f"- **{source.title}**: {line}")
    return "\n\n".join(f"### {category}\n\n" + "\n".join(lines) for category, lines in sections.items())


def _status_table(sources: Sequence[Source], results: dict) -> str:
    lines = ["| Source | What it tracks | Rows | Status |", "| --- | --- | ---: | --- |"]
    for s in sources:
        r = results.get(s.name)
        lines.append(f"| [`{s.name}`](data/{s.name}) | {text(s.description, 140)} [↗](<{s.homepage}>) "
                     f"| {r['rows'] if r else ''} | {_status_cell(r)} |")
    return "\n".join(lines)


def _status_cell(result: dict | None) -> str:
    if not result:
        return "not run yet"
    status: str = result["status"]
    cell = STATUS.get(status, status)
    errors = result.get("errors") or []
    if errors:
        cell += f" ({_count(len(errors), result.get('expected'))} items failed: {text(errors[0], 60)})"
    elif result.get("error"):
        cell += f" ({text(result['error'], 70)})"
    return cell


def _count(failed: int, expected: int | None) -> str:
    return f"{failed} of {expected}" if expected else str(failed)


def _health(manifests: list[dict]) -> str:
    if not manifests:
        return "_No runs yet._"
    intro = f"Last {len(manifests)} runs, newest first." if len(manifests) > 1 else "First run."
    lines = [intro, "",
             "| Date | Sources ok | Rows | Problems |", "| --- | ---: | ---: | --- |"]
    for m in manifests:
        results = m.get("results", [])
        ok = sum(r["status"] == "ok" for r in results)
        problems = ([f"`{r['source']}` ⚠️" for r in results if r["status"] == "partial"]
                    + [f"`{r['source']}`" for r in results if r["status"] == "failed"])
        lines.append(f"| {m['run_date']} | {ok}/{len(results)} | {sum(r['rows'] for r in results):,} "
                     f"| {', '.join(problems) or 'none'} |")
    return "\n".join(lines)


def _when(timestamp: str | None) -> str:
    if not timestamp:
        return "never"
    return datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M UTC")
