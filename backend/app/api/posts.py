from typing import List, Optional, Dict
from uuid import UUID
import logging

from app.core.security import get_current_user
from app.core.cache import get_cached, set_cached, invalidate_cache
from app.core.cache_headers import CacheStrategy, handle_conditional_request, apply_performance_headers
from app.core.pagination import paginate_auto, format_paginated_response
from app.database import get_db
from app.models import Post, PostLike, PostComment, User
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    CommentCreate,
    CommentResponse,
    PostUser,
    CommentUser,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter()
logger = logging.getLogger(__name__)


async def batch_get_post_metadata(
    post_ids: List[int],
    db: AsyncSession,
    current_user: Optional[User] = None
) -> Dict[int, Dict]:
    """
    Batch fetch metadata for multiple posts to prevent N+1 queries.
    
    Returns dict mapping post_id to metadata:
    {
        post_id: {
            'likes_count': int,
            'comments_count': int,
            'is_liked': bool
        }
    }
    """
    if not post_ids:
        return {}
    
    # Batch fetch likes counts for all posts in one query
    likes_query = (
        select(PostLike.post_id, func.count(PostLike.id).label('count'))
        .where(PostLike.post_id.in_(post_ids))
        .group_by(PostLike.post_id)
    )
    likes_result = await db.execute(likes_query)
    likes_counts = {row.post_id: row.count for row in likes_result}
    
    # Batch fetch comments counts for all posts in one query
    comments_query = (
        select(PostComment.post_id, func.count(PostComment.id).label('count'))
        .where(PostComment.post_id.in_(post_ids))
        .group_by(PostComment.post_id)
    )
    comments_result = await db.execute(comments_query)
    comments_counts = {row.post_id: row.count for row in comments_result}
    
    # Batch fetch user likes if user is authenticated
    user_likes = set()
    if current_user:
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
        user_likes = {row.post_id for row in user_likes_result}
    
    # Build metadata dictionary
    metadata = {}
    for post_id in post_ids:
        metadata[post_id] = {
            'likes_count': likes_counts.get(post_id, 0),
            'comments_count': comments_counts.get(post_id, 0),
            'is_liked': post_id in user_likes
        }
    
    return metadata


async def enrich_post_with_metadata(
    post: Post,
    db: AsyncSession,
    current_user: Optional[User] = None
) -> PostResponse:
    """
    Helper function to enrich a post with metadata (likes count, comments count, is_liked).
    This helps avoid N+1 query problems by centralizing the logic.
    """
    # Get likes count
    likes_result = await db.execute(
        select(func.count()).select_from(PostLike).where(PostLike.post_id == post.id)
    )
    likes_count = likes_result.scalar() or 0

    # Get comments count
    comments_result = await db.execute(
        select(func.count())
        .select_from(PostComment)
        .where(PostComment.post_id == post.id)
    )
    comments_count = comments_result.scalar() or 0

    # Check if current user liked this post
    is_liked = False
    if current_user:
        liked_result = await db.execute(
            select(PostLike).where(
                and_(
                    PostLike.post_id == post.id, PostLike.user_id == current_user.id
                )
            )
        )
        is_liked = liked_result.scalar_one_or_none() is not None

    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        user=PostUser.model_validate(post.user),
        content=post.content,
        image_url=post.image_url,
        video_url=post.video_url,
        post_type=post.post_type,
        related_job_id=post.related_job_id,
        likes_count=likes_count,
        comments_count=comments_count,
        is_liked=is_liked,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


