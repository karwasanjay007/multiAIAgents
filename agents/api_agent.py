# ============================================================================
# FILE: agents/api_agent.py
# FIXED VERSION - Proper domain-based API routing
# ============================================================================

from agents.base_agent import BaseAgent
from typing import Dict, List
import asyncio


class APIAgent(BaseAgent):
    """
    API Agent for academic papers and news
    Uses real APIs with domain-specific routing
    """
    
    def __init__(self):
        self.name = "API Research Agent"
    
    async def execute(self, query: str, domain: str = "general") -> Dict:
        """
        Execute API research with domain-specific routing
        
        Args:
            query: Research question
            domain: Research domain (stocks, technology, medical, academic)
            
        Returns:
            Dict with papers, summary, findings, insights
        """
        
        print(f"   📚 API Agent starting for domain: {domain}")
        print(f"   🔍 Query: {query}")
        
        papers = []
        findings = []
        insights = []
        
        # Domain-specific API routing
        if domain in ["stocks", "technology", "general"]:
            print(f"   🌐 Using news/web sources for {domain} domain")
            
            # For business/tech/stocks - use news and web sources
            try:
                from agents.news_analyzer import analyze_news
                from agents.web_researcher import research_web
                from graph.state import ResearchState
                
                state = {
                    "topic": query,
                    "domain": domain,
                    "mode": "extended"
                }
                
                # Fetch news
                print(f"   📰 Fetching news articles...")
                news_result = analyze_news(state)
                
                # Fetch web results
                print(f"   🔍 Fetching web results...")
                web_result = research_web(state)
                
                # Process news results
                news_data = news_result.get("news_results", {})
                news_sources = news_data.get("sources", [])
                
                for source in news_sources:
                    source_name = source.get("name", "")
                    items = source.get("items", [])
                    print(f"   ✅ {source_name}: {len(items)} items")
                    
                    for item in items:
                        papers.append({
                            "title": item.get("title", "Untitled"),
                            "url": item.get("source", ""),
                            "summary": item.get("summary", ""),
                            "published": item.get("published_date", ""),
                            "type": "news"
                        })
                        
                        if item.get("summary"):
                            findings.append(f"News: {item['title']}")
                
                # Process web results
                web_data = web_result.get("web_results", {})
                web_sources = web_data.get("sources", [])
                
                for source in web_sources:
                    source_name = source.get("name", "")
                    items = source.get("items", [])
                    print(f"   ✅ {source_name}: {len(items)} items")
                    
                    for item in items:
                        papers.append({
                            "title": item.get("title", "Untitled"),
                            "url": item.get("source", ""),
                            "summary": item.get("summary", ""),
                            "published": item.get("published_date", ""),
                            "type": "web"
                        })
                
                news_count = len([p for p in papers if p.get("type") == "news"])
                web_count = len([p for p in papers if p.get("type") == "web"])
                
                insights.append(f"Found {news_count} news articles")
                insights.append(f"Found {web_count} web sources")
                
                summary = f"Retrieved {len(papers)} sources from news and web APIs for {domain} domain."
                
            except Exception as e:
                print(f"   ⚠️  Error fetching news/web: {e}")
                summary = f"Error fetching data: {str(e)}"
        
        elif domain in ["medical", "academic"]:
            print(f"   🎓 Using academic sources for {domain} domain")
            
            # For medical/academic - use academic sources
            try:
                from agents.academic_researcher import research_academic_papers
                from graph.state import ResearchState
                
                state = {
                    "topic": query,
                    "domain": domain,
                    "mode": "extended"
                }
                
                # Fetch academic papers
                print(f"   📖 Fetching academic papers...")
                academic_result = research_academic_papers(state)
                
                # Process results
                academic_data = academic_result.get("academic_results", {})
                academic_sources = academic_data.get("sources", [])
                
                for source in academic_sources:
                    source_name = source.get("name", "")
                    items = source.get("items", [])
                    print(f"   ✅ {source_name}: {len(items)} items")
                    
                    for item in items:
                        papers.append({
                            "title": item.get("title", "Untitled"),
                            "url": item.get("source", ""),
                            "summary": item.get("summary", ""),
                            "published": item.get("published_date", ""),
                            "authors": item.get("authors", []),
                            "type": "academic"
                        })
                        
                        if item.get("summary"):
                            findings.append(f"Academic: {item['title']}")
                
                academic_count = len(papers)
                
                if academic_count > 0:
                    insights.append(f"Found {academic_count} peer-reviewed academic sources")
                
                summary = f"Retrieved {len(papers)} academic papers for {domain} domain."
                
            except Exception as e:
                print(f"   ⚠️  Error fetching academic papers: {e}")
                summary = f"Error fetching data: {str(e)}"
        
        else:
            # Unknown domain - use all sources
            print(f"   ⚠️  Unknown domain '{domain}', using all available sources")
            
            try:
                from agents.academic_researcher import research_academic_papers
                from agents.news_analyzer import analyze_news
                from graph.state import ResearchState
                
                state = {
                    "topic": query,
                    "domain": domain,
                    "mode": "extended"
                }
                
                # Fetch from all sources
                print(f"   📖 Fetching academic papers...")
                academic_result = research_academic_papers(state)
                
                print(f"   📰 Fetching news articles...")
                news_result = analyze_news(state)
                
                # Process academic results
                academic_data = academic_result.get("academic_results", {})
                academic_sources = academic_data.get("sources", [])
                
                for source in academic_sources:
                    source_name = source.get("name", "")
                    items = source.get("items", [])
                    print(f"   ✅ {source_name}: {len(items)} items")
                    
                    for item in items:
                        papers.append({
                            "title": item.get("title", "Untitled"),
                            "url": item.get("source", ""),
                            "summary": item.get("summary", ""),
                            "published": item.get("published_date", ""),
                            "authors": item.get("authors", []),
                            "type": "academic"
                        })
                
                # Process news results
                news_data = news_result.get("news_results", {})
                news_sources = news_data.get("sources", [])
                
                for source in news_sources:
                    source_name = source.get("name", "")
                    items = source.get("items", [])
                    print(f"   ✅ {source_name}: {len(items)} items")
                    
                    for item in items:
                        papers.append({
                            "title": item.get("title", "Untitled"),
                            "url": item.get("source", ""),
                            "summary": item.get("summary", ""),
                            "published": item.get("published_date", ""),
                            "type": "news"
                        })
                
                academic_count = len([p for p in papers if p.get("type") == "academic"])
                news_count = len([p for p in papers if p.get("type") == "news"])
                
                insights.append(f"Found {academic_count} academic papers and {news_count} news articles")
                
                summary = f"Retrieved {len(papers)} sources from multiple APIs."
                
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                summary = f"Error fetching data: {str(e)}"
        
        print(f"   ✅ API Agent complete: {len(papers)} sources retrieved")
        
        return {
            "papers": papers,
            "summary": summary,
            "findings": findings,
            "insights": insights
        }
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "name": self.name,
            "type": "api",
            "available": True
        }