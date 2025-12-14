"""
User login analytics and monitoring API endpoints.

Provides comprehensive user activity statistics, login tracking,
and inactive user identification for admin users.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, LoginAttempt
from app.api.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin authentication"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/user-logins")
async def get_user_login_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get comprehensive user login statistics
    
    Returns:
        - Total users count
        - Active users count (logged in last 30 days)
        - Users who have never logged in (no last_login)
        - Users who haven't logged in recently (30+ days)
        - OAuth users vs password users breakdown
        - Users with failed login attempts
        - Average logins per day/week
    
    Requires admin authentication.
    """
    logger.info(f"User login analytics requested by admin user_id={current_user.id}")
    
    # Calculate date thresholds
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    
    # Active users (logged in last 30 days)
    result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.last_login.isnot(None),
                User.last_login >= thirty_days_ago
            )
        )
    )
    active_users_30d = result.scalar()
    
    # Active users (logged in last 7 days)
    result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.last_login.isnot(None),
                User.last_login >= seven_days_ago
            )
        )
    )
    active_users_7d = result.scalar()
    
    # Never logged in (no last_login)
    result = await db.execute(
        select(func.count(User.id)).where(User.last_login.is_(None))
    )
    never_logged_in = result.scalar()
    
    # Inactive users (30+ days since last login)
    result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.last_login.isnot(None),
                User.last_login < thirty_days_ago
            )
        )
    )
    inactive_users = result.scalar()
    
    # OAuth vs password users
    result = await db.execute(
        select(func.count(User.id)).where(User.oauth_provider.isnot(None))
    )
    oauth_users = result.scalar()
    
    result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.oauth_provider.is_(None),
                User.hashed_password.isnot(None)
            )
        )
    )
    password_users = result.scalar()
    
    # Users with failed login attempts (last 30 days)
    result = await db.execute(
        select(func.count(func.distinct(LoginAttempt.user_id))).where(
            and_(
                LoginAttempt.success == False,
                LoginAttempt.timestamp >= thirty_days_ago,
                LoginAttempt.user_id.isnot(None)
            )
        )
    )
    users_with_failed_attempts = result.scalar() or 0
    
    # Total login attempts (last 30 days)
    result = await db.execute(
        select(func.count(LoginAttempt.id)).where(
            and_(
                LoginAttempt.success == True,
                LoginAttempt.timestamp >= thirty_days_ago
            )
        )
    )
    total_logins_30d = result.scalar() or 0
    
    # Average logins per day (last 30 days)
    avg_logins_per_day = round(total_logins_30d / 30, 2) if total_logins_30d > 0 else 0
    
    # Average logins per week
    avg_logins_per_week = round(avg_logins_per_day * 7, 2)
    
    # Get distribution by authentication method
    result = await db.execute(
        select(
            User.oauth_provider,
            func.count(User.id).label('count')
        ).group_by(User.oauth_provider)
    )
    auth_distribution = {
        row.oauth_provider or 'password': row.count
        for row in result.all()
    }
    
    return {
        "total_users": total_users,
        "active_users": {
            "last_30_days": active_users_30d,
            "last_7_days": active_users_7d
        },
        "never_logged_in": never_logged_in,
        "inactive_users_30d": inactive_users,
        "authentication_methods": {
            "oauth_users": oauth_users,
            "password_users": password_users,
            "distribution": auth_distribution
        },
        "failed_login_attempts": {
            "users_with_failures_30d": users_with_failed_attempts
        },
        "login_activity": {
            "total_logins_30d": total_logins_30d,
            "avg_logins_per_day": avg_logins_per_day,
            "avg_logins_per_week": avg_logins_per_week
        },
        "generated_at": now.isoformat()
    }


