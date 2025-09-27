# ============================================================================
# FILE: check_event_loop.py
# Check if asyncio works at all
# ============================================================================
import asyncio
import sys

print("Testing asyncio event loop...")
print(f"Platform: {sys.platform}")
print(f"Python: {sys.version}")

async def simple_test():
    print("Inside async function")
    await asyncio.sleep(0.1)
    return "Success"

try:
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print("Using WindowsSelectorEventLoopPolicy")
    
    result = asyncio.run(simple_test())
    print(f"Result: {result}")
    print("✅ Asyncio works!")
    
except Exception as e:
    print(f"❌ Asyncio failed: {e}")
    import traceback
    traceback.print_exc()