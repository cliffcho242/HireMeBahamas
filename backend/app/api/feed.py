"""
Feed API - Cached global feed endpoint

Implements a cached feed endpoint that serves posts from the database
with in-memory TTL caching for improved performance. The cache automatically
expires after 30 seconds.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.memory_cache import cache_get, cache_set
from app.database import get_db
from app.models import Post

router = APIRouter()


@router.get("/")
async def feed(db: AsyncSession = Depends(get_db)):
    """
    Get the global feed of posts with in-memory caching.
    
    This endpoint implements a cached feed that:
    - Checks in-memory cache first for fast response
    - Falls back to database if cache miss
    - Caches the result for 30 seconds (TTL ≤ 60s)
    - Returns a list of posts with basic information
    
    Returns:
        dict: Response containing posts array
    """
    key = "feed:global"
    
    # Try to get cached data (30s TTL)
    cached = cache_get(key, ttl=30)
    
    if cached is not None:
        return cached
    
    # Cache miss - fetch from database
    query = select(Post).options(
        selectinload(Post.user)
    ).order_by(desc(Post.created_at)).limit(20)
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # Serialize posts for response
    posts_data = [
        {
            "id": str(post.id),
            "content": post.content,
            "user_id": str(post.user_id),
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        }
        for post in posts
    ]
    
    data = {"posts": posts_data}
    
    # Cache the result for 30 seconds
    cache_set(key, data)
    
    return data