@router.get("/user-logins/{user_id}")
async def get_user_login_history(
    user_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get specific user's login history
    
    Args:
        user_id: User ID to get history for
        limit: Maximum number of login attempts to return
    
    Returns:
        - User's login timestamps
        - Failed login attempts
        - Last login date
        - Account status (active/inactive)
        - Authentication method (OAuth vs password)
    
    Requires admin authentication.
    """
    logger.info(f"User login history requested for user_id={user_id} by admin user_id={current_user.id}")
    
    # Get user details
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get login attempts (both successful and failed)
    result = await db.execute(
        select(LoginAttempt)
        .where(LoginAttempt.user_id == user_id)
        .order_by(LoginAttempt.timestamp.desc())
        .limit(limit)
    )
    login_attempts = result.scalars().all()
    
    # Calculate failed attempts
    failed_attempts = [
        {
            "timestamp": attempt.timestamp.isoformat(),
            "ip_address": attempt.ip_address,
            "failure_reason": attempt.failure_reason
        }
        for attempt in login_attempts if not attempt.success
    ]
    
    # Calculate successful logins
    successful_logins = [
        {
            "timestamp": attempt.timestamp.isoformat(),
            "ip_address": attempt.ip_address
        }
        for attempt in login_attempts if attempt.success
    ]
    
    # Determine authentication method
    auth_method = "oauth" if user.oauth_provider else "password"
    if user.oauth_provider:
        auth_method = f"oauth_{user.oauth_provider}"
    
    # Calculate days since last login
    days_since_login = None
    if user.last_login:
        days_since_login = (datetime.utcnow() - user.last_login).days
    
    return {
        "user_id": user.id,
        "email": user.email,
        "name": f"{user.first_name} {user.last_name}",
        "account_status": "active" if user.is_active else "inactive",
        "authentication_method": auth_method,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "days_since_login": days_since_login,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "login_history": {
            "successful_logins": successful_logins,
            "failed_attempts": failed_attempts,
            "total_attempts_shown": len(login_attempts)
        }
    }


@router.get("/inactive-users")
async def get_inactive_users(
    days: int = Query(default=30, ge=1, le=365, description="Days threshold for inactive users"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List users who haven't logged in
    
    Args:
        days: Threshold for "inactive" (default: 30)
        limit: Maximum number of users to return
        offset: Number of users to skip (for pagination)
    
    Returns:
        List of users with no recent activity including:
        - id, email, last_login, created_at
        - days_since_login
        - authentication_method
    
    Requires admin authentication.
    """
    logger.info(f"Inactive users requested (days={days}) by admin user_id={current_user.id}")
    
    threshold_date = datetime.utcnow() - timedelta(days=days)
    
    # Get inactive users (either never logged in or last login beyond threshold)
    result = await db.execute(
        select(User)
        .where(
            or_(
                User.last_login.is_(None),
                User.last_login < threshold_date
            )
        )
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()
    
    # Count total inactive users (for pagination)
    result = await db.execute(
        select(func.count(User.id))
        .where(
            or_(
                User.last_login.is_(None),
                User.last_login < threshold_date
            )
        )
    )
    total_inactive = result.scalar()
    
    # Format response
    inactive_users = []
    for user in users:
        days_since_login = None
        if user.last_login:
            days_since_login = (datetime.utcnow() - user.last_login).days
        
        auth_method = "password"
        if user.oauth_provider:
            auth_method = f"oauth_{user.oauth_provider}"
        
        inactive_users.append({
            "id": user.id,
            "email": user.email,
            "name": f"{user.first_name} {user.last_name}",
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "days_since_login": days_since_login,
            "authentication_method": auth_method,
            "is_active": user.is_active
        })
    
    return {
        "users": inactive_users,
        "total": total_inactive,
        "limit": limit,
        "offset": offset,
        "threshold_days": days
    }


@router.get("/login-activity")
async def get_login_activity_timeline(
    days: int = Query(default=30, ge=1, le=90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get login activity over time for charting
    
    Returns daily login counts for the specified period.
    
    Args:
        days: Number of days to analyze (default: 30)
    
    Returns:
        Daily login activity data for visualization
    
    Requires admin authentication.
    """
    logger.info(f"Login activity timeline requested (days={days}) by admin user_id={current_user.id}")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get successful logins grouped by day
    result = await db.execute(
        select(
            func.date(LoginAttempt.timestamp).label('date'),
            func.count(LoginAttempt.id).label('count')
        )
        .where(
            and_(
                LoginAttempt.success == True,
                LoginAttempt.timestamp >= start_date
            )
        )
        .group_by(func.date(LoginAttempt.timestamp))
        .order_by(func.date(LoginAttempt.timestamp))
    )
    
    daily_logins = [
        {
            "date": str(row.date),
            "count": row.count
        }
        for row in result.all()
    ]
    
    return {
        "daily_logins": daily_logins,
        "period_days": days,
        "start_date": start_date.date().isoformat(),
        "end_date": datetime.utcnow().date().isoformat()
    }
