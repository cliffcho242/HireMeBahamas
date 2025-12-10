# Security Deployment Checklist

Use this checklist for all production deployments and security reviews of the HireMeBahamas application.

## Quick Reference

- 🔴 **Critical** - Must be completed before production deployment
- 🟡 **Important** - Should be completed for production (can be addressed post-launch)
- 🟢 **Recommended** - Best practices for enhanced security

---

## Pre-Deployment Security Checklist

### 1. Database Security 🔴

#### PostgreSQL SSL/TLS Configuration

- [ ] **🔴 DATABASE_URL includes `?sslmode=require`**
  ```bash
  # Verify format:
  postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
  ```
  
- [ ] **🔴 SSL mode is NOT set to `disable` or `prefer`**
  
- [ ] **🟡 TLS 1.3 enforcement enabled**
  ```bash
  DB_FORCE_TLS_1_3=true
  ```

- [ ] **🟡 Connection pool configured for security**
  ```bash
  DB_POOL_RECYCLE=120  # Prevent stale SSL connections
  DB_POOL_SIZE=2       # Appropriate for workload
  ```

- [ ] **🟢 Statement timeout configured**
  ```bash
  STATEMENT_TIMEOUT_MS=30000  # 30 seconds
  ```

#### Database Access Control

- [ ] **🔴 No database credentials in source code**
  ```bash
  grep -r "postgresql://.*:.*@" --include="*.py" --include="*.js" \
    --exclude-dir=docs --exclude='*.example' --exclude='*.md'
  # Should return no hardcoded credentials
  ```

- [ ] **🔴 Database password is strong** (12+ characters, mixed case, numbers, symbols)

- [ ] **🟡 Database user has minimum required privileges**

- [ ] **🟢 Separate database users for dev/staging/prod**

#### Database Connection Validation

```bash
# Test SSL connection locally:
python3 << 'EOF'
import asyncio
from backend.app.database import test_db_connection
result = asyncio.run(test_db_connection())
print('✅ Connected!' if result[0] else f'❌ Failed: {result[1]}')
EOF
```

---

### 2. Secrets Management 🔴

#### Environment Variables

- [ ] **🔴 SECRET_KEY is set and NOT a default value**
  ```bash
  # Forbidden values:
  # - "your-secret-key-here"
  # - "change-in-production"
  # - "test-secret"
  # - Any value less than 32 characters
  
  echo $SECRET_KEY | wc -c  # Should be 32+
  ```

- [ ] **🔴 JWT_SECRET_KEY is set and NOT a default value**
  ```bash
  echo $JWT_SECRET_KEY | wc -c  # Should be 32+
  ```

- [ ] **🔴 SECRET_KEY and JWT_SECRET_KEY are DIFFERENT**

- [ ] **🔴 Secrets are randomly generated**
  ```bash
  # Generate new secrets:
  python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
  python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
  ```

- [ ] **🟡 Secrets are documented in secure password manager**

- [ ] **🟢 Secret rotation schedule established** (recommend annually)

#### Secrets Validation

Run this validation script:

```bash
# Check for weak secrets in environment
python3 << 'EOF'
import os
import sys

weak_patterns = [
    "your-secret",
    "change-in-production", 
    "test-secret",
    "dev-secret",
    "default",
]

secret_key = os.getenv("SECRET_KEY", "")
jwt_secret = os.getenv("JWT_SECRET_KEY", "")

errors = []

# Check if secrets are set
if not secret_key:
    errors.append("❌ SECRET_KEY not set")
elif len(secret_key) < 32:
    errors.append("❌ SECRET_KEY too short (minimum 32 chars)")
elif any(pattern in secret_key.lower() for pattern in weak_patterns):
    errors.append("❌ SECRET_KEY contains weak pattern")

if not jwt_secret:
    errors.append("❌ JWT_SECRET_KEY not set")
elif len(jwt_secret) < 32:
    errors.append("❌ JWT_SECRET_KEY too short (minimum 32 chars)")
elif any(pattern in jwt_secret.lower() for pattern in weak_patterns):
    errors.append("❌ JWT_SECRET_KEY contains weak pattern")

if secret_key and jwt_secret and secret_key == jwt_secret:
    errors.append("❌ SECRET_KEY and JWT_SECRET_KEY must be different")

if errors:
    print("\n".join(errors))
    sys.exit(1)
else:
    print("✅ All secrets validated")
EOF
```

