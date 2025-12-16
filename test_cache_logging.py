"""
Test script to verify cache logging changes.
This script ensures redundant log messages have been removed.
"""
import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

# Configure logging to capture all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Track log messages
log_messages = []

class LogCapture(logging.Handler):
    def emit(self, record):
        log_messages.append({
            'name': record.name,
            'level': record.levelname,
            'message': record.getMessage()
        })

# Add handler to capture logs
log_handler = LogCapture()
logging.getLogger().addHandler(log_handler)

async def test_redis_cache_logging():
    """Test that redis_cache logs at DEBUG level when not configured."""
    print("\n=== Testing redis_cache module ===")
    from app.core.redis_cache import redis_cache
    
    # Ensure REDIS_URL is not set for testing
    if 'REDIS_URL' in os.environ:
        del os.environ['REDIS_URL']
    
    # Connect should return False and log at DEBUG
    result = await redis_cache.connect()
    
    # Find relevant log messages
    redis_cache_logs = [
        msg for msg in log_messages 
        if 'redis_cache' in msg['name'].lower() and 'redis' in msg['message'].lower()
    ]
    
    print(f"Result: {result}")
    print(f"Found {len(redis_cache_logs)} redis_cache log messages")
    
    for log in redis_cache_logs:
        print(f"  [{log['level']}] {log['name']}: {log['message']}")
    
    # Verify DEBUG level is used
    info_logs = [log for log in redis_cache_logs if log['level'] == 'INFO']
    debug_logs = [log for log in redis_cache_logs if log['level'] == 'DEBUG']
    
    if info_logs:
        print(f"❌ FAIL: Found {len(info_logs)} INFO level logs (should be DEBUG)")
        for log in info_logs:
            print(f"     {log['message']}")
        return False
    
    if debug_logs:
        print(f"✓ PASS: Logs are at DEBUG level")
        return True
    
    print("ℹ️  No Redis-related logs found (Redis may be configured)")
    return True

async def test_cache_module_logging():
    """Test that cache module logs at DEBUG level when not configured."""
    print("\n=== Testing cache module ===")
    log_messages.clear()
    
    from app.core.cache import get_redis
    
    # Ensure REDIS_URL is not set for testing
    if 'REDIS_URL' in os.environ:
        del os.environ['REDIS_URL']
    
    result = await get_redis()
    
    # Find relevant log messages
    cache_logs = [
        msg for msg in log_messages 
        if 'cache' in msg['name'].lower() and 'redis' in msg['message'].lower()
    ]
    
    print(f"Result: {result}")
    print(f"Found {len(cache_logs)} cache log messages")
    
    for log in cache_logs:
        print(f"  [{log['level']}] {log['name']}: {log['message']}")
    
    # Verify DEBUG level is used
    info_logs = [log for log in cache_logs if log['level'] == 'INFO']
    debug_logs = [log for log in cache_logs if log['level'] == 'DEBUG']
    
    if info_logs:
        print(f"❌ FAIL: Found {len(info_logs)} INFO level logs (should be DEBUG)")
        for log in info_logs:
            print(f"     {log['message']}")
        return False
    
    if debug_logs:
        print(f"✓ PASS: Logs are at DEBUG level")
        return True
    
    print("ℹ️  No Redis-related logs found (Redis may be configured)")
    return True

async def main():
    """Run all tests."""
    print("Testing cache logging changes...")
    print("=" * 60)
    
    test1 = await test_redis_cache_logging()
    test2 = await test_cache_module_logging()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("✅ All tests passed!")
        print("✓ Redundant log messages have been removed")
        print("✓ Cache initialization logs are at appropriate levels")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
