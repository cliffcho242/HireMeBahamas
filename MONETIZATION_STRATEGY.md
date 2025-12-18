# 💰 MONETIZATION STRATEGY — Generate Recurring Revenue

## 🎯 GOAL
Generate $10,000+/month in recurring revenue without killing UX

---

## 💎 SUBSCRIPTION TIERS

### Free Tier (Always Free)
**Target**: Job seekers, individual professionals
**Cost**: $0/month
**Features**:
- ✅ Create profile and apply to jobs
- ✅ Basic job search and filters
- ✅ View job postings (unlimited)
- ✅ Send 10 messages/month
- ✅ Create 5 posts/month
- ✅ Follow up to 100 connections
- ✅ Basic analytics (views only)
- ⚠️ Ads displayed
- ⚠️ Standard support (email only)

**Monetization**:
- **Ads revenue**: $0.50-2 CPM → $100-500/month (1M users, 20% engagement)
- **Conversion to Pro**: 2-5% upgrade rate

---

### Pro Tier ($9.99/month)
**Target**: Active job seekers, professionals
**Cost**: $9.99/month ($99/year - save 17%)
**Features**:
- ✅ **Everything in Free**, plus:
- ✅ **Unlimited messaging** — no message limits
- ✅ **Unlimited posts** — share as much as you want
- ✅ **No ads** — clean, distraction-free experience
- ✅ **Advanced search** — filter by salary, skills, company
- ✅ **InMail credits** — 5 direct messages to recruiters/month
- ✅ **Profile analytics** — who viewed your profile, search appearances
- ✅ **Resume insights** — see how your profile ranks
- ✅ **Priority support** — email + chat support
- ✅ **Profile badge** — "Pro" badge on profile
- ✅ **Featured in search** — 2x visibility boost

**Target Market**:
- 1,000,000 users × 2% conversion = **20,000 Pro users**
- 20,000 users × $9.99/month = **$199,800/month**

**Value Proposition**:
> "Get noticed by employers. Land your dream job faster."

---

### Business Tier ($49.99/month)
**Target**: Employers, recruiters, companies
**Cost**: $49.99/month ($499/year - save 17%)
**Features**:
- ✅ **Everything in Pro**, plus:
- ✅ **Post unlimited jobs** — no job posting limits
- ✅ **Advanced candidate search** — filter by skills, experience, salary
- ✅ **InMail credits** — 50 direct messages to candidates/month
- ✅ **Applicant tracking** — manage applications in one place
- ✅ **Team collaboration** — add team members (up to 5)
- ✅ **Company page** — branded company profile
- ✅ **Analytics dashboard** — job performance, applicant insights
- ✅ **Priority job placement** — featured in job listings
- ✅ **Candidate recommendations** — AI-powered matching
- ✅ **Priority support** — phone + email + chat
- ✅ **API access** — integrate with your ATS

**Target Market**:
- 1,000,000 users ÷ 100 = **10,000 employers**
- 10,000 employers × 5% conversion = **500 Business users**
- 500 users × $49.99/month = **$24,995/month**

**Value Proposition**:
> "Find the perfect candidate. Hire faster. Grow your team."

---

### Enterprise Tier (Custom Pricing)
**Target**: Large companies, staffing agencies
**Cost**: Custom ($500+/month)
**Features**:
- ✅ **Everything in Business**, plus:
- ✅ **Unlimited team members** — scale your recruiting team
- ✅ **Unlimited InMail** — reach any candidate
- ✅ **Dedicated account manager** — personalized support
- ✅ **Custom integrations** — integrate with your systems
- ✅ **White-label options** — brand it as your own
- ✅ **Advanced analytics** — custom reports and dashboards
- ✅ **Bulk candidate actions** — message/invite in bulk
- ✅ **SLA guarantee** — 99.9% uptime commitment
- ✅ **Training & onboarding** — dedicated onboarding support
- ✅ **Priority feature requests** — influence product roadmap

**Target Market**:
- 10 large companies × $500/month = **$5,000/month**
- 5 staffing agencies × $1,000/month = **$5,000/month**

---

## 📊 REVENUE PROJECTION

### Monthly Recurring Revenue (MRR)

| Tier | Users | Price | Revenue |
|------|-------|-------|---------|
| **Free** | 980,000 | $0 | $0 |
| **Free (Ads)** | 980,000 | $0.10/user | $98,000 |
| **Pro** | 20,000 | $9.99 | $199,800 |
| **Business** | 500 | $49.99 | $24,995 |
| **Enterprise** | 20 | $500 avg | $10,000 |
| **Total MRR** | 1,000,000 | | **$332,795** |

