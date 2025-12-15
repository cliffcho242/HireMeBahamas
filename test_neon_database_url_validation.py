"""
Test DATABASE_URL validation for NEON format requirements.

This test validates the strict requirements for DATABASE_URL with focus on:
1. Real hostname (e.g., ep-xxxx.us-east-1.aws.neon.tech)
2. Port number (:5432)
3. SSL mode (?sslmode=require)
4. No whitespace (leading, trailing, or embedded)
"""
import sys
import os

# Add the api directory to the path to import db_url_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from db_url_utils import validate_database_url_structure


class TestNeonDatabaseURLValidation:
    """Test cases for NEON (Vercel Postgres) DATABASE_URL validation."""
    
    def _assert_whitespace_error(self, error):
        """Helper method to check if error message mentions whitespace."""
        assert 'whitespace' in error.lower() or 'spaces' in error.lower()
    
    def test_valid_neon_format(self):
        """Test valid NEON PostgreSQL URL with all required components."""
        url = "postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"Valid NEON URL should pass: {error}"
        assert error == ""
        print("✅ Valid NEON format: PASSED")
    
    def test_neon_with_real_endpoint(self):
        """Test NEON URL with realistic endpoint name."""
        url = "postgresql://default:mypassword@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"Valid NEON URL with real endpoint should pass: {error}"
        assert error == ""
        print("✅ NEON with real endpoint: PASSED")
    
    def test_neon_different_region(self):
        """Test NEON URL with different AWS region."""
        url = "postgresql://user:pass@ep-abc123.us-west-2.aws.neon.tech:5432/database?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"Valid NEON URL with different region should pass: {error}"
        assert error == ""
        print("✅ NEON with different region: PASSED")
    
    def test_invalid_leading_whitespace(self):
        """Test that leading whitespace is rejected."""
        url = " postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with leading whitespace should fail"
        self._assert_whitespace_error(error)
        print("✅ Leading whitespace rejection: PASSED")
    
    def test_invalid_trailing_whitespace(self):
        """Test that trailing whitespace is rejected."""
        url = "postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require "
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with trailing whitespace should fail"
        self._assert_whitespace_error(error)
        print("✅ Trailing whitespace rejection: PASSED")
    
    def test_invalid_embedded_space_in_path(self):
        """Test that embedded space in database path is rejected."""
        url = "postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname ?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with space before query string should fail"
        self._assert_whitespace_error(error)
        print("✅ Embedded space in path rejection: PASSED")
    
    def test_invalid_space_in_password(self):
        """Test that space in password portion is rejected."""
        url = "postgresql://USER:PASS WORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with space in password should fail"
        self._assert_whitespace_error(error)
        print("✅ Space in password rejection: PASSED")
    
    def test_invalid_tab_character(self):
        """Test that tab character is rejected."""
        url = "postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname\t?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with tab character should fail"
        self._assert_whitespace_error(error)
        print("✅ Tab character rejection: PASSED")
    
    def test_invalid_newline_character(self):
        """Test that newline character is rejected."""
        url = "postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname\n?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with newline should fail"
        self._assert_whitespace_error(error)
        print("✅ Newline character rejection: PASSED")
    
    def test_invalid_missing_port(self):
        """Test that URL without explicit port is rejected (NEON requirement)."""
        url = "postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL without port should fail"
        assert "port" in error.lower()
        print("✅ Missing port rejection: PASSED")
    
    def test_invalid_missing_sslmode(self):
        """Test that URL without sslmode is rejected (NEON requirement)."""
        url = "postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL without sslmode should fail"
        assert "sslmode" in error.lower()
        print("✅ Missing sslmode rejection: PASSED")
    
    def test_invalid_localhost_hostname(self):
        """Test that localhost is rejected (NEON uses cloud hostnames)."""
        url = "postgresql://USER:PASSWORD@localhost:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "Localhost should be rejected"
        assert "localhost" in error.lower() or "socket" in error.lower()
        print("✅ Localhost rejection: PASSED")
    
    def test_neon_with_additional_params(self):
        """Test NEON URL with additional query parameters."""
        url = "postgresql://user:pass@ep-abc.us-east-1.aws.neon.tech:5432/db?sslmode=require&connect_timeout=30"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"NEON URL with extra params should pass: {error}"
        assert error == ""
        print("✅ NEON with additional params: PASSED")
    
    def test_neon_with_special_chars_in_password(self):
        """Test NEON URL with special characters in password (URL-encoded)."""
        # Password with @ and ! should be URL-encoded
        url = "postgresql://user:p%40ssw0rd%21@ep-abc.us-east-1.aws.neon.tech:5432/db?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"NEON URL with encoded special chars should pass: {error}"
        assert error == ""
        print("✅ NEON with encoded special chars: PASSED")
    
    def test_neon_asyncpg_driver(self):
        """Test NEON URL with asyncpg driver specification."""
        url = "postgresql+asyncpg://user:pass@ep-abc.us-east-1.aws.neon.tech:5432/db?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert is_valid, f"NEON URL with asyncpg driver should pass: {error}"
        assert error == ""
        print("✅ NEON with asyncpg driver: PASSED")
    
    def test_invalid_double_quotes_wrapping(self):
        """Test that URL wrapped in double quotes is rejected."""
        url = '"postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"'
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL wrapped in double quotes should fail"
        assert "quote" in error.lower()
        print("✅ Double quotes wrapping rejection: PASSED")
    
    def test_invalid_single_quotes_wrapping(self):
        """Test that URL wrapped in single quotes is rejected."""
        url = "'postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require'"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL wrapped in single quotes should fail"
        assert "quote" in error.lower()
        print("✅ Single quotes wrapping rejection: PASSED")
    
    def test_invalid_quotes_in_username(self):
        """Test that quotes in username portion is rejected."""
        url = 'postgresql://"user":PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require'
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with quotes in username should fail"
        assert "quote" in error.lower()
        print("✅ Quotes in username rejection: PASSED")
    
    def test_invalid_quotes_in_password(self):
        """Test that quotes in password portion is rejected."""
        url = "postgresql://user:'PASSWORD'@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with quotes in password should fail"
        assert "quote" in error.lower()
        print("✅ Quotes in password rejection: PASSED")
    
    def test_invalid_quotes_in_hostname(self):
        """Test that quotes in hostname portion is rejected."""
        url = 'postgresql://user:PASSWORD@"ep-xxxx.us-east-1.aws.neon.tech":5432/dbname?sslmode=require'
        is_valid, error = validate_database_url_structure(url)
        assert not is_valid, "URL with quotes in hostname should fail"
        assert "quote" in error.lower()
        print("✅ Quotes in hostname rejection: PASSED")


