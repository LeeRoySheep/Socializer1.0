# Socializer 1.0 - Installation Guide

Complete installation instructions for all platforms.

## 📋 Prerequisites

### All Platforms
- **Python 3.11+** (3.13 recommended)
- **Git** (for cloning the repository)
- **4GB RAM** minimum
- **500MB disk space**

### API Keys Required
- `OPENAI_API_KEY` - For GPT models (required)
- `TAVILY_API_KEY` - For web search (required)
- `ANTHROPIC_API_KEY` - For Claude (optional)
- `GEMINI_API_KEY` - For Google Gemini (optional)

---

## 🍎 macOS Installation

### Quick Setup
```bash
# Download and extract, then:
cd Socializer1.0
chmod +x setup_socializer1.0.sh
./setup_socializer1.0.sh
```

### Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 4. Initialize database
python init_database_proper.py

# 5. Start server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🐧 Linux Installation

### Quick Setup
```bash
# Download and extract, then:
cd Socializer1.0
chmod +x setup_linux.sh
./setup_linux.sh
```

### Install Python (if needed)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

### Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 4. Initialize database
python init_database_proper.py

# 5. Start server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🪟 Windows Installation

### Quick Setup
```batch
REM Download and extract, then:
cd Socializer1.0
setup_windows.bat
```

### Install Python (if needed)
1. Download Python from https://www.python.org/downloads/
2. Run installer
3. ⚠️ **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"

### Manual Setup
```batch
REM 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate.bat

REM 2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 3. Configure environment
copy .env.example .env
notepad .env  REM Add your API keys

REM 4. Initialize database
python init_database_proper.py

REM 5. Start server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🔑 API Keys Setup

### 1. Edit .env file

**macOS/Linux:**
```bash
nano .env
```

**Windows:**
```batch
notepad .env
```

### 2. Add Your Keys

```env
# Required
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here

# Optional
ANTHROPIC_API_KEY=sk-ant-your-claude-key-here
GEMINI_API_KEY=your-gemini-key-here

# Security (auto-generated if not set)
SECRET_KEY=your-secret-key-for-jwt-tokens
```

### 3. Where to Get Keys

| Service | URL | Free Tier |
|---------|-----|-----------|
| OpenAI | https://platform.openai.com/api-keys | $5 credit |
| Tavily | https://tavily.com/ | 1000 searches/month |
| Anthropic | https://console.anthropic.com/ | Limited |
| Gemini | https://makersuite.google.com/app/apikey | Free |

---

## ✅ Verification

Run the verification script to check your setup:

```bash
# macOS/Linux
source .venv/bin/activate
python verify_setup.py

# Windows
.venv\Scripts\activate.bat
python verify_setup.py
```

**Expected Output:**
```
============================================================
🔍 Socializer 1.0 - Setup Verification
============================================================

1️⃣  Python Version Check...
   ✅ Python 3.13

2️⃣  File Structure Check...
   ✅ app/main.py
   ✅ ai_chatagent.py
   ✅ requirements.txt
   [...]

3️⃣  Module Import Check...
   ✅ FastAPI
   ✅ SQLAlchemy
   [...]

4️⃣  Environment Variables Check...
   ✅ .env file exists
   ✅ SECRET_KEY is set
   ✅ OPENAI_API_KEY is set
   ✅ TAVILY_API_KEY is set

5️⃣  Database Check...
   ✅ data.sqlite.db exists

============================================================
✅ SETUP LOOKS GOOD!
============================================================
```

---

## 🚀 Starting the Server

### Development Mode (with auto-reload)

**macOS/Linux:**
```bash
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Windows:**
```batch
.venv\Scripts\activate.bat
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Production Mode

**macOS/Linux:**
```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Windows:**
```batch
.venv\Scripts\activate.bat
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🌐 Access the Application

Once the server is running, open your browser:

- **Main App:** http://localhost:8000
- **Login:** http://localhost:8000/login
- **Register:** http://localhost:8000/register
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🏠 Local LLM Setup (Optional)

### LM Studio

1. Download from https://lmstudio.ai/
2. Install and open LM Studio
3. Download a model (e.g., Llama 3.2)
4. Click "Start Server" (default: http://localhost:1234)
5. In Socializer settings, enable "Use Local LLM"

### Ollama

1. Download from https://ollama.ai/
2. Install Ollama
3. Pull a model: `ollama pull llama3.2`
4. Server auto-starts on http://localhost:11434
5. In Socializer settings, enable "Use Local LLM"

---

## 🔧 Troubleshooting

### "Command not found: python"
- **macOS/Linux:** Use `python3` instead of `python`
- **Windows:** Python not in PATH, reinstall with "Add to PATH" checked

### "Port 8000 already in use"
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "No module named 'app'"
Make sure you're in the Socializer1.0 directory and virtual environment is activated.

### Database Errors
```bash
# Reset database
rm data.sqlite.db  # or del data.sqlite.db on Windows
python init_database_proper.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Next Steps

After successful installation:

1. **Create an account** at http://localhost:8000/register
2. **Login** at http://localhost:8000/login
3. **Try AI chat** with `/ai hello`
4. **Test tools** with `/ai what's the weather?`
5. **Configure Local LLM** in settings (optional)

---

## 📞 Support

- **Issues:** Check `FIXES_APPLIED.md` for known fixes
- **Documentation:** See `README_STABLE.md`
- **Version Info:** See `VERSION_INFO.md`

---

**Enjoy using Socializer 1.0!** 🎉
