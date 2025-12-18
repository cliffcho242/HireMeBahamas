"""
Feature gating and usage limit enforcement for monetization
"""
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Callable

from fastapi import HTTPException, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UserSubscription, SubscriptionTier, FeatureUsage


# ============================================================================
# SUBSCRIPTION TIER HIERARCHY
# ============================================================================

TIER_HIERARCHY = {
    "free": 0,
    "pro": 1,
    "business": 2,
    "enterprise": 3,
}


# ============================================================================
# GET USER SUBSCRIPTION
# ============================================================================

async def get_user_subscription(
    user_id: int,
    db: AsyncSession
) -> tuple[str, dict, dict]:
    """
    Get user's subscription tier, features, and limits
    
    Returns:
        tuple: (tier_name, features_dict, limits_dict)
    """
    # Get active subscription
    result = await db.execute(
        select(UserSubscription)
        .join(SubscriptionTier)
        .where(
            and_(
                UserSubscription.user_id == user_id,
                UserSubscription.status == "active"
            )
        )
        .order_by(UserSubscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()
    
    # Default to free tier
    if not subscription:
        return (
            "free",
            {
                "unlimited_messaging": False,
                "unlimited_posts": False,
                "no_ads": False,
                "advanced_search": False,
                "analytics": False,
                "priority_support": False,
                "api_access": False,
            },
            {
                "messages_per_month": 10,
                "posts_per_month": 5,
                "connections": 100,
                "inmails_per_month": 0,
                "job_posts": 1,
            }
        )
    
    # Get tier from subscription
    tier_result = await db.execute(
        select(SubscriptionTier).where(SubscriptionTier.id == subscription.tier_id)
    )
    tier = tier_result.scalar_one()
    
    # Parse JSON features and limits
    features = json.loads(tier.features) if tier.features else {}
    limits = json.loads(tier.limits) if tier.limits else {}
    
    return (tier.name, features, limits)


# ============================================================================
# CHECK FEATURE ACCESS
# ============================================================================

async def check_feature_access(
    user: User,
    feature_name: str,
    db: AsyncSession
) -> bool:
    """
    Check if user has access to a specific feature
    
    Args:
        user: User object
        feature_name: Name of the feature (e.g., 'unlimited_messaging', 'api_access')
        db: Database session
    
    Returns:
        bool: True if user has access, False otherwise
    """
    tier_name, features, _ = await get_user_subscription(user.id, db)
    return features.get(feature_name, False)


# ============================================================================
# CHECK USAGE LIMIT
# ============================================================================

async def check_usage_limit(
    user_id: int,
    feature: str,
    limit_key: str,
    db: AsyncSession
) -> tuple[bool, int, int]:
    """
    Check if user has reached usage limit for a feature
    
    Args:
        user_id: User ID
        feature: Feature name (e.g., 'messages', 'posts')
        limit_key: Limit key from subscription (e.g., 'messages_per_month')
        db: Database session
    
    Returns:
        tuple: (can_use, current_usage, limit)
    """
    # Get user's subscription limits
    tier_name, _, limits = await get_user_subscription(user_id, db)
    
    # Get limit for this feature
    limit = limits.get(limit_key, 0)
    
    # -1 means unlimited
    if limit == -1:
        return (True, 0, -1)
    
    # Get current usage for this period
    period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    result = await db.execute(
        select(FeatureUsage)
        .where(
            and_(
                FeatureUsage.user_id == user_id,
                FeatureUsage.feature == feature,
                FeatureUsage.period_start >= period_start,
                FeatureUsage.period_end <= period_end
            )
        )
    )
    usage = result.scalar_one_or_none()
    
    current_usage = usage.usage_count if usage else 0
    can_use = current_usage < limit
    
    return (can_use, current_usage, limit)


# ============================================================================
# INCREMENT USAGE
# ============================================================================

async def increment_usage(
    user_id: int,
    feature: str,
    db: AsyncSession,
    amount: int = 1
):
    """
    Increment usage count for a feature
    
    Args:
        user_id: User ID
        feature: Feature name (e.g., 'messages', 'posts')
        db: Database session
        amount: Amount to increment by (default 1)
    """
    # Get current period
    period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    # Get or create usage record
    result = await db.execute(
        select(FeatureUsage)
        .where(
            and_(
                FeatureUsage.user_id == user_id,
                FeatureUsage.feature == feature,
                FeatureUsage.period_start >= period_start,
                FeatureUsage.period_end <= period_end
            )
        )
    )
    usage = result.scalar_one_or_none()
    
    if usage:
        usage.usage_count += amount
        usage.updated_at = datetime.utcnow()
    else:
        usage = FeatureUsage(
            user_id=user_id,
            feature=feature,
            usage_count=amount,
            period_start=period_start,
            period_end=period_end
        )
        db.add(usage)
    
    await db.commit()


# ============================================================================
# DECORATORS
# ============================================================================

def require_subscription(required_tier: str):
    """
    Decorator to require a specific subscription tier
    
    Usage:
        @router.post("/premium-feature")
        @require_subscription("pro")
        async def premium_feature(user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user and db from kwargs
            user = kwargs.get("user")
            db = kwargs.get("db")
            
            if not user or not db:
                raise HTTPException(
                    status_code=500,
                    detail="Internal error: user or db not provided"
                )
            
            # Get user's subscription
            tier_name, _, _ = await get_user_subscription(user.id, db)
            
            # Check tier hierarchy
            user_tier_level = TIER_HIERARCHY.get(tier_name, 0)
            required_tier_level = TIER_HIERARCHY.get(required_tier, 0)
            
            if user_tier_level < required_tier_level:
                raise HTTPException(
                    status_code=403,
                    detail=f"This feature requires {required_tier.title()} subscription or higher"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_feature(feature_name: str):
    """
    Decorator to require access to a specific feature
    
    Usage:
        @router.post("/advanced-search")
        @require_feature("advanced_search")
        async def advanced_search(user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            db = kwargs.get("db")
            
            if not user or not db:
                raise HTTPException(
                    status_code=500,
                    detail="Internal error: user or db not provided"
                )
            
            # Check feature access
            has_access = await check_feature_access(user, feature_name, db)
            
            if not has_access:
                raise HTTPException(
                    status_code=403,
                    detail=f"This feature is not available in your subscription plan. Please upgrade to access {feature_name.replace('_', ' ')}."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_limit(feature: str, limit_key: str):
    """
    Decorator to check usage limits for a feature
    
    Usage:
        @router.post("/send-message")
        @check_limit("messages", "messages_per_month")
        async def send_message(user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            db = kwargs.get("db")
            
            if not user or not db:
                raise HTTPException(
                    status_code=500,
                    detail="Internal error: user or db not provided"
                )
            
            # Check usage limit
            can_use, current_usage, limit = await check_usage_limit(
                user.id, feature, limit_key, db
            )
            
            if not can_use:
                raise HTTPException(
                    status_code=403,
                    detail=f"You've reached your {feature} limit ({current_usage}/{limit} used this month). Please upgrade your subscription to continue."
                )
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Increment usage after successful execution
            await increment_usage(user.id, feature, db)
            
            return result
        return wrapper
    return decorator


# ============================================================================
# HELPER FUNCTIONS FOR MANUAL CHECKS
# ============================================================================

async def require_tier_access(
    user: User,
    required_tier: str,
    db: AsyncSession
):
    """
    Manually check tier access (for use in route functions)
    """
    tier_name, _, _ = await get_user_subscription(user.id, db)
    user_tier_level = TIER_HIERARCHY.get(tier_name, 0)
    required_tier_level = TIER_HIERARCHY.get(required_tier, 0)
    
    if user_tier_level < required_tier_level:
        raise HTTPException(
            status_code=403,
            detail=f"This feature requires {required_tier.title()} subscription or higher"
        )


async def enforce_usage_limit(
    user: User,
    feature: str,
    limit_key: str,
    db: AsyncSession
):
    """
    Manually enforce usage limit (for use in route functions)
    
    Raises HTTPException if limit exceeded, otherwise increments usage
    """
    can_use, current_usage, limit = await check_usage_limit(
        user.id, feature, limit_key, db
    )
    
    if not can_use:
        raise HTTPException(
            status_code=403,
            detail=f"You've reached your {feature} limit ({current_usage}/{limit} used this month). Please upgrade your subscription to continue."
        )
    
    # Increment usage
    await increment_usage(user.id, feature, db)