---

### 3. Authentication & Authorization 🔴

#### Password Security

- [ ] **🔴 Bcrypt is used for password hashing**
  ```bash
  grep -r "bcrypt" backend/app/core/security.py
  ```

- [ ] **🟡 Bcrypt rounds configured appropriately**
  ```bash
  BCRYPT_ROUNDS=10  # Default: 10 (recommended: 10-12)
  ```

- [ ] **🟡 Async password hashing is used**
  ```python
  # Check for async usage:
  grep -r "get_password_hash_async\|verify_password_async" backend/
  ```

#### JWT Configuration

- [ ] **🔴 JWT token expiration is configured**
  ```bash
  TOKEN_EXPIRATION_DAYS=7  # Or ACCESS_TOKEN_EXPIRE_MINUTES
  ```

- [ ] **🔴 JWT algorithm is HS256 or stronger**

- [ ] **🟡 JWT tokens include user ID in 'sub' claim**

- [ ] **🟡 Token validation checks expiration and signature**

#### Session Management

- [ ] **🟡 Sessions expire after inactivity**

- [ ] **🟡 Logout functionality implemented**

- [ ] **🟢 "Logout all devices" option available**

---

### 4. Rate Limiting 🟡

#### Login Protection

- [ ] **🟡 Login rate limiting is enabled**
  ```python
  # Check implementation:
  grep -r "check_rate_limit\|MAX_LOGIN_ATTEMPTS" backend/app/api/auth.py
  ```

- [ ] **🟡 Rate limit is appropriate** (default: 5 attempts per 5 minutes)
  ```bash
  MAX_LOGIN_ATTEMPTS=5
  RATE_LIMIT_WINDOW_SECONDS=300
  ```

- [ ] **🟡 Rate limiting tracks both IP and email**

#### API Protection

- [ ] **🟢 General API rate limiting implemented**
  ```bash
  # Consider implementing with slowapi:
  # pip install slowapi
  ```

- [ ] **🟢 Rate limiting uses distributed storage (Redis)**

- [ ] **🟢 Rate limit violations are logged**

#### Rate Limiting Test

```bash
# Test rate limiting (should fail after max attempts):
for i in {1..6}; do
  curl -X POST https://your-api.com/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' \
    -w "\nAttempt $i: %{http_code}\n"
  sleep 1
done
# Expected: First 5 return 401, 6th returns 429
```

---

### 5. HTTP Security Headers 🔴

#### Required Security Headers

Verify these headers are present in `vercel.json` or server configuration:

- [ ] **🔴 X-Content-Type-Options: nosniff**
  ```bash
  grep -r "X-Content-Type-Options" vercel.json
  ```

- [ ] **🔴 X-Frame-Options: DENY**
  ```bash
  grep -r "X-Frame-Options" vercel.json
  ```

- [ ] **🔴 Strict-Transport-Security** (HSTS)
  ```bash
  grep -r "Strict-Transport-Security" vercel.json
  # Should include: max-age=31536000; includeSubDomains
  ```

- [ ] **🟡 Referrer-Policy: strict-origin-when-cross-origin**

- [ ] **🟡 Permissions-Policy configured**
  ```
  camera=(), microphone=(), geolocation=(self), payment=()
  ```

- [ ] **🟢 Content-Security-Policy (CSP) configured**
  ```bash
  # TODO: Add CSP header to vercel.json
  ```

#### Headers Validation

```bash
# Test deployed headers:
curl -I https://your-domain.com | grep -E "X-Content-Type-Options|X-Frame-Options|Strict-Transport-Security"

# Should output:
# x-content-type-options: nosniff
# x-frame-options: DENY
# strict-transport-security: max-age=31536000; includeSubDomains; preload
```

---

### 6. CORS Configuration 🔴

#### Allowed Origins

