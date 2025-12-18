# Monetization Implementation Guide

This document provides a comprehensive guide to the monetization features implemented in HireMeBahamas.

## Overview

The platform now includes a complete monetization system with:
- **Subscription tiers** (Free, Pro, Business, Enterprise)
- **Stripe payment integration**
- **Boosted posts** for enhanced visibility
- **Feature gating** and usage limits
- **Analytics tracking** for conversions and ROI

## Architecture

### Backend Components

#### 1. Database Models (`backend/app/models.py`)

**New Models:**
- `SubscriptionTier` - Defines subscription plans with pricing and features
- `UserSubscription` - Links users to their active subscriptions
- `Payment` - Tracks all payment transactions
- `FeatureUsage` - Monitors feature usage for limit enforcement
- `BoostedPost` - Manages boosted post campaigns
- `SponsoredContent` - Handles sponsored ads (future)
- `AnalyticsEvent` - Tracks user events for conversion analysis

**Updated Models:**
- `User` - Added `stripe_customer_id` field
- `Job` - Added `is_featured`, `is_sponsored`, `featured_until` fields

#### 2. API Endpoints

**Subscriptions API** (`backend/app/api/subscriptions.py`)
```
GET    /api/subscriptions/tiers          - List all subscription tiers
POST   /api/subscriptions/checkout       - Create Stripe checkout session
GET    /api/subscriptions/me             - Get user's current subscription
POST   /api/subscriptions/cancel         - Cancel subscription
POST   /api/subscriptions/reactivate     - Reactivate subscription
POST   /api/subscriptions/webhook        - Stripe webhook handler
GET    /api/subscriptions/payments       - Get payment history
```

**Boosts API** (`backend/app/api/boosts.py`)
```
POST   /api/boosts/post                  - Boost a post ($5/day)
GET    /api/boosts/active                - Get active boosts
GET    /api/boosts/history               - Get boost history
DELETE /api/boosts/{id}                  - Cancel boost
POST   /api/boosts/{id}/impression       - Track impression
POST   /api/boosts/{id}/click            - Track click
```

**Analytics API** (`backend/app/api/monetization_analytics.py`)
```
POST   /api/analytics/track              - Track analytics event
GET    /api/analytics/conversions        - Conversion metrics (admin)
GET    /api/analytics/boost-roi          - Boost ROI metrics
GET    /api/analytics/usage/{feature}    - Feature usage stats
GET    /api/analytics/revenue            - Revenue metrics (admin)
GET    /api/analytics/growth             - Growth metrics (admin)
```

#### 3. Feature Gating (`backend/app/core/feature_gates.py`)

**Helper Functions:**
- `get_user_subscription()` - Get user's tier, features, and limits
- `check_feature_access()` - Check if user has access to a feature
- `check_usage_limit()` - Check if user has reached limit
- `increment_usage()` - Increment usage count

**Decorators:**
- `@require_subscription(tier)` - Require minimum subscription tier
- `@require_feature(feature_name)` - Require specific feature access
- `@check_limit(feature, limit_key)` - Enforce usage limits

**Example Usage:**
```python
from app.core.feature_gates import require_subscription, check_limit

@router.post("/premium-search")
@require_subscription("pro")
async def advanced_search(user: User = Depends(get_current_user)):
    # Only Pro+ users can access
    ...

@router.post("/send-message")
@check_limit("messages", "messages_per_month")
async def send_message(user: User = Depends(get_current_user)):
    # Enforces message limits for Free users
    ...
```

### Frontend Components

#### 1. Pricing Page (`frontend/src/pages/Pricing.tsx`)

Features:
- Displays all subscription tiers with pricing
- Toggle between monthly/annual billing
- Shows current user's plan
- Handles Stripe checkout flow
- Responsive grid layout

#### 2. Success/Cancel Pages
- `SubscriptionSuccess.tsx` - Post-checkout success page
- `SubscriptionCancel.tsx` - Checkout cancellation page

## Subscription Tiers

### Free Tier
- **Price:** $0/month
- **Limits:**
  - 10 messages/month
  - 5 posts/month
  - 100 connections
  - 1 job post
- **Features:**
  - Basic job search
  - View job postings
  - Create profile
  - Apply to jobs

### Pro Tier
- **Price:** $9.99/month ($99/year - save 17%)
- **Limits:**
  - Unlimited messages
  - Unlimited posts
  - Unlimited connections
  - 5 InMails/month
  - 3 job posts
- **Features:**
  - No ads
  - Advanced search
  - Profile analytics
  - Priority support
  - Pro badge

### Business Tier
- **Price:** $49.99/month ($499/year - save 17%)
- **Limits:**
  - Unlimited everything
  - 50 InMails/month
  - 5 team members
- **Features:**
  - All Pro features
  - Boost posts
  - Featured jobs
  - Team collaboration
  - Applicant tracking
  - API access
  - Priority job placement

### Enterprise Tier
- **Price:** $500+/month (custom)
- **Limits:** Unlimited
- **Features:**
  - All Business features
  - White-label options
  - Dedicated account manager
  - SLA guarantee
  - Custom integrations
  - Training & onboarding

## Setup Instructions

### 1. Database Setup

Run the migration script to create tables and seed tiers:

```bash
cd backend
python create_subscription_tables.py
```

This will:
- Create all monetization tables
- Seed 4 subscription tiers (Free, Pro, Business, Enterprise)

### 2. Stripe Configuration

