"""
Example Usage of Safe Database Retry Logic

This module demonstrates how to properly use the db_retry decorator
for idempotent read operations in the HireMeBahamas application.

⚠️  CRITICAL SAFETY RULE: Only use db_retry on idempotent read operations.
🚫 Never use on write operations (INSERT, UPDATE, DELETE).

Author: Copilot
Date: December 2025
"""

import asyncio
import logging

# Note: Actual import paths depend on how you run the module:
# - From backend directory: from app.core.db_retry import db_retry
# - From project root: from backend.app.core.db_retry import db_retry
# This example uses the "from backend directory" convention
from app.core.db_retry import db_retry, retry_db_operation
from app.database import get_db, AsyncSessionLocal
from app.models import User
from sqlalchemy import select

# Configure logging to see retry attempts
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================================
# ✅ EXAMPLE 1: Safe usage with decorator on read-only function
# ============================================================================

@db_retry(retries=3, delay=1)
async def get_user_by_email(email: str):
    """
    Get a user by email with automatic retry on transient failures.
    
    This is SAFE because:
    - It's a read-only operation (SELECT)
    - It's idempotent (same result when called multiple times)
    - No data modification occurs
    
    Args:
        email: User email address
        
    Returns:
        User object or None if not found
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


# ============================================================================
# ✅ EXAMPLE 2: Safe usage with decorator on count operation
# ============================================================================

@db_retry(retries=3, delay=1)
async def count_active_users():
    """
    Count active users with retry logic.
    
    This is SAFE because:
    - It's a read-only operation (COUNT)
    - It's idempotent
    - No data modification
    
    Returns:
        Number of active users
    """
    async with AsyncSessionLocal() as session:
        from sqlalchemy import func
        result = await session.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        return result.scalar()


# ============================================================================
# ✅ EXAMPLE 3: Safe usage with retry_db_operation function
# ============================================================================

async def get_users_by_role_with_retry(role: str):
    """
    Get users by role using inline retry logic.
    
    This demonstrates using retry_db_operation() without a decorator.
    """
    
    async def fetch_users():
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.role == role)
            )
            return result.scalars().all()
    
    # Use retry_db_operation for inline retry logic
    return await retry_db_operation(
        fetch_users,
        retries=3,
        delay=1.0
    )


# ============================================================================
# 🚫 EXAMPLE 4: UNSAFE - DO NOT USE RETRY ON WRITES
# ============================================================================

# ❌ BAD: Never use @db_retry on write operations
# This could lead to duplicate records, data corruption, or race conditions

# @db_retry(retries=3, delay=1)  # ❌ DON'T DO THIS
async def create_user_UNSAFE_EXAMPLE(user_data: dict):
    """
    ❌ UNSAFE EXAMPLE - DO NOT USE RETRY ON WRITES
    
    This is UNSAFE because:
    - It's a write operation (INSERT)
    - Retrying could create duplicate records
    - Not idempotent
    
    NEVER decorate write operations with @db_retry!
    """
    async with AsyncSessionLocal() as session:
        user = User(**user_data)
        session.add(user)
        await session.commit()
        return user


# ============================================================================
# ✅ EXAMPLE 5: Correct approach for writes (no retry)
# ============================================================================

async def create_user_SAFE(user_data: dict):
    """
    ✅ SAFE - Write operation without retry logic
    
    For write operations, handle errors at a higher level:
    - Let the caller decide whether to retry
    - Implement idempotency tokens if needed
    - Use database constraints to prevent duplicates
    """
    async with AsyncSessionLocal() as session:
        try:
            user = User(**user_data)
            session.add(user)
            await session.commit()
            return user
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create user: {e}")
            raise


# ============================================================================
# ✅ EXAMPLE 6: Custom retry parameters for slow operations
# ============================================================================

@db_retry(retries=5, delay=2.0)
async def get_user_statistics():
    """
    Get user statistics with longer retry delays.
    
    Use higher retries and delays for:
    - Complex queries that might timeout
    - Operations during high load periods
    - Cold start scenarios
    
    Returns:
        Dictionary with user statistics
    """
    async with AsyncSessionLocal() as session:
        from sqlalchemy import func
        
        total_users = await session.execute(
            select(func.count(User.id))
        )
        active_users = await session.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        
        return {
            'total': total_users.scalar(),
            'active': active_users.scalar(),
        }


# ============================================================================
# Demo function to show retry in action
# ============================================================================

async def demo_retry_logic():
    """
    Demonstrate the retry logic with simulated failures.
    
    This shows what happens when database operations fail and retry.
    """
    print("=" * 70)
    print("Database Retry Logic Demo")
    print("=" * 70)
    
    # Simulate a failing database operation
    attempt_count = {"value": 0}
    
    @db_retry(retries=3, delay=0.5)
    async def flaky_database_operation():
        """Simulates a database operation that fails sometimes."""
        attempt_count["value"] += 1
        print(f"\n→ Attempting database operation (attempt #{attempt_count['value']})")
        
        # Fail on first 2 attempts, succeed on 3rd
        if attempt_count["value"] < 3:
            print(f"  ✗ Simulated transient failure (attempt {attempt_count['value']})")
            raise ConnectionError("Simulated database connection timeout")
        
        print(f"  ✓ Operation succeeded on attempt {attempt_count['value']}")
        return {"status": "success", "attempts": attempt_count["value"]}
    
    try:
        result = await flaky_database_operation()
        print(f"\n✅ Final result: {result}")
        print(f"   Total attempts needed: {result['attempts']}")
    except Exception as e:
        print(f"\n❌ Operation failed after all retries: {e}")
    
    print("=" * 70)


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                 Safe Database Retry Logic Examples                   ║
║                                                                      ║
║  This module demonstrates proper usage of the db_retry decorator    ║
║  for idempotent read operations only.                               ║
║                                                                      ║
║  ✅ DO: Use on SELECT queries (reads)                               ║
║  🚫 DON'T: Use on INSERT/UPDATE/DELETE (writes)                     ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run the demo
    asyncio.run(demo_retry_logic())
    
    print("\n✓ See the function examples in this file for proper usage patterns.")
    print("✓ Read the docstrings for detailed explanations.")
    print("✓ Always follow the safety rules: reads only, never writes!\n")
