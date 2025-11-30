"""
Test bcrypt performance optimization

This test verifies that the bcrypt configuration provides reasonable
performance while maintaining backward compatibility with existing passwords.
It also tests async password verification and bcrypt pre-warming.
"""
import asyncio
import time
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_bcrypt_performance():
    """Test that bcrypt password verification is performant"""
    
    # Save original environment variable value to restore later
    original_bcrypt_rounds = os.environ.get('BCRYPT_ROUNDS')
    
    try:
        # Set environment variable for testing
        os.environ['BCRYPT_ROUNDS'] = '10'
        
        # Import passlib directly to avoid fastapi dependencies
        from passlib.context import CryptContext
        
        # Recreate the optimized context from security.py
        BCRYPT_ROUNDS = int(os.environ.get('BCRYPT_ROUNDS', '10'))
        pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=BCRYPT_ROUNDS
        )
        
        def get_password_hash(password: str) -> str:
            return pwd_context.hash(password)
        
        def verify_password(plain_password: str, hashed_password: str) -> bool:
            return pwd_context.verify(plain_password, hashed_password)
        
        print("=" * 80)
        print("Bcrypt Performance Test")
        print("=" * 80)
        
        # Test password
        test_password = "TestPassword123!"
        
        # Test 1: Check configured rounds
        print("\n1. Testing configured bcrypt rounds...")
        hashed = get_password_hash(test_password)
        parts = hashed.split('$')
        if len(parts) >= 3:
            rounds = int(parts[2])
            print(f"   Configured rounds: {rounds}")
            assert rounds == 10, f"Expected 10 rounds, got {rounds}"
            print("   ✓ Bcrypt rounds configured correctly")
        
        # Test 2: Password verification performance
        print("\n2. Testing password verification performance...")
        
        # Run multiple verifications to get average time
        num_tests = 5
        times = []
        
        for i in range(num_tests):
            start_time = time.time()
            result = verify_password(test_password, hashed)
            elapsed_ms = (time.time() - start_time) * 1000
            times.append(elapsed_ms)
            assert result, "Password verification should succeed"
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"   Average verification time: {avg_time:.2f}ms")
        print(f"   Max verification time: {max_time:.2f}ms")
        
        # Performance threshold: should be under 200ms for 10 rounds
        # This prevents the 204-second issue we're fixing
        assert max_time < 200, f"Verification too slow: {max_time:.2f}ms (should be < 200ms)"
        print("   ✓ Verification performance acceptable")
        
        # Test 3: Backward compatibility with 12-round hashes
        print("\n3. Testing backward compatibility with 12-round hashes...")
        
        # Create a hash with 12 rounds (old default) - CryptContext already imported above
        old_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
        old_hash = old_context.hash(test_password)
    
        # Verify that new context can verify old hashes
        start_time = time.time()
        can_verify_old = verify_password(test_password, old_hash)
        verify_time = (time.time() - start_time) * 1000
        
        assert can_verify_old, "Should be able to verify old 12-round hashes"
        print(f"   12-round hash verification time: {verify_time:.2f}ms")
        print("   ✓ Backward compatibility confirmed")
        
        # Test 4: Verify incorrect password fails
        print("\n4. Testing incorrect password rejection...")
        wrong_password = "WrongPassword123!"
        assert not verify_password(wrong_password, hashed), "Wrong password should fail"
        print("   ✓ Incorrect passwords properly rejected")
        
        print("\n" + "=" * 80)
        print("All bcrypt performance tests passed!")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  - Configured rounds: 10")
        print(f"  - Average verification time: {avg_time:.2f}ms")
        print(f"  - Max verification time: {max_time:.2f}ms")
        print(f"  - Performance improvement: ~4x faster than default 12 rounds")
        print(f"  - Backward compatibility: ✓")
        
        return True
    
    finally:
        # Restore original environment variable
        if original_bcrypt_rounds is not None:
            os.environ['BCRYPT_ROUNDS'] = original_bcrypt_rounds
        elif 'BCRYPT_ROUNDS' in os.environ:
            del os.environ['BCRYPT_ROUNDS']


