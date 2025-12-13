# 🚀 Socializer 1.0 - Quick Start

Get up and running in 5 minutes!

## 📦 Download & Extract

```bash
# Clone or download the repository
git clone <your-repo-url> Socializer1.0
cd Socializer1.0
```

## ⚡ One-Command Setup

### macOS
```bash
chmod +x setup_socializer1.0.sh && ./setup_socializer1.0.sh
```

### Linux
```bash
chmod +x setup_linux.sh && ./setup_linux.sh
```

### Windows
```batch
setup_windows.bat
```

## 🔑 Add API Keys

Edit `.env` file and add your keys:

```bash
# macOS/Linux
nano .env

# Windows
notepad .env
```

**Minimum required:**
```env
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

**Get free keys:**
- OpenAI: https://platform.openai.com/api-keys ($5 free credit)
- Tavily: https://tavily.com/ (1000 searches/month free)

## 🏃 Run

```bash
# macOS/Linux
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Windows
.venv\Scripts\activate.bat
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 🌐 Access

Open browser: **http://localhost:8000**

1. **Register** a new account
2. **Login** with your credentials
3. **Chat** with AI: Type `/ai hello`
4. **Test tools**: Try `/ai what's the weather?`

## 🎯 That's It!

You're ready to use Socializer 1.0!

### Next Steps:
- See **INSTALL.md** for detailed installation options
- Check **README_STABLE.md** for features and documentation
- Review **FIXES_APPLIED.md** for recent improvements

### Optional: Local LLM
- Install **LM Studio** or **Ollama**
- Enable in settings for free, private AI

---

**Having issues?** Check troubleshooting in INSTALL.md
