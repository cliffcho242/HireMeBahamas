"""
Monetization Analytics API - Track conversions, usage, and revenue metrics
"""
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models import (
    User, UserSubscription, Payment, FeatureUsage,
    BoostedPost, AnalyticsEvent, SubscriptionTier
)
from app.schemas.subscription import (
    AnalyticsEventCreate,
    ConversionMetrics,
    BoostROIMetrics,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ============================================================================
# TRACK ANALYTICS EVENTS
# ============================================================================

@router.post("/track")
async def track_event(
    event: AnalyticsEventCreate,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track analytics event (conversion, paywall view, etc.)
    
    Events to track:
    - upgrade_clicked
    - paywall_viewed
    - checkout_started
    - checkout_completed
    - subscription_cancelled
    - boost_purchased
    """
    analytics_event = AnalyticsEvent(
        user_id=user.id if user else None,
        event_type=event.event_type,
        event_data=json.dumps(event.event_data) if event.event_data else None,
        session_id=event.session_id,
    )
    db.add(analytics_event)
    await db.commit()
    
    return {"status": "tracked", "event_type": event.event_type}


# ============================================================================
# CONVERSION METRICS (ADMIN ONLY)
# ============================================================================

@router.get("/conversions", response_model=ConversionMetrics)
async def get_conversion_metrics(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get conversion and revenue metrics
    
    Admin only endpoint for business intelligence
    """
    # Check if user is admin
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # Premium users (active subscriptions)
    premium_users_result = await db.execute(
        select(func.count(UserSubscription.id.distinct()))
        .where(UserSubscription.status == "active")
        .join(SubscriptionTier)
        .where(SubscriptionTier.name != "free")
    )
    premium_users = premium_users_result.scalar() or 0
    
    free_users = total_users - premium_users
    
    # Calculate conversion rate
    conversion_rate = (premium_users / total_users * 100) if total_users > 0 else 0
    
    # Calculate MRR (Monthly Recurring Revenue)
    mrr_result = await db.execute(
        select(func.sum(SubscriptionTier.price))
        .join(UserSubscription)
        .where(
            and_(
                UserSubscription.status == "active",
                SubscriptionTier.billing_period == "monthly"
            )
        )
    )
    mrr = float(mrr_result.scalar() or 0)
    
    # Calculate ARPU (Average Revenue Per User)
    arpu = mrr / total_users if total_users > 0 else 0
    
    # Paywall metrics (last N days)
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    paywall_views_result = await db.execute(
        select(func.count(AnalyticsEvent.id))
        .where(
            and_(
                AnalyticsEvent.event_type == "paywall_viewed",
                AnalyticsEvent.created_at >= date_threshold
            )
        )
    )
    paywall_views = paywall_views_result.scalar() or 0
    
    paywall_conversions_result = await db.execute(
        select(func.count(AnalyticsEvent.id))
        .where(
            and_(
                AnalyticsEvent.event_type == "checkout_completed",
                AnalyticsEvent.created_at >= date_threshold
            )
        )
    )
    paywall_conversions = paywall_conversions_result.scalar() or 0
    
    paywall_conversion_rate = (
        (paywall_conversions / paywall_views * 100)
        if paywall_views > 0 else 0
    )
    
    return ConversionMetrics(
        total_users=total_users,
        free_users=free_users,
        premium_users=premium_users,
        conversion_rate=round(conversion_rate, 2),
        mrr=round(mrr, 2),
        arpu=round(arpu, 2),
        paywall_views=paywall_views,
        paywall_conversions=paywall_conversions,
        paywall_conversion_rate=round(paywall_conversion_rate, 2),
    )


# ============================================================================
# BOOST ROI METRICS (USER)
# ============================================================================

@router.get("/boost-roi", response_model=BoostROIMetrics)
async def get_boost_roi(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get boost post ROI metrics for the user
    
    Analyzes user's boosted posts performance
    """
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    # Get user's boosts in period
    result = await db.execute(
        select(BoostedPost)
        .where(
            and_(
                BoostedPost.user_id == user.id,
                BoostedPost.created_at >= date_threshold
            )
        )
    )
    boosts = result.scalars().all()
    
    if not boosts:
        return BoostROIMetrics(
            total_boosts=0,
            total_spent=0.0,
            total_impressions=0,
            total_clicks=0,
            average_ctr=0.0,
            average_roi=0.0,
        )
    
    total_boosts = len(boosts)
    total_spent = sum(boost.amount_paid for boost in boosts)
    total_impressions = sum(boost.impressions for boost in boosts)
    total_clicks = sum(boost.clicks for boost in boosts)
    
    # Calculate CTR (Click-Through Rate)
    average_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    # Calculate ROI (assuming $1 value per click for simplicity)
    # In production, you'd want to track actual conversions
    revenue = total_clicks * 1.0  # $1 per click
    average_roi = ((revenue - total_spent) / total_spent * 100) if total_spent > 0 else 0
    
    return BoostROIMetrics(
        total_boosts=total_boosts,
        total_spent=round(total_spent, 2),
        total_impressions=total_impressions,
        total_clicks=total_clicks,
        average_ctr=round(average_ctr, 2),
        average_roi=round(average_roi, 2),
    )


# ============================================================================
# FEATURE USAGE (USER)
# ============================================================================

@router.get("/usage/{feature}")
async def get_feature_usage(
    feature: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current month's usage for a specific feature
    
    Features:
    - messages
    - posts
    - inmails
    - job_posts
    """
    # Get current period
    period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    # Get usage record
    result = await db.execute(
        select(FeatureUsage)
        .where(
            and_(
                FeatureUsage.user_id == user.id,
                FeatureUsage.feature == feature,
                FeatureUsage.period_start >= period_start,
                FeatureUsage.period_end <= period_end
            )
        )
    )
    usage = result.scalar_one_or_none()
    
    # Get subscription limits
    from app.core.feature_gates import get_user_subscription
    tier_name, features, limits = await get_user_subscription(user.id, db)
    
    # Map feature to limit key
    limit_key_map = {
        "messages": "messages_per_month",
        "posts": "posts_per_month",
        "inmails": "inmails_per_month",
        "job_posts": "job_posts",
    }
    
    limit_key = limit_key_map.get(feature)
    limit = limits.get(limit_key, 0) if limit_key else 0
    
    current_usage = usage.usage_count if usage else 0
    is_unlimited = limit == -1
    
    return {
        "feature": feature,
        "usage": current_usage,
        "limit": "unlimited" if is_unlimited else limit,
        "is_unlimited": is_unlimited,
        "remaining": "unlimited" if is_unlimited else max(0, limit - current_usage),
        "percentage": 0 if is_unlimited else (current_usage / limit * 100 if limit > 0 else 0),
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
    }


# ============================================================================
# REVENUE DASHBOARD (ADMIN ONLY)
# ============================================================================

@router.get("/revenue")
async def get_revenue_metrics(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get revenue metrics and trends
    
    Admin only endpoint for financial reporting
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    # Total revenue in period
    revenue_result = await db.execute(
        select(func.sum(Payment.amount))
        .where(
            and_(
                Payment.status == "succeeded",
                Payment.created_at >= date_threshold
            )
        )
    )
    total_revenue = float(revenue_result.scalar() or 0)
    
    # Revenue by type
    subscription_revenue_result = await db.execute(
        select(func.sum(Payment.amount))
        .where(
            and_(
                Payment.status == "succeeded",
                Payment.subscription_id.isnot(None),
                Payment.created_at >= date_threshold
            )
        )
    )
    subscription_revenue = float(subscription_revenue_result.scalar() or 0)
    
    boost_revenue = total_revenue - subscription_revenue
    
    # Payment count
    payment_count_result = await db.execute(
        select(func.count(Payment.id))
        .where(
            and_(
                Payment.status == "succeeded",
                Payment.created_at >= date_threshold
            )
        )
    )
    payment_count = payment_count_result.scalar() or 0
    
    # Average transaction value
    avg_transaction = total_revenue / payment_count if payment_count > 0 else 0
    
    return {
        "period_days": days,
        "total_revenue": round(total_revenue, 2),
        "subscription_revenue": round(subscription_revenue, 2),
        "boost_revenue": round(boost_revenue, 2),
        "transaction_count": payment_count,
        "average_transaction": round(avg_transaction, 2),
        "daily_average": round(total_revenue / days, 2),
    }


# ============================================================================
# SUBSCRIPTION GROWTH (ADMIN ONLY)
# ============================================================================

@router.get("/growth")
async def get_growth_metrics(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get subscription growth metrics
    
    Admin only endpoint for growth tracking
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get subscription counts by tier
    tier_counts = {}
    
    result = await db.execute(
        select(
            SubscriptionTier.name,
            func.count(UserSubscription.id)
        )
        .join(UserSubscription)
        .where(UserSubscription.status == "active")
        .group_by(SubscriptionTier.name)
    )
    
    for tier_name, count in result:
        tier_counts[tier_name] = count
    
    # Get new subscriptions (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    new_subs_result = await db.execute(
        select(func.count(UserSubscription.id))
        .where(
            and_(
                UserSubscription.status == "active",
                UserSubscription.created_at >= thirty_days_ago
            )
        )
    )
    new_subscriptions = new_subs_result.scalar() or 0
    
    # Get cancelled subscriptions (last 30 days)
    cancelled_result = await db.execute(
        select(func.count(UserSubscription.id))
        .where(
            and_(
                UserSubscription.status == "canceled",
                UserSubscription.updated_at >= thirty_days_ago
            )
        )
    )
    cancelled_subscriptions = cancelled_result.scalar() or 0
    
    # Calculate churn rate
    total_active = sum(tier_counts.values())
    churn_rate = (
        (cancelled_subscriptions / total_active * 100)
        if total_active > 0 else 0
    )
    
    return {
        "tier_distribution": tier_counts,
        "new_subscriptions_30d": new_subscriptions,
        "cancelled_subscriptions_30d": cancelled_subscriptions,
        "net_growth_30d": new_subscriptions - cancelled_subscriptions,
        "churn_rate": round(churn_rate, 2),
    }
