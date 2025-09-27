import asyncio
from datetime import datetime

class ResearchWorkflow:
    async def execute(self, query: str, domain: str, agents: list):
        """Mock workflow that returns fake data"""
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Return mock results
        return {
            "query": query,
            "domain": domain,
            "summary": f"This is a mock summary for '{query}' in {domain} domain. The research used {len(agents)} agents.",
            "key_findings": [
                "Mock finding 1: Sample data point",
                "Mock finding 2: Another insight",
                "Mock finding 3: Key observation"
            ],
            "agent_results": [
                {
                    "agent_name": agent,
                    "sources": [
                        {
                            "title": f"Sample Source from {agent}",
                            "summary": f"Mock summary from {agent} agent",
                            "url": f"https://example.com/{agent}",
                            "confidence": 4.5,
                            "date": datetime.now().strftime("%Y-%m-%d")
                        }
                    ]
                }
                for agent in agents
            ],
            "insights": [
                f"Mock insight for {domain} research",
                "Pattern detected in mock data"
            ],
            "contradictions": [],
            "total_cost": sum([0.65 if a == "perplexity" else 0.15 if a == "youtube" else 0.35 for a in agents]),
            "execution_time": 2.5
        }