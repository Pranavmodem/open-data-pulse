# open-data-pulse

[![CI](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/ci.yml/badge.svg)](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/ci.yml)
[![daily snapshot](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/daily.yml/badge.svg)](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/daily.yml)
[![MIT license](https://img.shields.io/github/license/Pranavmodem/open-data-pulse)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://docs.python.org/3.12/)

A small data pipeline that takes a daily snapshot of 21 public feeds: AI research and model hubs, agent frameworks, data-engineering tool releases and adoption, platform status, security advisories, and weather, air and hazards in the cities that host the big cloud regions.

A GitHub Actions job runs it every morning. It fetches the feeds in parallel, retries what fails, writes one date-partitioned JSONL file per feed, records a run manifest, and rebuilds this README.

**Last run:** 2026-11-24 23:03 UTC

## Today's digest

### AI and agents

- **arXiv agent papers**: 30 new papers. Newest: [TowerBridge: Bridging the Dual-Encoder Modality Gap via Weight-Space Programming](<https://arxiv.org/abs/2611.31233v1>)
- **Hugging Face daily papers**: Top: [Embo-Harness: Towards Understanding Frontier-Model-as-Policy Harness](<https://huggingface.co/papers/2611.31201>) (90 upvotes)
- **Hugging Face trending models**: #1: [thinkingmachines/Inkling-2-Mini](<https://huggingface.co/thinkingmachines/Inkling-2-Mini>) (image-text-to-text, 5.8K likes)
- **Hugging Face trending datasets**: #1: [Vyber07/cyber-security](<https://huggingface.co/datasets/Vyber07/cyber-security>) (35.3K downloads)
- **LLM catalog and prices**: 470 models, 1 new since the last run: Xiaomi: MiMo-V2.6-Flash-MOPD
- **New agent and MCP repos**: Top new repo: [EL4CTEO/fast-anything](<https://github.com/EL4CTEO/fast-anything>) (3.6K stars in under a week)
- **Agent framework releases**: Latest: [CrewAI 1.15.45](<https://github.com/crewAIInc/crewAI/releases/tag/1.15.45>) (today)
- **AI SDK downloads (npm)**: Most downloaded: `@modelcontextprotocol/sdk` 14.2M, `@anthropic-ai/sdk` 11.4M, `openai` 9.6M

### Data engineering

- **Data tool releases**: Latest: [Polars py-2.2.0](<https://github.com/pola-rs/polars/releases/tag/py-2.2.0>) (today)
- **Python package downloads**: Yesterday: `pandas` 26.0M, `pyarrow` 15.6M, `openai` 15.5M, `mcp` 13.9M
- **Docker image pulls**: Most pulled since the last run: `library/postgres` (+60.3M)
- **Data engineering articles**: Top: [A Little Look At The Engine That Generates MegaBit-trajectories](<https://dev.to/sumama-jameel/a-little-look-at-the-engine-that-generates-megabit-trajectories-46gn>) (6 reactions)

### Tech pulse

- **Hacker News front page**: Top: [2035 came early](<https://news.ycombinator.com/item?id=50624497>) (934 points)
- **Platform status**: Degraded: [Cloudflare: Minor Service Outage](<https://www.cloudflarestatus.com>); [Anthropic: Partially Degraded Service](<https://status.anthropic.com>)
- **Known exploited vulnerabilities**: 13 added in the week to 2026-11-24. Newest: [CVE-2026-132224](<https://nvd.nist.gov/vuln/detail/CVE-2026-132224>) (Optimizely Web Experimentation)
- **Most-read Wikipedia articles**: Most read: [Ramayana: Part 1](<https://en.wikipedia.org/wiki/Ramayana%3A_Part_1>) (365.7K), [Grand Theft Auto VI](<https://en.wikipedia.org/wiki/Grand_Theft_Auto_VI>) (266.2K), [Jensen Huang](<https://en.wikipedia.org/wiki/Jensen_Huang>) (234.3K)

### World signals

- **Weather in cloud-region cities**: Dallas 9°C / 6°C, drizzle. Hottest: Mumbai (ap-south-1) 34°C. Coldest: Columbus, OH (us-east-2) -3°C
- **Air quality in cloud-region cities**: Worst air: Mumbai (AQI 157). Cleanest: Dublin (AQI 19)
- **Earthquakes**: 54 quakes of M2.5+ in 24h. Largest: [M6.4 Mauritius - Reunion region](<https://earthquake.usgs.gov/earthquakes/eventpage/us6000ud6h>)
- **Natural hazards**: 16 open events: 8 sea and lake ice, 6 wildfires, 2 severe storms
- **Exchange rates**: 1 USD = 0.9122 EUR, 0.7635 GBP, 92.92 INR, 159.1 JPY, 19.27 MXN (ECB, 2026-11-24)

## Sources

| Source | What it tracks | Rows | Status |
| --- | --- | ---: | --- |
| [`arxiv_agent_papers`](data/arxiv_agent_papers) | Newest arXiv papers on LLM agents, agentic systems and multi-agent work. [↗](<https://arxiv.org/>) | 30 | ✅ ok |
| [`hf_daily_papers`](data/hf_daily_papers) | Papers the Hugging Face community picked today, with upvotes and linked code. [↗](<https://huggingface.co/papers>) | 50 | ✅ ok |
| [`hf_trending_models`](data/hf_trending_models) | The 30 models trending on the Hugging Face Hub. [↗](<https://huggingface.co/models?sort=trending>) | 30 | ✅ ok |
| [`hf_trending_datasets`](data/hf_trending_datasets) | The 30 datasets trending on the Hugging Face Hub. [↗](<https://huggingface.co/datasets?sort=trending>) | 30 | ✅ ok |
| [`llm_catalog`](data/llm_catalog) | Every model on OpenRouter with context window and price per million tokens; flags new models. [↗](<https://openrouter.ai/models>) | 470 | ✅ ok |
| [`github_agent_repos`](data/github_agent_repos) | Repos created this week under agent and MCP topics on GitHub, ranked by stars. [↗](<https://github.com/topics/ai-agents>) | 30 | ✅ ok |
| [`ai_framework_releases`](data/ai_framework_releases) | Latest release of the main agent, LLM-serving and model frameworks. [↗](<https://github.com/>) | 13 | ✅ ok |
| [`ai_sdk_downloads`](data/ai_sdk_downloads) | Yesterday's npm downloads for the main LLM and agent SDKs. [↗](<https://www.npmjs.com/>) | 11 | ✅ ok |
| [`data_tool_releases`](data/data_tool_releases) | Latest stable release of the core lakehouse, streaming, orchestration and query engines. [↗](<https://github.com/>) | 13 | ✅ ok |
| [`pypi_downloads`](data/pypi_downloads) | Daily, weekly and monthly PyPI downloads for data and AI libraries. [↗](<https://pypistats.org/>) | 16 | ✅ ok |
| [`docker_pulls`](data/docker_pulls) | Total Docker Hub pulls for data-platform images, with the change since the last run. [↗](<https://hub.docker.com/>) | 11 | ✅ ok |
| [`devto_data_engineering`](data/devto_data_engineering) | Today's top dev.to articles tagged dataengineering. [↗](<https://dev.to/t/dataengineering>) | 20 | ✅ ok |
| [`hackernews_front_page`](data/hackernews_front_page) | The 30 stories on the Hacker News front page at snapshot time. [↗](<https://news.ycombinator.com/>) | 30 | ✅ ok |
| [`cloud_status`](data/cloud_status) | Live status and open incidents for the data and AI platforms teams depend on. [↗](<https://www.atlassian.com/software/statuspage>) | 8 | ✅ ok |
| [`cisa_kev`](data/cisa_kev) | The 20 newest entries in CISA's catalog of vulnerabilities exploited in the wild. [↗](<https://www.cisa.gov/known-exploited-vulnerabilities-catalog>) | 20 | ✅ ok |
| [`wikipedia_top_pages`](data/wikipedia_top_pages) | Yesterday's 25 most-viewed English Wikipedia articles, from the Wikimedia pageviews API. [↗](<https://wikimedia.org/api/rest_v1/>) | 25 | ✅ ok |
| [`cloud_region_weather`](data/cloud_region_weather) | Today's forecast for Dallas and the cities behind nine major AWS regions. [↗](<https://open-meteo.com/>) | 10 | ✅ ok |
| [`air_quality`](data/air_quality) | Current US AQI, PM2.5, PM10 and ozone for the same cities. [↗](<https://open-meteo.com/en/docs/air-quality-api>) | 10 | ✅ ok |
| [`earthquakes`](data/earthquakes) | Every magnitude 2.5+ earthquake in the past 24 hours, from the USGS feed. [↗](<https://earthquake.usgs.gov/earthquakes/feed/>) | 54 | ✅ ok |
| [`natural_events`](data/natural_events) | Open wildfires, storms, volcanoes and other events NASA EONET tracked this week. [↗](<https://eonet.gsfc.nasa.gov/>) | 16 | ✅ ok |
| [`fx_rates`](data/fx_rates) | European Central Bank reference rates against the US dollar. [↗](<https://frankfurter.dev/>) | 29 | ✅ ok |

## Pipeline health

Last 14 runs, newest first.

| Date | Sources ok | Rows | Failed |
| --- | ---: | ---: | --- |
| 2026-11-24 | 21/21 | 926 | none |
| 2026-11-22 | 21/21 | 899 | none |
| 2026-11-21 | 21/21 | 917 | none |
| 2026-11-20 | 21/21 | 918 | none |
| 2026-11-19 | 21/21 | 911 | none |
| 2026-11-18 | 21/21 | 919 | none |
| 2026-11-17 | 21/21 | 920 | none |
| 2026-11-16 | 21/21 | 902 | none |
| 2026-11-15 | 21/21 | 903 | none |
| 2026-11-14 | 20/21 | 907 | `cloud_region_weather` |
| 2026-11-13 | 21/21 | 901 | none |
| 2026-11-12 | 21/21 | 901 | none |
| 2026-11-11 | 21/21 | 894 | none |
| 2026-11-10 | 21/21 | 907 | none |

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
- **Idempotent partitions.** Output goes to `data/<source>/dt=<YYYY-MM-DD>/data.jsonl`. Re-running a day overwrites that day's file, so reruns never duplicate rows.
- **Change detection.** A source can read its previous partition. The LLM catalog flags models that weren't there on the last run, and Docker pulls report the change since the last run.
- **Run manifests.** `data/_runs/dt=<YYYY-MM-DD>/manifest.json` records the status, row count, duration and any error for every source.
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
