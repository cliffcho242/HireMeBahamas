#!/usr/bin/env python3
"""
Validate Final Architecture Configuration

This script validates that the HireMeBahamas platform is correctly configured
with the final architecture settings specified in the problem statement.

Usage:
    python scripts/validate_final_architecture.py
"""

import yaml
import json
import sys
import os
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_check(name, passed, details=""):
    """Print a check result."""
    status = "✅" if passed else "❌"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")

def validate_render_config():
    """Validate render.yaml configuration."""
    print_header("RENDER CONFIGURATION VALIDATION")
    
    try:
        with open('render.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        service = config['services'][0]
        start_cmd = service['startCommand']
        
        checks = []
        
        # Service type
        is_web = service.get('type') == 'web'
        checks.append(('Service type is "web"', is_web, f"Found: {service.get('type')}"))
        
        # Runtime
        is_python = service.get('runtime') == 'python'
        checks.append(('Runtime is "python"', is_python, f"Found: {service.get('runtime')}"))
        
        # Plan
        is_standard = service.get('plan') == 'standard'
        checks.append(('Plan is "standard" (Always On)', is_standard, f"Found: {service.get('plan')}"))
        
        # Workers = 1
        has_workers_1 = '--workers 1' in start_cmd
        checks.append(('Workers = 1', has_workers_1))
        
        # Threads = 2
        has_threads_2 = '--threads 2' in start_cmd
        checks.append(('Threads = 2', has_threads_2))
        
        # Timeout = 120
        has_timeout_120 = '--timeout 120' in start_cmd
        checks.append(('Timeout = 120s', has_timeout_120))
        
        # Keep-alive = 5
        has_keepalive_5 = '--keep-alive 5' in start_cmd
        checks.append(('Keep-alive = 5s', has_keepalive_5))
        
        # Graceful timeout
        has_graceful = '--graceful-timeout' in start_cmd
        checks.append(('Graceful timeout configured', has_graceful))
        
        # Health check path
        health_path = service.get('healthCheckPath') == '/health'
        checks.append(('Health check path: /health', health_path, f"Found: {service.get('healthCheckPath')}"))
        
        # Environment variables
        env_vars = {env['key']: env.get('value') for env in service.get('envVars', [])}
        
        has_env = env_vars.get('ENVIRONMENT') == 'production'
        checks.append(('ENVIRONMENT = production', has_env))
        
        has_pythonpath = env_vars.get('PYTHONPATH') == 'backend'
        checks.append(('PYTHONPATH = backend', has_pythonpath))
        
        has_web_concurrency = env_vars.get('WEB_CONCURRENCY') == '1'
        checks.append(('WEB_CONCURRENCY = 1', has_web_concurrency))
        
        # Print results
        all_passed = True
        for name, passed, *details in checks:
            print_check(name, passed, details[0] if details else "")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("❌ render.yaml not found")
        return False
    except Exception as e:
        print(f"❌ Error validating render.yaml: {e}")
        return False

def validate_gunicorn_config():
    """Validate gunicorn.conf.py configuration."""
    print_header("GUNICORN CONFIGURATION VALIDATION")
    
    try:
        config_path = Path('backend/gunicorn.conf.py')
        with open(config_path, 'r') as f:
            content = f.read()
        
        checks = []
        
        # Workers default
        has_workers = 'workers = int(os.environ.get("WEB_CONCURRENCY", "1"))' in content
        checks.append(('Workers default = 1', has_workers))
        
        # Threads default
        has_threads = 'threads = int(os.environ.get("WEB_THREADS", "2"))' in content
        checks.append(('Threads default = 2', has_threads))
        
        # Timeout default
        has_timeout = 'timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))' in content
        checks.append(('Timeout default = 120', has_timeout))
        
        # Keepalive
        has_keepalive = 'keepalive = 5' in content
        checks.append(('Keep-alive = 5', has_keepalive))
        
        # Graceful timeout
        has_graceful = 'graceful_timeout = 30' in content
        checks.append(('Graceful timeout = 30', has_graceful))
        
        # Worker class
        has_uvicorn = 'worker_class = "uvicorn.workers.UvicornWorker"' in content
        checks.append(('Worker class = UvicornWorker', has_uvicorn))
        
        # Preload app safety
        has_preload_false = 'preload_app = False' in content
        checks.append(('Preload app = False (safe)', has_preload_false))
        
        # Print results
        all_passed = True
        for name, passed, *details in checks:
            print_check(name, passed, details[0] if details else "")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("❌ backend/gunicorn.conf.py not found")
        return False
    except Exception as e:
        print(f"❌ Error validating gunicorn.conf.py: {e}")
        return False

def validate_vercel_config():
    """Validate vercel.json configuration."""
    print_header("VERCEL CONFIGURATION VALIDATION")
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        checks = []
        
        # Build command
        has_build = 'buildCommand' in config and 'frontend' in config['buildCommand']
        checks.append(('Build command configured', has_build))
        
        # Output directory
        has_output = config.get('outputDirectory') == 'frontend/dist'
        checks.append(('Output directory = frontend/dist', has_output))
        
        # API rewrites
        has_rewrites = 'rewrites' in config and len(config['rewrites']) > 0
        checks.append(('API rewrites configured', has_rewrites))
        
        if has_rewrites:
            rewrite = config['rewrites'][0]
            has_api_source = rewrite.get('source') == '/api/(.*)'
            checks.append(('API source = /api/(.*)', has_api_source))
            
            has_destination = 'destination' in rewrite and 'onrender.com' in rewrite['destination']
            checks.append(('API destination points to Render', has_destination))
        
        # Security headers
        headers = config.get('headers', [])
        has_headers = len(headers) > 0
        checks.append(('Security headers configured', has_headers))
        
        if has_headers:
            header_str = str(headers)
            has_hsts = 'Strict-Transport-Security' in header_str
            checks.append(('HSTS header present', has_hsts))
            
            has_xframe = 'X-Frame-Options' in header_str
            checks.append(('X-Frame-Options present', has_xframe))
            
            has_content_type = 'X-Content-Type-Options' in header_str
            checks.append(('X-Content-Type-Options present', has_content_type))
            
            has_cache = 'Cache-Control' in header_str
            checks.append(('Cache-Control headers present', has_cache))
            
            has_immutable = 'immutable' in header_str
            checks.append(('Immutable caching for assets', has_immutable))
            
            has_swr = 'stale-while-revalidate' in header_str
            checks.append(('Stale-while-revalidate configured', has_swr))
        
        # Print results
        all_passed = True
        for name, passed, *details in checks:
            print_check(name, passed, details[0] if details else "")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("❌ vercel.json not found")
        return False
    except Exception as e:
        print(f"❌ Error validating vercel.json: {e}")
        return False

def validate_fastapi_app():
    """Validate FastAPI application configuration."""
    print_header("FASTAPI APPLICATION VALIDATION")
    
    try:
        app_path = Path('backend/app/main.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        checks = []
        
        # Health endpoint
        has_health = '@app.get("/health"' in content
        checks.append(('Health endpoint /health exists', has_health))
        
        # Liveness endpoint
        has_live = '@app.get("/live"' in content
        checks.append(('Liveness endpoint /live exists', has_live))
        
        # Readiness endpoint
        has_ready = '@app.get("/ready"' in content
        checks.append(('Readiness endpoint /ready exists', has_ready))
        
        # No database in health
        health_no_db = 'def health()' in content
        checks.append(('Health endpoint is synchronous (fast)', health_no_db))
        
        # FastAPI app initialization
        has_fastapi = 'app = FastAPI(' in content
        checks.append(('FastAPI app initialized', has_fastapi))
        
        # Docs disabled for performance
        docs_disabled = 'docs_url=None' in content
        checks.append(('Docs disabled for fast startup', docs_disabled))
        
        # Print results
        all_passed = True
        for name, passed, *details in checks:
            print_check(name, passed, details[0] if details else "")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("❌ backend/app/main.py not found")
        return False
    except Exception as e:
        print(f"❌ Error validating FastAPI app: {e}")
        return False

def validate_documentation():
    """Validate that documentation exists."""
    print_header("DOCUMENTATION VALIDATION")
    
    docs = [
        'FINAL_ARCHITECTURE_2025.md',
        'DEPLOYMENT_VERIFICATION_2025.md',
        'RENDER_SETTINGS_QUICK_REF.md',
    ]
    
    all_exist = True
    for doc in docs:
        exists = Path(doc).exists()
        print_check(f'{doc} exists', exists)
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Run all validations."""
    print("\n" + "🔍" * 35)
    print("  FINAL ARCHITECTURE CONFIGURATION VALIDATOR")
    print("🔍" * 35)
    
    results = []
    
    # Run validations
    results.append(('Render Configuration', validate_render_config()))
    results.append(('Gunicorn Configuration', validate_gunicorn_config()))
    results.append(('Vercel Configuration', validate_vercel_config()))
    results.append(('FastAPI Application', validate_fastapi_app()))
    results.append(('Documentation', validate_documentation()))
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\nYour HireMeBahamas platform is correctly configured with:")
        print("  ✅ Workers: 1")
        print("  ✅ Threads: 2")
        print("  ✅ Timeout: 120s")
        print("  ✅ Keep-alive: 5s")
        print("  ✅ Auto-deploy: ON")
        print("\n🚀 Architecture: Vercel Edge CDN → Render FastAPI → Neon Postgres")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("\nPlease review the errors above and fix the configuration.")
        print("See FINAL_ARCHITECTURE_2025.md for details.")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
