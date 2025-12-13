# Socializer 1.0 - Stable Local Version

## 📦 What is this?

This is the **stable, local-only version** of Socializer from commit `2678b5d` (Dec 11, 2025).

This version contains all features **before** the Render.com deployment changes were made.

## ✅ What works:
- ✅ Local LLM integration (LM Studio, Ollama)
- ✅ Multi-AI provider support (OpenAI, Claude, Gemini)
- ✅ Social skills training system
- ✅ Encrypted memory system
- ✅ WebSocket real-time chat
- ✅ Private rooms with passwords
- ✅ Tool calling (search, skills, memory)
- ✅ All features tested and working locally

## 🚀 Quick Start

### 1. Set up environment
```bash
cd /Users/leeroystevenson/PycharmProjects/Socializer1.0

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure .env
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
# Edit .env with your keys
```

### 3. Initialize database
```bash
python init_chat_tables.py
```

### 4. Run the app
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Visit: http://localhost:8000

## 🔑 Required API Keys
Add these to your `.env`:
- `OPENAI_API_KEY` - For GPT models
- `ANTHROPIC_API_KEY` - For Claude
- `GEMINI_API_KEY` - For Google Gemini
- `TAVILY_API_KEY` - For web search

## 🏠 Local LLM Setup
For LM Studio:
1. Install LM Studio
2. Load a model
3. Start server on `http://localhost:1234`
4. Enable in Socializer settings

## 📝 Key Differences from Main Branch
- ❌ No Render.com deployment code
- ❌ No PostgreSQL support
- ❌ No BrowserAgent (uses backend only)
- ✅ SQLite database (simpler)
- ✅ All features work locally
- ✅ Stable and tested

## 🔧 Troubleshooting

### Database Issues
```bash
# Reset database
rm data.sqlite.db
python init_chat_tables.py
```

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Documentation
- See `docs/` folder for detailed documentation
- `OTE_PRINCIPLES.md` - Architecture principles
- `PROJECT_FILE_DOCUMENTATION.md` - File structure

## 🆚 Main Branch vs Socializer1.0

| Feature | Main Branch | Socializer1.0 |
|---------|-------------|---------------|
| Render.com Deploy | ✅ | ❌ |
| PostgreSQL | ✅ | ❌ |
| SQLite | ✅ | ✅ |
| Local LLM | ✅ | ✅ |
| BrowserAgent | ✅ | ❌ |
| All Tools | ⚠️ (fixing) | ✅ |
| Stability | ⚠️ (testing) | ✅ |

## 🎯 Use This Version If:
- ✅ Running locally only
- ✅ Want stable, tested features
- ✅ Don't need cloud deployment
- ✅ Prefer SQLite over PostgreSQL

## 🔄 Switch to Main Branch
If you want the latest features (with Render.com support):
```bash
cd /Users/leeroystevenson/PycharmProjects/Socializer
git checkout main
```

---

**Created:** Dec 12, 2025  
**Base Commit:** 2678b5d  
**Status:** Stable ✅
