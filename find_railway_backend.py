"""
Automated Railway Backend URL Discovery and Testing
Finds and tests all possible Railway backend URLs
"""

import requests
import json
from datetime import datetime

# Possible Railway URLs to test
POSSIBLE_URLS = [
    "https://hiremebahamas-backend.railway.app",
    "https://hiremebahamas-backend-production.up.railway.app",
    "https://web-production.up.railway.app",
    "https://api.hiremebahamas.com",
]

def test_url(url):
    """Test a URL to see if it's serving the Flask app"""
    results = {
        "url": url,
        "accessible": False,
        "is_flask_app": False,
        "health_status": None,
        "routes_count": None,
        "error": None
    }
    
    try:
        # Test health endpoint
        print(f"\n🔍 Testing: {url}")
        health_resp = requests.get(
            f"{url}/health", 
            timeout=10,
            headers={"Cache-Control": "no-cache"}
        )
        
        results["accessible"] = True
        results["health_status"] = health_resp.status_code
        
        print(f"   Health Status: {health_resp.status_code}")
        print(f"   Content-Type: {health_resp.headers.get('content-type')}")
        print(f"   Response Length: {len(health_resp.text)} bytes")
        
        # Check if it's JSON (Flask app) or plain text (default page)
        try:
            health_data = health_resp.json()
            results["is_flask_app"] = True
            print(f"   ✅ Flask app detected! Response: {health_data}")
        except:
            print(f"   ⚠️ Plain text response: {health_resp.text[:100]}")
        
        # Test routes endpoint
        try:
            routes_resp = requests.get(f"{url}/api/routes", timeout=10)
            if routes_resp.status_code == 200:
                routes_data = routes_resp.json()
                results["routes_count"] = len(routes_data.get("routes", []))
                print(f"   ✅ Routes endpoint working! {results['routes_count']} routes found")
            else:
                print(f"   Routes Status: {routes_resp.status_code}")
        except Exception as e:
            print(f"   Routes endpoint not accessible: {str(e)[:50]}")
        
        # Test user profile endpoint
        try:
            user_resp = requests.get(f"{url}/api/users/1", timeout=10)
            print(f"   User Profile Status: {user_resp.status_code}")
            if user_resp.status_code == 200:
                user_data = user_resp.json()
                print(f"   ✅ User profile working! User: {user_data.get('email')}")
        except Exception as e:
            print(f"   User profile error: {str(e)[:50]}")
            
    except requests.exceptions.SSLError as e:
        results["error"] = f"SSL Error: {str(e)[:100]}"
        print(f"   ❌ SSL Error: {str(e)[:100]}")
    except requests.exceptions.ConnectionError as e:
        results["error"] = f"Connection Error: {str(e)[:100]}"
        print(f"   ❌ Connection Error: {str(e)[:100]}")
    except requests.exceptions.Timeout:
        results["error"] = "Request timeout"
        print(f"   ❌ Request timeout")
    except Exception as e:
        results["error"] = str(e)[:100]
        print(f"   ❌ Error: {str(e)[:100]}")
    
    return results

def main():
    print("=" * 70)
    print("🔍 RAILWAY BACKEND URL DISCOVERY & TESTING")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    working_url = None
    
    for url in POSSIBLE_URLS:
        result = test_url(url)
        all_results.append(result)
        
        if result["is_flask_app"]:
            working_url = url
            break
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    for result in all_results:
        status = "✅ WORKING" if result["is_flask_app"] else "❌ NOT WORKING"
        print(f"\n{status}: {result['url']}")
        print(f"   Accessible: {result['accessible']}")
        print(f"   Flask App: {result['is_flask_app']}")
        if result['routes_count']:
            print(f"   Routes: {result['routes_count']}")
        if result['error']:
            print(f"   Error: {result['error']}")
    
    print("\n" + "=" * 70)
    if working_url:
        print(f"🎉 SUCCESS! Working backend URL: {working_url}")
        print("=" * 70)
        print("\n📝 Next Steps:")
        print(f"   1. Update frontend/.env.production with: VITE_API_URL={working_url}")
        print("   2. Test user profiles in your frontend")
        print("   3. All API endpoints should now work!")
    else:
        print("⚠️ NO WORKING BACKEND FOUND")
        print("=" * 70)
        print("\n🔧 Troubleshooting Steps:")
        print("   1. Check Railway dashboard for the correct public URL")
        print("   2. Verify the deployment is 'Active' in Railway")
        print("   3. Check Railway logs for errors")
        print("   4. Ensure the service is set to 'public' not 'private'")
        print("   5. Try generating a new domain in Railway settings")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
