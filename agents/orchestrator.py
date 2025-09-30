"""Planning utilities for orchestrating the research workflow."""
from __future__ import annotations

from graph.state import ResearchState


def create_research_plan(state: ResearchState) -> dict:
    """Build a human-readable plan outlining which agents will run for *state*."""
    topic = state.get("topic", "")
    plan = (
        f"Research plan for topic: {topic}\n"
        "- Web research\n"
        "- Academic papers\n"
        "- News\n"
        "- Social sentiment\n"
        "- Financial data (if relevant)"
    )
    return {"research_plan": plan}
