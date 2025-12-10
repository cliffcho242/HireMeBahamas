#!/usr/bin/env python3
"""
Tests for filter_postgres_logs.py

This script tests the PostgreSQL log filter to ensure it correctly:
1. Identifies benign messages
2. Corrects log levels
3. Suppresses benign messages when requested
4. Calculates accurate statistics
"""

import json
import subprocess
import sys
from typing import Dict, List


# Test cases
TEST_CASES = [
    {
        "name": "Database ready message (miscategorized as error)",
        "input": {
            "message": "2025-12-10 02:55:37.131 UTC [6] LOG:  database system is ready to accept connections",
            "attributes": {"level": "error"},
            "timestamp": "2025-12-10T02:55:37.553241247Z"
        },
        "expected_benign": True,
        "expected_level": "info",
        "expected_original_level": "error"
    },
    {
        "name": "Autovacuum launcher started (miscategorized as error)",
        "input": {
            "message": "2025-12-10 02:55:37.234 UTC [7] LOG:  autovacuum launcher started",
            "attributes": {"level": "error"},
            "timestamp": "2025-12-10T02:55:37.234Z"
        },
        "expected_benign": True,
        "expected_level": "info",
        "expected_original_level": "error"
    },
    {
        "name": "Actual database error",
        "input": {
            "message": "2025-12-10 02:55:38.456 UTC [10] ERROR:  relation \"users\" does not exist",
            "attributes": {"level": "error"},
            "timestamp": "2025-12-10T02:55:38.456Z"
        },
        "expected_benign": False,
        "expected_level": "error",
        "expected_original_level": None
    },
    {
        "name": "Warning message",
        "input": {
            "message": "2025-12-10 02:55:39.123 UTC [11] WARNING:  deprecated configuration parameter",
            "attributes": {"level": "warning"},
            "timestamp": "2025-12-10T02:55:39.123Z"
        },
        "expected_benign": False,
        "expected_level": "warning",
        "expected_original_level": None
    },
    {
        "name": "Checkpoint starting (miscategorized as error)",
        "input": {
            "message": "2025-12-10 03:00:00.000 UTC [8] LOG:  checkpoint starting: time",
            "attributes": {"level": "error"},
            "timestamp": "2025-12-10T03:00:00.000Z"
        },
        "expected_benign": True,
        "expected_level": "info",
        "expected_original_level": "error"
    },
    {
        "name": "Shutdown message (miscategorized as error)",
        "input": {
            "message": "2025-12-10 03:01:00.000 UTC [1] LOG:  database system was shut down at 2025-12-10 03:00:00 UTC",
            "attributes": {"level": "error"},
            "timestamp": "2025-12-10T03:01:00.000Z"
        },
        "expected_benign": True,
        "expected_level": "info",
        "expected_original_level": "error"
    },
    {
        "name": "Fatal error",
        "input": {
            "message": "2025-12-10 03:02:00.000 UTC [12] FATAL:  password authentication failed for user \"testuser\"",
            "attributes": {"level": "error"},
            "timestamp": "2025-12-10T03:02:00.000Z"
        },
        "expected_benign": False,
        "expected_level": "error",
        "expected_original_level": None
    }
]


def run_filter(input_data: List[Dict], args: List[str] = None) -> List[Dict]:
    """
    Run the filter script with the given input data.
    
    Args:
        input_data: List of log entries to filter
        args: Additional command line arguments
        
    Returns:
        List of filtered log entries
    """
    if args is None:
        args = []
    
    # Convert input to JSONL format (one JSON object per line)
    input_text = '\n'.join(json.dumps(entry) for entry in input_data)
    
    # Run the filter
    cmd = ['python', 'filter_postgres_logs.py'] + args
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = proc.communicate(input=input_text)
    
    # Parse output
    results = []
    for line in stdout.strip().split('\n'):
        if line:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # Skip non-JSON lines
    
    return results


