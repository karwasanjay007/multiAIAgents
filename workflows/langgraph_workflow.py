# ============================================================================
# FILE: workflows/langgraph_workflow.py (COMPLETE INTEGRATION)
# ============================================================================
import asyncio
from datetime import datetime
from typing import Dict, List
import os
from dotenv import load_dotenv

class ResearchWorkflow:
    """Complete research workflow with all three agents integrated"""
    
    def __init__(self):
        self.perplexity_agent = None
        self.youtube_agent = None
        self.api_agent = None
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
            "execution_time": 0,
            "agents_used": agents
        }
        
        start_time = datetime.now()
        
        # Execute agents in parallel
        tasks = []
        
        if "perplexity" in agents:
            tasks.append(self._execute_perplexity(query, domain))
        
        if "youtube" in agents:
            tasks.append(self._execute_youtube(query, domain))
        
        if "api" in agents:
            tasks.append(self._execute_api(query, domain))
        
        # Wait for all agents to complete
        if tasks:
            agent_responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process responses
            for response in agent_responses:
                if isinstance(response, Exception):
                    print(f"❌ Agent failed: {response}")
                    continue
                
                if response and isinstance(response, dict):
                    results["agent_results"].append(response)
                    results["total_cost"] += response.get("cost", 0)
                    results["total_tokens"] += response.get("tokens", 0)
        
        # Consolidate results
        self._consolidate_results(results)
        
        end_time = datetime.now()
        results["execution_time"] = (end_time - start_time).total_seconds()
        
        return results
    
    async def _execute_perplexity(self, query: str, domain: str) -> Dict:
        """Execute Perplexity agent"""
        try:
            from agents.perplexity_agent import PerplexityAgent
            
            api_key = os.getenv("PERPLEXITY_API_KEY")
            
            if not api_key:
                return {
                    "agent_name": "perplexity",
                    "error": "PERPLEXITY_API_KEY not found",
                    "sources": [],
                    "cost": 0,
                    "tokens": 0
                }
            
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
                sources = []
                for source in perplexity_result.get("sources", []):
                    sources.append({
                        "title": source.get("title", "Untitled"),
                        "url": source.get("url", ""),
                        "summary": source.get("snippet", "No description"),
                        "confidence": 4.5,
                        "date": perplexity_result.get("timestamp", "")[:10]
                    })
                
                print(f"✅ Perplexity completed: {len(sources)} sources")
                
                return {
                    "agent_name": "perplexity",
                    "sources": sources,
                    "summary": perplexity_result.get("executive_summary", ""),
                    "findings": perplexity_result.get("key_findings", []),
                    "insights": perplexity_result.get("insights", []),
                    "cost": perplexity_result.get("estimated_cost", 0),
                    "tokens": perplexity_result.get("tokens_used", 0),
                    "model": perplexity_result.get("model", "sonar-pro")
                }
            else:
                print(f"❌ Perplexity failed: {perplexity_result.get('error')}")
                return {
                    "agent_name": "perplexity",
                    "error": perplexity_result.get("error", "Unknown error"),
                    "sources": [],
                    "cost": 0,
                    "tokens": 0
                }
                
        except Exception as e:
            print(f"❌ Perplexity exception: {e}")
            import traceback
            traceback.print_exc()
            return {
                "agent_name": "perplexity",
                "error": f"Exception: {str(e)}",
                "sources": [],
                "cost": 0,
                "tokens": 0
            }
    
    async def _execute_youtube(self, query: str, domain: str) -> Dict:
        """Execute YouTube agent"""
        try:
            from agents.youtube_researcher import analyze_youtube
            from graph.state import ResearchState
            
            api_key = os.getenv("YOUTUBE_API_KEY")
            
            if not api_key:
                return {
                    "agent_name": "youtube",
                    "error": "YOUTUBE_API_KEY not found",
                    "sources": [],
                    "cost": 0,
                    "tokens": 0
                }
            
            print(f"📹 Executing YouTube agent for: {query}")
            
            # Create state for YouTube agent
            state: ResearchState = {
                "topic": query,
                "domain": domain,
                "mode": "extended"
            }
            
            # Execute YouTube agent
            youtube_result = analyze_youtube(state)
            
            # Extract results
            youtube_data = youtube_result.get("youtube_results", {})
            sources_list = youtube_data.get("sources", [])
            
            # Format sources for UI
            formatted_sources = []
            for source in sources_list:
                items = source.get("items", [])
                for item in items:
                    formatted_sources.append({
                        "title": item.get("title", "Untitled Video"),
                        "url": item.get("source", ""),
                        "summary": item.get("summary", "No summary available"),
                        "confidence": 4.0,
                        "date": item.get("published_date", "")[:10] if item.get("published_date") else ""
                    })
            
            print(f"✅ YouTube completed: {len(formatted_sources)} videos")
            
            return {
                "agent_name": "youtube",
                "sources": formatted_sources,
                "cost": youtube_data.get("cost", 0.15),
                "tokens": youtube_data.get("tokens", 0),
                "video_count": len(formatted_sources),
                "processing_time": youtube_data.get("elapsed", 0)
            }
            
        except Exception as e:
            print(f"❌ YouTube exception: {e}")
            import traceback
            traceback.print_exc()
            return {
                "agent_name": "youtube",
                "error": f"Exception: {str(e)}",
                "sources": [],
                "cost": 0,
                "tokens": 0
            }
    
    async def _execute_api(self, query: str, domain: str) -> Dict:
        """Execute API agent (academic papers + news)"""
        try:
            from agents.academic_researcher import research_academic_papers
            from agents.news_analyzer import analyze_news
            from graph.state import ResearchState
            
            print(f"📚 Executing API agent for: {query}")
            
            # Create state for API agent
            state: ResearchState = {
                "topic": query,
                "domain": domain,
                "mode": "extended"
            }
            
            # Execute both academic and news agents
            academic_result = research_academic_papers(state)
            news_result = analyze_news(state)
            
            # Extract and combine sources
            formatted_sources = []
            
            # Process academic results
            academic_data = academic_result.get("academic_results", {})
            for source in academic_data.get("sources", []):
                items = source.get("items", [])
                for item in items:
                    formatted_sources.append({
                        "title": item.get("title", "Untitled Paper"),
                        "url": item.get("source", ""),
                        "summary": item.get("summary", "No summary available"),
                        "confidence": 4.2,
                        "date": item.get("published_date", "")[:10] if item.get("published_date") else "",
                        "source_type": "academic"
                    })
            
            # Process news results
            news_data = news_result.get("news_results", {})
            for source in news_data.get("sources", []):
                items = source.get("items", [])
                for item in items:
                    formatted_sources.append({
                        "title": item.get("title", "Untitled Article"),
                        "url": item.get("source", ""),
                        "summary": item.get("summary", "No summary available"),
                        "confidence": 3.8,
                        "date": item.get("published_date", "")[:10] if item.get("published_date") else "",
                        "source_type": "news"
                    })
            
            print(f"✅ API completed: {len(formatted_sources)} sources")
            
            return {
                "agent_name": "api",
                "sources": formatted_sources,
                "cost": 0.35,  # Estimated cost
                "tokens": 0,
                "academic_count": len([s for s in formatted_sources if s.get("source_type") == "academic"]),
                "news_count": len([s for s in formatted_sources if s.get("source_type") == "news"])
            }
            
        except Exception as e:
            print(f"❌ API exception: {e}")
            import traceback
            traceback.print_exc()
            return {
                "agent_name": "api",
                "error": f"Exception: {str(e)}",
                "sources": [],
                "cost": 0,
                "tokens": 0
            }
    
    def _consolidate_results(self, results: Dict):
        """Consolidate results from all agents with better extraction"""
        
        all_findings = []
        all_insights = []
        best_summary = ""
        
        for agent_result in results["agent_results"]:
            agent_name = agent_result.get("agent_name", "")
            
            # Get findings from agent
            findings = agent_result.get("findings", [])
            if findings and isinstance(findings, list):
                # Add agent attribution
                for finding in findings:
                    if finding and str(finding).strip():
                        all_findings.append(f"{str(finding).strip()}")
            
            # Get insights from agent  
            insights = agent_result.get("insights", [])
            if insights and isinstance(insights, list):
                for insight in insights:
                    if insight and str(insight).strip():
                        all_insights.append(f"{str(insight).strip()}")
            
            # Get best summary (prefer Perplexity)
            summary = agent_result.get("summary", "")
            if summary and isinstance(summary, str):
                if agent_name == "perplexity" and not best_summary:
                    best_summary = summary
                elif not best_summary:
                    best_summary = summary
        
        # Deduplicate and limit
        all_findings = list(dict.fromkeys(all_findings))  # Remove duplicates preserving order
        all_insights = list(dict.fromkeys(all_insights))
        
        results["key_findings"] = all_findings[:10]
        results["insights"] = all_insights[:8]
        
        # Set summary
        if best_summary:
            results["summary"] = best_summary
        else:
            # Create a basic summary
            agent_names = [r.get("agent_name", "").capitalize() for r in results["agent_results"]]
            total_sources = sum(len(r.get("sources", [])) for r in results["agent_results"])
            results["summary"] = (
                f"Research completed using {len(agent_names)} specialized agents: "
                f"{', '.join(agent_names)}. "
                f"Collected {total_sources} sources from multiple channels including "
                f"academic papers, news articles, and web research."
            )