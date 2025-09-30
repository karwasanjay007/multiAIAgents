"""Academic research helper tools used by the agent suite."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from langchain_community.tools import ArxivQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper

from src.utils.structured_data import build_structured_record

__all__ = ["arxiv_tool", "scholar_search", "fetch_arxiv_structured"]

# Provide a high-level arXiv wrapper that returns full metadata for downstream processing.
arxiv_tool = ArxivQueryRun(load_all_available_meta=True, doc_content_chars_max=None)

# DuckDuckGo search tuned for Google Scholar results grants broad academic coverage without an API key.
scholar_search = DuckDuckGoSearchRun(
    name="GoogleScholarSearch",
    description="Searches Google Scholar for academic papers.",
)


def fetch_arxiv_structured(query: str, max_results: int) -> Tuple[List[Dict[str, Any]], str | None]:
    """Return arXiv papers as unified structured records."""
    wrapper = ArxivAPIWrapper(
        top_k_results=max_results,
        load_all_available_meta=True,
        continue_on_failure=True,
        doc_content_chars_max=None,
    )
    try:
        search_results = list(wrapper._fetch_results(query))  # type: ignore[attr-defined]
    except Exception as exc:  # pragma: no cover - third-party failure
        return [], str(exc)

    # Attempt to fetch full text where available so downstream summarisation has richer context.
    content_map: Dict[str, str] = {}
    if search_results:
        try:
            fulltext_wrapper = ArxivAPIWrapper(
                top_k_results=max_results,
                load_all_available_meta=True,
                continue_on_failure=True,
                doc_content_chars_max=None,
            )
            for doc in fulltext_wrapper.load(query):
                title = doc.metadata.get("Title")
                if title and doc.page_content:
                    content_map.setdefault(title, doc.page_content)
        except Exception:  # pragma: no cover - optional dependency (PyMuPDF)
            pass

    structured_results: List[Dict[str, Any]] = []
    for result in search_results:
        published = getattr(result, "published", None)
        if published is not None and hasattr(published, "date"):
            published_str = published.date().isoformat()
        elif published is not None:
            published_str = str(published)
        else:
            published_str = None

        authors = [
            getattr(author, "name", str(author))
            for author in getattr(result, "authors", [])
            if getattr(author, "name", str(author))
        ]
        title = getattr(result, "title", "")
        summary = getattr(result, "summary", "")
        content = content_map.get(title) or summary
        structured_results.append(
            build_structured_record(
                title=title,
                summary=summary,
                content=content,
                source=getattr(result, "entry_id", ""),
                published_date=published_str,
                authors=authors,
                pdf_url=getattr(result, "pdf_url", None),
            )
        )

    return structured_results, None