### Annual Recurring Revenue (ARR)

- **ARR**: $332,795/month × 12 = **$3,993,540/year**
- **Net Margin** (after infrastructure): $3,993,540 - ($130 × 12) = **$3,992,000/year**

### Revenue Growth Projections

| Quarter | Users | MRR | ARR |
|---------|-------|-----|-----|
| **Q1** | 250,000 | $83,199 | $998,388 |
| **Q2** | 500,000 | $166,398 | $1,996,776 |
| **Q3** | 750,000 | $249,596 | $2,995,152 |
| **Q4** | 1,000,000 | $332,795 | $3,993,540 |

---

## 🛠 IMPLEMENTATION ARCHITECTURE

### Subscription Management

**Tech Stack**:
- **Payment Processing**: Stripe (3% + $0.30 per transaction)
- **Billing**: Stripe Billing (subscription management)
- **Invoicing**: Stripe Invoices (automatic)
- **Tax Compliance**: Stripe Tax (automatic tax calculation)

**Database Schema**:
```sql
-- Subscription tiers
CREATE TABLE subscription_tiers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,  -- 'free', 'pro', 'business', 'enterprise'
    price DECIMAL(10, 2) NOT NULL,
    billing_period VARCHAR(20),  -- 'monthly', 'annual'
    features JSONB,              -- Feature flags
    limits JSONB,                -- Usage limits
    created_at TIMESTAMP DEFAULT NOW()
);

-- User subscriptions
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    tier_id INTEGER REFERENCES subscription_tiers(id),
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    status VARCHAR(50),  -- 'active', 'canceled', 'past_due', 'trialing'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    trial_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, stripe_subscription_id)
);

-- Feature usage tracking
CREATE TABLE feature_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    feature VARCHAR(100),  -- 'messages', 'posts', 'inmails'
    usage_count INTEGER DEFAULT 0,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, feature, period_start)
);

-- Payment history
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subscription_id INTEGER REFERENCES user_subscriptions(id),
    stripe_payment_id VARCHAR(255),
    amount DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50),  -- 'succeeded', 'failed', 'pending'
    payment_method VARCHAR(50),  -- 'card', 'bank_transfer'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX idx_feature_usage_user_id ON feature_usage(user_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
```

---

### Backend API Implementation

**Subscription Management Endpoints**:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import stripe

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Get subscription tiers
@router.get("/tiers")
async def get_subscription_tiers(db: Session = Depends(get_db)):
    """Get all available subscription tiers"""
    tiers = await db.execute(select(SubscriptionTier))
    return [
        {
            "id": tier.id,
            "name": tier.name,
            "price": tier.price,
            "billing_period": tier.billing_period,
            "features": tier.features,
            "limits": tier.limits
        }
        for tier in tiers.scalars().all()
    ]

# Create checkout session
@router.post("/checkout")
async def create_checkout_session(
    tier_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for subscription"""
    
    # Get subscription tier
    tier = await db.get(SubscriptionTier, tier_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    # Create Stripe customer if doesn't exist
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
            metadata={"user_id": user.id}
        )
        user.stripe_customer_id = customer.id
        await db.commit()
    
    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        mode="subscription",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": int(tier.price * 100),  # Convert to cents
                "recurring": {
                    "interval": "month" if tier.billing_period == "monthly" else "year"
                },
                "product_data": {
                    "name": f"HireMeBahamas {tier.name.title()}",
                    "description": f"{tier.name.title()} subscription"
                }
            },
            "quantity": 1
        }],
        success_url=f"{os.getenv('FRONTEND_URL')}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{os.getenv('FRONTEND_URL')}/subscription/cancel",
        metadata={
            "user_id": user.id,
            "tier_id": tier_id
        }
    )
    
    return {"checkout_url": session.url}

# Webhook handler for Stripe events
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_completed(session, db)
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await handle_subscription_updated(subscription, db)
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_canceled(subscription, db)
    
    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        await handle_payment_succeeded(invoice, db)
    
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        await handle_payment_failed(invoice, db)
    
    return {"status": "success"}

# Get user's current subscription
@router.get("/me")
async def get_my_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription details"""
    
    subscription = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.user_id == user.id)
        .where(UserSubscription.status == "active")
    )
    sub = subscription.scalar_one_or_none()
    
    if not sub:
        return {
            "tier": "free",
            "status": "active",
            "features": get_free_tier_features()
        }
    
    tier = await db.get(SubscriptionTier, sub.tier_id)
    
    return {
        "tier": tier.name,
        "status": sub.status,
        "current_period_end": sub.current_period_end,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "features": tier.features,
        "limits": tier.limits
    }

