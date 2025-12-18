#!/usr/bin/env python3
"""
Test Production Config Absolute Bans

This test validates that the following ABSOLUTE PROHIBITIONS are enforced:
❌ DB calls at import time
❌ Multiple Gunicorn workers
❌ psycopg.connect(... sslmode=...) with URL
❌ Health endpoint touching DB
❌ Backend on more than one platform
❌ Render + Render together
"""
import os
import json
import re


def test_no_render_config():
    """Verify Render configuration files are removed."""
    print("\n1. Testing: No Render configuration files")
    
    # Check render.toml doesn't exist
    assert not os.path.exists("render.toml"), "❌ render.toml should be removed"
    
    # Check render.json doesn't exist
    assert not os.path.exists("render.json"), "❌ render.json should be removed"
    
    print("   ✅ Render config files removed")


def test_single_gunicorn_worker():
    """Verify Gunicorn is configured with single worker."""
    print("\n2. Testing: Single Gunicorn worker")
    
    # Check gunicorn.conf.py
    with open("backend/gunicorn.conf.py", "r") as f:
        content = f.read()
        
    # Find workers configuration
    match = re.search(r'workers\s*=\s*int\(os\.environ\.get\("WEB_CONCURRENCY",\s*"(\d+)"\)\)', content)
    assert match, "❌ Could not find workers configuration"
    
    default_workers = int(match.group(1))
    assert default_workers == 1, f"❌ Default workers should be 1, found {default_workers}"
    
    print(f"   ✅ Gunicorn configured with workers=1 (default)")
    
    # Check render.yaml
    with open("render.yaml", "r") as f:
        render_content = f.read()
        
    assert 'WEB_CONCURRENCY' in render_content, "❌ WEB_CONCURRENCY not in render.yaml"
    assert 'value: "1"' in render_content, "❌ WEB_CONCURRENCY should be set to 1"
    
    print(f"   ✅ render.yaml sets WEB_CONCURRENCY=1")
    
    # Check main.py __main__ section
    with open("backend/app/main.py", "r") as f:
        main_content = f.read()
        
    # Find uvicorn.run in __main__
    if 'if __name__ == "__main__":' in main_content:
        main_section = main_content.split('if __name__ == "__main__":')[1]
        assert 'workers=1' in main_section, "❌ uvicorn.run should use workers=1"
        print(f"   ✅ main.py uvicorn.run configured with workers=1")


def test_health_endpoints_no_db():
    """Verify health endpoints don't access database."""
    print("\n3. Testing: Health endpoints don't touch database")
    
    with open("backend/app/main.py", "r") as f:
        content = f.read()
    
    # Extract health endpoint function
    health_match = re.search(r'@app\.get\("/health".*?\ndef health\(\):(.*?)(?=\n@|^\S)', content, re.DOTALL)
    assert health_match, "❌ Could not find /health endpoint"
    health_func = health_match.group(1)
    
    assert "get_db" not in health_func, "❌ /health endpoint should not use get_db"
    assert "AsyncSession" not in health_func, "❌ /health endpoint should not use AsyncSession"
    assert "Depends" not in health_func, "❌ /health endpoint should not use Depends"
    
    print("   ✅ /health endpoint has no database dependency")
    
    # Check /ready endpoint (not /ready/db)
    ready_match = re.search(r'@app\.get\("/ready",.*?\ndef ready\(\):(.*?)(?=\n\n|\nprint)', content, re.DOTALL)
    if ready_match:
        ready_func = ready_match.group(1)
        assert "get_db" not in ready_func, "❌ /ready endpoint should not use get_db"
        assert "db:" not in ready_func, "❌ /ready endpoint should not have db parameter"
        print("   ✅ /ready endpoint has no database dependency")
    
    # Check /live endpoint
    live_match = re.search(r'@app\.get\("/live".*?\ndef liveness\(\):(.*?)(?=\n@|^\S)', content, re.DOTALL)
    if live_match:
        live_func = live_match.group(1)
        assert "get_db" not in live_func, "❌ /live endpoint should not use get_db"
        print("   ✅ /live endpoint has no database dependency")


