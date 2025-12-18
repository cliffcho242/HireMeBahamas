"""
Boost Posts API - Enhanced post visibility for paid promotion
"""
import os
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models import User, Post, BoostedPost, Payment
from app.schemas.subscription import (
    BoostPostRequest,
    BoostPostResponse,
    BoostedPostStats,
)

router = APIRouter(prefix="/boosts", tags=["boosts"])

# Stripe for payment processing
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_AVAILABLE = bool(stripe.api_key)
except ImportError:
    STRIPE_AVAILABLE = False

# Boost pricing configuration
BOOST_PRICE_PER_DAY = 5.0  # $5 per day of boosting
MIN_BOOST_DAYS = 1
MAX_BOOST_DAYS = 30


# ============================================================================
# BOOST POST
# ============================================================================

@router.post("/post", response_model=BoostPostResponse)
async def boost_post(
    boost_request: BoostPostRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Boost a post for enhanced visibility
    
    Boosted posts:
    - Appear first in feeds
    - Are highlighted visually
    - Get priority placement
    
    Price: $5/day (default 7 days = $35)
    """
    # Validate post exists and belongs to user
    post = await db.get(Post, boost_request.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only boost your own posts"
        )
    
    # Check if post is already boosted
    result = await db.execute(
        select(BoostedPost)
        .where(
            and_(
                BoostedPost.post_id == boost_request.post_id,
                BoostedPost.status == "active",
                BoostedPost.boost_end > datetime.utcnow()
            )
        )
    )
    existing_boost = result.scalar_one_or_none()
    
    if existing_boost:
        raise HTTPException(
            status_code=400,
            detail="Post is already boosted. Wait for current boost to expire."
        )
    
    # Calculate pricing
    duration = min(max(boost_request.duration_days, MIN_BOOST_DAYS), MAX_BOOST_DAYS)
    amount = BOOST_PRICE_PER_DAY * duration
    
    # Create payment intent with Stripe
    if STRIPE_AVAILABLE and user.stripe_customer_id:
        try:
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                customer=user.stripe_customer_id,
                amount=int(amount * 100),  # Convert to cents
                currency="usd",
                description=f"Boost post #{post.id} for {duration} days",
                metadata={
                    "user_id": user.id,
                    "post_id": post.id,
                    "duration_days": duration,
                }
            )
            
            # Create payment record
            payment = Payment(
                user_id=user.id,
                stripe_payment_id=payment_intent.id,
                amount=amount,
                currency="USD",
                status="pending",
                description=f"Boost post #{post.id} for {duration} days"
            )
            db.add(payment)
            await db.flush()
            
            payment_id = payment.id
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Payment error: {str(e)}"
            )
    else:
        # Create a pending payment record even without Stripe
        payment = Payment(
            user_id=user.id,
            amount=amount,
            currency="USD",
            status="pending",
            description=f"Boost post #{post.id} for {duration} days"
        )
        db.add(payment)
        await db.flush()
        payment_id = payment.id
    
    # Create boost record
    boost_start = datetime.utcnow()
    boost_end = boost_start + timedelta(days=duration)
    
    boosted_post = BoostedPost(
        post_id=post.id,
        user_id=user.id,
        boost_duration_days=duration,
        boost_start=boost_start,
        boost_end=boost_end,
        amount_paid=amount,
        payment_id=payment_id,
        status="active"
    )
    db.add(boosted_post)
    await db.commit()
    await db.refresh(boosted_post)
    
    return BoostPostResponse(
        id=boosted_post.id,
        post_id=boosted_post.post_id,
        boost_duration_days=boosted_post.boost_duration_days,
        boost_start=boosted_post.boost_start,
        boost_end=boosted_post.boost_end,
        amount_paid=boosted_post.amount_paid,
        status=boosted_post.status,
        checkout_url=None  # Payment intent would have confirmation URL
    )


# ============================================================================
# GET BOOSTED POSTS
# ============================================================================

@router.get("/active", response_model=List[BoostedPostStats])
async def get_active_boosts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's active boosted posts
    
    Returns statistics for all active boosts
    """
    result = await db.execute(
        select(BoostedPost)
        .where(
            and_(
                BoostedPost.user_id == user.id,
                BoostedPost.status == "active",
                BoostedPost.boost_end > datetime.utcnow()
            )
        )
        .order_by(desc(BoostedPost.created_at))
    )
    boosts = result.scalars().all()
    
    # Calculate ROI for each boost
    stats = []
    for boost in boosts:
        roi = None
        if boost.amount_paid > 0 and boost.clicks > 0:
            # Simple ROI calculation: (clicks * avg_value - cost) / cost
            # Assuming each click is worth $1 for simplicity
            roi = ((boost.clicks * 1.0) - boost.amount_paid) / boost.amount_paid * 100
        
        stats.append(BoostedPostStats(
            id=boost.id,
            post_id=boost.post_id,
            impressions=boost.impressions,
            clicks=boost.clicks,
            boost_end=boost.boost_end,
            status=boost.status,
            roi=roi
        ))
    
    return stats


@router.get("/history", response_model=List[BoostedPostStats])
async def get_boost_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20
):
    """
    Get user's boost history
    
    Returns past and current boosts with performance metrics
    """
    result = await db.execute(
        select(BoostedPost)
        .where(BoostedPost.user_id == user.id)
        .order_by(desc(BoostedPost.created_at))
        .limit(limit)
    )
    boosts = result.scalars().all()
    
    stats = []
    for boost in boosts:
        roi = None
        if boost.amount_paid > 0 and boost.clicks > 0:
            roi = ((boost.clicks * 1.0) - boost.amount_paid) / boost.amount_paid * 100
        
        stats.append(BoostedPostStats(
            id=boost.id,
            post_id=boost.post_id,
            impressions=boost.impressions,
            clicks=boost.clicks,
            boost_end=boost.boost_end,
            status=boost.status,
            roi=roi
        ))
    
    return stats


