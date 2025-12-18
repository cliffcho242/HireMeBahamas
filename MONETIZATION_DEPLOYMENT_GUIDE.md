# HireMeBahamas Monetization System - Deployment Guide

## Quick Start

This guide helps you deploy the monetization features to production.

## Prerequisites

- PostgreSQL database
- Stripe account (test or live mode)
- Backend deployed (Railway/Render)
- Frontend deployed (Vercel)

## Step 1: Environment Variables

### Backend Environment Variables

Add to your backend deployment (Railway/Render):

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_...  # or sk_test_... for testing
STRIPE_WEBHOOK_SECRET=whsec_...

# Frontend URL for redirects
FRONTEND_URL=https://your-frontend-domain.com

# Database (already configured)
DATABASE_URL=postgresql://...
```

### Frontend Environment Variables

Add to your Vercel deployment:

```env
# API Base URL (already configured)
VITE_API_URL=https://your-backend-domain.com
```

## Step 2: Stripe Setup

### 2.1 Get API Keys

1. Log in to [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Developers** → **API keys**
3. Copy:
   - **Publishable key** (starts with `pk_`)
   - **Secret key** (starts with `sk_`)

**For Testing:**
- Use test mode keys (look for "Test" toggle in dashboard)
- Test cards: `4242 4242 4242 4242` (success)

**For Production:**
- Switch to live mode
- Use live keys (requires business verification)

### 2.2 Configure Webhook

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Set URL: `https://your-backend-domain.com/api/subscriptions/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**
6. Copy the **Signing secret** (starts with `whsec_`)
7. Add to backend environment as `STRIPE_WEBHOOK_SECRET`

### 2.3 Test Webhook

```bash
# Install Stripe CLI (optional, for local testing)
stripe listen --forward-to http://localhost:8000/api/subscriptions/webhook

# Trigger test event
stripe trigger checkout.session.completed
```

## Step 3: Database Migration

### Option A: Manual Migration (Recommended)

SSH into your backend server and run:

```bash
cd /path/to/backend
python create_subscription_tables.py
```

This will:
- Create all monetization tables
- Seed subscription tiers (Free, Pro, Business, Enterprise)

### Option B: Include in Deployment Script

Add to your deployment script:

```bash
# After pip install and before app start
python backend/create_subscription_tables.py || echo "Tables already exist"
```

## Step 4: Verify Installation

### 4.1 Check Database Tables

Connect to your PostgreSQL database and verify tables exist:

```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

Should include:
- `subscription_tiers`
- `user_subscriptions`
- `payments`
- `feature_usage`
- `boosted_posts`
- `sponsored_content`
- `analytics_events`

### 4.2 Verify Subscription Tiers

```sql
SELECT name, display_name, price FROM subscription_tiers;
```

Should show:
- free ($0)
- pro ($9.99)
- business ($49.99)
- enterprise ($500)

### 4.3 Test API Endpoints

```bash
# Get subscription tiers (no auth required)
curl https://your-backend-domain.com/api/subscriptions/tiers

# Should return JSON array of 4 tiers
```

## Step 5: Frontend Deployment

### 5.1 Add Route to Router

In your main router file (e.g., `App.tsx` or `router.tsx`):

```tsx
import { 
  Pricing, 
  SubscriptionSuccess, 
  SubscriptionCancel 
} from './pages';

// Add routes
<Route path="/pricing" element={<Pricing />} />
<Route path="/subscription/success" element={<SubscriptionSuccess />} />
<Route path="/subscription/cancel" element={<SubscriptionCancel />} />
```

### 5.2 Add Navigation Link

In your navigation menu:

```tsx
<Link to="/pricing">Pricing</Link>
```

### 5.3 Deploy to Vercel

```bash
cd frontend
npm run build
vercel --prod
```

Or push to GitHub (if auto-deployment is configured).

## Step 6: Test Complete Flow

### 6.1 Test Checkout (Test Mode)

1. Go to `https://your-frontend-domain.com/pricing`
2. Click "Upgrade to Pro"
3. Use test card: `4242 4242 4242 4242`
4. Complete checkout
5. Verify redirect to success page
6. Check database for new subscription record

### 6.2 Test Webhook Processing

1. Complete a test checkout
2. Check backend logs for webhook events
3. Verify subscription status in database:

```sql
SELECT u.email, s.status, t.name 
FROM user_subscriptions s
JOIN users u ON s.user_id = u.id
JOIN subscription_tiers t ON s.tier_id = t.id
WHERE s.status = 'active';
```

### 6.3 Test Feature Gating

1. Log in as a free user
2. Try to access a premium feature
3. Should see upgrade prompt
4. Upgrade to Pro
5. Verify access to premium features

## Step 7: Monitoring

### 7.1 Stripe Dashboard

Monitor in Stripe Dashboard:
- **Payments** → See all transactions
- **Subscriptions** → See active subscriptions
- **Webhooks** → Monitor webhook delivery

