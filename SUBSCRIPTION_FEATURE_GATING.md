# Subscription Feature Gating Guide

This guide shows how to implement feature gating based on subscription plans in HireMeBahamas.

## Overview

The subscription system supports 4 plans:
- **Free** ($0): Basic features
- **Pro** ($9.99/mo): Enhanced features for job seekers
- **Business** ($29.99/mo): Advanced features for employers
- **Enterprise** (Custom): Full-featured with custom integrations

## Backend Feature Gating

### Option 1: Using Dependency Injection (Recommended)

Add the subscription dependency to your endpoint:

```python
from app.api.subscriptions import require_pro_subscription

@router.post("/premium-feature")
async def premium_feature(
    user: User = Depends(require_pro_subscription),
    db: AsyncSession = Depends(get_db)
):
    # Only Pro+ users can access this endpoint
    # If user is not Pro+, they get a 402 Payment Required error
    return {"message": "This is a premium feature"}
```

Available dependencies:
- `require_pro_subscription` - Pro, Business, or Enterprise
- `require_business_subscription` - Business or Enterprise
- `require_enterprise_subscription` - Enterprise only

### Option 2: Manual Check

For more granular control, check the subscription within your endpoint:

```python
@router.post("/some-feature")
async def some_feature(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if user has Pro or higher
    if not current_user.is_pro:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Upgrade required. This feature requires a Pro subscription or higher."
        )
    
    # Continue with feature logic
    return {"message": "Feature accessed"}
```

### Example: Limit Job Posts by Plan

```python
@router.post("/", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new job posting with subscription limits"""
    
    # Get user's current job post count
    result = await db.execute(
        select(func.count(Job.id))
        .where(Job.employer_id == current_user.id)
        .where(Job.status == "active")
    )
    active_jobs_count = result.scalar()
    
    # Check limits based on subscription
    limits = {
        "free": 1,
        "pro": 5,
        "business": -1,  # unlimited
        "enterprise": -1  # unlimited
    }
    
    max_jobs = limits.get(current_user.subscription_plan, 1)
    
    if max_jobs != -1 and active_jobs_count >= max_jobs:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Job posting limit reached. Upgrade to post more jobs."
        )
    
    # Create job...
    db_job = Job(**job.dict(), employer_id=current_user.id)
    db.add(db_job)
    await db.commit()
    return db_job
```

## Frontend Feature Gating

### Using the Subscription Hook

```typescript
import { useSubscription } from '../hooks/useSubscription';
import UpgradePrompt from '../components/UpgradePrompt';

function PremiumFeature() {
  const { isPro, requirePro } = useSubscription();
  const [showUpgrade, setShowUpgrade] = useState(false);

  const handlePremiumAction = () => {
    if (!requirePro('Advanced Analytics')) {
      setShowUpgrade(true);
      return;
    }
    
    // Continue with premium action
    // ...
  };

  return (
    <div>
      <button onClick={handlePremiumAction}>
        Access Premium Feature
      </button>
      
      {showUpgrade && (
        <UpgradePrompt 
          featureName="Advanced Analytics"
          requiredPlan="pro"
          onClose={() => setShowUpgrade(false)}
        />
      )}
    </div>
  );
}
```

### Inline Upgrade Prompt

For features that are disabled, show an inline upgrade prompt:

```typescript
import UpgradePrompt from '../components/UpgradePrompt';
import { useSubscription } from '../hooks/useSubscription';

function FeatureSection() {
  const { isBusiness } = useSubscription();

  return (
    <div>
      {isBusiness ? (
        <AnalyticsDashboard />
      ) : (
        <UpgradePrompt 
          featureName="Analytics Dashboard"
          requiredPlan="business"
          inline
        />
      )}
    </div>
  );
}
```

### Conditional UI Elements

Hide or disable features based on subscription:

