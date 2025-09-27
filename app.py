# ============================================================================
# FILE: app.py (UPDATED - Complete Version)
# ============================================================================
import streamlit as st
import asyncio
import time
from datetime import datetime

# Import UI components
from ui.components.sidebar import render_sidebar
from ui.components.agent_display import render_agent_display
from ui.components.cost_tracker import render_cost_tracker
from ui.components.results_display import render_results
from ui.components.export_buttons import render_export_buttons
from ui.styles.themes import apply_custom_theme

# Import workflow
from workflows.langgraph_workflow import ResearchWorkflow

# Page configuration
st.set_page_config(
    page_title="Multi-Agent AI Deep Researcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/multi-agent-researcher',
        'Report a bug': 'https://github.com/yourusername/multi-agent-researcher/issues',
        'About': 'Multi-Agent AI Deep Researcher v0.1.0'
    }
)

# Apply custom theme
apply_custom_theme()

# Initialize session state
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'selected_agents' not in st.session_state:
    st.session_state.selected_agents = ['perplexity', 'api']
if 'cost_history' not in st.session_state:
    st.session_state.cost_history = []
if 'research_history' not in st.session_state:
    st.session_state.research_history = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'mock_mode' not in st.session_state:
    st.session_state.mock_mode = False

async def simulate_research(selected_agents: list, domain: str):
    """Simulate a research workflow for mock mode."""
    st.session_state.research_results = None
    
    for agent in selected_agents:
        st.session_state[f"{agent}_status"] = "processing"
        for i in range(101):
            st.session_state[f"{agent}_progress"] = i
            await asyncio.sleep(0.01)
        st.session_state[f"{agent}_status"] = "complete"

    # Mock results based on domain
    mock_data = {
        "stocks": {
            "summary": "Mock analysis for the stock market indicates a bullish trend for tech stocks, driven by recent advancements in AI.",
            "articles": [
                {"title": "Tech Stocks Surge on AI Optimism", "url": "https://example.com/stock1", "snippet": "The tech sector saw a significant surge this week, with investors showing strong confidence in AI-related companies."},
                {"title": "Market Analysis: A Bullish Outlook", "url": "https://example.com/stock2", "snippet": "Our analysis suggests a continued bullish market for the foreseeable future, with tech and renewable energy leading the way."},
            ],
            "videos": [],
            "total_cost": 0.0,
        },
        "medical": {
            "summary": "Mock medical research highlights a breakthrough in Alzheimer's treatment, with a new drug showing promising results in clinical trials.",
            "articles": [
                {"title": "New Alzheimer's Drug Shows Promise", "url": "https://example.com/medical1", "snippet": "A new drug, 'CogniClear', has shown remarkable results in slowing the progression of Alzheimer's disease in phase 3 clinical trials."},
                {"title": "The Future of Alzheimer's Treatment", "url": "https://example.com/medical2", "snippet": "Researchers are optimistic about the future of Alzheimer's treatment, with several new drugs and therapies in the pipeline."},
            ],
            "videos": [
                {"title": "Expert Opinions on CogniClear", "url": "https://youtube.com/watch?v=dQw4w9WgXcQ", "snippet": "Leading neurologists discuss the potential impact of CogniClear on Alzheimer's patients and their families."},
            ],
            "total_cost": 0.0,
        },
        "academic": {
            "summary": "Mock academic research on quantum computing reveals new algorithms that could solve previously intractable problems.",
            "articles": [
                {"title": "New Quantum Algorithm Breaks Ground", "url": "https://example.com/academic1", "snippet": "A paper published in 'Nature' this week details a new quantum algorithm with the potential to revolutionize fields from medicine to finance."},
                {"title": "The Implications of Quantum Supremacy", "url": "https://example.com/academic2", "snippet": "As quantum computers become more powerful, the implications for society are vast. This article explores the potential benefits and risks."},
            ],
            "videos": [],
            "total_cost": 0.0,
        },
        "technology": {
            "summary": "Mock technology trend analysis shows a rapid increase in the adoption of decentralized identity solutions.",
            "articles": [
                {"title": "The Rise of Decentralized Identity", "url": "https://example.com/tech1", "snippet": "Decentralized identity is gaining traction as a more secure and user-centric alternative to traditional identity systems."},
                {"title": "How Web3 is Changing the Internet", "url": "https://example.com/tech2", "snippet": "Web3 technologies, including decentralized identity and blockchain, are poised to reshape the internet as we know it."},
            ],
            "videos": [
                {"title": "Decentralized Identity Explained", "url": "https://youtube.com/watch?v=dQw4w9WgXcQ", "snippet": "This video provides a clear and concise explanation of decentralized identity and its potential benefits."},
            ],
            "total_cost": 0.0,
        },
    }
    
    return mock_data.get(domain, {"summary": "No mock data available for this domain.", "articles": [], "videos": [], "total_cost": 0.0})

