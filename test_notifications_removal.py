#!/usr/bin/env python3
"""
Test script to verify fake notifications have been removed
Checks that notification components use empty/real data only
"""

import re
import sys
from pathlib import Path


def check_notifications_component():
    """Check Notifications.tsx for fake data"""
    print("\n🔍 Checking Notifications Component...")
    
    notifications_file = Path("frontend/src/components/Notifications.tsx")
    
    if not notifications_file.exists():
        print(f"❌ Notifications component not found at {notifications_file}")
        return False
    
    content = notifications_file.read_text()
    
    # Check that notifications state is initialized with empty array
    if "useState<NotificationItem[]>([]);" in content or "useState<NotificationItem[]>([]);" in content.replace('\n', '').replace(' ', ''):
        print("✅ Notifications initialized with empty array (no fake data)")
    else:
        # Check if there's any hardcoded notification data
        fake_patterns = [
            r'useState.*\[\s*\{',  # useState with object array
            r'const notifications = \[.*\{',  # Direct array with objects
        ]
        
        for pattern in fake_patterns:
            if re.search(pattern, content, re.DOTALL):
                print(f"⚠️  Possible hardcoded notification data found")
                return False
        
        print("✅ No fake notification data detected")
    
    # Check for comments about real data
    if "Real notifications" in content or "real notifications" in content:
        print("✅ Component has comments about using real API data")
    
    return True


def check_notification_api():
    """Check if there's a real notification API"""
    print("\n🔍 Checking for Notification API...")
    
    api_file = Path("frontend/src/services/api.ts")
    
    if not api_file.exists():
        print(f"❌ API service file not found at {api_file}")
        return False
    
    content = api_file.read_text()
    
    # Check if there's a notifications API section
    if "notification" in content.lower():
        print("✅ Notification API methods found in api.ts")
    else:
        print("ℹ️  No notification API yet (component ready for future integration)")
    
    return True


def check_for_fake_data_generators():
    """Check for any fake data generation scripts"""
    print("\n🔍 Checking for Fake Data Generators...")
    
    root = Path(".")
    fake_patterns = ["fake", "mock", "dummy"]
    
    found_fake_files = []
    
    for pattern in fake_patterns:
        # Check for Python files
        for py_file in root.glob(f"**/*{pattern}*.py"):
            if "node_modules" not in str(py_file) and ".git" not in str(py_file):
                found_fake_files.append(str(py_file))
        
        # Check for TypeScript/JavaScript files
        for ts_file in root.glob(f"**/*{pattern}*.ts*"):
            if "node_modules" not in str(ts_file) and ".git" not in str(ts_file):
                found_fake_files.append(str(ts_file))
    
    if found_fake_files:
        print(f"ℹ️  Found {len(found_fake_files)} files with 'fake/mock/dummy' in name:")
        for f in found_fake_files[:5]:  # Show first 5
            print(f"    - {f}")
        if len(found_fake_files) > 5:
            print(f"    ... and {len(found_fake_files) - 5} more")
        print("ℹ️  These may be test utilities (not necessarily a problem)")
    else:
        print("✅ No fake data generator files found")
    
    return True


def check_notification_content():
    """Deep check of notification component content"""
    print("\n🔍 Deep Check: Notification Component Content...")
    
    notifications_file = Path("frontend/src/components/Notifications.tsx")
    content = notifications_file.read_text()
    
    # Count the notification array initialization
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'useState' in line and 'NotificationItem[]' in line:
            print(f"  Line {i}: {line.strip()}")
            if '([])' in line or '([ ])' in line:
                print("  ✅ Initialized with empty array")
            elif '([{' in line:
                print("  ⚠️  Initialized with data array")
                return False
    
    # Check for sample/fake notification objects
    fake_keywords = ['sample', 'fake', 'dummy', 'test notification', 'example']
    for keyword in fake_keywords:
        if keyword in content.lower():
            print(f"  ⚠️  Found keyword '{keyword}' - may indicate fake data")
    
    # Check that it shows empty state
    if "No notifications yet" in content or "no notifications" in content.lower():
        print("  ✅ Has proper empty state message")
    
    return True


def main():
    """Run all notification verification tests"""
    print("=" * 60)
    print("TESTING FAKE NOTIFICATION REMOVAL")
    print("=" * 60)
    
    tests = [
        ("Notifications Component Check", check_notifications_component),
        ("Notification API Check", check_notification_api),
        ("Fake Data Generators Check", check_for_fake_data_generators),
        ("Notification Content Deep Check", check_notification_content),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Fake notifications have been removed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
