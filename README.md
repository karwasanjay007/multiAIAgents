# 🔬 Multi-Agent AI Deep Researcher

> **Advanced AI-powered research assistant using specialized agents to conduct comprehensive, multi-source investigations**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [How to Use](#how-to-use)
- [Project Structure](#project-structure)
- [Agent Details](#agent-details)
- [Cost Tracking](#cost-tracking)
- [API Integration](#api-integration)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

The **Multi-Agent AI Deep Researcher** is an intelligent research assistant that orchestrates multiple specialized AI agents to conduct deep, comprehensive investigations across various domains. The system retrieves information from diverse sources, critically analyzes findings, generates insights, and compiles structured research reports.

### Key Capabilities

- **🌐 Web Research**: Deep web search using Perplexity AI with domain-specific prompts
- **📹 Video Analysis**: YouTube sentiment analysis (Coming Soon)
- **📚 API Agent**: Academic papers and news aggregation (Coming Soon)
- **💰 Cost Tracking**: Real-time token usage and cost estimation
- **📊 Structured Reports**: Executive summaries, key findings, insights, and citations
- **🎨 Interactive UI**: Clean Streamlit interface with live updates

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Domain    │  │    Query     │  │ Agent Select  │  │
│  │  Selection  │  │    Input     │  │   Display     │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└────────────────────────────┬────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│        Research Workflow (LangGraph Orchestrator)       │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Perplexity  │  │   YouTube    │  │  API Agent   │  │
│  │    Agent     │  │    Agent     │  │   (RAG)      │  │
│  │  (Active)    │  │ (Coming Soon)│  │(Coming Soon) │  │
│  └──────┬───────┘  └──────────────┘  └──────────────┘  │
│         │                                                │
│         └──────────────┬─────────────────────────────┐  │
│                        ↓                             │  │
│              ┌──────────────────┐                    │  │
│              │  Consolidation   │                    │  │
│              │     Agent        │                    │  │
│              └──────────────────┘                    │  │
└────────────────────────────┬────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│                  External APIs                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Perplexity  │  │   YouTube    │  │   News API   │  │
│  │     API      │  │     API      │  │   / arXiv    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → User selects domain, enters query, selects agents
2. **Workflow Orchestration** → LangGraph coordinates agent execution
3. **Agent Execution** → Each agent performs specialized research
4. **Result Consolidation** → Findings are merged and structured
5. **UI Display** → Results rendered with citations, costs, and export options

### Agent Communication

```python
# Async workflow execution
async def execute(query: str, domain: str, agents: List[str]):
    - Initialize agents based on selection
    - Execute agents in parallel (where possible)
    - Collect and format results
    - Calculate costs and metrics
    - Return structured JSON response
```

---

## ✨ Features

### Current Features

- ✅ **Domain-Specific Research**
  - 📈 Stock Market Analysis
  - 🏥 Medical Research
  - 📚 Academic Research
  - 💻 Technology Trends

- ✅ **Perplexity Deep Search**
  - Real-time web search with citations
  - Domain-specific system prompts
  - Structured response parsing
  - Token usage tracking

- ✅ **Cost Management**
  - Real-time cost estimation
  - Token usage breakdown
  - Session-level tracking
  - Budget alerts

- ✅ **Results Display**
  - Executive summary
  - Key findings (3-5 bullet points)
  - Detailed analysis
  - Insights and patterns
  - Source citations

- ✅ **Export Options**
  - PDF export
  - Markdown export
  - JSON export
  - Research history

### Coming Soon

- 🔄 YouTube Video Analysis Agent
- 🔄 Academic Paper Retrieval (arXiv, PubMed)
- 🔄 News API Integration
- 🔄 Advanced caching mechanisms
- 🔄 Multi-language support

---

## 🛠️ Technologies Used

### Core Framework
- **Python 3.13+** - Main programming language
- **Streamlit 1.29.0** - Web UI framework
- **LangChain/LangGraph** - Agent orchestration
- **asyncio** - Asynchronous execution

### AI & APIs
- **Perplexity API** - Deep web search (sonar-pro model)
- **OpenRouter** - Multi-model AI routing (planned)
- **YouTube Data API v3** - Video analysis (planned)

### Data Processing
- **aiohttp 3.12.15** - Async HTTP client
- **python-dotenv 1.0.0** - Environment management
- **pandas 2.1.4** - Data manipulation

### Storage & Export
- **ReportLab 4.0.4** - PDF generation
- **python-docx** - Word document export

### Development Tools
- **pytest 7.4.3** - Testing framework
- **black** - Code formatting (optional)

---

## 📦 Prerequisites

- **Python 3.13 or higher**
- **pip** package manager
- **Git** (for cloning)
- **Perplexity API Key** ([Get one here](https://www.perplexity.ai/settings/api))

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/multi-agent-researcher.git
cd multi-agent-researcher
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
pip install aiohttp langchain-community youtube-transcript-api arxiv
```

**requirements.txt includes:**
```
streamlit==1.29.0
langchain==0.1.0
langgraph==0.0.20
openai==1.6.1
aiohttp==3.12.15
python-dotenv==1.0.0
pandas==2.1.4
pytest==7.4.3
reportlab==4.0.4
```

---

## ⚙️ Configuration

### Step 1: Create Environment File

Copy the example environment file:
```bash
cp .env.example .env
```

### Step 2: Add API Keys

Edit `.env` and add your API keys:

```bash
# Perplexity API (Required)
PERPLEXITY_API_KEY=pplx-your-api-key-here

# OpenRouter (Optional - for future use)
OPENROUTER_API_KEY=your-openrouter-key

# YouTube API (Optional - for video analysis)
YOUTUBE_API_KEY=your-youtube-key

# News API (Optional - for news aggregation)
NEWS_API_KEY=your-news-api-key
```

### Step 3: Verify Configuration

Run the environment checker:
```bash
python check_env.py
```

Expected output:
```
============================================================
ENVIRONMENT VARIABLE DEBUG
============================================================
✅ API Key: pplx-PtOPA...29qA
✅ .env file exists
✅ All dependencies installed
```

---

## 🏃 Running the Application

### Method 1: Using the Wrapper Script (Recommended)

```bash
python run_streamlit.py
```

This ensures environment variables are loaded correctly.

### Method 2: Direct Streamlit

```bash
streamlit run app.py
```

### Method 3: With Environment Variables

**Windows PowerShell:**
```powershell
$env:PERPLEXITY_API_KEY = "your-key-here"
streamlit run app.py
```

**Mac/Linux:**
```bash
export PERPLEXITY_API_KEY="your-key-here"
streamlit run app.py
```

### Accessing the Application

Once started, open your browser to:
```
http://localhost:8501
```

---

## 📖 How to Use

### 1. **Select Research Domain**

Choose from:
- 📈 **Stock Market Analysis** - Financial data, trends, analyst opinions
- 🏥 **Medical Research** - Clinical trials, studies, treatments
- 📚 **Academic Research** - Scholarly articles, papers, citations
- 💻 **Technology Trends** - Tech news, innovations, products

### 2. **Enter Research Question**

Type your question in the text area:
```
Example: "What are the latest AI trends in 2025?"
```

### 3. **Select Research Sources**

Choose which agents to use:
- ✅ **🌐 Web Research** - Perplexity deep search (Active)
- 🔄 **📹 Video Analysis** - YouTube sentiment (Coming Soon)
- 🔄 **📚 API Agent** - Academic papers (Coming Soon)

### 4. **Start Research**

Click **🚀 Start Research** button

The system will:
1. Initialize selected agents
2. Execute research (10-30 seconds)
3. Process and consolidate results
4. Display findings with citations

### 5. **View Results**

Results include:
- **📊 Executive Summary** - 2-3 sentence overview
- **🔍 Key Findings** - Main discoveries (bullet points)
- **💡 Insights** - Patterns and trends
- **🔗 Sources** - Cited references with URLs
- **📈 Metrics** - Tokens used, cost, execution time

### 6. **Export Results**

Choose export format:
- **📄 Export PDF** - Formatted report
- **📝 Export Markdown** - Plain text format
- **📋 Export JSON** - Raw data

---

## 📁 Project Structure

```
multi-agent-researcher/
│
├── 📄 app.py                          # Main Streamlit application
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env.example                    # Example environment file
├── 📄 .env                            # Your API keys (gitignored)
├── 📄 README.md                       # This file
│
├── 📂 agents/                         # AI Agent implementations
│   ├── __init__.py
│   ├── base_agent.py                 # Base agent class
│   ├── perplexity_agent.py          # Perplexity search agent
│   ├── youtube_agent.py             # YouTube analysis agent (planned)
│   └── api_agent.py                 # API retrieval agent (planned)
│
├── 📂 services/                       # External service clients
│   ├── __init__.py
│   ├── perplexity_client.py         # Perplexity API client
│   ├── youtube_client.py            # YouTube API client (planned)
│   ├── news_api_client.py           # News API client (planned)
│   └── arxiv_client.py              # arXiv API client (planned)
│
├── 📂 workflows/                      # Orchestration logic
│   ├── __init__.py
│   ├── langgraph_workflow.py        # Main workflow coordinator
│   ├── agent_coordinator.py         # Agent coordination (planned)
│   └── consolidation.py             # Result consolidation (planned)
│
├── 📂 ui/                             # UI components
│   ├── __init__.py
│   ├── components/
│   │   ├── sidebar.py               # Settings sidebar
│   │   ├── agent_display.py         # Agent selection UI
│   │   ├── agent_cards.py           # Agent status cards
│   │   ├── cost_tracker.py          # Cost tracking display
│   │   ├── results_display.py       # Results rendering
│   │   └── export_buttons.py        # Export functionality
│   ├── pages/
│   │   ├── 1_Research.py            # Research page
│   │   ├── 2_History.py             # History page
│   │   └── 3_Settings.py            # Settings page
│   └── styles/
│       └── themes.py                # Custom CSS themes
│
├── 📂 config/                         # Configuration
│   ├── __init__.py
│   ├── settings.py                  # App settings
│   └── constants.py                 # Constants (domains, costs)
│
├── 📂 prompts/                        # Domain-specific prompts
│   ├── __init__.py
│   ├── base_prompts.py              # Base prompt templates
│   ├── stock_analysis.py            # Stock market prompts
│   ├── medical_research.py          # Medical research prompts
│   ├── academic_research.py         # Academic prompts
│   └── technology_trends.py         # Tech trend prompts
│
├── 📂 utils/                          # Utility functions
│   ├── __init__.py
│   ├── export.py                    # Export utilities (PDF, MD)
│   ├── parsers.py                   # Response parsers
│   ├── validators.py                # Input validators
│   └── logger.py                    # Logging configuration
│
├── 📂 data/                           # Data storage
│   ├── cache/                       # Cached responses
│   ├── exports/                     # Exported reports
│   └── history/                     # Research history
│
├── 📂 tests/                          # Test suite
│   ├── test_agents/
│   ├── test_services/
│   └── test_workflows/
│
├── 📂 scripts/                        # Utility scripts
│   ├── check_env.py                 # Environment checker
│   ├── run_streamlit.py             # Streamlit wrapper
│   ├── test_perplexity.py          # Perplexity test
│   └── fix_model_name.py           # Quick fix script
│
└── 📂 .streamlit/                     # Streamlit config
    └── config.toml                   # Streamlit settings
```

---

## 🤖 Agent Details

### 1. **Perplexity Agent** (Active)

**Purpose**: Deep web research using Perplexity AI

**Model**: `sonar-pro`

**Features**:
- Domain-specific system prompts
- Real-time web search with citations
- Structured response parsing
- Token usage tracking

**Cost**: ~$1 per 1M tokens

**Response Structure**:
```json
{
  "success": true,
  "executive_summary": "2-3 sentence overview",
  "key_findings": ["finding 1", "finding 2", ...],
  "detailed_analysis": "Full analysis text",
  "insights": ["insight 1", "insight 2"],
  "sources": [...],
  "tokens_used": 1543,
  "estimated_cost": 0.001543
}
```

### 2. **YouTube Agent** (Coming Soon)

**Purpose**: Video content and sentiment analysis

**Features**:
- Video search by keywords
- Transcript extraction
- Sentiment analysis
- Public opinion insights

### 3. **API Agent** (Coming Soon)

**Purpose**: Academic and news data retrieval

**Data Sources**:
- arXiv (research papers)
- PubMed (medical literature)
- News API (current news)
- Semantic Scholar (citations)

---

## 💰 Cost Tracking

### Real-Time Cost Display

The UI shows:
- **Active Agents**: Number of agents running
- **Estimated Cost**: Cost per query
- **Processing Time**: Estimated completion time
- **Session Total**: Cumulative session cost

### Cost Breakdown by Agent

| Agent | Avg Cost/Query | Processing Time |
|-------|----------------|-----------------|
| Perplexity | $0.001 | ~5 min |
| YouTube | $0.15 | ~2 min |
| API Agent | $0.35 | ~3 min |

### Token Usage

- **Input Tokens**: System prompt + user query
- **Output Tokens**: Generated response
- **Total Tokens**: Sum of input + output
- **Cost Calculation**: (tokens / 1M) × model_price

### Budget Management

Set limits in **Settings**:
- Max cost per query
- Daily budget
- Alert thresholds

---

## 🔌 API Integration

### Perplexity API

**Endpoint**: `https://api.perplexity.ai/chat/completions`

**Authentication**:
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

**Request Format**:
```json
{
  "model": "sonar-pro",
  "messages": [
    {"role": "system", "content": "system_prompt"},
    {"role": "user", "content": "user_query"}
  ],
  "max_tokens": 2000,
  "temperature": 0.2,
  "return_citations": true
}
```

**Response Format**:
```json
{
  "choices": [{
    "message": {
      "content": "AI response text"
    }
  }],
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 123,
    "total_tokens": 168
  },
  "citations": ["url1", "url2", ...]
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **API Key Not Found**

**Error**: `PERPLEXITY_API_KEY not found in environment`

**Solution**:
```bash
# Verify .env file exists
ls -la .env

# Check API key is set
python check_env.py

# Use wrapper script
python run_streamlit.py
```

#### 2. **Module Not Found**

**Error**: `ModuleNotFoundError: No module named 'agents'`

**Solution**:
```bash
# Ensure you're in project root
pwd

# Run from correct directory
cd multi-agent-researcher
python test_perplexity.py
```

#### 3. **Invalid Model Error**

**Error**: `Invalid model 'llama-3.1-sonar-large-128k-online'`

**Solution**:
```bash
# Run fix script
python scripts/fix_model_name.py

# Or manually update services/perplexity_client.py
# Change model to: "sonar-pro"
```

#### 4. **Timeout Error**

**Error**: `Request timed out after 120 seconds`

**Solution**:
- Check internet connection
- Increase timeout in `perplexity_client.py`:
```python
timeout=aiohttp.ClientTimeout(total=180)  # 3 minutes
```

#### 5. **No Output from Test**

**Error**: Script exits with no output

**Solution**:
```bash
# Use debug version
python test_perplexity_debug.py

# Check Python version
python --version  # Should be 3.13+

# Test asyncio
python check_event_loop.py
```

### Debug Mode

Enable verbose logging:
```python
# Add to app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support

For additional help:
1. Check [GitHub Issues](https://github.com/yourusername/multi-agent-researcher/issues)
2. Review [Documentation](https://docs.example.com)
3. Contact: support@example.com

---

## 🚀 Future Enhancements

### Planned Features

- [ ] **YouTube Integration**
  - Video search and analysis
  - Transcript processing
  - Sentiment analysis

- [ ] **Advanced RAG System**
  - Vector database (ChromaDB/Pinecone)
  - Document embedding
  - Semantic search

- [ ] **Multi-Source Integration**
  - arXiv papers
  - PubMed articles
  - News APIs
  - Google Scholar

- [ ] **Enhanced UI**
  - Dark mode
  - Custom themes
  - Mobile responsiveness
  - Real-time streaming

- [ ] **Advanced Features**
  - Caching mechanisms
  - Query history search
  - Batch processing
  - Scheduled research
  - Email reports

- [ ] **Collaboration Tools**
  - Team workspaces
  - Shared research
  - Comments & annotations
  - Version control

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Perplexity AI** - Deep search capabilities
- **Streamlit** - Web application framework
- **LangChain** - Agent orchestration
- **Anthropic** - AI guidance and best practices

---

## 📞 Contact

- **Author**: Your Name
- **Email**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **Project Link**: [https://github.com/yourusername/multi-agent-researcher](https://github.com/yourusername/multi-agent-researcher)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/multi-agent-researcher&type=Date)](https://star-history.com/#yourusername/multi-agent-researcher&Date)

---

**Built with ❤️ using AI and Open Source**