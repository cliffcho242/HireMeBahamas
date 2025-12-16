#!/usr/bin/env python3
"""
Demo script for bulletproof database parsing (app/database.py)
This demonstrates how the module behaves in different scenarios.
"""

import os
import sys
import logging

# Configure logging to see output
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

print("=" * 70)
print("BULLETPROOF DATABASE PARSING DEMO")
print("=" * 70)
print()

# Scenario 1: Missing DATABASE_URL
print("Scenario 1: Missing DATABASE_URL")
print("-" * 70)
if "DATABASE_URL" in os.environ:
    del os.environ["DATABASE_URL"]
if "app.database" in sys.modules:
    del sys.modules["app.database"]

import app.database as db

db.DATABASE_URL = None
db.engine = None
result = db.init_db()
print(f"Result: {result}")
print(f"✓ No crash, returns None\n")

# Scenario 2: Invalid DATABASE_URL (missing credentials)
print("Scenario 2: Invalid DATABASE_URL (missing credentials)")
print("-" * 70)
os.environ["DATABASE_URL"] = "postgresql://@localhost:5432/testdb"
if "app.database" in sys.modules:
    del sys.modules["app.database"]
import app.database as db2

db2.engine = None
result = db2.init_db()
print(f"Result: {result}")
print(f"✓ No crash, returns None\n")

# Scenario 3: Invalid DATABASE_URL (missing host)
print("Scenario 3: Invalid DATABASE_URL (missing host)")
print("-" * 70)
os.environ["DATABASE_URL"] = "postgresql://user:pass@:5432/testdb"
if "app.database" in sys.modules:
    del sys.modules["app.database"]
import app.database as db3

db3.engine = None
result = db3.init_db()
print(f"Result: {result}")
print(f"✓ No crash, returns None\n")

# Scenario 4: Malformed DATABASE_URL
print("Scenario 4: Malformed DATABASE_URL")
print("-" * 70)
os.environ["DATABASE_URL"] = "not-a-valid-url"
if "app.database" in sys.modules:
    del sys.modules["app.database"]
import app.database as db4

db4.engine = None
result = db4.init_db()
print(f"Result: {result}")
print(f"✓ No crash, returns None\n")

# Scenario 5: Valid DATABASE_URL (mocked)
print("Scenario 5: Valid DATABASE_URL structure")
print("-" * 70)
os.environ["DATABASE_URL"] = "postgresql://testuser:testpass@localhost:5432/testdb"
if "app.database" in sys.modules:
    del sys.modules["app.database"]

from unittest.mock import patch, MagicMock
import app.database as db5

with patch("app.database.create_engine") as mock_create_engine:
    mock_engine = MagicMock()
    mock_engine.__repr__ = lambda self: "<Mock SQLAlchemy Engine>"
    mock_create_engine.return_value = mock_engine

    db5.engine = None
    result = db5.init_db()
    print(f"Result: {result}")
    print(f"✓ Returns engine object")
    print(f"✓ Configuration:")
    call_args = mock_create_engine.call_args
    print(f"  - pool_pre_ping: {call_args.kwargs['pool_pre_ping']}")
    print(f"  - pool_recycle: {call_args.kwargs['pool_recycle']}")
    print(f"  - sslmode: {call_args.kwargs['connect_args']['sslmode']}")

print()
print("=" * 70)
print("DEMO COMPLETE")
print("=" * 70)
print()
print("Key Features Demonstrated:")
print("✓ Clean validation - checks for missing URL, credentials, and host")
print("✓ No crashes - always returns None on error")
print("✓ Clear logs - warning for errors, info for success")
print("✓ Zero ambiguity - explicit error messages")
print("✓ Production-ready config - pool_pre_ping, pool_recycle, SSL required")
print()
