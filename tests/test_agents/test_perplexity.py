# ============================================================================
# FILE: test_perplexity.py (NEW - For Testing)
# ============================================================================
"""
Test script for Perplexity integration
Run: python test_perplexity.py
"""

import asyncio
import json
from agents.perplexity_agent import PerplexityAgent
from dotenv import load_dotenv

async def test_perplexity():
    """Test Perplexity agent with sample queries"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize agent
    try:
        agent = PerplexityAgent()
        print("✅ Perplexity Agent initialized successfully\n")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Make sure PERPLEXITY_API_KEY is set in .env file")
        return
    
    # Test queries for different domains
    test_cases = [
        {
            "query": "What are the latest AI trends in 2025?",
            "domain": "technology"
        },
        {
            "query": "Current performance of NVIDIA stock",
            "domain": "stocks"
        },
        {
            "query": "Latest breakthrough in Alzheimer's treatment",
            "domain": "medical"
        }
    ]
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {idx}: {test['domain'].upper()}")
        print(f"Query: {test['query']}")
        print(f"{'='*60}\n")
        
        result = await agent.execute(
            query=test["query"],
            domain=test["domain"],
            max_tokens=1500  # Lower for testing
        )
        
        if result.get("success"):
            print(f"✅ Success!\n")
            print(f"Executive Summary:")
            print(f"{result.get('executive_summary', 'N/A')}\n")
            
            print(f"Key Findings:")
            for finding in result.get('key_findings', [])[:3]:
                print(f"  • {finding}")
            
            print(f"\nToken Usage:")
            print(f"  - Prompt tokens: {result.get('prompt_tokens', 0)}")
            print(f"  - Completion tokens: {result.get('completion_tokens', 0)}")
            print(f"  - Total tokens: {result.get('tokens_used', 0)}")
            
            print(f"\nCost: ${result.get('estimated_cost', 0):.4f}")
            print(f"Sources: {result.get('citation_count', 0)}")
            
            # Save full result to file
            filename = f"test_result_{idx}_{test['domain']}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n📄 Full result saved to: {filename}")
            
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Wait between requests
        if idx < len(test_cases):
            await asyncio.sleep(2)
    
    print(f"\n{'='*60}")
    print("✅ All tests completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_perplexity())
