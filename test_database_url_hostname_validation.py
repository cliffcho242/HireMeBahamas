"""
Test DATABASE_URL validation for hostname, port, TCP, and SSL requirements.

This test validates the strict requirements for DATABASE_URL:
1. Must contain a hostname (not localhost, 127.0.0.1, or empty)
2. Must contain a port number
3. Must use TCP connection (no Unix sockets)
4. Must have SSL mode configured
"""
import pytest
import sys
import os

# Add the api directory to the path to import db_url_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from db_url_utils import validate_database_url_structure


class TestDatabaseURLValidation:
    """Test cases for DATABASE_URL structure validation."""
    
    def test_valid_neon_url(self):
        """Test valid Neon PostgreSQL URL."""
        url = "postgresql://user:password@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"Valid Neon URL should pass: {error}"
        assert error == ""
    
    def test_valid_railway_url(self):
        """Test valid Railway PostgreSQL URL."""
        url = "postgresql://user:password@db.railway.internal:5432/railway?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"Valid Railway URL should pass: {error}"
        assert error == ""
    
    def test_valid_with_asyncpg_driver(self):
        """Test valid URL with asyncpg driver specification."""
        url = "postgresql+asyncpg://user:password@db.example.com:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"Valid URL with asyncpg should pass: {error}"
        assert error == ""
    
    def test_invalid_empty_url(self):
        """Test that empty URL is rejected."""
        is_valid, error = validate_database_url_structure("")
        assert not is_valid
        assert "empty" in error.lower()
    
    def test_invalid_none_url(self):
        """Test that None URL is rejected."""
        is_valid, error = validate_database_url_structure(None)
        assert not is_valid
        assert "empty" in error.lower() or "none" in error.lower()
    
    def test_invalid_missing_hostname(self):
        """Test that URL without hostname is rejected (Unix socket usage)."""
        url = "postgresql://user:password@/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid
        assert "hostname" in error.lower()
    
    def test_invalid_localhost_hostname(self):
        """Test that localhost is rejected (may use Unix sockets)."""
        url = "postgresql://user:password@localhost:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid
        assert "localhost" in error.lower()
        assert "socket" in error.lower()
    
    def test_invalid_127_0_0_1_hostname(self):
        """Test that 127.0.0.1 is rejected (may use Unix sockets)."""
        url = "postgresql://user:password@127.0.0.1:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid
        assert "127.0.0.1" in error
        assert "socket" in error.lower()
    
    def test_invalid_ipv6_localhost(self):
        """Test that IPv6 localhost (::1) is rejected."""
        # Note: IPv6 addresses in URLs need to be enclosed in brackets
        # The bare ::1 format is parsed as missing hostname
        url = "postgresql://user:password@[::1]:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid
        # If urlparse doesn't extract the hostname properly, check for either error
        assert "socket" in error.lower() or "hostname" in error.lower()
    
    def test_invalid_missing_port(self):
        """Test that URL without explicit port is rejected."""
        url = "postgresql://user:password@db.example.com/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid
        assert "port" in error.lower()
    
    def test_invalid_missing_sslmode(self):
        """Test that URL without sslmode is now accepted (sslmode added automatically)."""
        url = "postgresql://user:password@db.example.com:5432/dbname"
        is_valid, error = validate_database_url_structure(url)
        # After removing redundant validation, this should pass
        # The ensure_sslmode() function will add sslmode=require automatically
        assert is_valid, f"URL without sslmode should now pass validation: {error}"
    
    def test_invalid_missing_port(self):
        """Test that URL missing port is rejected."""
        url = "postgresql://user:password@db.example.com/dbname"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid
        # Should fail on port check
        assert "port" in error.lower()
    
    def test_valid_with_additional_params(self):
        """Test valid URL with additional query parameters."""
        url = "postgresql://user:password@db.example.com:5432/dbname?sslmode=require&timeout=10&pool_size=5"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"Valid URL with extra params should pass: {error}"
        assert error == ""
    
    def test_valid_with_special_chars_in_password(self):
        """Test valid URL with special characters in password."""
        url = "postgresql://user:p@ssw0rd!@db.example.com:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"Valid URL with special chars should pass: {error}"
        assert error == ""
    
    def test_valid_sslmode_variations(self):
        """Test that various sslmode values are accepted."""
        sslmodes = ['require', 'verify-ca', 'verify-full', 'prefer']
        for mode in sslmodes:
            url = f"postgresql://user:password@db.example.com:5432/dbname?sslmode={mode}"
            is_valid, error = validate_database_url_structure(url)
            assert is_valid, f"URL with sslmode={mode} should pass: {error}"
    
    def test_case_insensitive_sslmode_check(self):
        """Test that sslmode check is case-insensitive."""
        url = "postgresql://user:password@db.example.com:5432/dbname?SSLMODE=REQUIRE"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"URL with uppercase SSLMODE should pass: {error}"
    
    def test_case_insensitive_localhost_check(self):
        """Test that localhost check is case-insensitive."""
        url = "postgresql://user:password@LOCALHOST:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid
        assert "socket" in error.lower()


def test_integration_with_ensure_sslmode():
    """Test that validate and ensure_sslmode work together."""
    from db_url_utils import ensure_sslmode
    
    # URL without sslmode
    url = "postgresql://user:password@db.example.com:5432/dbname"
    
    # First, ensure sslmode is added
    url_with_ssl = ensure_sslmode(url)
    assert "sslmode=require" in url_with_ssl
    
    # Then validate - should pass now
    is_valid, error = validate_database_url_structure(url_with_ssl)
    assert is_valid, f"URL after ensure_sslmode should pass validation: {error}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
