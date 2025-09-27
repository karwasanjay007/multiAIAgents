# ============================================================================
# FILE 1: ui/components/cost_tracker.py (ENHANCED VERSION)
# ============================================================================
import streamlit as st
from config.constants import AGENT_COSTS, AGENT_TIMES

def render_cost_tracker(selected_agents: list):
    """Enhanced cost tracking with actual vs estimated comparison"""
    
    # Calculate estimates
    estimated_cost = sum(AGENT_COSTS.get(a, 0) for a in selected_agents)
    max_time = max([AGENT_TIMES.get(a, 0) for a in selected_agents]) if selected_agents else 0
    
    st.markdown("---")
    st.markdown("### 💰 Cost & Performance Metrics")
    
    # Get actual results if available
    results = st.session_state.get('research_results', {})
    actual_cost = results.get('total_cost', 0)
    actual_tokens = results.get('total_tokens', 0)
    actual_time = results.get('execution_time', 0)
    
    has_results = actual_cost > 0 or actual_tokens > 0
    
    if has_results:
        # Show comparison cards for completed research
        st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .metric-label {
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 600;
            margin: 8px 0;
        }
        .metric-comparison {
            font-size: 14px;
            opacity: 0.85;
        }
        .metric-good {
            color: #10b981;
        }
        .metric-warning {
            color: #f59e0b;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Cost Comparison
        cost_diff = actual_cost - estimated_cost
        cost_diff_pct = (cost_diff / estimated_cost * 100) if estimated_cost > 0 else 0
        cost_color = "metric-good" if cost_diff <= 0 else "metric-warning"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💵 Total Cost</div>
            <div class="metric-value">${actual_cost:.6f}</div>
            <div class="metric-comparison">
                Estimated: ${estimated_cost:.6f} 
                <span class="{cost_color}">
                    ({'+' if cost_diff > 0 else ''}{cost_diff_pct:.1f}%)
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tokens Used
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">🎯 Tokens Consumed</div>
            <div class="metric-value">{actual_tokens:,}</div>
            <div class="metric-comparison">
                Active Agents: {len(selected_agents)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Execution Time
        time_diff = actual_time - (max_time * 60)  # Convert minutes to seconds
        time_color = "metric-good" if time_diff <= 0 else "metric-warning"
        
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">⏱️ Execution Time</div>
            <div class="metric-value">{actual_time:.1f}s</div>
            <div class="metric-comparison">
                Estimated: ~{max_time} min 
                <span class="{time_color}">
                    (Actual: {actual_time/60:.1f} min)
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Show estimates only for upcoming research
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Active Agents",
                len(selected_agents),
                help="Number of agents selected for this query"
            )
            st.metric(
                "Estimated Cost",
                f"${estimated_cost:.3f}",
                help="Estimated cost for selected agents"
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
                f"${session_total:.3f}",
                help="Total cost for current session"
            )
    
    # Cost breakdown
    if selected_agents:
        with st.expander("💡 Cost Breakdown by Agent"):
            for agent in selected_agents:
                agent_cost = AGENT_COSTS.get(agent, 0)
                agent_time = AGENT_TIMES.get(agent, 0)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.text(f"🔹 {agent.capitalize()}")
                with col2:
                    st.text(f"${agent_cost:.3f}")
                with col3:
                    st.text(f"~{agent_time} min")


# ============================================================================
# FILE 2: ui/components/results_display.py (ENHANCED VERSION)
# ============================================================================
import streamlit as st
from typing import Dict

def render_results(results: Dict):
    """Enhanced results display with beautiful formatting"""
    
    st.markdown("### 📊 Research Results")
    
    if not results:
        st.info("No results to display")
        return
    
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
    .insight-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        margin-right: 8px;
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
    .source-title {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 8px;
    }
    .source-url {
        color: #667eea;
        text-decoration: none;
        font-size: 14px;
    }
    .source-url:hover {
        text-decoration: underline;
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
    st.markdown(f"""
    <div class="result-header">
        <strong>Query:</strong> {results.get('query', 'N/A')}<br>
        <strong>Domain:</strong> {results.get('domain', 'N/A').capitalize()}
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for organized content
    tabs = st.tabs(["📝 Summary", "🔍 Key Findings", "💡 Insights", "🔗 Sources", "📊 Raw Data"])
    
    with tabs[0]:
        # Executive Summary
        summary = results.get('summary', 'No summary available')
        st.markdown(f"""
        <div class="summary-box">
            <h4>Executive Summary</h4>
            <p style="line-height: 1.6;">{summary}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[1]:
        # Key Findings with hover effects
        findings = results.get('key_findings', [])
        if findings:
            st.markdown("#### Key Discoveries")
            for idx, finding in enumerate(findings, 1):
                # Remove markdown formatting for display
                clean_finding = finding.replace('**', '').replace('*', '')
                st.markdown(f"""
                <div class="finding-card">
                    <strong>{idx}.</strong> {clean_finding}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No key findings available")
    
    with tabs[2]:
        # Insights with badges
        insights = results.get('insights', [])
        if insights:
            st.markdown("#### Research Insights")
            for idx, insight in enumerate(insights, 1):
                clean_insight = insight.replace('**', '').replace('*', '')
                st.markdown(f"""
                <div style="margin: 12px 0;">
                    <span class="insight-badge">Insight {idx}</span>
                    <span style="margin-left: 8px;">{clean_insight}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No insights generated")
    
    with tabs[3]:
        # Sources with enhanced cards
        st.markdown("#### Research Sources")
        
        agent_results = results.get('agent_results', [])
        
        for agent_result in agent_results:
            agent_name = agent_result.get('agent_name', 'Unknown')
            sources = agent_result.get('sources', [])
            
            if sources and agent_name != "youtube" and agent_name != "api":
                st.markdown(f"**{agent_name.capitalize()} Agent** ({len(sources)} sources)")
                
                for idx, source in enumerate(sources, 1):
                    title = source.get('title', 'Untitled')
                    url = source.get('url', '#')
                    summary = source.get('summary', 'No description')
                    confidence = source.get('confidence', 0)
                    
                    # Confidence indicator
                    conf_color = "#10b981" if confidence >= 4 else "#f59e0b" if confidence >= 3 else "#ef4444"
                    conf_width = f"{(confidence / 5) * 100}%"
                    
                    st.markdown(f"""
                    <div class="source-card">
                        <div class="source-title">{idx}. {title}</div>
                        <a href="{url}" target="_blank" class="source-url">🔗 {url[:60]}...</a>
                        <p style="margin: 12px 0 8px 0; color: #6b7280; font-size: 14px;">{summary}</p>
                        <div style="background: #e5e7eb; height: 4px; border-radius: 2px; margin-top: 8px;">
                            <div style="background: {conf_color}; height: 4px; width: {conf_width}; border-radius: 2px;"></div>
                        </div>
                        <span style="font-size: 12px; color: #6b7280;">Confidence: {confidence}/5</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tabs[4]:
        # Raw Data
        st.markdown("#### Complete Response Data")
        st.json(results)
    
    # Performance Metrics Footer
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Sources", len(agent_results))
    with col2:
        st.metric("💰 Cost", f"${results.get('total_cost', 0):.6f}")
    with col3:
        st.metric("🎯 Tokens", f"{results.get('total_tokens', 0):,}")
    with col4:
        st.metric("⏱️ Time", f"{results.get('execution_time', 0):.1f}s")
