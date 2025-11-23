#!/usr/bin/env python3
"""
Create profile_pictures table for storing multiple profile images per user
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import engine, Base
from app.models import ProfilePicture
import asyncio


async def create_profile_pictures_table():
    """Create the profile_pictures table"""
    async with engine.begin() as conn:
        # Create the table
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Profile pictures table created successfully!")


if __name__ == "__main__":
    print("Creating profile_pictures table...")
    asyncio.run(create_profile_pictures_table())
    print("\nTable structure:")
    print("- id: Primary key")
    print("- user_id: Foreign key to users table")
    print("- file_url: URL/path to the image file")
    print("- filename: Original filename")
    print("- file_size: Size of the file in bytes")
    print("- is_current: Boolean indicating if this is the active profile picture")
    print("- created_at: Timestamp when uploaded")
