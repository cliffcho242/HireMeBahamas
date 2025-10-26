"""
Automated Namecheap DNS Configuration Helper
This script will guide you through fixing hiremebahamas.com DNS on Namecheap
"""

import webbrowser
import time
import subprocess

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_box(text):
    lines = text.split('\n')
    max_len = max(len(line) for line in lines)
    print("\n┌" + "─" * (max_len + 2) + "┐")
    for line in lines:
        print(f"│ {line.ljust(max_len)} │")
    print("└" + "─" * (max_len + 2) + "┘\n")

print_header("Namecheap DNS Auto-Fix for hiremebahamas.com")

print("🎯 This script will help you configure DNS on Namecheap")
print("   Follow the steps below to fix the DNS_PROBE_FINISHED_NXDOMAIN error\n")

# Step 1: Open Namecheap
print("Step 1: Opening Namecheap Domain Management...")
print("-" * 70)

namecheap_url = "https://ap.www.namecheap.com/Domains/DomainControlPanel/hiremebahamas.com/advancedns"

print(f"✓ Opening: {namecheap_url}")
print("  (If browser doesn't open, copy this URL manually)\n")

try:
    webbrowser.open(namecheap_url)
    print("✓ Browser opened successfully")
except:
    print("⚠ Could not open browser automatically")
    print(f"  Please open this URL manually: {namecheap_url}")

time.sleep(2)

# Step 2: Instructions
print("\n" + "="*70)
print("Step 2: Configure DNS Records on Namecheap")
print("="*70 + "\n")

print("You should now see the Namecheap Advanced DNS page.\n")

print("🔧 ACTIONS TO TAKE:")
print("-" * 70)

print("\n1️⃣  DELETE EXISTING RECORDS (if any)")
print("    ✗ Look for any existing A or CNAME records")
print("    ✗ Click the trash/delete icon next to them")
print("    ✗ Remove parking page or placeholder records\n")

print("2️⃣  ADD NEW A RECORD")
print_box("Click 'ADD NEW RECORD'\n\n" +
          "Type:  A Record\n" +
          "Host:  @\n" +
          "Value: 76.76.21.21\n" +
          "TTL:   Automatic (or 1 min)")

print("3️⃣  ADD NEW CNAME RECORD (for www)")
print_box("Click 'ADD NEW RECORD'\n\n" +
          "Type:  CNAME Record\n" +
          "Host:  www\n" +
          "Value: cname.vercel-dns.com\n" +
          "TTL:   Automatic (or 1 min)")

print("4️⃣  SAVE ALL CHANGES")
print("    ✓ Click the green 'SAVE ALL CHANGES' button at the bottom")
print("    ✓ Wait for confirmation message\n")

print("=" * 70)
print("⏱️  PROPAGATION TIME")
print("=" * 70)
print("\nDNS changes typically take:")
print("  • 5-10 minutes (fast)")
print("  • Up to 30 minutes (normal)")
print("  • Up to 48 hours (maximum, rare)\n")

print("Namecheap usually propagates within 10-15 minutes.\n")

# Step 3: Verification
print("=" * 70)
print("Step 3: Verify Configuration")
print("=" * 70 + "\n")

print("After saving changes on Namecheap:\n")

print("1. Wait 5 minutes")
print("2. Run verification: python check_dns_config.py")
print("3. Or manually check: nslookup hiremebahamas.com")
print("4. Expected result: Should show IP 76.76.21.21\n")

# Step 4: Testing
print("=" * 70)
print("Step 4: Test Your Website")
print("=" * 70 + "\n")

print("Once DNS propagates (5-30 minutes), visit:\n")
print("  ✓ https://hiremebahamas.com")
print("  ✓ https://www.hiremebahamas.com")
print("  ✓ https://hiremebahamas.com/download\n")

print("If you see a security warning about SSL:")
print("  → Wait 5 more minutes for SSL certificate generation")
print("  → Vercel automatically provisions SSL after DNS is configured\n")

# Temporary URL
print("=" * 70)
print("🌐 TEMPORARY URL (Works Right Now)")
print("=" * 70 + "\n")

temp_url = "https://frontend-8hx9eshko-cliffs-projects-a84c76c9.vercel.app"
print(f"While waiting for DNS, use: {temp_url}\n")

print("Opening temporary URL in browser...")
try:
    webbrowser.open(temp_url)
    print("✓ Opened temporary URL")
except:
    print("⚠ Could not open browser")
    print(f"  Please open manually: {temp_url}")

# Troubleshooting
print("\n" + "=" * 70)
print("🆘 TROUBLESHOOTING")
print("=" * 70 + "\n")

print("❌ Can't log in to Namecheap?")
print("   → Go to https://www.namecheap.com/myaccount/login/")
print("   → Use your Namecheap account credentials\n")

print("❌ Don't see 'Advanced DNS' tab?")
print("   → Click on 'Domain List' first")
print("   → Click 'MANAGE' next to hiremebahamas.com")
print("   → Then click 'Advanced DNS' tab\n")

print("❌ Getting errors when saving?")
print("   → Make sure Host is '@' not 'hiremebahamas.com'")
print("   → Make sure Value for A record is: 76.76.21.21")
print("   → Make sure Value for CNAME is: cname.vercel-dns.com\n")

print("❌ Still showing old site after 30 minutes?")
print("   → Clear browser cache: Ctrl + Shift + Delete")
print("   → Try incognito mode: Ctrl + Shift + N")
print("   → Try different device/network\n")

print("❌ DNS not propagating?")
print("   → Check online: https://dnschecker.org/#A/hiremebahamas.com")
print("   → Some locations update faster than others\n")

# Summary
print("=" * 70)
print("📋 QUICK SUMMARY")
print("=" * 70 + "\n")

print("✅ What you need to do on Namecheap:")
print("   1. Go to Advanced DNS")
print("   2. Delete existing records")
print("   3. Add A record: @ → 76.76.21.21")
print("   4. Add CNAME: www → cname.vercel-dns.com")
print("   5. Save all changes")
print("   6. Wait 10-15 minutes")
print("   7. Test: https://hiremebahamas.com\n")

print("=" * 70)
print("Need more help? Check DOMAIN_SETUP_INSTRUCTIONS.md")
print("=" * 70 + "\n")

input("Press Enter to finish...")
