"""
Integration test to verify frontend and backend work together correctly
for followers/following functionality with inactive user filtering.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Set test database URL
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test_integration.db'

from app.database import Base, engine
from app.models import User, Follow
from app.core.security import get_password_hash, create_access_token
from app.main import app


@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_users(db_session: AsyncSession):
    """Create test users with follow relationships."""
    # Create main user
    main_user = User(
        email="main@example.com",
        hashed_password=get_password_hash("password123"),
        first_name="Main",
        last_name="User",
        is_active=True
    )
    
    # Create active follower
    active_follower = User(
        email="active_follower@example.com",
        hashed_password=get_password_hash("password123"),
        first_name="Active",
        last_name="Follower",
        is_active=True
    )
    
    # Create inactive follower (should be filtered out)
    inactive_follower = User(
        email="inactive_follower@example.com",
        hashed_password=get_password_hash("password123"),
        first_name="Inactive",
        last_name="Follower",
        is_active=False
    )
    
    # Create active user that main user follows
    active_followed = User(
        email="active_followed@example.com",
        hashed_password=get_password_hash("password123"),
        first_name="Active",
        last_name="Followed",
        is_active=True
    )
    
    # Create inactive user that main user follows (should be filtered out)
    inactive_followed = User(
        email="inactive_followed@example.com",
        hashed_password=get_password_hash("password123"),
        first_name="Inactive",
        last_name="Followed",
        is_active=False
    )
    
    db_session.add_all([main_user, active_follower, inactive_follower, active_followed, inactive_followed])
    await db_session.commit()
    
    # Refresh to get IDs
    for user in [main_user, active_follower, inactive_follower, active_followed, inactive_followed]:
        await db_session.refresh(user)
    
    # Create follow relationships
    # Both active and inactive users follow main user
    follow1 = Follow(follower_id=active_follower.id, followed_id=main_user.id)
    follow2 = Follow(follower_id=inactive_follower.id, followed_id=main_user.id)
    
    # Main user follows both active and inactive users
    follow3 = Follow(follower_id=main_user.id, followed_id=active_followed.id)
    follow4 = Follow(follower_id=main_user.id, followed_id=inactive_followed.id)
    
    db_session.add_all([follow1, follow2, follow3, follow4])
    await db_session.commit()
    
    return {
        'main_user': main_user,
        'active_follower': active_follower,
        'inactive_follower': inactive_follower,
        'active_followed': active_followed,
        'inactive_followed': inactive_followed
    }


class TestFollowersIntegration:
    """Integration tests for followers/following API endpoints."""
    
    @pytest.mark.asyncio
    async def test_followers_list_filters_inactive_users(self, test_users):
        """Test that GET /api/users/followers/list filters out inactive users."""
        main_user = test_users['main_user']
        
        # Create access token for main user (sub should be user_id)
        token = create_access_token(data={"sub": str(main_user.id)})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/users/followers/list",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "followers" in data
        
        # Should only return active follower, not inactive
        assert len(data["followers"]) == 1
        assert data["followers"][0]["email"] == "active_follower@example.com"
        assert data["followers"][0]["first_name"] == "Active"
        
    @pytest.mark.asyncio
    async def test_following_list_filters_inactive_users(self, test_users):
        """Test that GET /api/users/following/list filters out inactive users."""
        main_user = test_users['main_user']
        
        # Create access token for main user (sub should be user_id)
        token = create_access_token(data={"sub": str(main_user.id)})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/users/following/list",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "following" in data
        
        # Should only return active followed user, not inactive
        assert len(data["following"]) == 1
        assert data["following"][0]["email"] == "active_followed@example.com"
        assert data["following"][0]["first_name"] == "Active"
    
    @pytest.mark.asyncio
    async def test_discover_users_also_filters_inactive(self, test_users):
        """Test that GET /api/users/list also filters inactive users (consistency check)."""
        main_user = test_users['main_user']
        
        # Create access token for main user (sub should be user_id)
        token = create_access_token(data={"sub": str(main_user.id)})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/users/list",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "users" in data
        
        # Should only return active users (excluding main user)
        # active_follower and active_followed should appear
        assert len(data["users"]) == 2
        
        user_emails = {user["email"] for user in data["users"]}
        assert "active_follower@example.com" in user_emails
        assert "active_followed@example.com" in user_emails
        assert "inactive_follower@example.com" not in user_emails
        assert "inactive_followed@example.com" not in user_emails
    
    @pytest.mark.asyncio
    async def test_frontend_api_response_structure(self, test_users):
        """Test that API responses match the structure expected by frontend."""
        main_user = test_users['main_user']
        token = create_access_token(data={"sub": str(main_user.id)})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test followers endpoint
            followers_response = await client.get(
                "/api/users/followers/list",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Test following endpoint
            following_response = await client.get(
                "/api/users/following/list",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Verify followers response structure
        followers_data = followers_response.json()
        assert "success" in followers_data
        assert "followers" in followers_data
        assert isinstance(followers_data["followers"], list)
        
        if len(followers_data["followers"]) > 0:
            follower = followers_data["followers"][0]
            # Verify all required fields are present (matching frontend User interface)
            assert "id" in follower
            assert "first_name" in follower
            assert "last_name" in follower
            assert "email" in follower
            assert "is_following" in follower
            assert "followers_count" in follower
            assert "following_count" in follower
        
        # Verify following response structure
        following_data = following_response.json()
        assert "success" in following_data
        assert "following" in following_data
        assert isinstance(following_data["following"], list)
        
        if len(following_data["following"]) > 0:
            followed = following_data["following"][0]
            # Verify all required fields are present
            assert "id" in followed
            assert "first_name" in followed
            assert "last_name" in followed
            assert "email" in followed
            assert "is_following" in followed
            assert "followers_count" in followed
            assert "following_count" in followed
            assert followed["is_following"] is True  # Should always be True for following list


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
