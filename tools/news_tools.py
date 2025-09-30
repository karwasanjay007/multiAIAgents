"""News collection utilities for web and API-backed agents."""
from __future__ import annotations

import os

from langchain_community.tools import DuckDuckGoSearchRun

try:
    from langchain_community.tools.news_api import NewsAPIWrapper
    NEWS_API_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    NEWS_API_AVAILABLE = False

news_api_key = os.getenv("NEWS_API_KEY")
if NEWS_API_AVAILABLE and news_api_key:
    news_api_tool = NewsAPIWrapper(api_key=news_api_key)
else:
    news_api_tool = None

news_search = DuckDuckGoSearchRun(
    name="NewsSearch",
    description="Searches the web for recent news articles.",
)
