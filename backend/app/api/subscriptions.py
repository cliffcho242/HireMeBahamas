"""
Subscriptions API - Stripe integration for subscription management
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.database import get_db
from app.models import (
    User, SubscriptionTier, UserSubscription, Payment, FeatureUsage
)
from app.schemas.subscription import (
    SubscriptionTierResponse,
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    SubscriptionStatusResponse,
    PaymentResponse,
    FeatureUsageResponse,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# Stripe will be imported only when needed to avoid dependency issues
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_AVAILABLE = bool(stripe.api_key)
except ImportError:
    STRIPE_AVAILABLE = False


# ============================================================================
# SUBSCRIPTION TIERS
# ============================================================================

@router.get("/tiers", response_model=List[SubscriptionTierResponse])
async def get_subscription_tiers(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all available subscription tiers
    
    Returns list of subscription tiers with pricing and features
    """
    result = await db.execute(
        select(SubscriptionTier)
        .where(SubscriptionTier.is_active == True)
        .order_by(SubscriptionTier.price)
    )
    tiers = result.scalars().all()
    
    # Parse JSON strings for features and limits
    response = []
    for tier in tiers:
        tier_dict = {
            "id": tier.id,
            "name": tier.name,
            "display_name": tier.display_name,
            "price": tier.price,
            "annual_price": tier.annual_price,
            "billing_period": tier.billing_period,
            "description": tier.description,
            "features": json.loads(tier.features) if tier.features else {},
            "limits": json.loads(tier.limits) if tier.limits else {},
            "is_active": tier.is_active,
            "created_at": tier.created_at,
            "updated_at": tier.updated_at,
        }
        response.append(tier_dict)
    
    return response


# ============================================================================
# CHECKOUT & SUBSCRIPTION MANAGEMENT
# ============================================================================

@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    checkout_data: CheckoutSessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription
    
    Creates a Stripe checkout session and redirects user to payment page
    """
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Payment processing is not configured. Please contact support."
        )
    
    # Get subscription tier
    tier = await db.get(SubscriptionTier, checkout_data.tier_id)
    if not tier or not tier.is_active:
        raise HTTPException(status_code=404, detail="Subscription tier not found")
    
    # Don't allow downgrade to free tier
    if tier.name == "free":
        raise HTTPException(status_code=400, detail="Cannot checkout free tier")
    
    # Create or get Stripe customer
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
            metadata={"user_id": user.id}
        )
        user.stripe_customer_id = customer.id
        await db.commit()
    
    # Determine price based on billing period
    price = tier.annual_price if checkout_data.billing_period == "annual" and tier.annual_price else tier.price
    interval = "year" if checkout_data.billing_period == "annual" else "month"
    
    # Create checkout session
    try:
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            mode="subscription",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(price * 100),  # Convert to cents
                    "recurring": {"interval": interval},
                    "product_data": {
                        "name": f"HireMeBahamas {tier.display_name}",
                        "description": tier.description or f"{tier.display_name} subscription"
                    }
                },
                "quantity": 1
            }],
            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/subscription/cancel",
            metadata={
                "user_id": user.id,
                "tier_id": tier.id
            }
        )
        
        return CheckoutSessionResponse(checkout_url=session.url)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Payment error: {str(e)}")


@router.get("/me", response_model=SubscriptionStatusResponse)
async def get_my_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's subscription details
    
    Returns subscription tier, status, and available features
    """
    # Get active subscription
    result = await db.execute(
        select(UserSubscription)
        .options(selectinload(UserSubscription.tier))
        .where(
            and_(
                UserSubscription.user_id == user.id,
                UserSubscription.status == "active"
            )
        )
        .order_by(desc(UserSubscription.created_at))
    )
    subscription = result.scalar_one_or_none()
    
    # Default to free tier if no subscription
    if not subscription:
        return SubscriptionStatusResponse(
            tier="free",
            status="active",
            is_premium=False,
            features={
                "unlimited_messaging": False,
                "unlimited_posts": False,
                "no_ads": False,
                "advanced_search": False,
                "analytics": False,
                "priority_support": False,
                "api_access": False,
            },
            limits={
                "messages_per_month": 10,
                "posts_per_month": 5,
                "connections": 100,
                "inmails_per_month": 0,
                "job_posts": 1,
            }
        )
    
    # Parse tier features and limits
    tier = subscription.tier
    features = json.loads(tier.features) if tier.features else {}
    limits = json.loads(tier.limits) if tier.limits else {}
    
    return SubscriptionStatusResponse(
        tier=tier.name,
        status=subscription.status,
        is_premium=tier.name != "free",
        features=features,
        limits=limits
    )


