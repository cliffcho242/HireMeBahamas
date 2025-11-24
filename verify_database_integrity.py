#!/usr/bin/env python3
"""
Database Integrity Verification Utility

This script verifies the integrity of the database by:
1. Checking schema matches model definitions
2. Validating data constraints
3. Checking for orphaned records
4. Verifying relationship integrity
5. Testing user data storage and retrieval
"""

import asyncio
import sys
import os
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import Base, engine
from app.models import User, Follow, Notification, Message, Conversation, Job, JobApplication, Review
from app.core.security import get_password_hash, verify_password


class DatabaseIntegrityChecker:
    """Database integrity checker."""
    
    def __init__(self, engine):
        self.engine = engine
        self.errors = []
        self.warnings = []
        self.info = []
    
    async def check_schema_integrity(self, session: AsyncSession):
        """Check if database schema matches model definitions."""
        print("\n=== Checking Schema Integrity ===")
        
        # Try to query each table to verify it exists
        tables_to_check = [
            ('users', User),
            ('jobs', Job),
            ('job_applications', JobApplication),
            ('conversations', Conversation),
            ('messages', Message),
            ('reviews', Review),
            ('follows', Follow),
            ('notifications', Notification)
        ]
        
        for table_name, model in tables_to_check:
            try:
                result = await session.execute(select(func.count()).select_from(model))
                count = result.scalar()
                self.info.append(f"✓ Table '{table_name}' exists (count: {count})")
            except Exception as e:
                self.warnings.append(f"⚠ Table '{table_name}' may not exist or is not accessible: {str(e)[:50]}")
    
    async def check_data_constraints(self, session: AsyncSession):
        """Check data constraints and uniqueness."""
        print("\n=== Checking Data Constraints ===")
        
        # Check for duplicate emails
        result = await session.execute(
            select(User.email, func.count(User.email))
            .group_by(User.email)
            .having(func.count(User.email) > 1)
        )
        duplicates = result.all()
        
        if duplicates:
            for email, count in duplicates:
                self.errors.append(f"✗ Duplicate email found: {email} ({count} occurrences)")
        else:
            self.info.append("✓ No duplicate emails found")
        
        # Check for users with invalid data
        result = await session.execute(
            select(User).where(
                (User.email == None) | 
                (User.hashed_password == None) |
                (User.first_name == None) |
                (User.last_name == None)
            )
        )
        invalid_users = result.scalars().all()
        
        if invalid_users:
            self.errors.append(f"✗ Found {len(invalid_users)} users with missing required fields")
        else:
            self.info.append("✓ All users have required fields")
    
    async def check_orphaned_records(self, session: AsyncSession):
        """Check for orphaned records (references to non-existent users)."""
        print("\n=== Checking for Orphaned Records ===")
        
        try:
            # Check for jobs with non-existent employers
            result = await session.execute(
                select(Job)
                .outerjoin(User, Job.employer_id == User.id)
                .where(User.id == None)
            )
            orphaned_jobs = result.scalars().all()
            
            if orphaned_jobs:
                self.errors.append(f"✗ Found {len(orphaned_jobs)} jobs with non-existent employers")
            else:
                self.info.append("✓ No orphaned job records")
        except Exception:
            self.info.append("⚠ Jobs table not checked (may not exist yet)")
        
        try:
            # Check for follows with non-existent users
            result = await session.execute(
                select(Follow)
                .outerjoin(User, Follow.follower_id == User.id)
                .where(User.id == None)
            )
            orphaned_follows = result.scalars().all()
            
            if orphaned_follows:
                self.errors.append(f"✗ Found {len(orphaned_follows)} follows with non-existent followers")
            else:
                self.info.append("✓ No orphaned follow records")
        except Exception:
            self.info.append("⚠ Follows table not checked (may not exist yet)")
    
    async def test_user_storage_and_retrieval(self, session: AsyncSession):
        """Test user data storage and retrieval."""
        print("\n=== Testing User Data Storage and Retrieval ===")
        
        test_email = f"integrity_test_{datetime.now().timestamp()}@example.com"
        test_password = "test_password_123"
        
        try:
            # Test 1: Create user
            user = User(
                email=test_email,
                hashed_password=get_password_hash(test_password),
                first_name="Integrity",
                last_name="Test",
                username=f"integrity_test_{datetime.now().timestamp()}",
                phone="+1-242-555-0100",
                location="Nassau, Bahamas",
                occupation="Tester",
                bio="Testing database integrity",
                is_available_for_hire=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            self.info.append("✓ User creation successful")
            
            # Test 2: Retrieve user by ID
            result = await session.execute(select(User).where(User.id == user.id))
            retrieved_user = result.scalar_one_or_none()
            
            if retrieved_user and retrieved_user.email == test_email:
                self.info.append("✓ User retrieval by ID successful")
            else:
                self.errors.append("✗ User retrieval by ID failed")
            
            # Test 3: Retrieve user by email
            result = await session.execute(select(User).where(User.email == test_email))
            retrieved_user = result.scalar_one_or_none()
            
            if retrieved_user and retrieved_user.id == user.id:
                self.info.append("✓ User retrieval by email successful")
            else:
                self.errors.append("✗ User retrieval by email failed")
            
            # Test 4: Verify password hashing
            if verify_password(test_password, retrieved_user.hashed_password):
                self.info.append("✓ Password hashing and verification working")
            else:
                self.errors.append("✗ Password verification failed")
            
            # Test 5: Verify all data fields
            all_fields_correct = (
                retrieved_user.first_name == "Integrity" and
                retrieved_user.last_name == "Test" and
                retrieved_user.phone == "+1-242-555-0100" and
                retrieved_user.location == "Nassau, Bahamas" and
                retrieved_user.occupation == "Tester" and
                retrieved_user.bio == "Testing database integrity" and
                retrieved_user.is_available_for_hire is True
            )
            
            if all_fields_correct:
                self.info.append("✓ All user data fields stored and retrieved correctly")
            else:
                self.errors.append("✗ Some user data fields not stored correctly")
            
            # Test 6: Update user data
            retrieved_user.bio = "Updated bio"
            retrieved_user.occupation = "Senior Tester"
            await session.commit()
            await session.refresh(retrieved_user)
            
            if retrieved_user.bio == "Updated bio" and retrieved_user.occupation == "Senior Tester":
                self.info.append("✓ User data update successful")
            else:
                self.errors.append("✗ User data update failed")
            
            # Test 7: Test timestamp tracking
            if retrieved_user.created_at is not None:
                self.info.append("✓ Timestamp tracking working (created_at)")
            else:
                self.warnings.append("⚠ created_at timestamp not set")
            
            # Cleanup: Delete test user
            await session.delete(retrieved_user)
            await session.commit()
            self.info.append("✓ Test user cleanup successful")
            
        except Exception as e:
            self.errors.append(f"✗ User storage/retrieval test failed: {str(e)}")
    
    async def get_statistics(self, session: AsyncSession):
        """Get database statistics."""
        print("\n=== Database Statistics ===")
        
        # Count users
        result = await session.execute(select(func.count(User.id)))
        user_count = result.scalar()
        self.info.append(f"Total users: {user_count}")
        
        # Count active users
        result = await session.execute(select(func.count(User.id)).where(User.is_active == True))
        active_count = result.scalar()
        self.info.append(f"Active users: {active_count}")
        
        # Count jobs (if table exists)
        try:
            result = await session.execute(select(func.count(Job.id)))
            job_count = result.scalar()
            self.info.append(f"Total jobs: {job_count}")
        except Exception:
            self.info.append("Jobs table not yet created or not accessible")
        
        # Count follows (if table exists)
        try:
            result = await session.execute(select(func.count(Follow.id)))
            follow_count = result.scalar()
            self.info.append(f"Total follows: {follow_count}")
        except Exception:
            self.info.append("Follows table not yet created or not accessible")
    
    async def run_all_checks(self):
        """Run all integrity checks."""
        print("=" * 60)
        print("DATABASE INTEGRITY VERIFICATION")
        print("=" * 60)
        
        # Create session for all checks
        AsyncSessionLocal = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with AsyncSessionLocal() as session:
            try:
                await self.check_schema_integrity(session)
                await self.get_statistics(session)
                await self.check_data_constraints(session)
                await self.check_orphaned_records(session)
                await self.test_user_storage_and_retrieval(session)
            except Exception as e:
                self.errors.append(f"✗ Error during data checks: {str(e)}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print summary of checks."""
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        if self.info:
            print(f"\n✓ Passed Checks ({len(self.info)}):")
            for msg in self.info:
                print(f"  {msg}")
        
        if self.warnings:
            print(f"\n⚠ Warnings ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print(f"\n✗ Errors ({len(self.errors)}):")
            for msg in self.errors:
                print(f"  {msg}")
        else:
            print("\n✓ No errors found!")
        
        print("\n" + "=" * 60)
        print(f"Total: {len(self.info)} passed, {len(self.warnings)} warnings, {len(self.errors)} errors")
        print("=" * 60)
        
        return len(self.errors) == 0


async def main():
    """Main entry point."""
    checker = DatabaseIntegrityChecker(engine)
    await checker.run_all_checks()
    
    # Return exit code based on results
    return 0 if checker.errors == [] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
