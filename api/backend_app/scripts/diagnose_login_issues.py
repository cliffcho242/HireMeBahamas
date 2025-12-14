#!/usr/bin/env python3
"""
Diagnose login issues for all users.

This script checks all users for potential login problems:
- Missing passwords (OAuth users without password set)
- Inactive accounts
- Accounts with many failed login attempts
- Users created but never logged in
- Users with no authentication method

Run this script manually to identify and optionally fix common issues.

Usage:
    python -m backend_app.scripts.diagnose_login_issues
    
    Or from the api directory:
    python -m backend_app.scripts.diagnose_login_issues --fix
"""
import asyncio
import argparse
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend_app.database import AsyncSessionLocal
from backend_app.models import User, LoginAttempt


async def diagnose_login_issues(fix_issues: bool = False):
    """Run comprehensive diagnosis of user login issues
    
    Args:
        fix_issues: If True, attempt to fix common issues automatically
    """
    print("=" * 80)
    print("USER LOGIN DIAGNOSTIC REPORT")
    print(f"Generated: {datetime.utcnow().isoformat()}")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        # 1. Check for users with no authentication method
        print("1. USERS WITH NO AUTHENTICATION METHOD")
        print("-" * 80)
        result = await db.execute(
            select(User).where(
                and_(
                    User.hashed_password.is_(None),
                    User.oauth_provider.is_(None)
                )
            )
        )
        no_auth_users = result.scalars().all()
        
        if no_auth_users:
            print(f"❌ Found {len(no_auth_users)} users with no authentication method:")
            for user in no_auth_users:
                print(f"   - ID: {user.id}, Email: {user.email}, Created: {user.created_at}")
                if fix_issues:
                    # These users need manual intervention - can't auto-fix
                    print(f"     ⚠️  Manual intervention required - user needs to reset password or use OAuth")
        else:
            print("✅ All users have an authentication method")
        print()
        
        # 2. Check for inactive accounts
        print("2. INACTIVE ACCOUNTS")
        print("-" * 80)
        result = await db.execute(
            select(User).where(User.is_active == False)
        )
        inactive_users = result.scalars().all()
        
        if inactive_users:
            print(f"⚠️  Found {len(inactive_users)} inactive accounts:")
            for user in inactive_users:
                print(f"   - ID: {user.id}, Email: {user.email}, Last login: {user.last_login}")
                if fix_issues:
                    print(f"     ℹ️  Skipping - inactive accounts require manual review")
        else:
            print("✅ No inactive accounts found")
        print()
        
        # 3. Check for users created but never logged in (30+ days)
        print("3. USERS CREATED BUT NEVER LOGGED IN (30+ DAYS)")
        print("-" * 80)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        result = await db.execute(
            select(User).where(
                and_(
                    User.last_login.is_(None),
                    User.created_at < thirty_days_ago
                )
            )
        )
        never_logged_in = result.scalars().all()
        
        if never_logged_in:
            print(f"⚠️  Found {len(never_logged_in)} users who never logged in:")
            for user in never_logged_in:
                days_old = (datetime.utcnow() - user.created_at).days if user.created_at else 0
                print(f"   - ID: {user.id}, Email: {user.email}, Created {days_old} days ago")
        else:
            print("✅ All users have logged in at least once (or were created recently)")
        print()
        
        # 4. Check for users with excessive failed login attempts
        print("4. USERS WITH EXCESSIVE FAILED LOGIN ATTEMPTS (10+ in last 30 days)")
        print("-" * 80)
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
        )
        high_failure_users = result.all()
        
        if high_failure_users:
            print(f"⚠️  Found {len(high_failure_users)} users with many failed attempts:")
            for user_id, email, failed_count in high_failure_users:
                print(f"   - ID: {user_id}, Email: {email}, Failed attempts: {failed_count}")
                
                # Get recent failure reasons
                failure_result = await db.execute(
                    select(LoginAttempt.failure_reason, func.count(LoginAttempt.id))
                    .where(
                        and_(
                            LoginAttempt.user_id == user_id,
                            LoginAttempt.success == False,
                            LoginAttempt.timestamp >= thirty_days_ago
                        )
                    )
                    .group_by(LoginAttempt.failure_reason)
                )
                
                reasons = failure_result.all()
                if reasons:
                    print(f"     Reasons:")
                    for reason, count in reasons:
                        print(f"       • {reason}: {count} times")
        else:
            print("✅ No users with excessive failed login attempts")
        print()
        
        # 5. Summary statistics
        print("5. SUMMARY STATISTICS")
        print("-" * 80)
        
        # Total users
        result = await db.execute(select(func.count(User.id)))
        total_users = result.scalar()
        
        # Users who have logged in
        result = await db.execute(
            select(func.count(User.id)).where(User.last_login.isnot(None))
        )
        users_with_logins = result.scalar()
        
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
        
        print(f"Total users: {total_users}")
        print(f"Users who have logged in: {users_with_logins} ({users_with_logins/total_users*100:.1f}%)")
        print(f"Users who never logged in: {total_users - users_with_logins}")
        print(f"OAuth users: {oauth_users}")
        print(f"Password users: {password_users}")
        print()
        
        # 6. Recommendations
        print("6. RECOMMENDATIONS")
        print("-" * 80)
        
        recommendations = []
        
        if no_auth_users:
            recommendations.append(
                f"• {len(no_auth_users)} users have no authentication method - contact them to complete setup"
            )
        
        if len(never_logged_in) > 10:
            recommendations.append(
                f"• {len(never_logged_in)} users never logged in - consider email campaign or account cleanup"
            )
        
        if high_failure_users:
            recommendations.append(
                f"• {len(high_failure_users)} users have excessive failed logins - reach out to provide support"
            )
        
        if not recommendations:
            print("✅ No major issues found. System is healthy!")
        else:
            for rec in recommendations:
                print(rec)
        
        print()
        print("=" * 80)
        print("END OF REPORT")
        print("=" * 80)


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Diagnose login issues for all users"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to automatically fix common issues"
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(diagnose_login_issues(fix_issues=args.fix))
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
