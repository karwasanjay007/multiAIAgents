# ============================================================================
# FILE: ui/components/export_buttons.py
# ============================================================================
import streamlit as st
import json
from datetime import datetime
from utils.export import export_to_pdf, export_to_markdown

def render_export_buttons(results: dict):
    """Render export functionality buttons"""
    
    st.markdown("### Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_base = f"research_{timestamp}"
    
    with col1:
        # PDF Export
        if st.button("📄 Export PDF", use_container_width=True):
            try:
                pdf_content = export_to_pdf(results)
                st.download_button(
                    label="Download PDF",
                    data=pdf_content,
                    file_name=f"{filename_base}.pdf",
                    mime="application/pdf"
                )
                st.success("PDF ready for download")
            except Exception as e:
                st.error(f"PDF export failed: {str(e)}")
    
    with col2:
        # Markdown Export
        if st.button("📝 Export Markdown", use_container_width=True):
            try:
                md_content = export_to_markdown(results)
                st.download_button(
                    label="Download Markdown",
                    data=md_content,
                    file_name=f"{filename_base}.md",
                    mime="text/markdown"
                )
                st.success("Markdown ready for download")
            except Exception as e:
                st.error(f"Markdown export failed: {str(e)}")
    
    with col3:
        # JSON Export
        json_content = json.dumps(results, indent=2)
        st.download_button(
            label="📋 Export JSON",
            data=json_content,
            file_name=f"{filename_base}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Save to history option
    st.markdown("---")
    if st.checkbox("Save to Research History"):
        if 'research_history' not in st.session_state:
            st.session_state.research_history = []
        
        st.session_state.research_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': results.get('query'),
            'domain': results.get('domain'),
            'results': results
        })
        st.success("Saved to history")
