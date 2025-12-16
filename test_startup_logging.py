"""
Test script to verify startup logging changes in main.py.
This ensures the consolidated log messages are clear and concise.
"""
import re

def test_main_py_logging():
    """Test that main.py has the correct consolidated log messages."""
    print("Testing main.py logging changes...")
    print("=" * 60)
    
    with open('backend/app/main.py', 'r') as f:
        content = f.read()
    
    # Check for the new consolidated messages
    checks = [
        {
            'name': 'Redis connected success message',
            'pattern': r'logger\.info\("✅ Redis cache connected successfully"\)',
            'expected': True
        },
        {
            'name': 'In-memory cache message',
            'pattern': r'logger\.info\("ℹ️  Using in-memory cache \(Redis not configured\)"\)',
            'expected': True
        },
        {
            'name': 'Cache system ready message',
            'pattern': r'logger\.info\("✅ Cache system ready"\)',
            'expected': True
        },
        {
            'name': 'Redundant "Using in-memory cache fallback"',
            'pattern': r'logger\.info\("Using in-memory cache fallback"\)',
            'expected': False  # Should not exist
        },
        {
            'name': 'Redundant "Cache warmup completed"',
            'pattern': r'logger\.info\("Cache warmup completed"\)',
            'expected': False  # Should not exist
        },
        {
            'name': 'Debug level for module not available',
            'pattern': r'logger\.debug\("Redis cache module not available"\)',
            'expected': True
        }
    ]
    
    all_passed = True
    for check in checks:
        found = bool(re.search(check['pattern'], content))
        expected = check['expected']
        
        if found == expected:
            status = "✓ PASS"
        else:
            status = "❌ FAIL"
            all_passed = False
        
        expected_str = "should exist" if expected else "should NOT exist"
        found_str = "found" if found else "not found"
        
        print(f"{status}: {check['name']}")
        print(f"       Expected: {expected_str}, Actual: {found_str}")
    
    print("=" * 60)
    if all_passed:
        print("✅ All checks passed!")
        print("✓ Redundant log messages removed from main.py")
        print("✓ Clear, consolidated messages in place")
        return 0
    else:
        print("❌ Some checks failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(test_main_py_logging())
