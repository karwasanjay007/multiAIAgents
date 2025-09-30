"""Academic agent helpers for collecting structured research papers."""
from __future__ import annotations

import time
from typing import Any, Dict, List

from langchain_community.embeddings import HuggingFaceEmbeddings

from src.graph.state import ResearchState
from src.tools.academic_tools import fetch_arxiv_structured, scholar_search
from src.utils.llm_registry import get_llm
from src.utils.structured_data import build_structured_record

llm = get_llm("research_assistant")
embeddings = HuggingFaceEmbeddings()


def _normalize_results(results: Any, limit: int) -> List[Any]:
    """Clamp tool output to *limit* items so downstream processing stays bounded."""
    if isinstance(results, list):
        return results[:limit]
    if isinstance(results, str):
        return [results][:limit]
    return []


def _structure_generic_item(item: Any) -> Dict[str, Any]:
    """Translate heterogeneous search records into the unified research schema."""
    if isinstance(item, dict):
        title = item.get("title") or item.get("name")
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
        source = item.get("link") or item.get("url")
        published = item.get("published") or item.get("date")
        authors = item.get("authors") or item.get("author")
    else:
        text = str(item)
        title = text[:120]
        summary = text
        content = text
        source = None
        published = None
        authors = None
    return build_structured_record(
        title=title,
        summary=summary,
        content=content,
        source=source,
        published_date=published,
        authors=authors,
    )


def _fetch_results(tool: Any, query: str, limit: int) -> Dict[str, Any]:
    """Execute *tool* with *query* and return structured items plus error context."""
    try:
        raw = tool.run(query)
        normalized = _normalize_results(raw, limit)
        structured = [_structure_generic_item(item) for item in normalized]
        return {"items": structured}
    except Exception as exc:  # pragma: no cover - defensive
        return {"items": [], "error": str(exc)}


def research_academic_papers(state: ResearchState) -> dict:
    """Collect academic search results for *state* from arXiv and Google Scholar."""
    start = time.time()
    topic = state.get("topic", "")
    mode = state.get("mode", "extended")
    num_items = 2 if mode == "simple" else 10

    arxiv_items, arxiv_error = fetch_arxiv_structured(topic, num_items)
    arxiv_metadata = {
        "limit": num_items,
        "item_count": len(arxiv_items),
    }
    if arxiv_error:
        arxiv_metadata["error"] = arxiv_error

    scholar_payload = _fetch_results(scholar_search, f"site:scholar.google.com {topic}", num_items)

    sources: List[Dict[str, Any]] = [
        {
            "name": "arxiv",
            "items": arxiv_items,
            "metadata": arxiv_metadata,
        },
        {
            "name": "scholar",
            "items": scholar_payload.get("items", []),
            "metadata": {
                "limit": num_items,
                "item_count": len(scholar_payload.get("items", [])),
                **({"error": scholar_payload["error"]} if "error" in scholar_payload else {}),
            },
        },
    ]

    elapsed = time.time() - start
    return {
        "academic_results": {
            "sources": sources,
            "elapsed": elapsed,
            "tokens": 0,
            "cost": 0.0,
            "details": {"mode": mode, "topic": topic},
        }
    }
