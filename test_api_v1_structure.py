"""
Test script to verify the v1 API structure.

This test ensures that the app/api/v1 directory properly imports
all routers and creates the versioned API structure.
"""
import sys
import os

# Add the repository root to the path
repo_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(repo_root, 'backend')
sys.path.insert(0, backend_path)


def test_v1_api_structure():
    """Test that app/api/v1 modules can be imported."""
    print("Testing app/api/v1 structure...")
    
    try:
        # Test importing the v1 API router
        from app.api.v1 import router as v1_router
        
        # Verify the router has the correct prefix
        assert hasattr(v1_router, 'prefix'), "v1 router should have a prefix attribute"
        assert v1_router.prefix == "/api/v1", f"Expected prefix '/api/v1', got '{v1_router.prefix}'"
        
        # Test importing individual v1 modules
        from app.api.v1 import analytics
        from app.api.v1 import auth
        from app.api.v1 import debug
        from app.api.v1 import feed
        from app.api.v1 import health
        from app.api.v1 import hireme
        from app.api.v1 import jobs
        from app.api.v1 import messages
        from app.api.v1 import notifications
        from app.api.v1 import posts
        from app.api.v1 import profile_pictures
        from app.api.v1 import reviews
        from app.api.v1 import upload
        from app.api.v1 import users
        
        # Verify all modules have a router attribute
        modules = [
            analytics, auth, debug, feed, health, hireme, jobs,
            messages, notifications, posts, profile_pictures,
            reviews, upload, users
        ]
        
        for module in modules:
            assert hasattr(module, 'router'), f"Module {module.__name__} should have a router attribute"
        
        print("✓ app/api/v1 structure is correct")
        print(f"  - V1 router prefix: {v1_router.prefix}")
        print(f"  - All {len(modules)} modules imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ app/api/v1 structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_v1_router_routes():
    """Test that the v1 router includes all expected routes."""
    print("\nTesting v1 router routes...")
    
    try:
        from app.api.v1 import router as v1_router
        
        # Check that routes were included
        # Note: We can't easily inspect included routers without running the app,
        # but we can verify the router object exists and has the correct structure
        
        assert hasattr(v1_router, 'routes'), "v1 router should have routes attribute"
        
        print(f"✓ v1 router has {len(v1_router.routes)} routes")
        return True
        
    except Exception as e:
        print(f"✗ v1 router routes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*60)
    print("API v1 Structure Test")
    print("="*60)
    
    # Run tests
    test1_passed = test_v1_api_structure()
    test2_passed = test_v1_router_routes()
    
    print("\n" + "="*60)
    if test1_passed and test2_passed:
        print("✓ All v1 API structure tests passed!")
        print("="*60)
        sys.exit(0)
    else:
        print("✗ Some v1 API structure tests failed")
        print("="*60)
        sys.exit(1)
