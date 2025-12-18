"""
Create subscription and monetization tables in the database
"""
import asyncio
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import (
    SubscriptionTier,
    UserSubscription,
    Payment,
    FeatureUsage,
    BoostedPost,
    SponsoredContent,
    AnalyticsEvent,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def create_tables():
    """Create all monetization tables"""
    print("Creating monetization tables...")
    
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Tables created successfully")


async def seed_subscription_tiers():
    """Seed default subscription tiers"""
    print("Seeding subscription tiers...")
    
    async with AsyncSession(engine) as session:
        # Check if tiers already exist
        result = await session.execute(select(SubscriptionTier))
        existing_tiers = result.scalars().all()
        
        if existing_tiers:
            print("⚠️  Subscription tiers already exist, skipping seed")
            return
        
        # Define tier features and limits
        tiers = [
            {
                "name": "free",
                "display_name": "Free",
                "price": 0.0,
                "annual_price": 0.0,
                "billing_period": "monthly",
                "description": "Perfect for getting started",
                "features": json.dumps({
                    "unlimited_messaging": False,
                    "unlimited_posts": False,
                    "no_ads": False,
                    "advanced_search": False,
                    "analytics": False,
                    "priority_support": False,
                    "api_access": False,
                    "boost_posts": False,
                    "featured_jobs": False,
                }),
                "limits": json.dumps({
                    "messages_per_month": 10,
                    "posts_per_month": 5,
                    "connections": 100,
                    "inmails_per_month": 0,
                    "job_posts": 1,
                }),
            },
            {
                "name": "pro",
                "display_name": "Pro",
                "price": 9.99,
                "annual_price": 99.0,  # Save 17%
                "billing_period": "monthly",
                "description": "For active job seekers and professionals",
                "features": json.dumps({
                    "unlimited_messaging": True,
                    "unlimited_posts": True,
                    "no_ads": True,
                    "advanced_search": True,
                    "analytics": True,
                    "priority_support": True,
                    "api_access": False,
                    "boost_posts": False,
                    "featured_jobs": False,
                }),
                "limits": json.dumps({
                    "messages_per_month": -1,  # Unlimited
                    "posts_per_month": -1,  # Unlimited
                    "connections": -1,  # Unlimited
                    "inmails_per_month": 5,
                    "job_posts": 3,
                }),
            },
            {
                "name": "business",
                "display_name": "Business",
                "price": 49.99,
                "annual_price": 499.0,  # Save 17%
                "billing_period": "monthly",
                "description": "For employers and recruiters",
                "features": json.dumps({
                    "unlimited_messaging": True,
                    "unlimited_posts": True,
                    "no_ads": True,
                    "advanced_search": True,
                    "analytics": True,
                    "priority_support": True,
                    "api_access": True,
                    "boost_posts": True,
                    "featured_jobs": True,
                    "team_collaboration": True,
                    "applicant_tracking": True,
                }),
                "limits": json.dumps({
                    "messages_per_month": -1,  # Unlimited
                    "posts_per_month": -1,  # Unlimited
                    "connections": -1,  # Unlimited
                    "inmails_per_month": 50,
                    "job_posts": -1,  # Unlimited
                    "team_members": 5,
                }),
            },
            {
                "name": "enterprise",
                "display_name": "Enterprise",
                "price": 500.0,  # Starting price
                "annual_price": 5000.0,
                "billing_period": "monthly",
                "description": "Custom solutions for large organizations",
                "features": json.dumps({
                    "unlimited_messaging": True,
                    "unlimited_posts": True,
                    "no_ads": True,
                    "advanced_search": True,
                    "analytics": True,
                    "priority_support": True,
                    "api_access": True,
                    "boost_posts": True,
                    "featured_jobs": True,
                    "team_collaboration": True,
                    "applicant_tracking": True,
                    "white_label": True,
                    "dedicated_account_manager": True,
                    "sla_guarantee": True,
                }),
                "limits": json.dumps({
                    "messages_per_month": -1,  # Unlimited
                    "posts_per_month": -1,  # Unlimited
                    "connections": -1,  # Unlimited
                    "inmails_per_month": -1,  # Unlimited
                    "job_posts": -1,  # Unlimited
                    "team_members": -1,  # Unlimited
                }),
            },
        ]
        
        # Create tier objects
        for tier_data in tiers:
            tier = SubscriptionTier(**tier_data)
            session.add(tier)
        
        await session.commit()
        print(f"✅ Created {len(tiers)} subscription tiers")


async def main():
    """Main function"""
    try:
        await create_tables()
        await seed_subscription_tiers()
        print("\n✅ Database setup complete!")
        print("\nSubscription tiers created:")
        print("  - Free: $0/month")
        print("  - Pro: $9.99/month ($99/year)")
        print("  - Business: $49.99/month ($499/year)")
        print("  - Enterprise: $500+/month (custom)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
