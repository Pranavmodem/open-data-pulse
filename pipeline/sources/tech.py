"""Tech pulse: what engineers are reading, whether the platforms are up, and new exploited CVEs."""

from __future__ import annotations

import urllib.error
from datetime import date, timedelta
from urllib.parse import quote

from pipeline import http
from pipeline.core import Context, Source
from pipeline.markdown import link, number, text
from pipeline.sources.common import collect

CATEGORY = "Tech pulse"


class HackerNewsFrontPage(Source):
    name = "hackernews_front_page"
    title = "Hacker News front page"
    category = CATEGORY
    description = "The 30 stories on the Hacker News front page at snapshot time."
    homepage = "https://news.ycombinator.com/"

    def fetch(self, ctx: Context) -> list[dict]:
        hits = http.get_json("https://hn.algolia.com/api/v1/search", {"tags": "front_page", "hitsPerPage": 30})["hits"]
        return [{
            "rank": rank,
            "story_id": h["objectID"],
            "title": h.get("title"),
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
            "points": h.get("points"),
            "comments": h.get("num_comments"),
            "author": h.get("author"),
            "created_at": h.get("created_at"),
            "discussion_url": f"https://news.ycombinator.com/item?id={h['objectID']}",
        } for rank, h in enumerate(hits, 1)]

    def highlight(self, rows):
        top = max(rows, key=lambda r: r["points"] or 0)
        return f"Top: {link(top['title'], top['discussion_url'])} ({text(top['points'], 20)} points)"


class CloudStatus(Source):
    name = "cloud_status"
    title = "Platform status"
    category = CATEGORY
    description = "Live status and open incidents for the data and AI platforms teams depend on."
    homepage = "https://www.atlassian.com/software/statuspage"

    PAGES = {
        "GitHub": "https://www.githubstatus.com",
        "Snowflake": "https://status.snowflake.com",
        "Confluent Cloud": "https://status.confluent.cloud",
        "dbt Cloud": "https://status.getdbt.com",
        "Datadog": "https://status.datadoghq.com",
        "Cloudflare": "https://www.cloudflarestatus.com",
        "Vercel": "https://www.vercel-status.com",
        "Anthropic": "https://status.anthropic.com",
        "OpenAI": "https://status.openai.com",
    }

    def fetch(self, ctx: Context) -> list[dict]:
        def one(item: tuple[str, str]) -> dict:
            provider, page = item
            summary = http.get_json(f"{page}/api/v2/summary.json")
            incidents = summary.get("incidents", [])
            return {
                "provider": provider,
                "indicator": summary["status"]["indicator"],
                "status": summary["status"]["description"],
                "open_incidents": len(incidents),
                "incident_titles": [i.get("name") for i in incidents][:5],
                "url": page,
            }

        return collect(self.PAGES.items(), one)

    def highlight(self, rows):
        degraded = [r for r in rows if r["indicator"] != "none"]
        if not degraded:
            return f"All {len(rows)} platforms operational"
        return "Degraded: " + "; ".join(link(f"{r['provider']}: {r['status']}", r["url"], 80) for r in degraded)


class CisaKnownExploited(Source):
    name = "cisa_kev"
    title = "Known exploited vulnerabilities"
    category = CATEGORY
    description = "The 20 newest entries in CISA's catalog of vulnerabilities exploited in the wild."
    homepage = "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"

    def fetch(self, ctx: Context) -> list[dict]:
        catalog = http.get_json(
            "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", timeout=60)
        newest = sorted(catalog["vulnerabilities"], key=lambda v: (v["dateAdded"], v["cveID"]), reverse=True)[:20]
        return [{
            "cve_id": v["cveID"],
            "vendor": v.get("vendorProject"),
            "product": v.get("product"),
            "name": v.get("vulnerabilityName"),
            "date_added": v["dateAdded"],
            "due_date": v.get("dueDate"),
            "ransomware_use": v.get("knownRansomwareCampaignUse"),
            "url": f"https://nvd.nist.gov/vuln/detail/{v['cveID']}",
        } for v in newest]

    def highlight(self, rows):
        newest = rows[0]
        week_ago = str(date.fromisoformat(newest["date_added"]) - timedelta(days=7))
        this_week = sum(r["date_added"] > week_ago for r in rows)
        return (f"{this_week} added in the week to {text(newest['date_added'], 20)}. Newest: "
                f"{link(newest['cve_id'], newest['url'])} ({text(newest['vendor'], 40)} {text(newest['product'], 40)})")


class WikipediaTopPages(Source):
    name = "wikipedia_top_pages"
    title = "Most-read Wikipedia articles"
    category = CATEGORY
    description = "Yesterday's 25 most-viewed English Wikipedia articles, from the Wikimedia pageviews API."
    homepage = "https://wikimedia.org/api/rest_v1/"

    SKIP_PREFIXES = ("Special:", "Wikipedia:", "Portal:", "File:", "Help:", "Talk:", "Category:", "Template:")

    def fetch(self, ctx: Context) -> list[dict]:
        # Yesterday's file usually lands within hours; fall back a day if it hasn't yet.
        for days_back in (1, 2):
            day = ctx.day - timedelta(days=days_back)
            try:
                payload = http.get_json(
                    "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/"
                    f"{day:%Y/%m/%d}", retries=1)
                break
            except urllib.error.HTTPError as exc:
                if exc.code != 404 or days_back == 2:
                    raise
        articles = [a for a in payload["items"][0]["articles"]
                    if a["article"] not in ("Main_Page", "-") and not a["article"].startswith(self.SKIP_PREFIXES)]
        return [{
            "rank": rank,
            "article": a["article"].replace("_", " "),
            "views": a["views"],
            "day": str(day),
            "url": f"https://en.wikipedia.org/wiki/{quote(a['article'])}",
        } for rank, a in enumerate(articles[:25], 1)]

    def highlight(self, rows):
        return "Most read: " + ", ".join(f"{link(r['article'], r['url'], 50)} ({number(r['views'])})" for r in rows[:3])


SOURCES = [HackerNewsFrontPage(), CloudStatus(), CisaKnownExploited(), WikipediaTopPages()]
