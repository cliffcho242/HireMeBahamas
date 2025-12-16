#!/usr/bin/env python3
"""
Database migration script to create the refresh_tokens table.

This script creates the refresh_tokens table for storing JWT refresh tokens
as part of the production-grade authentication implementation.

Run this script once to set up the table:
    python create_refresh_tokens_table.py
"""
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from api.backend_app.database import get_async_session


async def create_refresh_tokens_table():
    """Create the refresh_tokens table if it doesn't exist"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash VARCHAR(255) NOT NULL UNIQUE,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        revoked BOOLEAN NOT NULL DEFAULT FALSE,
        revoked_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ip_address VARCHAR(45),
        user_agent VARCHAR(500)
    );
    
    CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
    CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
    CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
    CREATE INDEX IF NOT EXISTS idx_refresh_tokens_revoked ON refresh_tokens(revoked);
    """
    
    try:
        async with get_async_session() as session:
            # Execute each statement separately
            for statement in create_table_sql.strip().split(';'):
                statement = statement.strip()
                if statement:
                    await session.execute(text(statement))
            await session.commit()
            print("✅ Successfully created refresh_tokens table and indexes")
            return True
    except Exception as e:
        print(f"❌ Error creating refresh_tokens table: {e}")
        return False


async def verify_table():
    """Verify the table was created correctly"""
    try:
        async with get_async_session() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'refresh_tokens'")
            )
            count = result.scalar()
            
            if count > 0:
                print("✅ Table 'refresh_tokens' exists")
                
                # Get column info
                result = await session.execute(
                    text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'refresh_tokens'
                        ORDER BY ordinal_position
                    """)
                )
                columns = result.fetchall()
                print("\nTable structure:")
                for col_name, col_type in columns:
                    print(f"  - {col_name}: {col_type}")
                
                return True
            else:
                print("❌ Table 'refresh_tokens' does not exist")
                return False
    except Exception as e:
        print(f"❌ Error verifying table: {e}")
        return False


async def main():
    """Main migration function"""
    print("=" * 60)
    print("Refresh Tokens Table Migration")
    print("=" * 60)
    print()
    
    print("Creating refresh_tokens table...")
    success = await create_refresh_tokens_table()
    
    if success:
        print("\nVerifying table creation...")
        await verify_table()
        print("\n✅ Migration completed successfully!")
        print("\nYou can now use the refresh token authentication system.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
