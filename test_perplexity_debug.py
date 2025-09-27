# ============================================================================
# FILE: test_perplexity_debug.py
# ============================================================================
"""
Debug version with verbose output at each step
"""

import asyncio
import os
import sys
from pathlib import Path

print("=" * 60)
print("PERPLEXITY DEBUG TEST")
print("=" * 60)

# Step 1: Check Python path
print("\n[1] Python Configuration:")
print(f"    Python: {sys.version}")
print(f"    Path: {sys.executable}")
print(f"    CWD: {os.getcwd()}")

# Step 2: Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
print(f"    Project root: {project_root}")

# Step 3: Load .env
print("\n[2] Loading environment...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("    ✅ dotenv loaded")
except ImportError:
    print("    ❌ python-dotenv not installed")
    print("    Run: pip install python-dotenv")
    sys.exit(1)

# Step 4: Check API key
print("\n[3] Checking API key...")
api_key = os.getenv("PERPLEXITY_API_KEY")
if not api_key:
    print("    ❌ PERPLEXITY_API_KEY not found")
    print("\n    Fix:")
    print("    1. Create .env file in project root")
    print("    2. Add: PERPLEXITY_API_KEY=pplx-your-key-here")
    sys.exit(1)
else:
    print(f"    ✅ Key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"    Length: {len(api_key)}")

# Step 5: Check dependencies
print("\n[4] Checking dependencies...")
try:
    import aiohttp
    print(f"    ✅ aiohttp {aiohttp.__version__}")
except ImportError:
    print("    ❌ aiohttp not installed")
    print("    Run: pip install aiohttp")
    sys.exit(1)

# Step 6: Import agent
print("\n[5] Importing agent...")
try:
    from agents.perplexity_agent import PerplexityAgent
    print("    ✅ PerplexityAgent imported")
except Exception as e:
    print(f"    ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 7: Initialize agent
print("\n[6] Initializing agent...")
try:
    agent = PerplexityAgent(api_key)
    print("    ✅ Agent initialized")
except Exception as e:
    print(f"    ❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 8: Test API call
print("\n[7] Testing API call...")
print("    Query: 'What is 2+2?'")
print("    (This may take 10-30 seconds...)")

async def test_api():
    try:
        result = await agent.execute(
            query="What is 2+2?",
            domain="technology",
            max_tokens=500
        )
        
        print("\n[8] API Response:")
        print(f"    Success: {result.get('success')}")
        
        if result.get('success'):
            print(f"    ✅ API call successful!")
            print(f"    Tokens: {result.get('tokens_used', 0)}")
            print(f"    Cost: ${result.get('estimated_cost', 0):.4f}")
            print(f"\n    Response preview:")
            print(f"    {result.get('executive_summary', 'N/A')[:200]}")
        else:
            print(f"    ❌ API call failed")
            print(f"    Error: {result.get('error', 'Unknown')}")
            
        return result
        
    except Exception as e:
        print(f"\n    ❌ Exception during API call:")
        print(f"    {e}")
        import traceback
        traceback.print_exc()
        return None

print("\n[*] Starting async execution...")
try:
    result = asyncio.run(test_api())
    
    if result and result.get('success'):
        print("\n" + "=" * 60)
        print("✅ TEST PASSED - Perplexity integration working!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED - Check errors above")
        print("=" * 60)
        
except KeyboardInterrupt:
    print("\n\n⚠️  Test interrupted by user (Ctrl+C)")
except Exception as e:
    print(f"\n❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()

print("\n[DONE]")