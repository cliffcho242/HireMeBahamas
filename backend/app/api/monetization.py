"""API endpoints for monetization system"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.auth import get_current_user
from app.database import get_db
from app.models import (
    User, Subscription, JobPostingPackage, BoostedPost, 
    Advertisement, EnterpriseAccount, SubscriptionTier
)
from app.schemas.monetization import (
    SubscriptionResponse, SubscriptionCreate, SubscriptionUpdate,
    JobPostingPackageResponse, JobPostingPackageCreate,
    BoostedPostResponse, BoostedPostCreate,
    AdvertisementResponse, AdvertisementCreate, AdvertisementUpdate,
    EnterpriseAccountResponse, EnterpriseAccountCreate, EnterpriseAccountUpdate,
    PricingResponse, PricingTierInfo, SubscriptionTierEnum
)

router = APIRouter(tags=["monetization"])


# =============================================================================
# PRICING INFORMATION
# =============================================================================

@router.get("/pricing", response_model=PricingResponse)
def get_pricing_info():
    """Get all pricing information for the platform"""
    
    subscription_tiers = [
        PricingTierInfo(
            tier=SubscriptionTierEnum.FREE,
            name="Free",
            monthly_price=0,
            annual_price=0,
            features=[
                "Basic profile",
                "Apply to jobs",
                "1 job post per month",
                "Standard support"
            ],
            job_posts_per_month=1,
            recommended=False
        ),
        PricingTierInfo(
            tier=SubscriptionTierEnum.BASIC,
            name="Basic",
            monthly_price=19.99,
            annual_price=199.99,
            features=[
                "Enhanced profile",
                "Apply to unlimited jobs",
                "5 job posts per month",
                "Priority support",
                "Basic analytics"
            ],
            job_posts_per_month=5,
            recommended=False
        ),
        PricingTierInfo(
            tier=SubscriptionTierEnum.PROFESSIONAL,
            name="Professional",
            monthly_price=49.99,
            annual_price=499.99,
            features=[
                "Premium profile with verification badge",
                "Unlimited job applications",
                "20 job posts per month",
                "Featured profile in search",
                "Advanced analytics",
                "Priority support"
            ],
            job_posts_per_month=20,
            recommended=True
        ),
        PricingTierInfo(
            tier=SubscriptionTierEnum.BUSINESS,
            name="Business",
            monthly_price=99.99,
            annual_price=999.99,
            features=[
                "Everything in Professional",
                "50 job posts per month",
                "Company branding",
                "Team collaboration (up to 5 users)",
                "Dedicated account manager",
                "API access"
            ],
            job_posts_per_month=50,
            recommended=False
        ),
        PricingTierInfo(
            tier=SubscriptionTierEnum.ENTERPRISE,
            name="Enterprise",
            monthly_price=0,  # Custom pricing
            annual_price=0,
            features=[
                "Everything in Business",
                "Unlimited job posts",
                "Unlimited team members",
                "Custom branding and white-label options",
                "Dedicated support team",
                "SLA guarantees",
                "Custom integrations"
            ],
            job_posts_per_month=999999,
            recommended=False
        )
    ]
    
    job_posting_packages = [
        {
            "name": "5 Job Posts",
            "credits": 5,
            "price": 49.99,
            "price_per_post": 9.99,
            "expires_in_days": 90
        },
        {
            "name": "20 Job Posts",
            "credits": 20,
            "price": 149.99,
            "price_per_post": 7.49,
            "expires_in_days": 180,
            "popular": True
        },
        {
            "name": "50 Job Posts",
            "credits": 50,
            "price": 299.99,
            "price_per_post": 5.99,
            "expires_in_days": 365
        }
    ]
    
    boost_options = [
        {
            "type": "local",
            "name": "Local Boost",
            "description": "Boost your post to users in your area",
            "price": 9.99,
            "duration_days": 7,
            "estimated_impressions": "500-1,000"
        },
        {
            "type": "national",
            "name": "National Boost",
            "description": "Boost your post nationwide across the Bahamas",
            "price": 29.99,
            "duration_days": 7,
            "estimated_impressions": "2,000-5,000",
            "popular": True
        },
        {
            "type": "featured",
            "name": "Featured",
            "description": "Feature your post on the homepage and in feeds",
            "price": 49.99,
            "duration_days": 14,
            "estimated_impressions": "10,000+"
        }
    ]
    
    return PricingResponse(
        subscription_tiers=subscription_tiers,
        job_posting_packages=job_posting_packages,
        boost_options=boost_options
    )


# =============================================================================
# SUBSCRIPTION ENDPOINTS
# =============================================================================

@router.get("/subscriptions/me", response_model=SubscriptionResponse)
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        # Create free tier subscription if none exists
        subscription = Subscription(
            user_id=current_user.id,
            tier=SubscriptionTier.FREE,
            is_active=True
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return subscription


@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or upgrade a subscription (admin/payment webhook endpoint)"""
    
    # Use authenticated user's ID for security
    user_id = current_user.id
    
    # Check if subscription already exists
    existing = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription already exists. Use update endpoint."
        )
    
    # Set expiry based on tier (example: 30 days for paid tiers)
    expires_at = None
    if subscription_data.tier != SubscriptionTierEnum.FREE:
        expires_at = datetime.utcnow() + timedelta(days=30)
    
    subscription = Subscription(
        user_id=user_id,
        tier=subscription_data.tier,
        price_paid=subscription_data.price_paid,
        expires_at=expires_at,
        is_active=True,
        auto_renew=subscription_data.auto_renew
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.put("/subscriptions/me", response_model=SubscriptionResponse)
def update_my_subscription(
    subscription_update: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's subscription"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Update fields
    if subscription_update.tier is not None:
        subscription.tier = subscription_update.tier
    if subscription_update.auto_renew is not None:
        subscription.auto_renew = subscription_update.auto_renew
    if subscription_update.is_active is not None:
        subscription.is_active = subscription_update.is_active
    
    subscription.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(subscription)
    
    return subscription


# =============================================================================
# JOB POSTING PACKAGES
# =============================================================================

@router.get("/job-packages/me", response_model=List[JobPostingPackageResponse])
def get_my_job_packages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's job posting packages"""
    packages = db.query(JobPostingPackage).filter(
        JobPostingPackage.user_id == current_user.id,
        JobPostingPackage.credits_remaining > 0
    ).order_by(JobPostingPackage.purchased_at.desc()).all()
    
    return packages


@router.post("/job-packages", response_model=JobPostingPackageResponse, status_code=status.HTTP_201_CREATED)
def purchase_job_package(
    package_data: JobPostingPackageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Purchase a job posting package (payment webhook endpoint)"""
    
    # Use authenticated user's ID for security
    package = JobPostingPackage(
        user_id=current_user.id,
        package_name=package_data.package_name,
        credits_purchased=package_data.credits_purchased,
        credits_remaining=package_data.credits_purchased,
        price_paid=package_data.price_paid,
        expires_at=package_data.expires_at
    )
    
    db.add(package)
    db.commit()
    db.refresh(package)
    
    return package


@router.post("/job-packages/{package_id}/use-credit")
def use_job_credit(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use one credit from a job posting package"""
    
    package = db.query(JobPostingPackage).filter(
        JobPostingPackage.id == package_id,
        JobPostingPackage.user_id == current_user.id
    ).first()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    if package.credits_remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No credits remaining in this package"
        )
    
    if package.expires_at and package.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Package has expired"
        )
    
    package.credits_remaining -= 1
    db.commit()
    
    return {"message": "Credit used successfully", "credits_remaining": package.credits_remaining}


# =============================================================================
# BOOSTED POSTS
# =============================================================================

@router.get("/boosted-posts/me", response_model=List[BoostedPostResponse])
def get_my_boosted_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's boosted posts"""
    boosted = db.query(BoostedPost).filter(
        BoostedPost.user_id == current_user.id
    ).order_by(BoostedPost.created_at.desc()).all()
    
    return boosted


@router.post("/boosted-posts", response_model=BoostedPostResponse, status_code=status.HTTP_201_CREATED)
def create_boosted_post(
    boost_data: BoostedPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Boost a post (payment webhook endpoint)"""
    
    # Use authenticated user's ID for security
    boosted = BoostedPost(
        post_id=boost_data.post_id,
        user_id=current_user.id,
        boost_type=boost_data.boost_type,
        price_paid=boost_data.price_paid,
        impressions_target=boost_data.impressions_target,
        expires_at=boost_data.expires_at,
        is_active=True
    )
    
    db.add(boosted)
    db.commit()
    db.refresh(boosted)
    
    return boosted


@router.get("/boosted-posts/active", response_model=List[BoostedPostResponse])
def get_active_boosted_posts(
    db: Session = Depends(get_db)
):
    """Get all active boosted posts (for feed prioritization)"""
    now = datetime.utcnow()
    boosted = db.query(BoostedPost).filter(
        BoostedPost.is_active.is_(True),
        BoostedPost.expires_at > now
    ).all()
    
    return boosted


# =============================================================================
# ADVERTISEMENTS
# =============================================================================

@router.get("/ads/me", response_model=List[AdvertisementResponse])
def get_my_ads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's advertisements"""
    ads = db.query(Advertisement).filter(
        Advertisement.user_id == current_user.id
    ).order_by(Advertisement.created_at.desc()).all()
    
    return ads


@router.post("/ads", response_model=AdvertisementResponse, status_code=status.HTTP_201_CREATED)
def create_advertisement(
    ad_data: AdvertisementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new advertisement"""
    
    # Use authenticated user's ID for security
    ad = Advertisement(
        user_id=current_user.id,
        title=ad_data.title,
        description=ad_data.description,
        image_url=ad_data.image_url,
        link_url=ad_data.link_url,
        ad_type=ad_data.ad_type,
        targeting_location=ad_data.targeting_location,
        targeting_category=ad_data.targeting_category,
        budget_total=ad_data.budget_total,
        cost_per_click=ad_data.cost_per_click,
        cost_per_impression=ad_data.cost_per_impression,
        starts_at=ad_data.starts_at,
        expires_at=ad_data.expires_at,
        is_active=False,  # Requires approval
        is_approved=False
    )
    
    db.add(ad)
    db.commit()
    db.refresh(ad)
    
    return ad


@router.put("/ads/{ad_id}", response_model=AdvertisementResponse)
def update_advertisement(
    ad_id: int,
    ad_update: AdvertisementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an advertisement"""
    
    ad = db.query(Advertisement).filter(
        Advertisement.id == ad_id,
        Advertisement.user_id == current_user.id
    ).first()
    
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advertisement not found"
        )
    
    # Update fields
    for field, value in ad_update.dict(exclude_unset=True).items():
        setattr(ad, field, value)
    
    ad.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ad)
    
    return ad


@router.get("/ads/active", response_model=List[AdvertisementResponse])
def get_active_ads(
    ad_type: str = None,
    location: str = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get active advertisements (for display on platform)"""
    now = datetime.utcnow()
    
    query = db.query(Advertisement).filter(
        Advertisement.is_active.is_(True),
        Advertisement.is_approved.is_(True),
        Advertisement.starts_at <= now,
        Advertisement.expires_at > now,
        Advertisement.budget_spent < Advertisement.budget_total
    )
    
    if ad_type:
        query = query.filter(Advertisement.ad_type == ad_type)
    if location:
        query = query.filter(
            or_(
                Advertisement.targeting_location == location,
                Advertisement.targeting_location.is_(None)
            )
        )
    if category:
        query = query.filter(
            or_(
                Advertisement.targeting_category == category,
                Advertisement.targeting_category.is_(None)
            )
        )
    
    ads = query.all()
    return ads


@router.post("/ads/{ad_id}/impression")
def record_ad_impression(
    ad_id: int,
    db: Session = Depends(get_db)
):
    """Record an impression for an advertisement"""
    
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advertisement not found"
        )
    
    ad.impressions += 1
    
    # Track cost if CPM pricing
    if ad.cost_per_impression:
        ad.budget_spent += ad.cost_per_impression
    
    db.commit()
    
    return {"message": "Impression recorded"}


@router.post("/ads/{ad_id}/click")
def record_ad_click(
    ad_id: int,
    db: Session = Depends(get_db)
):
    """Record a click for an advertisement"""
    
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advertisement not found"
        )
    
    ad.clicks += 1
    
    # Track cost if CPC pricing
    if ad.cost_per_click:
        ad.budget_spent += ad.cost_per_click
    
    db.commit()
    
    return {"message": "Click recorded"}


# =============================================================================
# ENTERPRISE ACCOUNTS
# =============================================================================

@router.get("/enterprise/me", response_model=EnterpriseAccountResponse)
def get_my_enterprise_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's enterprise account"""
    
    enterprise = db.query(EnterpriseAccount).filter(
        EnterpriseAccount.user_id == current_user.id
    ).first()
    
    if not enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise account not found"
        )
    
    return enterprise


@router.post("/enterprise", response_model=EnterpriseAccountResponse, status_code=status.HTTP_201_CREATED)
def create_enterprise_account(
    enterprise_data: EnterpriseAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an enterprise account (admin only)"""
    
    # Check if already exists
    existing = db.query(EnterpriseAccount).filter(
        EnterpriseAccount.user_id == enterprise_data.user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise account already exists"
        )
    
    enterprise = EnterpriseAccount(
        user_id=enterprise_data.user_id,
        company_name=enterprise_data.company_name,
        contract_value=enterprise_data.contract_value,
        starts_at=enterprise_data.starts_at,
        expires_at=enterprise_data.expires_at,
        max_job_posts=enterprise_data.max_job_posts,
        max_users=enterprise_data.max_users,
        dedicated_support=enterprise_data.dedicated_support,
        custom_branding=enterprise_data.custom_branding,
        api_access=enterprise_data.api_access,
        analytics_access=enterprise_data.analytics_access,
        account_manager=enterprise_data.account_manager,
        notes=enterprise_data.notes,
        is_active=True
    )
    
    db.add(enterprise)
    db.commit()
    db.refresh(enterprise)
    
    return enterprise


@router.put("/enterprise/{account_id}", response_model=EnterpriseAccountResponse)
def update_enterprise_account(
    account_id: int,
    enterprise_update: EnterpriseAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an enterprise account (admin only)"""
    
    enterprise = db.query(EnterpriseAccount).filter(
        EnterpriseAccount.id == account_id
    ).first()
    
    if not enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise account not found"
        )
    
    # Update fields
    for field, value in enterprise_update.dict(exclude_unset=True).items():
        setattr(enterprise, field, value)
    
    enterprise.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(enterprise)
    
    return enterprise
