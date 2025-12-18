"""Pydantic schemas for monetization system"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class SubscriptionTierEnum(str, Enum):
    """Subscription tier levels"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


# =============================================================================
# SUBSCRIPTION SCHEMAS
# =============================================================================

class SubscriptionBase(BaseModel):
    tier: SubscriptionTierEnum
    price_paid: Optional[float] = None
    auto_renew: bool = True


class SubscriptionCreate(SubscriptionBase):
    user_id: int


class SubscriptionUpdate(BaseModel):
    tier: Optional[SubscriptionTierEnum] = None
    auto_renew: Optional[bool] = None
    is_active: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    starts_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    payment_provider: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# =============================================================================
# JOB POSTING PACKAGE SCHEMAS
# =============================================================================

class JobPostingPackageBase(BaseModel):
    package_name: str = Field(..., max_length=100)
    credits_purchased: int = Field(..., gt=0)
    price_paid: float = Field(..., gt=0)
    expires_at: Optional[datetime] = None


class JobPostingPackageCreate(JobPostingPackageBase):
    user_id: int


class JobPostingPackageResponse(JobPostingPackageBase):
    id: int
    user_id: int
    credits_remaining: int
    purchased_at: datetime
    payment_provider: Optional[str]
    payment_provider_transaction_id: Optional[str]

    class Config:
        from_attributes = True


# =============================================================================
# BOOSTED POST SCHEMAS
# =============================================================================

class BoostType(str, Enum):
    """Boost types for posts"""
    LOCAL = "local"
    NATIONAL = "national"
    FEATURED = "featured"


class BoostedPostBase(BaseModel):
    boost_type: BoostType
    price_paid: float = Field(..., gt=0)
    impressions_target: Optional[int] = Field(None, gt=0)
    expires_at: datetime


class BoostedPostCreate(BoostedPostBase):
    post_id: int
    user_id: int


class BoostedPostResponse(BoostedPostBase):
    id: int
    post_id: int
    user_id: int
    impressions_actual: int
    starts_at: datetime
    is_active: bool
    payment_provider: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# ADVERTISEMENT SCHEMAS
# =============================================================================

class AdType(str, Enum):
    """Advertisement types"""
    BANNER = "banner"
    SIDEBAR = "sidebar"
    SPONSORED_POST = "sponsored_post"


class AdvertisementBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    image_url: Optional[str] = Field(None, max_length=500)
    link_url: str = Field(..., max_length=500)
    ad_type: AdType
    targeting_location: Optional[str] = Field(None, max_length=200)
    targeting_category: Optional[str] = Field(None, max_length=100)
    budget_total: float = Field(..., gt=0)
    cost_per_click: Optional[float] = Field(None, gt=0)
    cost_per_impression: Optional[float] = Field(None, gt=0)
    starts_at: datetime
    expires_at: datetime

    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        if 'starts_at' in values and v <= values['starts_at']:
            raise ValueError('expires_at must be after starts_at')
        return v


class AdvertisementCreate(AdvertisementBase):
    user_id: int


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    link_url: Optional[str] = Field(None, max_length=500)
    budget_total: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class AdvertisementResponse(AdvertisementBase):
    id: int
    user_id: int
    budget_spent: float
    impressions: int
    clicks: int
    is_active: bool
    is_approved: bool
    payment_provider: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# =============================================================================
# ENTERPRISE ACCOUNT SCHEMAS
# =============================================================================

class EnterpriseAccountBase(BaseModel):
    company_name: str = Field(..., max_length=200)
    contract_value: float = Field(..., gt=0)
    starts_at: datetime
    expires_at: datetime
    max_job_posts: Optional[int] = Field(None, gt=0)
    max_users: Optional[int] = Field(None, gt=0)
    dedicated_support: bool = True
    custom_branding: bool = True
    api_access: bool = True
    analytics_access: bool = True

    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        if 'starts_at' in values and v <= values['starts_at']:
            raise ValueError('expires_at must be after starts_at')
        return v


class EnterpriseAccountCreate(EnterpriseAccountBase):
    user_id: int
    account_manager: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class EnterpriseAccountUpdate(BaseModel):
    contract_value: Optional[float] = Field(None, gt=0)
    expires_at: Optional[datetime] = None
    max_job_posts: Optional[int] = Field(None, gt=0)
    max_users: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    account_manager: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class EnterpriseAccountResponse(EnterpriseAccountBase):
    id: int
    user_id: int
    is_active: bool
    account_manager: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# =============================================================================
# PRICING TIER INFORMATION
# =============================================================================

class PricingTierInfo(BaseModel):
    """Information about a subscription pricing tier"""
    tier: SubscriptionTierEnum
    name: str
    monthly_price: float
    annual_price: float
    features: list[str]
    job_posts_per_month: int
    recommended: bool = False


class PricingResponse(BaseModel):
    """Complete pricing information"""
    subscription_tiers: list[PricingTierInfo]
    job_posting_packages: list[dict]
    boost_options: list[dict]
