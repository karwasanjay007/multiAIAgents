# ============================================================================
# FILE 2: app.py (COMPLETE UPDATED VERSION)
# ============================================================================
import streamlit as st
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# ⭐ CRITICAL: Load environment variables FIRST before any other imports
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Verify API key is loaded
if os.getenv("PERPLEXITY_API_KEY"):
    print(f"✅ API Key loaded: {os.getenv('PERPLEXITY_API_KEY')[:10]}...")
else:
    print("❌ PERPLEXITY_API_KEY not found!")

# Import UI components (after loading env)
from ui.components.sidebar import render_sidebar
from ui.components.agent_display import render_agent_display
from ui.components.cost_tracker import render_cost_tracker
from ui.components.results_display import render_results
from ui.components.export_buttons import render_export_buttons
from ui.styles.themes import apply_custom_theme

# Import workflow
from workflows.langgraph_workflow import ResearchWorkflow

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
    initial_sidebar_state="expanded"
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

# Windows event loop fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
            
            # Show progress
            progress_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Create workflow
                    workflow = ResearchWorkflow()
                    
                    # Update progress
                    status_text.text("🔄 Initializing agents...")
                    progress_bar.progress(20)
                    
                    # Execute research (async)
                    status_text.text(f"🔍 Researching: {query[:50]}...")
                    progress_bar.progress(40)
                    
                    # Run async workflow
                    results = asyncio.run(
                        workflow.execute(query, domain, selected_agents)
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Research complete!")
                    
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
                    st.rerun()

# ============================================================================
# FILE: app.py (ENHANCED ERROR HANDLING)
# Add this around line 190 where render_cost_tracker is called
# ============================================================================

with col2:
    st.subheader("Results & Cost")
    
    # FIX: Add try-except wrapper for cost tracker
    try:
        render_cost_tracker(selected_agents)
    except Exception as e:
        st.error(f"Error displaying cost tracker: {str(e)}")
        # Fallback display
        st.metric("Selected Agents", len(selected_agents))
    
    # Results section
    if st.session_state.research_results:
        st.markdown("---")
        try:
            render_results(st.session_state.research_results)
        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            st.json(st.session_state.research_results)
        
        st.markdown("---")
        try:
            render_export_buttons(st.session_state.research_results)
        except Exception as e:
            st.error(f"Error displaying export buttons: {str(e)}")
    else:
        st.info("💡 Configure your research and click 'Start Research'")
        
        with st.expander("✨ Quick Tips", expanded=True):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                        padding: 20px; border-radius: 12px; border-left: 4px solid #667eea;">
                <h4 style="margin-top: 0; color: #667eea;">🎯 How to Get Best Results</h4>
                <ul style="line-height: 1.8;">
                    <li><strong>Choose domain carefully</strong> - Gets better agent recommendations</li>
                    <li><strong>Select Web Research</strong> - Uses Perplexity AI for deep analysis</li>
                    <li><strong>Be specific</strong> - Detailed questions get better answers</li>
                    <li><strong>Check costs</strong> - Review estimates before starting</li>
                    <li><strong>View history</strong> - Access past queries anytime</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)                    

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