def test_basic_filtering():
    """Test basic log filtering and level correction."""
    print("Testing basic filtering and level correction...")
    
    passed = 0
    failed = 0
    
    for test_case in TEST_CASES:
        name = test_case["name"]
        input_entry = test_case["input"]
        
        results = run_filter([input_entry])
        
        if not results:
            print(f"  ❌ {name}: No output received")
            failed += 1
            continue
        
        output = results[0]
        
        # Check benign flag
        is_benign = output.get('attributes', {}).get('benign', False)
        if is_benign != test_case["expected_benign"]:
            print(f"  ❌ {name}: Expected benign={test_case['expected_benign']}, got {is_benign}")
            failed += 1
            continue
        
        # Check level
        level = output.get('attributes', {}).get('level')
        if level != test_case["expected_level"]:
            print(f"  ❌ {name}: Expected level={test_case['expected_level']}, got {level}")
            failed += 1
            continue
        
        # Check original level
        original_level = output.get('attributes', {}).get('original_level')
        if original_level != test_case["expected_original_level"]:
            if test_case["expected_original_level"] is not None:
                print(f"  ❌ {name}: Expected original_level={test_case['expected_original_level']}, got {original_level}")
                failed += 1
                continue
        
        print(f"  ✅ {name}")
        passed += 1
    
    return passed, failed


def test_suppress_benign():
    """Test that benign messages can be suppressed."""
    print("\nTesting benign message suppression...")
    
    # Run with suppress-benign flag
    input_data = [tc["input"] for tc in TEST_CASES]
    results = run_filter(input_data, args=['--suppress-benign'])
    
    # Count expected non-benign messages
    expected_count = sum(1 for tc in TEST_CASES if not tc["expected_benign"])
    actual_count = len(results)
    
    if actual_count == expected_count:
        print(f"  ✅ Suppression works correctly: {actual_count} non-benign messages shown")
        return 1, 0
    else:
        print(f"  ❌ Expected {expected_count} messages, got {actual_count}")
        return 0, 1


def test_statistics():
    """Test statistics output."""
    print("\nTesting statistics output...")
    
    input_data = [tc["input"] for tc in TEST_CASES]
    
    cmd = ['python', 'filter_postgres_logs.py', '--stats']
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    input_text = '\n'.join(json.dumps(entry) for entry in input_data)
    stdout, stderr = proc.communicate(input=input_text)
    
    # Check that stats are printed to stderr
    if "PostgreSQL Log Statistics" in stderr:
        print(f"  ✅ Statistics output generated")
        
        # Check for expected counts
        if f"Total entries:        {len(TEST_CASES)}" in stderr:
            print(f"  ✅ Correct total count: {len(TEST_CASES)}")
            return 1, 0
        else:
            print(f"  ❌ Total count mismatch")
            return 0, 1
    else:
        print(f"  ❌ No statistics output")
        return 0, 1


def test_non_json_passthrough():
    """Test that non-JSON lines are passed through unchanged."""
    print("\nTesting non-JSON passthrough...")
    
    non_json_line = "This is a plain text log line"
    
    cmd = ['python', 'filter_postgres_logs.py']
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = proc.communicate(input=non_json_line)
    
    if non_json_line in stdout:
        print(f"  ✅ Non-JSON line passed through unchanged")
        return 1, 0
    else:
        print(f"  ❌ Non-JSON line was modified or lost")
        return 0, 1


def main():
    """Run all tests."""
    print("=" * 70)
    print("PostgreSQL Log Filter Tests")
    print("=" * 70)
    
    total_passed = 0
    total_failed = 0
    
    # Run tests
    passed, failed = test_basic_filtering()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_suppress_benign()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_statistics()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_non_json_passthrough()
    total_passed += passed
    total_failed += failed
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"Test Results: {total_passed} passed, {total_failed} failed")
    print("=" * 70)
    
    if total_failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total_failed} test(s) failed")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTests cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
