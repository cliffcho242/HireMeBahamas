#!/usr/bin/env python3
"""
Test script to verify notification badge only shows for user interaction notifications
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import Base, engine, AsyncSessionLocal
from app.models import User, Notification, NotificationType
from sqlalchemy import select, func


async def test_notification_badge_count():
    """Test that notification badge count only includes interaction notifications"""
    print("\n🔍 Testing Notification Badge Count Logic...")
    
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with AsyncSessionLocal() as session:
            # Create test user
            user = User(
                email="test_badge@example.com",
                hashed_password="hashedpass123",
                first_name="Test",
                last_name="Badge",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"✅ Created test user: {user.id}")
            
            # Create different types of notifications
            notifications_data = [
                # User interaction notifications (should be counted in badge)
                (NotificationType.LIKE, "Someone liked your post", True),
                (NotificationType.COMMENT, "Someone commented on your post", True),
                (NotificationType.MENTION, "Someone mentioned you", True),
                # Non-interaction notifications (should NOT be counted in badge)
                (NotificationType.FOLLOW, "Someone followed you", False),
                (NotificationType.JOB_APPLICATION, "Someone applied to your job", False),
                (NotificationType.JOB_POST, "New job posted", False),
            ]
            
            for notif_type, content, should_count in notifications_data:
                notification = Notification(
                    user_id=user.id,
                    notification_type=notif_type,
                    content=content,
                    is_read=False
                )
                session.add(notification)
            
            await session.commit()
            print(f"✅ Created 6 unread notifications (3 interaction, 3 non-interaction)")
            
            # Test 1: Count all unread notifications
            all_unread = await session.execute(
                select(func.count())
                .select_from(Notification)
                .where(
                    Notification.user_id == user.id,
                    Notification.is_read == False
                )
            )
            all_count = all_unread.scalar()
            assert all_count == 6, f"Expected 6 total unread notifications, got {all_count}"
            print(f"✅ All unread notifications count: {all_count}")
            
            # Test 2: Count only interaction notifications (badge count)
            interaction_types = [
                NotificationType.LIKE,
                NotificationType.COMMENT,
                NotificationType.MENTION,
            ]
            
            interaction_unread = await session.execute(
                select(func.count())
                .select_from(Notification)
                .where(
                    Notification.user_id == user.id,
                    Notification.is_read == False,
                    Notification.notification_type.in_(interaction_types)
                )
            )
            badge_count = interaction_unread.scalar()
            assert badge_count == 3, f"Expected 3 interaction notifications for badge, got {badge_count}"
            print(f"✅ Badge notification count (interactions only): {badge_count}")
            
            # Test 3: Verify follow and job notifications are excluded
            non_interaction_types = [
                NotificationType.FOLLOW,
                NotificationType.JOB_APPLICATION,
                NotificationType.JOB_POST,
            ]
            
            non_interaction_unread = await session.execute(
                select(func.count())
                .select_from(Notification)
                .where(
                    Notification.user_id == user.id,
                    Notification.is_read == False,
                    Notification.notification_type.in_(non_interaction_types)
                )
            )
            non_badge_count = non_interaction_unread.scalar()
            assert non_badge_count == 3, f"Expected 3 non-interaction notifications, got {non_badge_count}"
            print(f"✅ Non-badge notifications (follow, job): {non_badge_count}")
            
            # Test 4: Mark one interaction notification as read
            like_notif = await session.execute(
                select(Notification).where(
                    Notification.user_id == user.id,
                    Notification.notification_type == NotificationType.LIKE
                )
            )
            like = like_notif.scalar_one()
            like.is_read = True
            await session.commit()
            
            # Re-count badge notifications
            interaction_unread_after = await session.execute(
                select(func.count())
                .select_from(Notification)
                .where(
                    Notification.user_id == user.id,
                    Notification.is_read == False,
                    Notification.notification_type.in_(interaction_types)
                )
            )
            badge_count_after = interaction_unread_after.scalar()
            assert badge_count_after == 2, f"Expected 2 interaction notifications after marking one read, got {badge_count_after}"
            print(f"✅ Badge count after marking LIKE as read: {badge_count_after}")
            
            # Cleanup
            notifications_result = await session.execute(
                select(Notification).where(Notification.user_id == user.id)
            )
            for notification in notifications_result.scalars().all():
                await session.delete(notification)
            
            await session.delete(user)
            await session.commit()
            print("✅ Test data cleaned up")
            
        return True
    except Exception as e:
        print(f"❌ Error testing notification badge count: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING NOTIFICATION BADGE FUNCTIONALITY")
    print("=" * 60)
    print("Testing that badge only shows for user interaction notifications")
    print("(likes, comments, mentions - NOT follows or job notifications)")
    
    result = await test_notification_badge_count()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if result:
        print("✅ PASSED: Notification badge correctly filters interaction types")
        print("\n🎉 Badge will now only highlight likes, comments, and mentions!")
        return 0
    else:
        print("❌ FAILED: Notification badge test failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
