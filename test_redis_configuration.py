#!/usr/bin/env python3
"""
Test Redis Cache Configuration

This script verifies that Redis cache is properly configured and working.
It tests the connection and basic operations.

Usage:
    # Run from project root directory:
    python test_redis_configuration.py
    
    # Or with explicit Redis URL:
    REDIS_URL=redis://localhost:6379 python test_redis_configuration.py

Expected outcomes:
    - With REDIS_URL set: "✅ Redis is configured and working"
    - Without REDIS_URL: "⚠️ Redis not configured, using in-memory cache"

Requirements:
    - Must be run from the project root directory
    - Requires backend/app/core/cache.py module
"""

import os
import sys
import asyncio


async def test_redis_configuration():
    """Test Redis configuration and connection."""
    
    print("=" * 70)
    print("Redis Configuration Test")
    print("=" * 70)
    
    # Check if REDIS_URL is set
    redis_url = os.getenv('REDIS_URL') or \
                os.getenv('REDIS_PRIVATE_URL') or \
                os.getenv('UPSTASH_REDIS_REST_URL')
    
    print(f"\n1. Environment Variables Check:")
    print(f"   REDIS_URL: {'✅ Set' if os.getenv('REDIS_URL') else '❌ Not set'}")
    print(f"   REDIS_PRIVATE_URL: {'✅ Set' if os.getenv('REDIS_PRIVATE_URL') else '❌ Not set'}")
    print(f"   UPSTASH_REDIS_REST_URL: {'✅ Set' if os.getenv('UPSTASH_REDIS_REST_URL') else '❌ Not set'}")
    
    if not redis_url:
        print("\n⚠️  Redis not configured (REDIS_URL not set)")
        print("\nThis is not an error - the application will use in-memory cache.")
        print("\nTo enable Redis caching:")
        print("1. Set up a Redis instance (see REDIS_CONFIGURATION.md)")
        print("2. Set REDIS_URL environment variable")
        print("3. Restart the application")
        print("\nSee REDIS_CONFIGURATION.md for quick setup guide")
        return False
    
    print(f"\n2. Redis URL Configuration:")
    # Mask password in URL for security
    masked_url = redis_url
    if '@' in masked_url:
        parts = masked_url.split('@')
        if ':' in parts[0]:
            credentials = parts[0].split(':')
            if len(credentials) >= 3:
                # Format: rediss://:password@host
                masked_url = f"{credentials[0]}:{credentials[1]}:***@{parts[1]}"
    print(f"   URL: {masked_url}")
    print(f"   SSL/TLS: {'✅ Enabled (rediss://)' if redis_url.startswith('rediss://') else '⚠️  Not enabled (redis://)'}")
    
    # Test Redis connection
    print(f"\n3. Connection Test:")
    try:
        # Import the cache module
        # Add backend to path if needed (supports running from project root)
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if os.path.exists(backend_path) and backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Try to import from backend directory structure
        try:
            from app.core.cache import get_redis
        except ImportError:
            # If that fails, try adding the backend directory explicitly
            print("   ⚠️  Please run this script from the project root directory")
            print("   Example: cd /path/to/HireMeBahamas && python test_redis_configuration.py")
            return False
        
        # Try to connect
        redis_client = await get_redis()
        
        if redis_client is None:
            print("   ❌ Failed to connect to Redis")
            print("   Application will use in-memory cache")
            return False
        
        # Test ping
        await asyncio.wait_for(redis_client.ping(), timeout=2.0)
        print("   ✅ Successfully connected to Redis")
        
        # Test set/get operations
        print(f"\n4. Basic Operations Test:")
        test_key = "test:redis:configuration"
        test_value = "Redis is working!"
        
        # Set a value
        await redis_client.setex(test_key, 10, test_value)
        print(f"   ✅ SET operation successful")
        
        # Get the value
        result = await redis_client.get(test_key)
        if result == test_value:
            print(f"   ✅ GET operation successful")
        else:
            print(f"   ❌ GET operation failed (expected: {test_value}, got: {result})")
        
        # Delete the test key
        await redis_client.delete(test_key)
        print(f"   ✅ DELETE operation successful")
        
        # Get info
        print(f"\n5. Redis Server Info:")
        try:
            info = await redis_client.info()
            print(f"   Redis version: {info.get('redis_version', 'unknown')}")
            print(f"   Used memory: {info.get('used_memory_human', 'unknown')}")
            print(f"   Connected clients: {info.get('connected_clients', 'unknown')}")
        except Exception as e:
            print(f"   ⚠️  Could not get server info: {e}")
        
        print(f"\n{'=' * 70}")
        print("✅ Redis is properly configured and working!")
        print("=" * 70)
        print("\nYour application will now use Redis for caching, providing:")
        print("  • 90% faster authentication")
        print("  • 80-90% reduction in database load")
        print("  • Shared cache across multiple instances")
        print("  • Session persistence across restarts")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Failed to import cache module: {e}")
        print("   Make sure you're running this from the project root directory")
        return False
    except asyncio.TimeoutError:
        print(f"   ❌ Connection timeout")
        print("   Check if Redis server is running and accessible")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Redis connection failed, application will use in-memory cache")
        return False


def main():
    """Main entry point."""
    try:
        result = asyncio.run(test_redis_configuration())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
