#!/usr/bin/env python3
"""
Test to verify that LazyEngine handles None engine correctly.

This test validates that when get_engine() returns None (due to invalid DATABASE_URL),
LazyEngine.__getattr__ raises a clear RuntimeError with helpful message instead of
a confusing AttributeError about NoneType.
"""

import os
import sys
from unittest.mock import patch

# Import path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def test_lazy_engine_none_handling():
    """Test that LazyEngine handles None engine gracefully with clear error."""
    print("Test: LazyEngine None Engine Handling")
    print("=" * 70)
    
    # Import the database module
    from app.database import LazyEngine
    
    print("\n1. Testing LazyEngine with None engine (simulates invalid DATABASE_URL)...")
    
    # Create a LazyEngine instance
    lazy_engine = LazyEngine()
    
    # Mock get_engine to return None (simulates invalid DATABASE_URL scenario)
    with patch('app.database.get_engine', return_value=None):
        try:
            # Try to access an attribute (like 'connect') on the lazy engine
            # This should raise RuntimeError with clear message, NOT AttributeError
            _ = lazy_engine.connect
            
            # If we get here, the test failed - it should have raised an exception
            print("   ✗ FAILED: No exception raised when accessing attribute on None engine")
            return False
            
        except RuntimeError as e:
            # This is the expected behavior - clear RuntimeError
            error_msg = str(e)
            print(f"   ✓ Raised RuntimeError (expected): {error_msg}")
            
            # Verify the error message is helpful
            required_phrases = [
                "get_engine() returned None",
                "Cannot access attribute 'connect'",
                "DATABASE_URL",
                "postgresql://user:password@host:5432/database"
            ]
            
            missing_phrases = []
            for phrase in required_phrases:
                if phrase not in error_msg:
                    missing_phrases.append(phrase)
            
            if missing_phrases:
                print(f"   ✗ Error message missing helpful phrases: {missing_phrases}")
                return False
            
            print("   ✓ Error message contains all required helpful information")
            
        except AttributeError as e:
            # This is the OLD broken behavior - confusing AttributeError
            error_msg = str(e)
            print(f"   ✗ FAILED: Raised AttributeError (old broken behavior): {error_msg}")
            print("   ✗ Should have raised RuntimeError with clear message instead")
            return False
        
        except Exception as e:
            # Unexpected exception type
            print(f"   ✗ FAILED: Raised unexpected exception: {type(e).__name__}: {e}")
            return False
    
    print("\n2. Testing LazyEngine with different attribute names...")
    
    # Test with a few different attribute names to ensure consistency
    test_attributes = ['connect', 'execute', 'begin', 'dispose']
    
    with patch('app.database.get_engine', return_value=None):
        for attr_name in test_attributes:
            try:
                getattr(lazy_engine, attr_name)
                print(f"   ✗ FAILED: No exception for attribute '{attr_name}'")
                return False
            except RuntimeError as e:
                if f"Cannot access attribute '{attr_name}'" in str(e):
                    print(f"   ✓ Attribute '{attr_name}' handled correctly")
                else:
                    print(f"   ✗ FAILED: Error message doesn't mention attribute '{attr_name}'")
                    return False
            except AttributeError:
                print(f"   ✗ FAILED: AttributeError for '{attr_name}' (should be RuntimeError)")
                return False
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("   - LazyEngine raises clear RuntimeError when engine is None")
    print("   - Error message is helpful and actionable")
    print("   - No more confusing 'NoneType' object has no attribute errors")
    print("=" * 70)
    return True


def main():
    """Run all tests."""
    try:
        success = test_lazy_engine_none_handling()
        return 0 if success else 1
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED WITH EXCEPTION: {type(e).__name__}: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
