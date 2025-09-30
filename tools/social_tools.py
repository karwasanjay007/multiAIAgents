"""Social media scraping helpers for sentiment analysis."""
from __future__ import annotations

import os
from typing import List

import requests

from src.utils.structured_data import build_structured_record

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


def twitter_search(query: str, max_results: int = 10) -> List[dict]:
    """Return recent tweets for a query as structured research records."""
    if not TWITTER_BEARER_TOKEN:
        return []
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "created_at,author_id,text",
        "expansions": "author_id",
        "user.fields": "name,username",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    if resp.status_code != 200:
        return []

    data = resp.json()
    tweets = data.get("data", [])
    users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}

    structured = []
    for tweet in tweets:
        author_id = tweet.get("author_id")
        user = users.get(author_id)
        if user:
            authors = [user.get("name") or user.get("username") or author_id]
            username = user.get("username")
        else:
            authors = [author_id] if author_id else []
            username = None
        tweet_url = (
            f"https://twitter.com/{username}/status/{tweet['id']}"
            if username
            else f"https://twitter.com/i/web/status/{tweet['id']}"
        )
        text = tweet.get("text", "")
        structured.append(
            build_structured_record(
                title=text[:120] if text else None,
                summary=text,
                content=text,
                source=tweet_url,
                published_date=tweet.get("created_at"),
                authors=authors,
            )
        )
    return structured