# ============================================================================
# CANCEL BOOST
# ============================================================================

@router.delete("/{boost_id}")
async def cancel_boost(
    boost_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel an active boost
    
    Note: No refunds for partial cancellations
    """
    boost = await db.get(BoostedPost, boost_id)
    
    if not boost:
        raise HTTPException(status_code=404, detail="Boost not found")
    
    if boost.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only cancel your own boosts"
        )
    
    if boost.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Boost is not active"
        )
    
    boost.status = "cancelled"
    boost.boost_end = datetime.utcnow()
    await db.commit()
    
    return {"message": "Boost cancelled successfully"}


# ============================================================================
# TRACK BOOST PERFORMANCE (Internal API - Authenticated)
# ============================================================================

@router.post("/{boost_id}/impression")
async def track_impression(
    boost_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track impression for boosted post
    
    Called when a boosted post is displayed to a user
    Requires authentication to prevent abuse
    """
    # Use atomic update to prevent race conditions
    stmt = (
        update(BoostedPost)
        .where(
            and_(
                BoostedPost.id == boost_id,
                BoostedPost.status == "active"
            )
        )
        .values(impressions=BoostedPost.impressions + 1)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    if result.rowcount == 0:
        return {"status": "ignored"}
    
    return {"status": "tracked"}


@router.post("/{boost_id}/click")
async def track_click(
    boost_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track click for boosted post
    
    Called when a user clicks on a boosted post
    Requires authentication to prevent abuse
    """
    # Use atomic update to prevent race conditions
    stmt = (
        update(BoostedPost)
        .where(
            and_(
                BoostedPost.id == boost_id,
                BoostedPost.status == "active"
            )
        )
        .values(clicks=BoostedPost.clicks + 1)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    if result.rowcount == 0:
        return {"status": "ignored"}
    
    return {"status": "tracked"}
