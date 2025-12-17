"""
Simple Demo of Database Retry Logic (Standalone)

This is a standalone demo that doesn't require database connection.
It demonstrates the retry behavior with simulated failures.

Author: Copilot
Date: December 2025
"""

import sys
import logging
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.db_retry import db_retry, retry_db_operation

# Configure logging to see retry attempts
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s - %(message)s'
)


def demo_successful_retry():
    """Demo: Operation fails twice then succeeds."""
    print("\n" + "=" * 70)
    print("Demo 1: Successful Retry After Transient Failures")
    print("=" * 70)
    
    attempt_count = {"value": 0}
    
    @db_retry(retries=3, delay=0.1)
    def flaky_operation():
        """Simulates operation that fails sometimes."""
        attempt_count["value"] += 1
        print(f"  → Attempt #{attempt_count['value']}")
        
        if attempt_count["value"] < 3:
            raise ConnectionError("Simulated transient failure")
        
        return "SUCCESS"
    
    try:
        result = flaky_operation()
        print(f"✅ Result: {result}")
        print(f"   Total attempts: {attempt_count['value']}")
    except Exception as e:
        print(f"❌ Failed: {e}")


def demo_max_retries_exceeded():
    """Demo: All retries fail."""
    print("\n" + "=" * 70)
    print("Demo 2: All Retries Exhausted")
    print("=" * 70)
    
    @db_retry(retries=3, delay=0.1)
    def always_fails():
        """Simulates persistent failure."""
        print(f"  → Attempting operation...")
        raise RuntimeError("Persistent database error")
    
    try:
        always_fails()
    except RuntimeError as e:
        print(f"✅ Exception properly raised after retries: {e}")


def demo_immediate_success():
    """Demo: Operation succeeds immediately (no retries needed)."""
    print("\n" + "=" * 70)
    print("Demo 3: Immediate Success (No Retries Needed)")
    print("=" * 70)
    
    @db_retry(retries=3, delay=0.1)
    def successful_operation():
        """Simulates successful operation."""
        print(f"  → Operation executing...")
        return {"users": [{"id": 1, "name": "John"}]}
    
    result = successful_operation()
    print(f"✅ Result: {result}")
    print(f"   No retries were needed!")


def demo_inline_retry():
    """Demo: Using retry_db_operation without decorator."""
    print("\n" + "=" * 70)
    print("Demo 4: Inline Retry (Without Decorator)")
    print("=" * 70)
    
    attempt_count = {"value": 0}
    
    def fetch_data():
        attempt_count["value"] += 1
        print(f"  → Attempt #{attempt_count['value']}")
        
        if attempt_count["value"] < 2:
            raise TimeoutError("Database timeout")
        
        return ["record1", "record2", "record3"]
    
    try:
        result = retry_db_operation(fetch_data, retries=3, delay=0.1)
        print(f"✅ Result: {result}")
        print(f"   Total attempts: {attempt_count['value']}")
    except Exception as e:
        print(f"❌ Failed: {e}")


def demo_safety_documentation():
    """Demo: Show safety rules in docstring."""
    print("\n" + "=" * 70)
    print("Demo 5: Safety Rules and Documentation")
    print("=" * 70)
    
    from app.core import db_retry as module
    
    # Extract key safety rules from docstring
    docstring = module.__doc__
    
    print("Key Safety Rules from Module Documentation:")
    print()
    
    # Look for safety-related lines
    for line in docstring.split('\n'):
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['✅', '🚫', 'safe', 'unsafe', 'never', 'only']):
            if line:
                print(f"  {line}")
    
    print("\n✅ Always check documentation before using retry logic!")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           Database Retry Logic - Interactive Demo                   ║
║                                                                      ║
║  This demo shows the retry behavior with simulated failures.        ║
║                                                                      ║
║  Safety Rules:                                                       ║
║    ✅ DO: Use on idempotent read operations (SELECT)                ║
║    🚫 DON'T: Use on writes (INSERT/UPDATE/DELETE)                   ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run all demos
    demo_successful_retry()
    demo_max_retries_exceeded()
    demo_immediate_success()
    demo_inline_retry()
    demo_safety_documentation()
    
    print("\n" + "=" * 70)
    print("All demos completed successfully!")
    print("=" * 70)
    print("\n✓ See backend/app/core/db_retry.py for implementation")
    print("✓ See backend/test_db_retry.py for comprehensive tests")
    print("✓ See backend/example_db_retry_usage.py for real-world examples\n")