- [ ] **🔴 CORS origins are explicitly defined** (not using "*")
  ```python
  # Check backend/app/core/middleware.py
  grep -A 10 "allow_origins" backend/app/core/middleware.py
  ```

- [ ] **🔴 Production domain is in allowed origins**
  ```python
  ALLOWED_ORIGINS = [
      "https://hiremebahamas.com",
      "https://www.hiremebahamas.com",
      # ...
  ]
  ```

- [ ] **🟡 Credentials are only allowed for trusted origins**
  ```python
  allow_credentials=True  # Only with explicit origin list
  ```

- [ ] **🟡 Development origins removed in production**
  ```python
  # Remove in production:
  # "http://localhost:3000"
  # "http://localhost:5173"
  ```

---

### 7. Error Handling & Logging 🔴

#### Error Messages

- [ ] **🔴 Error messages don't expose sensitive information**
  ```python
  # ❌ Bad: return {"error": f"Database error: {str(e)}"}
  # ✅ Good: return {"error": "An error occurred. Please try again."}
  ```

- [ ] **🔴 Stack traces are NOT sent to clients in production**
  ```python
  # Check middleware.py for exception handlers
  grep -A 5 "global_exception_handler" backend/app/core/middleware.py
  ```

- [ ] **🔴 Database errors are sanitized**

- [ ] **🟡 Request IDs included in error responses**
  ```json
  {"error": "...", "request_id": "uuid-here"}
  ```

#### Logging

- [ ] **🔴 Passwords are NEVER logged**
  ```bash
  # Verify no password logging:
  grep -ri "log.*password\|logger.*password" backend/ api/
  # Should return no dangerous patterns
  ```

- [ ] **🔴 Database URLs are masked in logs**
  ```python
  # Check for _mask_database_url usage
  grep -r "_mask_database_url\|mask.*url" backend/app/database.py
  ```

- [ ] **🟡 Failed login attempts are logged**

- [ ] **🟡 Security events are logged** (auth failures, rate limits)

- [ ] **🟢 Logs are centralized** (e.g., CloudWatch, Datadog)

---

### 8. HTTPS & TLS 🔴

#### Domain Configuration

- [ ] **🔴 HTTPS is enabled on production domain**
  ```bash
  curl -I https://hiremebahamas.com
  # Should return 200, not redirect to HTTP
  ```

- [ ] **🔴 HTTP redirects to HTTPS**
  ```bash
  curl -I http://hiremebahamas.com
  # Should return 301/302 redirect to https://
  ```

- [ ] **🟡 SSL certificate is valid**
  ```bash
  openssl s_client -connect hiremebahamas.com:443 -servername hiremebahamas.com < /dev/null 2>/dev/null | openssl x509 -noout -dates
  ```

- [ ] **🟡 Certificate expiration monitoring enabled**

- [ ] **🟢 TLS 1.2+ only** (disable TLS 1.0/1.1)

---

### 9. Dependency Security 🟡

#### Vulnerability Scanning

- [ ] **🟡 Frogbot is enabled** (checks PRs for vulnerabilities)
  ```bash
  # Check .github/workflows/frogbot-pr-scan.yml exists
  ls -la .github/workflows/frogbot-pr-scan.yml
  ```

- [ ] **🟡 Dependabot is enabled**
  ```bash
  # Check .github/dependabot.yml exists
  ls -la .github/dependabot.yml
  ```

- [ ] **🟡 No high/critical vulnerabilities in dependencies**
  ```bash
  # Run dependency check:
  pip install safety
  safety check -r requirements.txt
  
  # Or for npm:
  npm audit
  ```

- [ ] **🟢 Dependencies are up to date**
  ```bash
  pip list --outdated
  npm outdated
  ```

#### Supply Chain Security

- [ ] **🟢 Dependencies are pinned to specific versions**
  ```bash
  # requirements.txt should have exact versions:
  grep -E "==[0-9]" requirements.txt
  ```

- [ ] **🟢 Package integrity verified** (checksums, signatures)

---

### 10. Code Security 🟡

#### Static Analysis

