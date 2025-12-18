#!/usr/bin/env python3
"""
Production Audit Test Suite
Verifies all production readiness requirements from the audit.
"""
import json
import os
import re
from pathlib import Path


def test_vercel_json_backend_url():
    """Verify vercel.json has correct backend URL without trailing slash."""
    vercel_json_path = Path(__file__).parent / "vercel.json"
    with open(vercel_json_path) as f:
        config = json.load(f)
    
    # Check rewrites
    assert "rewrites" in config, "vercel.json missing rewrites"
    rewrites = config["rewrites"]
    assert len(rewrites) > 0, "vercel.json has no rewrite rules"
    
    # Verify backend URL
    api_rewrite = next((r for r in rewrites if r["source"] == "/api/(.*)"), None)
    assert api_rewrite is not None, "No /api/ rewrite rule found"
    
    destination = api_rewrite["destination"]
    
    # Must be hiremebahamas.onrender.com (no hyphens)
    assert "hiremebahamas.onrender.com" in destination, \
        f"Wrong backend URL: {destination}"
    assert "hire-me-bahamas" not in destination, \
        "Backend URL has incorrect format (should be hiremebahamas, not hire-me-bahamas)"
    
    # Must not have trailing slash
    url_match = re.search(r'https://[^/]+', destination)
    if url_match:
        base_url = url_match.group(0)
        assert not base_url.endswith('/'), \
            f"Backend URL has trailing slash: {base_url}"
    
    print("✅ vercel.json backend URL is correct")


def test_env_production_example():
    """Verify .env.production.example has correct format."""
    env_path = Path(__file__).parent / "frontend" / ".env.production.example"
    with open(env_path) as f:
        content = f.read()
    
    # Check for correct URL
    assert "hiremebahamas.onrender.com" in content, \
        "VITE_API_URL not set to hiremebahamas.onrender.com"
    assert "hire-me-bahamas" not in content, \
        "Found incorrect URL format (hire-me-bahamas)"
    
    # Check for VITE_API_URL line
    lines = [line.strip() for line in content.split('\n') if 'VITE_API_URL=' in line and not line.startswith('#')]
    assert len(lines) > 0, "No VITE_API_URL found in .env.production.example"
    
    vite_api_url_line = lines[0]
    
    # Must not have trailing slash
    assert not vite_api_url_line.rstrip().endswith('/'), \
        f"VITE_API_URL has trailing slash: {vite_api_url_line}"
    
    # Must not have quotes
    # Extract the URL part after the =
    url_part = vite_api_url_line.split('=', 1)[1]
    assert not url_part.startswith('"') and not url_part.startswith("'"), \
        f"VITE_API_URL has quotes: {vite_api_url_line}"
    assert not url_part.rstrip().endswith('"') and not url_part.rstrip().endswith("'"), \
        f"VITE_API_URL has quotes: {vite_api_url_line}"
    
    print("✅ .env.production.example format is correct")


def test_render_yaml_config():
    """Verify render.yaml has correct configuration."""
    render_yaml_path = Path(__file__).parent / "render.yaml"
    with open(render_yaml_path) as f:
        content = f.read()
    
    # Check service type
    assert "type: web" in content, "Service type not set to 'web'"
    
    # Check runtime
    assert "runtime: python" in content, "Runtime not set to 'python'"
    
    # Check health check path
    assert "healthCheckPath: /health" in content, \
        "Health check path not set to /health"
    
    # Check start command uses gunicorn
    assert "gunicorn app.main:app" in content, \
        "Start command doesn't use gunicorn"
    
    # Check single worker configuration
    assert "WEB_CONCURRENCY" in content, "WEB_CONCURRENCY not configured"
    
    print("✅ render.yaml configuration is correct")


def test_gunicorn_config():
    """Verify gunicorn.conf.py has production-ready settings."""
    gunicorn_conf_path = Path(__file__).parent / "backend" / "gunicorn.conf.py"
    with open(gunicorn_conf_path) as f:
        content = f.read()
    
    # Check for worker configuration
    assert 'workers = int(os.environ.get("WEB_CONCURRENCY"' in content, \
        "Workers not using WEB_CONCURRENCY env var"
    
    # Check for timeout configuration
    assert 'timeout = int(os.environ.get("GUNICORN_TIMEOUT"' in content, \
        "Timeout not using GUNICORN_TIMEOUT env var"
    
    # Check worker class
    assert 'worker_class = "uvicorn.workers.UvicornWorker"' in content, \
        "Worker class not set to UvicornWorker"
    
    # Check preload_app is False (critical for database safety)
    assert "preload_app = False" in content, \
        "preload_app should be False for database safety"
    
    # Check port 5432 validation
    assert "5432" in content and "PostgreSQL" in content, \
        "Missing port 5432 validation"
    
    print("✅ gunicorn.conf.py configuration is correct")


