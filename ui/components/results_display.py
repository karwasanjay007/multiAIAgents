# ============================================================================
# FILE: ui/components/results_display.py (ENHANCED WITH CONSOLIDATED STATS)
# ============================================================================
import streamlit as st
from typing import Dict

def render_results(results: Dict):
    """Enhanced results display with consolidated stats per agent"""
    
    st.markdown("### 📊 Research Results")
    
    # Validate results
    if not results or not isinstance(results, dict):
        st.info("No results to display")
        return
    
    # Ensure required keys exist
    if 'agent_results' not in results:
        results['agent_results'] = []
    if 'agents_used' not in results:
        results['agents_used'] = []
    if 'query' not in results:
        results['query'] = 'N/A'
    if 'domain' not in results:
        results['domain'] = 'N/A'
    
    # Custom CSS for better formatting
    st.markdown("""
    <style>
    .result-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .agent-stats-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        transition: all 0.3s ease;
    }
    .agent-stats-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    .agent-icon {
        font-size: 32px;
        margin-bottom: 8px;
    }
    .stat-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #f3f4f6;
    }
    .stat-label {
        color: #6b7280;
        font-weight: 500;
    }
    .stat-value {
        color: #1f2937;
        font-weight: 600;
    }
    .finding-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    .finding-card:hover {
        background: #e9ecef;
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .source-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
        transition: all 0.3s ease;
        background: white;
    }
    .source-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }
    .summary-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid #667eea30;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with query info
    agents_used = results.get('agents_used', [])
    st.markdown(f"""
    <div class="result-header">
        <strong>Query:</strong> {results.get('query', 'N/A')}<br>
        <strong>Domain:</strong> {results.get('domain', 'N/A').capitalize()}<br>
        <strong>Agents Used:</strong> {', '.join([a.capitalize() for a in agents_used])}
    </div>
    """, unsafe_allow_html=True)
    
    # Agent-by-Agent Stats Section
    st.markdown("### 🤖 Agent Performance Stats")
    
    agent_results = results.get('agent_results', [])
    
    if agent_results and isinstance(agent_results, list):
        # Create columns for agent cards
        num_agents = len(agent_results)
        if num_agents > 0:
            cols = st.columns(min(num_agents, 3))  # Max 3 columns
            
            agent_icons = {
                "perplexity": "🌐",
                "youtube": "📹",
                "api": "📚"
            }
            
            for idx, agent_result in enumerate(agent_results):
                col_idx = idx % 3  # Wrap to new row after 3
                
                with cols[col_idx]:
                    agent_name = str(agent_result.get('agent_name', 'Unknown'))
                    icon = agent_icons.get(agent_name, "🔹")
                    
                    # Safely get values with defaults
                    sources = agent_result.get('sources', [])
                    sources_count = len(sources) if isinstance(sources, list) else 0
                    
                    try:
                        cost = float(agent_result.get('cost', 0))
                    except (ValueError, TypeError):
                        cost = 0.0
                    
                    try:
                        tokens = int(agent_result.get('tokens', 0))
                    except (ValueError, TypeError):
                        tokens = 0
                    
                    st.markdown(f"""
                    <div class="agent-stats-card">
                        <div class="agent-icon">{icon}</div>
                        <h4 style="margin: 0 0 12px 0; color: #667eea;">{agent_name.capitalize()}</h4>
                        
                        <div class="stat-row">
                            <span class="stat-label">Sources:</span>
                            <span class="stat-value">{sources_count}</span>
                        </div>
                        
                        <div class="stat-row">
                            <span class="stat-label">Cost:</span>
                            <span class="stat-value">${cost:.6f}</span>
                        </div>
                        
                        <div class="stat-row" style="border-bottom: none;">
                            <span class="stat-label">Tokens:</span>
                            <span class="stat-value">{tokens:,}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Tabs for organized content
    tabs = st.tabs(["📝 Summary", "🔍 Key Findings", "💡 Insights", "🔗 All Sources", "📊 Raw Data"])
    
    with tabs[0]:
        # Executive Summary
        summary = results.get('summary', 'No summary available')
        
        # Clean up summary - remove HTML/XML tags and excessive whitespace
        import re
        if summary and isinstance(summary, str):
            # Remove XML/HTML tags
            summary = re.sub(r'<[^>]+>', '', summary)
            # Remove excessive whitespace
            summary = ' '.join(summary.split())
            # Limit length
            if len(summary) > 2000:
                summary = summary[:2000] + "..."
        else:
            summary = 'No summary available'
        
        st.markdown(f"""
        <div class="summary-box">
            <h4>Executive Summary</h4>
            <p style="line-height: 1.6; white-space: pre-wrap;">{summary}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[1]:
        # Key Findings
        findings = results.get('key_findings', [])
        if findings and isinstance(findings, list):
            st.markdown("#### Key Discoveries")
            for idx, finding in enumerate(findings, 1):
                # Convert to string and clean
                clean_finding = str(finding).replace('**', '').replace('*', '')
                # Remove any HTML/XML tags
                import re
                clean_finding = re.sub(r'<[^>]+>', '', clean_finding)
                
                if clean_finding.strip():
                    st.markdown(f"""
                    <div class="finding-card">
                        <strong>{idx}.</strong> {clean_finding}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No key findings available")
    
    with tabs[2]:
        # Insights
        insights = results.get('insights', [])
        if insights and isinstance(insights, list):
            st.markdown("#### Research Insights")
            for idx, insight in enumerate(insights, 1):
                # Convert to string and clean
                clean_insight = str(insight).replace('**', '').replace('*', '')
                # Remove any HTML/XML tags
                import re
                clean_insight = re.sub(r'<[^>]+>', '', clean_insight)
                
                if clean_insight.strip():
                    st.markdown(f"""
                    <div style="margin: 12px 0;">
                        <span style="display: inline-block; background: #667eea; color: white; 
                              padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-right: 8px;">
                            Insight {idx}
                        </span>
                        <span style="margin-left: 8px;">{clean_insight}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No insights generated")
    
    with tabs[3]:
        # All Sources - Organized by Agent
        st.markdown("#### Research Sources by Agent")
        
        agent_icons = {
            "perplexity": "🌐",
            "youtube": "📹",
            "api": "📚"
        }
        
        for agent_result in agent_results:
            agent_name = agent_result.get('agent_name', 'Unknown')
            sources = agent_result.get('sources', [])
            
            if sources:
                agent_icon = agent_icons.get(agent_name, "🔹")
                st.markdown(f"### {agent_icon} {agent_name.capitalize()} Agent ({len(sources)} sources)")
                
                for idx, source in enumerate(sources, 1):
                    # Safely get source properties with defaults
                    title = str(source.get('title', 'Untitled'))[:200]
                    url = str(source.get('url', '#'))
                    summary_text = str(source.get('summary', 'No description'))
                    
                    # Clean up any HTML/XML in title and summary
                    import re
                    title = re.sub(r'<[^>]+>', '', title)
                    summary_text = re.sub(r'<[^>]+>', '', summary_text)
                    
                    # Truncate summary
                    if len(summary_text) > 300:
                        summary_text = summary_text[:300] + "..."
                    
                    confidence = float(source.get('confidence', 3.0))
                    
                    # Confidence indicator
                    conf_color = "#10b981" if confidence >= 4 else "#f59e0b" if confidence >= 3 else "#ef4444"
                    conf_width = f"{min(100, (confidence / 5) * 100)}%"
                    
                    # Truncate URL for display
                    display_url = url[:80] + "..." if len(url) > 80 else url
                    
                    st.markdown(f"""
                    <div class="source-card">
                        <div style="font-weight: 600; color: #1f2937; margin-bottom: 8px;">
                            {idx}. {title}
                        </div>
                        <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none; font-size: 14px;">
                            🔗 {display_url}
                        </a>
                        <p style="margin: 12px 0 8px 0; color: #6b7280; font-size: 14px;">{summary_text}</p>
                        <div style="background: #e5e7eb; height: 4px; border-radius: 2px; margin-top: 8px;">
                            <div style="background: {conf_color}; height: 4px; width: {conf_width}; border-radius: 2px;"></div>
                        </div>
                        <span style="font-size: 12px; color: #6b7280;">Confidence: {confidence:.1f}/5</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tabs[4]:
        # Raw Data
        st.markdown("#### Complete Response Data")
        st.json(results)
    
    # Performance Metrics Footer
    st.markdown("---")
    st.markdown("### 📈 Overall Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_sources = sum(len(r.get('sources', [])) for r in agent_results)
    
    with col1:
        st.metric("📚 Total Sources", total_sources)
    with col2:
        st.metric("💰 Total Cost", f"${results.get('total_cost', 0):.6f}")
    with col3:
        st.metric("🎯 Total Tokens", f"{results.get('total_tokens', 0):,}")
    with col4:
        st.metric("⏱️ Time", f"{results.get('execution_time', 0):.1f}s")