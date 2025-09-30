#!/usr/bin/env python3
"""
Auto-fix all 'src.' imports to remove the 'src' prefix
Run: python fix_imports.py
"""

import os
from pathlib import Path

def fix_file_imports(filepath):
    """Fix imports in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all src. imports
        replacements = [
            ('from src.graph.state', 'from graph.state'),
            ('from src.tools.', 'from tools.'),
            ('from src.utils.', 'from utils.'),
            ('from src.agent.', 'from agents.'),
            ('from src.graph.', 'from graph.'),
            ('from src.services.', 'from services.'),
            ('import src.', 'import '),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Fix all Python files in the project"""
    
    print("="*60)
    print("FIXING 'src' IMPORTS IN ALL PYTHON FILES")
    print("="*60)
    
    # Directories to search
    dirs_to_search = ['agents', 'tools', 'utils', 'graph', 'workflows', 'services']
    
    fixed_count = 0
    total_count = 0
    
    for dir_name in dirs_to_search:
        dir_path = Path(dir_name)
        
        if not dir_path.exists():
            continue
        
        print(f"\n📁 Processing {dir_name}/")
        
        # Find all .py files
        for py_file in dir_path.rglob('*.py'):
            total_count += 1
            print(f"  Checking: {py_file}")
            
            if fix_file_imports(py_file):
                print(f"    ✅ Fixed imports")
                fixed_count += 1
            else:
                print(f"    ⏭️  No changes needed")
    
    print("\n" + "="*60)
    print(f"✅ COMPLETE: Fixed {fixed_count}/{total_count} files")
    print("="*60)
    print("\n🚀 Now run: python run_streamlit.py")

if __name__ == "__main__":
    main()