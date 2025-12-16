"""
Test suite for Render DATABASE_URL validation script.

This test file validates that the verify_render_database_url.py script
correctly identifies valid and invalid DATABASE_URL formats.
"""

import sys
import pytest
from pathlib import Path

# Add parent directory to path to import the validation script
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from verify_render_database_url import validate_database_url


class TestDatabaseURLValidation:
    """Test cases for DATABASE_URL validation."""
    
    def test_valid_vercel_postgres_url(self):
        """Test that a valid Vercel Postgres URL passes validation."""
        url = "postgresql://default:abc123xyz@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert is_valid, f"Valid URL was rejected: {errors}"
        assert len(errors) == 0
    
    def test_valid_railway_postgres_url(self):
        """Test that a valid Railway Postgres URL passes validation."""
        url = "postgresql://postgres:abc123xyz@containers-us-west-1.railway.app:5432/railway?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert is_valid, f"Valid URL was rejected: {errors}"
        assert len(errors) == 0
    
    def test_valid_render_postgres_url(self):
        """Test that a valid Render Postgres URL passes validation."""
        url = "postgresql://hiremebahamas_user:abc123xyz@dpg-xyz123-a.oregon-postgres.render.com:5432/hiremebahamas?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert is_valid, f"Valid URL was rejected: {errors}"
        assert len(errors) == 0
    
    def test_invalid_url_with_quotes(self):
        """Test that URLs with quotes are rejected."""
        url = '"postgresql://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"'
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("quotes" in error.lower() for error in errors)
    
    def test_invalid_url_with_single_quotes(self):
        """Test that URLs with single quotes are rejected."""
        url = "'postgresql://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require'"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("quotes" in error.lower() for error in errors)
    
    def test_invalid_url_with_spaces(self):
        """Test that URLs with spaces are rejected."""
        url = "postgresql://user:pass word@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("spaces" in error.lower() for error in errors)
    
    def test_invalid_url_with_placeholder_host(self):
        """Test that URLs with placeholder 'host' are rejected."""
        url = "postgresql://USER:PASSWORD@host:5432/dbname?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("placeholder" in error.lower() for error in errors)
    
    def test_invalid_url_with_example_domain(self):
        """Test that URLs with example.com are rejected."""
        url = "postgresql://user:pass@example.com:5432/dbname?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("placeholder" in error.lower() for error in errors)
    
    def test_url_without_sslmode_now_valid(self):
        """Test that URLs without sslmode=require are now accepted (added automatically)."""
        url = "postgresql://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb"
        is_valid, errors = validate_database_url(url)
        # After removing redundant validation, this should pass
        # The ensure_sslmode() function will add sslmode=require automatically
        assert is_valid, f"URL without sslmode should now pass validation: {errors}"
    
    def test_invalid_url_old_postgres_format(self):
        """Test that URLs using postgres:// instead of postgresql:// are rejected."""
        url = "postgres://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("postgresql://" in error for error in errors)
    
    def test_invalid_url_no_hostname(self):
        """Test that URLs without hostname are rejected."""
        url = "postgresql://user:pass@:5432/verceldb?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
    
    def test_invalid_url_no_database_name(self):
        """Test that URLs without database name are rejected."""
        url = "postgresql://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("database name" in error.lower() for error in errors)
    
    def test_url_with_special_characters_in_password(self):
        """Test that URLs with URL-encoded special characters in password are valid."""
        url = "postgresql://user:pass%40word@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert is_valid, f"Valid URL with encoded password was rejected: {errors}"
    
    def test_url_with_additional_parameters(self):
        """Test that URLs with additional parameters after sslmode=require are valid."""
        url = "postgresql://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require&connect_timeout=30"
        is_valid, errors = validate_database_url(url)
        assert is_valid, f"Valid URL with additional parameters was rejected: {errors}"
    
    def test_railway_private_network_url(self):
        """Test that Railway private network URLs are valid."""
        url = "postgresql://postgres:abc123@postgres.railway.internal:5432/railway?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert is_valid, f"Valid Railway private network URL was rejected: {errors}"


class TestDatabaseURLValidationEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_multiple_validation_errors(self):
        """Test that a URL with multiple issues reports all errors."""
        url = '"postgres://USER:PASSWORD@host:5432/db"'  # quotes + old format + placeholder + no sslmode
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert len(errors) >= 3  # Should have multiple errors
    
    def test_localhost_is_rejected(self):
        """Test that localhost URLs are rejected as placeholder."""
        url = "postgresql://user:pass@localhost:5432/dbname?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("placeholder" in error.lower() for error in errors)
    
    def test_invalid_port_number(self):
        """Test that invalid port numbers are rejected."""
        url = "postgresql://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:99999/verceldb?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        assert any("port" in error.lower() for error in errors)
    
    def test_hostname_without_tld(self):
        """Test that hostnames without TLD are flagged."""
        url = "postgresql://user:pass@database:5432/dbname?sslmode=require"
        is_valid, errors = validate_database_url(url)
        assert not is_valid
        # Should fail both placeholder check and TLD check


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
