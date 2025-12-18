"""
Pydantic schemas for subscription and monetization features
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# SUBSCRIPTION TIER SCHEMAS
# ============================================================================

class SubscriptionTierBase(BaseModel):
    """Base subscription tier schema"""
    name: str = Field(..., description="Tier name (free, pro, business, enterprise)")
    display_name: str = Field(..., description="Display name for UI")
    price: float = Field(0, ge=0, description="Monthly price in USD")
    annual_price: Optional[float] = Field(None, ge=0, description="Annual price (optional)")
    billing_period: str = Field("monthly", description="Billing period (monthly or annual)")
    description: Optional[str] = None
    features: Optional[Dict[str, Any]] = Field(default_factory=dict)
    limits: Optional[Dict[str, int]] = Field(default_factory=dict)


class SubscriptionTierCreate(SubscriptionTierBase):
    """Create subscription tier schema"""
    pass


class SubscriptionTierResponse(SubscriptionTierBase):
    """Subscription tier response schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# USER SUBSCRIPTION SCHEMAS
# ============================================================================

class CheckoutSessionCreate(BaseModel):
    """Create Stripe checkout session"""
    tier_id: int = Field(..., description="Subscription tier ID")
    billing_period: Optional[str] = Field("monthly", description="monthly or annual")


class CheckoutSessionResponse(BaseModel):
    """Checkout session response"""
    checkout_url: str = Field(..., description="Stripe checkout URL")


class UserSubscriptionResponse(BaseModel):
    """User subscription response"""
    id: int
    tier_name: str
    tier_display_name: str
    status: str
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    features: Dict[str, Any]
    limits: Dict[str, int]

    class Config:
        from_attributes = True


class SubscriptionStatusResponse(BaseModel):
    """Simple subscription status response"""
    tier: str = Field(..., description="Current tier (free, pro, business, enterprise)")
    status: str = Field(..., description="Subscription status")
    is_premium: bool = Field(..., description="Whether user has premium subscription")
    features: Dict[str, bool] = Field(default_factory=dict)
    limits: Dict[str, int] = Field(default_factory=dict)


# ============================================================================
# PAYMENT SCHEMAS
# ============================================================================

class PaymentResponse(BaseModel):
    """Payment transaction response"""
    id: int
    amount: float
    currency: str
    status: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# FEATURE USAGE SCHEMAS
# ============================================================================

class FeatureUsageResponse(BaseModel):
    """Feature usage response"""
    feature: str
    usage_count: int
    limit: Optional[int]
    period_start: datetime
    period_end: datetime
    is_limited: bool
    usage_percentage: Optional[float] = None

    class Config:
        from_attributes = True


# ============================================================================
# BOOSTED POST SCHEMAS
# ============================================================================

class BoostPostRequest(BaseModel):
    """Request to boost a post"""
    post_id: int = Field(..., description="Post ID to boost")
    duration_days: int = Field(7, ge=1, le=30, description="Boost duration in days")


class BoostPostResponse(BaseModel):
    """Boost post response"""
    id: int
    post_id: int
    boost_duration_days: int
    boost_start: datetime
    boost_end: datetime
    amount_paid: float
    status: str
    checkout_url: Optional[str] = None  # For payment if needed

    class Config:
        from_attributes = True


class BoostedPostStats(BaseModel):
    """Boosted post statistics"""
    id: int
    post_id: int
    impressions: int
    clicks: int
    boost_end: datetime
    status: str
    roi: Optional[float] = None  # Return on investment metric

    class Config:
        from_attributes = True


# ============================================================================
# SPONSORED CONTENT SCHEMAS
# ============================================================================

class SponsoredContentCreate(BaseModel):
    """Create sponsored content campaign"""
    content_type: str = Field(..., description="Type: job, profile, post")
    content_id: int = Field(..., description="ID of the content to sponsor")
    campaign_name: str = Field(..., description="Campaign name")
    budget: float = Field(..., ge=10, description="Total campaign budget (min $10)")
    duration_days: int = Field(7, ge=1, le=90, description="Campaign duration in days")
    cost_model: str = Field("cpm", description="Cost model: cpm or cpc")
    cost_per_click: Optional[float] = Field(None, ge=0)
    cost_per_impression: Optional[float] = Field(None, ge=0)


class SponsoredContentResponse(BaseModel):
    """Sponsored content response"""
    id: int
    content_type: str
    content_id: int
    campaign_name: str
    budget: float
    start_date: datetime
    end_date: datetime
    status: str
    impressions: int
    clicks: int
    conversions: int
    amount_spent: float

    class Config:
        from_attributes = True


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class AnalyticsEventCreate(BaseModel):
    """Create analytics event"""
    event_type: str = Field(..., description="Event type (e.g., upgrade_clicked, paywall_viewed)")
    event_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    session_id: Optional[str] = None


class ConversionMetrics(BaseModel):
    """Conversion and revenue metrics"""
    total_users: int
    free_users: int
    premium_users: int
    conversion_rate: float
    mrr: float  # Monthly Recurring Revenue
    arpu: float  # Average Revenue Per User
    paywall_views: int
    paywall_conversions: int
    paywall_conversion_rate: float


class BoostROIMetrics(BaseModel):
    """Boost ROI metrics"""
    total_boosts: int
    total_spent: float
    total_impressions: int
    total_clicks: int
    average_ctr: float  # Click-through rate
    average_roi: float
