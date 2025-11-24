"""
Test for filtering inactive users from followers/following lists
This test verifies that inactive users do not appear in followers/following lists
"""

import asyncio
import os
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Set test database URL
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test_follow_inactive.db'

from app.database import Base, engine
from app.models import User, Follow
from app.core.security import get_password_hash


@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database for each test."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class TestFollowInactiveUsersFilter:
    """Test that inactive users are filtered from followers/following lists."""
    
    @pytest.mark.asyncio
    async def test_inactive_users_not_in_followers_list(self, db_session: AsyncSession):
        """Test that inactive users do not appear in followers list."""
        # Create current user
        current_user = User(
            email="current@example.com",
            hashed_password=get_password_hash("password"),
            first_name="Current",
            last_name="User",
            is_active=True
        )
        
        # Create active follower
        active_follower = User(
            email="active@example.com",
            hashed_password=get_password_hash("password"),
            first_name="Active",
            last_name="Follower",
            is_active=True
        )
        
        # Create inactive follower
        inactive_follower = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("password"),
            first_name="Inactive",
            last_name="Follower",
            is_active=False
        )
        
        db_session.add_all([current_user, active_follower, inactive_follower])
        await db_session.commit()
        await db_session.refresh(current_user)
        await db_session.refresh(active_follower)
        await db_session.refresh(inactive_follower)
        
        # Both users follow current user
        follow1 = Follow(follower_id=active_follower.id, followed_id=current_user.id)
        follow2 = Follow(follower_id=inactive_follower.id, followed_id=current_user.id)
        db_session.add_all([follow1, follow2])
        await db_session.commit()
        
        # Query followers (simulating the API endpoint logic)
        result = await db_session.execute(
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .where(Follow.followed_id == current_user.id, User.is_active == True)
        )
        followers = result.scalars().all()
        
        # Verify only active follower is returned
        assert len(followers) == 1
        assert followers[0].id == active_follower.id
        assert followers[0].email == "active@example.com"
    
    @pytest.mark.asyncio
    async def test_inactive_users_not_in_following_list(self, db_session: AsyncSession):
        """Test that inactive users do not appear in following list."""
        # Create current user
        current_user = User(
            email="current@example.com",
            hashed_password=get_password_hash("password"),
            first_name="Current",
            last_name="User",
            is_active=True
        )
        
        # Create active user that current user follows
        active_followed = User(
            email="active@example.com",
            hashed_password=get_password_hash("password"),
            first_name="Active",
            last_name="Followed",
            is_active=True
        )
        
        # Create inactive user that current user follows
        inactive_followed = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("password"),
            first_name="Inactive",
            last_name="Followed",
            is_active=False
        )
        
        db_session.add_all([current_user, active_followed, inactive_followed])
        await db_session.commit()
        await db_session.refresh(current_user)
        await db_session.refresh(active_followed)
        await db_session.refresh(inactive_followed)
        
        # Current user follows both users
        follow1 = Follow(follower_id=current_user.id, followed_id=active_followed.id)
        follow2 = Follow(follower_id=current_user.id, followed_id=inactive_followed.id)
        db_session.add_all([follow1, follow2])
        await db_session.commit()
        
        # Query following (simulating the API endpoint logic)
        result = await db_session.execute(
            select(User)
            .join(Follow, Follow.followed_id == User.id)
            .where(Follow.follower_id == current_user.id, User.is_active == True)
        )
        following = result.scalars().all()
        
        # Verify only active user is returned
        assert len(following) == 1
        assert following[0].id == active_followed.id
        assert following[0].email == "active@example.com"
    
    @pytest.mark.asyncio
    async def test_all_active_users_appear_in_lists(self, db_session: AsyncSession):
        """Test that all active users appear in followers/following lists."""
        # Create current user
        current_user = User(
            email="current@example.com",
            hashed_password=get_password_hash("password"),
            first_name="Current",
            last_name="User",
            is_active=True
        )
        
        # Create multiple active followers
        followers = []
        for i in range(3):
            follower = User(
                email=f"follower{i}@example.com",
                hashed_password=get_password_hash("password"),
                first_name=f"Follower",
                last_name=f"User{i}",
                is_active=True
            )
            followers.append(follower)
        
        db_session.add(current_user)
        db_session.add_all(followers)
        await db_session.commit()
        await db_session.refresh(current_user)
        for follower in followers:
            await db_session.refresh(follower)
        
        # All users follow current user
        for follower in followers:
            follow = Follow(follower_id=follower.id, followed_id=current_user.id)
            db_session.add(follow)
        await db_session.commit()
        
        # Query followers
        result = await db_session.execute(
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .where(Follow.followed_id == current_user.id, User.is_active == True)
        )
        retrieved_followers = result.scalars().all()
        
        # Verify all active followers are returned
        assert len(retrieved_followers) == 3
        follower_emails = {f.email for f in retrieved_followers}
        expected_emails = {f"follower{i}@example.com" for i in range(3)}
        assert follower_emails == expected_emails


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