@router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel user's subscription at period end
    
    Subscription remains active until the end of the billing period
    """
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Payment processing is not configured"
        )
    
    # Get active subscription
    result = await db.execute(
        select(UserSubscription)
        .where(
            and_(
                UserSubscription.user_id == user.id,
                UserSubscription.status == "active"
            )
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    # Cancel at period end via Stripe
    try:
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local record
        subscription.cancel_at_period_end = True
        await db.commit()
        
        return {
            "message": "Subscription will cancel at the end of the billing period",
            "cancel_at": subscription.current_period_end
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Cancellation error: {str(e)}")


@router.post("/reactivate")
async def reactivate_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reactivate a canceled subscription
    
    Removes the cancellation and subscription continues
    """
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Payment processing is not configured"
        )
    
    # Get subscription that's set to cancel
    result = await db.execute(
        select(UserSubscription)
        .where(
            and_(
                UserSubscription.user_id == user.id,
                UserSubscription.cancel_at_period_end == True
            )
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription to reactivate")
    
    # Reactivate via Stripe
    try:
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        # Update local record
        subscription.cancel_at_period_end = False
        await db.commit()
        
        return {"message": "Subscription reactivated successfully"}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Reactivation error: {str(e)}")


# ============================================================================
# STRIPE WEBHOOK
# ============================================================================

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events
    
    Processes subscription updates, payments, and cancellations from Stripe
    """
    if not STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    event_type = event["type"]
    data = event["data"]["object"]
    
    if event_type == "checkout.session.completed":
        await handle_checkout_completed(data, db)
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data, db)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(data, db)
    elif event_type == "invoice.payment_succeeded":
        await handle_payment_succeeded(data, db)
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(data, db)
    
    return {"status": "success"}


# ============================================================================
# WEBHOOK HANDLERS (HELPER FUNCTIONS)
# ============================================================================

async def handle_checkout_completed(session_data: dict, db: AsyncSession):
    """Handle successful checkout"""
    user_id = int(session_data["metadata"]["user_id"])
    tier_id = int(session_data["metadata"]["tier_id"])
    
    # Get subscription from Stripe
    subscription_id = session_data.get("subscription")
    if not subscription_id:
        return
    
    stripe_sub = stripe.Subscription.retrieve(subscription_id)
    
    # Create user subscription record
    subscription = UserSubscription(
        user_id=user_id,
        tier_id=tier_id,
        stripe_subscription_id=subscription_id,
        stripe_customer_id=session_data["customer"],
        status="active",
        current_period_start=datetime.fromtimestamp(stripe_sub["current_period_start"]),
        current_period_end=datetime.fromtimestamp(stripe_sub["current_period_end"]),
    )
    db.add(subscription)
    await db.commit()


async def handle_subscription_updated(subscription_data: dict, db: AsyncSession):
    """Handle subscription updates"""
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.stripe_subscription_id == subscription_data["id"])
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.status = subscription_data["status"]
        subscription.current_period_start = datetime.fromtimestamp(subscription_data["current_period_start"])
        subscription.current_period_end = datetime.fromtimestamp(subscription_data["current_period_end"])
        subscription.cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)
        await db.commit()


async def handle_subscription_deleted(subscription_data: dict, db: AsyncSession):
    """Handle subscription cancellation"""
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.stripe_subscription_id == subscription_data["id"])
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.status = "canceled"
        await db.commit()


async def handle_payment_succeeded(invoice_data: dict, db: AsyncSession):
    """Handle successful payment"""
    # Get subscription
    subscription_id = invoice_data.get("subscription")
    if not subscription_id:
        return
    
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.stripe_subscription_id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        return
    
    # Create payment record
    payment = Payment(
        user_id=subscription.user_id,
        subscription_id=subscription.id,
        stripe_payment_id=invoice_data.get("payment_intent"),
        stripe_invoice_id=invoice_data["id"],
        amount=invoice_data["amount_paid"] / 100,  # Convert from cents
        currency=invoice_data["currency"].upper(),
        status="succeeded",
        description=f"Subscription payment for period {invoice_data['period_start']} to {invoice_data['period_end']}"
    )
    db.add(payment)
    await db.commit()


async def handle_payment_failed(invoice_data: dict, db: AsyncSession):
    """Handle failed payment"""
    subscription_id = invoice_data.get("subscription")
    if not subscription_id:
        return
    
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.stripe_subscription_id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.status = "past_due"
        await db.commit()


# ============================================================================
# PAYMENT HISTORY
# ============================================================================

@router.get("/payments", response_model=List[PaymentResponse])
async def get_payment_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """
    Get user's payment history
    
    Returns list of past payments and invoices
    """
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == user.id)
        .order_by(desc(Payment.created_at))
        .limit(limit)
    )
    payments = result.scalars().all()
    
    return payments
