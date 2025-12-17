"""
Test Edge Caching and CDN Configuration (Vercel Frontend)

This test validates that:
1. Assets have immutable cache headers (max-age=31536000)
2. API routes have no-store cache control
3. React Query is configured with proper staleTime and gcTime
"""
import json
import re


def test_vercel_config_assets_cache():
    """Test that vercel.json configures assets with immutable cache headers"""
    with open('vercel.json', 'r') as f:
        config = json.load(f)
    
    # Find assets header configuration
    assets_headers = None
    for header_config in config.get('headers', []):
        if header_config['source'] == '/assets/(.*)':
            assets_headers = header_config
            break
    
    assert assets_headers is not None, "Assets header configuration not found"
    
    # Check Cache-Control header
    cache_control = None
    for header in assets_headers['headers']:
        if header['key'] == 'Cache-Control':
            cache_control = header['value']
            break
    
    assert cache_control is not None, "Cache-Control header not found for assets"
    assert 'max-age=31536000' in cache_control, "Assets should have max-age=31536000"
    assert 'immutable' in cache_control, "Assets should have immutable cache directive"
    print("✅ Assets have immutable cache headers: public, max-age=31536000, immutable")


def test_vercel_config_api_no_store():
    """Test that vercel.json configures API routes with no-store"""
    with open('vercel.json', 'r') as f:
        config = json.load(f)
    
    # Check routes configuration for API
    api_route = None
    for route in config.get('routes', []):
        if '/api/' in route.get('src', ''):
            api_route = route
            break
    
    assert api_route is not None, "API route configuration not found"
    assert 'headers' in api_route, "API route should have headers"
    assert api_route['headers'].get('Cache-Control') == 'no-store', \
        "API routes should have no-store cache control"
    print("✅ API routes have no-store cache control")


def test_react_query_cache_config():
    """Test that React Query is configured with proper cache times"""
    with open('frontend/src/config/reactQuery.ts', 'r') as f:
        content = f.read()
    
    # Check staleTime configuration
    stale_time_match = re.search(r'staleTime:\s*1000\s*\*\s*30', content)
    assert stale_time_match is not None, "staleTime should be 1000 * 30 (30 seconds)"
    print("✅ React Query staleTime: 30 seconds")
    
    # Check gcTime configuration (formerly cacheTime in v4)
    gc_time_match = re.search(r'gcTime:\s*1000\s*\*\s*60\s*\*\s*60', content)
    assert gc_time_match is not None, "gcTime should be 1000 * 60 * 60 (1 hour)"
    print("✅ React Query gcTime: 1 hour")


def test_static_file_extensions_cached():
    """Test that static file extensions have immutable cache headers"""
    with open('vercel.json', 'r') as f:
        config = json.load(f)
    
    # Check JS/CSS files
    js_css_config = None
    for header_config in config.get('headers', []):
        if 'js|css' in header_config['source']:
            js_css_config = header_config
            break
    
    assert js_css_config is not None, "JS/CSS header configuration not found"
    
    cache_control = None
    for header in js_css_config['headers']:
        if header['key'] == 'Cache-Control':
            cache_control = header['value']
            break
    
    assert cache_control is not None, "Cache-Control header not found for JS/CSS files"
    assert 'max-age=31536000' in cache_control, "JS/CSS should have max-age=31536000"
    assert 'immutable' in cache_control, "JS/CSS should have immutable cache directive"
    print("✅ Static files (JS/CSS) have immutable cache headers")
    
    # Check image files
    image_config = None
    for header_config in config.get('headers', []):
        if 'jpg|jpeg|png' in header_config['source']:
            image_config = header_config
            break
    
    assert image_config is not None, "Image header configuration not found"
    
    cache_control = None
    for header in image_config['headers']:
        if header['key'] == 'Cache-Control':
            cache_control = header['value']
            break
    
    assert cache_control is not None, "Cache-Control header not found for images"
    assert 'max-age=31536000' in cache_control, "Images should have max-age=31536000"
    assert 'immutable' in cache_control, "Images should have immutable cache directive"
    print("✅ Images have immutable cache headers")


def test_html_not_cached():
    """Test that HTML files have proper cache control (no aggressive caching)"""
    with open('vercel.json', 'r') as f:
        config = json.load(f)
    
    # Check index.html configuration
    html_config = None
    for header_config in config.get('headers', []):
        if header_config['source'] == '/index.html':
            html_config = header_config
            break
    
    assert html_config is not None, "HTML header configuration not found"
    
    cache_control = None
    for header in html_config['headers']:
        if header['key'] == 'Cache-Control':
            cache_control = header['value']
            break
    
    assert cache_control is not None, "Cache-Control header not found for HTML"
    assert 'max-age=0' in cache_control or 'must-revalidate' in cache_control, \
        "HTML should not be aggressively cached"
    print("✅ HTML files have proper cache control (max-age=0, must-revalidate)")


def main():
    """Run all cache configuration tests"""
    print("\n🧪 Testing Edge Caching and CDN Configuration\n")
    print("=" * 60)
    
    try:
        test_vercel_config_assets_cache()
        test_vercel_config_api_no_store()
        test_react_query_cache_config()
        test_static_file_extensions_cached()
        test_html_not_cached()
        
        print("\n" + "=" * 60)
        print("\n✅ All edge caching tests passed!")
        print("\n📊 Cache Strategy Summary:")
        print("   • Assets: public, max-age=31536000, immutable (1 year)")
        print("   • API routes: no-store (always fresh)")
        print("   • React Query: staleTime=30s, gcTime=1hr")
        print("   • HTML: max-age=0, must-revalidate (always fresh)")
        print("\n🚀 Result: Instant page loads + zero backend hit for static routes")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
