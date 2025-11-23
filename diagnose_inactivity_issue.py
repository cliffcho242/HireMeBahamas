#!/usr/bin/env python3
"""
Diagnostic tool to identify why users can't sign in after inactivity.

This tool checks:
1. Database file existence and permissions
2. User accounts status
3. Token expiration settings
4. File system persistence
5. Logs user activity
"""

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

def check_database_file():
    """Check database file status"""
    print("=" * 80)
    print("1. DATABASE FILE CHECK")
    print("=" * 80)
    
    db_path = "hiremebahamas.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file NOT FOUND: {db_path}")
        print("   This could mean:")
        print("   - Database was never created")
        print("   - Database file was deleted")
        print("   - Running in a different directory")
        return False
    
    print(f"✓ Database file exists: {db_path}")
    abs_path = os.path.abspath(db_path)
    print(f"  Absolute path: {abs_path}")
    print(f"  Size: {os.path.getsize(db_path)} bytes")
    print(f"  Permissions: {oct(os.stat(db_path).st_mode)[-3:]}")
    print(f"  Last modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    
    # Check if directory is writable
    db_dir = os.path.dirname(abs_path) or "."
    if os.access(db_dir, os.W_OK):
        print(f"✓ Directory is writable")
    else:
        print(f"❌ Directory is NOT writable")
        return False
    
    return True


def check_users():
    """Check user accounts"""
    print("\n" + "=" * 80)
    print("2. USER ACCOUNTS CHECK")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect("hiremebahamas.db")
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, email, first_name, last_name, is_active, is_available_for_hire, last_login FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("❌ NO USERS FOUND in database")
            print("   Possible causes:")
            print("   - Users were never registered")
            print("   - Database was cleared")
            print("   - Users were deleted")
            return False
        
        print(f"✓ Found {len(users)} user(s):\n")
        for u in users:
            user_id, email, first, last, active, hire_me, last_login = u
            status = "ACTIVE" if active else "INACTIVE"
            hire_status = "ON" if hire_me else "OFF"
            last_login_str = last_login if last_login else "Never"
            
            print(f"  User ID: {user_id}")
            print(f"  Email: {email}")
            print(f"  Name: {first} {last}")
            print(f"  Status: {status}")
            print(f"  Hire Me: {hire_status}")
            print(f"  Last Login: {last_login_str}")
            print()
        
        # Check specifically for the user's emails
        target_emails = ["cliffyv24@gmail.com", "cliff242@gmail.com"]
        cursor.execute("SELECT email FROM users WHERE email IN (?, ?)", target_emails)
        found_emails = [row[0] for row in cursor.fetchall()]
        
        print(f"Target user emails check:")
        for email in target_emails:
            if email in found_emails:
                print(f"  ✓ {email} - FOUND")
            else:
                print(f"  ❌ {email} - NOT FOUND")
        
        conn.close()
        return len(found_emails) > 0
        
    except sqlite3.OperationalError as e:
        print(f"❌ Database error: {e}")
        if "no such table" in str(e):
            print("   The 'users' table doesn't exist!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_token_config():
    """Check token configuration"""
    print("\n" + "=" * 80)
    print("3. TOKEN CONFIGURATION CHECK")
    print("=" * 80)
    
    # Check environment variables
    token_exp = os.getenv("TOKEN_EXPIRATION_DAYS", "7")
    print(f"Token expiration: {token_exp} days")
    
    if int(token_exp) < 7:
        print(f"⚠️  Warning: Token expiration is short ({token_exp} days)")
        print(f"   Users will need to re-login frequently")
    else:
        print(f"✓ Token expiration is reasonable")
    
    return True


def check_persistence_setup():
    """Check if environment is set up for persistence"""
    print("\n" + "=" * 80)
    print("4. PERSISTENCE SETUP CHECK")
    print("=" * 80)
    
    # Check if DATABASE_URL is set (production)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"✓ DATABASE_URL is set (using PostgreSQL)")
        print(f"  Database: {db_url.split('@')[1] if '@' in db_url else 'configured'}")
        print(f"  This ensures data persists across restarts")
        return True
    else:
        print(f"⚠️  DATABASE_URL not set (using SQLite)")
        print(f"  For production, set DATABASE_URL to ensure persistence")
        print(f"  Example: DATABASE_URL=postgresql://user:pass@host:5432/db")
        
        # Check if .gitignore excludes the database
        if os.path.exists(".gitignore"):
            with open(".gitignore") as f:
                if "*.db" in f.read() or "hiremebahamas.db" in f.read():
                    print(f"\n  ⚠️  IMPORTANT: *.db is in .gitignore")
                    print(f"     Database file will NOT be committed to git")
                    print(f"     On deployment, database will be empty/reset")
                    print(f"\n     SOLUTION for production:")
                    print(f"     1. Use PostgreSQL (set DATABASE_URL)")
                    print(f"     2. Or ensure persistent volume for SQLite")
        
        return False


def provide_recommendations():
    """Provide recommendations to fix the issue"""
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    print("\nTo prevent 'can't sign in after inactivity' issue:\n")
    
    print("1. FOR PRODUCTION DEPLOYMENT:")
    print("   ✓ Use PostgreSQL (not SQLite)")
    print("   ✓ Set DATABASE_URL environment variable")
    print("   ✓ Example: DATABASE_URL=postgresql://user:pass@host:5432/hiremebahamas")
    
    print("\n2. IF USING SQLITE:")
    print("   ✓ Ensure database file is in a persistent directory")
    print("   ✓ Do NOT store in /tmp or ephemeral storage")
    print("   ✓ Set proper file permissions (644)")
    print("   ✓ Use a persistent volume mount")
    
    print("\n3. TOKEN CONFIGURATION:")
    print("   ✓ Set TOKEN_EXPIRATION_DAYS=30 (or more)")
    print("   ✓ This reduces re-login frequency")
    
    print("\n4. BACKUP:")
    print("   ✓ Regularly backup the database")
    print("   ✓ For SQLite: cp hiremebahamas.db hiremebahamas.db.backup")
    print("   ✓ For PostgreSQL: use pg_dump")
    
    print()


def main():
    print("\n" + "=" * 80)
    print("INACTIVITY LOGIN ISSUE DIAGNOSTIC TOOL")
    print("=" * 80)
    print()
    
    issues_found = []
    
    # Run all checks
    if not check_database_file():
        issues_found.append("Database file missing or not accessible")
    
    if not check_users():
        issues_found.append("No users found in database")
    
    check_token_config()
    
    if not check_persistence_setup():
        issues_found.append("Persistence not properly configured")
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if issues_found:
        print(f"\n❌ ISSUES FOUND ({len(issues_found)}):")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print()
        provide_recommendations()
    else:
        print("\n✅ No issues detected!")
        print("   System is configured correctly for data persistence")
        print()


if __name__ == "__main__":
    main()
