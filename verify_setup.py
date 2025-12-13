#!/usr/bin/env python3
"""
Quick verification script for Socializer 1.0 setup
Tests that all critical components are importable and functional
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("🔍 Socializer 1.0 - Setup Verification")
print("=" * 60)

# Test 1: Python version
print("\n1️⃣  Python Version Check...")
if sys.version_info >= (3, 11):
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
else:
    print(f"   ⚠️  Python {sys.version_info.major}.{sys.version_info.minor} (3.11+ recommended)")

# Test 2: Required files exist
print("\n2️⃣  File Structure Check...")
required_files = [
    "app/main.py",
    "ai_chatagent.py",
    "requirements.txt",
    ".env",
    "static/js/chat.js",
    "templates/login.html"
]

for file in required_files:
    if Path(file).exists():
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - MISSING!")

# Test 3: Import critical modules
print("\n3️⃣  Module Import Check...")
imports_to_test = [
    ("fastapi", "FastAPI"),
    ("sqlalchemy", "SQLAlchemy"),
    ("langchain", "LangChain"),
    ("pydantic", "Pydantic"),
    ("uvicorn", "Uvicorn"),
]

failed_imports = []
for module, name in imports_to_test:
    try:
        __import__(module)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} - NOT INSTALLED!")
        failed_imports.append(name)

# Test 4: Environment variables
print("\n4️⃣  Environment Variables Check...")
if Path(".env").exists():
    print("   ✅ .env file exists")
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["SECRET_KEY", "OPENAI_API_KEY", "TAVILY_API_KEY"]
    for var in required_vars:
        if os.getenv(var):
            print(f"   ✅ {var} is set")
        else:
            print(f"   ⚠️  {var} not set (may cause issues)")
else:
    print("   ❌ .env file not found! Copy .env.example to .env")

# Test 5: Database
print("\n5️⃣  Database Check...")
if Path("data.sqlite.db").exists():
    print("   ✅ data.sqlite.db exists")
else:
    print("   ⚠️  data.sqlite.db not found (will be created on first run)")

# Summary
print("\n" + "=" * 60)
if failed_imports:
    print("❌ SETUP INCOMPLETE")
    print(f"   Missing: {', '.join(failed_imports)}")
    print("   Run: pip install -r requirements.txt")
else:
    print("✅ SETUP LOOKS GOOD!")
    print("   Run: uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
print("=" * 60)
