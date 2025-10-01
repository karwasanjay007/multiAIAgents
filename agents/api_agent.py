# ============================================================================
# FILE: agents/api_agent.py
# COMPLETE REPLACEMENT - This is the REAL working version
# ============================================================================

from agents.base_agent import BaseAgent
from typing import Dict
import asyncio


class APIAgent(BaseAgent):
    """
    API Agent for academic papers and news
    Uses real APIs: arXiv, Google Scholar, News
    """
    
    def __init__(self):
        self.name = "API Research Agent"
    
    async def execute(self, query: str, domain: str = "general") -> Dict:
        """
        Execute API research using real academic and news APIs
        
        Args:
            query: Research question
            domain: Research domain (stocks, technology, medical, academic)
            
        Returns:
            Dict with papers, summary, findings, insights
        """
        
        print(f"   📚 API Agent searching for: {domain}")
        print(f"   🔍 Query: {query}")
        
        try:
            # Import the real research functions
            from agents.academic_researcher import research_academic_papers
            from agents.news_analyzer import analyze_news
            from graph.state import ResearchState
            
            # Create state
            state = {
                "topic": query,
                "domain": domain,
                "mode": "extended"  # Get more results
            }
            
            # Execute both research functions
            print(f"   📖 Fetching academic papers...")
            academic_result = research_academic_papers(state)
            
            print(f"   📰 Fetching news articles...")
            news_result = analyze_news(state)
            
            # Process results
            papers = []
            findings = []
            insights = []
            
            # Extract academic papers
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
                    
                    # Add to findings
                    if item.get("summary"):
                        findings.append(f"Academic: {item['title']}")
            
            # Extract news articles
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
                    
                    # Add to findings
                    if item.get("summary"):
                        findings.append(f"News: {item['title']}")
            
            # Generate insights
            academic_count = len([p for p in papers if p.get("type") == "academic"])
            news_count = len([p for p in papers if p.get("type") == "news"])
            
            if academic_count > 0:
                insights.append(f"Found {academic_count} peer-reviewed academic sources")
            if news_count > 0:
                insights.append(f"Collected {news_count} current news articles")
            if papers:
                insights.append("Multiple sources provide comprehensive coverage")
            
            summary = f"Retrieved {len(papers)} sources: {academic_count} academic papers and {news_count} news articles."
            
            print(f"   ✅ API Agent complete: {len(papers)} total sources")
            
            return {
                "papers": papers,
                "summary": summary,
                "findings": findings[:10],  # Limit to 10
                "insights": insights
            }
            
        except ImportError as e:
            print(f"   ❌ Import Error: {e}")
            print(f"   ⚠️  Falling back to direct API calls...")
            
            # Fallback: Use direct API calls without langchain
            return await self._execute_direct_apis(query, domain)
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
            # Return empty but valid structure
            return {
                "papers": [],
                "summary": f"Error fetching data: {str(e)}",
                "findings": [],
                "insights": []
            }
    
    async def _execute_direct_apis(self, query: str, domain: str) -> Dict:
        """
        Fallback method using direct API calls (no langchain dependencies)
        """
        
        papers = []
        findings = []
        insights = []
        
        try:
            # Use direct arXiv API
            print(f"   📖 Trying direct arXiv API...")
            arxiv_papers = await self._fetch_arxiv_direct(query)
            papers.extend(arxiv_papers)
            
            if arxiv_papers:
                findings.append(f"Found {len(arxiv_papers)} papers from arXiv")
                insights.append("Academic sources provide peer-reviewed research")
        except Exception as e:
            print(f"   ⚠️  arXiv error: {e}")
        
        try:
            # Use DuckDuckGo for news (simple scraping)
            print(f"   📰 Trying news search...")
            news_articles = await self._fetch_news_direct(query)
            papers.extend(news_articles)
            
            if news_articles:
                findings.append(f"Found {len(news_articles)} news articles")
                insights.append("Current news provides real-time perspective")
        except Exception as e:
            print(f"   ⚠️  News error: {e}")
        
        summary = f"Retrieved {len(papers)} sources using direct API calls."
        
        print(f"   ✅ Direct API fetch complete: {len(papers)} sources")
        
        return {
            "papers": papers,
            "summary": summary,
            "findings": findings,
            "insights": insights
        }
    
    async def _fetch_arxiv_direct(self, query: str, max_results: int = 5) -> list:
        """Fetch papers directly from arXiv API"""
        
        import aiohttp
        import xml.etree.ElementTree as ET
        
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        papers = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        root = ET.fromstring(xml_content)
                        
                        # Parse XML
                        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
                        
                        for entry in root.findall('atom:entry', namespace):
                            title_elem = entry.find('atom:title', namespace)
                            summary_elem = entry.find('atom:summary', namespace)
                            link_elem = entry.find('atom:id', namespace)
                            published_elem = entry.find('atom:published', namespace)
                            
                            authors = []
                            for author in entry.findall('atom:author', namespace):
                                name_elem = author.find('atom:name', namespace)
                                if name_elem is not None:
                                    authors.append(name_elem.text)
                            
                            papers.append({
                                "title": title_elem.text.strip() if title_elem is not None else "Untitled",
                                "url": link_elem.text if link_elem is not None else "",
                                "summary": summary_elem.text.strip() if summary_elem is not None else "",
                                "published": published_elem.text[:10] if published_elem is not None else "",
                                "authors": authors,
                                "type": "academic"
                            })
        except Exception as e:
            print(f"   ⚠️  arXiv API error: {e}")
        
        return papers
    
    async def _fetch_news_direct(self, query: str, max_results: int = 5) -> list:
        """Fetch news using simple search"""
        
        # For now, return empty - can add NewsAPI or other news sources
        # This requires API keys, so leaving as placeholder
        
        articles = []
        
        # TODO: Add NewsAPI integration if API key available
        # TODO: Add other news sources
        
        return articles
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "name": self.name,
            "type": "api",
            "available": True
        }