# Main header
st.title("🔬 Multi-Agent AI Deep Researcher")
st.markdown("Advanced AI-powered research assistant with specialized agents")

# Sidebar
with st.sidebar:
    render_sidebar()

# Main content layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Research Configuration")
    
    # Domain selection
    domain = st.selectbox(
        "Research Domain",
        ["stocks", "medical", "academic", "technology"],
        format_func=lambda x: {
            "stocks": "📈 Stock Market Analysis",
            "medical": "🏥 Medical Research",
            "academic": "📚 Academic Research",
            "technology": "💻 Technology Trends"
        }[x],
        help="Select the domain for your research"
    )
    
    # Query input
    query = st.text_area(
        "Research Question",
        value=st.session_state.get('template_query', ''),
        placeholder="E.g., What are the latest breakthrough treatments for Alzheimer's disease?",
        height=100,
        help="Enter your research question in detail"
    )
    
    # Agent selection and status
    selected_agents = render_agent_display(domain, st.session_state.processing)
    
    # Start research button
    start_button = st.button(
        "🚀 Start Research",
        use_container_width=True,
        type="primary",
        disabled=st.session_state.processing
    )
    
    if start_button:
        if not query.strip():
            st.error("Please enter a research question")
        elif not selected_agents:
            st.error("Please select at least one research source")
        else:
            st.session_state.processing = True
            
            if st.session_state.get("mock_mode", False):
                # Run mock workflow
                results = asyncio.run(simulate_research(selected_agents, domain))
                st.session_state.research_results = results
                st.session_state.processing = False
                st.rerun()
            else:
                # Run real workflow
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Create workflow
                    workflow = ResearchWorkflow()
                    
                    # Execute research
                    with st.spinner("Initializing agents..."):
                        status_text.text("Starting research workflow...")
                        progress_bar.progress(20)
                        
                        # Run workflow (async)
                        results = asyncio.run(
                            workflow.execute(query, domain, selected_agents)
                        )
                        
                        progress_bar.progress(100)
                        status_text.text("Research complete!")
                    
                    # Store results
                    st.session_state.research_results = results
                    
                    # Add to history
                    st.session_state.research_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'query': query,
                        'domain': domain,
                        'results': results
                    })
                    
                    # Add to cost history
                    st.session_state.cost_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'cost': results.get('total_cost', 0),
                        'agents': selected_agents
                    })
                    
                    st.success("Research completed successfully!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Research failed: {str(e)}")
                    st.exception(e)
                
                finally:
                    st.session_state.processing = False
                    progress_bar.empty()
                    status_text.empty()

with col2:
    st.subheader("Results & Cost")
    render_cost_tracker(selected_agents)
    # Results section
    if st.session_state.research_results:
        st.markdown("---")
        render_results(st.session_state.research_results)
        st.markdown("---")
        render_export_buttons(st.session_state.research_results)
    else:
        st.info("💡 Configure your research options and click 'Start Research' to begin")
        
        # Show quick tips
        with st.expander("Quick Tips"):
            st.markdown("""
            - **Choose your domain** carefully for better agent recommendations
            - **Select multiple agents** for comprehensive analysis
            - **Be specific** in your research question for better results
            - **Check cost estimates** before starting research
            - **View history** to review past queries
            """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Multi-Agent AI Deep Researcher v0.1.0")
with col2:
    st.caption(f"Session: {len(st.session_state.cost_history)} queries")
with col3:
    total_cost = sum([c.get('cost', 0) for c in st.session_state.cost_history])
    st.caption(f"Total Cost: ${total_cost:.2f}")
