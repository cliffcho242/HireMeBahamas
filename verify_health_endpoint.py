#!/usr/bin/env python3
"""
Verify Health Endpoint Configuration
Tests that all health check requirements are met
"""
import sys
import re
from pathlib import Path

def check_health_endpoint_exists():
    """Verify health endpoint exists in api/backend_app/main.py"""
    print("✓ Checking if health endpoint exists...")
    
    main_py = Path("api/backend_app/main.py")
    if not main_py.exists():
        print("❌ api/backend_app/main.py not found")
        return False
    
    content = main_py.read_text()
    
    # Check for health endpoint definition
    if '@app.get("/health"' not in content:
        print("❌ Health endpoint not found in main.py")
        return False
    
    print("✅ Health endpoint exists at /health in api/backend_app/main.py")
    return True

def check_health_returns_ok():
    """Verify health endpoint returns status: ok"""
    print("\n✓ Checking if health endpoint returns correct response...")
    
    main_py = Path("api/backend_app/main.py")
    if not main_py.exists():
        print("❌ api/backend_app/main.py not found")
        return False
    
    content = main_py.read_text()
    
    # Look for the health endpoint response - simpler pattern
    if '"status": "ok"' in content or "'status': 'ok'" in content:
        print('✅ Health endpoint returns {"status": "ok"}')
        return True
    
    print("❌ Health endpoint does not return correct response")
    return False

def check_no_database_dependency():
    """Verify health endpoint has no database dependency"""
    print("\n✓ Checking that health endpoint has no database dependency...")
    
    main_py = Path("api/backend_app/main.py")
    if not main_py.exists():
        print("❌ api/backend_app/main.py not found")
        return False
    
    content = main_py.read_text()
    
    # Extract health endpoint function - simplified pattern
    health_section = re.search(r'@app\.get\("/health".*?def health\(\):.*?return JSONResponse', content, re.DOTALL)
    if not health_section:
        print("❌ Could not find health endpoint function")
        return False
    
    health_func = health_section.group(0)
    
    # Check for database-related keywords (should NOT be present)
    db_keywords = ['get_db', 'AsyncSession', 'execute', 'query', 'session.', 'db.']
    found_keywords = [kw for kw in db_keywords if kw in health_func.lower()]
    
    if found_keywords:
        print(f"⚠️  Warning: Health endpoint may have database dependency (found: {found_keywords})")
        return False
    
    # Check for positive indicators of no DB access
    if 'NO database' in content or 'no database dependency' in content.lower():
        print("✅ Health endpoint explicitly documented as having no database dependency")
        return True
    
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
    
    # Check Procfile first
    procfile = Path("Procfile")
    if procfile.exists():
        content = procfile.read_text()
        if '$PORT' in content:
            print("✅ App listens on $PORT environment variable (Procfile)")
            return True
    
    # Check render.yaml as alternative
    render_yaml = Path("render.yaml")
    if render_yaml.exists():
        content = render_yaml.read_text()
        if '$PORT' in content or '${PORT}' in content:
            print("✅ App listens on $PORT environment variable (render.yaml)")
            return True
    
    print("⚠️  Could not verify PORT configuration (Procfile or render.yaml not found)")
    return True  # Don't fail if using different deployment method

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
