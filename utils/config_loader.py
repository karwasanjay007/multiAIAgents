"""Environment variable helpers shared across the project."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_openrouter_api_key() -> str | None:
    """Return the OpenRouter key used for LLM access."""
    return os.getenv("OPENROUTER_API_KEY")


def get_huggingface_api_key() -> str | None:
    """Return the HuggingFace key for embeddings or model downloads."""
    return os.getenv("HUGGINGFACE_API_KEY")


def get_perplexity_api_key() -> str | None:
    """Return the Perplexity REST API key."""
    return os.getenv("PERPLEXITY_API_KEY")


def get_youtube_api_key() -> str | None:
    """Return the YouTube Data API key."""
    return os.getenv("YOUTUBE_API_KEY")

