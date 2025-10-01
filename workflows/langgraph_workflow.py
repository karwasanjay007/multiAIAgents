# ============================================================================
# FILE: workflows/langgraph_workflow.py
# COMPLETE FINAL VERSION - All fixes integrated
# ============================================================================

import asyncio
import os
import re
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class ResearchWorkflow:
    """Orchestrates multi-agent research workflow"""
    
    def __init__(self):
        self.perplexity_agent = None
        self.youtube_agent = None
        self.api_agent = None
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
    
    def _clean_text(self, text: str) -> str:
        """Remove HTML/XML tags and special characters"""
        if not text or not isinstance(text, str):
            return ""
        
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"\n]', '', text)
        
        return text.strip()
    
    def _clean_list_items(self, items: List) -> List[str]:
        """Clean list items and remove duplicates"""
        if not items:
            return []
        
        cleaned = []
        seen = set()
        
        for item in items:
            if not item:
                continue
            
            text = self._clean_text(str(item))
            
            if text and text not in seen:
                cleaned.append(text)
                seen.add(text)
        
        return cleaned
    
    async def execute(self, query: str, domain: str, agent_selection: List[str]) -> Dict:
        """
        Execute research workflow with selected agents
        
        Args:
            query: Research question
            domain: Domain (technology, medical, academic, stocks, general)
            agent_selection: List of agent names (case-insensitive)
            
        Returns:
            Consolidated results
        """
        
        print(f"\n🚀 Starting research workflow")
        print(f"   Query: {query}")
        print(f"   Domain: {domain}")
        print(f"   Agents: {agent_selection}")
        
        start_time = datetime.now()
        
        # Initialize results structure
        results = {
            "query": query,
            "domain": domain,
            "timestamp": start_time.isoformat(),
            "agent_results": [],
            "summary": "",
            "key_findings": [],
            "insights": [],
            "total_sources": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "execution_time": 0.0
        }
        
        # Normalize agent names (handle both 'perplexity' and 'Perplexity')
        agent_selection_lower = [agent.lower() for agent in agent_selection]
        
        # Create tasks for parallel execution
        tasks = []
        
        if "perplexity" in agent_selection_lower:
            print("   ✅ Adding Perplexity agent to execution queue")
            tasks.append(("perplexity", self._execute_perplexity(query, domain)))
        
        if "youtube" in agent_selection_lower:
            print("   ✅ Adding YouTube agent to execution queue")
            tasks.append(("youtube", self._execute_youtube(query, domain)))
        
        if "api" in agent_selection_lower:
            print("   ✅ Adding API agent to execution queue")
            tasks.append(("api", self._execute_api(query, domain)))
        
        if not tasks:
            print("   ⚠️  No agents selected!")
            results["error"] = "No agents selected for execution"
            return results
        
        print(f"\n⏳ Executing {len(tasks)} agents in parallel...")
        
        # Execute all agents in parallel
        task_coroutines = [task[1] for task in tasks]
        agent_responses = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process responses
        for idx, response in enumerate(agent_responses):
            agent_name = tasks[idx][0]
            
            if isinstance(response, Exception):
                print(f"   ❌ {agent_name} agent error: {response}")
                results["agent_results"].append({
                    "agent_name": agent_name,
                    "error": str(response),
                    "sources": [],
                    "cost": 0,
                    "tokens": 0
                })
                continue
            
            if response and isinstance(response, dict):
                print(f"   ✅ {agent_name} agent completed: {len(response.get('sources', []))} sources")
                results["agent_results"].append(response)
                results["total_sources"] += len(response.get("sources", []))
                results["total_cost"] += response.get("cost", 0)
                results["total_tokens"] += response.get("tokens", 0)
        
        # Consolidate and clean results
        self._consolidate_results(results)
        
        # Calculate execution time
        end_time = datetime.now()
        results["execution_time"] = (end_time - start_time).total_seconds()
        
        print(f"\n✅ Research complete:")
        print(f"   Total sources: {results['total_sources']}")
        print(f"   Total cost: ${results['total_cost']:.4f}")
        print(f"   Execution time: {results['execution_time']:.1f}s")
        
        return results
    
    async def _execute_perplexity(self, query: str, domain: str) -> Dict:
        """Execute Perplexity agent"""
        try:
            print(f"\n🌐 Initializing Perplexity agent...")
            
            from agents.perplexity_agent import PerplexityAgent
            
            api_key = os.getenv("PERPLEXITY_API_KEY")
            
            if not api_key:
                print(f"   ❌ PERPLEXITY_API_KEY not found in environment")
                return {
                    "agent_name": "perplexity",
                    "error": "PERPLEXITY_API_KEY not found",
                    "sources": [],
                    "cost": 0,
                    "tokens": 0
                }
            
            print(f"   ✅ API key loaded: {api_key[:10]}...")
            
            if not self.perplexity_agent:
                self.perplexity_agent = PerplexityAgent(api_key)
                print(f"   ✅ Agent created: {self.perplexity_agent.name}")
            
            print(f"   🔍 Executing search for: '{query}'")
            print(f"   📁 Domain: {domain}")
            
            # Execute agent
            result = await self.perplexity_agent.execute(
                query=query,
                domain=domain,
                max_tokens=2000
            )
            
            print(f"   ⏱️  Agent execution complete")
            
            if not result:
                print(f"   ❌ No result returned from agent")
                return {
                    "agent_name": "perplexity",
                    "error": "No result returned",
                    "sources": [],
                    "cost": 0,
                    "tokens": 0
                }
            
            if not result.get("success"):
                error = result.get("error", "Unknown error")
                print(f"   ❌ Agent returned error: {error}")
                return {
                    "agent_name": "perplexity",
                    "error": error,
                    "sources": [],
                    "cost": 0,
                    "tokens": 0
                }
            
            # Format sources
            sources = []
            for source in result.get("sources", []):
                sources.append({
                    "title": self._clean_text(source.get("title", "Untitled")),
                    "url": source.get("url", ""),
                    "summary": self._clean_text(source.get("snippet", "No description")),
                    "confidence": 4.5,
                    "date": result.get("timestamp", "")[:10]
                })
            
            print(f"   ✅ Perplexity success: {len(sources)} sources collected")
            
            return {
                "agent_name": "perplexity",
                "sources": sources,
                "summary": self._clean_text(result.get("executive_summary", "")),
                "findings": self._clean_list_items(result.get("key_findings", [])),
                "insights": self._clean_list_items(result.get("insights", [])),
                "cost": result.get("estimated_cost", 0),
                "tokens": result.get("tokens_used", 0)
            }
            
        except ImportError as e:
            print(f"   ❌ Import error: {e}")
            return {
                "agent_name": "perplexity",
                "error": f"Import error: {str(e)}",
                "sources": [],
                "cost": 0,
                "tokens": 0
            }
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
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
            print(f"\n📹 Initializing YouTube agent...")
            
            api_key = os.getenv("YOUTUBE_API_KEY")
            
            if not api_key:
                print(f"   ⚠️  YOUTUBE_API_KEY not configured (optional)")
                return {
                    "agent_name": "youtube",
                    "error": "YOUTUBE_API_KEY not configured",
                    "sources": [],
                    "cost": 0,
                    "tokens": 0
                }
            
            from agents.youtube_researcher import analyze_youtube
            
            print(f"   🔍 Searching videos for: '{query}'")
            
            # Execute YouTube analysis
            state = {
                "topic": query,
                "domain": domain,
                "mode": "extended"
            }
            
            result = analyze_youtube(state)
            youtube_data = result.get("youtube_results", {})
            
            sources = []
            for video in youtube_data.get("sources", []):
                sources.append({
                    "title": self._clean_text(video.get("title", "Untitled")),
                    "url": video.get("url", ""),
                    "summary": self._clean_text(video.get("description", "No description")),
                    "confidence": 3.5,
                    "date": video.get("published_at", "")[:10]
                })
            
            print(f"   ✅ YouTube success: {len(sources)} videos found")
            
            return {
                "agent_name": "youtube",
                "sources": sources,
                "summary": self._clean_text(youtube_data.get("summary", "")),
                "findings": self._clean_list_items(youtube_data.get("findings", [])),
                "insights": self._clean_list_items(youtube_data.get("insights", [])),
                "cost": 0,
                "tokens": 0
            }
            
        except Exception as e:
            print(f"   ❌ YouTube error: {e}")
            return {
                "agent_name": "youtube",
                "error": str(e),
                "sources": [],
                "cost": 0,
                "tokens": 0
            }
    
    async def _execute_api(self, query: str, domain: str) -> Dict:
        """Execute API agent - COMPLETE WORKING VERSION"""
        try:
            print(f"\n📚 Initializing API agent...")
            
            from agents.api_agent import APIAgent
            
            if not self.api_agent:
                self.api_agent = APIAgent()
            
            print(f"   🔍 Executing API agent...")
            
            # Execute and get result
            result = await self.api_agent.execute(query=query, domain=domain)
            
            # Debug: Print what we got
            print(f"   📦 API agent returned: {type(result)}")
            print(f"   📦 Papers in result: {len(result.get('papers', []))}")
            
            # Handle None or empty result
            if not result or not isinstance(result, dict):
                print(f"   ❌ API agent returned invalid result")
                return {
                    "agent_name": "api",
                    "sources": [],
                    "summary": "",
                    "findings": [],
                    "insights": [],
                    "cost": 0,
                    "tokens": 0,
                    "error": "Invalid result from API agent"
                }
            
            # Extract papers
            papers = result.get("papers", [])
            
            print(f"   📄 Processing {len(papers)} papers...")
            
            # Format sources for UI
            formatted_sources = []
            
            for idx, paper in enumerate(papers, 1):
                try:
                    # Safely extract all fields
                    title = paper.get("title") if isinstance(paper, dict) else str(paper)
                    url = paper.get("url", "") if isinstance(paper, dict) else ""
                    summary = paper.get("summary", "") if isinstance(paper, dict) else ""
                    paper_type = paper.get("type", "unknown") if isinstance(paper, dict) else "unknown"
                    published = paper.get("published", "") if isinstance(paper, dict) else ""
                    authors = paper.get("authors", []) if isinstance(paper, dict) else []
                    
                    # Clean text
                    clean_title = self._clean_text(title) if title else f"Source {idx}"
                    clean_summary = self._clean_text(summary) if summary else "No description"
                    
                    # Add to sources
                    formatted_sources.append({
                        "title": clean_title,
                        "url": url if url else "",
                        "summary": clean_summary,
                        "confidence": 4.2 if paper_type == "academic" else 3.8,
                        "date": published[:10] if published else "",
                        "source_type": paper_type,
                        "authors": authors if isinstance(authors, list) else []
                    })
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing paper {idx}: {e}")
                    continue
            
            print(f"   ✅ Formatted {len(formatted_sources)} sources")
            
            # Extract other fields
            summary = result.get("summary", "")
            findings = result.get("findings", [])
            insights = result.get("insights", [])
            
            # Clean lists
            clean_findings = self._clean_list_items(findings) if findings else []
            clean_insights = self._clean_list_items(insights) if insights else []
            
            # Generate fallback summary if needed
            if not summary:
                academic_count = len([s for s in formatted_sources if s.get("source_type") == "academic"])
                news_count = len([s for s in formatted_sources if s.get("source_type") == "news"])
                summary = f"Retrieved {len(formatted_sources)} sources: {academic_count} academic papers and {news_count} news articles"
            
            final_result = {
                "agent_name": "api",
                "sources": formatted_sources,
                "summary": self._clean_text(summary),
                "findings": clean_findings,
                "insights": clean_insights,
                "cost": 0,
                "tokens": 0
            }
            
            print(f"   ✅ API agent complete: {len(formatted_sources)} sources")
            
            return final_result
            
        except ImportError as e:
            print(f"   ❌ Import error: {e}")
            return {
                "agent_name": "api",
                "sources": [],
                "summary": "",
                "findings": [],
                "insights": [],
                "cost": 0,
                "tokens": 0,
                "error": f"Import error: {str(e)}"
            }
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "agent_name": "api",
                "sources": [],
                "summary": "",
                "findings": [],
                "insights": [],
                "cost": 0,
                "tokens": 0,
                "error": f"Error: {str(e)}"
            }
    
    def _consolidate_results(self, results: Dict):
        """Consolidate results from all agents - ENHANCED"""
        
        all_findings = []
        all_insights = []
        best_summary = ""
        
        print(f"\n📊 Consolidating results...")
        print(f"   Agent results count: {len(results.get('agent_results', []))}")
        
        for idx, agent_result in enumerate(results.get("agent_results", []), 1):
            agent_name = agent_result.get("agent_name", f"agent_{idx}")
            
            print(f"\n   {idx}. Processing {agent_name}:")
            
            # Check for error
            if agent_result.get("error"):
                print(f"      ⚠️  Has error: {agent_result['error']}")
                continue
            
            # Check for sources
            sources = agent_result.get("sources", [])
            print(f"      📚 Sources: {len(sources)}")
            
            # Check for findings
            findings = agent_result.get("findings", [])
            if findings and isinstance(findings, list):
                print(f"      🔍 Findings: {len(findings)}")
                all_findings.extend([str(f).strip() for f in findings if f])
            
            # Check for insights
            insights = agent_result.get("insights", [])
            if insights and isinstance(insights, list):
                print(f"      💡 Insights: {len(insights)}")
                all_insights.extend([str(i).strip() for i in insights if i])
            
            # Check for summary
            summary = agent_result.get("summary", "")
            if summary and isinstance(summary, str) and summary.strip():
                print(f"      📝 Summary: {len(summary)} chars")
                if agent_name == "perplexity" or not best_summary:
                    best_summary = summary
        
        # Clean and deduplicate
        results["key_findings"] = self._clean_list_items(all_findings)[:10]
        results["insights"] = self._clean_list_items(all_insights)[:8]
        results["summary"] = self._clean_text(best_summary) if best_summary else self._generate_fallback_summary(results)
        
        print(f"\n   ✅ Consolidated:")
        print(f"      - Findings: {len(results['key_findings'])}")
        print(f"      - Insights: {len(results['insights'])}")
        print(f"      - Summary: {len(results['summary'])} chars")
    
    def _generate_fallback_summary(self, results: Dict) -> str:
        """Generate fallback summary"""
        agent_count = len([r for r in results.get("agent_results", []) if not r.get("error")])
        total_sources = results.get("total_sources", 0)
        
        return (
            f"Research completed using {agent_count} specialized agents. "
            f"Collected {total_sources} sources from multiple channels."
        )