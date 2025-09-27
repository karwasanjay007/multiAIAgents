
# ============================================================================
# FILE: setup_test.py (Alternative - Run this first)
# Save this in: multi-agent-researcher/setup_test.py
# ============================================================================
"""
Setup script to verify project structure before testing
Run: python setup_test.py
"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """Check if all required files exist"""
    
    print("🔍 Checking project structure...\n")
    
    required_files = [
        "agents/perplexity_agent.py",
        "agents/base_agent.py",
        "services/perplexity_client.py",
        "config/settings.py",
        ".env",
        "requirements.txt"
    ]
    
    required_dirs = [
        "agents",
        "services", 
        "config",
        "workflows",
        "utils"
    ]
    
    project_root = Path.cwd()
    print(f"Project root: {project_root}\n")
    
    # Check directories
    print("📁 Checking directories:")
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ - MISSING")
    
    print("\n📄 Checking files:")
    # Check files
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
    
    # Check .env specifically
    env_path = project_root / ".env"
    print(f"\n🔑 Environment Configuration:")
    if env_path.exists():
        print(f"   ✅ .env file exists")
        
        # Check for API key
        with open(env_path, 'r') as f:
            content = f.read()
            if "PERPLEXITY_API_KEY" in content:
                # Check if it has a value
                for line in content.split('\n'):
                    if line.startswith("PERPLEXITY_API_KEY="):
                        value = line.split('=', 1)[1].strip()
                        if value and value != "your_perplexity_api_key_here":
                            print(f"   ✅ PERPLEXITY_API_KEY is set")
                        else:
                            print(f"   ⚠️  PERPLEXITY_API_KEY is empty - add your key")
            else:
                print(f"   ⚠️  PERPLEXITY_API_KEY not found in .env")
    else:
        print(f"   ❌ .env file not found")
        print(f"   💡 Copy .env.example to .env and add your API key")
    
    # Check Python path
    print(f"\n🐍 Python Configuration:")
    print(f"   Python version: {sys.version.split()[0]}")
    print(f"   Python path: {sys.executable}")
    print(f"   Current directory: {os.getcwd()}")
    
    # Check installed packages
    print(f"\n📦 Checking required packages:")
    required_packages = ["aiohttp", "streamlit", "python-dotenv"]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Run: pip install {package}")
    
    print("\n" + "="*60)
    print("Setup check complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Fix any missing files/directories")
    print("2. Add PERPLEXITY_API_KEY to .env")
    print("3. Run: python test_perplexity.py")

if __name__ == "__main__":
    check_project_structure()


