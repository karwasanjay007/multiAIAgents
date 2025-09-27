# ============================================================================
# FILE 5: run_streamlit.py (WRAPPER SCRIPT)
# Use this to run Streamlit with environment loaded
# ============================================================================
"""
Wrapper script to run Streamlit with environment variables loaded
Run: python run_streamlit.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import subprocess

# Load environment
env_file = Path(__file__).parent / '.env'
load_dotenv(env_file)

# Verify API key
api_key = os.getenv("PERPLEXITY_API_KEY")
if api_key:
    print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:]}")
else:
    print("❌ WARNING: PERPLEXITY_API_KEY not found in .env!")
    sys.exit(1)

# Run Streamlit with environment inherited
print("\n🚀 Starting Streamlit with environment loaded...\n")
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])