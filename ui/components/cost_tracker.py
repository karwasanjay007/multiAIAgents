# ============================================================================
# FILE: ui/components/cost_tracker.py (FIXED)
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
    
    # FIX: Safely get results with None check
    results = st.session_state.get('research_results')
    
    # Only get actual values if results exist
    if results and isinstance(results, dict):
        actual_cost = results.get('total_cost', 0)
        actual_tokens = results.get('total_tokens', 0)
        actual_time = results.get('execution_time', 0)
        has_results = True
    else:
        actual_cost = 0
        actual_tokens = 0
        actual_time = 0
        has_results = False
    
    # Enhanced CSS for metrics
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        color: white;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.4);
    }
    .metric-label {
        font-size: 11px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        margin: 12px 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-comparison {
        font-size: 13px;
        opacity: 0.9;
        font-weight: 500;
    }
    .metric-good {
        color: #10b981;
        font-weight: 600;
    }
    .metric-warning {
        color: #fbbf24;
        font-weight: 600;
    }
    .estimate-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    .estimate-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        transform: translateX(4px);
    }
    .breakdown-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px;
        margin: 6px 0;
        background: #f9fafb;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .breakdown-item:hover {
        background: #f3f4f6;
        transform: translateX(4px);
    }
    .agent-icon {
        font-size: 20px;
        margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if has_results:
        # Show comparison cards for completed research
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
        
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">🎯 Tokens Consumed</div>
            <div class="metric-value">{actual_tokens:,}</div>
            <div class="metric-comparison">
                Active Agents: {len(selected_agents)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        time_diff = actual_time - (max_time * 60)
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
        # Show estimates with beautiful cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="estimate-card">
                <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Active Agents</div>
                <div style="font-size: 28px; font-weight: 700; color: #667eea; margin: 8px 0;">{len(selected_agents)}</div>
                <div style="color: #9ca3af; font-size: 13px;">Sources selected</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="estimate-card">
                <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Estimated Cost</div>
                <div style="font-size: 28px; font-weight: 700; color: #10b981; margin: 8px 0;">${estimated_cost:.3f}</div>
                <div style="color: #9ca3af; font-size: 13px;">Per query</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="estimate-card">
                <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Processing Time</div>
                <div style="font-size: 28px; font-weight: 700; color: #f59e0b; margin: 8px 0;">~{max_time}</div>
                <div style="color: #9ca3af; font-size: 13px;">Minutes (approx)</div>
            </div>
            """, unsafe_allow_html=True)
            
            session_total = sum([c.get('cost', 0) for c in st.session_state.get('cost_history', [])])
            st.markdown(f"""
            <div class="estimate-card">
                <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Session Total</div>
                <div style="font-size: 28px; font-weight: 700; color: #667eea; margin: 8px 0;">${session_total:.3f}</div>
                <div style="color: #9ca3af; font-size: 13px;">All queries</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced cost breakdown
    if selected_agents:
        with st.expander("💡 Detailed Cost Breakdown", expanded=False):
            agent_icons = {
                "perplexity": "🌐",
                "youtube": "📹",
                "api": "📚"
            }
            
            for agent in selected_agents:
                agent_cost = AGENT_COSTS.get(agent, 0)
                agent_time = AGENT_TIMES.get(agent, 0)
                icon = agent_icons.get(agent, "🔹")
                
                st.markdown(f"""
                <div class="breakdown-item">
                    <div>
                        <span class="agent-icon">{icon}</span>
                        <strong>{agent.capitalize()}</strong>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 600; color: #667eea;">${agent_cost:.3f}</div>
                        <div style="font-size: 12px; color: #9ca3af;">~{agent_time} min</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Budget warning
    max_cost = st.session_state.get('max_cost', 2.0)
    if estimated_cost > max_cost:
        st.warning(f"⚠️ Estimated cost ${estimated_cost:.3f} exceeds budget ${max_cost:.2f}")