### 7.2 Application Logs

Monitor backend logs for:
- Subscription creations
- Payment processing
- Webhook events
- Feature gate rejections

### 7.3 Database Monitoring

Query key metrics:

```sql
-- Active subscriptions by tier
SELECT t.name, COUNT(*) 
FROM user_subscriptions s
JOIN subscription_tiers t ON s.tier_id = t.id
WHERE s.status = 'active'
GROUP BY t.name;

-- Monthly Recurring Revenue (MRR)
SELECT SUM(t.price) as mrr
FROM user_subscriptions s
JOIN subscription_tiers t ON s.tier_id = t.id
WHERE s.status = 'active' AND t.billing_period = 'monthly';

-- Recent payments
SELECT u.email, p.amount, p.status, p.created_at
FROM payments p
JOIN users u ON p.user_id = u.id
ORDER BY p.created_at DESC
LIMIT 10;
```

## Step 8: Go Live Checklist

### Before Going Live

- [ ] Switch Stripe to live mode
- [ ] Update STRIPE_SECRET_KEY with live key
- [ ] Update STRIPE_WEBHOOK_SECRET with live webhook secret
- [ ] Test complete checkout flow in production
- [ ] Verify webhook is receiving events
- [ ] Test subscription cancellation
- [ ] Test feature gating
- [ ] Set up monitoring alerts
- [ ] Review pricing and features
- [ ] Prepare customer support documentation

### After Going Live

- [ ] Monitor first 24 hours closely
- [ ] Check for any payment failures
- [ ] Verify webhook processing
- [ ] Monitor error rates
- [ ] Collect user feedback
- [ ] Track conversion metrics

## Troubleshooting

### Issue: Webhook not receiving events

**Symptoms:** Subscriptions created but not showing in database

**Solutions:**
1. Check webhook URL is correct in Stripe dashboard
2. Verify STRIPE_WEBHOOK_SECRET matches in environment
3. Check backend logs for webhook errors
4. Test webhook manually using Stripe CLI
5. Ensure backend is publicly accessible (not localhost)

**Test:**
```bash
stripe trigger checkout.session.completed --api-key sk_test_...
```

### Issue: Checkout redirects to wrong URL

**Symptoms:** After payment, redirect fails or goes to localhost

**Solutions:**
1. Verify FRONTEND_URL environment variable is set correctly
2. Check success_url and cancel_url in checkout session creation
3. Ensure no trailing slashes in URLs

### Issue: Database connection errors

**Symptoms:** 500 errors when accessing subscription endpoints

**Solutions:**
1. Verify DATABASE_URL is correct
2. Check database connection pool settings
3. Ensure migration script ran successfully
4. Verify all tables exist

### Issue: Feature gates not working

**Symptoms:** Free users accessing premium features

**Solutions:**
1. Verify feature gate decorators are applied
2. Check subscription tier features JSON format
3. Ensure FeatureUsage table exists
4. Test with actual user accounts, not admin

## Security Best Practices

1. **Never commit secrets**
   - Use environment variables
   - Add .env to .gitignore

2. **Verify webhook signatures**
   - Always check Stripe signature
   - Reject invalid signatures

3. **Validate user input**
   - Sanitize all user inputs
   - Use Pydantic validation

4. **Rate limiting**
   - Implement rate limits on payment endpoints
   - Use Redis for distributed rate limiting

5. **Audit logging**
   - Log all subscription changes
   - Monitor for suspicious activity

## Support Resources

- **Stripe Documentation:** https://stripe.com/docs
- **Stripe Testing:** https://stripe.com/docs/testing
- **Stripe Webhooks:** https://stripe.com/docs/webhooks
- **Implementation Guide:** See MONETIZATION_IMPLEMENTATION.md
- **API Reference:** https://your-backend-domain.com/docs

## Cost Estimates

### Stripe Fees

- **Credit Card:** 2.9% + $0.30 per transaction
- **International:** +1.5% on international cards
- **Disputes:** $15 per dispute

### Monthly Costs (1M Users, 2% Conversion)

| Item | Cost |
|------|------|
| Stripe fees (20k subs) | ~$6,000 |
| Database | ~$50 |
| Backend hosting | ~$50 |
| Frontend hosting | ~$30 |
| **Total** | **~$6,130** |

**Revenue:** $234,795/month (subscriptions + ads)
**Profit:** $228,665/month (97.4% margin)

## Next Steps

1. Set up production Stripe account
2. Complete business verification
3. Deploy to production
4. Run migration script
5. Test complete flow
6. Monitor for 48 hours
7. Announce new features
8. Track metrics

## Contact

For deployment support:
- Email: dev@hiremebahamas.com
- Slack: #deployments
- Docs: /docs/deployment

---

**Last Updated:** December 2024
**Version:** 1.0.0
