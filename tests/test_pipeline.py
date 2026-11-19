"""Offline tests for the runner, the partition writer and the README renderer."""

from __future__ import annotations

import re
import tempfile
import unittest
from datetime import date
from pathlib import Path

from pipeline import readme
from pipeline.core import Context, Source, read_jsonl, read_manifest, manifest_path, run_all, write_manifest
from pipeline.markdown import link, number, text
from pipeline.sources import SOURCES, ai, data_eng, tech, world
from pipeline.sources.common import collect

DAY = date(2026, 10, 27)
EVIL = "<img src=x onerror=alert(1)> | [x](javascript:1)"


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


class ItemSource(Source):
    """A source that fetches one item at a time, the way the real multi-item sources do."""

    category = "Test"
    homepage = "https://example.com"

    def __init__(self, name: str, items: tuple[str, ...] = ("a", "b"), broken: tuple[str, ...] = ()):
        self.name = self.title = self.description = name
        self.items, self.broken = items, set(broken)

    def fetch(self, ctx):
        return collect(self.items, self._one, on_error=self.note_failure)

    def _one(self, item: str) -> dict | None:
        if item in self.broken:
            raise RuntimeError(f"503 for {item}")
        return {"item": item} if item != "skip" else None

    def highlight(self, rows):
        return f"{len(rows)} items"



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

    def test_rerun_that_returns_no_rows_clears_the_day(self):
        ctx = Context(DAY, self.data_dir)
        path = self.data_dir / "s" / "dt=2026-10-27" / "data.jsonl"
        run_all([FakeSource("s", [{"v": 1}])], ctx)
        self.assertTrue(path.exists())
        run_all([FakeSource("s")], ctx)
        self.assertFalse(path.exists(), "a rerun with no rows must not leave the earlier rows behind")
        self.assertEqual(read_jsonl(path), [])

    def test_failed_fetch_keeps_the_partition_it_already_had(self):
        ctx = Context(DAY, self.data_dir)
        run_all([FakeSource("s", [{"v": 1}])], ctx)
        run_all([FakeSource("s", error=OSError("down"))], ctx)
        self.assertEqual(read_jsonl(self.data_dir / "s" / "dt=2026-10-27" / "data.jsonl"), [{"v": 1}])


class PartialResultTest(unittest.TestCase):
    """Items that fail inside a source must not disappear into a clean-looking 'ok'."""

    def setUp(self):
        self.data_dir = Path(tempfile.mkdtemp())

    def test_some_items_failing_is_a_partial_result(self):
        (result,) = run_all([ItemSource("feeds", items=("a", "b", "c"), broken=("b",))], Context(DAY, self.data_dir))
        self.assertEqual((result.status, result.rows, result.expected), ("partial", 2, 3))
        self.assertEqual(len(result.errors), 1)
        self.assertIn("b: RuntimeError: 503 for b", result.errors[0])
        self.assertIsNone(result.error)

    def test_every_item_failing_is_failed_not_empty(self):
        (result,) = run_all([ItemSource("feeds", items=("a", "b"), broken=("a", "b"))], Context(DAY, self.data_dir))
        self.assertEqual((result.status, result.rows), ("failed", 0))
        self.assertIn("503 for a", result.error or "")

    def test_items_that_return_nothing_are_not_failures(self):
        (result,) = run_all([ItemSource("feeds", items=("a", "skip"))], Context(DAY, self.data_dir))
        self.assertEqual((result.status, result.rows, result.expected, result.errors), ("ok", 1, None, []))

    def test_failures_are_written_to_the_manifest(self):
        ctx = Context(DAY, self.data_dir)
        write_manifest(self.data_dir, DAY, run_all([ItemSource("feeds", items=("a", "b"), broken=("b",))], ctx), ["feeds"])
        (record,) = read_manifest(manifest_path(self.data_dir, DAY))["results"]
        self.assertEqual((record["status"], record["expected"], len(record["errors"])), ("partial", 2, 1))

    def test_failures_do_not_leak_into_the_next_run_of_the_same_process(self):
        source = ItemSource("feeds", items=("a", "b"), broken=("b",))
        (first,) = run_all([source], Context(DAY, self.data_dir))
        source.broken = set()
        (second,) = run_all([source], Context(DAY, self.data_dir))
        self.assertEqual((first.status, second.status, second.errors), ("partial", "ok", []))



