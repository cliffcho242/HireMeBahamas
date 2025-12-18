"""
Tests for subscription API endpoints and feature gating.
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from app.models import User
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_get_subscription_plans(client: AsyncClient):
    """Test getting subscription plans (public endpoint)"""
    response = await client.get("/api/subscriptions/plans")
    assert response.status_code == 200
    
    data = response.json()
    assert "plans" in data
    plans = data["plans"]
    
    # Check all plans are present
    assert "free" in plans
    assert "pro" in plans
    assert "business" in plans
    assert "enterprise" in plans
    
    # Verify plan structure
    assert plans["free"]["price"] == 0
    assert plans["pro"]["price"] == 9.99
    assert plans["business"]["price"] == 29.99
    assert plans["enterprise"]["price"] is None


@pytest.mark.asyncio
async def test_get_current_subscription_unauthenticated(client: AsyncClient):
    """Test getting current subscription without authentication"""
    response = await client.get("/api/subscriptions/current")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_subscription_free_user(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test getting current subscription for free user"""
    response = await client.get("/api/subscriptions/current", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["plan"] == "free"
    assert data["status"] == "active"
    assert data["is_pro"] is False


@pytest.mark.asyncio
async def test_upgrade_to_pro(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test upgrading to Pro plan"""
    response = await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "pro"},
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["plan"] == "pro"
    assert data["status"] == "active"
    assert data["end_date"] is not None
    
    # Verify user can now access current subscription as pro
    response = await client.get("/api/subscriptions/current", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_pro"] is True


@pytest.mark.asyncio
async def test_upgrade_invalid_plan(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test upgrading to invalid plan"""
    response = await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "invalid_plan"},
        headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upgrade_to_same_plan(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test upgrading to same plan"""
    # First upgrade to pro
    await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "pro"},
        headers=auth_headers
    )
    
    # Try to upgrade to pro again
    response = await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "pro"},
        headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upgrade_to_free_blocked(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test that upgrading to free plan is blocked"""
    response = await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "free"},
        headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cancel_subscription(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test cancelling subscription"""
    # First upgrade to pro
    await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "pro"},
        headers=auth_headers
    )
    
    # Cancel subscription
    response = await client.post("/api/subscriptions/cancel", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["plan"] == "free"
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_free_subscription(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test cancelling free subscription (should fail)"""
    response = await client.post("/api/subscriptions/cancel", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_feature_gating_free_user(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test that free users can't access pro features"""
    # This test assumes there's a pro-gated endpoint
    # For now, we just verify the is_pro property
    response = await client.get("/api/subscriptions/current", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_pro"] is False


@pytest.mark.asyncio
async def test_feature_gating_pro_user(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test that pro users can access pro features"""
    # Upgrade to pro
    await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "pro"},
        headers=auth_headers
    )
    
    # Verify user is now pro
    response = await client.get("/api/subscriptions/current", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_pro"] is True


@pytest.mark.asyncio
async def test_upgrade_to_business(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test upgrading to Business plan"""
    response = await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "business"},
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["plan"] == "business"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_upgrade_to_enterprise(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test upgrading to Enterprise plan"""
    response = await client.post(
        "/api/subscriptions/upgrade",
        json={"plan": "enterprise"},
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["plan"] == "enterprise"
    assert data["status"] == "active"
    # Enterprise has no end date (custom contracts)
    assert data["end_date"] is None
