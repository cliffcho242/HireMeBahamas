"""
Feed routes - Posts, likes, comments.

Provides endpoints for social feed functionality including creating posts,
liking posts, and commenting on posts.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.core.cache import get_cached, set_cached, invalidate_cache
from app.core.pagination import paginate_auto, format_paginated_response
from app.database import get_db
from app.models import Post, PostLike, PostComment, User
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    CommentCreate,
    CommentResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[PostResponse])
async def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's personalized feed with posts from followed users."""
    # Get list of users the current user follows
    from app.models import Follow
    
    follow_result = await db.execute(
        select(Follow.followed_id).where(Follow.follower_id == current_user.id)
    )
    followed_ids = [row[0] for row in follow_result.all()]
    
    # Include current user's own posts
    followed_ids.append(current_user.id)
    
    # Get posts from followed users
    query = (
        select(Post)
        .where(Post.user_id.in_(followed_ids))
        .options(selectinload(Post.user))
        .order_by(desc(Post.created_at))
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # Get likes and comments count for each post
    post_ids = [post.id for post in posts]
    
    # Get likes count
    likes_query = (
        select(PostLike.post_id, func.count(PostLike.id).label('count'))
        .where(PostLike.post_id.in_(post_ids))
        .group_by(PostLike.post_id)
    )
    likes_result = await db.execute(likes_query)
    likes_counts = {row.post_id: row.count for row in likes_result}
    
    # Get user's likes
    user_likes_query = (
        select(PostLike.post_id)
        .where(
            and_(
                PostLike.post_id.in_(post_ids),
                PostLike.user_id == current_user.id
            )
        )
    )
    user_likes_result = await db.execute(user_likes_query)
    user_liked_post_ids = {row[0] for row in user_likes_result}
    
    # Get comments count
    comments_query = (
        select(PostComment.post_id, func.count(PostComment.id).label('count'))
        .where(PostComment.post_id.in_(post_ids))
        .group_by(PostComment.post_id)
    )
    comments_result = await db.execute(comments_query)
    comments_counts = {row.post_id: row.count for row in comments_result}
    
    # Build response with metadata
    posts_data = []
    for post in posts:
        post_dict = PostResponse.from_orm(post).dict()
        post_dict['likes_count'] = likes_counts.get(post.id, 0)
        post_dict['comments_count'] = comments_counts.get(post.id, 0)
        post_dict['is_liked'] = post.id in user_liked_post_ids
        posts_data.append(post_dict)
    
    return posts_data


@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new post."""
    new_post = Post(
        content=post_data.content,
        image_url=post_data.image_url,
        user_id=current_user.id,
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    # Invalidate feed cache
    await invalidate_cache("posts:*")
    
    logger.info(f"Post created: id={new_post.id}, user_id={current_user.id}")
    
    return PostResponse.from_orm(new_post)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific post by ID."""
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.user))
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get metadata
    likes_result = await db.execute(
        select(func.count()).select_from(PostLike).where(PostLike.post_id == post_id)
    )
    likes_count = likes_result.scalar()
    
    is_liked_result = await db.execute(
        select(PostLike).where(
            and_(
                PostLike.post_id == post_id,
                PostLike.user_id == current_user.id
            )
        )
    )
    is_liked = is_liked_result.scalar_one_or_none() is not None
    
    comments_result = await db.execute(
        select(func.count()).select_from(PostComment).where(PostComment.post_id == post_id)
    )
    comments_count = comments_result.scalar()
    
    post_dict = PostResponse.from_orm(post).dict()
    post_dict['likes_count'] = likes_count
    post_dict['comments_count'] = comments_count
    post_dict['is_liked'] = is_liked
    
    return post_dict


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Like a post."""
    # Check if post exists
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if already liked
    like_result = await db.execute(
        select(PostLike).where(
            and_(
                PostLike.post_id == post_id,
                PostLike.user_id == current_user.id
            )
        )
    )
    existing_like = like_result.scalar_one_or_none()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    # Create like
    like = PostLike(post_id=post_id, user_id=current_user.id)
    db.add(like)
    await db.commit()
    
    # Invalidate cache
    await invalidate_cache(f"post:{post_id}:*")
    
    return {"message": "Post liked successfully"}


@router.delete("/{post_id}/like")
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unlike a post."""
    # Find like
    like_result = await db.execute(
        select(PostLike).where(
            and_(
                PostLike.post_id == post_id,
                PostLike.user_id == current_user.id
            )
        )
    )
    like = like_result.scalar_one_or_none()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )
    
    await db.delete(like)
    await db.commit()
    
    # Invalidate cache
    await invalidate_cache(f"post:{post_id}:*")
    
    return {"message": "Post unliked successfully"}


@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a comment on a post."""
    # Check if post exists
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Create comment
    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content,
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    # Invalidate cache
    await invalidate_cache(f"post:{post_id}:*")
    
    return CommentResponse.from_orm(comment)


@router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comments for a post."""
    # Check if post exists
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get comments
    query = (
        select(PostComment)
        .where(PostComment.post_id == post_id)
        .options(selectinload(PostComment.user))
        .order_by(desc(PostComment.created_at))
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    comments = result.scalars().all()
    
    return [CommentResponse.from_orm(comment) for comment in comments]


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a post (only post owner or admin can delete)."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user is post owner or admin
    if post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    await db.delete(post)
    await db.commit()
    
    # Invalidate cache
    await invalidate_cache("posts:*")
    
    return {"message": "Post deleted successfully"}
