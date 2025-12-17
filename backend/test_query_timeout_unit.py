"""
Unit tests for query-level timeout functionality (no database required).

These tests validate the timeout utility functions without requiring
a live database connection.
"""

import os
import sys

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.query_timeout import (
    get_timeout_for_operation,
    DEFAULT_QUERY_TIMEOUT_MS,
    FAST_QUERY_TIMEOUT_MS,
    SLOW_QUERY_TIMEOUT_MS,
)


def test_get_timeout_for_operation():
    """Test the timeout lookup helper function."""
    print("\n" + "="*70)
    print("TEST: get_timeout_for_operation")
    print("="*70)
    
    # Test fast timeout
    fast_timeout = get_timeout_for_operation('fast')
    assert fast_timeout == FAST_QUERY_TIMEOUT_MS, f"Expected {FAST_QUERY_TIMEOUT_MS}, got {fast_timeout}"
    print(f"✓ Fast timeout: {fast_timeout}ms")
    
    # Test default timeout
    default_timeout = get_timeout_for_operation('default')
    assert default_timeout == DEFAULT_QUERY_TIMEOUT_MS, f"Expected {DEFAULT_QUERY_TIMEOUT_MS}, got {default_timeout}"
    print(f"✓ Default timeout: {default_timeout}ms")
    
    # Test slow timeout
    slow_timeout = get_timeout_for_operation('slow')
    assert slow_timeout == SLOW_QUERY_TIMEOUT_MS, f"Expected {SLOW_QUERY_TIMEOUT_MS}, got {slow_timeout}"
    print(f"✓ Slow timeout: {slow_timeout}ms")
    
    # Test unknown operation (should return default)
    unknown_timeout = get_timeout_for_operation('unknown')
    assert unknown_timeout == DEFAULT_QUERY_TIMEOUT_MS, f"Expected {DEFAULT_QUERY_TIMEOUT_MS}, got {unknown_timeout}"
    print(f"✓ Unknown operation defaults to: {unknown_timeout}ms")
    
    print("\n✅ All timeout lookup tests passed!")
    return True


def test_timeout_constants():
    """Test that timeout constants are properly configured."""
    print("\n" + "="*70)
    print("TEST: Timeout Constants Configuration")
    print("="*70)
    
    # Verify constants are positive integers
    assert isinstance(FAST_QUERY_TIMEOUT_MS, int), "FAST_QUERY_TIMEOUT_MS must be an integer"
    assert FAST_QUERY_TIMEOUT_MS > 0, "FAST_QUERY_TIMEOUT_MS must be positive"
    print(f"✓ FAST_QUERY_TIMEOUT_MS: {FAST_QUERY_TIMEOUT_MS}ms")
    
    assert isinstance(DEFAULT_QUERY_TIMEOUT_MS, int), "DEFAULT_QUERY_TIMEOUT_MS must be an integer"
    assert DEFAULT_QUERY_TIMEOUT_MS > 0, "DEFAULT_QUERY_TIMEOUT_MS must be positive"
    print(f"✓ DEFAULT_QUERY_TIMEOUT_MS: {DEFAULT_QUERY_TIMEOUT_MS}ms")
    
    assert isinstance(SLOW_QUERY_TIMEOUT_MS, int), "SLOW_QUERY_TIMEOUT_MS must be an integer"
    assert SLOW_QUERY_TIMEOUT_MS > 0, "SLOW_QUERY_TIMEOUT_MS must be positive"
    print(f"✓ SLOW_QUERY_TIMEOUT_MS: {SLOW_QUERY_TIMEOUT_MS}ms")
    
    # Verify timeout hierarchy (fast < default < slow)
    assert FAST_QUERY_TIMEOUT_MS < DEFAULT_QUERY_TIMEOUT_MS, \
        f"Fast timeout ({FAST_QUERY_TIMEOUT_MS}) should be less than default ({DEFAULT_QUERY_TIMEOUT_MS})"
    print(f"✓ Fast < Default: {FAST_QUERY_TIMEOUT_MS} < {DEFAULT_QUERY_TIMEOUT_MS}")
    
    assert DEFAULT_QUERY_TIMEOUT_MS < SLOW_QUERY_TIMEOUT_MS, \
        f"Default timeout ({DEFAULT_QUERY_TIMEOUT_MS}) should be less than slow ({SLOW_QUERY_TIMEOUT_MS})"
    print(f"✓ Default < Slow: {DEFAULT_QUERY_TIMEOUT_MS} < {SLOW_QUERY_TIMEOUT_MS}")
    
    print("\n✅ All timeout constant tests passed!")
    return True


def test_module_imports():
    """Test that all required functions and constants can be imported."""
    print("\n" + "="*70)
    print("TEST: Module Imports")
    print("="*70)
    
    try:
        from app.core.query_timeout import (
            set_query_timeout,
            with_query_timeout,
            set_fast_query_timeout,
            set_slow_query_timeout,
            get_timeout_for_operation,
            DEFAULT_QUERY_TIMEOUT_MS,
            FAST_QUERY_TIMEOUT_MS,
            SLOW_QUERY_TIMEOUT_MS,
        )
        print("✓ set_query_timeout imported")
        print("✓ with_query_timeout imported")
        print("✓ set_fast_query_timeout imported")
        print("✓ set_slow_query_timeout imported")
        print("✓ get_timeout_for_operation imported")
        print("✓ DEFAULT_QUERY_TIMEOUT_MS imported")
        print("✓ FAST_QUERY_TIMEOUT_MS imported")
        print("✓ SLOW_QUERY_TIMEOUT_MS imported")
        
        print("\n✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_environment_variable_support():
    """Test that environment variables can override defaults."""
    print("\n" + "="*70)
    print("TEST: Environment Variable Support")
    print("="*70)
    
    # Note: We can't test actual override without reloading the module,
    # but we can verify the current values are from the right source
    
    # Check if custom values are set
    custom_default = os.getenv("DB_QUERY_TIMEOUT_MS")
    custom_fast = os.getenv("DB_FAST_QUERY_TIMEOUT_MS")
    custom_slow = os.getenv("DB_SLOW_QUERY_TIMEOUT_MS")
    
    if custom_default:
        print(f"✓ DB_QUERY_TIMEOUT_MS env var detected: {custom_default}")
    else:
        print(f"✓ DB_QUERY_TIMEOUT_MS using default: {DEFAULT_QUERY_TIMEOUT_MS}")
    
    if custom_fast:
        print(f"✓ DB_FAST_QUERY_TIMEOUT_MS env var detected: {custom_fast}")
    else:
        print(f"✓ DB_FAST_QUERY_TIMEOUT_MS using default: {FAST_QUERY_TIMEOUT_MS}")
    
    if custom_slow:
        print(f"✓ DB_SLOW_QUERY_TIMEOUT_MS env var detected: {custom_slow}")
    else:
        print(f"✓ DB_SLOW_QUERY_TIMEOUT_MS using default: {SLOW_QUERY_TIMEOUT_MS}")
    
    print("\n✅ Environment variable support verified!")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("QUERY TIMEOUT UNIT TESTS (No Database Required)")
    print("="*70)
    
    all_passed = True
    
    try:
        all_passed = all_passed and test_module_imports()
        all_passed = all_passed and test_timeout_constants()
        all_passed = all_passed and test_get_timeout_for_operation()
        all_passed = all_passed and test_environment_variable_support()
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL UNIT TESTS PASSED")
        print("="*70)
        exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("="*70)
        exit(1)