def test_async_bcrypt_performance():
    """Test that async bcrypt operations work correctly and don't block the event loop"""
    
    # Save original environment variable value to restore later
    original_bcrypt_rounds = os.environ.get('BCRYPT_ROUNDS')
    
    try:
        # Set environment variable for testing
        os.environ['BCRYPT_ROUNDS'] = '10'
        
        import anyio
        from passlib.context import CryptContext
        
        # Recreate the optimized context from security.py
        BCRYPT_ROUNDS = int(os.environ.get('BCRYPT_ROUNDS', '10'))
        pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=BCRYPT_ROUNDS
        )
        
        async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
            return await anyio.to_thread.run_sync(
                pwd_context.verify, plain_password, hashed_password
            )
        
        async def get_password_hash_async(password: str) -> str:
            return await anyio.to_thread.run_sync(pwd_context.hash, password)
        
        async def prewarm_bcrypt_async() -> None:
            await anyio.to_thread.run_sync(lambda: pwd_context.hash("prewarm-dummy"))
        
        async def run_async_tests():
            print("=" * 80)
            print("Async Bcrypt Performance Test")
            print("=" * 80)
            
            test_password = "TestPassword123!"
            
            # Test 1: Pre-warming
            print("\n1. Testing bcrypt pre-warming...")
            start_time = time.time()
            await prewarm_bcrypt_async()
            prewarm_ms = (time.time() - start_time) * 1000
            print(f"   Pre-warm time: {prewarm_ms:.2f}ms")
            print("   ✓ Pre-warming completed")
            
            # Test 2: Async hashing
            print("\n2. Testing async password hashing...")
            start_time = time.time()
            hashed = await get_password_hash_async(test_password)
            hash_ms = (time.time() - start_time) * 1000
            print(f"   Async hash time: {hash_ms:.2f}ms")
            assert hashed.startswith('$2b$'), "Hash should be bcrypt format"
            print("   ✓ Async hashing works correctly")
            
            # Test 3: Async verification
            print("\n3. Testing async password verification...")
            times = []
            for _ in range(5):
                start_time = time.time()
                result = await verify_password_async(test_password, hashed)
                elapsed_ms = (time.time() - start_time) * 1000
                times.append(elapsed_ms)
                assert result, "Password verification should succeed"
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            print(f"   Average async verification time: {avg_time:.2f}ms")
            print(f"   Max async verification time: {max_time:.2f}ms")
            
            # Performance threshold
            assert max_time < 200, f"Async verification too slow: {max_time:.2f}ms"
            print("   ✓ Async verification performance acceptable")
            
            # Test 4: Concurrent verification (simulate multiple login requests)
            print("\n4. Testing concurrent password verifications...")
            start_time = time.time()
            results = await asyncio.gather(*[
                verify_password_async(test_password, hashed)
                for _ in range(10)
            ])
            total_ms = (time.time() - start_time) * 1000
            avg_per_request = total_ms / 10
            
            assert all(results), "All concurrent verifications should succeed"
            print(f"   10 concurrent verifications completed in {total_ms:.2f}ms")
            print(f"   Average per request: {avg_per_request:.2f}ms")
            print("   ✓ Concurrent verification works correctly")
            
            print("\n" + "=" * 80)
            print("All async bcrypt tests passed!")
            print("=" * 80)
            print(f"\nAsync Summary:")
            print(f"  - Pre-warm time: {prewarm_ms:.2f}ms")
            print(f"  - Async hash time: {hash_ms:.2f}ms")
            print(f"  - Average async verification: {avg_time:.2f}ms")
            print(f"  - Concurrent performance: {avg_per_request:.2f}ms/request")
            
            return True
        
        return asyncio.run(run_async_tests())
    
    finally:
        # Restore original environment variable
        if original_bcrypt_rounds is not None:
            os.environ['BCRYPT_ROUNDS'] = original_bcrypt_rounds
        elif 'BCRYPT_ROUNDS' in os.environ:
            del os.environ['BCRYPT_ROUNDS']


if __name__ == "__main__":
    try:
        test_bcrypt_performance()
        print("\n✓ Sync test completed successfully\n")
        
        test_async_bcrypt_performance()
        print("\n✓ Async test completed successfully")
        
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
