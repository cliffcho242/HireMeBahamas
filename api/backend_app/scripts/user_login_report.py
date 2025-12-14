#!/usr/bin/env python3
"""
Generate comprehensive CSV report of all users and their login activity.

This script creates a detailed CSV report with:
- User ID, email, name
- Created date and last login date
- Days since last login
- Account status (active/inactive)
- Authentication method
- Failed login attempts count

The report is saved to reports/user_login_report_[date].csv

Usage:
    python -m backend_app.scripts.user_login_report
    
    Or from the api directory:
    python -m backend_app.scripts.user_login_report --output /path/to/custom/location.csv
"""
import asyncio
import argparse
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend_app.database import AsyncSessionLocal
from backend_app.models import User, LoginAttempt


async def generate_user_login_report(output_file: str = None):
    """Generate comprehensive CSV report of all users
    
    Args:
        output_file: Custom output file path (optional)
    """
    # Determine output file path
    if not output_file:
        # Create reports directory if it doesn't exist
        reports_dir = Path(__file__).parent.parent.parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Generate filename with current date
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = reports_dir / f"user_login_report_{date_str}.csv"
    else:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating user login report...")
    print(f"Output file: {output_file}")
    print()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    async with AsyncSessionLocal() as db:
        # Get all users
        result = await db.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        
        print(f"Processing {len(users)} users...")
        
        # Prepare CSV data
        csv_data = []
        
        for user in users:
            # Calculate days since login
            days_since_login = None
            if user.last_login:
                days_since_login = (datetime.utcnow() - user.last_login).days
            
            # Determine authentication method
            auth_method = "password"
            if user.oauth_provider:
                auth_method = f"oauth_{user.oauth_provider}"
            elif not user.hashed_password:
                auth_method = "none"
            
            # Get failed login attempts count (last 30 days)
            result = await db.execute(
                select(func.count(LoginAttempt.id))
                .where(
                    and_(
                        LoginAttempt.user_id == user.id,
                        LoginAttempt.success == False,
                        LoginAttempt.timestamp >= thirty_days_ago
                    )
                )
            )
            failed_attempts = result.scalar() or 0
            
            # Add to CSV data
            csv_data.append({
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat() if user.created_at else "",
                "last_login": user.last_login.isoformat() if user.last_login else "",
                "days_since_login": days_since_login if days_since_login is not None else "",
                "is_active": "yes" if user.is_active else "no",
                "is_admin": "yes" if user.is_admin else "no",
                "auth_method": auth_method,
                "failed_attempts_30d": failed_attempts,
                "location": user.location or "",
                "role": user.role or ""
            })
        
        # Write to CSV
        fieldnames = [
            "id", "email", "first_name", "last_name",
            "created_at", "last_login", "days_since_login",
            "is_active", "is_admin", "auth_method",
            "failed_attempts_30d", "location", "role"
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"✅ Report generated successfully!")
        print(f"📄 File: {output_file}")
        print(f"📊 Total users: {len(csv_data)}")
        print()
        
        # Print summary statistics
        print("SUMMARY STATISTICS")
        print("-" * 80)
        
        active_users = sum(1 for row in csv_data if row["is_active"] == "yes")
        users_with_logins = sum(1 for row in csv_data if row["last_login"])
        never_logged_in = len(csv_data) - users_with_logins
        oauth_users = sum(1 for row in csv_data if row["auth_method"].startswith("oauth"))
        password_users = sum(1 for row in csv_data if row["auth_method"] == "password")
        users_with_failures = sum(1 for row in csv_data if int(row["failed_attempts_30d"] or 0) > 0)
        
        print(f"Total users: {len(csv_data)}")
        print(f"Active users: {active_users}")
        print(f"Users who have logged in: {users_with_logins}")
        print(f"Users who never logged in: {never_logged_in}")
        print(f"OAuth users: {oauth_users}")
        print(f"Password users: {password_users}")
        print(f"Users with failed attempts (30d): {users_with_failures}")
        print()


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Generate CSV report of all users and their login activity"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Custom output file path (default: reports/user_login_report_[date].csv)"
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(generate_user_login_report(output_file=args.output))
    except KeyboardInterrupt:
        print("\n\nReport generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
