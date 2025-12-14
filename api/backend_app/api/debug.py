"""
Login diagnostic and debugging API endpoints.

Provides tools to identify and diagnose user login issues.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, and_
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


@router.get("/user-login-status/{email}")
async def check_user_login_status(
    email: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Check why a user can't log in
    
    Diagnostic endpoint that checks:
    - If user exists
    - If account is active
    - If password is set (or OAuth only)
    - Recent failed login attempts
    - Rate limiting/lockouts
    
    Returns detailed diagnostic report.
    
    Args:
        email: User email to diagnose
    
    Returns:
        Comprehensive diagnostic information
    
    Requires admin authentication.
    """
    logger.info(f"Login diagnostic requested for {email} by admin user_id={current_user.id}")
    
    # Initialize diagnostic results
    diagnostic = {
        "email": email,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check 1: User exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        diagnostic["checks"]["user_exists"] = {
            "status": "fail",
            "message": "User does not exist in database",
            "recommendation": "User needs to register first"
        }
        diagnostic["overall_status"] = "user_not_found"
        return diagnostic
    
    diagnostic["checks"]["user_exists"] = {
        "status": "pass",
        "message": f"User found (ID: {user.id})",
        "user_id": user.id
    }
    
    # Check 2: Account is active
    if user.is_active:
        diagnostic["checks"]["account_active"] = {
            "status": "pass",
            "message": "Account is active"
        }
    else:
        diagnostic["checks"]["account_active"] = {
            "status": "fail",
            "message": "Account is deactivated",
            "recommendation": "Reactivate account in admin panel"
        }
    
    # Check 3: Password is set
    if user.hashed_password:
        diagnostic["checks"]["password_set"] = {
            "status": "pass",
            "message": "Password is configured"
        }
    else:
        if user.oauth_provider:
            diagnostic["checks"]["password_set"] = {
                "status": "warning",
                "message": f"No password set - OAuth user ({user.oauth_provider})",
                "recommendation": f"User should sign in with {user.oauth_provider.title()}"
            }
        else:
            diagnostic["checks"]["password_set"] = {
                "status": "fail",
                "message": "No password set and no OAuth provider",
                "recommendation": "User needs to reset password"
            }
    
    # Check 4: Recent failed login attempts
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(LoginAttempt)
        .where(
            and_(
                LoginAttempt.user_id == user.id,
                LoginAttempt.success == False,
                LoginAttempt.timestamp >= thirty_days_ago
            )
        )
        .order_by(LoginAttempt.timestamp.desc())
        .limit(10)
    )
    failed_attempts = result.scalars().all()
    
    if failed_attempts:
        recent_failures = [
            {
                "timestamp": attempt.timestamp.isoformat(),
                "reason": attempt.failure_reason,
                "ip_address": attempt.ip_address
            }
            for attempt in failed_attempts
        ]
        
        diagnostic["checks"]["failed_attempts"] = {
            "status": "warning",
            "message": f"{len(failed_attempts)} failed login attempts in last 30 days",
            "recent_failures": recent_failures,
            "recommendation": "Review failure reasons and advise user"
        }
    else:
        diagnostic["checks"]["failed_attempts"] = {
            "status": "pass",
            "message": "No recent failed login attempts"
        }
    
    # Check 5: Last successful login
    if user.last_login:
        days_since_login = (datetime.utcnow() - user.last_login).days
        diagnostic["checks"]["last_login"] = {
            "status": "info",
            "message": f"Last login: {user.last_login.isoformat()}",
            "days_since_login": days_since_login
        }
    else:
        diagnostic["checks"]["last_login"] = {
            "status": "info",
            "message": "User has never logged in successfully",
            "recommendation": "User may be having trouble with initial login"
        }
    
    # Check 6: Authentication method
    auth_method = "password"
    if user.oauth_provider:
        auth_method = f"oauth_{user.oauth_provider}"
    
    diagnostic["checks"]["authentication_method"] = {
        "status": "info",
        "message": f"Authentication method: {auth_method}"
    }
    
    # Determine overall status
    has_failures = any(
        check.get("status") == "fail"
        for check in diagnostic["checks"].values()
    )
    
    if has_failures:
        diagnostic["overall_status"] = "issues_found"
        diagnostic["summary"] = "User account has issues preventing login"
    else:
        diagnostic["overall_status"] = "ok"
        diagnostic["summary"] = "No critical issues found. User should be able to log in."
    
    return diagnostic


