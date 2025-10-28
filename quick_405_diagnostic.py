#!/usr/bin/env python3
"""
Quick 405 Error Diagnostic Tool
Fast diagnosis and fix for HireBahamas authentication 405 errors
"""

import requests
import time
import json
from pathlib import Path


def test_authentication_endpoints():
    """Test authentication endpoints for 405 errors"""
    print("Testing authentication endpoints...")

    api_base = "https://hiremebahamas-backend.railway.app"
    endpoints = ["/api/auth/login", "/auth/login", "/api/auth/register"]

    test_data = {"email": "admin@hiremebahamas.com", "password": "AdminPass123!"}

    results = []

    for endpoint in endpoints:
        url = f"{api_base}{endpoint}"
        print(f"\nTesting: {url}")

        # Test OPTIONS (CORS preflight)
        try:
            options_response = requests.options(url, timeout=10)
            options_status = options_response.status_code
            print(f"  OPTIONS: {options_status}")

            if options_status == 405:
                print("  ❌ 405 ERROR: Backend not handling OPTIONS requests")

        except Exception as e:
            print(f"  OPTIONS failed: {e}")
            options_status = "Error"

        # Test POST
        try:
            post_response = requests.post(
                url,
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            post_status = post_response.status_code
            print(f"  POST: {post_status}")

            if post_status == 405:
                print("  ❌ 405 ERROR: Backend not accepting POST requests")
            elif post_status == 200:
                print("  ✅ Login endpoint working")

        except Exception as e:
            print(f"  POST failed: {e}")
            post_status = "Error"

        results.append(
            {"endpoint": endpoint, "options": options_status, "post": post_status}
        )

    return results


def check_frontend_config():
    """Check frontend API configuration"""
    print("\nChecking frontend configuration...")

    api_file = Path("frontend/src/services/api.ts")
    issues = []

    if api_file.exists():
        print("✅ API service file found")

        with open(api_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check base URL
        import re

        base_url_match = re.search(r'baseURL:\s*[\'"]([^\'"]+)[\'"]', content)
        if base_url_match:
            base_url = base_url_match.group(1)
            print(f"  Base URL: {base_url}")
        else:
            issues.append("Base URL not found in API config")

        # Check for 405 error handling
        if "405" not in content:
            issues.append("No specific 405 error handling")

    else:
        issues.append("API service file not found")

    return issues


def check_backend_routes():
    """Check backend route definitions"""
    print("\nAnalyzing backend routes...")

    # Find potential backend files
    backend_files = []
    for pattern in [
        "*backend*.py",
        "*server*.py",
        "final_backend.py",
        "ULTIMATE_BACKEND_FIXED.py",
    ]:
        backend_files.extend(Path(".").glob(pattern))

    auth_routes = []
    route_issues = []

    for file_path in backend_files[:5]:  # Check first 5 files
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find auth routes
            import re

            routes = re.findall(
                r'@app\.route\([\'"]([^\'"]*auth[^\'"]*)[\'"].*methods\s*=\s*\[([^\]]+)\]',
                content,
            )

            for route_path, methods in routes:
                auth_routes.append(
                    {"path": route_path, "methods": methods, "file": file_path.name}
                )

                # Check for issues
                if "POST" in methods and "OPTIONS" not in methods:
                    route_issues.append(
                        f"Route {route_path} in {file_path.name} missing OPTIONS"
                    )

        except Exception as e:
            print(f"  Error reading {file_path.name}: {e}")

    print(f"  Found {len(auth_routes)} auth routes")
    for route in auth_routes:
        print(f"    {route['path']} [{route['methods']}] in {route['file']}")

    return route_issues


def generate_fix_recommendations(test_results, frontend_issues, route_issues):
    """Generate specific fix recommendations"""
    print("\n" + "=" * 50)
    print("DIAGNOSIS RESULTS & RECOMMENDATIONS")
    print("=" * 50)

    has_405_errors = any(
        result["options"] == 405 or result["post"] == 405 for result in test_results
    )

    if has_405_errors:
        print("\n🔴 CRITICAL: 405 Errors Detected!")
        print("\nImmediate fixes needed:")

        # Check which endpoints have 405 errors
        for result in test_results:
            if result["options"] == 405:
                print(f"  - Add OPTIONS method to {result['endpoint']}")
            if result["post"] == 405:
                print(f"  - Fix POST method on {result['endpoint']}")

        print("\n🔧 Recommended Actions:")
        print("1. Update backend route definitions to include OPTIONS")
        print("2. Add proper CORS headers")
        print("3. Verify backend deployment is complete")

    else:
        print("\n✅ No 405 errors detected in current tests")

    # Frontend issues
    if frontend_issues:
        print(f"\n⚠️ Frontend issues ({len(frontend_issues)}):")
        for issue in frontend_issues:
            print(f"  - {issue}")

    # Route issues
    if route_issues:
        print(f"\n⚠️ Route issues ({len(route_issues)}):")
        for issue in route_issues:
            print(f"  - {issue}")

    return has_405_errors


def create_fix_script():
    """Create automated fix script"""
    fix_script = '''#!/usr/bin/env python3
"""Quick 405 Fix Script"""

import re
from pathlib import Path

def fix_backend_routes():
    """Add OPTIONS to auth routes"""
    print("Fixing backend routes...")
    
    # Target the main backend file
    backend_file = Path("ULTIMATE_BACKEND_FIXED.py")
    if not backend_file.exists():
        backend_file = Path("final_backend.py") 
    if not backend_file.exists():
        print("❌ No main backend file found")
        return
        
    with open(backend_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Fix routes missing OPTIONS
    original_content = content
    content = re.sub(
        r'methods\\s*=\\s*\\["POST"\\]',
        'methods=["POST", "OPTIONS"]',
        content
    )
    content = re.sub(
        r"methods\\s*=\\s*\\['POST'\\]",
        "methods=['POST', 'OPTIONS']",
        content
    )
    
    if content != original_content:
        with open(backend_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed routes in {backend_file.name}")
    else:
        print("ℹ️ No route fixes needed")

def fix_frontend_api():
    """Add 405 error handling to frontend"""
    print("Fixing frontend API...")
    
    api_file = Path("frontend/src/services/api.ts")
    if not api_file.exists():
        print("❌ Frontend API file not found")
        return
        
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "status === 405" not in content:
        # Add 405 handling in error interceptor
        error_handler = """
    // Handle 405 Method Not Allowed
    if (error.response?.status === 405) {
      console.error('405 Method Not Allowed:', error.config?.url);
      throw new Error('Service temporarily unavailable. Please try again.');
    }
"""
        
        # Insert before existing error handling
        if "console.error('API Error':" in content:
            content = content.replace(
                "console.error('API Error':",
                error_handler + "\\n    console.error('API Error':"
            )
            
            with open(api_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Added 405 error handling to frontend")
        else:
            print("⚠️ Could not find insertion point for error handler")
    else:
        print("ℹ️ 405 error handling already present")

if __name__ == "__main__":
    print("🔧 Applying quick fixes for 405 errors...")
    fix_backend_routes() 
    fix_frontend_api()
    print("✅ Fixes applied! Test the login again.")
'''

    with open("quick_405_fix.py", "w", encoding="utf-8") as f:
        f.write(fix_script)

    print(f"\n🔧 Fix script created: quick_405_fix.py")


def main():
    """Main diagnostic function"""
    print("🔍 Quick 405 Error Diagnostics for HireBahamas")
    print("=" * 50)

    # Run diagnostics
    test_results = test_authentication_endpoints()
    frontend_issues = check_frontend_config()
    route_issues = check_backend_routes()

    # Generate recommendations
    has_critical_issues = generate_fix_recommendations(
        test_results, frontend_issues, route_issues
    )

    # Create fix script
    create_fix_script()

    print("\n" + "=" * 50)
    print("NEXT STEPS:")
    print("1. Run: python quick_405_fix.py")
    print("2. Test login again in browser")
    print("3. Check browser DevTools Network tab")
    print("=" * 50)

    return has_critical_issues


if __name__ == "__main__":
    main()
