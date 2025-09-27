# ============================================================================
# FILE 2: test_perplexity.py (FINAL WORKING VERSION)
# Replace entire file with this:
# ============================================================================
"""
Perplexity Integration Test
Tests the complete agent workflow
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.perplexity_agent import PerplexityAgent
from dotenv import load_dotenv

async def test_perplexity():
    """Test Perplexity agent with different domains"""
    
    load_dotenv()
    
    print("="*70)
    print("PERPLEXITY AGENT TEST - Full Integration")
    print("="*70)
    
    # Check API key
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("\n❌ PERPLEXITY_API_KEY not found in .env")
        return
    
    print(f"\n✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Initialize agent
    try:
        agent = PerplexityAgent(api_key)
        print(f"✅ Agent initialized: {agent.name}")
        print(f"   Model: {agent.client.model}")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Test cases for different domains
    test_cases = [
        {
            "query": "What are the latest AI trends in 2025?",
            "domain": "technology",
            "max_tokens": 500
        },
        {
            "query": "What is the current stock price trend for NVIDIA?",
            "domain": "stocks",
            "max_tokens": 500
        }
    ]
    
    results = []
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {idx}: {test['domain'].upper()} Domain")
        print(f"{'='*70}")
        print(f"Query: {test['query']}")
        print(f"\n⏳ Executing (may take 10-30 seconds)...")
        
        try:
            result = await agent.execute(
                query=test['query'],
                domain=test['domain'],
                max_tokens=test['max_tokens']
            )
            
            if result.get('success'):
                print(f"\n✅ SUCCESS!")
                
                # Display executive summary
                print(f"\n📊 Executive Summary:")
                summary = result.get('executive_summary', 'N/A')
                print(f"   {summary}")
                
                # Display key findings
                findings = result.get('key_findings', [])
                if findings:
                    print(f"\n🔍 Key Findings ({len(findings)}):")
                    for i, finding in enumerate(findings[:3], 1):
                        print(f"   {i}. {finding[:100]}...")
                
                # Display insights
                insights = result.get('insights', [])
                if insights:
                    print(f"\n💡 Insights ({len(insights)}):")
                    for i, insight in enumerate(insights[:2], 1):
                        print(f"   {i}. {insight[:100]}...")
                
                # Display metrics
                print(f"\n📈 Metrics:")
                print(f"   Tokens Used: {result.get('tokens_used', 0)}")
                print(f"   Cost: ${result.get('estimated_cost', 0):.6f}")
                print(f"   Citations: {result.get('citation_count', 0)}")
                print(f"   Model: {result.get('model', 'N/A')}")
                
                # Display sources
                sources = result.get('sources', [])
                if sources:
                    print(f"\n🔗 Sample Sources:")
                    for i, source in enumerate(sources[:3], 1):
                        print(f"   {i}. {source.get('title', 'Untitled')}")
                        print(f"      {source.get('url', 'No URL')[:60]}...")
                
                # Save full result
                filename = f"result_{idx}_{test['domain']}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Full result saved: {filename}")
                
                results.append(result)
                
            else:
                print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            import traceback
            traceback.print_exc()
        
        # Wait between requests
        if idx < len(test_cases):
            await asyncio.sleep(2)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(test_cases) - len(results)}")
    
    if results:
        total_tokens = sum(r.get('tokens_used', 0) for r in results)
        total_cost = sum(r.get('estimated_cost', 0) for r in results)
        print(f"\nTotal Tokens: {total_tokens}")
        print(f"Total Cost: ${total_cost:.6f}")
    
    print(f"\n{'='*70}")
    print("✅ Testing Complete!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        asyncio.run(test_perplexity())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()