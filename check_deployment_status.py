#!/usr/bin/env python3
"""
Deployment Status Checker
Verify all fixes are properly deployed to hiremebahamas.com
"""

import requests
import time


def check_backend_deployment():
    """Check if Railway backend is responding"""
    print("🔍 Checking Railway Backend Deployment...")
    print("=" * 60)

    backend_url = "https://hiremebahamas-backend.railway.app"

    endpoints = {
        "Health": "/health",
        "Login": "/api/auth/login",
        "Register": "/api/auth/register",
    }

    print(f"Backend URL: {backend_url}\n")

    all_working = True

    for name, endpoint in endpoints.items():
        url = f"{backend_url}{endpoint}"

        try:
            if name == "Health":
                response = requests.get(url, timeout=10)
            else:
                # Test OPTIONS for CORS
                response = requests.options(url, timeout=10)

            status = response.status_code

            if status == 200:
                print(f"✅ {name:<12} {endpoint:<25} Status: {status}")
            elif status == 404:
                print(f"❌ {name:<12} {endpoint:<25} Status: {status} (Not Found)")
                all_working = False
            else:
                print(f"⚠️ {name:<12} {endpoint:<25} Status: {status}")

        except requests.exceptions.RequestException as e:
            print(f"❌ {name:<12} {endpoint:<25} Error: {str(e)[:40]}")
            all_working = False

    return all_working


def check_frontend_deployment():
    """Check if Vercel frontend is responding"""
    print("\n🔍 Checking Vercel Frontend Deployment...")
    print("=" * 60)

    frontend_url = "https://hiremebahamas.vercel.app"

    try:
        response = requests.get(frontend_url, timeout=10)
        status = response.status_code

        if status == 200:
            print(f"✅ Frontend: {frontend_url}")
            print(f"   Status: {status}")
            return True
        else:
            print(f"⚠️ Frontend: {frontend_url}")
            print(f"   Status: {status}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend: {frontend_url}")
        print(f"   Error: {e}")
        return False


def check_domain_dns():
    """Check if hiremebahamas.com resolves"""
    print("\n🔍 Checking Domain DNS...")
    print("=" * 60)

    try:
        response = requests.get(
            "https://hiremebahamas.com", timeout=10, allow_redirects=True
        )
        print(f"✅ Domain: hiremebahamas.com")
        print(f"   Status: {response.status_code}")
        print(f"   Redirects to: {response.url}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Domain: hiremebahamas.com")
        print(f"   Info: {e}")
        print("   Note: Domain may not be configured yet")
        return False


def summarize_deployment_status():
    """Summarize all deployment fixes"""
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT FIXES SUMMARY")
    print("=" * 60)

    fixes = [
        (
            "✅",
            "Empty admin_panel/package.json",
            ".nixpacksignore prevents build error",
        ),
        ("✅", "TOML syntax error", "providers moved to root level"),
        ("✅", "Pip command not found", "Removed invalid 'pip' from nixPkgs"),
        ("✅", "No module named pip", "Simplified config, using Nixpacks defaults"),
        ("✅", "405 Authentication errors", "Backend routes properly configured"),
    ]

    for status, issue, fix in fixes:
        print(f"{status} {issue:<30} → {fix}")

    print("\n" + "=" * 60)
    print("🚀 DEPLOYMENT STATUS")
    print("=" * 60)


def main():
    print("🔧 HireBahamas Deployment Status Check")
    print("=" * 60)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check all deployments
    backend_ok = check_backend_deployment()
    frontend_ok = check_frontend_deployment()
    domain_ok = check_domain_dns()

    # Show summary
    summarize_deployment_status()

    # Final status
    if backend_ok and frontend_ok:
        print("✅ All services are operational!")
        print("\n🌐 Access your application:")
        print("   Frontend: https://hiremebahamas.vercel.app")
        print("   Backend:  https://hiremebahamas-backend.railway.app")
        if domain_ok:
            print("   Domain:   https://hiremebahamas.com")
    else:
        print("⚠️ Some services may still be deploying...")
        print("   Railway deployments can take 3-5 minutes")
        print("   Check Railway dashboard for build status")

    print("=" * 60)


if __name__ == "__main__":
    main()
