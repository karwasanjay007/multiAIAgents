# ============================================================================
# FILE 1: services/perplexity_client.py
# COMPLETE REPLACEMENT - Copy entire content
# ============================================================================
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

class PerplexityClient:
    """Async client for Perplexity API with deep search"""
    
    def __init__(self, api_key: str):
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
            domain: Research domain (stocks, medical, academic, technology, general)
            max_tokens: Maximum response tokens
            
        Returns:
            Dict with success, sources, findings, etc.
        """
        
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
                        print(f"   ❌ API Error {response.status}: {error_text[:200]}")
                        return {
                            "success": False,
                            "error": f"API error {response.status}",
                            "tokens_used": 0
                        }
                    
                    result = await response.json()
                    return self._parse_response(result, query, domain)
        
        except asyncio.TimeoutError:
            print(f"   ❌ Request timeout after 120s")
            return {
                "success": False,
                "error": "Request timeout",
                "tokens_used": 0
            }
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "tokens_used": 0
            }
    
    def _get_system_prompt(self, domain: str) -> str:
        """Get domain-specific system prompt"""
        
        base = """You are an expert research analyst. Provide comprehensive, well-structured analysis with:

1. EXECUTIVE SUMMARY (2-3 sentences)
2. KEY FINDINGS (3-5 specific bullet points)
3. DETAILED ANALYSIS (comprehensive evaluation)
4. INSIGHTS (2-4 strategic observations)

Format your response with clear section headers."""

        domain_prompts = {
            "stocks": base + "\n\nFocus on: Stock performance, financial metrics, analyst ratings, market trends, earnings, and investment outlook.",
            "medical": base + "\n\nFocus on: Clinical trials, peer-reviewed studies, treatment efficacy, safety data, and regulatory status.",
            "academic": base + "\n\nFocus on: Scholarly research, peer-reviewed papers, citations, methodologies, and academic discourse.",
            "technology": base + "\n\nFocus on: Technology developments, product launches, innovations, market impact, and technical specifications.",
            "general": base
        }
        
        return domain_prompts.get(domain, domain_prompts["general"])
    
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
            
            # Extract structured sections
            sections = self._extract_sections(content)
            
            # Format citations as sources
            sources = self._format_citations(citations)
            
            # Calculate cost (sonar-pro: $5 per 1M tokens)
            estimated_cost = (tokens_used / 1_000_000) * 5.0
            
            print(f"   ✅ API Success: {len(sources)} sources, {tokens_used} tokens")
            
            return {
                "success": True,
                "query": query,
                "domain": domain,
                "timestamp": datetime.now().isoformat(),
                "executive_summary": sections.get("summary", ""),
                "key_findings": sections.get("findings", []),
                "detailed_analysis": sections.get("analysis", ""),
                "insights": sections.get("insights", []),
                "sources": sources,
                "citation_count": len(sources),
                "tokens_used": tokens_used,
                "estimated_cost": estimated_cost,
                "model": self.model
            }
            
        except Exception as e:
            print(f"   ❌ Parse error: {e}")
            return {
                "success": False,
                "error": f"Parse error: {str(e)}",
                "tokens_used": 0
            }
    
    def _extract_sections(self, content: str) -> Dict:
        """Extract structured sections from content"""
        
        sections = {
            "summary": "",
            "findings": [],
            "analysis": "",
            "insights": []
        }
        
        content_lower = content.lower()
        
        # Extract Executive Summary
        summary_markers = ["executive summary", "summary:", "overview:"]
        for marker in summary_markers:
            if marker in content_lower:
                try:
                    start = content_lower.index(marker)
                    text = content[start + len(marker):].strip()
                    
                    # Find end (next section or double newline)
                    end = 500
                    for delimiter in ["\n\n", "key finding", "analysis:"]:
                        pos = text[:end].lower().find(delimiter)
                        if pos > 0:
                            end = pos
                            break
                    
                    sections["summary"] = text[:end].strip()
                    break
                except:
                    pass
        
        # Extract Key Findings
        finding_markers = ["key finding", "findings:", "main points:"]
        for marker in finding_markers:
            if marker in content_lower:
                try:
                    start = content_lower.index(marker)
                    text = content[start:].strip()
                    
                    lines = text.split("\n")
                    for line in lines[:15]:
                        line = line.strip()
                        # Check if line starts with bullet or number
                        if line and any(line.startswith(x) for x in ["-", "•", "*", "1.", "2.", "3.", "4.", "5."]):
                            finding = line.lstrip("-•*0123456789. ").strip()
                            if len(finding) > 20:
                                sections["findings"].append(finding)
                        
                        if len(sections["findings"]) >= 5:
                            break
                    break
                except:
                    pass
        
        # Extract Insights
        insight_markers = ["insights:", "key insights", "observations:"]
        for marker in insight_markers:
            if marker in content_lower:
                try:
                    start = content_lower.index(marker)
                    text = content[start:].strip()
                    
                    lines = text.split("\n")
                    for line in lines[:10]:
                        line = line.strip()
                        if line and any(line.startswith(x) for x in ["-", "•", "*", "1.", "2.", "3.", "4."]):
                            insight = line.lstrip("-•*0123456789. ").strip()
                            if len(insight) > 20:
                                sections["insights"].append(insight)
                        
                        if len(sections["insights"]) >= 4:
                            break
                    break
                except:
                    pass
        
        # Fallbacks
        if not sections["summary"]:
            sentences = content.split(". ")[:3]
            sections["summary"] = ". ".join(sentences).strip() + "."
        
        if not sections["findings"]:
            sentences = [s.strip() for s in content.split(". ") if len(s.strip()) > 40]
            sections["findings"] = sentences[:5]
        
        sections["analysis"] = content
        
        return sections
    
    def _format_citations(self, citations: List) -> List[Dict]:
        """Format citations as source objects"""
        
        sources = []
        
        for idx, citation in enumerate(citations, 1):
            if isinstance(citation, str):
                sources.append({
                    "id": idx,
                    "url": citation,
                    "title": f"Source {idx}",
                    "snippet": "",
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
