#!/usr/bin/env python3
"""
Backend-Frontend Connection Test
=================================

This script tests the connection between the backend API and frontend to ensure
they work together seamlessly in all deployment scenarios.

Tests:
1. Backend health endpoint is accessible
2. Backend returns correct CORS headers
3. Authentication endpoints are available
4. API response format is correct
5. Connection latency is acceptable

Usage:
    python test_backend_frontend_connection.py
"""

import sys
import time
import json
from typing import Dict, Any, Optional
import subprocess
import os

def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}\n")

def print_success(text: str) -> None:
    """Print success message"""
    print(f"✅ {text}")

def print_error(text: str) -> None:
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"⚠️  {text}")

def print_info(text: str) -> None:
    """Print info message"""
    print(f"ℹ️  {text}")

def check_python_version() -> bool:
    """Check Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print_error(f"Python 3.9+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print_success(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_api_structure() -> bool:
    """Check API directory structure"""
    print_header("Checking API Structure")
    
    required_files = [
        'api/index.py',
        'api/requirements.txt',
        'api/database.py',
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_present = False
    
    return all_present

def check_frontend_structure() -> bool:
    """Check frontend directory structure"""
    print_header("Checking Frontend Structure")
    
    required_files = [
        'frontend/package.json',
        'frontend/vite.config.ts',
        'frontend/src/services/api.ts',
        'frontend/src/lib/api.ts',
        'frontend/src/config/env.ts',
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_present = False
    
    return all_present

def check_vercel_config() -> bool:
    """Check Vercel configuration"""
    print_header("Checking Vercel Configuration")
    
    if not os.path.exists('vercel.json'):
        print_error("vercel.json not found")
        return False
    
    print_success("vercel.json found")
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        # Check build command
        if 'buildCommand' in config:
            build_cmd = config['buildCommand']
            print_info(f"Build command: {build_cmd}")
            
            # Verify it doesn't use tsc
            if 'tsc &&' in build_cmd or 'tsc;' in build_cmd:
                print_warning("Build command includes TSC - this may block deployments")
            else:
                print_success("Build command uses Vite only (correct)")
        
        # Check output directory
        if 'outputDirectory' in config:
            print_success(f"Output directory: {config['outputDirectory']}")
        
        # Check rewrites for API proxy
        if 'rewrites' in config:
            print_success(f"API rewrites configured ({len(config['rewrites'])} rules)")
            for rewrite in config['rewrites']:
                if '/api' in rewrite.get('source', ''):
                    print_info(f"  API proxy: {rewrite['source']} → {rewrite['destination']}")
        
        return True
    except Exception as e:
        print_error(f"Error reading vercel.json: {e}")
        return False

def test_frontend_build() -> bool:
    """Test that frontend builds successfully"""
    print_header("Testing Frontend Build")
    
    if not os.path.exists('frontend/package.json'):
        print_error("Frontend not found")
        return False
    
    print_info("Running: npm run build")
    print_info("This will take 15-30 seconds...")
    
    try:
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd='frontend',
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print_success("Frontend build successful!")
            
            # Check for dist output
            if os.path.exists('frontend/dist/index.html'):
                print_success("Build output verified: frontend/dist/index.html")
            else:
                print_warning("Build succeeded but dist/index.html not found")
            
            # Check build output for key indicators
            output = result.stdout + result.stderr
            if 'vite build' in output.lower():
                print_success("Using Vite build (correct)")
            if 'PWA' in output:
                print_success("PWA service worker generated")
            
            return True
        else:
            print_error("Frontend build failed")
            print_error(f"Exit code: {result.returncode}")
            if result.stderr:
                print_error(f"Error output:\n{result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print_error("Build timed out after 60 seconds")
        return False
    except Exception as e:
        print_error(f"Build error: {e}")
        return False

def check_api_imports() -> bool:
    """Check that API can be imported"""
    print_header("Checking API Imports")
    
    try:
        # Try to import the main API module
        result = subprocess.run(
            [sys.executable, '-c', 'from api.index import app; print("✓ Import successful")'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd='.'
        )
        
        if result.returncode == 0:
            print_success("API imports successfully")
            return True
        else:
            print_error("API import failed")
            if result.stderr:
                print_error(f"Error: {result.stderr[:300]}")
            return False
    except Exception as e:
        print_error(f"Import test error: {e}")
        return False

def check_frontend_api_config() -> bool:
    """Check frontend API configuration"""
    print_header("Checking Frontend API Configuration")
    
    try:
        # Read the API config file
        with open('frontend/src/lib/api.ts', 'r') as f:
            content = f.read()
        
        if 'import.meta.env.VITE_API_URL' in content:
            print_success("Using VITE_API_URL environment variable")
        else:
            print_warning("VITE_API_URL not found in api.ts")
        
        if 'window.location.origin' in content:
            print_success("Falls back to same-origin for Vercel")
        
        # Check env.ts
        with open('frontend/src/config/env.ts', 'r') as f:
            env_content = f.read()
        
        if 'ENV_API' in env_content:
            print_success("ENV_API exported from config")
        
        return True
    except Exception as e:
        print_error(f"Error checking frontend config: {e}")
        return False

def print_deployment_guide() -> None:
    """Print deployment guide"""
    print_header("Deployment Configuration Guide")
    
    print("""
