"""Offline tests for the runner, the partition writer and the README renderer."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from pipeline import readme
from pipeline.core import Context, Source, read_jsonl, read_manifest, manifest_path, run_all, write_manifest
from pipeline.markdown import link, number, text
from pipeline.sources import SOURCES

DAY = date(2026, 10, 27)


class FakeSource(Source):
    category = "Test"
    homepage = "https://example.com"

    def __init__(self, name: str, rows: list[dict] | None = None, error: Exception | None = None):
        self.name = self.title = self.description = name
        self.rows, self.error = rows or [], error

    def fetch(self, ctx):
        if self.error:
            raise self.error
        return self.rows

    def highlight(self, rows):
        return f"{len(rows)} rows"


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(tempfile.mkdtemp())

    def test_writes_hive_partition(self):
        run_all([FakeSource("quakes", [{"mag": 5.1}, {"mag": 4.2}])], Context(DAY, self.data_dir))
        self.assertEqual(read_jsonl(self.data_dir / "quakes" / "dt=2026-10-27" / "data.jsonl"),
                         [{"mag": 5.1}, {"mag": 4.2}])

    def test_failure_is_isolated(self):
        results = run_all([FakeSource("good", [{"a": 1}]), FakeSource("bad", error=ValueError("boom")),
                           FakeSource("quiet")], Context(DAY, self.data_dir))
        self.assertEqual([(r.source, r.status, r.rows) for r in results],
                         [("good", "ok", 1), ("bad", "failed", 0), ("quiet", "empty", 0)])
        self.assertIn("ValueError: boom", results[1].error)
        self.assertEqual(results[0].highlight, "1 rows")

    def test_rerunning_a_day_replaces_its_partition(self):
        ctx = Context(DAY, self.data_dir)
        run_all([FakeSource("s", [{"v": 1}, {"v": 2}])], ctx)
        run_all([FakeSource("s", [{"v": 3}])], ctx)
        self.assertEqual(read_jsonl(self.data_dir / "s" / "dt=2026-10-27" / "data.jsonl"), [{"v": 3}])

    def test_previous_rows_reads_the_newest_earlier_partition(self):
        for day, value in ((date(2026, 10, 25), 25), (date(2026, 10, 26), 26), (DAY, 27)):
            run_all([FakeSource("s", [{"v": value}])], Context(day, self.data_dir))
        self.assertEqual(Context(DAY, self.data_dir).previous_rows("s"), [{"v": 26}])
        self.assertEqual(Context(DAY, self.data_dir).previous_rows("missing"), [])

    def test_manifest_keeps_sources_not_rerun(self):
        ctx = Context(DAY, self.data_dir)
        write_manifest(self.data_dir, DAY, run_all([FakeSource("a", [{}]), FakeSource("b", [{}])], ctx), ["a", "b"])
        write_manifest(self.data_dir, DAY, run_all([FakeSource("b", error=OSError("down"))], ctx), ["a", "b"])
        results = read_manifest(manifest_path(self.data_dir, DAY))["results"]
        self.assertEqual([(r["source"], r["status"]) for r in results], [("a", "ok"), ("b", "failed")])


class ReadmeTest(unittest.TestCase):
    def test_lists_every_source_and_escapes_feed_text(self):
        data_dir = Path(tempfile.mkdtemp())
        sources = [FakeSource("one", [{}]), FakeSource("two", error=RuntimeError("bad | <b>html</b>"))]
        write_manifest(data_dir, DAY, run_all(sources, Context(DAY, data_dir)), ["one", "two"])
        out = readme.render("{{source_count}} | {{digest}} | {{status}} | {{health}}", sources, data_dir)
        self.assertTrue(out.startswith("2 |"))
        self.assertIn("[`one`](data/one)", out)
        self.assertIn("❌ failed", out)
        self.assertIn(r"\<b\>html\</b\>", out)
        self.assertIn("| 2026-10-27 | 1/2 |", out)


class MarkdownTest(unittest.TestCase):
    def test_text_escapes_and_trims(self):
        self.assertEqual(text("a  [b]\n| c"), r"a \[b\] \| c")
        self.assertEqual(len(text("x" * 300, 50)), 50)

    def test_link_rejects_non_http_urls(self):
        self.assertEqual(link("x", "javascript:alert(1)"), "x")
        self.assertEqual(link("x", "https://a.b/c d"), "[x](<https://a.b/c%20d>)")
        self.assertEqual(link("x", "https:///no-host"), "x")

    def test_link_url_cannot_break_out_of_the_link(self):
        out = link("x", "https://a.b/p>\n\n<img src=x onerror=alert(1)>\\")
        self.assertEqual(out, "[x](<https://a.b/p%3E%0A%0A%3Cimg%20src=x%20onerror=alert(1)%3E%5C>)")
        self.assertEqual(link("x", "https://a.b/q?a=1&b=%20"), "[x](<https://a.b/q?a=1&b=%20>)")

    def test_number(self):
        self.assertEqual([number(v) for v in (950, 12_345, 1_741_967, None)], ["950", "12.3K", "1.7M", "?"])


class RegistryTest(unittest.TestCase):
    def test_sources_are_unique_and_described(self):
        names = [s.name for s in SOURCES]
        self.assertGreaterEqual(len(names), 15)
        self.assertEqual(len(names), len(set(names)))
        for s in SOURCES:
            self.assertTrue(s.title and s.category and s.description and s.homepage.startswith("https://"), s.name)


if __name__ == "__main__":
    unittest.main()
