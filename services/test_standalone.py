# ============================================================================
# FILE: test_standalone.py
# Completely standalone test that WILL produce output
# ============================================================================
import sys
import os

# Force output immediately
print("="*60, flush=True)
print("STANDALONE PERPLEXITY TEST", flush=True)
print("="*60, flush=True)

try:
    # Test 1: Basic imports
    print("\n[1] Testing basic imports...", flush=True)
    import asyncio
    print("    ✅ asyncio", flush=True)
    
    import aiohttp
    print("    ✅ aiohttp", flush=True)
    
    from dotenv import load_dotenv
    print("    ✅ dotenv", flush=True)
    
    # Test 2: Load environment
    print("\n[2] Loading .env file...", flush=True)
    load_dotenv()
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("    ❌ PERPLEXITY_API_KEY not found!", flush=True)
        print("    Create .env file with: PERPLEXITY_API_KEY=your-key", flush=True)
        sys.exit(1)
    
    print(f"    ✅ API Key: {api_key[:10]}...{api_key[-4:]}", flush=True)
    
    # Test 3: Direct API call without any custom classes
    print("\n[3] Making direct API call...", flush=True)
    
    async def test_api():
        print("    → Creating session...", flush=True)
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {"role": "system", "content": "Be precise and concise."},
                {"role": "user", "content": "What is 2+2? Answer in one sentence."}
            ],
            "max_tokens": 100
        }
        
        print("    → Sending request...", flush=True)
        print(f"       URL: {url}", flush=True)
        print(f"       Model: {payload['model']}", flush=True)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    print(f"    → Status: {resp.status}", flush=True)
                    
                    if resp.status == 200:
                        result = await resp.json()
                        content = result["choices"][0]["message"]["content"]
                        tokens = result["usage"]["total_tokens"]
                        
                        print("\n    ✅ SUCCESS!", flush=True)
                        print(f"    Response: {content}", flush=True)
                        print(f"    Tokens: {tokens}", flush=True)
                        return True
                    else:
                        text = await resp.text()
                        print(f"\n    ❌ FAILED", flush=True)
                        print(f"    Error: {text[:200]}", flush=True)
                        return False
                        
        except asyncio.TimeoutError:
            print("    ❌ Request timed out", flush=True)
            return False
        except Exception as e:
            print(f"    ❌ Exception: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False
    
    # Test 4: Run the async function
    print("\n[4] Running async test...", flush=True)
    
    # Try different event loop methods
    try:
        if sys.platform == 'win32':
            # Windows-specific event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            print("    ℹ️  Using Windows event loop policy", flush=True)
        
        success = asyncio.run(test_api())
        
        if success:
            print("\n" + "="*60, flush=True)
            print("✅ TEST PASSED!", flush=True)
            print("="*60, flush=True)
        else:
            print("\n" + "="*60, flush=True)
            print("❌ TEST FAILED - Check errors above", flush=True)
            print("="*60, flush=True)
            
    except Exception as e:
        print(f"\n❌ Event loop error: {e}", flush=True)
        import traceback
        traceback.print_exc()

except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user", flush=True)
except Exception as e:
    print(f"\n❌ Fatal error: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("\n[DONE]", flush=True)