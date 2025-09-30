"""Web search agent that aggregates results from multiple tooling providers."""
from __future__ import annotations

import time
from typing import Any, Dict, List

from graph.state import ResearchState
from tools.web_search_tools import duckduckgo_search, serpapi_search, tavily_search
from utils.structured_data import build_structured_record


def _normalize_results(results: Any, limit: int) -> List[Any]:
    """Coerce tool output into a bounded list for downstream structuring."""
    if isinstance(results, list):
        return results[:limit]
    if isinstance(results, str):
        return [results][:limit]
    return []


def _structure_item(item: Any) -> Dict[str, Any]:
    """Convert a raw search item into the unified research record schema."""
    if isinstance(item, dict):
        title = item.get("title") or item.get("name") or item.get("headline")
        summary = item.get("summary") or item.get("snippet") or item.get("description")
        content = (
            item.get("raw_content")
            or item.get("content")
            or item.get("full_content")
            or item.get("body")
            or item.get("text")
            or summary
            or title
        )
        source = item.get("link") or item.get("url") or item.get("source")
        published = (
            item.get("published")
            or item.get("published_date")
            or item.get("date")
            or item.get("datetime")
        )
        authors = item.get("authors") or item.get("author") or item.get("byline")
        pdf_url = item.get("pdf_url") or item.get("pdf")
    else:
        text = str(item)
        title = text[:120]
        summary = text
        content = text
        source = None
        published = None
        authors = None
        pdf_url = None
    return build_structured_record(
        title=title,
        summary=summary,
        content=content,
        source=source,
        published_date=published,
        authors=authors,
        pdf_url=pdf_url,
    )


def _structure_items(items: List[Any]) -> List[Dict[str, Any]]:
    """Vectorised helper that applies ``_structure_item`` to every entry."""
    return [_structure_item(item) for item in items]


def _fetch_tool_results(tool: Any, topic: str, limit: int) -> Dict[str, Any]:
    """Execute a tool safely and wrap its response in a predictable contract."""
    if not tool:
        return {"items": [], "error": "tool_unavailable"}
    try:
        raw = tool.run(topic)
        normalized = _normalize_results(raw, limit)
        return {"items": _structure_items(normalized)}
    except Exception as exc:  # pragma: no cover - defensive
        return {"items": [], "error": str(exc)}


def _build_source_payload(name: str, payload: Dict[str, Any], limit: int) -> Dict[str, Any]:
    """Attach metadata describing the tool invocation to structured items."""
    items = payload.get("items", [])
    metadata: Dict[str, Any] = {"limit": limit, "item_count": len(items)}
    if "error" in payload:
        metadata["error"] = payload["error"]
    return {"name": name, "items": items, "metadata": metadata}


def research_web(state: ResearchState, mode: str = "extended") -> dict:
    """Collect web search results from enabled providers for the supplied *state*."""
    start = time.time()
    topic = state.get("topic", "")
    mode_value = state.get("mode", mode)
    num_items = 2 if mode_value == "simple" else 10

    sources: List[Dict[str, Any]] = []
    for name, tool in (
        ("serpapi", serpapi_search),
        ("tavily", tavily_search),
        ("duckduckgo", duckduckgo_search),
    ):
        payload = _fetch_tool_results(tool, topic, num_items)
        sources.append(_build_source_payload(name, payload, num_items))

    elapsed = time.time() - start
    return {
        "web_results": {
            "sources": sources,
            "elapsed": elapsed,
            "tokens": 0,
            "cost": 0.0,
            "details": {"mode": mode_value, "topic": topic},
        }
    }
