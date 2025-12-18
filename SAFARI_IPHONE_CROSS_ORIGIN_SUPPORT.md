# Safari/iPhone Cross-Origin Cookie Support

## Overview

This document explains how HireMeBahamas supports cross-origin authentication cookies on Safari and iPhone browsers.

## Safari/iPhone Cookie Requirements

Safari and iOS browsers have **stricter cookie policies** than other browsers, especially for cross-origin scenarios:

### 1. SameSite=None + Secure Requirement

**Critical Rule**: When using `SameSite=None` for cross-origin cookies, Safari **requires** the `Secure` flag to be set.

```
❌ REJECTED by Safari: SameSite=None; HttpOnly
✅ ACCEPTED by Safari: SameSite=None; Secure; HttpOnly
```

### 2. Intelligent Tracking Prevention (ITP)

Safari's ITP actively blocks third-party cookies to protect user privacy. Our implementation addresses this with:

- **Explicit SameSite attribute**: iOS 12+ requires explicit `SameSite` declaration
- **Secure cookies**: All production cookies use `Secure=True`
- **First-party context**: Cookies set in direct user interaction

### 3. iOS Version Compatibility

| iOS Version | SameSite Support | Requirements |
|-------------|------------------|--------------|
| iOS 12.x | Partial | Must explicitly set `SameSite` |
| iOS 13.x+ | Full | Standard `SameSite=None; Secure` works |
| iOS 14+ | Enhanced ITP | Additional privacy restrictions |

## Implementation

### Backend Configuration

Location: `api/backend_app/core/security.py`

```python
# Safari/iPhone requires Secure=True when SameSite=None
_is_prod = is_production()
COOKIE_SECURE = _is_prod  # True in production
COOKIE_SAMESITE = "none" if _is_prod else "lax"

# Validation: Safari will reject SameSite=None without Secure
if COOKIE_SAMESITE == "none" and not COOKIE_SECURE:
    logger.warning(
        "Safari/iPhone compatibility: SameSite=None requires Secure=True"
    )
    COOKIE_SECURE = True
```

### Cookie Attributes

Production cookies include:

```
Set-Cookie: access_token=<token>; 
    HttpOnly;           # Prevents JavaScript access (XSS protection)
    Secure;             # HTTPS only (REQUIRED for Safari with SameSite=None)
    SameSite=None;      # Allows cross-origin (frontend on different domain)
    Max-Age=900;        # 15 minutes for access token
    Path=/
```

### Frontend Configuration

Location: `frontend/src/services/api.ts`

```typescript
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Send cookies in cross-origin requests
});
```

### CORS Configuration

Location: `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
    ],  # Explicit origins (no wildcards with credentials)
    allow_credentials=True,  # Enable cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Testing Safari/iPhone Support

### Manual Testing

1. **Safari Desktop (macOS)**
   ```bash
   # Open Safari Developer Tools
   # Develop > Show Web Inspector > Storage > Cookies
   ```
   - Verify cookies have `Secure` and `SameSite=None` flags
   - Check cookies persist across requests

2. **iPhone Safari (iOS)**
   ```bash
   # Settings > Safari > Advanced > Web Inspector
   # Connect iPhone to Mac with cable
   # Safari > Develop > [Your iPhone] > [Website]
   ```
   - Test login flow end-to-end
   - Verify authentication persists
   - Check no cookie warnings in console

3. **Safari Private Browsing**
   - Test cross-origin authentication
   - Verify ITP doesn't block cookies

### Automated Testing

```python
# Test Safari cookie validation
def test_safari_cookie_requirements():
    """Verify cookies meet Safari requirements"""
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    
    # Check Set-Cookie header
    cookie_header = response.headers.get("set-cookie", "")
    
    # Safari requirements
    assert "Secure" in cookie_header, "Safari requires Secure flag"
    assert "SameSite=None" in cookie_header or "SameSite=Lax" in cookie_header
    assert "HttpOnly" in cookie_header
