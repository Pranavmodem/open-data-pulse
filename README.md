# open-data-pulse

[![CI](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/ci.yml/badge.svg)](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/ci.yml)
[![daily snapshot](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/daily.yml/badge.svg)](https://github.com/Pranavmodem/open-data-pulse/actions/workflows/daily.yml)
[![MIT license](https://img.shields.io/github/license/Pranavmodem/open-data-pulse)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://docs.python.org/3.12/)

A small data pipeline that takes a daily snapshot of 21 public feeds: AI research and model hubs, agent frameworks, data-engineering tool releases and adoption, platform status, security advisories, and weather, air and hazards in the cities that host the big cloud regions.

A GitHub Actions job runs it every morning. It fetches the feeds in parallel, retries what fails, writes one date-partitioned JSONL file per feed, records a run manifest, and rebuilds this README.

**Last run:** 2026-11-17 21:48 UTC

## Today's digest

### AI and agents

- **arXiv agent papers**: 30 new papers. Newest: [ViRA: Toward Ultra-High-Resolution Visual Agents via Cross-Input Relative Policy Optimization](<https://arxiv.org/abs/2611.21605v1>)
- **Hugging Face daily papers**: Top: [Sage S2.1 Flash Technical Report](<https://huggingface.co/papers/2611.21072>) (85 upvotes)
- **Hugging Face trending models**: #1: [MiniMaxAI/MiniMax-H3-Image](<https://huggingface.co/MiniMaxAI/MiniMax-H3-Image>) (text-to-image, 1.4K likes)
- **Hugging Face trending datasets**: #1: [Vyber07/cyber-security](<https://huggingface.co/datasets/Vyber07/cyber-security>) (24.0K downloads)
- **LLM catalog and prices**: 474 models, 4 new since the last run: OpenAI: GPT-6.2 Astra Pro, OpenAI: GPT-6.2 Astra, OpenAI: GPT-6.2 Sol Pro and 1 more
- **New agent and MCP repos**: Top new repo: [FrigadeHQ/yogurt](<https://github.com/FrigadeHQ/yogurt>) (2.0K stars in under a week)
- **Agent framework releases**: Latest: [Pydantic AI v2.69.0](<https://github.com/pydantic/pydantic-ai/releases/tag/v2.69.0>) (today)
- **AI SDK downloads (npm)**: Most downloaded: `@modelcontextprotocol/sdk` 14.8M, `@anthropic-ai/sdk` 11.7M, `openai` 9.8M

### Data engineering

- **Data tool releases**: Latest: [ClickHouse v26.9.31.21-stable](<https://github.com/ClickHouse/ClickHouse/releases/tag/v26.9.31.21-stable>) (today)
- **Python package downloads**: Yesterday: `pandas` 24.0M, `openai` 14.4M, `pyarrow` 13.8M, `mcp` 12.9M
- **Docker image pulls**: Most pulled since the last run: `library/postgres` (+27.7M)
- **Data engineering articles**: Top: [I Built a Serverless OLAP Engine in the Browser with DuckDB-WASM (No AWS, $0)](<https://dev.to/dayan_elvisjahuirapilco/i-built-a-serverless-olap-engine-in-the-browser-with-duckdb-wasm-no-aws-0-n27>) (20 reactions)

### Tech pulse

- **Hacker News front page**: Top: [New Evidence Shows School Phone Bans Are Gradually Improving Test Scores](<https://news.ycombinator.com/item?id=50530163>) (1076 points)
- **Platform status**: Degraded: [Cloudflare: Partially Degraded Service](<https://www.cloudflarestatus.com>); [Anthropic: Partially Degraded Service](<https://status.anthropic.com>); [OpenAI: Partial System Degradation](<https://status.openai.com>)
- **Known exploited vulnerabilities**: 3 added in the week to 2026-11-17. Newest: [CVE-2026-115731](<https://nvd.nist.gov/vuln/detail/CVE-2026-115731>) (Perforce Puppet Enterprise)
- **Most-read Wikipedia articles**: Most read: [Robert Pattinson](<https://en.wikipedia.org/wiki/Robert_Pattinson>) (1.4M), [Ramayana: Part 1](<https://en.wikipedia.org/wiki/Ramayana%3A_Part_1>) (551.9K), [Archive of Our Own](<https://en.wikipedia.org/wiki/Archive_of_Our_Own>) (463.7K)

### World signals

- **Weather in cloud-region cities**: Dallas 18°C / 5°C, clear. Hottest: Mumbai (ap-south-1) 35°C. Coldest: Columbus, OH (us-east-2) -3°C
- **Air quality in cloud-region cities**: Worst air: Mumbai (AQI 164). Cleanest: Dublin (AQI 26)
- **Earthquakes**: 45 quakes of M2.5+ in 24h. Largest: [M5.2 south of the Kermadec Islands](<https://earthquake.usgs.gov/earthquakes/eventpage/us7000tysq>)
- **Natural hazards**: 15 open events: 7 wildfires, 6 sea and lake ice, 2 severe storms
- **Exchange rates**: 1 USD = 0.91 EUR, 0.7581 GBP, 93.48 INR, 159.3 JPY, 18.46 MXN (ECB, 2026-11-17)

## Sources

| Source | What it tracks | Rows | Status |
| --- | --- | ---: | --- |
| [`arxiv_agent_papers`](data/arxiv_agent_papers) | Newest arXiv papers on LLM agents, agentic systems and multi-agent work. [↗](<https://arxiv.org/>) | 30 | ✅ ok |
| [`hf_daily_papers`](data/hf_daily_papers) | Papers the Hugging Face community picked today, with upvotes and linked code. [↗](<https://huggingface.co/papers>) | 50 | ✅ ok |
| [`hf_trending_models`](data/hf_trending_models) | The 30 models trending on the Hugging Face Hub. [↗](<https://huggingface.co/models?sort=trending>) | 30 | ✅ ok |
| [`hf_trending_datasets`](data/hf_trending_datasets) | The 30 datasets trending on the Hugging Face Hub. [↗](<https://huggingface.co/datasets?sort=trending>) | 30 | ✅ ok |
| [`llm_catalog`](data/llm_catalog) | Every model on OpenRouter with context window and price per million tokens; flags new models. [↗](<https://openrouter.ai/models>) | 474 | ✅ ok |
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
| [`earthquakes`](data/earthquakes) | Every magnitude 2.5+ earthquake in the past 24 hours, from the USGS feed. [↗](<https://earthquake.usgs.gov/earthquakes/feed/>) | 45 | ✅ ok |
| [`natural_events`](data/natural_events) | Open wildfires, storms, volcanoes and other events NASA EONET tracked this week. [↗](<https://eonet.gsfc.nasa.gov/>) | 15 | ✅ ok |
| [`fx_rates`](data/fx_rates) | European Central Bank reference rates against the US dollar. [↗](<https://frankfurter.dev/>) | 29 | ✅ ok |

## Pipeline health

Last 13 runs, newest first.

| Date | Sources ok | Rows | Failed |
| --- | ---: | ---: | --- |
| 2026-11-17 | 21/21 | 920 | none |
| 2026-11-16 | 21/21 | 902 | none |
| 2026-11-15 | 21/21 | 903 | none |
| 2026-11-14 | 20/21 | 907 | `cloud_region_weather` |
| 2026-11-13 | 21/21 | 901 | none |
| 2026-11-12 | 21/21 | 901 | none |
| 2026-11-11 | 21/21 | 894 | none |
| 2026-11-10 | 21/21 | 907 | none |
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
