# ============================================================================
# FILE: services/perplexity_client.py
# COMPLETE REPLACEMENT - Copy this entire file
# ============================================================================
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime

class PerplexityClient:
    """Client for Perplexity API with deep search capabilities"""
    
    SUPPORTED_DOMAINS = ["stocks", "medical", "academic", "technology", "general"]
    
    def __init__(self, api_key: str):
        """Initialize Perplexity client with API key"""
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.model = "sonar-pro"
        
    async def deep_search(
        self, 
        query: str, 
        domain: str = "general",
        max_tokens: int = 2000
    ) -> Dict:
        """
        Perform deep search using Perplexity API
        
        Args:
            query: Research question
            domain: Research domain
            max_tokens: Maximum tokens for response
            
        Returns:
            Dictionary containing search results and metadata
        """
        
        if domain not in self.SUPPORTED_DOMAINS:
            domain = "general"
        
        system_prompt = self._get_system_prompt(domain)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "return_images": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"API Error {response.status}: {error_text}",
                            "tokens_used": 0,
                            "status_code": response.status
                        }
                    
                    result = await response.json()
                    return self._parse_response(result, query, domain)
                    
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "tokens_used": 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "tokens_used": 0
            }
    
    def _get_system_prompt(self, domain: str) -> str:
        """Get domain-specific system prompt"""
        
        base = """You are an expert research assistant. Provide detailed, well-structured research with:

**Executive Summary** (2-3 sentences): Concise overview of main findings.
**Key Findings** (3-5 bullet points): Most important discoveries.
**Detailed Analysis**: Thorough analysis with evidence.
**Insights**: Patterns, trends, and implications.

Be thorough, accurate, and cite sources."""

        domains = {
            "stocks": base + "\n\n**Focus**: Stock market data, earnings, analyst opinions, market trends.",
            "medical": base + "\n\n**Focus**: Peer-reviewed studies, clinical trials, medical research, FDA approvals.",
            "academic": base + "\n\n**Focus**: Scholarly articles, research papers, academic publications, citations.",
            "technology": base + "\n\n**Focus**: Tech developments, product launches, industry trends, innovations.",
            "general": base + "\n\n**Focus**: Comprehensive research across all relevant sources."
        }
        
        return domains.get(domain, domains["general"])
    
    def _parse_response(self, result: Dict, query: str, domain: str) -> Dict:
        """Parse API response into structured format"""
        
        try:
            choices = result.get("choices", [])
            if not choices:
                return {
                    "success": False,
                    "error": "No response from API",
                    "tokens_used": 0
                }
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            citations = result.get("citations", [])
            usage = result.get("usage", {})
            
            tokens_used = usage.get("total_tokens", 0)
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            sections = self._extract_sections(content)
            
            return {
                "success": True,
                "query": query,
                "domain": domain,
                "timestamp": datetime.now().isoformat(),
                "executive_summary": sections.get("summary", content[:200]),
                "key_findings": sections.get("findings", []),
                "detailed_analysis": sections.get("analysis", content),
                "insights": sections.get("insights", []),
                "sources": self._format_citations(citations),
                "citation_count": len(citations),
                "tokens_used": tokens_used,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "token_breakdown": {
                    "input": prompt_tokens,
                    "output": completion_tokens,
                    "total": tokens_used
                },
                "estimated_cost": (tokens_used / 1_000_000) * 1.0,
                "full_response": content,
                "model": self.model,
                "search_quality": "deep" if tokens_used > 1000 else "standard"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Parse error: {str(e)}",
                "tokens_used": 0
            }
    
    def _extract_sections(self, content: str) -> Dict:
        """Extract structured sections from content"""
        
        sections = {"summary": "", "findings": [], "analysis": "", "insights": []}
        content_lower = content.lower()
        
        # Extract summary
        if "executive summary" in content_lower:
            try:
                start = content_lower.index("executive summary")
                text = content[start + 17:].strip()
                end = text.lower().find("\n\n")
                if end > 0:
                    sections["summary"] = text[:end].strip().lstrip(":").strip()
                else:
                    sections["summary"] = text[:200].strip()
            except:
                pass
        
        # Extract findings
        for marker in ["key findings", "findings:"]:
            if marker in content_lower:
                try:
                    start = content_lower.index(marker)
                    text = content[start + len(marker):].strip()
                    end = 500
                    for stop in ["\n\n**", "analysis:", "insights:"]:
                        idx = text.lower().find(stop)
                        if 0 < idx < end:
                            end = idx
                    findings_text = text[:end]
                    for line in findings_text.split("\n"):
                        line = line.strip()
                        if line and any(line.startswith(x) for x in ["-", "•", "*", "1", "2", "3"]):
                            sections["findings"].append(line.lstrip("-•*0123456789. "))
                    break
                except:
                    pass
        
        # Extract insights
        if "insights" in content_lower:
            try:
                start = content_lower.index("insights")
                text = content[start + 8:].strip()
                end = 300
                for line in text[:end].split("\n"):
                    line = line.strip()
                    if line and any(line.startswith(x) for x in ["-", "•", "*", "1", "2"]):
                        sections["insights"].append(line.lstrip("-•*0123456789. "))
            except:
                pass
        
        # Fallbacks
        if not sections["summary"]:
            sentences = content.split(". ")[:2]
            sections["summary"] = ". ".join(sentences).strip() + "."
        
        if not sections["findings"]:
            sentences = [s for s in content.split(". ") if len(s) > 30]
            sections["findings"] = sentences[:5]
        
        sections["analysis"] = content
        
        return sections
    
    def _format_citations(self, citations: List) -> List[Dict]:
        """Format citations into structured sources"""
        
        sources = []
        for idx, citation in enumerate(citations, 1):
            if isinstance(citation, str):
                sources.append({
                    "id": idx,
                    "url": citation,
                    "title": f"Source {idx}",
                    "type": "web"
                })
            elif isinstance(citation, dict):
                sources.append({
                    "id": idx,
                    "url": citation.get("url", ""),
                    "title": citation.get("title", f"Source {idx}"),
                    "snippet": citation.get("snippet", ""),
                    "type": citation.get("type", "web")
                })
        
        return sources