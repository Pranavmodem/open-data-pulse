"""Rebuilds README.md from README.template.md and the run manifests."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pipeline.core import Source, recent_manifests
from pipeline.markdown import text

STATUS = {"ok": "✅ ok", "empty": "⚪ no rows", "failed": "❌ failed"}
HEALTH_DAYS = 14


def render(template: str, sources: list[Source], data_dir: Path) -> str:
    manifests = recent_manifests(data_dir, HEALTH_DAYS)
    latest = manifests[0] if manifests else {}
    results = {r["source"]: r for r in latest.get("results", [])}
    replacements = {
        "{{source_count}}": str(len(sources)),
        "{{updated}}": _when(latest.get("finished_at")),
        "{{digest}}": _digest(sources, results) if results else "_Waiting for the first run._",
        "{{status}}": _status_table(sources, results),
        "{{health}}": _health(manifests),
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    return template


def _digest(sources: list[Source], results: dict) -> str:
    sections: dict[str, list[str]] = {}
    for source in sources:
        result = results.get(source.name, {})
        line = result.get("highlight") or "_no data today_"
        sections.setdefault(source.category, []).append(f"- **{source.title}**: {line}")
    return "\n\n".join(f"### {category}\n\n" + "\n".join(lines) for category, lines in sections.items())


def _status_table(sources: list[Source], results: dict) -> str:
    lines = ["| Source | What it tracks | Rows | Status |", "| --- | --- | ---: | --- |"]
    for s in sources:
        r = results.get(s.name)
        status = STATUS.get(r["status"], r["status"]) if r else "not run yet"
        if r and r.get("error"):
            status += f" ({text(r['error'], 70)})"
        lines.append(f"| [`{s.name}`](data/{s.name}) | {text(s.description, 140)} [↗](<{s.homepage}>) "
                     f"| {r['rows'] if r else ''} | {status} |")
    return "\n".join(lines)


def _health(manifests: list[dict]) -> str:
    if not manifests:
        return "_No runs yet._"
    intro = f"Last {len(manifests)} runs, newest first." if len(manifests) > 1 else "First run."
    lines = [intro, "",
             "| Date | Sources ok | Rows | Failed |", "| --- | ---: | ---: | --- |"]
    for m in manifests:
        results = m.get("results", [])
        ok = sum(r["status"] == "ok" for r in results)
        failed = ", ".join(f"`{r['source']}`" for r in results if r["status"] == "failed") or "none"
        lines.append(f"| {m['run_date']} | {ok}/{len(results)} | {sum(r['rows'] for r in results):,} | {failed} |")
    return "\n".join(lines)


def _when(timestamp: str | None) -> str:
    if not timestamp:
        return "never"
    return datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M UTC")