# Cancel subscription
@router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel user's subscription at period end"""
    
    subscription = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.user_id == user.id)
        .where(UserSubscription.status == "active")
    )
    sub = subscription.scalar_one_or_none()
    
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    # Cancel at period end via Stripe
    stripe.Subscription.modify(
        sub.stripe_subscription_id,
        cancel_at_period_end=True
    )
    
    # Update local record
    sub.cancel_at_period_end = True
    await db.commit()
    
    return {"message": "Subscription will cancel at period end"}

# Reactivate subscription
@router.post("/reactivate")
async def reactivate_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate a canceled subscription"""
    
    subscription = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.user_id == user.id)
        .where(UserSubscription.cancel_at_period_end == True)
    )
    sub = subscription.scalar_one_or_none()
    
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription to reactivate")
    
    # Reactivate via Stripe
    stripe.Subscription.modify(
        sub.stripe_subscription_id,
        cancel_at_period_end=False
    )
    
    # Update local record
    sub.cancel_at_period_end = False
    await db.commit()
    
    return {"message": "Subscription reactivated"}
```

---

### Feature Access Control

**Middleware for Feature Gating**:

```python
from functools import wraps
from fastapi import HTTPException

def require_subscription(tier: str):
    """Decorator to require specific subscription tier"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user") or args[0]
            
            # Check user's subscription
            subscription = await get_user_subscription(user.id)
            
            tier_hierarchy = {
                "free": 0,
                "pro": 1,
                "business": 2,
                "enterprise": 3
            }
            
            user_tier_level = tier_hierarchy.get(subscription.tier, 0)
            required_tier_level = tier_hierarchy.get(tier, 0)
            
            if user_tier_level < required_tier_level:
                raise HTTPException(
                    status_code=403,
                    detail=f"This feature requires {tier.title()} subscription"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def check_feature_limit(feature: str, limit_key: str):
    """Decorator to check feature usage limits"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user") or args[0]
            
            # Get user's subscription and limits
            subscription = await get_user_subscription(user.id)
            limits = subscription.tier.limits
            
            # Check usage
            usage = await get_feature_usage(user.id, feature)
            
            if limits.get(limit_key) and usage >= limits[limit_key]:
                raise HTTPException(
                    status_code=403,
                    detail=f"You've reached your {feature} limit. Upgrade to continue."
                )
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Increment usage
            await increment_feature_usage(user.id, feature)
            
            return result
        return wrapper
    return decorator

# Usage examples
@router.post("/messages")
@check_feature_limit("messages", "messages_per_month")
async def send_message(
    message: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message (limited by subscription)"""
    # Send message logic
    pass

@router.post("/jobs/featured")
@require_subscription("business")
async def feature_job(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Feature a job listing (Business+ only)"""
    # Feature job logic
    pass
```

---

## 📱 FRONTEND INTEGRATION

### Subscription UI Components

**Pricing Page** (`frontend/src/pages/Pricing.tsx`):
```typescript
import React from 'react';
import { Check, X } from 'lucide-react';

const pricingTiers = [
  {
    name: 'Free',
    price: 0,
    period: 'forever',
    features: [
      'Basic job search',
      '10 messages/month',
      '5 posts/month',
      'Follow 100 connections',
      'Ads displayed'
    ],
    cta: 'Get Started',
    ctaVariant: 'secondary'
  },
  {
    name: 'Pro',
    price: 9.99,
    period: 'month',
    popular: true,
    features: [
      'Everything in Free',
      'Unlimited messaging',
      'Unlimited posts',
      'No ads',
      'Advanced search',
      '5 InMail credits/month',
      'Profile analytics',
      'Priority support'
    ],
    cta: 'Upgrade to Pro',
    ctaVariant: 'primary'
  },
  {
    name: 'Business',
    price: 49.99,
    period: 'month',
    features: [
      'Everything in Pro',
      'Post unlimited jobs',
      'Advanced candidate search',
      '50 InMail credits/month',
      'Applicant tracking',
      'Team collaboration (5 members)',
      'Analytics dashboard',
      'API access'
    ],
    cta: 'Start Business',
    ctaVariant: 'primary'
  }
];

export const PricingPage: React.FC = () => {
  const handleSubscribe = async (tierName: string) => {
    if (tierName === 'Free') {
      // Already on free tier
      return;
    }
    
    try {
      const response = await fetch('/api/subscriptions/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier_name: tierName.toLowerCase() })
      });
      
      const { checkout_url } = await response.json();
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Failed to create checkout:', error);
    }
  };
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-4">
        Choose Your Plan
      </h1>
      <p className="text-xl text-gray-600 text-center mb-12">
        Find the perfect plan for your career goals
      </p>
      
      <div className="grid md:grid-cols-3 gap-8">
        {pricingTiers.map((tier) => (
          <div
            key={tier.name}
            className={`
              rounded-lg border-2 p-8
              ${tier.popular ? 'border-blue-500 shadow-xl scale-105' : 'border-gray-200'}
            `}
          >
            {tier.popular && (
              <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium mb-4 inline-block">
                Most Popular
              </span>
            )}
            
            <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
            
            <div className="mb-6">
              <span className="text-4xl font-bold">${tier.price}</span>
              <span className="text-gray-600">/{tier.period}</span>
            </div>
            
            <ul className="space-y-3 mb-8">
              {tier.features.map((feature, index) => (
                <li key={index} className="flex items-start">
                  <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            
            <button
              onClick={() => handleSubscribe(tier.name)}
              className={`
                w-full py-3 rounded-lg font-medium
                ${tier.ctaVariant === 'primary' 
                  ? 'bg-blue-500 hover:bg-blue-600 text-white' 
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
                }
              `}
            >
              {tier.cta}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## 📊 ANALYTICS & TRACKING

### Key Metrics to Track

**Subscription Metrics**:
- **MRR** (Monthly Recurring Revenue)
- **ARR** (Annual Recurring Revenue)
- **Churn Rate** (% of users canceling)
- **ARPU** (Average Revenue Per User)
- **LTV** (Lifetime Value)
- **CAC** (Customer Acquisition Cost)

**Feature Usage**:
- Messages sent per tier
- Posts created per tier
- InMails used per tier
- Job applications per tier
- Search queries per tier

**Conversion Funnel**:
- Free → Pro conversion rate
- Pro → Business conversion rate
- Trial → Paid conversion rate
- Cancellation → Reactivation rate

---

## 🚀 LAUNCH STRATEGY

### Phase 1: Soft Launch (Month 1)
- [ ] Launch with Free + Pro tiers only
- [ ] Offer 7-day free trial for Pro
- [ ] Limited to 1,000 beta users
- [ ] Gather feedback and iterate

### Phase 2: Public Launch (Month 2-3)
- [ ] Open to all users
- [ ] Add Business tier
- [ ] Launch referral program (1 month free for referrals)
- [ ] Marketing campaign

### Phase 3: Growth (Month 4-6)
- [ ] Add Enterprise tier
- [ ] Launch annual billing (save 17%)
- [ ] Add team features
- [ ] Partner with companies for bulk subscriptions

### Phase 4: Scale (Month 7-12)
- [ ] International expansion
- [ ] Add more premium features
- [ ] Mobile app with in-app purchases
- [ ] B2B partnerships

---

## 💡 UPSELL STRATEGIES

### In-App Prompts
- **Message limit reached**: "Upgrade to Pro for unlimited messaging"
- **Post limit reached**: "Upgrade to continue sharing"
- **InMail needed**: "Send direct message with Pro"
- **Job posting limit**: "Upgrade to Business for unlimited job posts"

### Email Campaigns
- **Welcome series**: Highlight Pro features
- **Usage milestones**: "You've sent 8/10 messages this month"
- **Feature discovery**: "Did you know Pro users get..."
- **Win-back campaigns**: Offer discounts to churned users

### Social Proof
- **Testimonials**: "How Pro helped me land my dream job"
- **Success stories**: Featured Pro users
- **Stats**: "Pro users get 3x more profile views"

---

## 🎯 SUCCESS METRICS

### 6-Month Goals
- **1,000,000** total users
- **20,000** Pro subscribers (2% conversion)
- **500** Business subscribers (5% of employers)
- **$225,000/month** MRR
- **$2.7M/year** ARR

### 12-Month Goals
- **2,000,000** total users
- **50,000** Pro subscribers (2.5% conversion)
- **1,500** Business subscribers (7% of employers)
- **$575,000/month** MRR
- **$6.9M/year** ARR

---

**Ready to monetize?** Let's make money! 💰

See also:
- [Scale to 1M Users Blueprint](./SCALE_TO_1M_USERS_BLUEPRINT.md)
- [Backend Scaling Pattern](./BACKEND_SCALING_PATTERN.md)
- [Feature Gating Guide](./FEATURE_GATING_GUIDE.md)
