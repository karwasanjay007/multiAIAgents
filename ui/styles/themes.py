# ============================================================================
# FILE: ui/styles/themes.py
# ============================================================================

# Custom Streamlit theme configuration
CUSTOM_THEME = {
    "primaryColor": "#5a67d8",
    "backgroundColor": "#f7fafc",
    "secondaryBackgroundColor": "#edf2f7",
    "textColor": "#2d3748",
    "font": "sans serif"
}

# CSS overrides for custom styling
CUSTOM_CSS = """
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Agent selection cards */
    .agent-card {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        background: white;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        cursor: pointer;
    }
    .agent-card:hover {
        border-color: #5a67d8;
        box-shadow: 0 12px 20px rgba(90, 103, 216, 0.2);
    }
    .agent-card-selected {
        border-width: 2px;
        border-color: #5a67d8;
        background: #f0f2ff;
    }

    .agent-card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .agent-card-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #eef2ff;
        color: #5a67d8;
        border-radius: 12px;
        width: 40px;
        height: 40px;
        flex-shrink: 0;
        font-size: 1.2rem;
    }

    .agent-card-title {
        font-weight: 600;
        color: #2d3748;
    }

    .agent-card-description {
        font-size: 0.85rem;
        color: #4a5568;
        margin-top: 0.5rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        color: #5a67d8;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: 2px solid #5a67d8;
        background-color: #5a67d8;
        color: white;
    }
    .stButton>button:hover {
        border: 2px solid #4c51bf;
        background-color: #4c51bf;
        color: white;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #ebf8ff;
        border-left: 4px solid #3182ce;
    }
    
    /* Success boxes */
    .stSuccess {
        background-color: #f0fff4;
        border-left: 4px solid #38a169;
    }
    
    /* Warning boxes */
    .stWarning {
        background-color: #fffaf0;
        border-left: 4px solid #dd6b20;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background-color: #5a67d8;
    }
</style>
"""

def apply_custom_theme():
    """Apply custom theme to Streamlit app"""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)