def enrich_post_with_cached_metadata(
    post: Post,
    metadata: Dict
) -> PostResponse:
    """
    Enrich a post with pre-fetched metadata (for batch operations).
    """
    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        user=PostUser.model_validate(post.user),
        content=post.content,
        image_url=post.image_url,
        video_url=post.video_url,
        post_type=post.post_type,
        related_job_id=post.related_job_id,
        likes_count=metadata.get('likes_count', 0),
        comments_count=metadata.get('comments_count', 0),
        is_liked=metadata.get('is_liked', False),
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new post"""
    db_post = Post(**post.model_dump(), user_id=current_user.id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    # Load user relationship
    result = await db.execute(
        select(Post).options(selectinload(Post.user)).where(Post.id == db_post.id)
    )
    post_with_user = result.scalar_one()

    # Use helper to enrich post with metadata
    post_data = await enrich_post_with_metadata(post_with_user, db, current_user)
    
    # Invalidate posts cache
    await invalidate_cache("posts:list:")

    return {"success": True, "post": post_data.model_dump()}


@router.get("/", response_model=dict)
async def get_posts(
    request: Request,
    # Dual pagination support
    cursor: Optional[str] = Query(None, description="Cursor for cursor-based pagination (mobile)"),
    skip: Optional[int] = Query(None, ge=0, description="Offset for offset-based pagination (web)"),
    page: Optional[int] = Query(None, ge=1, description="Page number (alternative to skip)"),
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    direction: str = Query("next", regex="^(next|previous)$", description="Pagination direction"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get posts with dual pagination support (cursor or offset-based)
    
    Mobile API Optimization Features:
    - **Dual Pagination**: Supports both cursor-based (efficient for infinite scroll) 
      and offset-based (page numbers) pagination
    - **HTTP Caching**: Returns 304 Not Modified when content hasn't changed (ETag validation)
    - **N+1 Prevention**: Batches all likes/comments queries to prevent N+1 problems
    
    Pagination Modes:
    - Cursor-based (recommended for mobile): Use `cursor` parameter
    - Offset-based (for web): Use `skip` or `page` parameter
    - Default: cursor-based starting from the most recent posts
    
    Note: Posts remain visible regardless of author's account status.
    Performance: Cached for 60 seconds with stale-while-revalidate.
    """
    # Try to get from cache first (sub-50ms cache hit)
    user_id = current_user.id if current_user else "anonymous"
    cache_params = f"{cursor}:{skip}:{page}:{limit}:{direction}"
    cache_key = f"posts:list:{cache_params}:{user_id}"
    cached_response = await get_cached(cache_key)
    if cached_response is not None:
        # Return cached response with HTTP caching headers
        response = handle_conditional_request(request, cached_response, CacheStrategy.POSTS)
        apply_performance_headers(response)
        return response
    
    # Build query with user relationship (eager loading to prevent N+1)
    # IMPORTANT: We intentionally do NOT filter by User.is_active here
    # Posts should remain visible regardless of the author's account status
    base_query = select(Post).options(selectinload(Post.user))

    # Use dual pagination system (auto-detects mode)
    posts, pagination_meta = await paginate_auto(
        db=db,
        query=base_query,
        model_class=Post,
        cursor=cursor,
        skip=skip,
        page=page,
        limit=limit,
        direction=direction,
        order_by_field="created_at",
        order_direction="desc",
        count_total=False,  # Expensive for large datasets
    )

    # Filter out posts with missing user relationships
    valid_posts = []
    for post in posts:
        if not post.user:
            logger.warning(
                f"Post {post.id} has no associated user relationship - "
                f"possible data integrity issue. Skipping post."
            )
            continue
        
        # Log inactive users for monitoring
        if not post.user.is_active:
            logger.info(
                f"Including post {post.id} from inactive user {post.user.id} "
                f"({post.user.email}) in feed - posts remain visible after user inactivity"
            )
        
        valid_posts.append(post)

    # Batch fetch metadata for all posts (prevents N+1 queries)
    post_ids = [post.id for post in valid_posts]
    metadata_batch = await batch_get_post_metadata(post_ids, db, current_user)

    # Build response with pre-fetched metadata
    posts_data = []
    for post in valid_posts:
        post_metadata = metadata_batch.get(post.id, {
            'likes_count': 0,
            'comments_count': 0,
            'is_liked': False
        })
        post_response = enrich_post_with_cached_metadata(post, post_metadata)
        posts_data.append(post_response.model_dump())

    response = format_paginated_response(posts_data, pagination_meta)
    
    # Cache for 60 seconds (balance between freshness and performance)
    await set_cached(cache_key, response, ttl=60)
    
    # Return with HTTP caching headers
    json_response = handle_conditional_request(request, response, CacheStrategy.POSTS)
    apply_performance_headers(json_response)
    return json_response