```typescript
import { useSubscription } from '../hooks/useSubscription';

function JobPostForm() {
  const { subscription, isPro } = useSubscription();
  
  return (
    <form>
      {/* Basic fields for all users */}
      <input name="title" placeholder="Job Title" />
      
      {/* Pro-only field */}
      <div className={!isPro ? 'opacity-50 pointer-events-none' : ''}>
        <input 
          name="featured" 
          type="checkbox" 
          disabled={!isPro}
        />
        <label>
          Feature this job 
          {!isPro && <span className="text-blue-600 ml-2">⭐ Pro</span>}
        </label>
      </div>
      
      {/* Show upgrade button for free users */}
      {!isPro && (
        <Link 
          to="/subscriptions" 
          className="text-blue-600 underline"
        >
          Upgrade to unlock all features
        </Link>
      )}
    </form>
  );
}
```

## API Endpoints

### Get Subscription Plans (Public)
```
GET /api/subscriptions/plans
```

Returns all available subscription plans with pricing and features.

### Get Current Subscription
```
GET /api/subscriptions/current
Authorization: Bearer <token>
```

Returns the current user's subscription information.

### Upgrade Subscription
```
POST /api/subscriptions/upgrade
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan": "pro"
}
```

Upgrades the user to a new plan. Accepts: "pro", "business", "enterprise".

### Cancel Subscription
```
POST /api/subscriptions/cancel
Authorization: Bearer <token>
```

Cancels the current subscription and downgrades to free plan.

## Database Migration

To apply the subscription fields to the database:

```bash
cd /home/runner/work/HireMeBahamas/HireMeBahamas
python migrations/add_subscription_fields.py upgrade
```

To rollback:

```bash
python migrations/add_subscription_fields.py downgrade
```

## User Model Changes

The User model now includes:
- `subscription_plan` (String): "free", "pro", "business", or "enterprise"
- `subscription_status` (String): "active", "cancelled", or "expired"
- `subscription_end_date` (DateTime): When the subscription expires (null for free)
- `is_pro` (Property): Boolean indicating if user has Pro+ subscription

## Error Responses

When a user tries to access a premium feature without the required subscription:

```json
{
  "detail": "Upgrade required. This feature requires a Pro subscription or higher."
}
```

Status Code: `402 Payment Required`

## Testing

Backend tests are in `tests/test_subscriptions.py`. Run with:

```bash
pytest tests/test_subscriptions.py -v
```

## Best Practices

1. **Always provide clear messaging** about what plan is required
2. **Use 402 Payment Required** status code for subscription-gated features
3. **Show upgrade prompts** rather than hiding features completely
4. **Check limits dynamically** - don't hardcode them in multiple places
5. **Log subscription events** for analytics and debugging
6. **Test both free and paid paths** to ensure proper gating

## Example: Complete Feature Implementation

Here's a complete example of adding a premium feature:

### Backend (api/backend_app/api/analytics.py)
```python
from app.api.subscriptions import require_business_subscription

@router.get("/advanced")
async def get_advanced_analytics(
    user: User = Depends(require_business_subscription),
    db: AsyncSession = Depends(get_db)
):
    """Get advanced analytics - Business plan only"""
    # Fetch advanced analytics data
    return {"analytics": "..."}
```

### Frontend (pages/Analytics.tsx)
```typescript
import { useSubscription } from '../hooks/useSubscription';
import UpgradePrompt from '../components/UpgradePrompt';

export default function Analytics() {
  const { isBusiness } = useSubscription();

  return (
    <div>
      <h1>Analytics</h1>
      
      {/* Basic analytics for all */}
      <BasicAnalytics />
      
      {/* Advanced analytics - Business+ only */}
      {isBusiness ? (
        <AdvancedAnalytics />
      ) : (
        <UpgradePrompt 
          featureName="Advanced Analytics"
          requiredPlan="business"
          inline
        />
      )}
    </div>
  );
}
```

## Support

For questions or issues with the subscription system, please contact the development team or create an issue in the repository.
