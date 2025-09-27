# ============================================================================
# FILE: workflows/langgraph_workflow.py (COMPLETE UPDATE)
# ============================================================================
import asyncio
from datetime import datetime
from typing import Dict, List
from agents.perplexity_agent import PerplexityAgent
from utils.response_formatter import format_for_ui
import os

class ResearchWorkflow:
    """Complete research workflow with Perplexity integration"""
    
    def __init__(self):
        self.perplexity_agent = None
    
    async def execute(self, query: str, domain: str, agents: List[str]) -> Dict:
        """
        Execute research workflow with selected agents
        
        Args:
            query: Research question
            domain: Research domain (stocks, medical, academic, technology)
            agents: List of agent IDs to use (e.g., ['perplexity', 'youtube', 'api'])
            
        Returns:
            Complete research results with all agent outputs
        """
        
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
                if not self.perplexity_agent:
                    api_key = os.getenv("PERPLEXITY_API_KEY")
                    if api_key:
                        self.perplexity_agent = PerplexityAgent(api_key)
                
                if self.perplexity_agent:
                    perplexity_result = await self.perplexity_agent.execute(
                        query=query,
                        domain=domain,
                        max_tokens=2000
                    )
                    
                    if perplexity_result.get("success"):
                        # Format for UI
                        formatted = format_for_ui(perplexity_result)
                        results["agent_results"].append(formatted)
                        
                        # Update totals
                        results["total_cost"] += perplexity_result.get("estimated_cost", 0)
                        results["total_tokens"] += perplexity_result.get("tokens_used", 0)
                        
                        # Use Perplexity as primary summary
                        results["summary"] = perplexity_result.get("executive_summary", "")
                        results["key_findings"] = perplexity_result.get("key_findings", [])
                        results["insights"] = perplexity_result.get("insights", [])
                    else:
                        results["agent_results"].append({
                            "agent_name": "perplexity",
                            "error": perplexity_result.get("error", "Unknown error"),
                            "sources": []
                        })
                        
            except Exception as e:
                results["agent_results"].append({
                    "agent_name": "perplexity",
                    "error": str(e),
                    "sources": []
                })
        
        # TODO: Add YouTube Agent integration
        if "youtube" in agents:
            results["agent_results"].append({
                "agent_name": "youtube",
                "sources": [],
                "summary": "YouTube agent not yet implemented"
            })
        
        # TODO: Add API Agent integration
        if "api" in agents:
            results["agent_results"].append({
                "agent_name": "api",
                "sources": [],
                "summary": "API agent not yet implemented"
            })
        
        # Calculate execution time
        end_time = datetime.now()
        results["execution_time"] = (end_time - start_time).total_seconds()
        
        return results
