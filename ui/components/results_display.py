# ============================================================================
# FILE: ui/components/results_display.py
# ============================================================================
import streamlit as st
import json
from typing import Dict, List

def render_results(results: Dict):
    """Render research results with structured display"""
    
    st.markdown("### 📊 Research Results")
    
    if not results:
        st.info("No results to display")
        return
    
    # Display query info
    st.markdown(f"**Query:** {results.get('query', 'N/A')}")
    st.markdown(f"**Domain:** {results.get('domain', 'N/A').capitalize()}")
    
    st.markdown("---")
    
    # Tabs for different result types
    tabs = st.tabs(["Summary", "Sources", "Insights", "Raw Data"])
    
    with tabs[0]:
        # Summary tab
        st.subheader("Executive Summary")
        summary = results.get('summary', 'No summary available')
        st.markdown(summary)
        
        # Key findings
        if 'key_findings' in results:
            st.subheader("Key Findings")
            for idx, finding in enumerate(results['key_findings'], 1):
                st.markdown(f"{idx}. {finding}")
    
    with tabs[1]:
        # Sources tab
        st.subheader("Sources")
        
        agent_results = results.get('agent_results', [])
        
        for agent_result in agent_results:
            agent_name = agent_result.get('agent_name', 'Unknown')
            sources = agent_result.get('sources', [])
            
            if sources:
                st.markdown(f"**{agent_name.capitalize()} Agent**")
                
                for idx, source in enumerate(sources, 1):
                    with st.expander(f"Source {idx}: {source.get('title', 'Untitled')}"):
                        st.markdown(f"**Summary:** {source.get('summary', 'N/A')}")
                        
                        if source.get('url'):
                            st.markdown(f"**Link:** [{source['url']}]({source['url']})")
                        
                        if source.get('confidence'):
                            st.progress(source['confidence'] / 5.0)
                            st.caption(f"Confidence: {source['confidence']}/5")
                        
                        if source.get('date'):
                            st.caption(f"Date: {source['date']}")
    
    with tabs[2]:
        # Insights tab
        st.subheader("Generated Insights")
        
        insights = results.get('insights', [])
        if insights:
            for idx, insight in enumerate(insights, 1):
                st.markdown(f"**Insight {idx}**")
                st.info(insight)
        else:
            st.write("No insights generated")
        
        # Contradictions
        if 'contradictions' in results:
            st.subheader("Contradictions Detected")
            for contradiction in results['contradictions']:
                st.warning(contradiction)
    
    with tabs[3]:
        # Raw data tab
        st.subheader("Raw Data")
        st.json(results)
    
    # Metadata footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sources", len(agent_results))
    with col2:
        st.metric("Total Cost", f"${results.get('total_cost', 0):.2f}")
    with col3:
        st.metric("Execution Time", f"{results.get('execution_time', 0):.1f}s")
