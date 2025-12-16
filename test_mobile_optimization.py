"""
Test mobile optimization features.

This test validates:
1. Pagination support (both page and skip styles)
2. Cache-Control headers on GET endpoints
3. Response payload structure
"""
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

def test_pagination_params():
    """Test PaginationParams class with both pagination styles"""
    from backend_app.core.pagination import PaginationParams
    
    # Test page-based pagination
    page_params = PaginationParams(page=2, limit=20)
    assert page_params.page == 2
    assert page_params.skip == 20  # (page - 1) * limit
    assert page_params.limit == 20
    print("✅ Page-based pagination works")
    
    # Test skip-based pagination
    skip_params = PaginationParams(skip=40, limit=20)
    assert skip_params.skip == 40
    assert skip_params.page == 3  # (skip // limit) + 1
    assert skip_params.limit == 20
    print("✅ Skip-based pagination works")
    
    # Test page takes precedence
    both_params = PaginationParams(page=3, skip=10, limit=20)
    assert both_params.page == 3
    assert both_params.skip == 40  # Page-based takes precedence
    print("✅ Page precedence works")


def test_pagination_metadata():
    """Test pagination metadata generation"""
    from backend_app.core.pagination import get_pagination_metadata
    
    # Test with page parameter
    metadata = get_pagination_metadata(total=150, page=2, limit=20)
    assert metadata['page'] == 2
    assert metadata['skip'] == 20
    assert metadata['limit'] == 20
    assert metadata['total'] == 150
    assert metadata['total_pages'] == 8  # ceil(150 / 20)
    assert metadata['has_next'] == True
    assert metadata['has_prev'] == True
    print("✅ Pagination metadata correct")
    
    # Test first page
    first_page = get_pagination_metadata(total=150, page=1, limit=20)
    assert first_page['has_prev'] == False
    assert first_page['has_next'] == True
    print("✅ First page metadata correct")
    
    # Test last page
    last_page = get_pagination_metadata(total=150, page=8, limit=20)
    assert last_page['has_prev'] == True
    assert last_page['has_next'] == False
    print("✅ Last page metadata correct")


def test_cache_headers_middleware():
    """Test cache headers middleware configuration"""
    from backend_app.core.cache_headers import CacheControlMiddleware
    
    # Test initialization with default values
    middleware = CacheControlMiddleware(app=None, max_age=30)
    assert middleware.max_age == 30
    assert '/posts' in middleware.cacheable_paths
    assert '/jobs' in middleware.cacheable_paths
    assert '/users' in middleware.cacheable_paths
    assert '/notifications' in middleware.cacheable_paths
    print("✅ Cache middleware initialization works")
    
    # Test skip paths
    assert '/auth/me' in middleware.skip_paths
    assert '/auth/login' in middleware.skip_paths
    print("✅ Skip paths configured correctly")


def test_pagination_response_format():
    """Test paginated response format"""
    from backend_app.core.pagination import PaginatedResponse
    
    # Create sample data
    items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    
    # Create paginated response
    response = PaginatedResponse.create(
        items=items,
        total=100,
        page=1,
        limit=20,
        skip=0
    )
    
    assert response.success == True
    assert len(response.data) == 2
    assert response.pagination['page'] == 1
    assert response.pagination['total'] == 100
    assert response.pagination['total_pages'] == 5
    assert response.pagination['has_next'] == True
    assert response.pagination['has_prev'] == False
    print("✅ Paginated response format correct")


def test_imports():
    """Test that all mobile optimization modules can be imported"""
    try:
        from backend_app.core.pagination import PaginationParams, get_pagination_metadata
        print("✅ Pagination module imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import pagination: {e}")
        return False
    
    try:
        from backend_app.core.cache_headers import CacheControlMiddleware, add_cache_headers
        print("✅ Cache headers module imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import cache headers: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Testing Mobile Optimization Features")
    print("="*60 + "\n")
    
    try:
        # Test imports first
        if not test_imports():
            print("\n❌ Import tests failed")
            return 1
        
        print("\nTesting pagination...")
        test_pagination_params()
        test_pagination_metadata()
        test_pagination_response_format()
        
        print("\nTesting cache headers...")
        test_cache_headers_middleware()
        
        print("\n" + "="*60)
        print("✅ All mobile optimization tests passed!")
        print("="*60)
        
        print("\nFeatures validated:")
        print("  ✅ Dual pagination support (page & skip)")
        print("  ✅ Pagination metadata generation")
        print("  ✅ Cache-Control middleware configuration")
        print("  ✅ Response format standardization")
        print("\nMobile optimization is ready! 📱")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
