"""The source contract, the runner, and the partition and manifest writers."""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Context:
    """What a source gets when it runs: the snapshot date and the data lake root."""

    day: date
    data_dir: Path

    def previous_rows(self, source: str) -> list[dict]:
        """Rows from the newest partition before `day`, or [] on a source's first run."""
        earlier = sorted(p for p in (self.data_dir / source).glob("dt=*") if p.name < f"dt={self.day}")
        return read_jsonl(earlier[-1] / "data.jsonl") if earlier else []


class Source:
    """One public feed. Subclasses set the metadata and implement fetch() and highlight()."""

    name: str
    title: str
    category: str
    description: str
    homepage: str

    def fetch(self, ctx: Context) -> list[dict]:
        raise NotImplementedError

    def highlight(self, rows: list[dict]) -> str:
        """One line of Markdown for the README digest."""
        return ""


@dataclass
class Result:
    source: str
    status: str  # ok | empty | failed
    rows: int
    seconds: float
    highlight: str = ""
    error: str | None = None


def run_source(source: Source, ctx: Context) -> Result:
    """Fetch one source and write its partition. Never raises: a failure becomes a 'failed' result."""
    start = time.monotonic()
    try:
        rows = source.fetch(ctx)
        if rows:
            write_partition(ctx.data_dir, source.name, ctx.day, rows)
    except Exception as exc:  # one broken feed must not stop the others
        return Result(source.name, "failed", 0, _since(start), error=f"{type(exc).__name__}: {exc}"[:300])
    try:
        highlight = source.highlight(rows) if rows else ""
    except Exception:
        highlight = ""
    return Result(source.name, "ok" if rows else "empty", len(rows), _since(start), highlight)


def run_all(sources: list[Source], ctx: Context, workers: int = 6) -> list[Result]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda s: run_source(s, ctx), sources))


def write_partition(data_dir: Path, source: str, day: date, rows: list[dict]) -> Path:
    """Write rows to data/<source>/dt=<day>/data.jsonl. Re-running a day replaces that day's file."""
    path = data_dir / source / f"dt={day}" / "data.jsonl"
    lines = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    _atomic_write(path, lines)
    return path


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def manifest_path(data_dir: Path, day: date) -> Path:
    return data_dir / "_runs" / f"dt={day}" / "manifest.json"


def write_manifest(data_dir: Path, day: date, results: list[Result], order: list[str]) -> dict:
    """Record the run. Results for sources not run this time are kept from an earlier run that day."""
    path = manifest_path(data_dir, day)
    merged = {r["source"]: r for r in read_manifest(path).get("results", [])}
    merged.update({r.source: asdict(r) for r in results})
    manifest = {
        "run_date": str(day),
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "results": sorted(merged.values(), key=lambda r: order.index(r["source"]) if r["source"] in order else len(order)),
    }
    _atomic_write(path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def read_manifest(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def recent_manifests(data_dir: Path, limit: int) -> list[dict]:
    """The newest `limit` run manifests, newest first."""
    paths = sorted((data_dir / "_runs").glob("dt=*/manifest.json"), reverse=True)[:limit]
    return [read_manifest(p) for p in paths]


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def _since(start: float) -> float:
    return round(time.monotonic() - start, 2)
