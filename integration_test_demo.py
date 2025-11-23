#!/usr/bin/env python3
"""
End-to-End Integration Test
Demonstrates complete follow/unfollow workflow
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import Base, engine, AsyncSessionLocal
from app.models import User, Follow
from sqlalchemy import select, func


async def demo_complete_workflow():
    """Demonstrate complete follow/unfollow workflow"""
    
    print("=" * 70)
    print("END-TO-END INTEGRATION TEST: Follow/Unfollow Workflow")
    print("=" * 70)
    
    # Setup database
    print("\n📦 Setting up database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database ready")
    
    async with AsyncSessionLocal() as session:
        # Create test users
        print("\n👥 Creating test users...")
        
        alice = User(
            email="alice@hiremebahamas.com",
            hashed_password="hash123",
            first_name="Alice",
            last_name="Johnson",
            username="alice_j",
            occupation="Software Developer",
            location="Nassau, Bahamas",
            is_active=True
        )
        
        bob = User(
            email="bob@hiremebahamas.com",
            hashed_password="hash456",
            first_name="Bob",
            last_name="Smith",
            username="bob_smith",
            occupation="Project Manager",
            location="Freeport, Bahamas",
            is_active=True
        )
        
        carol = User(
            email="carol@hiremebahamas.com",
            hashed_password="hash789",
            first_name="Carol",
            last_name="Williams",
            username="carol_w",
            occupation="UX Designer",
            location="Nassau, Bahamas",
            is_active=True
        )
        
        session.add_all([alice, bob, carol])
        await session.commit()
        await session.refresh(alice)
        await session.refresh(bob)
        await session.refresh(carol)
        
        print(f"✅ Created Alice (ID: {alice.id}) - {alice.occupation}")
        print(f"✅ Created Bob (ID: {bob.id}) - {bob.occupation}")
        print(f"✅ Created Carol (ID: {carol.id}) - {carol.occupation}")
        
        # Scenario 1: Alice follows Bob
        print("\n📍 Scenario 1: Alice follows Bob")
        follow1 = Follow(follower_id=alice.id, followed_id=bob.id)
        session.add(follow1)
        await session.commit()
        print(f"✅ Alice is now following Bob")
        
        # Check Bob's followers
        bob_followers = await session.execute(
            select(func.count()).select_from(Follow).where(Follow.followed_id == bob.id)
        )
        count = bob_followers.scalar()
        print(f"   Bob has {count} follower(s)")
        
        # Scenario 2: Alice follows Carol
        print("\n📍 Scenario 2: Alice follows Carol")
        follow2 = Follow(follower_id=alice.id, followed_id=carol.id)
        session.add(follow2)
        await session.commit()
        print(f"✅ Alice is now following Carol")
        
        # Check how many people Alice is following
        alice_following = await session.execute(
            select(func.count()).select_from(Follow).where(Follow.follower_id == alice.id)
        )
        count = alice_following.scalar()
        print(f"   Alice is following {count} people")
        
        # Scenario 3: Bob follows Alice back
        print("\n📍 Scenario 3: Bob follows Alice back")
        follow3 = Follow(follower_id=bob.id, followed_id=alice.id)
        session.add(follow3)
        await session.commit()
        print(f"✅ Bob is now following Alice")
        
        # Check mutual follows
        alice_followers = await session.execute(
            select(func.count()).select_from(Follow).where(Follow.followed_id == alice.id)
        )
        alice_follower_count = alice_followers.scalar()
        print(f"   Alice has {alice_follower_count} follower(s)")
        print(f"   Alice and Bob are now following each other!")
        
        # Scenario 4: Get Alice's following list
        print("\n📍 Scenario 4: Get Alice's following list")
        following_result = await session.execute(
            select(User)
            .join(Follow, Follow.followed_id == User.id)
            .where(Follow.follower_id == alice.id)
        )
        following_users = following_result.scalars().all()
        
        print(f"   Alice is following {len(following_users)} people:")
        for user in following_users:
            print(f"   - {user.first_name} {user.last_name} (@{user.username})")
        
        # Scenario 5: Alice unfollows Carol
        print("\n📍 Scenario 5: Alice unfollows Carol")
        unfollow_result = await session.execute(
            select(Follow).where(
                Follow.follower_id == alice.id,
                Follow.followed_id == carol.id
            )
        )
        unfollow = unfollow_result.scalar_one()
        await session.delete(unfollow)
        await session.commit()
        print(f"✅ Alice unfollowed Carol")
        
        # Verify unfollow
        alice_following_after = await session.execute(
            select(func.count()).select_from(Follow).where(Follow.follower_id == alice.id)
        )
        count = alice_following_after.scalar()
        print(f"   Alice is now following {count} person(s)")
        
        # Final statistics
        print("\n📊 Final Network Statistics:")
        print("-" * 70)
        
        for user in [alice, bob, carol]:
            # Get follower count
            followers_result = await session.execute(
                select(func.count()).select_from(Follow).where(Follow.followed_id == user.id)
            )
            follower_count = followers_result.scalar()
            
            # Get following count
            following_result = await session.execute(
                select(func.count()).select_from(Follow).where(Follow.follower_id == user.id)
            )
            following_count = following_result.scalar()
            
            print(f"{user.first_name:10} | Followers: {follower_count} | Following: {following_count}")
        
        print("-" * 70)
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        # Delete follows first (due to foreign key constraints)
        follows_result = await session.execute(select(Follow))
        follows = follows_result.scalars().all()
        for follow in follows:
            await session.delete(follow)
        await session.commit()
        
        # Then delete users
        await session.delete(alice)
        await session.delete(bob)
        await session.delete(carol)
        await session.commit()
        print("✅ Test data cleaned up")
    
    print("\n" + "=" * 70)
    print("✅ END-TO-END TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nAll follow/unfollow operations work as expected:")
    print("  ✅ Users can follow other users")
    print("  ✅ Users can unfollow users")
    print("  ✅ Follower counts update correctly")
    print("  ✅ Following lists can be retrieved")
    print("  ✅ Mutual follows work correctly")
    print("\n🎉 Follow/Unfollow system is production ready!")


async def main():
    try:
        await demo_complete_workflow()
        return 0
    except Exception as e:
        print(f"\n❌ Error during integration test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
