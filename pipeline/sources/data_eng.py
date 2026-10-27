"""Data engineering: tool releases, package and image adoption, and what the community is writing."""

from __future__ import annotations

import time

from pipeline import http
from pipeline.core import Context, Source
from pipeline.markdown import link, number
from pipeline.sources.common import collect, latest_release, release_highlight

CATEGORY = "Data engineering"


class DataToolReleases(Source):
    name = "data_tool_releases"
    title = "Data tool releases"
    category = CATEGORY
    description = "Latest stable release of the core lakehouse, streaming, orchestration and query engines."
    homepage = "https://github.com/"

    REPOS = {
        "Apache Spark": "apache/spark",
        "Apache Airflow": "apache/airflow",
        "Apache Kafka": "apache/kafka",
        "Apache Flink": "apache/flink",
        "Apache Iceberg": "apache/iceberg",
        "Apache Arrow": "apache/arrow",
        "Delta Lake": "delta-io/delta",
        "dbt Core": "dbt-labs/dbt-core",
        "DuckDB": "duckdb/duckdb",
        "Polars": "pola-rs/polars",
        "Trino": "trinodb/trino",
        "ClickHouse": "ClickHouse/ClickHouse",
        "Dagster": "dagster-io/dagster",
    }

    def fetch(self, ctx: Context) -> list[dict]:
        return collect(self.REPOS.items(), lambda item: latest_release(*item, ctx.day))

    def highlight(self, rows):
        return release_highlight(rows)


class PypiDownloads(Source):
    name = "pypi_downloads"
    title = "Python package downloads"
    category = CATEGORY
    description = "Daily, weekly and monthly PyPI downloads for data and AI libraries."
    homepage = "https://pypistats.org/"

    PACKAGES = [
        "pandas", "pyarrow", "pyspark", "polars", "duckdb", "apache-airflow", "dbt-core", "dagster",
        "pyiceberg", "deltalake", "sqlglot", "great-expectations", "langchain", "openai", "anthropic", "mcp",
    ]

    def fetch(self, ctx: Context) -> list[dict]:
        def one(package: str) -> dict:
            time.sleep(1)  # pypistats asks clients to keep request rates low
            d = http.get_json(f"https://pypistats.org/api/packages/{package}/recent")["data"]
            return {"package": package, "last_day": d["last_day"], "last_week": d["last_week"],
                    "last_month": d["last_month"]}

        return sorted(collect(self.PACKAGES, one), key=lambda r: r["last_day"], reverse=True)

    def highlight(self, rows):
        return "Yesterday: " + ", ".join(f"`{r['package']}` {number(r['last_day'])}" for r in rows[:4])


class DockerPulls(Source):
    name = "docker_pulls"
    title = "Docker image pulls"
    category = CATEGORY
    description = "Total Docker Hub pulls for data-platform images, with the change since the last run."
    homepage = "https://hub.docker.com/"

    IMAGES = [
        "library/postgres", "library/redis", "apache/airflow", "apache/spark", "apache/kafka",
        "confluentinc/cp-kafka", "library/flink", "clickhouse/clickhouse-server", "trinodb/trino",
        "apache/superset", "ollama/ollama",
    ]

    def fetch(self, ctx: Context) -> list[dict]:
        previous = {r["image"]: r["pull_count"] for r in ctx.previous_rows(self.name)}

        def one(image: str) -> dict:
            d = http.get_json(f"https://hub.docker.com/v2/repositories/{image}/")
            pulls = d["pull_count"]
            return {
                "image": image,
                "pull_count": pulls,
                "star_count": d.get("star_count"),
                "last_updated": d.get("last_updated"),
                "pulls_since_last_run": pulls - previous[image] if image in previous else None,
            }

        return collect(self.IMAGES, one)

    def highlight(self, rows):
        moving = [r for r in rows if r["pulls_since_last_run"] is not None]
        if moving:
            top = max(moving, key=lambda r: r["pulls_since_last_run"])
            return f"Most pulled since the last run: `{top['image']}` (+{number(top['pulls_since_last_run'])})"
        top = max(rows, key=lambda r: r["pull_count"])
        return f"Most pulled overall: `{top['image']}` ({number(top['pull_count'])} pulls)"


class DevtoDataEngineering(Source):
    name = "devto_data_engineering"
    title = "Data engineering articles"
    category = CATEGORY
    description = "Today's top dev.to articles tagged dataengineering."
    homepage = "https://dev.to/t/dataengineering"

    def fetch(self, ctx: Context) -> list[dict]:
        articles = http.get_json("https://dev.to/api/articles", {"tag": "dataengineering", "top": 1, "per_page": 20})
        return [{
            "article_id": a["id"],
            "title": a["title"],
            "author": (a.get("user") or {}).get("username"),
            "published_at": a.get("published_at"),
            "reactions": a.get("public_reactions_count"),
            "comments": a.get("comments_count"),
            "reading_minutes": a.get("reading_time_minutes"),
            "tags": a.get("tag_list", []),
            "url": a["url"],
        } for a in articles]

    def highlight(self, rows):
        top = max(rows, key=lambda r: r["reactions"] or 0)
        return f"Top: {link(top['title'], top['url'])} ({top['reactions']} reactions)"


SOURCES = [DataToolReleases(), PypiDownloads(), DockerPulls(), DevtoDataEngineering()]
