"""
Example Usage of Safe Database Retry Logic

This module demonstrates how to properly use the db_retry decorator
for idempotent read operations in the HireMeBahamas application.

⚠️  CRITICAL SAFETY RULE: Only use db_retry on idempotent read operations.
🚫 Never use on write operations (INSERT, UPDATE, DELETE).

⚠️  NOTE: The db_retry decorator is designed for synchronous functions.
For async database operations, use asyncio-native retry patterns.

Author: Copilot
Date: December 2025
"""

import logging

# Note: Actual import paths depend on how you run the module:
# - From backend directory: from app.core.db_retry import db_retry
# - From project root: from backend.app.core.db_retry import db_retry
# This example uses the "from backend directory" convention
from app.core.db_retry import db_retry, retry_db_operation

# Configure logging to see retry attempts
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================================
# ✅ EXAMPLE 1: Safe usage with decorator on read-only function (SYNCHRONOUS)
# ============================================================================
# Note: This is a conceptual example. The actual HireMeBahamas codebase uses
# async SQLAlchemy, but db_retry is designed for synchronous operations per
# the problem statement requirements (uses time.sleep, not asyncio.sleep).

@db_retry(retries=3, delay=1)
def count_users_by_role(role: str) -> int:
    """
    Count users by role with automatic retry on transient failures.
    
    This is SAFE because:
    - It's a read-only operation (COUNT/SELECT)
    - It's idempotent (same result when called multiple times)
    - No data modification occurs
    
    Args:
        role: User role to count
        
    Returns:
        Number of users with that role
        
    Note:
        This is a synchronous example. For actual async database operations
        in the HireMeBahamas codebase, use asyncio-native retry patterns.
    """
    # Conceptual synchronous database call
    # In practice, with async SQLAlchemy, use different retry approach
    from sqlalchemy import func, select
    
    # This would be: session.query(func.count(User.id)).filter(User.role == role).scalar()
    # or similar synchronous ORM call
    
    # For demonstration purposes (would need actual sync session)
    return 0  # Placeholder


# ============================================================================
# ✅ EXAMPLE 2: Safe usage for checking existence (SYNCHRONOUS)
# ============================================================================

@db_retry(retries=3, delay=1)
def user_exists(email: str) -> bool:
    """
    Check if user exists with retry logic.
    
    This is SAFE because:
    - It's a read-only operation (SELECT/EXISTS)
    - It's idempotent (same answer each time)
    - No data modification
    
    Args:
        email: Email address to check
        
    Returns:
        True if user exists, False otherwise
    """
    # Conceptual synchronous database call
    # Would be: session.query(exists().where(User.email == email)).scalar()
    return False  # Placeholder


# ============================================================================
# ✅ EXAMPLE 3: Safe usage with retry_db_operation function (SYNCHRONOUS)
# ============================================================================

def get_user_stats_with_retry():
    """
    Get user statistics using inline retry logic.
    
    This demonstrates using retry_db_operation() without a decorator.
    """
    
    def fetch_stats():
        # Conceptual synchronous database call
        # Would be: session.query(func.count(User.id)).scalar()
        return {"total_users": 0, "active_users": 0}  # Placeholder
    
    # Use retry_db_operation for inline retry logic
    return retry_db_operation(
        fetch_stats,
        retries=3,
        delay=1.0
    )


# ============================================================================
# 🚫 EXAMPLE 4: UNSAFE - DO NOT USE RETRY ON WRITES
# ============================================================================

# ❌ BAD: Never use @db_retry on write operations
# This could lead to duplicate records, data corruption, or race conditions

# @db_retry(retries=3, delay=1)  # ❌ DON'T DO THIS
def create_user_UNSAFE_EXAMPLE(user_data: dict):
    """
    ❌ UNSAFE EXAMPLE - DO NOT USE RETRY ON WRITES
    
    This is UNSAFE because:
    - It's a write operation (INSERT)
    - Retrying could create duplicate records
    - Not idempotent
    
    NEVER decorate write operations with @db_retry!
    """
    # Conceptual write operation
    # Would be: session.add(User(**user_data)); session.commit()
    pass


# ============================================================================
# ✅ EXAMPLE 5: Correct approach for writes (no retry)
# ============================================================================

def create_user_SAFE(user_data: dict):
    """
    ✅ SAFE - Write operation without retry logic
    
    For write operations, handle errors at a higher level:
    - Let the caller decide whether to retry
    - Implement idempotency tokens if needed
    - Use database constraints to prevent duplicates
    """
    try:
        # Conceptual write operation
        # Would be: session.add(User(**user_data)); session.commit()
        pass
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise


# ============================================================================
# ✅ EXAMPLE 6: Custom retry parameters for slow operations
# ============================================================================

@db_retry(retries=5, delay=2.0)
def get_table_row_count(table_name: str) -> int:
    """
    Get row count for a table with longer retry delays.
    
    Use higher retries and delays for:
    - Complex queries that might timeout
    - Operations during high load periods
    - Cold start scenarios
    
    Args:
        table_name: Name of the table to count
        
    Returns:
        Number of rows in the table
    """
    # Conceptual synchronous database call
    # Would be: session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    return 0  # Placeholder


# ============================================================================
# Main execution - Note about usage
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                 Safe Database Retry Logic Examples                   ║
║                                                                      ║
║  This module demonstrates proper usage of the db_retry decorator    ║
║  for idempotent read operations only.                               ║
║                                                                      ║
║  ✅ DO: Use on SELECT queries (reads) - synchronous operations      ║
║  🚫 DON'T: Use on INSERT/UPDATE/DELETE (writes)                     ║
║                                                                      ║
║  NOTE: db_retry is designed for synchronous functions.              ║
║  For async operations, use asyncio-native retry patterns.           ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    print("✓ See backend/demo_db_retry_simple.py for a working demonstration")
    print("✓ See the function examples in this file for usage patterns")
    print("✓ Read the docstrings for detailed explanations")
    print("✓ Always follow the safety rules: reads only, never writes!\n")
