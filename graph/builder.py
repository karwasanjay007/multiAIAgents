"""Graph builder for the research workflow."""
from langgraph.graph import StateGraph, END

from graph.state import ResearchState
from agents.orchestrator import create_research_plan
from agents.web_researcher import research_web
from agents.academic_researcher import research_academic_papers
from agents.news_analyzer import analyze_news
from agents.social_analyzer import analyze_social
from agents.financial_analyzer import analyze_financial
from agents.perplexity_researcher import research_perplexity
from agents.youtube_researcher import analyze_youtube
from agents.cleanup_agent import cleanup_archives
from agents.data_archiver import archive_state
from agents.vector_pipeline import store_in_vector_db, retrieve_from_vector_db
from agents.synthesizer import generate_final_report


# Mapping between conditional branch names and agent node identifiers.
PARALLEL_BRANCHES = {
    "parallel_web": "web_researcher",
    "parallel_academic": "academic_researcher",
    "parallel_news": "news_analyzer",
    "parallel_social": "social_analyzer",
    "parallel_financial": "financial_analyzer",
    "parallel_perplexity": "perplexity_researcher",
    "parallel_youtube": "youtube_researcher",
}


def orchestrator_fan_out(state: ResearchState) -> list[str]:
    """Return branch keys for the selected research agents in *state*."""
    selected = state.get("selected_agents") or []
    if selected:
        branches = [name for name, agent in PARALLEL_BRANCHES.items() if agent in selected]
        if branches:
            return branches
    return list(PARALLEL_BRANCHES.keys())


def build_graph():
    """Compile the research workflow graph with conditional parallel branches."""
    workflow = StateGraph(ResearchState)

    workflow.add_node("orchestrator", create_research_plan)
    workflow.add_node("web_researcher", research_web)
    workflow.add_node("academic_researcher", research_academic_papers)
    workflow.add_node("news_analyzer", analyze_news)
    workflow.add_node("social_analyzer", analyze_social)
    workflow.add_node("financial_analyzer", analyze_financial)
    workflow.add_node("perplexity_researcher", research_perplexity)
    workflow.add_node("youtube_researcher", analyze_youtube)
    workflow.add_node("cleanup", cleanup_archives)
    workflow.add_node("data_archiver", archive_state)
    workflow.add_node("vector_store", store_in_vector_db)
    workflow.add_node("rag_retriever", retrieve_from_vector_db)
    workflow.add_node("synthesizer", generate_final_report)

    workflow.set_entry_point("orchestrator")

    workflow.add_conditional_edges(
        "orchestrator",
        orchestrator_fan_out,
        PARALLEL_BRANCHES,
    )

    workflow.add_edge("web_researcher", "cleanup")
    workflow.add_edge("academic_researcher", "cleanup")
    workflow.add_edge("news_analyzer", "cleanup")
    workflow.add_edge("social_analyzer", "cleanup")
    workflow.add_edge("financial_analyzer", "cleanup")
    workflow.add_edge("perplexity_researcher", "cleanup")
    workflow.add_edge("youtube_researcher", "cleanup")

    workflow.add_edge("cleanup", "data_archiver")
    workflow.add_edge("data_archiver", "vector_store")
    workflow.add_edge("vector_store", "rag_retriever")
    workflow.add_edge("rag_retriever", "synthesizer")
    workflow.add_edge("synthesizer", END)

    app = workflow.compile()
    print("Agentic Research Graph Compiled!")
    return app