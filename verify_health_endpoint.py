#!/usr/bin/env python3
"""
Verify Health Endpoint Configuration
Tests that all health check requirements are met
"""
import sys
import re
from pathlib import Path

def check_health_endpoint_exists():
    """Verify health endpoint exists in backend/app/main.py"""
    print("✓ Checking if health endpoint exists...")
    
    main_py = Path("backend/app/main.py")
    if not main_py.exists():
        print("❌ backend/app/main.py not found")
        return False
    
    content = main_py.read_text()
    
    # Check for health endpoint definition
    if '@app.get("/health"' not in content:
        print("❌ Health endpoint not found in main.py")
        return False
    
    print("✅ Health endpoint exists at /health")
    return True

def check_health_returns_ok():
    """Verify health endpoint returns status: ok"""
    print("\n✓ Checking if health endpoint returns correct response...")
    
    main_py = Path("backend/app/main.py")
    content = main_py.read_text()
    
    # Look for the health endpoint function - find the return statement
    health_match = re.search(r'@app\.get\("/health".*?def health\(\):.*?return.*?\{.*?"status".*?:.*?"ok".*?\}', content, re.DOTALL)
    if not health_match:
        # Try alternative format
        health_match = re.search(r"@app\.get\('/health'.*?def health\(\):.*?return.*?\{.*?'status'.*?:.*?'ok'.*?\}", content, re.DOTALL)
    
    if health_match:
        print('✅ Health endpoint returns {"status": "ok"}')
        return True
    
    print("❌ Health endpoint does not return correct response")
    return False

def check_no_database_dependency():
    """Verify health endpoint has no database dependency"""
    print("\n✓ Checking that health endpoint has no database dependency...")
    
    main_py = Path("backend/app/main.py")
    content = main_py.read_text()
    
    # Extract health endpoint function - get just the function body
    health_match = re.search(r'def health\(\):.*?""".*?""".*?return \{"status": "ok"\}', content, re.DOTALL)
    if not health_match:
        print("❌ Could not find health endpoint function")
        return False
    
    health_func = health_match.group(0)
    
    # Check for database-related keywords (should NOT be present in function body)
    # But allow them in comments/docstrings
    db_keywords = ['get_db', 'AsyncSession', 'db:', 'db.', 'query(', 'session.']
    found_keywords = [kw for kw in db_keywords if kw in health_func and '"""' not in health_func.split(kw)[0].split('\n')[-1]]
    
    if found_keywords:
        print(f"⚠️  Warning: Health endpoint may have database dependency (found: {found_keywords})")
        return False
    
    print("✅ Health endpoint has no database dependency")
    return True

def check_render_health_path():
    """Verify render.yaml has correct health check path"""
    print("\n✓ Checking Render configuration...")
    
    render_yaml = Path("render.yaml")
    if not render_yaml.exists():
        print("⚠️  render.yaml not found (optional if not using Render)")
        return True
    
    content = render_yaml.read_text()
    
    if 'healthCheckPath: /health' in content:
        print("✅ Render health check path matches: /health")
        return True
    
    print("❌ Render health check path does not match")
    return False

def check_port_configuration():
    """Verify app listens on PORT environment variable"""
    print("\n✓ Checking port configuration...")
    
    procfile = Path("Procfile")
    if not procfile.exists():
        print("⚠️  Procfile not found (optional if not using Render/Heroku)")
        return True
    
    content = procfile.read_text()
    
    if '$PORT' in content:
        print("✅ App listens on $PORT environment variable")
        return True
    
    print("❌ App does not listen on $PORT environment variable")
    return False

def check_vercel_frontend_env():
    """Verify frontend environment variable configuration"""
    print("\n✓ Checking frontend environment variable configuration...")
    
    env_example = Path("frontend/.env.example")
    if not env_example.exists():
        print("⚠️  frontend/.env.example not found")
        return False
    
    content = env_example.read_text()
    
    if 'VITE_API_URL' in content:
        print("✅ Frontend uses VITE_API_URL (correct for Vite/React)")
        return True
    
    print("❌ Frontend environment variable configuration issue")
    return False

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("HEALTH ENDPOINT VERIFICATION")
    print("=" * 70)
    
    checks = [
        ("Health endpoint exists", check_health_endpoint_exists),
        ("Health endpoint returns OK", check_health_returns_ok),
        ("No database dependency", check_no_database_dependency),
        ("Render health path matches", check_render_health_path),
        ("Port configuration", check_port_configuration),
        ("Frontend env vars", check_vercel_frontend_env),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Health endpoint is properly configured.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
