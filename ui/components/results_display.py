# ============================================================================
# FILE: ui/components/results_display.py (UPDATED - FIXED VERSION)
# ============================================================================
"""
Results display component with proper HTML/XML cleaning and hyperlinked sources
"""

import streamlit as st
import re
from typing import Dict, List, Any


def clean_text(text: str) -> str:
    """
    Remove all HTML/XML tags, special characters, and markdown formatting
    
    Args:
        text: Raw text that may contain HTML/XML/markdown
        
    Returns:
        Clean plain text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML/XML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\']', '', text)
    
    return text.strip()


def render_results(results: Dict):
    """
    Render research results with clean formatting and hyperlinked sources
    
    Args:
        results: Consolidated research results from workflow
    """
    
    if not results:
        st.info("No results to display")
        return
    
    # Check for errors
    if results.get('error'):
        st.error(f"❌ Error: {results['error']}")
        return
    
    # Extract agent results
    agent_results = results.get('agent_results', [])
    
    if not agent_results:
        st.warning("No agent results found")
        return
    
    # Create custom CSS for better formatting
    st.markdown("""
    <style>
    .summary-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin: 16px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .summary-box h4 {
        color: white;
        margin-top: 0;
        font-size: 18px;
        font-weight: 600;
    }
    .summary-box p {
        margin: 12px 0 0 0;
        line-height: 1.6;
    }
    .finding-card {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 16px;
        margin: 12px 0;
        border-radius: 8px;
    }
    .insight-badge {
        display: inline-block;
        background: #10b981;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        margin-right: 8px;
        font-weight: 500;
    }
    .source-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
        transition: all 0.2s;
    }
    .source-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    .source-link {
        color: #3b82f6;
        text-decoration: none;
        font-weight: 500;
    }
    .source-link:hover {
        text-decoration: underline;
    }
    .confidence-bar {
        height: 4px;
        background: #e5e7eb;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 8px;
    }
    .confidence-fill {
        height: 100%;
        transition: width 0.3s;
    }
    .agent-badge {
        display: inline-block;
        background: #f3f4f6;
        color: #374151;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tabs = st.tabs(["📊 Summary", "🔍 Key Findings", "💡 Insights", "🔗 All Sources"])
    
    # ========================================================================
    # TAB 1: EXECUTIVE SUMMARY
    # ========================================================================
    with tabs[0]:
        summary = results.get('summary', '')
        
        if summary and isinstance(summary, str):
            # Clean the summary text
            clean_summary = clean_text(summary)
            
            st.markdown(f"""
            <div class="summary-box">
                <h4>📋 Executive Summary</h4>
                <p>{clean_summary}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No summary available")
    
    # ========================================================================
    # TAB 2: KEY FINDINGS
    # ========================================================================
    with tabs[1]:
        findings = results.get('key_findings', [])
        
        if findings and isinstance(findings, list):
            st.markdown("#### 🔍 Key Discoveries")
            
            for idx, finding in enumerate(findings, 1):
                if not finding:
                    continue
                
                # Clean the finding text
                clean_finding = clean_text(str(finding))
                
                if clean_finding:
                    st.markdown(f"""
                    <div class="finding-card">
                        <strong>{idx}.</strong> {clean_finding}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No key findings available")
    
    # ========================================================================
    # TAB 3: INSIGHTS
    # ========================================================================
    with tabs[2]:
        insights = results.get('insights', [])
        
        if insights and isinstance(insights, list):
            st.markdown("#### 💡 Research Insights")
            
            for idx, insight in enumerate(insights, 1):
                if not insight:
                    continue
                
                # Clean the insight text
                clean_insight = clean_text(str(insight))
                
                if clean_insight:
                    st.markdown(f"""
                    <div style="margin: 16px 0;">
                        <span class="insight-badge">Insight {idx}</span>
                        <span>{clean_insight}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No insights generated")
    
    # ========================================================================
    # TAB 4: ALL SOURCES WITH HYPERLINKS
    # ========================================================================
    with tabs[3]:
        st.markdown("#### 🔗 Research Sources by Agent")
        
        agent_icons = {
            "perplexity": "🌐",
            "youtube": "📹",
            "api": "📚"
        }
        
        for agent_result in agent_results:
            agent_name = agent_result.get('agent_name', 'Unknown')
            sources = agent_result.get('sources', [])
            
            if not sources:
                continue
            
            agent_icon = agent_icons.get(agent_name.lower(), "🔹")
            st.markdown(f"### {agent_icon} {agent_name.capitalize()} Agent ({len(sources)} sources)")
            
            for idx, source in enumerate(sources, 1):
                # Safely extract source properties
                title = str(source.get('title', 'Untitled'))
                url = str(source.get('url', ''))
                summary_text = str(source.get('summary', '') or source.get('snippet', 'No description'))
                confidence = float(source.get('confidence', 3.0))
                date = str(source.get('date', ''))
                
                # Clean all text fields
                title = clean_text(title)
                summary_text = clean_text(summary_text)
                
                # Truncate long text
                if len(title) > 150:
                    title = title[:150] + "..."
                if len(summary_text) > 250:
                    summary_text = summary_text[:250] + "..."
                
                # Validate URL
                if not url or url == '' or url == '#':
                    url_html = '<span style="color: #9ca3af;">No URL available</span>'
                else:
                    # Ensure URL is properly formatted
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    
                    # Create clickable hyperlink
                    display_url = url[:70] + "..." if len(url) > 70 else url
                    url_html = f'<a href="{url}" target="_blank" class="source-link">{display_url}</a>'
                
                # Confidence bar
                conf_color = "#10b981" if confidence >= 4 else "#f59e0b" if confidence >= 3 else "#ef4444"
                conf_width = f"{min(100, (confidence / 5) * 100)}%"
                
                # Agent badge
                agent_badge = f'<span class="agent-badge">{agent_icon} {agent_name}</span>'
                
                # Render source card
                st.markdown(f"""
                <div class="source-card">
                    <div style="margin-bottom: 12px;">
                        {agent_badge}
                        {f'<span style="color: #6b7280; font-size: 13px;">{date}</span>' if date else ''}
                    </div>
                    <div style="font-weight: 600; color: #1f2937; margin-bottom: 8px; font-size: 15px;">
                        {idx}. {title}
                    </div>
                    <div style="color: #4b5563; margin-bottom: 12px; line-height: 1.5; font-size: 14px;">
                        {summary_text}
                    </div>
                    <div style="margin-bottom: 8px;">
                        {url_html}
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {conf_width}; background: {conf_color};"></div>
                    </div>
                    <div style="color: #6b7280; font-size: 12px; margin-top: 4px;">
                        Confidence: {confidence:.1f}/5.0
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")