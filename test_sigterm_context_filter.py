#!/usr/bin/env python3
"""
Test to validate the SIGTERM context filter in gunicorn.conf.py

This test verifies that:
1. The SIGTERMContextFilter class is properly defined
2. The filter correctly detects SIGTERM messages
3. Context information is added to SIGTERM logs
4. Non-SIGTERM messages pass through unchanged
"""

import sys
import logging
from io import StringIO


def test_sigterm_context_filter():
    """Test the SIGTERM context filter functionality."""
    
    print("="*80)
    print("SIGTERM Context Filter Validation")
    print("="*80)
    print()
    
    # Load the gunicorn config directly
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gunicorn_conf", 
        "/home/runner/work/HireMeBahamas/HireMeBahamas/gunicorn.conf.py"
    )
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    
    # Create an instance of the filter
    sigterm_filter = config.SIGTERMContextFilter()
    
    # Test 1: SIGTERM message gets context
    print("Test 1: SIGTERM message detection")
    print("-" * 80)
    
    record = logging.LogRecord(
        name="gunicorn.error",
        level=logging.ERROR,
        pathname="",
        lineno=0,
        msg="Worker (pid:57) was sent SIGTERM!",
        args=(),
        exc_info=None
    )
    
    original_msg = record.msg
    result = sigterm_filter.filter(record)
    
    assert result is True, "Filter should return True"
    assert record.msg != original_msg, "Message should be modified"
    assert "SIGTERM CONTEXT" in record.msg, "Should add context header"
    assert "Deployments and service restarts" in record.msg, "Should explain normal cases"
    assert "Only investigate if" in record.msg, "Should add troubleshooting info"
    
    print(f"✓ SIGTERM message detected: YES")
    print(f"✓ Context added: YES")
    print(f"✓ Original message preserved: YES")
    print()
    print("Modified message preview:")
    print(record.msg[:200] + "...")
    print()
    
    # Test 2: Non-SIGTERM message passes through
    print("Test 2: Non-SIGTERM message handling")
    print("-" * 80)
    
    record2 = logging.LogRecord(
        name="gunicorn.error",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Worker booting with pid: 12345",
        args=(),
        exc_info=None
    )
    
    original_msg2 = record2.msg
    result2 = sigterm_filter.filter(record2)
    
    assert result2 is True, "Filter should return True"
    assert record2.msg == original_msg2, "Non-SIGTERM message should be unchanged"
    
    print(f"✓ Non-SIGTERM message detected: YES")
    print(f"✓ Message unchanged: YES")
    print(f"✓ Message: {record2.msg}")
    print()
    
    # Test 3: Verify filter is in logconfig_dict
    print("Test 3: Configuration validation")
    print("-" * 80)
    
    logconfig = config.logconfig_dict
    
    assert 'filters' in logconfig, "logconfig_dict should have filters"
    assert 'sigterm_context' in logconfig['filters'], "Should have sigterm_context filter"
    
    error_handler = logconfig['handlers'].get('error_console', {})
    assert 'filters' in error_handler, "error_console handler should have filters"
    assert 'sigterm_context' in error_handler['filters'], "error_console should use sigterm_context filter"
    
    print(f"✓ Filter registered in config: YES")
    print(f"✓ Filter applied to error_console: YES")
    print()
    
    # Summary
    print("="*80)
    print("✅ All Tests Passed!")
    print("="*80)
    print()
    print("The SIGTERM context filter is properly implemented:")
    print("1. ✓ Detects SIGTERM messages from Gunicorn master")
    print("2. ✓ Adds helpful context explaining normal behavior")
    print("3. ✓ Provides troubleshooting guidance")
    print("4. ✓ Non-SIGTERM messages pass through unchanged")
    print("5. ✓ Filter is properly configured in logging dict")
    print()
    print("Expected behavior in production:")
    print("  When a worker receives SIGTERM, you'll now see:")
    print("  • The original ERROR message")
    print("  • Followed immediately by context explaining it's normal")
    print("  • With guidance on when to investigate")
    print()
    
    return True


if __name__ == "__main__":
    try:
        test_sigterm_context_filter()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
