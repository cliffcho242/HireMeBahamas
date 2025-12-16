"""
Feed API - Cached global feed endpoint

Implements a cached feed endpoint that serves posts from the database
with Redis caching for improved performance. The cache is invalidated
when new posts are created (handled in posts.py).
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis_cache import redis_cache
from app.database import get_db
from app.models import Post

router = APIRouter()


@router.get("/")
async def feed(db: AsyncSession = Depends(get_db)):
    """
    Get the global feed of posts with Redis caching.
    
    This endpoint implements a cached feed that:
    - Checks Redis cache first for fast response
    - Falls back to database if cache miss
    - Caches the result for 30 seconds
    - Returns a list of posts with basic information
    
    Returns:
        dict: Response containing posts array
    """
    key = "feed:global"
    
    # Try to get cached data
    cached = await redis_cache.get(key)
    
    if cached:
        return json.loads(cached) if isinstance(cached, str) else cached
    
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
    await redis_cache.set(key, json.dumps(data), ttl=30)
    
    return data
