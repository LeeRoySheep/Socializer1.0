#!/bin/bash

# ================================================
# Socializer 1.0 Setup Script - Linux
# ================================================

echo "=================================================="
echo "🚀 Socializer 1.0 - Linux Setup"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Run this script from Socializer1.0 directory"
    exit 1
fi

# Check Python version
echo ""
echo "1️⃣  Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "   Install it with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   ✅ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "2️⃣  Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "   ⚠️  .venv already exists, skipping..."
else
    python3 -m venv .venv
    echo "   ✅ Virtual environment created"
fi

# Activate and install dependencies
echo ""
echo "3️⃣  Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   ✅ Dependencies installed"

# Check .env file
echo ""
echo "4️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ⚠️  .env not found, copying from .env.example..."
    cp .env.example .env
    echo "   ⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo "   Run: nano .env"
fi

# Initialize database
echo ""
echo "5️⃣  Initializing database..."
if [ -f "data.sqlite.db" ]; then
    echo "   ✅ Database already exists"
else
    python init_database_proper.py
    echo "   ✅ Database initialized"
fi

# Run verification
echo ""
echo "6️⃣  Running verification..."
python verify_setup.py

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env and add your API keys:"
echo "      nano .env"
echo ""
echo "   2. Activate virtual environment:"
echo "      source .venv/bin/activate"
echo ""
echo "   3. Start the server:"
echo "      uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
echo ""
echo "   4. Open browser:"
echo "      http://localhost:8000"
echo ""
echo "=================================================="
