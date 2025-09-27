# ============================================================================
# FILE 4: config/constants.py (UPDATE)
# ============================================================================
DOMAIN_AGENT_MAP = {
    "technology": ["perplexity", "youtube"],
    "medical": ["perplexity", "api"],
    "stocks": ["perplexity", "api"],
    "academic": ["perplexity", "api"],
}

# Cost per agent (approximate per query)
AGENT_COSTS = {
    "perplexity": 0.001,  # ~$1 per 1M tokens, avg 1000 tokens
    "youtube": 0.15,
    "api": 0.35,
}

AGENT_TIMES = {
    "perplexity": 5,  # minutes
    "youtube": 2,
    "api": 3,
}