from typing import List, Optional
from uuid import UUID

from app.core.security import get_current_user
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
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new post"""
    db_post = Post(**post.dict(), user_id=current_user.id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    # Load user relationship
    result = await db.execute(
        select(Post).options(selectinload(Post.user)).where(Post.id == db_post.id)
    )
    post_with_user = result.scalar_one()

    # Format response to match frontend expectations
    post_data = PostResponse(
        id=post_with_user.id,
        user_id=post_with_user.user_id,
        user=PostUser.from_orm(post_with_user.user),
        content=post_with_user.content,
        image_url=post_with_user.image_url,
        video_url=post_with_user.video_url,
        post_type=post_with_user.post_type,
        related_job_id=post_with_user.related_job_id,
        likes_count=0,
        comments_count=0,
        is_liked=False,
        created_at=post_with_user.created_at,
        updated_at=post_with_user.updated_at,
    )

    return {"success": True, "post": post_data.dict()}


@router.get("/", response_model=dict)
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get posts with pagination"""
    # Build query with user relationship
    query = select(Post).options(selectinload(Post.user)).order_by(desc(Post.created_at))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    posts = result.scalars().all()

    # Build response with like/comment counts
    posts_data = []
    for post in posts:
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

        post_data = PostResponse(
            id=post.id,
            user_id=post.user_id,
            user=PostUser.from_orm(post.user),
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
        posts_data.append(post_data.dict())

    return {"success": True, "posts": posts_data}


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get a specific post by ID"""
    result = await db.execute(
        select(Post).options(selectinload(Post.user)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    # Get likes count
    likes_result = await db.execute(
        select(func.count()).select_from(PostLike).where(PostLike.post_id == post.id)
    )
    likes_count = likes_result.scalar() or 0

    # Get comments count
    comments_result = await db.execute(
        select(func.count()).select_from(PostComment).where(PostComment.post_id == post.id)
    )
    comments_count = comments_result.scalar() or 0

    # Check if current user liked this post
    is_liked = False
    if current_user:
        liked_result = await db.execute(
            select(PostLike).where(
                and_(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
            )
        )
        is_liked = liked_result.scalar_one_or_none() is not None

    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        user=PostUser.from_orm(post.user),
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

    post_data = PostResponse(
        id=updated_post.id,
        user_id=updated_post.user_id,
        user=PostUser.from_orm(updated_post.user),
        content=updated_post.content,
        image_url=updated_post.image_url,
        video_url=updated_post.video_url,
        post_type=updated_post.post_type,
        related_job_id=updated_post.related_job_id,
        likes_count=0,
        comments_count=0,
        is_liked=False,
        created_at=updated_post.created_at,
        updated_at=updated_post.updated_at,
    )

    return {"success": True, "post": post_data.dict()}


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

    comments_data = [
        CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            user_id=comment.user_id,
            user=CommentUser.from_orm(comment.user),
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        ).dict()
        for comment in comments
    ]

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
        user=CommentUser.from_orm(comment_with_user.user),
        content=comment_with_user.content,
        created_at=comment_with_user.created_at,
        updated_at=comment_with_user.updated_at,
    )

    return {"success": True, "comment": comment_data.dict()}


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
