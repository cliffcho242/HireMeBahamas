"""
Migration to add subscription fields to users table.
Run this after the model changes to add subscription support.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


async def upgrade():
    """Add subscription fields to users table"""
    async with engine.begin() as conn:
        # Check if columns already exist
        result = await conn.execute(
            text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('subscription_plan', 'subscription_status', 'subscription_end_date')
            """
            )
        )
        existing_columns = {row[0] for row in result}
        
        # Add subscription_plan column if it doesn't exist
        if "subscription_plan" not in existing_columns:
            await conn.execute(
                text(
                    """
                    ALTER TABLE users 
                    ADD COLUMN subscription_plan VARCHAR(20) DEFAULT 'free'
                """
                )
            )
            print("✓ Added subscription_plan column")
        else:
            print("✓ subscription_plan column already exists")
        
        # Add subscription_status column if it doesn't exist
        if "subscription_status" not in existing_columns:
            await conn.execute(
                text(
                    """
                    ALTER TABLE users 
                    ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'active'
                """
                )
            )
            print("✓ Added subscription_status column")
        else:
            print("✓ subscription_status column already exists")
        
        # Add subscription_end_date column if it doesn't exist
        if "subscription_end_date" not in existing_columns:
            await conn.execute(
                text(
                    """
                    ALTER TABLE users 
                    ADD COLUMN subscription_end_date TIMESTAMP WITH TIME ZONE
                """
                )
            )
            print("✓ Added subscription_end_date column")
        else:
            print("✓ subscription_end_date column already exists")


async def downgrade():
    """Remove subscription fields from users table"""
    async with engine.begin() as conn:
        await conn.execute(
            text("ALTER TABLE users DROP COLUMN IF EXISTS subscription_plan")
        )
        await conn.execute(
            text("ALTER TABLE users DROP COLUMN IF EXISTS subscription_status")
        )
        await conn.execute(
            text("ALTER TABLE users DROP COLUMN IF EXISTS subscription_end_date")
        )
        print("✓ Removed subscription columns")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migration for subscription fields")
    parser.add_argument(
        "action", choices=["upgrade", "downgrade"], help="Migration action"
    )
    args = parser.parse_args()
    
    if args.action == "upgrade":
        print("Running migration: add subscription fields")
        asyncio.run(upgrade())
        print("Migration completed successfully!")
    else:
        print("Running downgrade: remove subscription fields")
        asyncio.run(downgrade())
        print("Downgrade completed successfully!")
