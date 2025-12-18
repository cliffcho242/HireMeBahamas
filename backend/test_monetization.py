"""Tests for monetization system"""
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.models import (
    Subscription, SubscriptionTier, JobPostingPackage, 
    BoostedPost, Advertisement, EnterpriseAccount
)


def test_subscription_tier_enum():
    """Test subscription tier enum values"""
    assert SubscriptionTier.FREE == "free"
    assert SubscriptionTier.BASIC == "basic"
    assert SubscriptionTier.PROFESSIONAL == "professional"
    assert SubscriptionTier.BUSINESS == "business"
    assert SubscriptionTier.ENTERPRISE == "enterprise"


def test_subscription_model_creation():
    """Test Subscription model can be instantiated"""
    now = datetime.utcnow()
    subscription = Subscription(
        user_id=1,
        tier=SubscriptionTier.PROFESSIONAL,
        price_paid=49.99,
        starts_at=now,
        expires_at=now + timedelta(days=30),
        is_active=True,
        auto_renew=True
    )
    
    assert subscription.user_id == 1
    assert subscription.tier == SubscriptionTier.PROFESSIONAL
    assert subscription.price_paid == 49.99
    assert subscription.is_active is True
    assert subscription.auto_renew is True


def test_job_posting_package_model():
    """Test JobPostingPackage model"""
    package = JobPostingPackage(
        user_id=1,
        package_name="20 Job Posts",
        credits_purchased=20,
        credits_remaining=20,
        price_paid=149.99
    )
    
    assert package.user_id == 1
    assert package.credits_purchased == 20
    assert package.credits_remaining == 20
    assert package.price_paid == 149.99


def test_boosted_post_model():
    """Test BoostedPost model"""
    now = datetime.utcnow()
    boosted = BoostedPost(
        post_id=1,
        user_id=1,
        boost_type="national",
        price_paid=29.99,
        impressions_target=5000,
        impressions_actual=0,
        starts_at=now,
        expires_at=now + timedelta(days=7),
        is_active=True
    )
    
    assert boosted.post_id == 1
    assert boosted.boost_type == "national"
    assert boosted.price_paid == 29.99
    assert boosted.impressions_target == 5000


def test_advertisement_model():
    """Test Advertisement model"""
    now = datetime.utcnow()
    ad = Advertisement(
        user_id=1,
        title="Hiring Software Engineers",
        description="Join our team",
        link_url="https://example.com/jobs",
        ad_type="banner",
        budget_total=500.0,
        budget_spent=0.0,
        starts_at=now,
        expires_at=now + timedelta(days=30),
        is_active=False,
        is_approved=False
    )
    
    assert ad.user_id == 1
    assert ad.title == "Hiring Software Engineers"
    assert ad.budget_total == 500.0
    assert ad.is_active is False
    assert ad.is_approved is False


def test_enterprise_account_model():
    """Test EnterpriseAccount model"""
    now = datetime.utcnow()
    enterprise = EnterpriseAccount(
        user_id=1,
        company_name="Tech Corp Bahamas",
        contract_value=50000.0,
        starts_at=now,
        expires_at=now + timedelta(days=365),
        max_job_posts=None,  # Unlimited
        max_users=50,
        dedicated_support=True,
        custom_branding=True,
        api_access=True,
        analytics_access=True,
        is_active=True
    )
    
    assert enterprise.user_id == 1
    assert enterprise.company_name == "Tech Corp Bahamas"
    assert enterprise.contract_value == 50000.0
    assert enterprise.max_job_posts is None  # Unlimited
    assert enterprise.dedicated_support is True


if __name__ == "__main__":
    # Run tests
    test_subscription_tier_enum()
    test_subscription_model_creation()
    test_job_posting_package_model()
    test_boosted_post_model()
    test_advertisement_model()
    test_enterprise_account_model()
    print("✅ All monetization model tests passed!")
