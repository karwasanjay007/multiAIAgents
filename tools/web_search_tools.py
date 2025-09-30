"""Utility wrappers around third-party web search tools."""
from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun

try:
    from langchain_community.tools.searchapi import SearchAPIRun
    SERPAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    SERPAPI_AVAILABLE = False

try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    TAVILY_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    TAVILY_AVAILABLE = False

# Load API keys from the project-level .env so downstream imports can access them.
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# DuckDuckGo is always available and used both as a standalone tool and a fallback for other providers.
duckduckgo_search = DuckDuckGoSearchRun(
    name="DuckDuckGoWebSearch",
    description="Performs a web search using DuckDuckGo.",
)

searchapi_key = os.getenv("SEARCHAPI_API_KEY")
if SERPAPI_AVAILABLE and searchapi_key:
    try:
        serpapi_search = SearchAPIRun(api_wrapper_kwargs={"searchapi_api_key": searchapi_key})
    except Exception:  # pragma: no cover - network failure
        serpapi_search = None
else:
    serpapi_search = None

# Tavily provides richer results when the SDK and API key are present.
tavily_key = os.getenv("TAVILY_API_KEY")
if TAVILY_AVAILABLE and tavily_key:
    try:
        tavily_search = TavilySearchResults(api_key=tavily_key)
    except Exception:  # pragma: no cover - network failure
        tavily_search = None
else:
    tavily_search = None
