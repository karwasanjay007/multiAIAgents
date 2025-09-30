"""Perplexity-powered research agent."""
from __future__ import annotations

import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from graph.state import ResearchState
from tools.perplexity_client import PerplexityClient
from utils.config_loader import get_perplexity_api_key
from utils.llm_registry import LLMCallMetrics
from utils.structured_data import build_structured_record

_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "perplexity_prompt.txt"
_DEFAULT_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "perplexity_prompt_default.txt"
_DOMAIN_ALIASES = {
    "finance": "stocks",
    "financial": "stocks",
    "stock": "stocks",
    "stocks": "stocks",
    "health": "medical",
    "healthcare": "medical",
    "medicine": "medical",
    "tech": "technology",
}
_PERPLEXITY_SOURCE = "https://www.perplexity.ai"


class _SafeFormatDict(dict):
    """Dictionary that leaves unknown placeholders untouched during formatting."""

    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


@lru_cache(maxsize=8)
def _load_prompt_template(custom_path: Optional[str]) -> str:
    """Load the Perplexity system prompt template from disk with fallbacks."""
    candidates = []
    if custom_path:
        try:
            candidates.append(Path(custom_path))
        except (TypeError, ValueError):
            pass
    candidates.extend([_PROMPT_PATH, _DEFAULT_PROMPT_PATH])
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate.read_text(encoding='utf-8')
    tried = [str(candidate) for candidate in candidates if candidate]
    raise FileNotFoundError(
        f"Perplexity prompt template not found. Tried: {tried}."
    )


def _normalize_domain(value: str | None) -> str:
    """Map user-supplied domain names to Perplexity's supported categories."""
    if not value:
        return "general"
    key = value.strip().lower()
    if key in PerplexityClient.SUPPORTED_DOMAINS:
        return key
    return _DOMAIN_ALIASES.get(key, "general")


def _build_system_prompt(domain: str, topic: str, prompt_path: Optional[str]) -> str:
    """Insert the domain-specific focus and topic into the system prompt template."""
    template = _load_prompt_template(prompt_path)
    focus = PerplexityClient.SUPPORTED_DOMAINS.get(
        domain, PerplexityClient.SUPPORTED_DOMAINS["general"]
    )
    context = _SafeFormatDict(
        domain=domain,
        domain_focus=focus,
        topic=topic,
        query=topic,
    )
    return template.format_map(context)


def _build_overview_item(topic: str, sections: Dict[str, Any], content: str) -> Dict[str, Any]:
    """Construct the primary summary record shown to downstream agents."""
    summary = sections.get("summary") or None
    analysis = sections.get("analysis") or content
    return build_structured_record(
        title=f"Perplexity Research Summary - {topic}",
        summary=summary,
        content=analysis,
        source=_PERPLEXITY_SOURCE,
    )


def _build_citation_items(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalise Perplexity citation metadata into structured records."""
    items: List[Dict[str, Any]] = []
    for citation in citations:
        title = citation.get("title") or citation.get("url") or "Perplexity Source"
        summary = citation.get("snippet") or None
        url = citation.get("url") or None
        meta = citation.get("metadata") or {}
        items.append(
            build_structured_record(
                title=title,
                summary=summary,
                source=url,
                content=meta.get("summary"),
            )
        )
    return items


def _sections_metadata(sections: Dict[str, Any]) -> Dict[str, Any]:
    """Extract supporting metadata derived from the Perplexity section parsing."""
    return {
        "key_findings": sections.get("findings") or [],
        "insights": sections.get("insights") or [],
        "next_steps": sections.get("next_steps") or [],
    }


def research_perplexity(state: ResearchState) -> Dict[str, Dict[str, Any]]:
    """Run a Perplexity deep-search and map the result into the research graph state."""
    overall_start = time.perf_counter()
    topic = (state.get("topic") or "").strip()
    if not topic:
        elapsed = time.perf_counter() - overall_start
        return {
            "perplexity_results": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": "Topic is required"},
            }
        }

    api_key = get_perplexity_api_key()
    if not api_key:
        elapsed = time.perf_counter() - overall_start
        return {
            "perplexity_results": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": "PERPLEXITY_API_KEY not configured"},
            }
        }

    domain = _normalize_domain(state.get("perplexity_domain") or state.get("domain"))
    domain_label = state.get("domain_label")
    mode = state.get("mode", "extended")
    max_tokens = 900 if mode == "simple" else 2200

    client = PerplexityClient(api_key)
    prompt_path = state.get("perplexity_prompt_path")
    system_prompt = _build_system_prompt(domain, topic, prompt_path)
    response = client.deep_search(
        topic,
        system_prompt,
        domain=domain,
        max_tokens=max_tokens,
    )
    elapsed = time.perf_counter() - overall_start

    if not response.get("success"):
        return {
            "perplexity_results": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {
                    "error": response.get("error", "Perplexity request failed"),
                    "domain": domain,
                    "status_code": response.get("status_code"),
                },
            }
        }

    sections: Dict[str, Any] = response.get("sections", {})
    sources_payload = response.get("sources") or []
    metrics = LLMCallMetrics(
        name="perplexity_researcher",
        model=str(response.get("model", "perplexity/sonar-pro")),
        prompt_tokens=int(response.get("prompt_tokens", 0) or 0),
        completion_tokens=int(response.get("completion_tokens", 0) or 0),
        total_tokens=int(response.get("tokens_used", 0) or 0),
        cost=float(response.get("estimated_cost", 0.0) or 0.0),
        duration=float(response.get("duration", 0.0) or 0.0),
        truncated=False,
    )
    tokens_per_second = metrics.total_tokens / metrics.duration if metrics.duration else None

    overview_item = _build_overview_item(topic, sections, response.get("content", ""))
    citation_items = _build_citation_items(sources_payload)

    overview_metadata = {
        "domain": domain,
        "domain_focus": PerplexityClient.SUPPORTED_DOMAINS.get(
            domain, PerplexityClient.SUPPORTED_DOMAINS["general"]
        ),
        **_sections_metadata(sections),
        "model": metrics.model,
    }
    if domain_label:
        overview_metadata["domain_label"] = str(domain_label)

    sources: List[Dict[str, Any]] = [
        {
            "name": "perplexity_overview",
            "items": [overview_item],
            "metadata": overview_metadata,
        }
    ]

    if citation_items:
        citation_metadata = {
            "domain": domain,
            "citation_count": len(citation_items),
        }
        if domain_label:
            citation_metadata["domain_label"] = str(domain_label)
        sources.append(
            {
                "name": "perplexity_citations",
                "items": citation_items,
                "metadata": citation_metadata,
            }
        )

    details: Dict[str, Any] = {
        "domain": domain,
        "mode": mode,
        "model": metrics.model,
        "prompt_tokens": metrics.prompt_tokens,
        "completion_tokens": metrics.completion_tokens,
        "call_duration": metrics.duration,
        "citation_count": response.get("citation_count", 0),
    }
    if domain_label:
        details["domain_label"] = str(domain_label)
    if tokens_per_second is not None:
        details["tokens_per_second"] = tokens_per_second

    return {
        "perplexity_results": {
            "sources": sources,
            "elapsed": elapsed,
            "tokens": metrics.total_tokens,
            "cost": metrics.cost,
            "details": details,
        }
    }



