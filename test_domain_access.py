"""
Comprehensive Domain Accessibility Test
Tests all domain variations and provides actionable fixes
"""
import requests
import socket
import dns.resolver
from datetime import datetime

def test_dns_resolution(domain):
    """Test if domain resolves to IP"""
    print(f"\n🔍 DNS Resolution for {domain}:")
    try:
        # A record
        try:
            a_records = dns.resolver.resolve(domain, 'A')
            for record in a_records:
                print(f"   ✅ A Record: {record}")
        except:
            print(f"   ❌ No A record found")
        
        # CNAME record
        try:
            cname_records = dns.resolver.resolve(domain, 'CNAME')
            for record in cname_records:
                print(f"   ✅ CNAME: {record}")
        except:
            pass
        
        # IP resolution
        ip = socket.gethostbyname(domain)
        print(f"   ✅ Resolves to IP: {ip}")
        return True
    except Exception as e:
        print(f"   ❌ DNS Error: {str(e)}")
        return False

def test_http_access(url, description):
    """Test HTTP/HTTPS access"""
    print(f"\n🌐 Testing {description}: {url}")
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        print(f"   Content Length: {len(response.content)} bytes")
        
        # Check if it's the expected content
        if 'hiremebahamas' in response.text.lower() or 'hire' in response.text.lower():
            print(f"   ✅ HireBahamas content detected")
            return True
        else:
            print(f"   ⚠️ Content might not be HireBahamas site")
            return False
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL Error: {str(e)[:100]}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection Error: {str(e)[:100]}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def main():
    print("=" * 70)
    print("🌍 HIREMEBAHAMAS.COM DOMAIN ACCESSIBILITY TEST")
    print("=" * 70)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    domains_to_test = [
        ('hiremebahamas.com', 'Root Domain'),
        ('www.hiremebahamas.com', 'WWW Subdomain'),
        ('api.hiremebahamas.com', 'API Subdomain'),
    ]
    
    # Test DNS Resolution
    print("\n" + "=" * 70)
    print("STEP 1: DNS RESOLUTION")
    print("=" * 70)
    
    dns_results = {}
    for domain, desc in domains_to_test:
        dns_results[domain] = test_dns_resolution(domain)
    
    # Test HTTP Access
    print("\n" + "=" * 70)
    print("STEP 2: HTTP/HTTPS ACCESS")
    print("=" * 70)
    
    http_results = {}
    for domain, desc in domains_to_test:
        for protocol in ['https', 'http']:
            url = f"{protocol}://{domain}"
            result = test_http_access(url, f"{desc} ({protocol.upper()})")
            http_results[url] = result
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    all_working = True
    
    print("\n✅ Working:")
    for url, working in http_results.items():
        if working:
            print(f"   {url}")
        else:
            all_working = False
    
    print("\n❌ Not Working:")
    for url, working in http_results.items():
        if not working:
            print(f"   {url}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("🔧 RECOMMENDATIONS")
    print("=" * 70)
    
    if not dns_results.get('hiremebahamas.com'):
        print("""
❌ ROOT DOMAIN NOT RESOLVING
Action Required:
1. Go to your DNS provider (Vercel DNS)
2. Ensure A record exists:
   Type: A
   Name: @ (or blank for root)
   Value: 76.76.21.21 (Vercel's IP)
   TTL: Auto
""")
    
    if not dns_results.get('www.hiremebahamas.com'):
        print("""
❌ WWW SUBDOMAIN NOT RESOLVING
Action Required:
1. Add CNAME record:
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   TTL: Auto
""")
    
    if not dns_results.get('api.hiremebahamas.com'):
        print("""
❌ API SUBDOMAIN NOT RESOLVING
Action Required:
1. Add CNAME record:
   Type: CNAME
   Name: api
   Value: hiremebahamas-backend-production.up.railway.app
   TTL: Auto
""")
    
    if all_working:
        print("""
🎉 ALL DOMAINS WORKING PERFECTLY!

Your site is accessible at:
- https://hiremebahamas.com
- https://www.hiremebahamas.com
- https://api.hiremebahamas.com (backend)

Users can access HireBahamas.com from any browser! ✅
""")
    else:
        print("""
⚠️ SOME ISSUES DETECTED

If DNS records are correct but still not working:
1. Wait 5-10 minutes for DNS propagation
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try incognito/private browsing mode
4. Check Vercel dashboard for deployment status
""")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
