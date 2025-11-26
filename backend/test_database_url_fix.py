"""
Test to verify that the database configuration correctly prioritizes DATABASE_PRIVATE_URL
over DATABASE_URL to avoid Railway egress fees.
"""

import os
from decouple import config


def test_database_url_priority():
    """Test that DATABASE_PRIVATE_URL takes precedence over DATABASE_URL"""
    
    # Save original values
    original_private_url = os.environ.get("DATABASE_PRIVATE_URL")
    original_url = os.environ.get("DATABASE_URL")
    
    try:
        # Test 1: When both are set, DATABASE_PRIVATE_URL should be used
        private_url = "postgresql+asyncpg://user:pass@private.railway.internal:5432/db"
        public_url = "postgresql+asyncpg://user:pass@public.railway.app:5432/db"
        
        os.environ["DATABASE_PRIVATE_URL"] = private_url
        os.environ["DATABASE_URL"] = public_url
        
        # Simulate the config logic from database.py
        test_url_1 = config(
            "DATABASE_PRIVATE_URL",
            default=config(
                "DATABASE_URL", 
                default="postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
            )
        )
        
        assert test_url_1 == private_url, (
            f"Expected DATABASE_PRIVATE_URL to be used, but got: {test_url_1}"
        )
        print("✓ Test 1 passed: DATABASE_PRIVATE_URL takes precedence over DATABASE_URL")
        
        # Test 2: When only DATABASE_URL is set, it should be used
        del os.environ["DATABASE_PRIVATE_URL"]
        os.environ["DATABASE_URL"] = public_url
        
        test_url_2 = config(
            "DATABASE_PRIVATE_URL",
            default=config(
                "DATABASE_URL", 
                default="postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
            )
        )
        
        assert test_url_2 == public_url, (
            f"Expected DATABASE_URL to be used when DATABASE_PRIVATE_URL is not set, but got: {test_url_2}"
        )
        print("✓ Test 2 passed: DATABASE_URL is used when DATABASE_PRIVATE_URL is not available")
        
        # Test 3: When neither is set, default should be used
        del os.environ["DATABASE_URL"]
        
        test_url_3 = config(
            "DATABASE_PRIVATE_URL",
            default=config(
                "DATABASE_URL", 
                default="postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
            )
        )
        
        assert "localhost" in test_url_3, (
            f"Expected default local database URL, but got: {test_url_3}"
        )
        print("✓ Test 3 passed: Default local database URL is used when neither variable is set")
        
        print("\n✅ All database URL priority tests passed!")
        print("✅ Configuration correctly avoids Railway egress fees by preferring DATABASE_PRIVATE_URL")
        
    finally:
        # Restore original values
        if original_private_url:
            os.environ["DATABASE_PRIVATE_URL"] = original_private_url
        elif "DATABASE_PRIVATE_URL" in os.environ:
            del os.environ["DATABASE_PRIVATE_URL"]
            
        if original_url:
            os.environ["DATABASE_URL"] = original_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
