# ============================================================================
# FILE 2: workflows/langgraph_workflow.py (FIX ENV LOADING)
# ============================================================================
import asyncio
from datetime import datetime
from typing import Dict, List
import os
from dotenv import load_dotenv

class ResearchWorkflow:
    """Complete research workflow with Perplexity integration"""
    
    def __init__(self):
        self.perplexity_agent = None
        # Load env variables when workflow is initialized
        load_dotenv()
    
    async def execute(self, query: str, domain: str, agents: List[str]) -> Dict:
        """Execute research workflow with selected agents"""
        
        results = {
            "query": query,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "summary": "",
            "key_findings": [],
            "insights": [],
            "agent_results": [],
            "total_cost": 0,
            "total_tokens": 0,
            "execution_time": 0
        }
        
        start_time = datetime.now()
        
        # Execute Perplexity Agent
        if "perplexity" in agents:
            try:
                from agents.perplexity_agent import PerplexityAgent
                
                # Get API key with multiple fallbacks
                api_key = (
                    os.getenv("PERPLEXITY_API_KEY") or 
                    os.environ.get("PERPLEXITY_API_KEY")
                )
                
                print(f"🔑 API Key check: {'Found' if api_key else 'NOT FOUND'}")
                
                if not api_key:
                    # Try to load .env again
                    from pathlib import Path
                    env_file = Path(__file__).parent.parent / '.env'
                    if env_file.exists():
                        load_dotenv(env_file)
                        api_key = os.getenv("PERPLEXITY_API_KEY")
                        print(f"🔄 Reloaded .env, API Key: {'Found' if api_key else 'NOT FOUND'}")
                
                if not api_key:
                    results["agent_results"].append({
                        "agent_name": "perplexity",
                        "error": f"PERPLEXITY_API_KEY not found. Checked: {os.environ.keys()}",
                        "sources": []
                    })
                    return results
                
                # Initialize agent
                if not self.perplexity_agent:
                    self.perplexity_agent = PerplexityAgent(api_key)
                
                print(f"🔍 Executing Perplexity agent for: {query}")
                
                perplexity_result = await self.perplexity_agent.execute(
                    query=query,
                    domain=domain,
                    max_tokens=2000
                )
                
                if perplexity_result.get("success"):
                    # Format for UI
                    formatted_result = {
                        "agent_name": "perplexity",
                        "sources": []
                    }
                    
                    for source in perplexity_result.get("sources", []):
                        formatted_result["sources"].append({
                            "title": source.get("title", "Untitled"),
                            "url": source.get("url", ""),
                            "summary": source.get("snippet", "No description"),
                            "confidence": 4.5,
                            "date": perplexity_result.get("timestamp", "")[:10]
                        })
                    
                    results["agent_results"].append(formatted_result)
                    results["summary"] = perplexity_result.get("executive_summary", "")
                    results["key_findings"] = perplexity_result.get("key_findings", [])
                    results["insights"] = perplexity_result.get("insights", [])
                    results["total_cost"] += perplexity_result.get("estimated_cost", 0)
                    results["total_tokens"] += perplexity_result.get("tokens_used", 0)
                    
                    print(f"✅ Perplexity completed: {len(formatted_result['sources'])} sources")
                else:
                    results["agent_results"].append({
                        "agent_name": "perplexity",
                        "error": perplexity_result.get("error", "Unknown error"),
                        "sources": []
                    })
                    print(f"❌ Perplexity failed: {perplexity_result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                import traceback
                traceback.print_exc()
                results["agent_results"].append({
                    "agent_name": "perplexity",
                    "error": f"Exception: {str(e)}",
                    "sources": []
                })
        
        # Other agents
        if "youtube" in agents:
            results["agent_results"].append({
                "agent_name": "youtube",
                "sources": [{
                    "title": "YouTube integration coming soon",
                    "url": "#",
                    "summary": "This agent will analyze video content",
                    "confidence": 0,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }]
            })
        
        if "api" in agents:
            results["agent_results"].append({
                "agent_name": "api",
                "sources": [{
                    "title": "API integration coming soon",
                    "url": "#",
                    "summary": "This agent will fetch academic/news data",
                    "confidence": 0,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }]
            })
        
        end_time = datetime.now()
        results["execution_time"] = (end_time - start_time).total_seconds()
        
        return results
