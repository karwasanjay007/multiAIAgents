# ============================================================================
# FILE 3: ui/components/agent_display.py (UPDATE)
# ============================================================================
import streamlit as st
from config.constants import DOMAIN_AGENT_MAP

def render_agent_display(domain: str, processing: bool = False) -> list:
    """Render agent selection and status in a unified display."""
    
    st.markdown("### Select Research Sources")

    agent_info = {
        "perplexity": {
            "name": "Web Research",
            "icon": "🌐",
            "description": "Deep web analysis using Perplexity AI",
        },
        "youtube": {
            "name": "Video Analysis",
            "icon": "📹",
            "description": "YouTube sentiment analysis (Coming Soon)",
        },
        "api": {
            "name": "API Agent",
            "icon": "📚",
            "description": "Academic papers and news (Coming Soon)",
        }
    }

    recommended = DOMAIN_AGENT_MAP.get(domain, ["perplexity", "api"])
    
    recommendation_text = {
        "stocks": "Web Research for real-time data, API Agent for news.",
        "medical": "Web Research for latest studies and research.",
        "academic": "Web Research for papers, API Agent for citations.",
        "technology": "Web Research for latest tech news and trends."
    }
    st.info(f"**Recommended for {domain.capitalize()}:** {recommendation_text.get(domain, 'Web Research + API Agent')}")

    # Agent selection
    options = [f"{info['icon']} {info['name']}" for agent_id, info in agent_info.items()]
    default_selection = [f"{agent_info[agent_id]['icon']} {agent_info[agent_id]['name']}" for agent_id in recommended]

    selected_options = st.multiselect(
        "Select sources:",
        options=options,
        default=default_selection,
        help="Choose the sources you want to use for your research."
    )

    # Map back to agent IDs
    selected_agents = [agent_id for agent_id, info in agent_info.items() 
                      if f"{info['icon']} {info['name']}" in selected_options]

    # Show status during processing
    if processing and selected_agents:
        st.markdown("#### Agent Status")
        for agent_id in selected_agents:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{agent_info[agent_id]['icon']} {agent_info[agent_id]['name']}**")
                with col2:
                    if agent_id == "perplexity":
                        st.spinner("Searching...")
                    else:
                        st.info("Waiting...")

    if not selected_agents:
        st.warning("Please select at least one research source to proceed.")
    
    st.session_state.selected_agents = selected_agents
    return selected_agents