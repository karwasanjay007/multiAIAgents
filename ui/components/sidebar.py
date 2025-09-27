"""
Complete UI Components for Multi-Agent AI Deep Researcher
Save each section to its respective file
"""

# ============================================================================
# FILE: ui/components/sidebar.py
# ============================================================================
import streamlit as st
from datetime import datetime

def render_sidebar():
    """Render sidebar with settings and information"""
    
    st.title("Settings")
    st.markdown("---")
    
    # About section
    st.subheader("About")
    st.info(
        "Multi-Agent AI Deep Researcher uses specialized agents "
        "to conduct comprehensive research across multiple sources."
    )
    
    # Configuration section
    with st.expander("Configuration", expanded=False):
        st.session_state.mock_mode = st.toggle("Mock Mode", value=False, help="Enable mock mode to simulate research without actual costs.")
        max_sources = st.slider("Max Sources per Agent", 5, 50, 10)
        timeout = st.slider("Timeout (minutes)", 1, 10, 5)
        st.session_state.max_sources = max_sources
        st.session_state.timeout = timeout
    
    # Cost settings
    with st.expander("Cost Settings", expanded=False):
        max_cost = st.number_input("Max Cost per Query ($)", 0.1, 10.0, 2.0, 0.1)
        st.session_state.max_cost = max_cost
        
        if st.button("Reset Cost History"):
            st.session_state.cost_history = []
            st.success("Cost history cleared")
    
    # Statistics
    st.markdown("---")
    st.subheader("Statistics")
    
    total_queries = len(st.session_state.get('cost_history', []))
    total_cost = sum([c.get('cost', 0) for c in st.session_state.get('cost_history', [])])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", total_queries)
    with col2:
        st.metric("Total Cost", f"${total_cost:.2f}")
    
    # Footer
    st.markdown("---")
    st.caption(f"v0.1.0 | {datetime.now().strftime('%Y-%m-%d')}")
    
    # Clear all button
    if st.button("Clear All Data", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()