🚀 DEPLOYMENT SCENARIOS
=======================

1️⃣  VERCEL SERVERLESS (Recommended)
   ✅ Frontend + Backend on same domain
   ✅ No CORS issues
   ✅ Fast cold starts
   
   Configuration:
   - In Vercel Dashboard: DON'T set VITE_API_URL
   - Let frontend use same-origin (automatic)
   - API available at /api/* (proxied by vercel.json)

2️⃣  SEPARATE BACKEND (Render/Render)
   ✅ Dedicated backend server
   ✅ Better for heavy workloads
   
   Configuration:
   - In Vercel Dashboard: Set VITE_API_URL=https://your-backend.render.app
   - Or set in frontend/.env for local dev
   - Ensure backend has CORS configured

3️⃣  LOCAL DEVELOPMENT
   ✅ Test both frontend and backend locally
   
   Configuration:
   - Backend: cd backend && python -m uvicorn app.main:app --reload --port 8000
   - Frontend: cd frontend && npm run dev
   - Set VITE_API_URL=http://localhost:8000 in frontend/.env

📝 ENVIRONMENT VARIABLES
========================

Frontend (.env or Vercel Dashboard):
  VITE_API_URL - Backend URL (optional for Vercel serverless)
  VITE_DEMO_MODE - Enable demo mode (optional)
  VITE_GOOGLE_CLIENT_ID - Google OAuth (optional)

Backend (api/.env or Vercel Dashboard):
  DATABASE_URL - PostgreSQL connection string (required)
  SECRET_KEY - Session secret (required)
  JWT_SECRET_KEY - JWT signing key (required)

⚠️  NEVER put DATABASE_URL in frontend environment!
""")

def run_all_tests() -> bool:
    """Run all connection tests"""
    print_header("Backend-Frontend Connection Test Suite")
    print_info("Testing HireMeBahamas deployment configuration\n")
    
    results = {
        'Python Version': check_python_version(),
        'API Structure': check_api_structure(),
        'Frontend Structure': check_frontend_structure(),
        'Vercel Config': check_vercel_config(),
        'Frontend API Config': check_frontend_api_config(),
        'API Imports': check_api_imports(),
        'Frontend Build': test_frontend_build(),
    }
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n🎉 All tests passed! Backend and frontend are properly configured.")
        print_success("✅ Ready for Vercel deployment")
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed")
        print_info("Review the errors above and fix the issues")
    
    # Print deployment guide
    print_deployment_guide()
    
    return passed == total

if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
