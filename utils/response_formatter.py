# ============================================================================
# FILE: utils/response_formatter.py (NEW)
# ============================================================================
"""Utility to format Perplexity responses for UI display"""

from typing import Dict, List

def format_for_ui(perplexity_result: Dict) -> Dict:
    """
    Format Perplexity API result for UI display
    
    Args:
        perplexity_result: Raw result from Perplexity agent
        
    Returns:
        Formatted dictionary for UI components
    """
    
    if not perplexity_result.get("success"):
        return {
            "error": perplexity_result.get("error", "Unknown error"),
            "agent_name": "Perplexity Agent"
        }
    
    # Format sources for display
    sources = []
    for source in perplexity_result.get("sources", []):
        sources.append({
            "title": source.get("title", "Untitled"),
            "url": source.get("url", ""),
            "snippet": source.get("snippet", "No description available"),
            "confidence": 4.5,  # Perplexity sources are high quality
            "date": perplexity_result.get("timestamp", "")[:10]
        })
    
    return {
        "agent_name": "perplexity",
        "sources": sources,
        "summary": perplexity_result.get("executive_summary", ""),
        "findings": perplexity_result.get("key_findings", []),
        "insights": perplexity_result.get("insights", []),
        "tokens_used": perplexity_result.get("tokens_used", 0),
        "cost": perplexity_result.get("estimated_cost", 0),
        "metadata": {
            "model": perplexity_result.get("model", "sonar-pro"),
            "search_quality": perplexity_result.get("search_quality", "standard"),
            "citation_count": perplexity_result.get("citation_count", 0)
        }
    }

