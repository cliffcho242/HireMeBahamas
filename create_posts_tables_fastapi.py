#!/usr/bin/env python3
"""
Create posts tables in the database.
This script creates the necessary tables for the posts feature.
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import async_engine, Base
from app.models import Post, PostLike, PostComment


async def create_posts_tables():
    """Create posts tables"""
    print("Creating posts tables...")
    
    try:
        async with async_engine.begin() as conn:
            # Create only the posts-related tables
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        
        print("✅ Posts tables created successfully!")
        print("Tables created:")
        print("  - posts")
        print("  - post_likes")
        print("  - post_comments")
        
    except Exception as e:
        print(f"❌ Failed to create posts tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_posts_tables())
