# ============================================================================
# FILE 2: agents/perplexity_agent.py  
# COMPLETE REPLACEMENT - Copy entire content
# ============================================================================
from agents.base_agent import BaseAgent
from services.perplexity_client import PerplexityClient
from typing import Dict, Optional
import os

class PerplexityAgent(BaseAgent):
    """Agent for deep research using Perplexity API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("Perplexity API key not found")
        
        self.client = PerplexityClient(self.api_key)
        self.name = "Perplexity Deep Research Agent"
    
    async def execute(
        self, 
        query: str, 
        domain: str = "general",
        max_tokens: int = 2000
    ) -> Dict:
        """
        Execute deep research query
        
        Args:
            query: Research question
            domain: Research domain
            max_tokens: Maximum tokens for response
            
        Returns:
            Structured research results
        """
        
        # Call the client's deep_search method
        result = await self.client.deep_search(
            query=query,
            domain=domain,
            max_tokens=max_tokens
        )
        
        # Add agent metadata
        result["agent_name"] = self.name
        result["agent_type"] = "perplexity"
        
        return result
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "name": self.name,
            "type": "perplexity",
            "available": bool(self.api_key),
            "model": "sonar-pro"
        }