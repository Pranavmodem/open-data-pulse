"""AI and agents: research papers, model hubs, the LLM catalog, agent repos and SDK adoption."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from pipeline import http
from pipeline.core import Context, Source
from pipeline.markdown import link, number, text
from pipeline.sources.common import collect, latest_release, release_highlight

CATEGORY = "AI and agents"
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivAgentPapers(Source):
    name = "arxiv_agent_papers"
    title = "arXiv agent papers"
    category = CATEGORY
    description = "Newest arXiv papers on LLM agents, agentic systems and multi-agent work."
    homepage = "https://arxiv.org/"

    QUERY = ('(abs:"LLM agent" OR abs:agentic OR abs:"multi-agent") '
             "AND (cat:cs.AI OR cat:cs.CL OR cat:cs.LG OR cat:cs.MA)")

    def fetch(self, ctx: Context) -> list[dict]:
        feed = ET.fromstring(http.get("https://export.arxiv.org/api/query", {
            "search_query": self.QUERY, "sortBy": "submittedDate", "sortOrder": "descending", "max_results": 30,
        }))
        rows = []
        for entry in feed.findall("a:entry", ATOM):
            url = entry.findtext("a:id", "", ATOM).replace("http://", "https://", 1)
            authors = [a.findtext("a:name", "", ATOM) for a in entry.findall("a:author", ATOM)]
            category = entry.find("arxiv:primary_category", ATOM)
            rows.append({
                "arxiv_id": url.rsplit("/", 1)[-1],
                "title": " ".join(entry.findtext("a:title", "", ATOM).split()),
                "published_at": entry.findtext("a:published", "", ATOM),
                "primary_category": category.get("term") if category is not None else None,
                "authors": authors[:5],
                "author_count": len(authors),
                "url": url,
            })
        return rows

    def highlight(self, rows):
        return f"{len(rows)} new papers. Newest: {link(rows[0]['title'], rows[0]['url'])}"


class HuggingFaceDailyPapers(Source):
    name = "hf_daily_papers"
    title = "Hugging Face daily papers"
    category = CATEGORY
    description = "Papers the Hugging Face community picked today, with upvotes and linked code."
    homepage = "https://huggingface.co/papers"

    def fetch(self, ctx: Context) -> list[dict]:
        rows = [{
            "paper_id": item["paper"]["id"],
            "title": item["paper"]["title"],
            "upvotes": item["paper"].get("upvotes", 0),
            "comments": item.get("numComments", 0),
            "published_at": item["paper"].get("publishedAt"),
            "github_repo": item["paper"].get("githubRepo"),
            "keywords": (item["paper"].get("ai_keywords") or [])[:6],
            "url": f"https://huggingface.co/papers/{item['paper']['id']}",
        } for item in http.get_json("https://huggingface.co/api/daily_papers", {"limit": 50})]
        return sorted(rows, key=lambda r: r["upvotes"], reverse=True)

    def highlight(self, rows):
        top = rows[0]
        return f"Top: {link(top['title'], top['url'])} ({top['upvotes']} upvotes)"


class HuggingFaceTrendingModels(Source):
    name = "hf_trending_models"
    title = "Hugging Face trending models"
    category = CATEGORY
    description = "The 30 models trending on the Hugging Face Hub."
    homepage = "https://huggingface.co/models?sort=trending"

    def fetch(self, ctx: Context) -> list[dict]:
        models = http.get_json("https://huggingface.co/api/models",
                               {"sort": "trendingScore", "direction": -1, "limit": 30})
        return [{
            "rank": rank,
            "model_id": m["id"],
            "task": m.get("pipeline_tag"),
            "library": m.get("library_name"),
            "likes": m.get("likes"),
            "downloads": m.get("downloads"),
            "trending_score": m.get("trendingScore"),
            "created_at": m.get("createdAt"),
            "url": f"https://huggingface.co/{m['id']}",
        } for rank, m in enumerate(models, 1)]

    def highlight(self, rows):
        top = rows[0]
        return f"#1: {link(top['model_id'], top['url'])} ({top['task'] or 'model'}, {number(top['likes'])} likes)"


class HuggingFaceTrendingDatasets(Source):
    name = "hf_trending_datasets"
    title = "Hugging Face trending datasets"
    category = CATEGORY
    description = "The 30 datasets trending on the Hugging Face Hub."
    homepage = "https://huggingface.co/datasets?sort=trending"

    def fetch(self, ctx: Context) -> list[dict]:
        datasets = http.get_json("https://huggingface.co/api/datasets",
                                 {"sort": "trendingScore", "direction": -1, "limit": 30})
        return [{
            "rank": rank,
            "dataset_id": d["id"],
            "likes": d.get("likes"),
            "downloads": d.get("downloads"),
            "trending_score": d.get("trendingScore"),
            "created_at": d.get("createdAt"),
            "url": f"https://huggingface.co/datasets/{d['id']}",
        } for rank, d in enumerate(datasets, 1)]

    def highlight(self, rows):
        top = rows[0]
        return f"#1: {link(top['dataset_id'], top['url'])} ({number(top['downloads'])} downloads)"


class LlmCatalog(Source):
    name = "llm_catalog"
    title = "LLM catalog and prices"
    category = CATEGORY
    description = "Every model on OpenRouter with context window and price per million tokens; flags new models."
    homepage = "https://openrouter.ai/models"

    def fetch(self, ctx: Context) -> list[dict]:
        known = {r["model_id"] for r in ctx.previous_rows(self.name)}
        rows = []
        for m in http.get_json("https://openrouter.ai/api/v1/models")["data"]:
            pricing = m.get("pricing") or {}
            rows.append({
                "model_id": m["id"],
                "name": m.get("name"),
                "created_at": datetime.fromtimestamp(m.get("created") or 0, timezone.utc).isoformat(),
                "context_length": m.get("context_length"),
                "modality": (m.get("architecture") or {}).get("modality"),
                "prompt_usd_per_mtok": _per_million(pricing.get("prompt")),
                "completion_usd_per_mtok": _per_million(pricing.get("completion")),
                "is_new": m["id"] not in known if known else None,
            })
        return sorted(rows, key=lambda r: r["created_at"], reverse=True)

    def highlight(self, rows):
        new = [r for r in rows if r["is_new"]]
        if new:
            names = ", ".join(text(r["name"] or r["model_id"], 50) for r in new[:3])
            more = f" and {len(new) - 3} more" if len(new) > 3 else ""
            return f"{len(rows)} models, {len(new)} new since the last run: {names}{more}"
        m = rows[0]
        price = (f", ${m['prompt_usd_per_mtok']:g} in / ${m['completion_usd_per_mtok']:g} out per 1M tokens"
                 if m["prompt_usd_per_mtok"] is not None and m["completion_usd_per_mtok"] is not None else "")
        return f"{len(rows)} models. Newest: {text(m['name'] or m['model_id'], 60)} ({number(m['context_length'])} context{price})"


class GithubAgentRepos(Source):
    name = "github_agent_repos"
    title = "New agent and MCP repos"
    category = CATEGORY
    description = "Repos created this week under agent and MCP topics on GitHub, ranked by stars."
    homepage = "https://github.com/topics/ai-agents"

    TOPICS = ["ai-agents", "agents", "agentic-ai", "llm-agent", "mcp", "mcp-server"]

    def fetch(self, ctx: Context) -> list[dict]:
        since = ctx.day - timedelta(days=7)
        repos = {}
        for topic in self.TOPICS:
            found = http.get_json("https://api.github.com/search/repositories", {
                "q": f"topic:{topic} created:>={since}", "sort": "stars", "order": "desc", "per_page": 20,
            })
            for r in found["items"]:
                repos[r["full_name"]] = {
                    "repo": r["full_name"],
                    "description": (r.get("description") or "")[:200],
                    "stars": r["stargazers_count"],
                    "forks": r["forks_count"],
                    "language": r.get("language"),
                    "topics": r.get("topics", [])[:8],
                    "created_at": r["created_at"],
                    "url": r["html_url"],
                }
        return sorted(repos.values(), key=lambda r: r["stars"], reverse=True)[:30]

    def highlight(self, rows):
        top = rows[0]
        return f"Top new repo: {link(top['repo'], top['url'])} ({number(top['stars'])} stars in under a week)"


class AiFrameworkReleases(Source):
    name = "ai_framework_releases"
    title = "Agent framework releases"
    category = CATEGORY
    description = "Latest release of the main agent, LLM-serving and model frameworks."
    homepage = "https://github.com/"

    REPOS = {
        "LangChain": "langchain-ai/langchain",
        "LangGraph": "langchain-ai/langgraph",
        "LlamaIndex": "run-llama/llama_index",
        "CrewAI": "crewAIInc/crewAI",
        "AutoGen": "microsoft/autogen",
        "OpenAI Agents SDK": "openai/openai-agents-python",
        "Claude Agent SDK": "anthropics/claude-agent-sdk-python",
        "Pydantic AI": "pydantic/pydantic-ai",
        "smolagents": "huggingface/smolagents",
        "MCP Python SDK": "modelcontextprotocol/python-sdk",
        "vLLM": "vllm-project/vllm",
        "Ollama": "ollama/ollama",
        "Transformers": "huggingface/transformers",
    }

    def fetch(self, ctx: Context) -> list[dict]:
        return collect(self.REPOS.items(), lambda item: latest_release(*item, ctx.day))

    def highlight(self, rows):
        return release_highlight(rows)


class AiSdkDownloads(Source):
    name = "ai_sdk_downloads"
    title = "AI SDK downloads (npm)"
    category = CATEGORY
    description = "Yesterday's npm downloads for the main LLM and agent SDKs."
    homepage = "https://www.npmjs.com/"

    PACKAGES = [
        "@anthropic-ai/sdk", "@anthropic-ai/claude-agent-sdk", "openai", "@openai/agents", "ai",
        "@modelcontextprotocol/sdk", "langchain", "@langchain/core", "@langchain/langgraph",
        "@google/genai", "@mastra/core",
    ]

    def fetch(self, ctx: Context) -> list[dict]:
        def one(package: str) -> dict:
            d = http.get_json(f"https://api.npmjs.org/downloads/point/last-day/{package}")
            return {"package": package, "downloads": d["downloads"], "day": d["end"]}

        return sorted(collect(self.PACKAGES, one), key=lambda r: r["downloads"], reverse=True)

    def highlight(self, rows):
        return "Most downloaded: " + ", ".join(f"`{r['package']}` {number(r['downloads'])}" for r in rows[:3])


def _per_million(price: str | None) -> float | None:
    try:
        value = float(price)
    except (TypeError, ValueError):
        return None
    return round(value * 1_000_000, 4) if value >= 0 else None


SOURCES = [
    ArxivAgentPapers(), HuggingFaceDailyPapers(), HuggingFaceTrendingModels(), HuggingFaceTrendingDatasets(),
    LlmCatalog(), GithubAgentRepos(), AiFrameworkReleases(), AiSdkDownloads(),
]
