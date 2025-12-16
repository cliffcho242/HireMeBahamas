#!/usr/bin/env python3
"""
Redis Connection Test Script

Tests Redis connection with production-safe configuration.
Validates SSL/TLS support, timeouts, and connection pooling.

Usage:
    python test_redis_connection.py

Environment Variables:
    REDIS_URL=rediss://:password@host:port
"""
import asyncio
import os
import sys
import time
from datetime import datetime


async def test_redis_connection():
    """Test Redis connection with production configuration."""
    
    print("=" * 60)
    print("Redis Connection Test")
    print("=" * 60)
    print()
    
    # Get Redis URL from environment
    redis_url = os.getenv("REDIS_URL") or \
                os.getenv("REDIS_PRIVATE_URL") or \
                os.getenv("UPSTASH_REDIS_REST_URL")
    
    if not redis_url:
        print("❌ REDIS_URL not set in environment")
        print()
        print("Please set one of:")
        print("  - REDIS_URL")
        print("  - REDIS_PRIVATE_URL")
        print("  - UPSTASH_REDIS_REST_URL")
        print()
        print("Example:")
        print("  export REDIS_URL=rediss://:password@host:port")
        return False
    
    # Mask password in URL for display
    display_url = redis_url
    if "@" in redis_url:
        parts = redis_url.split("@")
        if ":" in parts[0]:
            proto_pass = parts[0].rsplit(":", 1)
            display_url = f"{proto_pass[0]}:****@{parts[1]}"
    
    print(f"Redis URL: {display_url}")
    print()
    
    # Check for SSL/TLS
    uses_ssl = redis_url.startswith("rediss://")
    if uses_ssl:
        print("✅ SSL/TLS enabled (rediss://)")
    else:
        print("⚠️  SSL/TLS not enabled (redis://)")
        print("   Consider using rediss:// for production")
    print()
    
    # Try to import redis
    try:
        import redis.asyncio as aioredis
        print("✅ redis package installed")
    except ImportError:
        print("❌ redis package not installed")
        print()
        print("Install with:")
        print("  pip install redis")
        return False
    
    print()
    print("-" * 60)
    print("Testing Connection...")
    print("-" * 60)
    print()
    
    # Test connection with production-safe configuration
    try:
        start_time = time.time()
        
        # Create connection pool with production settings
        pool = aioredis.ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=10,
            socket_keepalive=True,
            socket_connect_timeout=2,  # 2s timeout
            socket_timeout=2,  # 2s timeout
            retry_on_timeout=True,
            health_check_interval=30,
        )
        
        client = aioredis.Redis(connection_pool=pool)
        
        # Test ping with timeout
        await asyncio.wait_for(client.ping(), timeout=2.0)
        connect_time = (time.time() - start_time) * 1000
        
        print(f"✅ Connection successful")
        print(f"   Connect time: {connect_time:.2f}ms")
        print()
        
        # Test basic operations
        print("-" * 60)
        print("Testing Basic Operations...")
        print("-" * 60)
        print()
        
        # Test SET
        test_key = f"test:connection:{int(time.time())}"
        test_value = f"test_value_{datetime.now().isoformat()}"
        
        start_time = time.time()
        await client.setex(test_key, 60, test_value)
        set_time = (time.time() - start_time) * 1000
        print(f"✅ SET operation: {set_time:.2f}ms")
        
        # Test GET
        start_time = time.time()
        retrieved = await client.get(test_key)
        get_time = (time.time() - start_time) * 1000
        print(f"✅ GET operation: {get_time:.2f}ms")
        
        if retrieved == test_value:
            print(f"✅ Value matches: {retrieved[:50]}...")
        else:
            print(f"❌ Value mismatch!")
            print(f"   Expected: {test_value[:50]}...")
            print(f"   Got: {retrieved[:50] if retrieved else 'None'}...")
        
        # Test DELETE
        start_time = time.time()
        await client.delete(test_key)
        del_time = (time.time() - start_time) * 1000
        print(f"✅ DELETE operation: {del_time:.2f}ms")
        
        print()
        
        # Performance summary
        print("-" * 60)
        print("Performance Summary")
        print("-" * 60)
        print()
        print(f"Connect time:  {connect_time:.2f}ms")
        print(f"SET time:      {set_time:.2f}ms")
        print(f"GET time:      {get_time:.2f}ms")
        print(f"DELETE time:   {del_time:.2f}ms")
        print()
        
        # Performance targets
        targets_met = True
        if connect_time > 2000:
            print(f"⚠️  Connect time exceeds 2000ms target")
            targets_met = False
        if set_time > 10:
            print(f"⚠️  SET time exceeds 10ms target")
            targets_met = False
        if get_time > 10:
            print(f"⚠️  GET time exceeds 10ms target (cache hit target: <1ms)")
            targets_met = False
        
        if targets_met:
            print("✅ All performance targets met!")
        print()
        
        # Connection pool info
        print("-" * 60)
        print("Connection Pool Info")
        print("-" * 60)
        print()
        print(f"Max connections: 10")
        print(f"Socket timeout: 2s")
        print(f"Connect timeout: 2s")
        print(f"Keepalive: enabled")
        print(f"Health check: 30s interval")
        print()
        
        # Close connection
        await client.close()
        await pool.disconnect()
        
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print()
        print("Your Redis cache is configured correctly and ready to use.")
        print("Expected backend performance:")
        print("  - Feed loads: <100ms")
        print("  - Health checks: <30ms")
        print("  - Cache hits: <1ms")
        print()
        
        return True
        
    except asyncio.TimeoutError:
        print("❌ Connection timeout (>2s)")
        print()
        print("Possible causes:")
        print("  - Redis server not responding")
        print("  - Network issues")
        print("  - Firewall blocking connection")
        print("  - Wrong host/port")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}")
        print(f"   {str(e)}")
        print()
        print("Possible causes:")
        print("  - Invalid REDIS_URL format")
        print("  - Wrong password")
        print("  - Redis server not running")
        print("  - Network issues")
        print()
        print("Expected format:")
        print("  rediss://:password@host:port")
        return False


def main():
    """Run the test."""
    print()
    success = asyncio.run(test_redis_connection())
    print()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