@router.get("/recent-failures")
async def get_recent_login_failures(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get recent failed login attempts across all users
    
    Useful for identifying system-wide issues or attack patterns.
    
    Args:
        hours: How many hours to look back (default: 24)
        limit: Maximum number of failures to return
    
    Returns:
        List of recent failed login attempts with details
    
    Requires admin authentication.
    """
    logger.info(f"Recent login failures requested (hours={hours}) by admin user_id={current_user.id}")
    
    threshold = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(LoginAttempt, User)
        .outerjoin(User, LoginAttempt.user_id == User.id)
        .where(
            and_(
                LoginAttempt.success == False,
                LoginAttempt.timestamp >= threshold
            )
        )
        .order_by(LoginAttempt.timestamp.desc())
        .limit(limit)
    )
    
    failures = []
    for attempt, user in result.all():
        failures.append({
            "timestamp": attempt.timestamp.isoformat(),
            "email_attempted": attempt.email_attempted,
            "user_id": attempt.user_id,
            "user_exists": user is not None,
            "ip_address": attempt.ip_address,
            "failure_reason": attempt.failure_reason
        })
    
    # Get failure statistics
    result = await db.execute(
        select(
            LoginAttempt.failure_reason,
            func.count(LoginAttempt.id).label('count')
        )
        .where(
            and_(
                LoginAttempt.success == False,
                LoginAttempt.timestamp >= threshold
            )
        )
        .group_by(LoginAttempt.failure_reason)
    )
    
    failure_reasons = {
        row.failure_reason: row.count
        for row in result.all()
    }
    
    return {
        "failures": failures,
        "total_shown": len(failures),
        "period_hours": hours,
        "failure_reasons_breakdown": failure_reasons
    }


@router.get("/problem-accounts")
async def get_problem_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Identify user accounts with potential issues
    
    Checks for:
    - Users created but never logged in (30+ days)
    - Inactive accounts
    - Accounts with many failed login attempts
    - Users with missing passwords and no OAuth
    
    Returns:
        Categorized list of accounts needing attention
    
    Requires admin authentication.
    """
    logger.info(f"Problem accounts analysis requested by admin user_id={current_user.id}")
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Users created but never logged in (30+ days old)
    result = await db.execute(
        select(User)
        .where(
            and_(
                User.last_login.is_(None),
                User.created_at < thirty_days_ago
            )
        )
        .limit(50)
    )
    never_logged_in = [
        {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "days_since_creation": (datetime.utcnow() - user.created_at).days if user.created_at else None
        }
        for user in result.scalars().all()
    ]
    
    # Inactive accounts
    result = await db.execute(
        select(User)
        .where(User.is_active == False)
        .limit(50)
    )
    inactive_accounts = [
        {
            "id": user.id,
            "email": user.email,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        for user in result.scalars().all()
    ]
    
    # Users with many failed attempts (10+ in last 30 days)
    result = await db.execute(
        select(
            User.id,
            User.email,
            func.count(LoginAttempt.id).label('failed_count')
        )
        .join(LoginAttempt, User.id == LoginAttempt.user_id)
        .where(
            and_(
                LoginAttempt.success == False,
                LoginAttempt.timestamp >= thirty_days_ago
            )
        )
        .group_by(User.id, User.email)
        .having(func.count(LoginAttempt.id) >= 10)
        .limit(50)
    )
    high_failure_accounts = [
        {
            "id": row.id,
            "email": row.email,
            "failed_attempts": row.failed_count
        }
        for row in result.all()
    ]
    
    # Users with no password and no OAuth
    result = await db.execute(
        select(User)
        .where(
            and_(
                User.hashed_password.is_(None),
                User.oauth_provider.is_(None)
            )
        )
        .limit(50)
    )
    no_auth_method = [
        {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in result.scalars().all()
    ]
    
    return {
        "never_logged_in_30d": {
            "count": len(never_logged_in),
            "users": never_logged_in
        },
        "inactive_accounts": {
            "count": len(inactive_accounts),
            "users": inactive_accounts
        },
        "high_failure_accounts": {
            "count": len(high_failure_accounts),
            "users": high_failure_accounts
        },
        "no_auth_method": {
            "count": len(no_auth_method),
            "users": no_auth_method
        }
    }