def run_all_tests():
    """Run all test cases and report results."""
    test_class = TestNeonDatabaseURLValidation()
    
    tests = [
        ("Valid NEON format", test_class.test_valid_neon_format),
        ("NEON with real endpoint", test_class.test_neon_with_real_endpoint),
        ("NEON with different region", test_class.test_neon_different_region),
        ("Leading whitespace rejection", test_class.test_invalid_leading_whitespace),
        ("Trailing whitespace rejection", test_class.test_invalid_trailing_whitespace),
        ("Embedded space rejection", test_class.test_invalid_embedded_space_in_path),
        ("Space in password rejection", test_class.test_invalid_space_in_password),
        ("Tab character rejection", test_class.test_invalid_tab_character),
        ("Newline character rejection", test_class.test_invalid_newline_character),
        ("Missing port rejection", test_class.test_invalid_missing_port),
        ("Missing sslmode rejection", test_class.test_invalid_missing_sslmode),
        ("Localhost rejection", test_class.test_invalid_localhost_hostname),
        ("NEON with additional params", test_class.test_neon_with_additional_params),
        ("NEON with encoded special chars", test_class.test_neon_with_special_chars_in_password),
        ("NEON with asyncpg driver", test_class.test_neon_asyncpg_driver),
        ("Double quotes wrapping rejection", test_class.test_invalid_double_quotes_wrapping),
        ("Single quotes wrapping rejection", test_class.test_invalid_single_quotes_wrapping),
        ("Quotes in username rejection", test_class.test_invalid_quotes_in_username),
        ("Quotes in password rejection", test_class.test_invalid_quotes_in_password),
        ("Quotes in hostname rejection", test_class.test_invalid_quotes_in_hostname),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*70)
    print("NEON DATABASE_URL VALIDATION TEST SUITE")
    print("="*70 + "\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: FAILED - {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(tests)} total")
    print("="*70 + "\n")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    exit(exit_code)
