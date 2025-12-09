"""
Test database URL configuration and environment variable handling.

This test ensures that the database URL is correctly retrieved from environment
variables in the correct priority order.

SECURITY NOTE: All database URLs and credentials in this test file are placeholder
values used only for testing configuration logic. These are not real credentials
and no actual database connections are made.
"""

import os
import sys
import unittest


class TestDatabaseURLConfiguration(unittest.TestCase):
    """Test database URL environment variable handling."""
    
    def setUp(self):
        """Save original environment variables before each test."""
        self.original_env = {
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'POSTGRES_URL': os.environ.get('POSTGRES_URL'),
            'DATABASE_PRIVATE_URL': os.environ.get('DATABASE_PRIVATE_URL'),
            'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
        }
    
    def tearDown(self):
        """Restore original environment variables after each test."""
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        # Reload module to restore original state
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
    
    def test_database_url_priority_order_primary(self):
        """Test that DATABASE_URL has highest priority."""
        os.environ['DATABASE_URL'] = 'postgresql://primary'
        os.environ['POSTGRES_URL'] = 'postgresql://secondary'
        os.environ['DATABASE_PRIVATE_URL'] = 'postgresql://tertiary'
        os.environ['ENVIRONMENT'] = 'development'
        
        # Reload the module to pick up new environment variables
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        self.assertEqual(DATABASE_URL.strip(), 'postgresql://primary',
                        "DATABASE_URL should be the primary choice")
    
    def test_database_url_priority_order_secondary(self):
        """Test that POSTGRES_URL is used when DATABASE_URL is not set."""
        os.environ.pop('DATABASE_URL', None)
        os.environ['POSTGRES_URL'] = 'postgresql://secondary'
        os.environ['DATABASE_PRIVATE_URL'] = 'postgresql://tertiary'
        os.environ['ENVIRONMENT'] = 'development'
        
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        self.assertEqual(DATABASE_URL.strip(), 'postgresql://secondary',
                        "POSTGRES_URL should be used when DATABASE_URL is not set")
    
    def test_database_url_priority_order_tertiary(self):
        """Test that DATABASE_PRIVATE_URL is used when both DATABASE_URL and POSTGRES_URL are not set."""
        os.environ.pop('DATABASE_URL', None)
        os.environ.pop('POSTGRES_URL', None)
        os.environ['DATABASE_PRIVATE_URL'] = 'postgresql://tertiary'
        os.environ['ENVIRONMENT'] = 'development'
        
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        self.assertEqual(DATABASE_URL.strip(), 'postgresql://tertiary',
                        "DATABASE_PRIVATE_URL should be used when DATABASE_URL and POSTGRES_URL are not set")
    
    def test_database_url_production_validation(self):
        """Test that ValueError is raised in production when DATABASE_URL is not set."""
        os.environ.pop('DATABASE_URL', None)
        os.environ.pop('POSTGRES_URL', None)
        os.environ.pop('DATABASE_PRIVATE_URL', None)
        os.environ['ENVIRONMENT'] = 'production'
        
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        # This should raise a ValueError
        with self.assertRaises(ValueError) as context:
            from backend.app.database import DATABASE_URL  # noqa: F401
        
        self.assertIn("DATABASE_URL must be set in production", str(context.exception))
    
    def test_database_url_development_default(self):
        """Test that a default local DATABASE_URL is used in development mode."""
        os.environ.pop('DATABASE_URL', None)
        os.environ.pop('POSTGRES_URL', None)
        os.environ.pop('DATABASE_PRIVATE_URL', None)
        os.environ['ENVIRONMENT'] = 'development'
        
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        # Should not raise an error, and should have a default value
        self.assertIsNotNone(DATABASE_URL, "DATABASE_URL should have a default in development")
        self.assertTrue('localhost' in DATABASE_URL or '127.0.0.1' in DATABASE_URL,
                       "Default DATABASE_URL should use localhost")
    
    def test_database_url_whitespace_handling(self):
        """Test that whitespace is stripped from DATABASE_URL."""
        os.environ['DATABASE_URL'] = '  postgresql://test:password@localhost:5432/testdb  '
        os.environ['ENVIRONMENT'] = 'development'
        
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        self.assertEqual(DATABASE_URL, 'postgresql://test:password@localhost:5432/testdb',
                        "Whitespace should be stripped from DATABASE_URL")
        self.assertFalse(DATABASE_URL.startswith(' '), "DATABASE_URL should not start with whitespace")
        self.assertFalse(DATABASE_URL.endswith(' '), "DATABASE_URL should not end with whitespace")