Set the following environment variables:

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:5173  # or production URL
```

**Stripe Setup Steps:**
1. Create Stripe account at https://stripe.com
2. Get API keys from Dashboard → Developers → API keys
3. Set up webhook endpoint at Dashboard → Developers → Webhooks
4. Add webhook URL: `https://your-backend-url.com/api/subscriptions/webhook`
5. Subscribe to events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### 3. Test Stripe Integration

Use Stripe test mode with test cards:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0025 0000 3155`

### 4. Frontend Routes

Add routes to your router configuration:

```tsx
import { Pricing, SubscriptionSuccess, SubscriptionCancel } from './pages';

// In your router
<Route path="/pricing" element={<Pricing />} />
<Route path="/subscription/success" element={<SubscriptionSuccess />} />
<Route path="/subscription/cancel" element={<SubscriptionCancel />} />
```

## Revenue Projections

Based on 1M users:

| Tier | Users | Conversion | Price | Monthly Revenue |
|------|-------|------------|-------|-----------------|
| Free | 980,000 | - | $0 | $0 |
| Pro | 20,000 | 2% | $9.99 | $199,800 |
| Business | 500 | 5% of employers | $49.99 | $24,995 |
| Enterprise | 20 | - | $500 avg | $10,000 |
| **Total MRR** | | | | **$234,795** |

**Additional Revenue:**
- Ads (Free users): ~$98,000/month
- Boosted posts: Variable
- **Total MRR: ~$332,795/month**
- **ARR: ~$3.99M/year**

## Boost Post Pricing

- **Base Price:** $5/day
- **Default Duration:** 7 days ($35 total)
- **Max Duration:** 30 days ($150 total)

**Benefits:**
- Appears first in feeds
- Highlighted visually
- Priority placement
- Performance tracking (impressions, clicks)

## Analytics Events to Track

Track these events for conversion optimization:

```typescript
// Frontend tracking
track('upgrade_clicked', { tier: 'pro' });
track('paywall_viewed', { feature: 'unlimited_messaging' });
track('checkout_started', { tier: 'business' });
track('checkout_completed', { tier: 'pro', amount: 9.99 });
track('boost_purchased', { post_id: 123, duration: 7 });
```

## Feature Gating Examples

### Example 1: Limit Messages for Free Users

```python
from app.core.feature_gates import enforce_usage_limit

@router.post("/messages")
async def send_message(
    message: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check and enforce limit
    await enforce_usage_limit(user, "messages", "messages_per_month", db)
    
    # Create message
    new_message = Message(...)
    db.add(new_message)
    await db.commit()
    
    return new_message
```

### Example 2: Require Pro for Advanced Search

```python
from app.core.feature_gates import require_tier_access

@router.get("/search/advanced")
async def advanced_search(
    query: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Require Pro tier or higher
    await require_tier_access(user, "pro", db)
    
    # Perform advanced search
    results = ...
    return results
```

## Security Considerations

1. **Webhook Verification:** Always verify Stripe webhook signatures
2. **Authentication:** All subscription endpoints require authentication
3. **Admin Endpoints:** Revenue/analytics endpoints restricted to admins
4. **Rate Limiting:** Implement rate limits on payment endpoints
5. **PCI Compliance:** Never store card details (Stripe handles this)

## Testing Checklist

- [ ] Create subscription checkout flow
- [ ] Complete payment with test card
- [ ] Verify webhook processing
- [ ] Test subscription cancellation
- [ ] Test subscription reactivation
- [ ] Test feature gating for Free users
- [ ] Test usage limit enforcement
- [ ] Test boost post creation
- [ ] Test analytics tracking
- [ ] Test admin revenue dashboard

## Deployment

### Environment Variables

**Backend:**
```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=https://your-frontend.com
DATABASE_URL=postgresql://...
```

**Frontend:**
```env
VITE_API_URL=https://your-backend.com
```

### Post-Deployment Steps

1. Run database migration: `python backend/create_subscription_tables.py`
2. Verify Stripe webhook is receiving events
3. Test checkout flow in production mode
4. Monitor error logs for payment issues
5. Set up Stripe billing dashboard alerts

## Support & Maintenance

### Monitoring

Monitor these metrics:
- Conversion rate (Free → Paid)
- Churn rate
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User)
- Payment failure rate
- Webhook processing time

### Common Issues

**Issue:** Webhook not receiving events
- **Solution:** Check webhook URL in Stripe dashboard
- Verify webhook secret matches environment variable
- Check firewall/security group settings

**Issue:** Checkout not redirecting
- **Solution:** Verify FRONTEND_URL is set correctly
- Check success/cancel URL configuration

**Issue:** Feature limits not working
- **Solution:** Ensure FeatureUsage table exists
- Verify subscription tier features JSON format
- Check feature gate middleware is applied

## Future Enhancements

- [ ] Add sponsored content management UI
- [ ] Implement API key generation for Enterprise
- [ ] Add bulk job posting for Business tier
- [ ] Create admin analytics dashboard
- [ ] Add email notifications for subscription events
- [ ] Implement referral program
- [ ] Add promo codes/discounts
- [ ] Create mobile app with in-app purchases

## Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [React Stripe Elements](https://stripe.com/docs/stripe-js/react)

## Support

For questions or issues:
- Email: support@hiremebahamas.com
- Documentation: /docs/monetization
- API Reference: /api/docs

---

**Last Updated:** December 2024
**Version:** 1.0.0
