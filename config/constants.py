# ============================================================================
# FILE 3: Update config/constants.py
# ============================================================================
# Update the AGENT_COSTS to reflect actual Perplexity pricing

DOMAIN_AGENT_MAP = {
    "technology": ["perplexity", "youtube"],
    "medical": ["perplexity", "youtube", "api"],
    "stocks": ["perplexity", "api"],
    "academic": ["perplexity", "api"],
}

# Updated costs based on actual Perplexity pricing
# sonar-pro: $1 per 1M tokens (both input and output)
AGENT_COSTS = {
    "perplexity": 0.001,  # Approximate per request (~1000 tokens)
    "youtube": 0.15,
    "api": 0.35,
}

AGENT_TIMES = {
    "perplexity": 5,
    "youtube": 2,
    "api": 3,
}