# ============================================================================
# FILE 3: ui/styles/themes.py (ENHANCED VERSION)
# ============================================================================

def apply_custom_theme():
    """Apply enhanced industry-standard theme"""
    import streamlit as st
    
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        font-weight: 600;
        color: #1f2937;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.25);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        border-radius: 8px;
        border: 2px solid #667eea;
        background: white;
        color: #667eea;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        border-radius: 8px;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #667eea;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        border-radius: 8px;
        background: #f9fafb;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f3f4f6;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f9fafb 0%, #ffffff 100%);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Tooltips */
    [data-testid="stTooltipIcon"] {
        color: #667eea;
    }
    
    /* Balloons animation enhancement */
    [data-testid="stBalloons"] {
        z-index: 9999;
    }
    
    /* Success messages */
    .stSuccess {
        background: linear-gradient(90deg, #10b98115 0%, #10b98125 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
    }
    
    /* Error messages */
    .stError {
        background: linear-gradient(90deg, #ef444415 0%, #ef444425 100%);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
    }
    
    /* Warning messages */
    .stWarning {
        background: linear-gradient(90deg, #f59e0b15 0%, #f59e0b25 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
    }
    
    /* Card-like containers */
    .element-container {
        transition: all 0.3s ease;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5568d3;
    }
    </style>
    """, unsafe_allow_html=True)