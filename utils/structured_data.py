"""Utilities for building structured research records."""
from __future__ import annotations

from typing import Any, Iterable, List, Optional


def _normalize_authors(authors: Any) -> List[str]:
    """Return a list of author strings for heterogeneous *authors* inputs."""
    if not authors:
        return []
    if isinstance(authors, str):
        return [authors]
    if isinstance(authors, Iterable):
        result: List[str] = []
        for author in authors:
            if not author:
                continue
            result.append(str(author))
        return result
    return [str(authors)]


def _format_date(value: Any) -> Optional[str]:
    """Best-effort conversion of *value* to an ISO 8601 string."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    for attr in ("isoformat",):
        if hasattr(value, attr):  # pragma: no branch - simple attr check
            try:
                return getattr(value, attr)()
            except Exception:
                continue
    if hasattr(value, "__str__"):
        try:
            return str(value)
        except Exception:
            return None
    return None


def build_structured_record(
    *,
    title: Optional[str] = None,
    content: Optional[str] = None,
    summary: Optional[str] = None,
    source: Optional[str] = None,
    published_date: Any = None,
    authors: Any = None,
    pdf_url: Optional[str] = None,
) -> dict:
    """Return a dictionary with unified research fields."""
    return {
        "published_date": _format_date(published_date),
        "title": title,
        "authors": _normalize_authors(authors),
        "summary": summary,
        "content": content,
        "source": source,
        "pdf_url": pdf_url,
    }
