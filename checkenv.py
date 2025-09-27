# ============================================================================
# FILE 4: check_env.py (DEBUG SCRIPT)
# Run this to verify environment loading
# ============================================================================
"""
Debug script to check environment variables
Run: python check_env.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("="*60)
print("ENVIRONMENT VARIABLE DEBUG")
print("="*60)

# Check current directory
print(f"\n1. Current Directory: {os.getcwd()}")
print(f"   Script Location: {Path(__file__).parent}")

# Check .env file
env_file = Path(__file__).parent / '.env'
print(f"\n2. .env File:")
print(f"   Path: {env_file}")
print(f"   Exists: {env_file.exists()}")

if env_file.exists():
    print(f"   Size: {env_file.stat().st_size} bytes")
    
    # Read content
    with open(env_file, 'r') as f:
        content = f.read()
    
    print(f"\n3. .env Content:")
    for line in content.split('\n'):
        if line.strip() and not line.startswith('#'):
            key = line.split('=')[0]
            value = line.split('=')[1] if '=' in line else ''
            if 'KEY' in key or 'SECRET' in key or 'TOKEN' in key:
                # Mask sensitive values
                masked = value[:10] + "..." + value[-4:] if len(value) > 14 else "****"
                print(f"   {key}={masked}")
            else:
                print(f"   {line}")

# Load with dotenv
print(f"\n4. Loading with python-dotenv:")
loaded = load_dotenv(env_file, verbose=True)
print(f"   Load successful: {loaded}")

# Check if loaded
print(f"\n5. Environment Variables:")
perplexity_key = os.getenv("PERPLEXITY_API_KEY")
if perplexity_key:
    print(f"   ✅ PERPLEXITY_API_KEY: {perplexity_key[:10]}...{perplexity_key[-4:]}")
else:
    print(f"   ❌ PERPLEXITY_API_KEY: Not found")

# Check all env vars
print(f"\n6. All Environment Variables with 'KEY' or 'API':")
for key, value in os.environ.items():
    if 'KEY' in key or 'API' in key:
        masked = value[:10] + "..." + value[-4:] if len(value) > 14 else "****"
        print(f"   {key}: {masked}")

print("\n" + "="*60)
print("DEBUG COMPLETE")
print("="*60)