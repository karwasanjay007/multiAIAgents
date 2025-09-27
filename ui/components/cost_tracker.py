# ============================================================================
# FILE: ui/components/cost_tracker.py
# ============================================================================
import streamlit as st
from config.constants import AGENT_COSTS, AGENT_TIMES

def render_cost_tracker(selected_agents: list):
    """Render cost tracking component with detailed breakdown"""
    
    # Calculate costs
    total_cost = sum(AGENT_COSTS.get(a, 0) for a in selected_agents)
    max_time = max([AGENT_TIMES.get(a, 0) for a in selected_agents]) if selected_agents else 0
    
    st.markdown("---")
    st.markdown("### 💰 Cost Tracking")
    
    # Current query cost
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Active Agents",
            len(selected_agents),
            help="Number of agents selected for this query"
        )
        st.metric(
            "Estimated Cost",
            f"${total_cost:.2f}",
            help="Total cost for selected agents"
        )
    
    with col2:
        st.metric(
            "Processing Time",
            f"~{max_time} min",
            help="Estimated time for longest running agent"
        )
        
        # Session total
        session_total = sum([c.get('cost', 0) for c in st.session_state.get('cost_history', [])])
        st.metric(
            "Session Total",
            f"${session_total:.2f}",
            help="Total cost for current session"
        )
    
    # Cost breakdown
    if selected_agents:
        with st.expander("Cost Breakdown"):
            for agent in selected_agents:
                agent_cost = AGENT_COSTS.get(agent, 0)
                agent_time = AGENT_TIMES.get(agent, 0)
                st.text(f"{agent.capitalize()}: ${agent_cost:.2f} (~{agent_time} min)")
    
    # Budget warning
    max_cost = st.session_state.get('max_cost', 2.0)
    if total_cost > max_cost:
        st.warning(f"Cost ${total_cost:.2f} exceeds budget ${max_cost:.2f}")
