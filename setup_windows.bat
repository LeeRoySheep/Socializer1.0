@echo off
REM ================================================
REM Socializer 1.0 Setup Script - Windows
REM ================================================

echo ==================================================
echo 🚀 Socializer 1.0 - Windows Setup
echo ==================================================

REM Check if we're in the right directory
if not exist "app\main.py" (
    echo ❌ Error: Run this script from Socializer1.0 directory
    pause
    exit /b 1
)

REM Check Python version
echo.
echo 1️⃣  Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH!
    echo    Download from: https://www.python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo    ✅ Python %PYTHON_VERSION% found

REM Create virtual environment
echo.
echo 2️⃣  Creating virtual environment...
if exist ".venv" (
    echo    ⚠️  .venv already exists, skipping...
) else (
    python -m venv .venv
    echo    ✅ Virtual environment created
)

REM Activate and install dependencies
echo.
echo 3️⃣  Installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
echo    ✅ Dependencies installed

REM Check .env file
echo.
echo 4️⃣  Checking environment configuration...
if exist ".env" (
    echo    ✅ .env file exists
) else (
    echo    ⚠️  .env not found, copying from .env.example...
    copy .env.example .env
    echo    ⚠️  IMPORTANT: Edit .env and add your API keys!
    echo    Run: notepad .env
)

REM Initialize database
echo.
echo 5️⃣  Initializing database...
if exist "data.sqlite.db" (
    echo    ✅ Database already exists
) else (
    python init_database_proper.py
    echo    ✅ Database initialized
)

REM Run verification
echo.
echo 6️⃣  Running verification...
python verify_setup.py

echo.
echo ==================================================
echo ✅ Setup Complete!
echo ==================================================
echo.
echo 📝 Next steps:
echo    1. Edit .env and add your API keys:
echo       notepad .env
echo.
echo    2. Activate virtual environment:
echo       .venv\Scripts\activate.bat
echo.
echo    3. Start the server:
echo       uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
echo.
echo    4. Open browser:
echo       http://localhost:8000
echo.
echo ==================================================
pause
