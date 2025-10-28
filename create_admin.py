#!/usr/bin/env python3
"""
Create Admin User Script for HireBahamas Platform
Creates a default admin account for platform management
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

import bcrypt
from app.database import AsyncSessionLocal
from app.models import User
from sqlalchemy import select


async def create_admin_user():
    """Create an admin user for the HireBahamas platform"""

    # Admin user details
    admin_data = {
        "email": "admin@hiremebahamas.com",
        "password": "Admin123!",
        "first_name": "Admin",
        "last_name": "User",
        "phone": "+1-242-555-0100",
        "location": "Nassau, Bahamas",
        "bio": "Platform Administrator for HireMeBahamas - Managing the job platform to connect Bahamian talent with opportunities.",
        "skills": "Platform Management, User Support, Content Moderation, Analytics",
        "experience": "Platform Administration, Community Management, Customer Support",
        "education": "Administrative Experience",
        "is_active": True,
        "is_admin": True,
        "role": "admin",
    }

    async with AsyncSessionLocal() as session:
        try:
            # Check if admin user already exists
            result = await session.execute(
                select(User).where(User.email == admin_data["email"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"❌ Admin user already exists with email: {admin_data['email']}")
                print(f"   User ID: {existing_user.id}")
                print(f"   Name: {existing_user.full_name}")
                print(f"   Is Admin: {existing_user.is_admin}")
                return False

            # Hash the password
            password_bytes = admin_data["password"].encode("utf-8")
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)

            # Create admin user
            admin_user = User(
                email=admin_data["email"],
                hashed_password=hashed_password.decode("utf-8"),
                first_name=admin_data["first_name"],
                last_name=admin_data["last_name"],
                phone=admin_data["phone"],
                location=admin_data["location"],
                bio=admin_data["bio"],
                skills=admin_data["skills"],
                experience=admin_data["experience"],
                education=admin_data["education"],
                is_active=admin_data["is_active"],
                is_admin=admin_data["is_admin"],
                role=admin_data["role"],
            )

            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            print("✅ Admin user created successfully!")
            print("=" * 50)
            print("📧 ADMIN LOGIN CREDENTIALS")
            print("=" * 50)
            print(f"📧 Email:    {admin_data['email']}")
            print(f"🔑 Password: {admin_data['password']}")
            print(f"👤 Name:     {admin_data['first_name']} {admin_data['last_name']}")
            print(f"📱 Phone:    {admin_data['phone']}")
            print(f"📍 Location: {admin_data['location']}")
            print(f"🎯 Role:     {admin_data['role'].upper()}")
            print(f"🆔 User ID:  {admin_user.id}")
            print("=" * 50)
            print("⚠️  IMPORTANT SECURITY NOTES:")
            print("   1. Change the default password after first login")
            print("   2. Use a strong, unique password")
            print("   3. Enable two-factor authentication if available")
            print("   4. Keep admin credentials secure")
            print("=" * 50)

            return True

        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating admin user: {e}")
            return False


async def main():
    """Main function"""
    print("🎯 HireMeBahamas Admin User Creation")
    print("=" * 40)

    try:
        success = await create_admin_user()
        if success:
            print("\n🎉 Admin account setup complete!")
            print("💻 You can now log in to the admin panel")
        else:
            print("\n❌ Admin account setup failed or already exists")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