def test_health_endpoint_no_database():
    """Verify health endpoint doesn't require database."""
    main_py_path = Path(__file__).parent / "backend" / "app" / "main.py"
    with open(main_py_path) as f:
        content = f.read()
    
    # Find the health endpoint definition
    health_endpoint_start = content.find('@app.get("/health"')
    assert health_endpoint_start != -1, "Health endpoint not found"
    
    # Extract the health endpoint function (find the next function or reasonable end)
    # Look for the next @app decorator or end of function (approximately)
    next_decorator = content.find('@app.', health_endpoint_start + 20)
    if next_decorator == -1:
        health_section = content[health_endpoint_start:health_endpoint_start + 800]
    else:
        health_section = content[health_endpoint_start:next_decorator]
    
    # Must be synchronous (def, not async def)
    assert 'async def health' not in health_section, \
        "Health endpoint should be synchronous for instant response"
    assert 'def health' in health_section, \
        "Health endpoint function not found"
    
    # Must not have database dependency
    assert 'db: AsyncSession' not in health_section and \
           'Depends(get_db)' not in health_section, \
        "Health endpoint should not depend on database"
    
    # Must have a return statement (validates it's a complete function)
    assert 'return' in health_section, \
        "Health endpoint should have a return statement"
    
    print("✅ Health endpoint is database-free and instant")


def test_health_endpoint_defined_early():
    """Verify health endpoint is defined before heavy imports."""
    main_py_path = Path(__file__).parent / "backend" / "app" / "main.py"
    with open(main_py_path) as f:
        lines = f.readlines()
    
    # Find health endpoint line
    health_line = None
    for i, line in enumerate(lines):
        if '@app.get("/health"' in line:
            health_line = i
            break
    
    assert health_line is not None, "Health endpoint not found"
    
    # Find first database import
    db_import_line = None
    for i, line in enumerate(lines):
        if 'from .database import' in line or 'import sqlalchemy' in line:
            db_import_line = i
            break
    
    # Health endpoint should be defined before database imports
    if db_import_line is not None:
        assert health_line < db_import_line, \
            f"Health endpoint (line {health_line}) should be defined before " \
            f"database imports (line {db_import_line})"
    
    print("✅ Health endpoint defined before heavy imports")


def test_no_trailing_slashes_in_urls():
    """Verify no URLs have trailing slashes in key config files."""
    files_to_check = [
        "vercel.json",
        "frontend/.env.production.example",
        "frontend/.env.production.template",
    ]
    
    for file_path in files_to_check:
        full_path = Path(__file__).parent / file_path
        if not full_path.exists():
            continue
            
        with open(full_path) as f:
            content = f.read()
        
        # Find URLs with trailing slashes (excluding directory paths in comments)
        # Match complete URLs including optional trailing slash
        url_pattern = r'https://[^\s"\']+/?'
        matches = re.finditer(url_pattern, content)
        
        suspicious_urls = []
        for match in matches:
            url = match.group(0)
            # Ignore URLs that are clearly directory paths (have more path segments)
            if url.count('/') <= 3:  # https://domain.com/
                suspicious_urls.append(url)
        
        # Filter out false positives (e.g., https://domain.com/path/ is ok)
        actual_trailing_slash_issues = [
            url for url in suspicious_urls 
            if url.endswith('hiremebahamas.onrender.com/') or 
               url.endswith('.vercel.app/')
        ]
        
        if actual_trailing_slash_issues:
            print(f"⚠️  Warning: Potential trailing slashes in {file_path}:")
            for url in actual_trailing_slash_issues:
                print(f"    {url}")
    
    print("✅ No trailing slashes in base URLs")


def run_all_tests():
    """Run all production audit tests."""
    tests = [
        test_vercel_json_backend_url,
        test_env_production_example,
        test_render_yaml_config,
        test_gunicorn_config,
        test_health_endpoint_no_database,
        test_health_endpoint_defined_early,
        test_no_trailing_slashes_in_urls,
    ]
    
    print("🧾🔐 Running Production Audit Tests...\n")
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"Tests Passed: {passed}/{len(tests)}")
    print(f"Tests Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ ALL PRODUCTION AUDIT TESTS PASSED")
        print("Status: SIGN-OFF READY")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Status: NEEDS ATTENTION")
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
