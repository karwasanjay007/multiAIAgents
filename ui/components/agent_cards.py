# ============================================================================
# FILE: ui/components/agent_cards.py (COMPLETE FIX)
# ============================================================================
import streamlit as st
from typing import List, Dict
from config.constants import AGENT_COSTS, AGENT_TIMES

def render_agent_cards(agents: List[str], processing: bool = False):
    """Render agent status cards with proper data display"""
    
    st.markdown("### 🤖 Agent Performance Stats")
    
    # Get results if available
    results = st.session_state.get('research_results', {})
    agent_results = results.get('agent_results', []) if results else []
    
    # Agent metadata
    agent_info = {
        "perplexity": {
            "name": "Web Research",
            "icon": "🌐",
            "color": "#667eea"
        },
        "youtube": {
            "name": "Video Analysis",
            "icon": "📹",
            "color": "#f093fb"
        },
        "api": {
            "name": "Academic & News",
            "icon": "📚",
            "color": "#4facfe"
        }
    }
    
    # Custom CSS for cards
    st.markdown("""
    <style>
    .perf-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .perf-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        transform: translateY(-4px);
    }
    .perf-icon {
        font-size: 48px;
        text-align: center;
        margin-bottom: 12px;
    }
    .perf-title {
        font-size: 18px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 20px;
        color: #1f2937;
    }
    .perf-stat {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f3f4f6;
    }
    .perf-stat:last-child {
        border-bottom: none;
    }
    .perf-label {
        font-size: 14px;
        color: #6b7280;
        font-weight: 500;
    }
    .perf-value {
        font-size: 16px;
        font-weight: 700;
        color: #1f2937;
    }
    .perf-processing {
        text-align: center;
        padding: 8px;
        background: #fef3c7;
        border-radius: 8px;
        color: #92400e;
        font-size: 13px;
        margin-top: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create columns for cards
    num_agents = len(agents)
    if num_agents == 0:
        st.info("No agents selected")
        return
    
    cols = st.columns(num_agents)
    
    # Create a map of agent results by name
    agent_data_map = {}
    for agent_result in agent_results:
        agent_name = agent_result.get('agent_name', '')
        if agent_name:
            agent_data_map[agent_name] = agent_result
    
    # Render cards
    for idx, agent_id in enumerate(agents):
        with cols[idx]:
            info = agent_info.get(agent_id, {
                "name": agent_id.capitalize(),
                "icon": "🔹",
                "color": "#667eea"
            })
            
            # Get actual data for this agent
            agent_data = agent_data_map.get(agent_id, {})
            
            # Extract stats
            sources = agent_data.get('sources', [])
            sources_count = len(sources) if isinstance(sources, list) else 0
            
            try:
                cost = float(agent_data.get('cost', 0))
            except (ValueError, TypeError):
                cost = 0.0
            
            try:
                tokens = int(agent_data.get('tokens', 0))
            except (ValueError, TypeError):
                tokens = 0
            
            # Status indicator
            if processing and not agent_data:
                status_html = f'<div class="perf-processing">⏳ Processing...</div>'
            elif agent_data:
                status_html = f'<div class="perf-processing" style="background: #d1fae5; color: #065f46;">✅ Complete</div>'
            else:
                status_html = ''
            
            # Render card
            st.markdown(f"""
            <div class="perf-card">
                <div class="perf-icon">{info['icon']}</div>
                <div class="perf-title" style="color: {info['color']};">{info['name']}</div>
                
                <div class="perf-stat">
                    <span class="perf-label">Sources</span>
                    <span class="perf-value">{sources_count}</span>
                </div>
                
                <div class="perf-stat">
                    <span class="perf-label">Cost</span>
                    <span class="perf-value">${cost:.6f}</span>
                </div>
                
                <div class="perf-stat">
                    <span class="perf-label">Tokens</span>
                    <span class="perf-value">{tokens:,}</span>
                </div>
                
                {status_html}
            </div>
            """, unsafe_allow_html=True)


def render_cost_breakdown(selected_agents: List[str]):
    """Render detailed cost breakdown as an expander"""
    
    # Get actual results
    results = st.session_state.get('research_results', {})
    agent_results = results.get('agent_results', []) if results else []
    
    # Create agent data map
    agent_data_map = {}
    for agent_result in agent_results:
        agent_name = agent_result.get('agent_name', '')
        if agent_name:
            agent_data_map[agent_name] = agent_result
    
    # Agent display info
    agent_display = {
        "perplexity": {"icon": "🌐", "name": "Perplexity"},
        "youtube": {"icon": "📹", "name": "Youtube"},
        "api": {"icon": "📚", "name": "Api"}
    }
    
    with st.expander("💡 Detailed Cost Breakdown", expanded=False):
        st.markdown("""
        <style>
        .cost-breakdown-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px;
            margin: 8px 0;
            background: #f9fafb;
            border-radius: 12px;
            transition: all 0.2s ease;
        }
        .cost-breakdown-item:hover {
            background: #f3f4f6;
            transform: translateX(4px);
        }
        .cost-breakdown-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .cost-breakdown-icon {
            font-size: 24px;
        }
        .cost-breakdown-name {
            font-weight: 600;
            color: #1f2937;
        }
        .cost-breakdown-right {
            text-align: right;
        }
        .cost-breakdown-cost {
            font-weight: 700;
            color: #667eea;
            font-size: 16px;
        }
        .cost-breakdown-time {
            font-size: 12px;
            color: #9ca3af;
        }
        </style>
        """, unsafe_allow_html=True)
        
        for agent_id in selected_agents:
            display_info = agent_display.get(agent_id, {"icon": "🔹", "name": agent_id.capitalize()})
            
            # Get actual data
            agent_data = agent_data_map.get(agent_id, {})
            actual_cost = agent_data.get('cost', 0) if agent_data else 0
            
            # Fallback to estimated cost if no actual data
            if actual_cost == 0:
                actual_cost = AGENT_COSTS.get(agent_id, 0)
            
            estimated_time = AGENT_TIMES.get(agent_id, 0)
            
            st.markdown(f"""
            <div class="cost-breakdown-item">
                <div class="cost-breakdown-left">
                    <span class="cost-breakdown-icon">{display_info['icon']}</span>
                    <strong class="cost-breakdown-name">{display_info['name']}</strong>
                </div>
                <div class="cost-breakdown-right">
                    <div class="cost-breakdown-cost">${actual_cost:.3f}</div>
                    <div class="cost-breakdown-time">~{estimated_time} sec</div>
                </div>
            </div>
            """, unsafe_allow_html=True)