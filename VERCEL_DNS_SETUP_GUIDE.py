#!/usr/bin/env python3
"""
Vercel DNS Configuration Guide for HireBahamas
================================================

⚠️ IMPORTANT: Update Nameservers to Manage DNS on Vercel
=========================================================

To manage your DNS records on Vercel, you need to update the nameservers
in your DNS provider. This is the RECOMMENDED approach for the best
integration with Vercel's features.

Learn more: https://vercel.com/docs/concepts/projects/domains#vercel-nameservers

NAMESERVERS TO USE:
-------------------
Update your domain registrar's nameservers to Vercel's:

Primary Nameservers:
  ns1.vercel-dns.com
  ns2.vercel-dns.com

STEP-BY-STEP INSTRUCTIONS:
==========================

1. LOG INTO YOUR DOMAIN REGISTRAR
   ------------------------------
   Go to where you purchased your domain (GoDaddy, Namecheap, Google Domains, etc.)

2. FIND NAMESERVER SETTINGS
   -------------------------
   Navigate to:
   → Domain Management / DNS Settings
   → Find "Nameservers" or "Custom Nameservers"

3. UPDATE NAMESERVERS TO VERCEL
   ----------------------------
   Change from your registrar's default to:
      ns1.vercel-dns.com
      ns2.vercel-dns.com
   → Save changes

4. VERIFY IN VERCEL
   ----------------
   Go to: https://vercel.com/dashboard
   → Select your project: hiremebahamas
   → Go to Settings → Domains
   → Click on your domain: hiremebahamas.com
   → Verify nameservers are detected

5. PROPAGATION TIME
   ----------------
   DNS changes take time to propagate:
   - Minimum: 1-2 hours
   - Typical: 4-24 hours
   - Maximum: 48 hours

   During this time, some users may see old site, some new site.

6. VERIFY DNS PROPAGATION
   -----------------------
   Use these commands to check:

   PowerShell:
   nslookup hiremebahamas.com

   Check multiple DNS servers:
   nslookup hiremebahamas.com 8.8.8.8  # Google DNS
   nslookup hiremebahamas.com 1.1.1.1  # Cloudflare DNS

7. CONFIGURE VERCEL DNS RECORDS
   -----------------------------
   After nameservers are updated, add DNS records in Vercel:

   A) Frontend (Vercel automatically adds):
      Type: A / CNAME
      Name: @ (root) and www
      Value: Vercel's servers (automatic)

   B) Backend (Railway) - Add manually:
      Type: CNAME
      Name: api (or backend)
      Value: hiremebahamas-backend.railway.app

   This allows: https://api.hiremebahamas.com → Railway backend

COMMON ISSUES:
==============

Issue 1: "Domain not verified"
→ Wait for DNS propagation (up to 48 hours)
→ Check nameservers are correct: nslookup -type=ns hiremebahamas.com

Issue 2: "SSL/HTTPS not working"
→ Vercel auto-generates SSL after DNS propagates
→ Usually takes 1-2 hours after nameservers update

Issue 3: "Old site still showing"
→ DNS cache issue
→ Clear browser cache
→ Try incognito/private browsing
→ Wait for global DNS propagation

ALTERNATIVE: CNAME SETUP (If nameservers won't work)
====================================================

If you can't change nameservers, use CNAME instead:

1. Keep registrar's nameservers
2. In registrar's DNS management, add:

   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com

   Type: A (or ALIAS)
   Name: @
   Value: 76.76.21.21  # Vercel's A record

3. In Vercel, the domain will work without nameserver change

RECOMMENDED DNS SETUP:
======================

After nameservers are configured, your DNS should look like:

hiremebahamas.com          → A record → Vercel frontend
www.hiremebahamas.com      → CNAME   → Vercel frontend
api.hiremebahamas.com      → CNAME   → Railway backend

TESTING AFTER SETUP:
====================

Test each subdomain:

PowerShell:
curl https://hiremebahamas.com
curl https://www.hiremebahamas.com
curl https://api.hiremebahamas.com/health

All should return 200 OK with correct content.

NEXT STEPS:
===========

1. Update nameservers at your domain registrar NOW
2. Wait 2-4 hours for propagation
3. Run: nslookup hiremebahamas.com to verify
4. Once propagated, configure DNS records in Vercel dashboard
5. Add CNAME for api.hiremebahamas.com → Railway backend
6. Test all endpoints
7. Update frontend environment variables with new API URL

VERCEL DASHBOARD LINKS:
=======================

Project: https://vercel.com/dashboard/hiremebahamas
Domains: https://vercel.com/dashboard/hiremebahamas/settings/domains
DNS:     Configure after nameservers propagate

"""

print(__doc__)

# Provide verification commands
print("\n" + "=" * 70)
print("🔍 VERIFICATION COMMANDS")
print("=" * 70)
print("\nCheck current nameservers:")
print("  nslookup -type=ns hiremebahamas.com")
print("\nCheck DNS resolution:")
print("  nslookup hiremebahamas.com")
print("\nTest website:")
print("  curl https://hiremebahamas.com")
print("\n" + "=" * 70)
