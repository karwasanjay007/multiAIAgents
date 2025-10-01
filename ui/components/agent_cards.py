# ============================================================================
# FILE: ui/components/agent_cards.py (COMPLETE REWRITE - NO XML)
# ============================================================================
import streamlit as st
from typing import List, Dict
from datetime import datetime

def render_agent_cards(selected_agents: List[str], processing: bool = False):
    """Render beautiful agent status cards with performance metrics"""
    
    if not selected_agents:
        st.info("No agents selected. Please select research sources above.")
        return
    
    st.markdown("### 📊 Agent Performance Stats")
    
    # Agent configuration with icons and colors
    agent_config = {
        "perplexity": {
            "name": "Perplexity",
            "icon": "🌐",
            "color": "#667eea",
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "estimated_time": 30,  # seconds
            "estimated_sources": 20,
            "estimated_cost": 0.002,
            "estimated_tokens": 2000
        },
        "youtube": {
            "name": "YouTube",
            "icon": "📹",
            "color": "#ff0000",
            "gradient": "linear-gradient(135deg, #ff0000 0%, #cc0000 100%)",
            "estimated_time": 120,
            "estimated_sources": 5,
            "estimated_cost": 0.15,
            "estimated_tokens": 500
        },
        "api": {
            "name": "API Agent",
            "icon": "📚",
            "color": "#10b981",
            "gradient": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            "estimated_time": 45,
            "estimated_sources": 12,
            "estimated_cost": 0.35,
            "estimated_tokens": 1000
        }
    }
    
    # Get actual results if available
    results = st.session_state.get('research_results', {})
    agent_results = results.get('agent_results', []) if results else []
    
    # Create columns for agent cards
    cols = st.columns(len(selected_agents))
    
    for idx, agent_id in enumerate(selected_agents):
        config = agent_config.get(agent_id, {})
        
        if not config:
            continue
            
        with cols[idx]:
            # Card container with custom styling
            card_html = f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                border: 2px solid {config['color']}20;
                transition: all 0.3s ease;
                min-height: 380px;
                position: relative;
                overflow: hidden;
            ">
                <!-- Header with gradient background -->
                <div style="
                    background: {config['gradient']};
                    margin: -24px -24px 20px -24px;
                    padding: 20px;
                    text-align: center;
                    border-radius: 14px 14px 0 0;
                ">
                    <div style="font-size: 48px; margin-bottom: 8px;">{config['icon']}</div>
                    <div style="color: white; font-size: 20px; font-weight: 600;">
                        {config['name']}
                    </div>
                </div>
            """
            
            # Get actual data for this agent
            actual_data = None
            for agent_result in agent_results:
                if agent_result.get('agent_name') == agent_id:
                    actual_data = agent_result
                    break
            
            if actual_data:
                # Show actual vs estimated comparison
                actual_sources = len(actual_data.get('sources', []))
                actual_cost = actual_data.get('cost', 0)
                actual_tokens = actual_data.get('tokens_used', 0)
                
                # Sources comparison
                sources_diff = actual_sources - config['estimated_sources']
                sources_color = "#10b981" if sources_diff >= 0 else "#f59e0b"
                
                card_html += f"""
                <div style="margin-bottom: 20px;">
                    <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                        📄 Sources Retrieved
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 32px; font-weight: 700; color: {config['color']};">
                            {actual_sources}
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #9ca3af; font-size: 12px;">Expected: {config['estimated_sources']}</div>
                            <div style="color: {sources_color}; font-size: 14px; font-weight: 600;">
                                {'+' if sources_diff >= 0 else ''}{sources_diff}
                            </div>
                        </div>
                    </div>
                    <div style="background: #e5e7eb; height: 4px; border-radius: 2px; margin-top: 8px;">
                        <div style="background: {config['gradient']}; height: 4px; width: {min(100, (actual_sources/config['estimated_sources'])*100)}%; border-radius: 2px;"></div>
                    </div>
                </div>
                """
                
                # Cost comparison
                cost_diff = actual_cost - config['estimated_cost']
                cost_color = "#10b981" if cost_diff <= 0 else "#ef4444"
                
                card_html += f"""
                <div style="margin-bottom: 20px;">
                    <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                        💰 Cost Analysis
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 24px; font-weight: 700; color: {config['color']};">
                            ${actual_cost:.6f}
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #9ca3af; font-size: 12px;">Est: ${config['estimated_cost']:.3f}</div>
                            <div style="color: {cost_color}; font-size: 14px; font-weight: 600;">
                                {'+' if cost_diff > 0 else ''}{cost_diff:.6f}
                            </div>
                        </div>
                    </div>
                </div>
                """
                
                # Tokens comparison
                tokens_diff = actual_tokens - config['estimated_tokens']
                tokens_color = "#667eea"
                
                card_html += f"""
                <div style="margin-bottom: 20px;">
                    <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                        🎯 Tokens Used
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 24px; font-weight: 700; color: {config['color']};">
                            {actual_tokens:,}
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #9ca3af; font-size: 12px;">Est: {config['estimated_tokens']:,}</div>
                            <div style="color: {tokens_color}; font-size: 14px;">
                                {'+' if tokens_diff > 0 else ''}{tokens_diff:,}
                            </div>
                        </div>
                    </div>
                </div>
                """
                
                # Status badge
                card_html += f"""
                <div style="
                    position: absolute;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: #10b981;
                    color: white;
                    padding: 6px 16px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                ">
                    ✅ Complete
                </div>
                """
                
            elif processing:
                # Show loading state
                card_html += f"""
                <div style="text-align: center; padding: 40px 0;">
                    <div style="color: {config['color']}; margin-bottom: 16px;">
                        <svg width="48" height="48" viewBox="0 0 24 24" style="animation: spin 1s linear infinite;">
                            <circle cx="12" cy="12" r="10" stroke="{config['color']}" stroke-width="4" fill="none" stroke-dasharray="60" stroke-dashoffset="20"/>
                        </svg>
                    </div>
                    <div style="color: #6b7280; font-size: 14px;">Processing...</div>
                    <div style="color: #9ca3af; font-size: 12px; margin-top: 8px;">
                        Est. time: {config['estimated_time']}s
                    </div>
                </div>
                
                <style>
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                </style>
                """
            else:
                # Show estimated metrics only
                card_html += f"""
                <div style="padding: 20px 0;">
                    <div style="margin-bottom: 16px;">
                        <div style="color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">
                            Expected Performance
                        </div>
                    </div>
                    
                    <div style="background: #f9fafb; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #6b7280; font-size: 14px;">📄 Sources</span>
                            <span style="color: {config['color']}; font-weight: 600;">{config['estimated_sources']}</span>
                        </div>
                    </div>
                    
                    <div style="background: #f9fafb; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #6b7280; font-size: 14px;">💰 Cost</span>
                            <span style="color: {config['color']}; font-weight: 600;">${config['estimated_cost']:.3f}</span>
                        </div>
                    </div>
                    
                    <div style="background: #f9fafb; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #6b7280; font-size: 14px;">🎯 Tokens</span>
                            <span style="color: {config['color']}; font-weight: 600;">{config['estimated_tokens']:,}</span>
                        </div>
                    </div>
                    
                    <div style="background: #f9fafb; border-radius: 12px; padding: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #6b7280; font-size: 14px;">⏱️ Time</span>
                            <span style="color: {config['color']}; font-weight: 600;">~{config['estimated_time']}s</span>
                        </div>
                    </div>
                </div>
                
                <div style="
                    position: absolute;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: #e5e7eb;
                    color: #6b7280;
                    padding: 6px 16px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                ">
                    Ready
                </div>
                """
            
            card_html += "</div>"
            
            st.markdown(card_html, unsafe_allow_html=True)
    
    # Performance summary if results available
    if results and agent_results:
        st.markdown("---")
        st.markdown("### 📈 Overall Performance Metrics")
        
        total_actual_cost = sum([a.get('cost', 0) for a in agent_results])
        total_estimated_cost = sum([agent_config[a]['estimated_cost'] for a in selected_agents if a in agent_config])
        
        total_actual_tokens = sum([a.get('tokens_used', 0) for a in agent_results])
        total_estimated_tokens = sum([agent_config[a]['estimated_tokens'] for a in selected_agents if a in agent_config])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cost_saved = total_estimated_cost - total_actual_cost
            st.metric(
                "💰 Cost Efficiency",
                f"${total_actual_cost:.6f}",
                f"Saved ${cost_saved:.6f}" if cost_saved > 0 else f"+${abs(cost_saved):.6f}",
                delta_color="normal" if cost_saved > 0 else "inverse"
            )
        
        with col2:
            token_diff = total_actual_tokens - total_estimated_tokens
            st.metric(
                "🎯 Token Usage",
                f"{total_actual_tokens:,}",
                f"{token_diff:+,} from estimate"
            )
        
        with col3:
            execution_time = results.get('execution_time', 0)
            st.metric(
                "⏱️ Total Time",
                f"{execution_time:.1f}s",
                f"{execution_time/60:.1f} minutes"
            )