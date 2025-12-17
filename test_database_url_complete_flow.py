#!/usr/bin/env python3
"""
Test complete DATABASE_URL processing flow.

This test simulates the complete flow of DATABASE_URL processing:
1. URL without port enters the system
2. asyncpg driver format conversion
3. sslmode removal
4. Port auto-fix
5. Validation (should pass without warnings about missing port)
"""

import sys
import os
import logging
from io import StringIO
from urllib.parse import urlparse

# Set up logging to capture output
log_stream = StringIO()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(log_stream),
        logging.StreamHandler(sys.stdout)
    ]
)

# Add backend path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app', 'core'))

from db_utils import ensure_port_in_url, strip_sslmode_from_url


def simulate_database_url_processing(input_url: str) -> tuple[str, bool]:
    """
    Simulate the complete DATABASE_URL processing flow.
    
    Returns:
        (processed_url, validation_passed)
    """
    print(f"\nProcessing: {input_url}")
    print("-" * 80)
    
    url = input_url.strip()
    print(f"After strip: {url}")
    
    # Step 1: Convert to asyncpg format
    if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        print(f"After asyncpg conversion: {url}")
    
    # Step 2: Remove sslmode
    url = strip_sslmode_from_url(url)
    print(f"After sslmode removal: {url}")
    
    # Step 3: Ensure port is present
    url = ensure_port_in_url(url)
    print(f"After port auto-fix: {url}")
    
    # Step 4: Validate
    parsed = urlparse(url)
    missing_fields = []
    
    if not parsed.username:
        missing_fields.append("username")
    if not parsed.password:
        missing_fields.append("password")
    if not parsed.hostname:
        missing_fields.append("hostname")
    if not parsed.port:
        missing_fields.append("port (explicit port required, e.g., :5432)")
    if not parsed.path or len(parsed.path) <= 1:
        missing_fields.append("database name in path")
    
    if missing_fields:
        print(f"⚠️  Validation FAILED: missing {', '.join(missing_fields)}")
        return url, False
    else:
        print("✅ Validation PASSED: All required fields present")
        return url, True


def test_complete_flow():
    """Test complete flow with various URL formats."""
    
    print("=" * 80)
    print("DATABASE_URL COMPLETE PROCESSING FLOW TEST")
    print("=" * 80)
    
    test_cases = [
        # (input_url, should_pass_validation, description)
        (
            "postgresql://user:password@host/database",
            True,
            "URL without port (should be auto-fixed)"
        ),
        (
            "postgresql://user:password@host/database?sslmode=require",
            True,
            "URL without port but with sslmode (should be auto-fixed)"
        ),
        (
            "postgresql://user:password@ep-xxxx.us-east-1.aws.neon.tech/database?sslmode=require",
            True,
            "Neon URL without port (should be auto-fixed)"
        ),
        (
            "postgresql://user:password@containers-us-west-1.railway.app/railway?sslmode=require",
            True,
            "Railway URL without port (should be auto-fixed)"
        ),
        (
            "postgresql://user:password@host:5432/database?sslmode=require",
            True,
            "Complete URL with port and sslmode (should pass)"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for input_url, should_pass, description in test_cases:
        print("\n" + "=" * 80)
        print(f"Test: {description}")
        print("=" * 80)
        
        processed_url, validation_passed = simulate_database_url_processing(input_url)
        
        # Check results
        if validation_passed == should_pass:
            print(f"✅ PASS: Validation result matches expectation")
            passed += 1
        else:
            print(f"❌ FAIL: Expected validation={should_pass}, got {validation_passed}")
            failed += 1
        
        # Additional checks
        parsed = urlparse(processed_url)
        if parsed.port:
            print(f"✅ Port is present: {parsed.port}")
        else:
            print(f"❌ Port is missing")
            failed += 1
        
        if "sslmode=" in processed_url:
            print(f"❌ sslmode still in URL (should be removed)")
            failed += 1
        else:
            print(f"✅ sslmode removed from URL")
    
    # Check log output for warnings
    log_output = log_stream.getvalue()
    
    print("\n" + "=" * 80)
    print("CHECKING FOR UNEXPECTED WARNINGS")
    print("=" * 80)
    
    # We should NOT see the old warning about missing port after auto-fix
    if "Invalid DATABASE_URL: missing" in log_output and "port" in log_output.lower():
        print("❌ WARNING: Found validation warning about missing port")
        print("   This suggests auto-fix didn't work properly")
        failed += 1
    else:
        print("✅ No warnings about missing port (auto-fix worked)")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(test_cases)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n✅ All tests passed! Complete flow works correctly.")
        print("   - Port auto-fix is working")
        print("   - No warnings about missing port")
        print("   - URLs are properly formatted for cloud deployments")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(test_complete_flow())
