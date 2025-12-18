"""
Pydantic schemas for subscription-related requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class SubscriptionUpgradeRequest(BaseModel):
    """Request model for upgrading subscription"""
    plan: str = Field(..., description="Subscription plan to upgrade to")

    @validator("plan")
    def validate_plan(cls, v):
        """Validate that plan is one of the allowed values"""
        allowed_plans = ["pro", "business", "enterprise"]
        if v.lower() not in allowed_plans:
            raise ValueError(f"Plan must be one of: {', '.join(allowed_plans)}")
        return v.lower()


class PlanFeatures(BaseModel):
    """Features included in a subscription plan"""
    name: str
    price: Optional[float]
    price_display: str
    billing_period: Optional[str]
    features: List[str]
    limits: Dict[str, int]


class SubscriptionPlansResponse(BaseModel):
    """Response model for subscription plans"""
    plans: Dict[str, PlanFeatures]


class CurrentSubscriptionResponse(BaseModel):
    """Response model for current subscription"""
    plan: str
    status: str
    end_date: Optional[datetime]
    plan_info: PlanFeatures
    is_pro: bool


class SubscriptionUpgradeResponse(BaseModel):
    """Response model for subscription upgrade"""
    message: str
    plan: str
    status: str
    end_date: Optional[datetime]
    plan_info: PlanFeatures


class SubscriptionCancelResponse(BaseModel):
    """Response model for subscription cancellation"""
    message: str
    plan: str
    status: str
