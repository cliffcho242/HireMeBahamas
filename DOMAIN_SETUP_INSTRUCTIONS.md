# 🌐 HireMeBahamas Domain Setup Instructions

## ⚠️ ISSUE: DNS_PROBE_FINISHED_NXDOMAIN

**Problem:** Your domain `hiremebahamas.com` is not pointing to Vercel's servers.

**Solution:** Configure DNS records at your domain registrar.

---

## 🎯 QUICK FIX (Recommended - Option A)

Add this **A Record** at your domain registrar:

```
Type: A
Name: @ (or leave blank for root domain)
Value: 76.76.21.21
TTL: 3600 (or Auto)
```

For www subdomain, add:

```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
TTL: 3600 (or Auto)
```

---

## 🚀 SETUP BY REGISTRAR

### If you registered with **GoDaddy**:

1. Go to https://dcc.godaddy.com/manage/hiremebahamas.com/dns
2. Click **"Add"** under DNS Records
3. Add A Record:
   - Type: **A**
   - Name: **@**
   - Value: **76.76.21.21**
   - TTL: **1 Hour** (or default)
4. Add CNAME Record:
   - Type: **CNAME**
   - Name: **www**
   - Value: **cname.vercel-dns.com**
   - TTL: **1 Hour**
5. Click **Save**

### If you registered with **Namecheap**:

1. Go to https://ap.www.namecheap.com/domains/list/
2. Click **"Manage"** next to hiremebahamas.com
3. Go to **"Advanced DNS"** tab
4. Click **"Add New Record"**
5. Add A Record:
   - Type: **A Record**
   - Host: **@**
   - Value: **76.76.21.21**
   - TTL: **Automatic**
6. Add CNAME Record:
   - Type: **CNAME**
   - Host: **www**
   - Value: **cname.vercel-dns.com**
   - TTL: **Automatic**
7. Click **Save**

### If you registered with **Google Domains/Squarespace**:

1. Go to https://domains.google.com/registrar/hiremebahamas.com
2. Click **"DNS"** in left menu
3. Scroll to **"Custom resource records"**
4. Add A Record:
   - Name: **@**
   - Type: **A**
   - TTL: **1h**
   - Data: **76.76.21.21**
5. Add CNAME Record:
   - Name: **www**
   - Type: **CNAME**
   - TTL: **1h**
   - Data: **cname.vercel-dns.com**
6. Click **Add**

### If you registered with **Cloudflare**:

1. Go to https://dash.cloudflare.com/
2. Select **hiremebahamas.com**
3. Go to **DNS** tab
4. Click **"Add record"**
5. Add A Record:
   - Type: **A**
   - Name: **@**
   - IPv4 address: **76.76.21.21**
   - Proxy status: **Proxied** (orange cloud) or **DNS only**
   - TTL: **Auto**
6. Add CNAME Record:
   - Type: **CNAME**
   - Name: **www**
   - Target: **cname.vercel-dns.com**
   - Proxy status: **Proxied** (orange cloud)
   - TTL: **Auto**
7. Click **Save**

---

## 🔄 ALTERNATIVE: Use Vercel Nameservers (Option B)

**Better for performance, automatic SSL, easier management**

Change your domain's nameservers to:

```
ns1.vercel-dns.com
ns2.vercel-dns.com
```

### Steps:

1. Log in to your domain registrar
2. Find **"Nameservers"** or **"DNS Settings"**
3. Select **"Custom Nameservers"**
4. Replace existing nameservers with:
   - `ns1.vercel-dns.com`
   - `ns2.vercel-dns.com`
5. Save changes

⚠️ **Note:** Nameserver changes take 24-48 hours to propagate fully.

---

## ⏱️ HOW LONG DOES IT TAKE?

| Change Type | Time to Propagate |
|------------|-------------------|
| A Record | 5 minutes - 1 hour |
| CNAME Record | 5 minutes - 1 hour |
| Nameservers | 24-48 hours |

---

## 🧪 CHECK IF IT'S WORKING

After making DNS changes, test with these commands:

### Windows PowerShell:
```powershell
nslookup hiremebahamas.com
nslookup www.hiremebahamas.com
```

### Expected Result:
```
Name:    hiremebahamas.com
Address: 76.76.21.21
```

### Online Tools:
- https://dnschecker.org/#A/hiremebahamas.com
- https://www.whatsmydns.net/#A/hiremebahamas.com

---

## ✅ VERIFICATION STEPS

1. **Wait 5-10 minutes** after DNS changes
2. **Clear browser cache**: Ctrl + Shift + Delete
3. **Try in incognito mode**: Ctrl + Shift + N
4. **Visit**: https://hiremebahamas.com
5. **Check SSL**: Look for 🔒 padlock in address bar

---

## 🆘 TROUBLESHOOTING

### "DNS_PROBE_FINISHED_NXDOMAIN" Still Showing?

1. **Wait longer**: DNS can take up to 24 hours
2. **Clear DNS cache**:
   ```powershell
   ipconfig /flushdns
   ```
3. **Try different network**: Mobile data vs WiFi
4. **Use Google DNS**: 8.8.8.8 and 8.8.4.4

### "NET::ERR_CERT_COMMON_NAME_INVALID"?

- SSL certificate is still generating (wait 5 more minutes)
- Try: https://frontend-8hx9eshko-cliffs-projects-a84c76c9.vercel.app

### Can't Find DNS Settings?

Contact your domain registrar's support - they can help you add the A record.

---

## 📝 CURRENT CONFIGURATION

**Domain:** hiremebahamas.com
**Status:** ⚠️ Not configured
**Vercel IP:** 76.76.21.21
**Vercel CNAME:** cname.vercel-dns.com
**Current Nameservers:** None detected
**Intended Nameservers:** ns1.vercel-dns.com, ns2.vercel-dns.com

---

## 🎯 ONCE DNS IS CONFIGURED

Your URLs will be:

- **Main Site:** https://hiremebahamas.com
- **WWW:** https://www.hiremebahamas.com
- **Download Page:** https://hiremebahamas.com/download
- **Test Page:** https://hiremebahamas.com/download-test

---

## 📞 NEED HELP?

1. **Check registrar**: Where did you buy hiremebahamas.com?
2. **Login to registrar**: Go to their DNS/Domain management
3. **Add the A record**: Point @ to 76.76.21.21
4. **Add the CNAME**: Point www to cname.vercel-dns.com
5. **Wait 10 minutes**: Then test

**Temporary URL (works now):**
https://frontend-8hx9eshko-cliffs-projects-a84c76c9.vercel.app

---

**Last Updated:** October 26, 2025
**Vercel Project:** frontend (cliffs-projects-a84c76c9)