- [ ] **🟡 CodeQL scanning is enabled**
  ```bash
  # Check .github/workflows/codeql.yml exists
  ls -la .github/workflows/codeql.yml
  ```

- [ ] **🟡 No security alerts from CodeQL**
  ```bash
  # Check GitHub Security tab for alerts
  ```

- [ ] **🟢 SonarCloud analysis passing**
  ```bash
  # Check .github/workflows/sonarcloud.yml exists
  ls -la .github/workflows/sonarcloud.yml
  ```

#### Code Review

- [ ] **🟡 All PRs reviewed before merge**

- [ ] **🟡 Security-sensitive changes get extra scrutiny**

- [ ] **🟢 Automated security checks in CI/CD**

---

## Environment-Specific Checklists

### Production Environment

#### Vercel Deployment

- [ ] **Environment variables set in Vercel Dashboard**
  - DATABASE_URL (with sslmode=require)
  - SECRET_KEY (unique, 32+ chars)
  - JWT_SECRET_KEY (unique, 32+ chars)
  - ENVIRONMENT=production
  - FRONTEND_URL=https://hiremebahamas.com

- [ ] **vercel.json security headers configured**

- [ ] **Function timeouts appropriate** (maxDuration: 30)

- [ ] **Domain configured with SSL**

- [ ] **Preview deployments secured** (if needed)

#### Railway Backend Deployment

- [ ] **Environment variables set in Railway Dashboard**
  - DATABASE_PRIVATE_URL (for zero egress) or DATABASE_URL
  - SECRET_KEY (same as Vercel)
  - JWT_SECRET_KEY (same as Vercel)
  - ENVIRONMENT=production
  - DB_POOL_RECYCLE=120
  - DB_FORCE_TLS_1_3=true

- [ ] **Health checks configured**
  ```bash
  # Railway checks /health endpoint every 5 minutes
  ```

- [ ] **Private networking enabled** (if available)

- [ ] **Monitoring and alerts configured**

### Staging Environment

- [ ] **Separate database from production**

- [ ] **Different secrets from production**

- [ ] **ENVIRONMENT=staging**

- [ ] **Limited access (IP whitelist, basic auth)**

### Development Environment

- [ ] **Local .env file NOT committed**
  ```bash
  # Verify .env is in .gitignore
  grep "^\.env$" .gitignore
  ```

- [ ] **Development secrets different from production**

- [ ] **Can use weaker security for convenience** (e.g., BCRYPT_ROUNDS=4)

---

## Post-Deployment Validation

### Immediate Checks (within 1 hour)

- [ ] **Application is accessible** (smoke test)
  ```bash
  curl https://hiremebahamas.com
  ```

- [ ] **Health endpoints return 200**
  ```bash
  curl https://your-api.com/health
  curl https://your-api.com/api/health
  ```

- [ ] **Database connections working**
  ```bash
  # Check application logs for database connection success
  ```

- [ ] **Authentication works** (test login/register)

- [ ] **No errors in production logs**

### Within 24 Hours

- [ ] **Monitor error rates** (should be <1%)

- [ ] **Monitor response times** (p95 should be <2s)

- [ ] **Check SSL certificate**
  ```bash
  curl -I https://hiremebahamas.com | grep -i "strict-transport-security"
  ```

- [ ] **Verify rate limiting works** (test with multiple failed logins)

- [ ] **Check CORS configuration** (test from browser console)

### Within 1 Week

- [ ] **Review all production logs**

- [ ] **No security warnings/alerts**

- [ ] **Performance metrics acceptable**

- [ ] **User feedback positive** (no security concerns)

- [ ] **Monitoring and alerting working**

---

## Security Incident Checklist

If a security incident is detected:

### Immediate Response (within 1 hour)

- [ ] **Assess severity** (Critical/High/Medium/Low)

- [ ] **Notify team** (security contact, on-call engineer)

- [ ] **Contain the threat**
  - [ ] Block malicious IPs
  - [ ] Disable compromised accounts
  - [ ] Revoke leaked credentials
  - [ ] Enable additional logging

### Investigation (within 24 hours)

- [ ] **Identify affected systems and data**

- [ ] **Determine attack vector**

