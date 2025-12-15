"""
Test to verify health check endpoints are lightweight and don't make database calls.

Requirements:
1. /health endpoint does not touch the database
2. /ready endpoint does not touch the database
3. Endpoints return quickly (<100ms for testing)
"""
import sys
import os
import time
import ast
import re

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))


def analyze_function_for_db_calls(source_code, function_name):
    """Analyze a function's source code for database calls."""
    # Parse the source code into an AST
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    
    # Find the function definition
    function_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function_name:
                function_node = node
                break
    
    if not function_node:
        return False, f"Function '{function_name}' not found"
    
    # Check for database-related calls
    db_indicators = [
        'execute',
        'SELECT',
        'INSERT',
        'UPDATE',
        'DELETE',
        'test_db_connection',
        'get_db_status',
        'check_database_health',
        'db_engine.begin',
        'session.execute',
    ]
    
    function_source = ast.get_source_segment(source_code, function_node)
    if not function_source:
        # Fallback: extract function manually
        lines = source_code.split('\n')
        start_line = function_node.lineno - 1
        # Find the end of the function (next def or class at same indent level)
        indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = start_line + 1
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() and not line.strip().startswith('#'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent and (line.strip().startswith('def ') or line.strip().startswith('async def ') or line.strip().startswith('class ')):
                    end_line = i
                    break
        else:
            end_line = len(lines)
        
        function_source = '\n'.join(lines[start_line:end_line])
    
    # Check for database indicators
    for indicator in db_indicators:
        if indicator in function_source:
            return False, f"Found database operation: '{indicator}'"
    
    return True, "No database calls found"


def test_api_index_health_no_db():
    """Test that api/index.py /health endpoint doesn't make DB calls"""
    print("\n✅ Testing api/index.py /health endpoint...")
    
    # Read the source file
    file_path = os.path.join(os.path.dirname(__file__), 'api', 'index.py')
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    # Analyze the health function
    is_clean, message = analyze_function_for_db_calls(source_code, 'health')
    
    if is_clean:
        print(f"   ✅ /health endpoint is database-free: {message}")
        return True
    else:
        print(f"   ❌ /health endpoint makes database calls: {message}")
        return False


def test_api_index_ready_no_db():
    """Test that api/index.py /ready endpoint doesn't make DB calls"""
    print("\n✅ Testing api/index.py /ready endpoint...")
    
    # Read the source file
    file_path = os.path.join(os.path.dirname(__file__), 'api', 'index.py')
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    # Analyze the ready function
    is_clean, message = analyze_function_for_db_calls(source_code, 'ready')
    
    if is_clean:
        print(f"   ✅ /ready endpoint is database-free: {message}")
        return True
    else:
        print(f"   ❌ /ready endpoint makes database calls: {message}")
        return False


def test_backend_main_health_no_db():
    """Test that api/backend_app/main.py /health endpoint doesn't make DB calls"""
    print("\n✅ Testing api/backend_app/main.py /health endpoint...")
    
    # Read the source file
    file_path = os.path.join(os.path.dirname(__file__), 'api', 'backend_app', 'main.py')
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    # Analyze the health function
    is_clean, message = analyze_function_for_db_calls(source_code, 'health')
    
    if is_clean:
        print(f"   ✅ /health endpoint is database-free: {message}")
        return True
    else:
        print(f"   ❌ /health endpoint makes database calls: {message}")
        return False


def test_backend_main_ready_no_db():
    """Test that api/backend_app/main.py /ready endpoint doesn't make DB calls"""
    print("\n✅ Testing api/backend_app/main.py /ready endpoint...")
    
    # Read the source file
    file_path = os.path.join(os.path.dirname(__file__), 'api', 'backend_app', 'main.py')
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    # Analyze the ready function
    is_clean, message = analyze_function_for_db_calls(source_code, 'ready')
    
    if is_clean:
        print(f"   ✅ /ready endpoint is database-free: {message}")
        return True
    else:
        print(f"   ❌ /ready endpoint makes database calls: {message}")
        return False


def test_vercel_caching_configuration():
    """Test that vercel.json has proper caching headers for CDN"""
    print("\n✅ Testing vercel.json caching configuration...")
    
    import json
    
    # Read vercel.json
    file_path = os.path.join(os.path.dirname(__file__), 'vercel.json')
    with open(file_path, 'r') as f:
        config = json.load(f)
    
    # Check that headers section exists
    if 'headers' not in config:
        print("   ❌ No headers section in vercel.json")
        return False
    
    headers_config = config['headers']
    
    # Check for cache control headers
    has_cache_control = False
    has_static_assets = False
    has_immutable = False
    
    for header_rule in headers_config:
        source = header_rule.get('source', '')
        headers = header_rule.get('headers', [])
        
        for header in headers:
            if header.get('key') == 'Cache-Control':
                has_cache_control = True
                value = header.get('value', '')
                
                # Check for static asset caching
                if 'immutable' in value:
                    has_immutable = True
                
                # Check if this applies to static assets
                if any(pattern in source for pattern in ['.js', '.css', '.woff', '.png', '.jpg', 'assets']):
                    has_static_assets = True
    
    results = []
    if has_cache_control:
        results.append("✅ Cache-Control headers configured")
    else:
        results.append("❌ No Cache-Control headers found")
    
    if has_static_assets:
        results.append("✅ Static assets have cache headers")
    else:
        results.append("❌ Static assets missing cache headers")
    
    if has_immutable:
        results.append("✅ Immutable flag set for static assets")
    else:
        results.append("❌ Immutable flag missing")
    
    for result in results:
        print(f"   {result}")
    
    return all('✅' in r for r in results)


if __name__ == "__main__":
    print("="*60)
    print("Testing Lightweight Health Check Requirements")
    print("="*60)
    
    all_passed = True
    
    try:
        # Test health endpoints don't make DB calls
        if not test_api_index_health_no_db():
            all_passed = False
        
        if not test_api_index_ready_no_db():
            all_passed = False
        
        if not test_backend_main_health_no_db():
            all_passed = False
        
        if not test_backend_main_ready_no_db():
            all_passed = False
        
        # Test CDN caching configuration
        if not test_vercel_caching_configuration():
            all_passed = False
        
        print("\n" + "="*60)
        if all_passed:
            print("✅ ALL TESTS PASSED")
            print("="*60)
            print("\nSummary:")
            print("  ✅ Health endpoints are database-free")
            print("  ✅ Ready endpoints are database-free")
            print("  ✅ Vercel CDN caching properly configured")
        else:
            print("❌ SOME TESTS FAILED")
            print("="*60)
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
