#!/bin/bash

echo "=================================================="
echo "🚀 Socializer 1.0 - Automated Setup"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Run this script from Socializer1.0 directory"
    exit 1
fi

# Step 1: Create virtual environment
echo ""
echo "1️⃣  Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "   ⚠️  .venv already exists, skipping..."
else
    python3 -m venv .venv
    echo "   ✅ Virtual environment created"
fi

# Step 2: Activate and install dependencies
echo ""
echo "2️⃣  Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   ✅ Dependencies installed"

# Step 3: Check .env file
echo ""
echo "3️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ⚠️  .env not found, copying from .env.example..."
    cp .env.example .env
    echo "   ⚠️  IMPORTANT: Edit .env and add your API keys!"
fi

# Step 4: Initialize database
echo ""
echo "4️⃣  Initializing database..."
if [ -f "data.sqlite.db" ]; then
    echo "   ✅ Database already exists"
else
    python init_database_proper.py
    echo "   ✅ Database initialized"
fi

# Step 5: Run verification
echo ""
echo "5️⃣  Running verification..."
python verify_setup.py

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env and add your API keys"
echo "   2. Activate virtual environment:"
echo "      source .venv/bin/activate"
echo "   3. Start the server:"
echo "      uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
echo "   4. Open browser:"
echo "      http://localhost:8000"
echo ""
echo "=================================================="
