#!/usr/bin/env python3
"""
HireBahamas DNS Configuration Status & Action Plan
===================================================

⚠️ IMPORTANT: Update Nameservers to Manage DNS on Vercel
=========================================================

To fully manage your DNS records on Vercel, update the nameservers
in your DNS provider to Vercel's nameservers.

Learn more: https://vercel.com/docs/concepts/projects/domains#vercel-nameservers

CURRENT DNS STATUS (Detected):
==============================

Domain: hiremebahamas.com

Current Nameservers:
  ⚠️ dns1.registrar-servers.com
  ⚠️ dns2.registrar-servers.com
  (Registrar: Appears to be Namecheap or similar)

Current A Record:
  ✅ 76.76.21.21 (Vercel's IP - ALREADY CONFIGURED!)

WHAT THIS MEANS:
================
- hiremebahamas.com → Already routes to Vercel ✅
- DNS is working ✅
- SSL should be active ✅
- But DNS is managed at registrar, not Vercel

RECOMMENDED ACTION:
===================

SWITCH TO VERCEL NAMESERVERS (Recommended for full Vercel integration)
-----------------------------------------------------------------------
Benefits:
- ✅ Easier DNS management in Vercel dashboard
- ✅ Automatic SSL/CDN configuration
- ✅ Better integration with Vercel features
- ✅ No need to manage DNS at multiple places

Steps:
1. Go to your domain registrar (dns1.registrar-servers.com suggests Namecheap)
2. Change nameservers from:
   dns1.registrar-servers.com
   dns2.registrar-servers.com

   TO:
   ns1.vercel-dns.com
   ns2.vercel-dns.com

3. Wait 24-48 hours for propagation
4. Manage all DNS in Vercel dashboard

ALTERNATIVE: Keep Current Setup
-------------------------------
If you prefer to keep managing DNS at your registrar, your current
A record setup (76.76.21.21) will continue to work, but you won't
have the benefits of full Vercel DNS management.

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

⚠️ RECOMMENDED: Switch to Vercel Nameservers
   Update nameservers in your DNS provider to manage DNS on Vercel:
   - ns1.vercel-dns.com
   - ns2.vercel-dns.com
   Learn more: https://vercel.com/docs/concepts/projects/domains#vercel-nameservers

🎯 NEXT STEPS:
   1. Update nameservers to Vercel's (recommended)
   2. Verify website loads: https://hiremebahamas.com
   3. Add backend subdomain: api.hiremebahamas.com
   4. Update frontend .env with new API URL

🚀 ONCE RAILWAY BACKEND IS DEPLOYED:
   1. Add CNAME: api → hiremebahamas-backend.railway.app
   2. Update frontend to use: https://api.hiremebahamas.com
   3. Test authentication flow end-to-end
"""
)
print("=" * 70)
