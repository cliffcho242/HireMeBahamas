"""
Script to create all database tables
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import init_db


async def create_all_tables():
    """Create all tables"""
    print("Creating all database tables...")
    try:
        await init_db()
        print("✓ All tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_all_tables())