def test_database_url_priority_order():
    """Test that DATABASE_URL environment variable has correct priority order."""
    # Save original environment variables
    original_env = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'POSTGRES_URL': os.environ.get('POSTGRES_URL'),
        'DATABASE_PRIVATE_URL': os.environ.get('DATABASE_PRIVATE_URL'),
        'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
    }
    
    try:
        # Test 1: DATABASE_URL has highest priority
        os.environ['DATABASE_URL'] = 'postgresql://primary'
        os.environ['POSTGRES_URL'] = 'postgresql://secondary'
        os.environ['DATABASE_PRIVATE_URL'] = 'postgresql://tertiary'
        os.environ['ENVIRONMENT'] = 'development'
        
        # Reload the module to pick up new environment variables
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        assert DATABASE_URL.strip() == 'postgresql://primary', \
            "DATABASE_URL should be the primary choice"
        
        # Test 2: POSTGRES_URL is used when DATABASE_URL is not set
        del os.environ['DATABASE_URL']
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        assert DATABASE_URL.strip() == 'postgresql://secondary', \
            "POSTGRES_URL should be used when DATABASE_URL is not set"
        
        # Test 3: DATABASE_PRIVATE_URL is used when both DATABASE_URL and POSTGRES_URL are not set
        del os.environ['POSTGRES_URL']
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        assert DATABASE_URL.strip() == 'postgresql://tertiary', \
            "DATABASE_PRIVATE_URL should be used when DATABASE_URL and POSTGRES_URL are not set"
        
        print("✓ All priority order tests passed!")
        
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        # Reload module to restore original state
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']


def test_database_url_production_validation():
    """Test that ValueError is raised in production when DATABASE_URL is not set."""
    # Save original environment variables
    original_env = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'POSTGRES_URL': os.environ.get('POSTGRES_URL'),
        'DATABASE_PRIVATE_URL': os.environ.get('DATABASE_PRIVATE_URL'),
        'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
    }
    
    try:
        # Clear all database URL environment variables
        os.environ.pop('DATABASE_URL', None)
        os.environ.pop('POSTGRES_URL', None)
        os.environ.pop('DATABASE_PRIVATE_URL', None)
        os.environ['ENVIRONMENT'] = 'production'
        
        # Reload the module to pick up new environment variables
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        # This should raise a ValueError
        try:
            from backend.app.database import DATABASE_URL  # noqa: F401
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "DATABASE_URL must be set in production" in str(e)
            print("✓ Production validation test passed!")
        
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        # Reload module to restore original state
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']


def test_database_url_development_default():
    """Test that a default local DATABASE_URL is used in development mode."""
    # Save original environment variables
    original_env = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'POSTGRES_URL': os.environ.get('POSTGRES_URL'),
        'DATABASE_PRIVATE_URL': os.environ.get('DATABASE_PRIVATE_URL'),
        'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
    }
    
    try:
        # Clear all database URL environment variables
        os.environ.pop('DATABASE_URL', None)
        os.environ.pop('POSTGRES_URL', None)
        os.environ.pop('DATABASE_PRIVATE_URL', None)
        os.environ['ENVIRONMENT'] = 'development'
        
        # Reload the module to pick up new environment variables
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        # Should not raise an error, and should have a default value
        assert DATABASE_URL is not None, "DATABASE_URL should have a default in development"
        assert 'localhost' in DATABASE_URL or '127.0.0.1' in DATABASE_URL, \
            "Default DATABASE_URL should use localhost"
        print("✓ Development default test passed!")
        
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        # Reload module to restore original state
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']


def test_database_url_whitespace_handling():
    """Test that whitespace is stripped from DATABASE_URL."""
    # Save original environment variables
    original_env = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'POSTGRES_URL': os.environ.get('POSTGRES_URL'),
        'DATABASE_PRIVATE_URL': os.environ.get('DATABASE_PRIVATE_URL'),
        'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
    }
    
    try:
        # Set DATABASE_URL with leading and trailing whitespace
        os.environ['DATABASE_URL'] = '  postgresql://test:password@localhost:5432/testdb  '
        os.environ['ENVIRONMENT'] = 'development'
        
        # Reload the module to pick up new environment variables
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        
        from backend.app.database import DATABASE_URL
        assert DATABASE_URL == 'postgresql://test:password@localhost:5432/testdb', \
            "Whitespace should be stripped from DATABASE_URL"
        assert not DATABASE_URL.startswith(' '), "DATABASE_URL should not start with whitespace"
        assert not DATABASE_URL.endswith(' '), "DATABASE_URL should not end with whitespace"
        print("✓ Whitespace handling test passed!")
        
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        # Reload module to restore original state
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']


if __name__ == '__main__':
    print("Running Database URL Configuration Tests...")
    print("=" * 60)
    
    # Run standalone tests
    test_database_url_priority_order()
    test_database_url_production_validation()
    test_database_url_development_default()
    test_database_url_whitespace_handling()
    
    print("=" * 60)
    print("Running unittest suite...")
    unittest.main()
