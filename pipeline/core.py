"""The source contract, the runner, and the partition and manifest writers."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
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
    failures: list[str]  # populated during a run by note_failure()

    def fetch(self, ctx: Context) -> list[dict]:
        raise NotImplementedError

    def highlight(self, rows: list[dict]) -> str:
        """One line of Markdown for the README digest."""
        return ""

    def note_failure(self, message: str) -> None:
        """Record one item that failed inside a multi-item fetch.

        `collect()` calls this so a source that lost 5 of its 16 items says so instead of
        reporting a clean run with a shorter list. The runner reads the recorded messages
        back through `failures` and marks the whole source `partial`.
        """
        self.__dict__.setdefault("failures", []).append(message)


@dataclass
class Result:
    source: str
    status: str  # ok | partial | empty | failed
    rows: int
    seconds: float
    highlight: str = ""
    error: str | None = None
    errors: list[str] = field(default_factory=list)  # items that failed inside the source
    expected: int | None = None  # rows + failed items, when the fetch is item-based


def run_source(source: Source, ctx: Context) -> Result:
    """Fetch one source and write its partition. Never raises: a failure becomes a 'failed' result."""
    start = time.monotonic()
    source.__dict__.pop("failures", None)  # a rerun in the same process starts clean
    try:
        rows = source.fetch(ctx)
        if rows:
            write_partition(ctx.data_dir, source.name, ctx.day, rows)
        else:
            remove_partition(ctx.data_dir, source.name, ctx.day)
    except Exception as exc:  # one broken feed must not stop the others
        return Result(source.name, "failed", 0, _since(start), error=f"{type(exc).__name__}: {exc}"[:300])
    try:
        highlight = source.highlight(rows) if rows else ""
    except Exception:
        highlight = ""
    errors: list[str] = list(getattr(source, "failures", []))
    status = _status(rows, errors)
    return Result(
        source.name, status, len(rows), _since(start), highlight,
        error="; ".join(errors)[:300] if errors and not rows else None,
        errors=errors,
        expected=len(rows) + len(errors) if errors else None,
    )


def _status(rows: list[dict], errors: list[str]) -> str:
    """ok = everything worked, partial = some items failed but rows were written, failed = nothing came back."""
    if rows:
        return "partial" if errors else "ok"
    return "failed" if errors else "empty"



def run_all(sources: Sequence[Source], ctx: Context, workers: int = 6) -> list[Result]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda s: run_source(s, ctx), sources))


def write_partition(data_dir: Path, source: str, day: date, rows: list[dict]) -> Path:
    """Write rows to data/<source>/dt=<day>/data.jsonl. Re-running a day replaces that day's file."""
    path = data_dir / source / f"dt={day}" / "data.jsonl"
    lines = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    _atomic_write(path, lines)
    return path


def remove_partition(data_dir: Path, source: str, day: date) -> None:
    """Drop a day's rows when a rerun returns none, so a stale file never outlives the run that wrote it."""
    path = data_dir / source / f"dt={day}" / "data.jsonl"
    path.unlink(missing_ok=True)
    try:
        path.parent.rmdir()  # only removes the day folder when it is now empty
    except OSError:
        pass


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def recent_manifests(data_dir: Path, limit: int) -> list[dict]:
    """The newest `limit` run manifests, newest first."""
    paths = sorted((data_dir / "_runs").glob("dt=*/manifest.json"), reverse=True)[:limit]
    return [read_manifest(p) for p in paths]


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _since(start: float) -> float:
    return round(time.monotonic() - start, 2)
