"""
Test to verify SQLAlchemy URL parsing fix for empty/whitespace DATABASE_URL.

This test validates that the fix in backend/app/core/config.py properly handles:
1. Empty DATABASE_URL environment variable
2. Whitespace-only DATABASE_URL environment variable
3. Valid DATABASE_URL with whitespace around it
"""
import os
import sys


def test_empty_database_url_in_production():
    """Test that empty DATABASE_URL raises ValueError in production."""
    # Save original environment
    original_env = os.environ.get('ENVIRONMENT')
    original_db_url = os.environ.get('DATABASE_URL')
    
    try:
        # Set production environment with empty DATABASE_URL
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DATABASE_URL'] = ''
        
        # Remove other potential DATABASE_URL sources
        for key in ['POSTGRES_URL', 'DATABASE_PRIVATE_URL']:
            if key in os.environ:
                del os.environ[key]
        
        # Reload the config module to pick up new environment
        if 'backend.app.core.config' in sys.modules:
            del sys.modules['backend.app.core.config']
        
        from backend.app.core.config import Settings
        
        # This should raise ValueError because DATABASE_URL is empty in production
        try:
            Settings.get_database_url()
            print("✗ Test failed: Expected ValueError but got no exception")
            raise AssertionError("Expected ValueError but got no exception")
        except ValueError as e:
            if "DATABASE_URL must be set in production" in str(e):
                print("✓ Test passed: Empty DATABASE_URL raises ValueError in production")
            else:
                print(f"✗ Test failed: Got ValueError with unexpected message: {e}")
                raise
        
    finally:
        # Restore original environment
        if original_env:
            os.environ['ENVIRONMENT'] = original_env
        elif 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
        
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']


def test_whitespace_database_url_in_production():
    """Test that whitespace-only DATABASE_URL raises ValueError in production."""
    # Save original environment
    original_env = os.environ.get('ENVIRONMENT')
    original_db_url = os.environ.get('DATABASE_URL')
    
    try:
        # Set production environment with whitespace-only DATABASE_URL
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DATABASE_URL'] = '   '  # Whitespace only
        
        # Remove other potential DATABASE_URL sources
        for key in ['POSTGRES_URL', 'DATABASE_PRIVATE_URL']:
            if key in os.environ:
                del os.environ[key]
        
        # Reload the config module to pick up new environment
        if 'backend.app.core.config' in sys.modules:
            del sys.modules['backend.app.core.config']
        
        from backend.app.core.config import Settings
        
        # This should raise ValueError because DATABASE_URL is whitespace-only in production
        try:
            Settings.get_database_url()
            print("✗ Test failed: Expected ValueError but got no exception")
            raise AssertionError("Expected ValueError but got no exception")
        except ValueError as e:
            if "DATABASE_URL is empty or contains only whitespace" in str(e):
                print("✓ Test passed: Whitespace-only DATABASE_URL raises ValueError in production")
            else:
                print(f"✗ Test failed: Got ValueError with unexpected message: {e}")
                raise
        
    finally:
        # Restore original environment
        if original_env:
            os.environ['ENVIRONMENT'] = original_env
        elif 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
        
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']


def test_valid_database_url_with_whitespace():
    """Test that valid DATABASE_URL with surrounding whitespace is properly stripped."""
    # Save original environment
    original_env = os.environ.get('ENVIRONMENT')
    original_db_url = os.environ.get('DATABASE_URL')
    
    try:
        # Set production environment with valid DATABASE_URL that has whitespace
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DATABASE_URL'] = '  postgresql://user:pass@database.example.com:5432/db?sslmode=require  '
        
        # Remove other potential DATABASE_URL sources
        for key in ['POSTGRES_URL', 'DATABASE_PRIVATE_URL']:
            if key in os.environ:
                del os.environ[key]
        
        # Reload the config module to pick up new environment
        if 'backend.app.core.config' in sys.modules:
            del sys.modules['backend.app.core.config']
        
        from backend.app.core.config import Settings
        
        # This should succeed and return the trimmed URL
        result = Settings.get_database_url()
        
        # Verify the result is trimmed and converted to asyncpg format
        assert result == 'postgresql+asyncpg://user:pass@database.example.com:5432/db?sslmode=require'
        assert not result.startswith(' ')
        assert not result.endswith(' ')
        
        print("✓ Test passed: Valid DATABASE_URL with whitespace is properly stripped and converted")
        
    finally:
        # Restore original environment
        if original_env:
            os.environ['ENVIRONMENT'] = original_env
        elif 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
        
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']


def test_empty_database_url_in_development():
    """Test that empty DATABASE_URL uses fallback in development."""
    # Save original environment
    original_env = os.environ.get('ENVIRONMENT')
    original_db_url = os.environ.get('DATABASE_URL')
    
    try:
        # Set development environment with empty DATABASE_URL
        os.environ['ENVIRONMENT'] = 'development'
        os.environ['DATABASE_URL'] = ''
        
        # Remove other potential DATABASE_URL sources
        for key in ['POSTGRES_URL', 'DATABASE_PRIVATE_URL']:
            if key in os.environ:
                del os.environ[key]
        
        # Reload the config module to pick up new environment
        if 'backend.app.core.config' in sys.modules:
            del sys.modules['backend.app.core.config']
        
        from backend.app.core.config import Settings
        
        # This should succeed and return the local development fallback
        result = Settings.get_database_url()
        
        # Verify the result is the local development URL
        assert 'localhost' in result
        assert 'hiremebahamas_user' in result
        
        print("✓ Test passed: Empty DATABASE_URL uses fallback in development")
        
    finally:
        # Restore original environment
        if original_env:
            os.environ['ENVIRONMENT'] = original_env
        elif 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
        
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']


if __name__ == '__main__':
    print("Running SQLAlchemy URL parsing fix tests...\n")
    
    try:
        test_empty_database_url_in_production()
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    try:
        test_whitespace_database_url_in_production()
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    try:
        test_valid_database_url_with_whitespace()
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    try:
        test_empty_database_url_in_development()
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print("\nAll tests completed!")
