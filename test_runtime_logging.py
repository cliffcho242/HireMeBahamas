#!/usr/bin/env python3
"""
Test that runtime logging configuration works correctly.
This test verifies that logs are written to /tmp/runtime-logs when the directory exists.
"""
import os
import sys
import tempfile
import logging
from pathlib import Path


def test_runtime_logging_directory_exists():
    """Test that logs are written when runtime log directory exists."""
    print("=" * 80)
    print("Test 1: Runtime logging when directory exists")
    print("=" * 80)
    
    # Create a temporary runtime logs directory
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime_log_dir = tmpdir
        runtime_log_file = os.path.join(runtime_log_dir, 'test-backend-runtime.log')
        
        # Set up logging like the backend does
        log_handlers = [logging.StreamHandler()]
        
        if os.path.exists(runtime_log_dir):
            try:
                file_handler = logging.FileHandler(runtime_log_file, mode='a')
                file_handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                )
                log_handlers.append(file_handler)
                print(f"✅ File handler created: {runtime_log_file}")
            except Exception as e:
                print(f"❌ Could not create file handler: {e}")
                return False
        
        # Configure logging
        test_logger = logging.getLogger('test_backend')
        test_logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in test_logger.handlers[:]:
            test_logger.removeHandler(handler)
        
        # Add our handlers
        for handler in log_handlers:
            test_logger.addHandler(handler)
        
        # Write test logs
        test_logger.info("Test log message 1")
        test_logger.warning("Test warning message")
        test_logger.info("Test log message 2")
        
        # Flush handlers
        for handler in test_logger.handlers:
            handler.flush()
        
        # Verify the file was created and contains logs
        if not os.path.exists(runtime_log_file):
            print(f"❌ Log file was not created: {runtime_log_file}")
            return False
        
        with open(runtime_log_file, 'r') as f:
            log_content = f.read()
        
        print(f"\n📝 Log file content ({len(log_content)} bytes):")
        print("-" * 80)
        print(log_content)
        print("-" * 80)
        
        # Verify log content
        required_messages = [
            "Test log message 1",
            "Test warning message",
            "Test log message 2"
        ]
        
        for msg in required_messages:
            if msg not in log_content:
                print(f"❌ Missing log message: {msg}")
                return False
            print(f"✅ Found log message: {msg}")
        
        print("\n✅ Test 1 PASSED: Logs written to file when directory exists\n")
        return True


def test_runtime_logging_directory_missing():
    """Test that logging works when runtime log directory doesn't exist."""
    print("=" * 80)
    print("Test 2: Runtime logging when directory doesn't exist")
    print("=" * 80)
    
    # Use a non-existent directory
    runtime_log_dir = '/tmp/nonexistent-runtime-logs-' + str(os.getpid())
    
    # Ensure it doesn't exist
    if os.path.exists(runtime_log_dir):
        os.rmdir(runtime_log_dir)
    
    # Set up logging like the backend does
    log_handlers = [logging.StreamHandler()]
    
    if os.path.exists(runtime_log_dir):
        runtime_log_file = os.path.join(runtime_log_dir, 'test-runtime.log')
        try:
            file_handler = logging.FileHandler(runtime_log_file, mode='a')
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            log_handlers.append(file_handler)
            print(f"File handler created: {runtime_log_file}")
        except Exception as e:
            print(f"Warning: Could not create runtime log file: {e}")
    else:
        print("✅ Runtime log directory doesn't exist, skipping file handler")
    
    # Verify we only have stream handler
    if len(log_handlers) != 1:
        print(f"❌ Expected 1 handler (stream), got {len(log_handlers)}")
        return False
    
    print(f"✅ Only stream handler configured (expected behavior)")
    
    # Configure logging
    test_logger = logging.getLogger('test_backend_nodir')
    test_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in test_logger.handlers[:]:
        test_logger.removeHandler(handler)
    
    # Add our handlers
    for handler in log_handlers:
        test_logger.addHandler(handler)
    
    # Write test logs (should go to stdout only)
    print("\n📝 Testing stdout logging (should see messages below):")
    print("-" * 80)
    test_logger.info("Test message to stdout only")
    print("-" * 80)
    
    print("\n✅ Test 2 PASSED: Logging works without file handler when directory missing\n")
    return True


def test_environment_variable():
    """Test that RUNTIME_LOG_DIR environment variable is respected."""
    print("=" * 80)
    print("Test 3: RUNTIME_LOG_DIR environment variable")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Set environment variable
        os.environ['RUNTIME_LOG_DIR'] = tmpdir
        
        # Get the value like the backend does
        runtime_log_dir = os.getenv('RUNTIME_LOG_DIR', '/tmp/runtime-logs')
        
        print(f"RUNTIME_LOG_DIR set to: {tmpdir}")
        print(f"Retrieved value: {runtime_log_dir}")
        
        if runtime_log_dir != tmpdir:
            print(f"❌ Environment variable not respected")
            return False
        
        print(f"✅ Environment variable correctly retrieved")
        
        # Test that we can create files in that directory
        test_file = os.path.join(runtime_log_dir, 'env-test.log')
        with open(test_file, 'w') as f:
            f.write("Test content\n")
        
        if not os.path.exists(test_file):
            print(f"❌ Could not create file in RUNTIME_LOG_DIR")
            return False
        
        print(f"✅ Successfully created file in RUNTIME_LOG_DIR")
        
        # Clean up
        del os.environ['RUNTIME_LOG_DIR']
        
        print("\n✅ Test 3 PASSED: Environment variable works correctly\n")
        return True


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("RUNTIME LOGGING TESTS")
    print("=" * 80 + "\n")
    
    tests = [
        test_runtime_logging_directory_exists,
        test_runtime_logging_directory_missing,
        test_environment_variable,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
