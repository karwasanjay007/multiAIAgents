# ============================================================================
# FILE: quick_test.py
# Single file to test Perplexity API with correct model
# ============================================================================
import asyncio
import aiohttp
import os
import sys
from dotenv import load_dotenv

async def test_perplexity():
    """Quick test of Perplexity API"""
    
    print("="*60)
    print("PERPLEXITY API QUICK TEST")
    print("="*60)
    
    # Load API key
    load_dotenv()
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        print("\n❌ ERROR: PERPLEXITY_API_KEY not found in .env file")
        print("\nSetup:")
        print("1. Create .env file in project root")
        print("2. Add: PERPLEXITY_API_KEY=pplx-your-key-here")
        return
    
    print(f"\n✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # API configuration
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with correct model name
    payload = {
        "model": "sonar-pro",  # Correct model name
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful research assistant. Provide concise, accurate answers."
            },
            {
                "role": "user",
                "content": "What are the latest AI trends in 2025? Provide a brief 2-3 sentence summary."
            }
        ],
        "max_tokens": 200,
        "temperature": 0.2,
        "return_citations": True
    }
    
    print(f"\n📡 Testing API...")
    print(f"   Model: {payload['model']}")
    print(f"   Query: {payload['messages'][1]['content'][:50]}...")
    print(f"\n⏳ Waiting for response (may take 10-30 seconds)...\n")
    
    try:
        # Set Windows-specific event loop if needed
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                headers=headers, 
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                status = response.status
                print(f"📊 Status Code: {status}")
                
                if status == 200:
                    result = await response.json()
                    
                    # Extract response
                    content = result["choices"][0]["message"]["content"]
                    usage = result.get("usage", {})
                    citations = result.get("citations", [])
                    
                    print("\n" + "="*60)
                    print("✅ SUCCESS!")
                    print("="*60)
                    
                    print(f"\n📝 Response:\n{content}\n")
                    
                    print(f"📈 Token Usage:")
                    print(f"   Input: {usage.get('prompt_tokens', 0)}")
                    print(f"   Output: {usage.get('completion_tokens', 0)}")
                    print(f"   Total: {usage.get('total_tokens', 0)}")
                    
                    print(f"\n💰 Estimated Cost: ${(usage.get('total_tokens', 0) / 1_000_000):.6f}")
                    
                    if citations:
                        print(f"\n🔗 Citations ({len(citations)}):")
                        for i, citation in enumerate(citations[:3], 1):
                            if isinstance(citation, str):
                                print(f"   {i}. {citation}")
                            elif isinstance(citation, dict):
                                print(f"   {i}. {citation.get('url', 'N/A')}")
                    
                    print("\n" + "="*60)
                    print("🎉 Perplexity integration is working!")
                    print("="*60)
                    
                    return True
                    
                else:
                    error_text = await response.text()
                    print(f"\n❌ API Error {status}:")
                    print(f"{error_text}\n")
                    
                    # Common error fixes
                    if status == 401:
                        print("💡 Fix: Check your API key is correct")
                    elif status == 400:
                        print("💡 Fix: Check the model name or parameters")
                    elif status == 429:
                        print("💡 Fix: Rate limit exceeded, wait a moment")
                    
                    return False
                    
    except asyncio.TimeoutError:
        print("\n❌ Request timed out after 60 seconds")
        print("💡 Try again or check your internet connection")
        return False
        
    except aiohttp.ClientError as e:
        print(f"\n❌ Connection Error: {e}")
        print("💡 Check your internet connection")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_perplexity())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)