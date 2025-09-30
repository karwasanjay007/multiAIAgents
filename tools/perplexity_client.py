"""Client utilities for the Perplexity.ai research API."""
from __future__ import annotations

import re
import time
from typing import Any, Dict, Iterable, List, Optional

import requests

_DEFAULT_BASE_URL = "https://api.perplexity.ai"
_DEFAULT_MODEL = "sonar-pro"
_DEFAULT_TIMEOUT = 120
_BULLET_MARKERS = ("-", "*", "\u2022", "\u2023", "\u00b7")


def _safe_text(response: requests.Response) -> str:
    try:
        return response.text[:500]
    except Exception:  # pragma: no cover - defensive
        return ""


def _strip_bullet_prefix(value: str) -> str:
    stripped = value.lstrip("-*\t \u2022\u2023\u00b7")
    return stripped.lstrip("0123456789. )-\u2022\u2023\u00b7")


class PerplexityClient:
    """Lightweight client wrapping the Perplexity chat completions endpoint."""

    SUPPORTED_DOMAINS = {
        "general": "Comprehensive research across all relevant sources.",
        "stocks": "Stock market data, earnings, analyst opinions, and market trends.",
        "medical": "Peer-reviewed studies, clinical trials, and regulatory updates.",
        "academic": "Scholarly articles, research papers, and academic publications.",
        "technology": "Technology developments, product launches, and innovations.",
    }

    def __init__(self, api_key: str, *, model: str = _DEFAULT_MODEL, base_url: str = _DEFAULT_BASE_URL) -> None:
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.base_url = base_url.rstrip("/")
        self.model = model

    def deep_search(
        self,
        query: str,
        system_prompt: str,
        *,
        domain: str = "general",
        max_tokens: int = 2000,
        temperature: float = 0.2,
        top_p: float = 0.9,
    ) -> Dict[str, Any]:
        """Execute a Perplexity deep-search styled chat completion."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": True,
            "return_images": False,
        }

        url = f"{self.base_url}/chat/completions"
        start = time.perf_counter()
        try:
            response = requests.post(url, headers=self._headers, json=payload, timeout=_DEFAULT_TIMEOUT)
        except requests.RequestException as exc:
            duration = time.perf_counter() - start
            return {
                "success": False,
                "error": f"Connection error: {exc}",
                "tokens_used": 0,
                "duration": duration,
            }

        duration = time.perf_counter() - start
        if not response.ok:
            return {
                "success": False,
                "error": f"API error {response.status_code}: {_safe_text(response)}",
                "tokens_used": 0,
                "status_code": response.status_code,
                "duration": duration,
            }

        try:
            result = response.json()
        except ValueError:
            return {
                "success": False,
                "error": "Invalid JSON response from Perplexity",
                "tokens_used": 0,
                "duration": duration,
            }

        parsed = self._parse_response(result, query=query, domain=domain)
        parsed.setdefault("tokens_used", 0)
        parsed["duration"] = duration
        return parsed

    def _parse_response(self, result: Dict[str, Any], *, query: str, domain: str) -> Dict[str, Any]:
        choices = result.get("choices") or []
        if not choices:
            return {
                "success": False,
                "error": "No response choices returned",
                "tokens_used": 0,
            }

        message = choices[0].get("message", {})
        content = self._to_text(message.get("content"))
        citations = result.get("citations") or message.get("citations") or []
        usage = result.get("usage") or {}

        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or usage.get("generation_tokens") or 0)
        total_tokens = int(usage.get("total_tokens") or (prompt_tokens + completion_tokens))

        sections = self._extract_sections(content)

        return {
            "success": True,
            "query": query,
            "domain": domain,
            "content": content,
            "sections": sections,
            "sources": self._format_citations(citations),
            "citation_count": len(citations),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "tokens_used": total_tokens,
            "estimated_cost": self._estimate_cost(prompt_tokens, completion_tokens),
            "model": self.model,
            "raw": result,
        }

    @staticmethod
    def _to_text(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: List[str] = []
            for chunk in content:
                if isinstance(chunk, dict):
                    value = chunk.get("text") or chunk.get("content")
                    if value:
                        parts.append(str(value))
                elif chunk:
                    parts.append(str(chunk))
            return "\n".join(parts)
        if isinstance(content, dict):
            value = content.get("text") or content.get("content")
            if value:
                return str(value)
        return str(content or "")

    def _extract_sections(self, content: str) -> Dict[str, Any]:
        text = (content or "").replace("\r\n", "\n")
        sections = {
            "summary": "",
            "findings": [],
            "analysis": text.strip(),
            "insights": [],
            "next_steps": [],
        }
        if not text.strip():
            return sections

        summary_block = self._locate_section(text, ("Executive Summary", "Summary"))
        if summary_block:
            sections["summary"] = self._truncate_sentences(summary_block, 3)

        findings_block = self._locate_section(text, ("Key Findings", "Findings"))
        if findings_block:
            sections["findings"] = self._collect_bullets(findings_block)

        analysis_block = self._locate_section(text, ("Detailed Analysis", "Analysis", "Discussion"))
        if analysis_block:
            sections["analysis"] = analysis_block.strip()

        insights_block = self._locate_section(text, ("Insights & Implications", "Insights", "Implications"))
        if insights_block:
            sections["insights"] = self._collect_bullets(insights_block)

        next_steps_block = self._locate_section(text, ("Recommended Next Steps", "Next Steps"))
        if next_steps_block:
            sections["next_steps"] = self._collect_bullets(next_steps_block)

        if not sections["findings"]:
            sections["findings"] = self._collect_bullets(self._fallback_first_bullets(text))

        return sections

    def _locate_section(self, text: str, headers: Iterable[str]) -> Optional[str]:
        for header in headers:
            heading = re.compile(
                rf"(?im)^\s*(?:\d+\.\s*)?(?:[#*]+\s*)?\**{re.escape(header)}\**\s*:?.*$"
            )
            match = heading.search(text)
            if not match:
                continue
            start = match.end()
            remainder = text[start:]
            boundary = re.compile(r"(?im)^\s*(?:\d+\.\s*)?(?:[#*]+\s*)?\**[A-Z][^\n]{0,80}\**\s*:?.*$")
            next_match = boundary.search(remainder)
            end = next_match.start() if next_match else len(remainder)
            section_text = remainder[:end].strip()
            if section_text:
                return section_text
        return None

    def _collect_bullets(self, section_text: str) -> List[str]:
        bullets: List[str] = []
        for line in (section_text or "").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(_BULLET_MARKERS) or re.match(r"^[0-9]+[\).]", stripped):
                cleaned = _strip_bullet_prefix(stripped)
                if cleaned:
                    bullets.append(cleaned)
        return bullets

    @staticmethod
    def _fallback_first_bullets(text: str) -> str:
        lines: List[str] = []
        for line in text.splitlines():
            if len(lines) >= 6:
                break
            stripped = line.strip()
            if stripped.startswith(_BULLET_MARKERS) or re.match(r"^[0-9]+[\).]", stripped):
                lines.append(stripped)
        return "\n".join(lines)

    @staticmethod
    def _truncate_sentences(text: str, max_sentences: int) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return " ".join(sentences[:max_sentences]).strip()

    def _format_citations(self, citations: Any) -> List[Dict[str, Any]]:
        formatted: List[Dict[str, Any]] = []
        if not citations:
            return formatted
        for idx, citation in enumerate(citations, start=1):
            if isinstance(citation, str):
                formatted.append(
                    {
                        "id": idx,
                        "title": f"Source {idx}",
                        "url": citation,
                        "snippet": None,
                        "type": "web",
                    }
                )
            elif isinstance(citation, dict):
                formatted.append(
                    {
                        "id": idx,
                        "title": citation.get("title") or citation.get("source") or f"Source {idx}",
                        "url": citation.get("url") or citation.get("link"),
                        "snippet": citation.get("snippet") or citation.get("excerpt"),
                        "type": citation.get("type") or "web",
                        "metadata": {
                            k: v
                            for k, v in citation.items()
                            if k not in {"title", "url", "snippet", "excerpt", "link", "type"}
                        },
                    }
                )
        return formatted

    @staticmethod
    def _estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
        total = prompt_tokens + completion_tokens
        return (total / 1_000_000) * 1.0
