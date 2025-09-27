
# ============================================================================
# FILE: ui/pages/2_History.py
# ============================================================================
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Research History", page_icon="📚", layout="wide")

st.title("📚 Research History")
st.markdown("View and manage past research queries")

# Initialize history if not exists
if 'research_history' not in st.session_state:
    st.session_state.research_history = []

if 'cost_history' not in st.session_state:
    st.session_state.cost_history = []

# Display history
history = st.session_state.research_history

if not history:
    st.info("No research history available. Run some queries first!")
else:
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Queries", len(history))
    with col2:
        total_cost = sum([h.get('results', {}).get('total_cost', 0) for h in history])
        st.metric("Total Cost", f"${total_cost:.2f}")
    with col3:
        domains = [h.get('domain') for h in history]
        st.metric("Most Used Domain", max(set(domains), key=domains.count) if domains else "N/A")
    with col4:
        avg_time = sum([h.get('results', {}).get('execution_time', 0) for h in history]) / len(history)
        st.metric("Avg Time", f"{avg_time:.1f}s")
    
    st.markdown("---")
    
    # Filter options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("Search history", placeholder="Search by query or domain...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Cost (High to Low)", "Cost (Low to High)"])
    
    # Filter and sort history
    filtered_history = history
    
    if search_query:
        filtered_history = [
            h for h in history 
            if search_query.lower() in h.get('query', '').lower() 
            or search_query.lower() in h.get('domain', '').lower()
        ]
    
    # Sort
    if sort_by == "Newest First":
        filtered_history = sorted(filtered_history, key=lambda x: x.get('timestamp', ''), reverse=True)
    elif sort_by == "Oldest First":
        filtered_history = sorted(filtered_history, key=lambda x: x.get('timestamp', ''))
    elif sort_by == "Cost (High to Low)":
        filtered_history = sorted(filtered_history, key=lambda x: x.get('results', {}).get('total_cost', 0), reverse=True)
    else:
        filtered_history = sorted(filtered_history, key=lambda x: x.get('results', {}).get('total_cost', 0))
    
    # Display history items
    for idx, item in enumerate(filtered_history):
        timestamp = datetime.fromisoformat(item['timestamp']).strftime("%Y-%m-%d %H:%M")
        
        with st.expander(f"{timestamp} | {item.get('domain', 'N/A').capitalize()} | {item.get('query', 'No query')[:50]}..."):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Query:** {item.get('query')}")
                st.markdown(f"**Domain:** {item.get('domain', 'N/A').capitalize()}")
                
                results = item.get('results', {})
                if results:
                    st.markdown(f"**Sources:** {len(results.get('agent_results', []))}")
                    st.markdown(f"**Cost:** ${results.get('total_cost', 0):.2f}")
            
            with col2:
                if st.button("View Details", key=f"view_{idx}"):
                    st.session_state.selected_history = item
                    st.switch_page("app.py")
                
                if st.button("Delete", key=f"delete_{idx}"):
                    st.session_state.research_history.remove(item)
                    st.rerun()
    
    # Export history
    st.markdown("---")
    if st.button("Export History to CSV"):
        df = pd.DataFrame([
            {
                'Timestamp': item['timestamp'],
                'Query': item.get('query'),
                'Domain': item.get('domain'),
                'Cost': item.get('results', {}).get('total_cost', 0)
            }
            for item in history
        ])
        
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "research_history.csv",
            "text/csv"
        )
    
    # Clear history
    if st.button("Clear All History", type="secondary"):
        if st.checkbox("I understand this will delete all history"):
            st.session_state.research_history = []
            st.rerun()