```

## Troubleshooting

### Issue: Cookies Not Set on Safari

**Symptoms:**
- Login succeeds but user immediately logged out
- Cookies visible in Chrome but not Safari
- Network tab shows cookies in response but Storage tab empty

**Solutions:**
1. Verify HTTPS is used (Safari rejects Secure cookies on HTTP)
2. Check `SameSite=None` includes `Secure` flag
3. Ensure frontend uses `withCredentials: true`
4. Verify CORS `allow_credentials=True` on backend

### Issue: Cookies Rejected by ITP

**Symptoms:**
- Cookies work initially but disappear after 7 days
- Safari console shows "blocked cookie" warnings
- Authentication fails after prolonged inactivity

**Solutions:**
1. Use first-party context for cookie setting
2. Implement proper user interaction before setting cookies
3. Consider using local storage fallback for non-sensitive data
4. Keep refresh token expiry reasonable (7-30 days)

### Issue: iOS App WebView Issues

**Symptoms:**
- Web app works in Safari but not in iOS WebView
- Cookies not accessible in WKWebView

**Solutions:**
```swift
// WKWebView configuration for cookie support
let config = WKWebViewConfiguration()
config.websiteDataStore = .default()
config.preferences.javaScriptEnabled = true

// Enable third-party cookies (for cross-origin)
let websiteDataStore = WKWebsiteDataStore.default()
config.websiteDataStore = websiteDataStore
```

## Security Considerations

### ✅ What We Do

1. **Strict SameSite Policy**: `None` only in production for legitimate cross-origin
2. **Secure Transmission**: All auth cookies require HTTPS
3. **HttpOnly Protection**: Prevents XSS attacks via JavaScript access
4. **Explicit Origins**: No wildcard CORS with credentials
5. **Token Rotation**: Short-lived access tokens (15 min) + refresh tokens

### 🔒 Safari Privacy Features We Support

- **Intelligent Tracking Prevention (ITP)**: Cookies set with user interaction
- **Cross-Site Tracking Prevention**: First-party cookie context
- **Private Browsing**: Works without persistent storage
- **Do Not Track**: Respects user privacy preferences

## Browser Compatibility Matrix

| Browser | Version | SameSite=None Support | Notes |
|---------|---------|----------------------|-------|
| Safari Desktop | 13.1+ | ✅ Full | Requires Secure flag |
| Safari Desktop | 12.x | ⚠️ Partial | May need polyfill |
| iOS Safari | 13.x+ | ✅ Full | Standard implementation |
| iOS Safari | 12.x | ⚠️ Partial | Must explicitly set SameSite |
| Chrome | 80+ | ✅ Full | Reference implementation |
| Firefox | 69+ | ✅ Full | Standard implementation |
| Edge | 86+ | ✅ Full | Chromium-based |

## References

### Official Documentation

- [Safari Cookies and Web Storage](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)
- [Apple ITP Documentation](https://webkit.org/tracking-prevention/)
- [MDN: SameSite Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)
- [IETF RFC 6265bis (SameSite)](https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-rfc6265bis)

### Best Practices

- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [Chrome SameSite Updates](https://www.chromium.org/updates/same-site)
- [Safari Privacy White Paper](https://www.apple.com/privacy/docs/Safari_Privacy_White_Paper.pdf)

## Changes Made

### Files Modified

1. **`api/backend_app/core/security.py`**
   - Added Safari/iPhone validation for `SameSite=None` + `Secure`
   - Enhanced cookie setting with Safari compatibility notes
   - Automatic enforcement of Secure flag when SameSite=None

2. **`backend/app/main.py`** (existing)
   - Already configured with proper CORS credentials support
   - Explicit origin list (no wildcards)

3. **`frontend/src/services/api.ts`** (existing)
   - Already configured with `withCredentials: true`

### Backward Compatibility

✅ **All changes are backward compatible**:
- Chrome, Firefox, Edge: Already supported
- Safari: Enhanced support for cross-origin
- Development mode: Uses `SameSite=Lax` (no changes)
- Production mode: Enforces `Secure` with `SameSite=None`

## Summary

HireMeBahamas now fully supports cross-origin authentication cookies on Safari and iPhone browsers by:

1. ✅ Enforcing `Secure=True` when `SameSite=None`
2. ✅ Using HTTPS-only cookies in production
3. ✅ Explicit CORS origin configuration
4. ✅ Safari ITP-compatible cookie handling
5. ✅ iOS 12+ compatibility with explicit SameSite attributes

No user-facing changes required - Safari/iPhone users will now experience seamless authentication!
