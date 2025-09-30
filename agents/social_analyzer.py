"""Social sentiment agent that wraps Twitter lookups."""
from __future__ import annotations

import time
from typing import Dict

from graph.state import ResearchState
from tools.social_tools import twitter_search


def analyze_social(state: ResearchState) -> dict:
    """Collect recent tweets for *state* and package them for downstream use."""
    start = time.time()
    topic = state.get("topic", "")
    mode = state.get("mode", "extended")
    num_items = 2 if mode == "simple" else 10
    tweets = twitter_search(topic, max_results=num_items)

    elapsed = time.time() - start
    return {
        "social_sentiment": {
            "sources": [
                {
                    "name": "twitter",
                    "items": tweets,
                    "metadata": {
                        "limit": num_items,
                        "item_count": len(tweets),
                        "query": topic,
                    },
                }
            ],
            "elapsed": elapsed,
            "tokens": 0,
            "cost": 0.0,
            "details": {"mode": mode, "topic": topic},
        }
    }
