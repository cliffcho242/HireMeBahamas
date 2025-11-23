"""
Script to create the notifications table in the database
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import engine, Base
from app.models import Notification


async def create_notifications_table():
    """Create notifications table"""
    print("Creating notifications table...")
    try:
        async with engine.begin() as conn:
            # Create only the notifications table
            await conn.run_sync(Base.metadata.create_all, tables=[Notification.__table__])
        print("✓ Notifications table created successfully!")
    except Exception as e:
        print(f"✗ Error creating notifications table: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_notifications_table())
