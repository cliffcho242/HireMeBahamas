"""
Feed API - Cached global feed endpoint

Implements a cached feed endpoint that serves posts from the database
with Redis caching for improved performance. The cache is invalidated
when new posts are created (handled in posts.py).
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Response
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis_cache import redis_cache
from app.database import get_db
from app.models import Post

router = APIRouter()


@router.get("/")
async def feed(response: Response, db: AsyncSession = Depends(get_db)):
    """
    Get the global feed of posts with Redis and edge caching.
    
    This endpoint implements a multi-layer caching strategy:
    - Edge caching via Cache-Control headers (CDN/browser caching)
    - Redis cache for fast response (TTL: 30 seconds)
    - Falls back to database if cache miss
    
    Edge Cache Strategy:
    - max-age=30: CDN/browser can serve cached response for 30 seconds
    - stale-while-revalidate=60: Can serve stale content while revalidating for 60 seconds
    - Total possible cache lifetime: up to 90 seconds (30s fresh + 60s stale)
    
    This "Facebook LOVES this" approach reduces database load and improves performance
    by allowing CDNs (like Vercel Edge) to serve cached responses at the edge.
    
    Returns:
        dict: Response containing posts array
    """
    # Set edge cache headers for CDN/browser caching
    # This enables Vercel Edge Network and other CDNs to cache responses
    response.headers["Cache-Control"] = "public, max-age=30, stale-while-revalidate=60"
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
