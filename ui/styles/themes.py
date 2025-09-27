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
    .stProgress > div > div > div > div {
        background-color: #5a67d8;
    }
</style>
"""

def apply_custom_theme():
    """Apply custom theme to Streamlit app"""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
