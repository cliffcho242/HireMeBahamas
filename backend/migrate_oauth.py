"""
Migration script to add OAuth support to the User model.

This script adds the following fields to the users table:
- oauth_provider: String field to store the OAuth provider name ('google', 'apple', or NULL)
- oauth_provider_id: String field to store the user's ID from the OAuth provider
- Makes hashed_password nullable for OAuth users

Run this script to update the database schema for OAuth support.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine, get_db


async def migrate_oauth_fields():
    """Add OAuth fields to users table"""
    
    print("Starting OAuth migration...")
    
    async with engine.begin() as conn:
        # Check if oauth_provider column exists
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='oauth_provider'
        """))
        
        if result.first() is None:
            print("Adding oauth_provider column...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN oauth_provider VARCHAR(50)
            """))
            print("✓ oauth_provider column added")
        else:
            print("✓ oauth_provider column already exists")
        
        # Check if oauth_provider_id column exists
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='oauth_provider_id'
        """))
        
        if result.first() is None:
            print("Adding oauth_provider_id column...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN oauth_provider_id VARCHAR(255)
            """))
            print("✓ oauth_provider_id column added")
        else:
            print("✓ oauth_provider_id column already exists")
        
        # Make hashed_password nullable for OAuth users
        print("Making hashed_password nullable...")
        await conn.execute(text("""
            ALTER TABLE users 
            ALTER COLUMN hashed_password DROP NOT NULL
        """))
        print("✓ hashed_password is now nullable")
    
    print("\nOAuth migration completed successfully!")
    print("\nNew features available:")
    print("- Users can sign in with Google")
    print("- Users can sign in with Apple")
    print("- OAuth users don't require passwords")


async def rollback_oauth_fields():
    """Rollback OAuth migration (WARNING: This will delete OAuth user data)"""
    
    print("WARNING: Rolling back OAuth migration...")
    print("This will remove OAuth-related fields from the users table.")
    
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Rollback cancelled.")
        return
    
    async with engine.begin() as conn:
        print("Removing oauth_provider column...")
        await conn.execute(text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS oauth_provider
        """))
        
        print("Removing oauth_provider_id column...")
        await conn.execute(text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS oauth_provider_id
        """))
        
        print("Making hashed_password required again...")
        # NOTE: This will fail if there are OAuth users with NULL passwords
        # You need to delete or update those users first
        await conn.execute(text("""
            ALTER TABLE users 
            ALTER COLUMN hashed_password SET NOT NULL
        """))
    
    print("\nOAuth migration rolled back successfully!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback_oauth_fields())
    else:
        asyncio.run(migrate_oauth_fields())
