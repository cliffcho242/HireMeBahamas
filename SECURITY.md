# Security Policy

## Overview

This document outlines security best practices, policies, and guidelines for the HireMeBahamas application. All contributors and deployers must follow these guidelines to ensure the security and integrity of the platform.

## Table of Contents

- [Reporting Security Issues](#reporting-security-issues)
- [Security Best Practices](#security-best-practices)
  - [Database Security](#database-security)
  - [Authentication & Secrets](#authentication--secrets)
  - [Rate Limiting](#rate-limiting)
  - [HTTP Security Headers](#http-security-headers)
  - [Session Management](#session-management)
- [Production Deployment Requirements](#production-deployment-requirements)
- [Security Monitoring](#security-monitoring)
- [Compliance & Standards](#compliance--standards)

## Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:
1. Opening a [GitHub Security Advisory](https://github.com/cliffcho242/HireMeBahamas/security/advisories/new)
2. Emailing the maintainers directly at security@hiremebahamas.com (if configured)

Please include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond to security reports within 48 hours and provide regular updates on the fix progress.

## Security Best Practices

### Database Security

#### SSL/TLS Encryption

**ALL production PostgreSQL connections MUST use SSL/TLS encryption.**

##### PostgreSQL Connection Requirements

1. **Connection String Format**
   ```
   postgresql+asyncpg://user:password@host:5432/database?sslmode=require
   ```
   
2. **Supported SSL Modes** (in order of security)
   - `verify-full` - Most secure: verify certificate and hostname
   - `verify-ca` - Verify server certificate
   - `require` - **MINIMUM for production**: encrypt connection
   - `prefer` - Try SSL, fallback to unencrypted (NOT ALLOWED in production)
   - `disable` - No SSL (NEVER use in production)

3. **Environment Variable Configuration**
   ```bash
   # Production - REQUIRED
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
   
   # Optional: Force TLS 1.3 only (recommended)
   DB_FORCE_TLS_1_3=true
   DB_SSL_MODE=require
   ```

4. **Automatic SSL Enforcement**
   - The application automatically adds `?sslmode=require` if missing
   - See `api/db_url_utils.py` for implementation
   - Production deployments validate SSL is enabled

##### Connection Pool Security

```bash
# Prevent stale connection SSL errors
DB_POOL_RECYCLE=120  # Recycle connections every 2 minutes
DB_POOL_SIZE=2       # Minimum pool size
DB_MAX_OVERFLOW=3    # Burst capacity
```

##### Database Access Control

1. **Never commit database credentials**
   - Use environment variables only
   - No credentials in code or configuration files
   - Database URLs are masked in logs

2. **Principle of Least Privilege**
   - Use separate database users for different environments
   - Grant only necessary permissions
   - Use read-only connections where applicable

3. **Connection Security**
   ```bash
   # Connection timeouts (prevent hung connections)
   DB_CONNECT_TIMEOUT=45       # Initial connection timeout
   DB_COMMAND_TIMEOUT=30       # Query execution timeout
   STATEMENT_TIMEOUT_MS=30000  # Server-side statement timeout
   ```

### Authentication & Secrets

#### Secret Key Management

**CRITICAL**: Never use default or weak secrets in production.

##### Requirements

1. **SECRET_KEY and JWT_SECRET_KEY**
   - MUST be randomly generated
   - MUST be at least 32 characters long
   - MUST be unique per environment
   - MUST NOT be committed to version control

2. **Generating Secure Secrets**
   ```bash
   # Python method (recommended)
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # OpenSSL method
   openssl rand -base64 32
   
   # Node.js method
   node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
   ```

3. **Environment Configuration**
   ```bash
   # REQUIRED in production
   SECRET_KEY=<generate-random-32-char-string>
   JWT_SECRET_KEY=<generate-different-random-32-char-string>
   
   # Token expiration (default: 7 days)
   TOKEN_EXPIRATION_DAYS=7
   ```

4. **Secret Rotation**
   - Rotate secrets at least annually
   - Rotate immediately if compromise suspected
   - Document rotation procedures

##### Forbidden Patterns

The CI/CD pipeline checks for and **REJECTS** these patterns:

```python
# ❌ FORBIDDEN - Will fail CI checks
SECRET_KEY = "your-secret-key-here"
SECRET_KEY = "change-in-production"
SECRET_KEY = "test-secret"
JWT_SECRET_KEY = "dev-secret-key"

# ✅ CORRECT - Environment variable
SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY = config("SECRET_KEY")  # with decouple
```

#### Password Security

1. **Password Hashing**
   - Use bcrypt with configurable rounds (default: 10)
   - Higher rounds = more secure but slower
   ```bash
   # Recommended: 10-12 rounds
   BCRYPT_ROUNDS=10  # ~60ms per operation
   BCRYPT_ROUNDS=12  # ~240ms per operation
   ```

2. **Password Requirements**
   - Minimum 8 characters
   - Recommend password managers
   - No common passwords
   - Implement rate limiting on login/registration

3. **Async Password Hashing**
   ```python
   # Use async versions to prevent blocking
   from app.core.security import get_password_hash_async, verify_password_async
   
   hashed = await get_password_hash_async(password)
   is_valid = await verify_password_async(password, hashed)
   ```

#### JWT Token Security

1. **Token Configuration**
   ```bash
   # Token expiration (recommended: 7-30 days)
   ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
   ```

2. **Token Validation**
   - Always verify token signature
   - Check expiration
   - Validate user still exists in database
   - Use HTTPS only for token transmission

3. **Token Storage**
   - Client: Store in httpOnly cookies or secure storage
   - Server: Never store raw tokens, only validate on each request

### Rate Limiting

#### Implementation

Rate limiting is implemented to prevent brute force attacks and API abuse.

##### Login Rate Limiting

```python
# Current implementation (in-memory)
MAX_LOGIN_ATTEMPTS = 5  # per IP or email
RATE_LIMIT_WINDOW = 300  # 5 minutes
```

**Configuration:**
```bash
# Optional: Override defaults
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_WINDOW_SECONDS=300
```

##### Best Practices

1. **Multiple Layers**
   - IP-based rate limiting
   - Email-based rate limiting
   - User-based rate limiting

2. **Endpoints to Protect**
   - Login: 5 attempts per 5 minutes
   - Registration: 3 attempts per hour
   - Password reset: 3 attempts per hour
   - API calls: 100 requests per minute (recommended)

3. **Production Recommendations**
   - Use Redis for distributed rate limiting
   - Implement sliding window algorithm
   - Add CAPTCHA after N failed attempts

##### Future Enhancements

For production scale, consider:
- **slowapi** - FastAPI rate limiting library
- **Redis** - Distributed rate limit storage
- **Cloudflare** - CDN-level rate limiting
- **WAF** - Web Application Firewall

Example with slowapi:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/5minutes")
async def login(...):
    ...
```

### HTTP Security Headers

#### Implemented Headers

All production deployments include the following security headers (configured in `vercel.json`):

```javascript
{
  "X-Content-Type-Options": "nosniff",           // Prevent MIME sniffing
  "X-Frame-Options": "DENY",                     // Prevent clickjacking
  "X-XSS-Protection": "1; mode=block",          // XSS protection
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",  // HSTS
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(self), payment=()"
}
```

#### Content Security Policy (CSP)

**Recommended CSP Header** (to be implemented):

```javascript
{
  "Content-Security-Policy": 
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; " +
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
    "font-src 'self' https://fonts.gstatic.com; " +
    "img-src 'self' data: https:; " +
    "connect-src 'self' https://hiremebahamas.onrender.com; " +
    "frame-ancestors 'none'; " +
    "base-uri 'self'; " +
    "form-action 'self'"
}
```

**Implementation Steps:**
1. Add CSP header to `vercel.json`
2. Test in report-only mode first
3. Gradually tighten policies
4. Monitor CSP violation reports

#### CORS Configuration

```python
# Allowed origins (backend/app/core/middleware.py)
ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Development
    "http://127.0.0.1:3000",
    "http://localhost:5173",      # Vite dev server
    "http://127.0.0.1:5173",
    "https://hiremebahamas.com",  # Production
    "https://www.hiremebahamas.com",
    "https://*.vercel.app",       # Vercel preview deployments
]

# CORS settings
CORS_SETTINGS = {
    "allow_origins": ALLOWED_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Request-ID"],
}
```

### Session Management

#### Session Security

1. **Session Configuration**
   ```python
   # Flask session settings (if using Flask)
   SESSION_COOKIE_SECURE = True      # HTTPS only
   SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
   SESSION_COOKIE_SAMESITE = "Lax"   # CSRF protection
   PERMANENT_SESSION_LIFETIME = 7    # Days
   ```

2. **Session Storage**
   - Production: Use Redis for session storage
   - Development: In-memory or database-backed sessions
   - Never store sensitive data in sessions

3. **Session Invalidation**
   - Implement logout functionality
   - Clear sessions on password change
   - Implement session timeout
   - Provide "logout all devices" option

#### Cookie Security

```python
# Secure cookie settings
response.set_cookie(
    key="session_token",
    value=token,
    max_age=604800,          # 7 days in seconds
    secure=True,             # HTTPS only
    httponly=True,           # No JavaScript access
    samesite="Lax",          # CSRF protection
    domain=".hiremebahamas.com"  # Subdomain support
)
```

## Production Deployment Requirements

### Pre-Deployment Checklist

Use the [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) for detailed deployment validation.

#### Critical Requirements

- [ ] **Database SSL/TLS enabled** (`?sslmode=require` in DATABASE_URL)
- [ ] **Unique SECRET_KEY and JWT_SECRET_KEY** (never use defaults)
- [ ] **ENVIRONMENT=production** set
- [ ] **HTTPS enabled** on all domains
- [ ] **Security headers configured** (verify in vercel.json)
- [ ] **Rate limiting enabled** (check login endpoint)
- [ ] **Error messages sanitized** (no stack traces or sensitive data)
- [ ] **Logging configured** (no sensitive data in logs)
- [ ] **Dependency vulnerabilities scanned** (Frogbot/dependabot)
- [ ] **Code security scanned** (CodeQL/SonarCloud)

#### Environment Variables

**Required for all production deployments:**

```bash
# Database (with SSL)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require

# Secrets (MUST be unique, randomly generated)
SECRET_KEY=<generated-random-secret>
JWT_SECRET_KEY=<generated-random-secret>

# Environment
ENVIRONMENT=production

# Frontend URL
FRONTEND_URL=https://hiremebahamas.com

# Optional but recommended
DB_POOL_RECYCLE=120
DB_FORCE_TLS_1_3=true
BCRYPT_ROUNDS=10
```

### Platform-Specific Guidelines

#### Vercel Deployment

1. Add environment variables in Vercel Dashboard
2. Verify security headers in vercel.json
3. Enable Edge Middleware (if needed)
4. Configure cron jobs for health checks

#### Railway Deployment

1. Use DATABASE_PRIVATE_URL for zero egress fees
2. Configure health checks
3. Set up monitoring alerts
4. Enable auto-deployments from main branch

## Security Monitoring

### Logging Best Practices

1. **What to Log**
   - Authentication events (login, logout, failed attempts)
   - Authorization failures
   - API errors and exceptions
   - Database connection issues
   - Rate limit violations

2. **What NOT to Log**
   - Passwords or password hashes
   - Full JWT tokens
   - Credit card or payment information
   - Personally Identifiable Information (PII)
   - Database connection strings with passwords

3. **Log Sanitization**
   ```python
   # Mask sensitive data
   logger.info(f"Database URL: {mask_database_url(DATABASE_URL)}")
   logger.info(f"Login attempt for user: {email}")  # OK
   logger.info(f"Password: {password}")  # ❌ NEVER DO THIS
   ```

### Monitoring Endpoints

The application provides several health and monitoring endpoints:

```
GET /health              - Quick health check (no DB access)
GET /health/ping         - Ultra-fast ping (returns "pong")
GET /api/health          - Detailed health with database status
GET /metrics             - Prometheus metrics (text format)
GET /api/database/ping   - Database keepalive ping
```

### Recommended Monitoring

1. **Application Performance**
   - Response times
   - Error rates
   - Database query performance
   - Connection pool status

2. **Security Events**
   - Failed login attempts
   - Rate limit violations
   - Unusual API access patterns
   - Database connection failures

3. **Infrastructure**
   - CPU and memory usage
   - Disk space
   - Network connectivity
   - SSL certificate expiration

### Alert Configuration

**Critical Alerts** (immediate notification):
- Database connection failures
- High error rate (>5%)
- SSL certificate expiring soon (<7 days)
- Unusual spike in failed logins

**Warning Alerts** (review within 24h):
- Slow query performance (>5s)
- High memory usage (>80%)
- Rate limit frequently triggered
- Dependency vulnerabilities found

## Compliance & Standards

### OWASP Top 10 Coverage

This application addresses the [OWASP Top 10 2021](https://owasp.org/Top10/) vulnerabilities:

- **A01 Broken Access Control**: JWT authentication, role-based access
- **A02 Cryptographic Failures**: SSL/TLS, bcrypt password hashing, secure tokens
- **A03 Injection**: Parameterized queries, input validation
- **A04 Insecure Design**: Security architecture, threat modeling
- **A05 Security Misconfiguration**: Secure defaults, automated scanning
- **A06 Vulnerable Components**: Dependency scanning (Frogbot, Dependabot)
- **A07 Authentication Failures**: Bcrypt, JWT, rate limiting, MFA ready
- **A08 Software Integrity Failures**: CI/CD validation, signed commits
- **A09 Logging Failures**: Structured logging, no sensitive data
- **A10 Server-Side Request Forgery**: Input validation, URL allowlisting

### Security Standards

1. **Password Storage**
   - Follows [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
   - Bcrypt with 10+ rounds
   - No password reuse allowed

2. **Authentication**
   - Follows [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
   - JWT tokens with expiration
   - Secure session management

3. **API Security**
   - Follows [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
   - Rate limiting
   - Input validation
   - Proper error handling

### Compliance Requirements

For organizations requiring compliance:

- **GDPR**: Implement data deletion, export, consent management
- **HIPAA**: Add audit logging, encryption at rest, BAA agreements
- **SOC 2**: Implement access controls, monitoring, incident response
- **PCI DSS**: If handling payments, use certified payment processor

## Security Maintenance

### Regular Tasks

#### Daily
- [ ] Monitor error logs
- [ ] Review failed authentication attempts
- [ ] Check application health endpoints

#### Weekly
- [ ] Review dependency alerts (Dependabot, Frogbot)
- [ ] Check for security advisories
- [ ] Review access logs for anomalies

#### Monthly
- [ ] Update dependencies with security patches
- [ ] Review and update secrets/tokens
- [ ] Conduct security scan (CodeQL, SonarCloud)
- [ ] Review rate limiting effectiveness

#### Quarterly
- [ ] Security audit of code changes
- [ ] Penetration testing (if applicable)
- [ ] Review and update security policies
- [ ] Team security training

### Incident Response

1. **Detection**
   - Monitor alerts and logs
   - User reports
   - Security scanner findings

2. **Assessment**
   - Determine severity (Critical/High/Medium/Low)
   - Identify affected systems and data
   - Estimate impact and scope

3. **Containment**
   - Isolate affected systems
   - Revoke compromised credentials
   - Enable additional logging
   - Block malicious IPs

4. **Eradication**
   - Remove threat/malware
   - Patch vulnerabilities
   - Update security controls

5. **Recovery**
   - Restore from clean backups
   - Verify system integrity
   - Resume normal operations
   - Monitor for recurrence

6. **Post-Incident**
   - Document incident details
   - Update procedures and documentation
   - Implement preventive measures
   - Conduct team retrospective

## Security Resources

### Documentation
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Deployment security checklist
- [.env.example](.env.example) - Environment variable reference
- [SECURITY_SUMMARY_VERCEL_POSTGRES.md](SECURITY_SUMMARY_VERCEL_POSTGRES.md) - Database security
- [SECURITY_SUMMARY_POSTGRESQL_SHUTDOWN.md](SECURITY_SUMMARY_POSTGRESQL_SHUTDOWN.md) - Graceful shutdown

### External Resources
- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

### Tools
- **CodeQL**: Automated security scanning (enabled in CI)
- **Frogbot**: Dependency vulnerability scanning
- **SonarCloud**: Code quality and security analysis
- **Dependabot**: Automated dependency updates

## Support

For security questions or concerns:
- Open a [GitHub Security Advisory](https://github.com/cliffcho242/HireMeBahamas/security/advisories/new)
- Email: security@hiremebahamas.com (if configured)
- Review existing [Security Summaries](.)

---

**Last Updated**: December 2025  
**Version**: 1.0.0  
**Next Review**: March 2026
