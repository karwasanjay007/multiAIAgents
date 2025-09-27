
# ============================================================================
# FILE: ui/pages/3_Settings.py
# ============================================================================
import streamlit as st
from config.settings import get_settings

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings")
st.markdown("Configure your research assistant")

# API Configuration
st.header("API Configuration")

with st.expander("API Keys", expanded=True):
    st.warning("Never share your API keys. Keys are stored only in your session.")
    
    openrouter_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        value=st.session_state.get('OPENROUTER_API_KEY', ''),
        help="Required for AI model access"
    )
    
    perplexity_key = st.text_input(
        "Perplexity API Key",
        type="password",
        value=st.session_state.get('PERPLEXITY_API_KEY', ''),
        help="Optional: For deep research agent"
    )
    
    youtube_key = st.text_input(
        "YouTube API Key",
        type="password",
        value=st.session_state.get('YOUTUBE_API_KEY', ''),
        help="Optional: For video analysis agent"
    )
    
    news_key = st.text_input(
        "News API Key",
        type="password",
        value=st.session_state.get('NEWS_API_KEY', ''),
        help="Optional: For news fetching"
    )
    
    if st.button("Save API Keys"):
        st.session_state.OPENROUTER_API_KEY = openrouter_key
        st.session_state.PERPLEXITY_API_KEY = perplexity_key
        st.session_state.YOUTUBE_API_KEY = youtube_key
        st.session_state.NEWS_API_KEY = news_key
        st.success("API keys saved to session")

# Model Configuration
st.header("Model Configuration")

col1, col2 = st.columns(2)

with col1:
    orchestrator_model = st.selectbox(
        "Orchestrator Model",
        ["openai/gpt-3.5-turbo", "openai/gpt-4-turbo", "anthropic/claude-3-haiku"],
        help="Model for coordinating agents"
    )
    
    analyzer_model = st.selectbox(
        "Analysis Model",
        ["anthropic/claude-3.5-sonnet", "anthropic/claude-opus", "openai/gpt-4"],
        help="Model for analyzing results"
    )

with col2:
    perplexity_model = st.selectbox(
        "Perplexity Model",
        ["perplexity/sonar", "perplexity/sonar-pro"],
        help="Model for web research"
    )
    
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=100,
        max_value=4000,
        value=2000,
        step=100,
        help="Maximum tokens for responses"
    )

# Cost Settings
st.header("Cost Management")

col1, col2, col3 = st.columns(3)

with col1:
    max_cost_per_query = st.number_input(
        "Max Cost Per Query ($)",
        min_value=0.1,
        max_value=10.0,
        value=2.0,
        step=0.1
    )

with col2:
    daily_budget = st.number_input(
        "Daily Budget ($)",
        min_value=1.0,
        max_value=100.0,
        value=20.0,
        step=1.0
    )

with col3:
    alert_threshold = st.number_input(
        "Alert Threshold ($)",
        min_value=0.5,
        max_value=50.0,
        value=10.0,
        step=0.5
    )

st.session_state.max_cost = max_cost_per_query
st.session_state.daily_budget = daily_budget

# Performance Settings
st.header("Performance Settings")

col1, col2 = st.columns(2)

with col1:
    timeout = st.slider(
        "Query Timeout (minutes)",
        min_value=1,
        max_value=15,
        value=5,
        help="Maximum time for a query to complete"
    )
    
    max_sources = st.slider(
        "Max Sources per Agent",
        min_value=5,
        max_value=50,
        value=10,
        help="Maximum number of sources each agent can fetch"
    )

with col2:
    enable_caching = st.checkbox(
        "Enable Caching",
        value=True,
        help="Cache results to reduce API calls"
    )
    
    enable_parallel = st.checkbox(
        "Parallel Execution",
        value=True,
        help="Run agents in parallel (faster but higher cost)"
    )

# Export/Import Settings
st.header("Export/Import Settings")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Export Configuration")
    
    export_format = st.multiselect(
        "Default Export Formats",
        ["PDF", "Markdown", "JSON", "DOCX"],
        default=["PDF", "JSON"]
    )
    
    include_metadata = st.checkbox("Include Metadata", value=True)
    include_citations = st.checkbox("Include Citations", value=True)

with col2:
    st.subheader("Import Configuration")
    
    if st.button("Import Settings from File"):
        uploaded = st.file_uploader("Upload settings JSON", type=['json'])
        if uploaded:
            import json
            settings = json.load(uploaded)
            st.success("Settings imported successfully")
    
    if st.button("Reset to Defaults"):
        st.warning("This will reset all settings to default values")
        if st.checkbox("Confirm reset"):
            # Clear all custom settings
            for key in list(st.session_state.keys()):
                if key.startswith('custom_'):
                    del st.session_state[key]
            st.success("Settings reset to defaults")

# LangSmith Integration
st.header("LangSmith Integration")

enable_langsmith = st.checkbox(
    "Enable LangSmith Tracing",
    value=False,
    help="Track and debug agent workflows"
)

if enable_langsmith:
    langsmith_key = st.text_input(
        "LangSmith API Key",
        type="password",
        help="Get from LangSmith dashboard"
    )
    
    project_name = st.text_input(
        "Project Name",
        value="multi-agent-researcher",
        help="LangSmith project name"
    )
    
    st.session_state.LANGCHAIN_TRACING_V2 = True
    st.session_state.LANGCHAIN_API_KEY = langsmith_key
    st.session_state.LANGCHAIN_PROJECT = project_name

# Save all settings
st.markdown("---")
if st.button("Save All Settings", type="primary"):
    st.session_state.update({
        'orchestrator_model': orchestrator_model,
        'analyzer_model': analyzer_model,
        'perplexity_model': perplexity_model,
        'max_tokens': max_tokens,
        'timeout': timeout,
        'max_sources': max_sources,
        'enable_caching': enable_caching,
        'enable_parallel': enable_parallel,
        'export_format': export_format,
        'include_metadata': include_metadata,
        'include_citations': include_citations
    })
    st.success("All settings saved successfully!")

# Display current configuration
with st.expander("Current Configuration"):
    st.json({
        "models": {
            "orchestrator": orchestrator_model,
            "analyzer": analyzer_model,
            "perplexity": perplexity_model
        },
        "cost": {
            "max_per_query": max_cost_per_query,
            "daily_budget": daily_budget
        },
        "performance": {
            "timeout": timeout,
            "max_sources": max_sources,
            "caching": enable_caching,
            "parallel": enable_parallel
        }
    })
