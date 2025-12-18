"""
Subscription API endpoints for managing user subscriptions and plans.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models import User


router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


# Subscription plan definitions
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "price_display": "$0",
        "billing_period": None,
        "features": [
            "Basic job search",
            "Limited applications (5 per month)",
            "Basic profile",
            "Email support",
        ],
        "limits": {
            "job_applications": 5,
            "job_posts": 1,
            "messages": 20,
        }
    },
    "pro": {
        "name": "Pro",
        "price": 9.99,
        "price_display": "$9.99/mo",
        "billing_period": "monthly",
        "features": [
            "Unlimited job applications",
            "Priority in search results",
            "Advanced profile customization",
            "Resume builder",
            "Priority support",
            "Job alerts",
        ],
        "limits": {
            "job_applications": -1,  # unlimited
            "job_posts": 5,
            "messages": -1,  # unlimited
        }
    },
    "business": {
        "name": "Business",
        "price": 29.99,
        "price_display": "$29.99/mo",
        "billing_period": "monthly",
        "features": [
            "Everything in Pro",
            "Post unlimited jobs",
            "Featured job listings",
            "Company page",
            "Analytics dashboard",
            "API access",
            "Dedicated support",
        ],
        "limits": {
            "job_applications": -1,  # unlimited
            "job_posts": -1,  # unlimited
            "messages": -1,  # unlimited
            "featured_jobs": 3,
        }
    },
    "enterprise": {
        "name": "Enterprise",
        "price": None,
        "price_display": "Custom",
        "billing_period": "custom",
        "features": [
            "Everything in Business",
            "Custom integrations",
            "White-label options",
            "Dedicated account manager",
            "SLA guarantee",
            "Custom contracts",
            "Advanced analytics",
        ],
        "limits": {
            "job_applications": -1,
            "job_posts": -1,
            "messages": -1,
            "featured_jobs": -1,
        }
    },
}


@router.get("/plans")
async def get_subscription_plans():
    """
    Get all available subscription plans.
    Public endpoint - no authentication required.
    """
    return {
        "plans": SUBSCRIPTION_PLANS
    }


@router.get("/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
):
    """
    Get the current user's subscription information.
    """
    plan_info = SUBSCRIPTION_PLANS.get(current_user.subscription_plan, SUBSCRIPTION_PLANS["free"])
    
    return {
        "plan": current_user.subscription_plan,
        "status": current_user.subscription_status,
        "end_date": current_user.subscription_end_date,
        "plan_info": plan_info,
        "is_pro": current_user.is_pro,
    }


@router.post("/upgrade")
async def upgrade_subscription(
    plan: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upgrade user subscription to a new plan.
    
    In a production environment, this would integrate with a payment processor
    like Stripe. For now, it's a simple plan change.
    """
    # Validate plan
    if plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {plan}. Must be one of: free, pro, business, enterprise"
        )
    
    # Don't allow downgrade to free through this endpoint
    if plan == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use the cancel endpoint to downgrade to free plan"
        )
    
    # Check if user is already on this plan
    if current_user.subscription_plan == plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are already subscribed to the {plan} plan"
        )
    
    # Update user subscription
    current_user.subscription_plan = plan
    current_user.subscription_status = "active"
    
    # Set end date to 30 days from now (or custom for enterprise)
    if plan == "enterprise":
        # Enterprise typically has custom contracts
        current_user.subscription_end_date = None
    else:
        current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
    
    await db.commit()
    await db.refresh(current_user)
    
    plan_info = SUBSCRIPTION_PLANS[plan]
    
    return {
        "message": f"Successfully upgraded to {plan_info['name']} plan",
        "plan": plan,
        "status": current_user.subscription_status,
        "end_date": current_user.subscription_end_date,
        "plan_info": plan_info,
    }


@router.post("/cancel")
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel current subscription and downgrade to free plan.
    """
    if current_user.subscription_plan == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already on the free plan"
        )
    
    # Update to free plan
    current_user.subscription_plan = "free"
    current_user.subscription_status = "cancelled"
    current_user.subscription_end_date = None
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "message": "Subscription cancelled successfully. You have been moved to the free plan.",
        "plan": "free",
        "status": "cancelled",
    }


def require_pro_subscription(user: User = Depends(get_current_user)) -> User:
    """
    Dependency to check if user has a Pro or higher subscription.
    Use this as a dependency on premium endpoints.
    
    Example:
        @router.get("/premium-feature")
        async def premium_feature(user: User = Depends(require_pro_subscription)):
            # Only pro+ users can access this
            pass
    """
    if not user.is_pro:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Upgrade required. This feature requires a Pro subscription or higher."
        )
    return user


def require_business_subscription(user: User = Depends(get_current_user)) -> User:
    """
    Dependency to check if user has a Business or higher subscription.
    """
    if user.subscription_plan not in ["business", "enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Upgrade required. This feature requires a Business subscription or higher."
        )
    return user


def require_enterprise_subscription(user: User = Depends(get_current_user)) -> User:
    """
    Dependency to check if user has an Enterprise subscription.
    """
    if user.subscription_plan != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Upgrade required. This feature requires an Enterprise subscription."
        )
    return user
