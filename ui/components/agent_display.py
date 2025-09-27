# ============================================================================
# FILE: ui/components/agent_display.py
# ============================================================================
import streamlit as st
from config.constants import DOMAIN_AGENT_MAP

def render_agent_display(domain: str, processing: bool = False) -> list:
    """Render agent selection and status in a unified, modern display."""
    
    st.markdown("### Select Research Sources")

    agent_info = {
        "perplexity": {
            "name": "Web Research",
            "icon": "🌐",
            "description": "Deep web analysis using Perplexity AI.",
        },
        "youtube": {
            "name": "Video Analysis",
            "icon": "📹",
            "description": "YouTube sentiment analysis.",
        },
        "api": {
            "name": "API Agent",
            "icon": "📚",
            "description": "Academic papers, news, and market data.",
        }
    }

    recommended = DOMAIN_AGENT_MAP.get(domain, ["perplexity", "api"])
    
    recommendation_text = {
        "stocks": "Web Research for real-time data, API Agent for news.",
        "medical": "All agents for comprehensive results.",
        "academic": "Web Research for new papers, API Agent for citations.",
        "technology": "Web Research for news, Video Analysis for reviews."
    }
    st.info(f"**Recommended for {domain.capitalize()}:** {recommendation_text.get(domain, 'Web Research + API Agent')}")

    # Create a list of options for the multiselect
    options = [f"{info['icon']} {info['name']}" for agent_id, info in agent_info.items()]
    
    # Map recommended agent_ids to the formatted options
    default_selection = [f"{agent_info[agent_id]['icon']} {agent_info[agent_id]['name']}" for agent_id in recommended]

    selected_options = st.multiselect(
        "Select sources:",
        options=options,
        default=default_selection,
        help="Choose the sources you want to use for your research."
    )

    # Map selected options back to agent_ids
    selected_agents = [agent_id for agent_id, info in agent_info.items() if f"{info['icon']} {info['name']}" in selected_options]

    if processing:
        progress_cols = st.columns(len(selected_agents))
        for i, agent_id in enumerate(selected_agents):
            with progress_cols[i]:
                st.write(f"**{agent_info[agent_id]['name']}**")
                status = st.session_state.get(f'{agent_id}_status', 'idle')
                progress = st.session_state.get(f'{agent_id}_progress', 0)

                if agent_id in st.session_state.get('selected_agents', []):
                    if status == 'processing':
                        st.progress(progress / 100, text=f"⏳ {progress}%")
                    elif status == 'complete':
                        st.progress(1.0, text="✅")
                    elif status == 'error':
                        st.error("❌")
                    else:
                        st.progress(0, text="...")

    if not selected_agents:
        st.warning("Please select at least one research source to proceed.")
    
    st.session_state.selected_agents = selected_agents
    return selected_agents