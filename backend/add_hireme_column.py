"""
Script to add is_available_for_hire column to users table
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import engine
from sqlalchemy import text


async def add_is_available_for_hire_column():
    """Add is_available_for_hire column to users table"""
    print("Adding is_available_for_hire column to users table...")
    try:
        async with engine.begin() as conn:
            # Check if column exists
            result = await conn.execute(
                text("PRAGMA table_info(users)")
            )
            columns = result.fetchall()
            column_names = [col[1] for col in columns]
            
            if "is_available_for_hire" not in column_names:
                # Add the column
                await conn.execute(
                    text("ALTER TABLE users ADD COLUMN is_available_for_hire BOOLEAN DEFAULT 0")
                )
                print("✓ is_available_for_hire column added successfully!")
            else:
                print("✓ is_available_for_hire column already exists!")
                
    except Exception as e:
        print(f"✗ Error adding column: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(add_is_available_for_hire_column())