@router.get("/user/{user_id}", response_model=dict)
async def get_user_posts(
    request: Request,
    user_id: int,
    # Dual pagination support
    cursor: Optional[str] = Query(None, description="Cursor for cursor-based pagination (mobile)"),
    skip: Optional[int] = Query(None, ge=0, description="Offset for offset-based pagination (web)"),
    page: Optional[int] = Query(None, ge=1, description="Page number (alternative to skip)"),
    limit: int = Query(20, ge=1, le=100),
    direction: str = Query("next", regex="^(next|previous)$"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get posts for a specific user with dual pagination and N+1 prevention
    
    Mobile API Optimization Features:
    - **Dual Pagination**: Cursor-based (mobile) or offset-based (web)
    - **HTTP Caching**: ETag validation with 304 Not Modified responses
    - **N+1 Prevention**: Batch fetching of likes/comments metadata
    
    Note: Posts remain visible regardless of author's account status.
    Performance: Cached with stale-while-revalidate strategy.
    """
    # Verify user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    target_user = user_result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Build query for user's posts with user relationship (eager loading)
    # IMPORTANT: We intentionally do NOT filter by User.is_active here
    base_query = (
        select(Post)
        .options(selectinload(Post.user))
        .where(Post.user_id == user_id)
    )

    # Use dual pagination system
    posts, pagination_meta = await paginate_auto(
        db=db,
        query=base_query,
        model_class=Post,
        cursor=cursor,
        skip=skip,
        page=page,
        limit=limit,
        direction=direction,
        order_by_field="created_at",
        order_direction="desc",
        count_total=False,
    )

    # Filter valid posts
    valid_posts = []
    for post in posts:
        if not post.user:
            logger.warning(
                f"Post {post.id} has no associated user relationship - "
                f"possible data integrity issue. Skipping post."
            )
            continue
        
        if not post.user.is_active:
            logger.info(
                f"Including post {post.id} from inactive user {post.user.id} "
                f"({post.user.email}) in user profile - posts remain visible after user inactivity"
            )
        
        valid_posts.append(post)

    # Batch fetch metadata (prevents N+1 queries)
    post_ids = [post.id for post in valid_posts]
    metadata_batch = await batch_get_post_metadata(post_ids, db, current_user)

    # Build response with pre-fetched metadata
    posts_data = []
    for post in valid_posts:
        post_metadata = metadata_batch.get(post.id, {
            'likes_count': 0,
            'comments_count': 0,
            'is_liked': False
        })
        post_response = enrich_post_with_cached_metadata(post, post_metadata)
        posts_data.append(post_response.model_dump())

    response = format_paginated_response(posts_data, pagination_meta)
    
    # Return with HTTP caching headers
    json_response = handle_conditional_request(request, response, CacheStrategy.PUBLIC_PROFILE)
    apply_performance_headers(json_response)
    return json_response


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get a specific post by ID
    
    Note: Returns post regardless of author's account status (is_active).
    Posts remain accessible even if the author's account becomes inactive.
    """
    result = await db.execute(
        select(Post).options(selectinload(Post.user)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    
    # Defensive check: ensure user relationship exists
    if not post.user:
        logger.error(
            f"Post {post_id} has no associated user - data integrity issue"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Post data incomplete - user information missing"
        )

    # Use helper to enrich post with metadata
    return await enrich_post_with_metadata(post, db, current_user)


@router.put("/{post_id}", response_model=dict)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a post"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    # Update post
    post.content = post_update.content
    await db.commit()
    await db.refresh(post)

    # Load user relationship
    result = await db.execute(
        select(Post).options(selectinload(Post.user)).where(Post.id == post_id)
    )
    updated_post = result.scalar_one()

    # Use helper to enrich post with metadata
    post_data = await enrich_post_with_metadata(updated_post, db, current_user)

    return {"success": True, "post": post_data.model_dump()}


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a post"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    await db.delete(post)
    await db.commit()

    return {"success": True, "message": "Post deleted successfully"}


@router.post("/{post_id}/like", response_model=dict)
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle like on a post"""
    # Check if post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    # Check if already liked
    like_result = await db.execute(
        select(PostLike).where(
            and_(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
        )
    )
    existing_like = like_result.scalar_one_or_none()

    if existing_like:
        # Unlike
        await db.delete(existing_like)
        await db.commit()
        action = "unlike"
    else:
        # Like
        new_like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        await db.commit()
        action = "like"

    # Get updated likes count
    likes_result = await db.execute(
        select(func.count()).select_from(PostLike).where(PostLike.post_id == post_id)
    )
    likes_count = likes_result.scalar() or 0

    return {
        "success": True,
        "action": action,
        "liked": action == "like",
        "likes_count": likes_count,
    }


@router.get("/{post_id}/comments", response_model=dict)
async def get_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get comments for a post"""
    # Check if post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    # Get comments
    result = await db.execute(
        select(PostComment)
        .options(selectinload(PostComment.user))
        .where(PostComment.post_id == post_id)
        .order_by(PostComment.created_at)
    )
    comments = result.scalars().all()

    comments_data = []
    for comment in comments:
        # Defensive check: ensure comment has a valid user relationship
        # This handles edge cases where user might be deleted but comment remains
        if not comment.user:
            logger.warning(
                f"Comment {comment.id} has no associated user relationship - "
                f"possible data integrity issue. Skipping comment."
            )
            continue

        comments_data.append(
            CommentResponse(
                id=comment.id,
                post_id=comment.post_id,
                user_id=comment.user_id,
                user=CommentUser.model_validate(comment.user),
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            ).model_dump()
        )

    return {"success": True, "comments": comments_data}


@router.post("/{post_id}/comments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a comment on a post"""
    # Check if post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    # Create comment
    db_comment = PostComment(
        post_id=post_id, user_id=current_user.id, content=comment.content
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    # Load user relationship
    result = await db.execute(
        select(PostComment)
        .options(selectinload(PostComment.user))
        .where(PostComment.id == db_comment.id)
    )
    comment_with_user = result.scalar_one()

    comment_data = CommentResponse(
        id=comment_with_user.id,
        post_id=comment_with_user.post_id,
        user_id=comment_with_user.user_id,
        user=CommentUser.model_validate(comment_with_user.user),
        content=comment_with_user.content,
        created_at=comment_with_user.created_at,
        updated_at=comment_with_user.updated_at,
    )

    return {"success": True, "comment": comment_data.model_dump()}


@router.delete("/{post_id}/comments/{comment_id}")
async def delete_comment(
    post_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment"""
    # Check if comment exists
    result = await db.execute(
        select(PostComment).where(
            and_(PostComment.id == comment_id, PostComment.post_id == post_id)
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    await db.delete(comment)
    await db.commit()

    return {"success": True, "message": "Comment deleted successfully"}
