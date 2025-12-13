#!/usr/bin/env python3
"""
Proper database initialization for Socializer 1.0
Uses the datamanager models (not app/models)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from datamanager.data_model import Base
from app.config import SQLALCHEMY_DATABASE_URL

print("=" * 60)
print("🔨 Initializing Socializer 1.0 Database")
print("=" * 60)
print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create all tables
print("\n📋 Creating tables from datamanager.data_model...")
Base.metadata.create_all(bind=engine)

# Verify tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"\n✅ Created {len(tables)} tables:")
for table in tables:
    columns = inspector.get_columns(table)
    print(f"   • {table} ({len(columns)} columns)")

# Check users table specifically
if 'users' in tables:
    print("\n📋 Users table schema:")
    for col in inspector.get_columns('users'):
        print(f"   • {col['name']}: {col['type']}")

print("\n" + "=" * 60)
print("✅ Database initialized successfully!")
print("=" * 60)