class ReadmeTest(unittest.TestCase):
    def test_template_badges_and_diagram_survive_render(self):
        template = (Path(__file__).resolve().parents[1] / "README.template.md").read_text(encoding="utf-8")
        data_dir = Path(tempfile.mkdtemp())
        sources = [FakeSource("one", [{}])]
        write_manifest(data_dir, DAY, run_all(sources, Context(DAY, data_dir)), ["one"])
        out = readme.render(template, sources, data_dir)
        for fragment in (
            "actions/workflows/ci.yml/badge.svg",
            "actions/workflows/daily.yml/badge.svg",
            "img.shields.io/github/license/Pranavmodem/open-data-pulse",
            "img.shields.io/badge/python-3.12-blue",
            "```mermaid",
            "data/&lt;source&gt;/dt=&lt;date&gt;/data.jsonl",
            "data/_runs/dt=&lt;date&gt;/manifest.json",
        ):
            self.assertIn(fragment, out)
        self.assertNotIn("{{", out)

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

    def test_partial_sources_are_marked_in_the_table_digest_and_health(self):
        data_dir = Path(tempfile.mkdtemp())
        sources = [ItemSource("feeds", items=("a", "b"), broken=("b",))]
        write_manifest(data_dir, DAY, run_all(sources, Context(DAY, data_dir)), ["feeds"])
        out = readme.render("{{digest}}\n{{status}}\n{{health}}", sources, data_dir)
        self.assertIn("⚠️ partial", out)
        self.assertIn("1 of 2 items failed", out)
        self.assertIn("_ (1 of 2 items failed)_".replace("_ (", "_("), out)
        self.assertIn("| 2026-10-27 | 0/1 |", out)
        self.assertIn("`feeds` ⚠️", out)

    def test_feed_text_cannot_inject_a_placeholder(self):
        data_dir = Path(tempfile.mkdtemp())

        class Sneaky(ItemSource):
            def highlight(self, rows):
                return "sneaky {{health}} and {{source_count}}"

        sources = [Sneaky("sneaky", items=("a",))]
        write_manifest(data_dir, DAY, run_all(sources, Context(DAY, data_dir)), ["sneaky"])
        out = readme.render("{{source_count}}|{{digest}}|{{health}}", sources, data_dir)
        self.assertIn("sneaky {{health}} and {{source_count}}", out)
        self.assertIn("| Date | Sources ok |", out)
        self.assertTrue(out.startswith("1|"))



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


class HighlightTest(unittest.TestCase):
    def test_feed_values_in_highlights_are_escaped(self):
        cases = [
            (ai.HuggingFaceTrendingModels(), {"model_id": "a/b", "url": "https://huggingface.co/a/b", "task": EVIL, "likes": 5}),
            (ai.HuggingFaceDailyPapers(), {"title": EVIL, "url": "https://huggingface.co/papers/1", "upvotes": EVIL}),
            (data_eng.DevtoDataEngineering(), {"title": EVIL, "url": "https://dev.to/x", "reactions": EVIL}),
            (tech.HackerNewsFrontPage(), {"title": EVIL, "discussion_url": "https://news.ycombinator.com/item?id=1", "points": EVIL}),
            (world.AirQuality(), {"city": "Dallas", "us_aqi": EVIL}),
            (world.FxRates(), {"currency": "EUR", "rate": 0.92, "date": EVIL}),
        ]
        for source, row in cases:
            with self.subTest(source.name):
                out = source.highlight([row])
                bare = re.sub(r"\]\(<[^<>\s]*>\)", "]", out)  # link targets are percent-encoded by link()
                self.assertIn("img", bare)
                self.assertNotRegex(bare, r"(?<!\\)[<>|]")


class RegistryTest(unittest.TestCase):
    def test_sources_are_unique_and_described(self):
        names = [s.name for s in SOURCES]
        self.assertGreaterEqual(len(names), 15)
        self.assertEqual(len(names), len(set(names)))
        for s in SOURCES:
            self.assertTrue(s.title and s.category and s.description and s.homepage.startswith("https://"), s.name)


if __name__ == "__main__":
    unittest.main()