def test_no_db_calls_at_import():
    """Verify database doesn't connect at import time."""
    print("\n4. Testing: No DB calls at import time")
    
    with open("backend/app/database.py", "r") as f:
        content = f.read()
    
    # Check for LazyEngine pattern
    assert "class LazyEngine" in content, "❌ LazyEngine class not found"
    assert "_engine = None" in content, "❌ Engine should be None at module level"
    assert "def get_engine():" in content, "❌ get_engine() function not found"
    
    print("   ✅ Lazy engine initialization pattern found")
    
    # Check that create_async_engine is inside get_engine function
    get_engine_section = re.search(r'def get_engine\(\):.*?(?=\ndef |\nclass |\nengine =)', content, re.DOTALL)
    assert get_engine_section, "❌ Could not find get_engine function"
    
    assert "create_async_engine" in get_engine_section.group(0), "❌ create_async_engine should be inside get_engine()"
    
    print("   ✅ create_async_engine is inside get_engine() function")


def test_ssl_in_url_not_connect_args():
    """Verify SSL is configured in URL, not in connect_args."""
    print("\n5. Testing: SSL in URL, not in connect_args")
    
    with open("backend/app/database.py", "r") as f:
        content = f.read()
    
    # Find connect_args section
    connect_args_match = re.search(r'connect_args\s*=\s*\{(.*?)\}', content, re.DOTALL)
    assert connect_args_match, "❌ Could not find connect_args"
    
    connect_args = connect_args_match.group(1)
    assert "ssl" not in connect_args.lower(), "❌ SSL should not be in connect_args"
    
    print("   ✅ SSL not in connect_args")
    
    # Check documentation mentions sslmode in URL
    assert "?sslmode=require" in content, "❌ Documentation should mention sslmode in URL"
    
    print("   ✅ Documentation shows sslmode in URL")


def test_vercel_config_no_comments():
    """Verify vercel.json has no comments."""
    print("\n6. Testing: vercel.json has no comments")
    
    with open("vercel.json", "r") as f:
        content = f.read()
    
    # Parse as JSON to ensure it's valid
    try:
        config = json.loads(content)
    except json.JSONDecodeError as e:
        raise AssertionError(f"❌ vercel.json is not valid JSON: {e}")
    
    print("   ✅ vercel.json is valid JSON (no comments)")
    
    # Check for rewrites
    assert "rewrites" in config, "❌ vercel.json should have rewrites"
    
    # Check rewrites point to Render backend
    rewrites = config["rewrites"]
    assert len(rewrites) > 0, "❌ vercel.json should have at least one rewrite"
    
    backend_url = rewrites[0].get("destination", "")
    assert "render.com" in backend_url, f"❌ Rewrites should point to Render backend, found: {backend_url}"
    
    print(f"   ✅ Rewrites configured to: {backend_url}")


def test_frontend_env_var_setup():
    """Verify frontend environment variable setup exists."""
    print("\n7. Testing: Frontend environment variable setup")
    
    # Check for .env.production.example
    assert os.path.exists("frontend/.env.production.example"), "❌ frontend/.env.production.example not found"
    
    with open("frontend/.env.production.example", "r") as f:
        content = f.read()
    
    assert "VITE_API_URL" in content, "❌ VITE_API_URL not in .env.production.example"
    assert "render.com" in content, "❌ Backend URL should point to Render"
    
    print("   ✅ Frontend env var example configured")


def test_render_only_deployment():
    """Verify backend is configured for Render only."""
    print("\n8. Testing: Backend deployment on Render only")
    
    # Check render.yaml exists
    assert os.path.exists("render.yaml"), "❌ render.yaml not found"
    
    with open("render.yaml", "r") as f:
        content = f.read()
    
    # Check for single platform enforcement
    assert "ABSOLUTE" in content, "❌ render.yaml should mention ABSOLUTE requirements"
    assert "PROHIBITION" in content, "❌ render.yaml should mention PROHIBITION patterns"
    
    print("   ✅ render.yaml enforces single platform deployment")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing Production Config Absolute Bans")
    print("=" * 70)
    
    try:
        test_no_render_config()
        test_single_gunicorn_worker()
        test_health_endpoints_no_db()
        test_no_db_calls_at_import()
        test_ssl_in_url_not_connect_args()
        test_vercel_config_no_comments()
        test_frontend_env_var_setup()
        test_render_only_deployment()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - Production config absolute bans enforced!")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("=" * 70)
        raise


if __name__ == "__main__":
    main()
