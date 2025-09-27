# ============================================================================
# FILE: ui/components/agent_display.py
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
            "description": "Deep web analysis using Perplexity AI - searches across internet sources with citations.",
            "cost": "$0.65",
            "time": "~5 min"
        },
        "youtube": {
            "name": "Video Analysis",
            "icon": "📹",
            "description": "YouTube sentiment analysis - extracts insights from expert videos and public opinion.",
            "cost": "$0.15",
            "time": "~2 min"
        },
        "api": {
            "name": "API Agent",
            "icon": "📚",
            "description": "External data sources - fetches academic papers, news, and market data via APIs.",
            "cost": "$0.35",
            "time": "~3 min"
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

    selected_agents = []
    
    for agent_id, info in agent_info.items():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                is_selected = st.toggle(
                    f"{info['icon']} **{info['name']}**",
                    value=(agent_id in recommended),
                    key=f"agent_toggle_{agent_id}",
                    help=info['description']
                )
            with col2:
                st.markdown(f"<div style='text-align: right;'>{info['cost']} | {info['time']}</div>", unsafe_allow_html=True)

            if is_selected:
                selected_agents.append(agent_id)
                status = st.session_state.get(f'{agent_id}_status', 'idle')
                progress = st.session_state.get(f'{agent_id}_progress', 0)

                if processing and agent_id in st.session_state.get('selected_agents', []):
                    if status == 'processing':
                        st.progress(progress / 100, text=f"⏳ Processing... {progress}%")
                    elif status == 'complete':
                        st.progress(1.0, text="✅ Complete")
                    elif status == 'error':
                        st.error("❌ Error")
                    else:
                        st.progress(0, text="⏸️ Ready")
        st.markdown('</div>', unsafe_allow_html=True)

    if not selected_agents:
        st.warning("Please select at least one research source to proceed.")
    
    st.session_state.selected_agents = selected_agents
    return selected_agents