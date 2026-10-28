"""Command line entry point: python -m pipeline.run [--date YYYY-MM-DD] [--only SOURCE ...] [--root DIR]"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from pipeline import readme
from pipeline.core import Context, Result, run_all, write_manifest
from pipeline.sources import SOURCES

REPO_ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Snapshot every public feed into date partitions.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT,
                        help="folder that receives data/ and README.md (default: the repo)")
    parser.add_argument("--date", type=date.fromisoformat, default=datetime.now(timezone.utc).date(),
                        help="snapshot date (default: today in UTC)")
    parser.add_argument("--only", nargs="+", metavar="SOURCE", help="run only these sources")
    parser.add_argument("--workers", type=int, default=6, help="sources fetched in parallel")
    args = parser.parse_args(argv)

    names = [s.name for s in SOURCES]
    unknown = sorted(set(args.only or []) - set(names))
    if unknown:
        parser.error(f"unknown source(s): {', '.join(unknown)}. Known: {', '.join(names)}")
    selected = [s for s in SOURCES if not args.only or s.name in args.only]

    data_dir = args.root / "data"
    results = run_all(selected, Context(args.date, data_dir), args.workers)
    write_manifest(data_dir, args.date, results, names)
    template = (REPO_ROOT / "README.template.md").read_text()
    (args.root / "README.md").write_text(readme.render(template, SOURCES, data_dir))

    ok = sum(r.status == "ok" for r in results)
    headline = f"{ok}/{len(results)} sources ok"
    print(_console_report(results), f"\n{headline}", sep="\n")
    _write_github_outputs(results, headline)
    return 0 if ok * 2 >= len(results) else 1


def _console_report(results: list[Result]) -> str:
    width = max(len(r.source) for r in results)
    return "\n".join(f"{r.status:<7} {r.source:<{width}} {r.rows:>5} rows {r.seconds:>6.1f}s"
                     + (f"  {r.error}" if r.error else "") for r in results)


def _write_github_outputs(results: list[Result], headline: str) -> None:
    """In GitHub Actions, expose the headline as a step output and write a job summary table."""
    if path := os.environ.get("GITHUB_OUTPUT"):
        with open(path, "a") as out:
            out.write(f"summary={headline}\n")
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        rows = "\n".join(f"| `{r.source}` | {r.status} | {r.rows} | {r.seconds:.1f}s | {(r.error or '').replace('|', '/')} |"
                         for r in results)
        with open(path, "a") as out:
            out.write(f"### {headline}\n\n| Source | Status | Rows | Time | Error |\n| --- | --- | ---: | ---: | --- |\n"
                      f"{rows}\n")


if __name__ == "__main__":
    sys.exit(main())
