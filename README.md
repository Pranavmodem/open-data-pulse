# open-data-pulse

[![CI](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/ci.yml/badge.svg)](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/ci.yml)
[![daily snapshot](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/daily.yml/badge.svg)](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/daily.yml)
[![MIT license](https://img.shields.io/github/license/Pranavmodem/open-data-pulse)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://docs.python.org/3.12/)

A small data pipeline that takes a daily snapshot of 21 public feeds: AI research and model hubs, agent frameworks, data-engineering tool releases and adoption, platform status, security advisories, and weather, air and hazards in the cities that host the big cloud regions.

A GitHub Actions job runs it every morning. It fetches the feeds in parallel, retries what fails, writes one date-partitioned JSONL file per feed, records a run manifest, and rebuilds this README.

**Last run:** 2026-11-09 23:00 UTC

## Today's digest

### AI and agents

- **arXiv agent papers**: 30 new papers. Newest: [On Agentic Manipulation Policies](<https://arxiv.org/abs/2611.09892v1>)
- **Hugging Face daily papers**: Top: [From Autonomous Agents to Cognitive Symbionts: Toward AI-Augmented Human Intelligence](<https://huggingface.co/papers/2611.05376>) (121 upvotes)
- **Hugging Face trending models**: #1: [speridlabs/idol](<https://huggingface.co/speridlabs/idol>) (image-to-3d, 1.6K likes)
- **Hugging Face trending datasets**: #1: [nvidia/simready-assets](<https://huggingface.co/datasets/nvidia/simready-assets>) (1.5M downloads)
- **LLM catalog and prices**: 464 models, 5 new since the last run: Thinking Machines: Inkling 2 Small (free), Anthropic: Claude Fable 5.2, Anthropic: Claude Fable 5.2 (batch) and 2 more
- **New agent and MCP repos**: Top new repo: [KKKKhazix/agent-autoloop](<https://github.com/KKKKhazix/agent-autoloop>) (4.3K stars in under a week)
- **Agent framework releases**: Latest: [CrewAI 1.15.39](<https://github.com/crewAIInc/crewAI/releases/tag/1.15.39>) (today)
- **AI SDK downloads (npm)**: Most downloaded: `@modelcontextprotocol/sdk` 7.7M, `@anthropic-ai/sdk` 6.3M, `openai` 5.1M

### Data engineering

- **Data tool releases**: Latest: [Apache Airflow 3.4.0](<https://github.com/apache/airflow/releases/tag/3.4.0>) (3d ago)
- **Python package downloads**: Yesterday: `pandas` 18.1M, `pyarrow` 10.4M, `openai` 8.7M, `mcp` 7.4M
- **Docker image pulls**: Most pulled since the last run: `library/postgres` (+26.5M)
- **Data engineering articles**: Top: [Why an ID Check Let the Same PDF Into Our Pipeline Twice](<https://dev.to/utkarsh_gupta/why-an-id-check-let-the-same-pdf-into-our-pipeline-twice-18g5>) (0 reactions)

### Tech pulse

- **Hacker News front page**: Top: [Claude Fable 5.2 and Mythos 5.2](<https://news.ycombinator.com/item?id=50429906>) (811 points)
- **Platform status**: Degraded: [Snowflake: Partially Degraded Service](<https://status.snowflake.com>); [Cloudflare: Partial System Outage](<https://www.cloudflarestatus.com>)
- **Known exploited vulnerabilities**: 7 added in the week to 2026-11-09. Newest: [CVE-2026-123218](<https://nvd.nist.gov/vuln/detail/CVE-2026-123218>) (IBM Aspera Faspex)
- **Most-read Wikipedia articles**: Most read: [Ramayana: Part 1](<https://en.wikipedia.org/wiki/Ramayana%3A_Part_1>) (716.4K), [.xxx](<https://en.wikipedia.org/wiki/.xxx>) (242.8K), [.xyz](<https://en.wikipedia.org/wiki/.xyz>) (232.3K)

### World signals

- **Weather in cloud-region cities**: Dallas 22°C / 14°C, overcast. Hottest: Mumbai (ap-south-1) 36°C. Coldest: Columbus, OH (us-east-2) 4°C
- **Air quality in cloud-region cities**: Worst air: Mumbai (AQI 152). Cleanest: Columbus, OH (AQI 28)
- **Earthquakes**: 48 quakes of M2.5+ in 24h. Largest: [M6.4 30 km WSW of Lata, Solomon Islands](<https://earthquake.usgs.gov/earthquakes/eventpage/us7000tx16>)
- **Natural hazards**: 9 open events: 5 sea and lake ice, 4 severe storms
- **Exchange rates**: 1 USD = 0.8934 EUR, 0.7454 GBP, 93.93 INR, 157.9 JPY, 18.61 MXN (ECB, 2026-11-09)

## Sources

`✅ ok` means every item was fetched, `⚠️ partial` that some items failed (so the row count is short and the digest says why), `⚪ no rows` that the feed had nothing today, and `❌ failed` that nothing came back at all.

| Source | What it tracks | Rows | Status |
| --- | --- | ---: | --- |
| [`arxiv_agent_papers`](data/arxiv_agent_papers) | Newest arXiv papers on LLM agents, agentic systems and multi-agent work. [↗](<https://arxiv.org/>) | 30 | ✅ ok |
| [`hf_daily_papers`](data/hf_daily_papers) | Papers the Hugging Face community picked today, with upvotes and linked code. [↗](<https://huggingface.co/papers>) | 50 | ✅ ok |
| [`hf_trending_models`](data/hf_trending_models) | The 30 models trending on the Hugging Face Hub. [↗](<https://huggingface.co/models?sort=trending>) | 30 | ✅ ok |
| [`hf_trending_datasets`](data/hf_trending_datasets) | The 30 datasets trending on the Hugging Face Hub. [↗](<https://huggingface.co/datasets?sort=trending>) | 30 | ✅ ok |
| [`llm_catalog`](data/llm_catalog) | Every model on OpenRouter with context window and price per million tokens; flags new models. [↗](<https://openrouter.ai/models>) | 464 | ✅ ok |
| [`github_agent_repos`](data/github_agent_repos) | Repos created this week under agent and MCP topics on GitHub, ranked by stars. [↗](<https://github.com/topics/ai-agents>) | 30 | ✅ ok |
| [`ai_framework_releases`](data/ai_framework_releases) | Latest release of the main agent, LLM-serving and model frameworks. [↗](<https://github.com/>) | 13 | ✅ ok |
| [`ai_sdk_downloads`](data/ai_sdk_downloads) | Yesterday's npm downloads for the main LLM and agent SDKs. [↗](<https://www.npmjs.com/>) | 11 | ✅ ok |
| [`data_tool_releases`](data/data_tool_releases) | Latest stable release of the core lakehouse, streaming, orchestration and query engines. [↗](<https://github.com/>) | 13 | ✅ ok |
| [`pypi_downloads`](data/pypi_downloads) | Daily, weekly and monthly PyPI downloads for data and AI libraries. [↗](<https://pypistats.org/>) | 16 | ✅ ok |
| [`docker_pulls`](data/docker_pulls) | Total Docker Hub pulls for data-platform images, with the change since the last run. [↗](<https://hub.docker.com/>) | 11 | ✅ ok |
| [`devto_data_engineering`](data/devto_data_engineering) | Today's top dev.to articles tagged dataengineering. [↗](<https://dev.to/t/dataengineering>) | 19 | ✅ ok |
| [`hackernews_front_page`](data/hackernews_front_page) | The 30 stories on the Hacker News front page at snapshot time. [↗](<https://news.ycombinator.com/>) | 30 | ✅ ok |
| [`cloud_status`](data/cloud_status) | Live status and open incidents for the data and AI platforms teams depend on. [↗](<https://www.atlassian.com/software/statuspage>) | 8 | ✅ ok |
| [`cisa_kev`](data/cisa_kev) | The 20 newest entries in CISA's catalog of vulnerabilities exploited in the wild. [↗](<https://www.cisa.gov/known-exploited-vulnerabilities-catalog>) | 20 | ✅ ok |
| [`wikipedia_top_pages`](data/wikipedia_top_pages) | Yesterday's 25 most-viewed English Wikipedia articles, from the Wikimedia pageviews API. [↗](<https://wikimedia.org/api/rest_v1/>) | 25 | ✅ ok |
| [`cloud_region_weather`](data/cloud_region_weather) | Today's forecast for Dallas and the cities behind nine major AWS regions. [↗](<https://open-meteo.com/>) | 10 | ✅ ok |
| [`air_quality`](data/air_quality) | Current US AQI, PM2.5, PM10 and ozone for the same cities. [↗](<https://open-meteo.com/en/docs/air-quality-api>) | 10 | ✅ ok |
| [`earthquakes`](data/earthquakes) | Every magnitude 2.5+ earthquake in the past 24 hours, from the USGS feed. [↗](<https://earthquake.usgs.gov/earthquakes/feed/>) | 48 | ✅ ok |
| [`natural_events`](data/natural_events) | Open wildfires, storms, volcanoes and other events NASA EONET tracked this week. [↗](<https://eonet.gsfc.nasa.gov/>) | 9 | ✅ ok |
| [`fx_rates`](data/fx_rates) | European Central Bank reference rates against the US dollar. [↗](<https://frankfurter.dev/>) | 29 | ✅ ok |

## Pipeline health

Last 5 runs, newest first.

| Date | Sources ok | Rows | Problems |
| --- | ---: | ---: | --- |
| 2026-11-09 | 21/21 | 906 | none |
| 2026-11-08 | 21/21 | 887 | none |
| 2026-11-07 | 21/21 | 884 | none |
| 2026-11-06 | 21/21 | 871 | none |
| 2026-11-05 | 21/21 | 882 | none |

## How it works

```mermaid
flowchart LR
  cron["daily.yml<br/>13:17 UTC"] --> sources

  subgraph sources [Sources]
    direction TB
    ai["AI and agents"]
    de["Data engineering"]
    tech["Tech pulse"]
    world["World signals"]
    %% Keep the category order stable in the layout.
    ai ~~~ de ~~~ tech ~~~ world
  end

  sources --> pool["thread pool, 6 workers<br/>urllib, retry with backoff"]
  pool --> parts["data/&lt;source&gt;/dt=&lt;date&gt;/data.jsonl"]
  pool --> manifest["data/_runs/dt=&lt;date&gt;/manifest.json"]
  manifest --> digest["README digest"]
  parts -.-> duck["DuckDB"]
  parts --> commit["commit data/ and README.md"]
  digest --> commit
```

- **One class per feed.** Each source in [`pipeline/sources/`](pipeline/sources) sets its metadata and implements `fetch()`, which returns rows, and `highlight()`, which writes its line in the digest.
- **Failures stay contained.** Sources run in a thread pool, and HTTP calls retry with backoff. A source that still errors is marked `failed` in the manifest while the rest carry on. The job only fails when fewer than half the sources succeed.
- **A short list is never silent.** A feed built from many items (repos, packages, status pages) fetches each one separately: one dead item does not sink the source, but it is recorded, the source is marked `partial`, and the README names the item that failed. The digest says "1 of 9 items failed" instead of letting an eight-row snapshot read as complete.
- **Idempotent partitions.** Output goes to `data/<source>/dt=<YYYY-MM-DD>/data.jsonl`. Re-running a day overwrites that day's file, and removes it when the rerun returns no rows, so a snapshot never keeps rows the latest run did not fetch.
- **Change detection.** A source can read its previous partition. The LLM catalog flags models that weren't there on the last run, and Docker pulls report the change since the last run.
- **Run manifests.** `data/_runs/dt=<YYYY-MM-DD>/manifest.json` records the status, row count, duration and any error for every source, plus the individual items that failed inside a `partial` one.
- **One pass over the template.** Feed text is escaped and substituted once, so a title that happens to look like a template placeholder is rendered as text rather than expanded into the page.
- **No dependencies.** Python standard library only.

## Query the data

The layout is Hive-style, so [DuckDB](https://duckdb.org/) reads it in place:

```sql
-- Largest earthquakes across every snapshot
SELECT dt, magnitude, place
FROM read_json_auto('data/earthquakes/*/data.jsonl', hive_partitioning = true)
ORDER BY magnitude DESC
LIMIT 10;

-- Models added to the LLM catalog, by day
SELECT dt, count(*) AS new_models, list(name) AS names
FROM read_json_auto('data/llm_catalog/*/data.jsonl', hive_partitioning = true)
WHERE is_new
GROUP BY dt
ORDER BY dt DESC;

-- Daily PyPI downloads for the data stack
SELECT dt, package, last_day
FROM read_json_auto('data/pypi_downloads/*/data.jsonl', hive_partitioning = true)
WHERE package IN ('pyspark', 'polars', 'duckdb')
ORDER BY dt, package;
```

## Run it locally

```bash
pip install -e .                            # optional; adds the open-data-pulse command
open-data-pulse                             # same entry point as python -m pipeline.run
python -m pipeline.run                      # every source, today's date
python -m pipeline.run --only earthquakes   # one source
python -m unittest discover tests
```

It needs Python 3.11 or newer. Set `GITHUB_TOKEN` for higher GitHub API limits. Spark, Kafka and Flink publish tags instead of GitHub releases, and looking those up needs the token.

## Add a source

Subclass `Source` in the matching module under [`pipeline/sources/`](pipeline/sources), implement `fetch()` and `highlight()`, and add an instance to that module's `SOURCES` list.

## Data and licenses

The code is MIT licensed. Each dataset belongs to its publisher and keeps its own terms: arXiv, Hugging Face, OpenRouter, GitHub, npm, PyPI Stats, Docker Hub, DEV, Hacker News (via Algolia), each platform's status page, CISA, Wikimedia, Open-Meteo, USGS, NASA EONET, and the European Central Bank (via Frankfurter). The Sources table links to each one.
