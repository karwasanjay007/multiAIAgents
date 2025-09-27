# In config/constants.py

# Maps research domains to a list of recommended agent IDs.
# These IDs correspond to the agent checkboxes in ui/components/agent_selector.py
DOMAIN_AGENT_MAP = {
    "technology": ["perplexity", "youtube"],
    "medical": ["perplexity", "youtube", "api"],
    "stocks": ["perplexity", "api"],
    "academic": ["perplexity", "api"],
}

# Maps agent IDs to their estimated cost per run.
AGENT_COSTS = {
    "perplexity": 0.65,
    "youtube": 0.15,
    "api": 0.35,
}

# Maps agent IDs to their estimated processing time in minutes.
AGENT_TIMES = {
    "perplexity": 5,
    "youtube": 2,
    "api": 3,
}