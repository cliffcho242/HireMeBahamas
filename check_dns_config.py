"""
Automated DNS Configuration Checker and Helper
Checks if hiremebahamas.com is properly configured for Vercel
"""

import subprocess
import sys
import time


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_dns(domain):
    """Check DNS resolution for domain"""
    try:
        result = subprocess.run(
            f"nslookup {domain}", shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


def check_vercel_domain():
    """Check Vercel domain configuration"""
    try:
        result = subprocess.run(
            "vercel domains inspect hiremebahamas.com",
            shell=True,
            capture_output=True,
            text=True,
            cwd=r"C:\Users\Dell\OneDrive\Desktop\HireBahamas\frontend",
            timeout=30,
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)


print_header("DNS Configuration Checker for hiremebahamas.com")

print("🔍 Step 1: Checking DNS Resolution...")
print("-" * 70)

# Check main domain
print("\nChecking: hiremebahamas.com")
dns_result = check_dns("hiremebahamas.com")
print(dns_result)

if "76.76.21.21" in dns_result:
    print("✅ CORRECT: Domain points to Vercel (76.76.21.21)")
    dns_ok = True
elif "can't find" in dns_result or "Non-existent" in dns_result:
    print("❌ ERROR: Domain not found (DNS_PROBE_FINISHED_NXDOMAIN)")
    print("   → You need to configure DNS at your registrar")
    dns_ok = False
else:
    print("⚠️  WARNING: Domain points to wrong IP address")
    print("   → Should point to: 76.76.21.21")
    dns_ok = False

# Check www subdomain
print("\n" + "-" * 70)
print("\nChecking: www.hiremebahamas.com")
www_result = check_dns("www.hiremebahamas.com")
print(www_result)

if "cname.vercel-dns.com" in www_result or "76.76.21.21" in www_result:
    print("✅ CORRECT: WWW subdomain configured")
    www_ok = True
else:
    print("⚠️  WARNING: WWW subdomain not configured properly")
    www_ok = False

# Check Vercel configuration
print("\n" + "=" * 70)
print("🔍 Step 2: Checking Vercel Domain Configuration...")
print("-" * 70)

success, vercel_output = check_vercel_domain()
if success and "76.76.21.21" in vercel_output:
    print("✅ Vercel project is configured")
    if "not configured properly" in vercel_output.lower():
        print("⚠️  But DNS records are not pointing correctly")
else:
    print("❌ Could not verify Vercel configuration")

print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

status = []
if dns_ok:
    status.append("✅ Main domain DNS: WORKING")
else:
    status.append("❌ Main domain DNS: NOT CONFIGURED")

if www_ok:
    status.append("✅ WWW subdomain: WORKING")
else:
    status.append("⚠️  WWW subdomain: NEEDS SETUP")

for s in status:
    print(f"  {s}")

if not dns_ok:
    print("\n" + "=" * 70)
    print("🛠️  WHAT YOU NEED TO DO")
    print("=" * 70)
    print("\nYour domain is NOT pointing to Vercel. Follow these steps:\n")
    print("1. Find where you registered hiremebahamas.com")
    print("   (GoDaddy, Namecheap, Google Domains, etc.)")
    print("")
    print("2. Log in to your registrar's website")
    print("")
    print("3. Go to DNS Settings / Domain Management")
    print("")
    print("4. Add these DNS records:")
    print("")
    print("   A Record:")
    print("   ┌─────────────────────────────────┐")
    print("   │ Type:  A                        │")
    print("   │ Name:  @ (or leave blank)       │")
    print("   │ Value: 76.76.21.21              │")
    print("   │ TTL:   3600 (or Auto)           │")
    print("   └─────────────────────────────────┘")
    print("")
    print("   CNAME Record (for www):")
    print("   ┌─────────────────────────────────┐")
    print("   │ Type:  CNAME                    │")
    print("   │ Name:  www                      │")
    print("   │ Value: cname.vercel-dns.com     │")
    print("   │ TTL:   3600 (or Auto)           │")
    print("   └─────────────────────────────────┘")
    print("")
    print("5. Save changes and wait 5-30 minutes")
    print("")
    print("6. Run this script again to verify: python check_dns_config.py")
    print("")
    print("📖 Full instructions: DOMAIN_SETUP_INSTRUCTIONS.md")
    print("")
    print("🌐 Temporary URL (works now):")
    print("   https://frontend-8hx9eshko-cliffs-projects-a84c76c9.vercel.app")

else:
    print("\n" + "=" * 70)
    print("🎉 SUCCESS!")
    print("=" * 70)
    print("\n✅ Your domain is configured correctly!")
    print("\nYour site should be accessible at:")
    print("  • https://hiremebahamas.com")
    print("  • https://www.hiremebahamas.com")
    print("\nDownload page:")
    print("  • https://hiremebahamas.com/download")
    print("\nTest page:")
    print("  • https://hiremebahamas.com/download-test")
    print("\nNote: SSL certificates may take 5 more minutes to activate.")
    print("      If you see a security warning, wait a few minutes.")

print("\n" + "=" * 70)
print("Need help? Check: DOMAIN_SETUP_INSTRUCTIONS.md")
print("=" * 70 + "\n")
