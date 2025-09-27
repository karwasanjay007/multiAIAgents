# ============================================================================
# FILE: README_TESTING.md
# ============================================================================
"""
# Testing Perplexity Integration

## Quick Fix for Module Not Found Error

### Option 1: Run from Project Root (RECOMMENDED)

```bash
# Navigate to project root
cd C:\Projects\2025\AI\Projects\ai-accelerator\multi-agent-researcher

# Run test
python test_perplexity.py
```

### Option 2: Fix Python Path in Test Script

The test script at the top already fixes this - make sure you're using the updated version.

### Option 3: Setup PYTHONPATH

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH = "C:\Projects\2025\AI\Projects\ai-accelerator\multi-agent-researcher"
python test_perplexity.py
```

**Windows (CMD):**
```cmd
set PYTHONPATH=C:\Projects\2025\AI\Projects\ai-accelerator\multi-agent-researcher
python test_perplexity.py
```

## Step-by-Step Testing

1. **Check Project Structure:**
```bash
python setup_test.py
```

2. **Add API Key to .env:**
```
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
```

3. **Install Dependencies:**
```bash
pip install aiohttp python-dotenv
```

4. **Run Test:**
```bash
python test_perplexity.py
```

## Expected Output

```
🔬 Perplexity Integration Test
============================================================
✅ API Key found: pplx-abc...xyz
✅ Perplexity Agent initialized successfully

============================================================
Test Case 1: TECHNOLOGY
Query: What are the latest AI trends in 2025?
============================================================

⏳ Searching... (this may take 10-30 seconds)

✅ Success!

📊 Executive Summary:
   The latest AI trends in 2025 include...

🔍 Key Findings:
   1. Finding one...
   2. Finding two...
   3. Finding three...

💰 Cost: $0.0015
📚 Sources: 5

📄 Full result saved to: test_result_1_technology.json

============================================================
✅ All tests completed!
============================================================
```

## Troubleshooting

### Error: No module named 'agents'
- Make sure you're in the project root directory
- Use the fixed test script provided above
- Run `setup_test.py` first to check structure

### Error: PERPLEXITY_API_KEY not found
- Create `.env` file in project root
- Add: `PERPLEXITY_API_KEY=your_key_here`
- Get key from: https://www.perplexity.ai/settings/api

### Error: aiohttp not installed
```bash
pip install aiohttp python-dotenv
```

### Error: API request failed
- Check API key is correct
- Verify internet connection
- Check Perplexity API status
"""