- [ ] **Assess data exposure**

- [ ] **Document timeline of events**

- [ ] **Preserve evidence** (logs, snapshots)

### Remediation (within 48 hours)

- [ ] **Patch vulnerabilities**

- [ ] **Rotate all secrets if compromise suspected**
  ```bash
  # Generate new secrets:
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- [ ] **Update dependencies**

- [ ] **Implement additional controls**

- [ ] **Verify fix deployed**

### Communication

- [ ] **Notify affected users** (if PII exposed)

- [ ] **Create incident report**

- [ ] **Update security documentation**

- [ ] **Conduct team postmortem**

---

## Continuous Security Maintenance

### Daily

- [ ] Monitor error logs
- [ ] Check application health
- [ ] Review failed authentication attempts

### Weekly  

- [ ] Review dependency alerts
- [ ] Check for security advisories
- [ ] Review access logs

### Monthly

- [ ] Update dependencies
- [ ] Run security scans (CodeQL, SonarCloud)
- [ ] Review rate limiting effectiveness
- [ ] Check SSL certificate expiration (90 days notice)

### Quarterly

- [ ] Security audit of new features
- [ ] Review and update secrets
- [ ] Penetration testing (if applicable)
- [ ] Security training for team

### Annually

- [ ] Comprehensive security review
- [ ] Rotate all secrets
- [ ] Update security policies
- [ ] Third-party security audit (recommended)

---

## Checklist Validation Commands

Run all validation checks:

```bash
#!/bin/bash
# save as: scripts/security-validation.sh

echo "=== HireMeBahamas Security Validation ==="
echo ""

# 1. Check for weak secrets in code
echo "1. Checking for weak secrets in code..."
if grep -r "your-secret-key\|change-in-production\|test-secret" \
  --include="*.py" --include="*.js" backend/ api/ > /dev/null; then
  echo "❌ FAIL: Weak secrets found in code"
else
  echo "✅ PASS: No weak secrets in code"
fi

# 2. Check DATABASE_URL has sslmode
echo "2. Checking DATABASE_URL SSL configuration..."
if echo "$DATABASE_URL" | grep -q "sslmode=require"; then
  echo "✅ PASS: DATABASE_URL has sslmode=require"
elif echo "$DATABASE_URL" | grep -q "sslmode="; then
  echo "⚠️  WARN: DATABASE_URL has sslmode but not 'require'"
else
  echo "❌ FAIL: DATABASE_URL missing sslmode parameter"
fi

# 3. Check environment variables are set
echo "3. Checking required environment variables..."
required_vars=("DATABASE_URL" "SECRET_KEY" "JWT_SECRET_KEY" "ENVIRONMENT")
all_set=true
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "❌ FAIL: $var not set"
    all_set=false
  fi
done
if [ "$all_set" = true ]; then
  echo "✅ PASS: All required environment variables set"
fi

# 4. Check security headers in vercel.json
echo "4. Checking security headers in vercel.json..."
required_headers=(
  "X-Content-Type-Options"
  "X-Frame-Options"
  "Strict-Transport-Security"
)
all_headers=true
for header in "${required_headers[@]}"; do
  if ! grep -q "$header" vercel.json 2>/dev/null; then
    echo "❌ FAIL: Missing header: $header"
    all_headers=false
  fi
done
if [ "$all_headers" = true ]; then
  echo "✅ PASS: All required security headers present"
fi

# 5. Check for .env in git
echo "5. Checking .env is not committed..."
if git ls-files | grep -q "^\.env$"; then
  echo "❌ FAIL: .env file is committed to git"
else
  echo "✅ PASS: .env file not in git"
fi

echo ""
echo "=== Validation Complete ==="
```

Make executable and run:
```bash
chmod +x scripts/security-validation.sh
./scripts/security-validation.sh
```

---

## Resources

- [SECURITY.md](SECURITY.md) - Comprehensive security documentation
- [.env.example](.env.example) - Environment variable reference
- [OWASP Top 10](https://owasp.org/Top10/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

**Last Updated**: December 2025  
**Version**: 1.0.0  
**Maintained By**: Security Team
