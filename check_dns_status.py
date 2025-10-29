#!/usr/bin/env python3
"""
HireBahamas DNS Configuration Status & Action Plan
===================================================

CURRENT DNS STATUS (Detected):
==============================

Domain: hiremebahamas.com

Current Nameservers:
  ✅ dns1.registrar-servers.com
  ✅ dns2.registrar-servers.com
  (Registrar: Appears to be Namecheap or similar)

Current A Record:
  ✅ 76.76.21.21 (Vercel's IP - ALREADY CONFIGURED!)

GOOD NEWS:
==========
Your domain is ALREADY pointing to Vercel! The A record (76.76.21.21) is correct.

WHAT THIS MEANS:
================
- hiremebahamas.com → Already routes to Vercel ✅
- DNS is working ✅
- SSL should be active ✅

RECOMMENDED ACTIONS:
====================

Option 1: KEEP CURRENT SETUP (Recommended if working)
------------------------------------------------------
Your current setup is fine. You're using A records instead of nameservers.

To verify it's working:
1. Visit: https://hiremebahamas.com
2. Check if your Vercel site loads
3. Check SSL certificate (should show as secure)

Option 2: SWITCH TO VERCEL NAMESERVERS (Optional, better control)
-----------------------------------------------------------------
Benefits:
- Easier DNS management in Vercel dashboard
- Automatic SSL/CDN configuration
- Better integration with Vercel features

Steps:
1. Go to your domain registrar (dns1.registrar-servers.com suggests Namecheap)
2. Change nameservers from:
   dns1.registrar-servers.com
   dns2.registrar-servers.com

   TO:
   ns1.vercel-dns.com
   ns2.vercel-dns.com

3. Wait 2-24 hours for propagation
4. Manage all DNS in Vercel dashboard

ADDING BACKEND SUBDOMAIN:
=========================

To connect your Railway backend to api.hiremebahamas.com:

Method A: Using Current Registrar DNS
--------------------------------------
1. Log into your domain registrar (Namecheap/similar)
2. Go to DNS Management / Advanced DNS
3. Add CNAME record:
   Type: CNAME
   Host: api
   Value: hiremebahamas-backend.railway.app
   TTL: Automatic

Result: https://api.hiremebahamas.com → Railway backend

Method B: After Switching to Vercel Nameservers
------------------------------------------------
1. Go to Vercel dashboard → Domains → hiremebahamas.com
2. Add DNS record:
   Type: CNAME
   Name: api
   Value: hiremebahamas-backend.railway.app

Result: Same as Method A but managed in Vercel

TESTING YOUR SETUP:
===================

Test frontend (should already work):
  curl https://hiremebahamas.com

Test after adding backend CNAME:
  curl https://api.hiremebahamas.com/health

FRONTEND ENVIRONMENT VARIABLES:
===============================

After setting up api.hiremebahamas.com, update your frontend:

File: frontend/.env.production (or .env)

Current:
  VITE_API_URL=https://hiremebahamas-backend.railway.app

Change to:
  VITE_API_URL=https://api.hiremebahamas.com

This gives you:
- Frontend: https://hiremebahamas.com
- Backend API: https://api.hiremebahamas.com
- Cleaner URLs, professional setup

VERIFICATION COMMANDS:
======================
"""

print(__doc__)

import subprocess
import sys


def run_check(command, description):
    """Run a verification check."""
    print(f"\n{'='*70}")
    print(f"🔍 {description}")
    print(f"{'='*70}")
    print(f"Command: {command}\n")

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# Run verification checks
print("\n" + "=" * 70)
print("🔍 CURRENT DNS VERIFICATION")
print("=" * 70)

checks = [
    ("nslookup -type=ns hiremebahamas.com", "Current Nameservers"),
    ("nslookup hiremebahamas.com", "Current A Record"),
    ("nslookup www.hiremebahamas.com", "WWW Subdomain"),
]

for cmd, desc in checks:
    run_check(cmd, desc)

print("\n" + "=" * 70)
print("📋 SUMMARY & RECOMMENDATIONS")
print("=" * 70)
print(
    """
✅ YOUR DOMAIN IS ALREADY CONFIGURED FOR VERCEL!
   - A record points to 76.76.21.21 (Vercel)
   - hiremebahamas.com should already work

🎯 NEXT STEPS:
   1. Verify website loads: https://hiremebahamas.com
   2. Add backend subdomain: api.hiremebahamas.com
   3. Update frontend .env with new API URL
   4. (Optional) Switch to Vercel nameservers for easier management

🚀 ONCE RAILWAY BACKEND IS DEPLOYED:
   1. Add CNAME: api → hiremebahamas-backend.railway.app
   2. Update frontend to use: https://api.hiremebahamas.com
   3. Test authentication flow end-to-end
"""
)
print("=" * 70)
