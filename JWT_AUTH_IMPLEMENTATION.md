# JWT Authentication Implementation - Production Grade

## Overview

This document describes the production-grade JWT authentication system with refresh token rotation, secure cookies, and comprehensive security features.

## Key Features

### 🔒 Security Features

1. **Short-Lived Access Tokens (15 minutes)**
   - Minimizes exposure window if token is compromised
   - Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` environment variable

2. **Long-Lived Refresh Tokens (7-30 days)**
   - Allows persistent sessions without constant re-authentication
   - Configurable via `REFRESH_TOKEN_EXPIRE_DAYS` environment variable
   - Default: 7 days

3. **Token Rotation Pattern**
   - Each refresh operation invalidates the old refresh token
   - Issues a new refresh token pair
   - Prevents replay attacks

4. **Secure Database Storage**
   - Refresh tokens hashed with SHA-256 before storage
   - Even if database is compromised, tokens cannot be used
   - Includes metadata: IP address, user agent, timestamps

5. **HttpOnly Cookies**
   - `httpOnly=True`: Prevents JavaScript access (XSS protection)
   - `secure=True`: HTTPS-only in production
   - `samesite="none"`: Cross-origin support in production
   - `samesite="lax"`: Development mode default

6. **Flexible Authentication**
   - Supports both cookie-based (browsers) and header-based (API clients)
   - Automatic fallback from cookies to Authorization header

## Architecture

### Database Schema

```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500)
);

-- Indexes for performance
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_revoked ON refresh_tokens(revoked);
```

### Token Flow

#### Registration/Login Flow
```
1. User submits credentials
2. Server validates credentials
3. Server generates:
   - Access token (15 min)
   - Refresh token (7 days)
4. Server stores hashed refresh token in database
5. Server sets secure HttpOnly cookies
6. Server returns tokens in response body (for API clients)
```

#### Token Refresh Flow
```
1. Client sends refresh token (cookie or header)
2. Server validates token:
   - Checks JWT signature
   - Checks expiration
   - Checks database (not revoked)
3. Server revokes old refresh token
4. Server generates new token pair
5. Server stores new refresh token hash
6. Server sets new cookies
7. Server returns new tokens
```

#### Logout Flow
```
1. Client sends refresh token
2. Server revokes token in database
3. Server clears cookies
4. Server returns success
```

## API Endpoints

### POST /api/auth/register
Register a new user and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "user"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": { ... }
}
```

**Cookies Set:**
- `access_token`: HttpOnly, Secure (prod), SameSite=none (prod)
- `refresh_token`: HttpOnly, Secure (prod), SameSite=none (prod)

### POST /api/auth/login
Authenticate and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** Same as registration

### POST /api/auth/refresh
Refresh access token using refresh token.

**Request (Body - Optional):**
```json
{
  "refresh_token": "eyJ..."
}
```

**Request (Cookie - Preferred):**
Token automatically read from `refresh_token` cookie.

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": { ... }
}
```

### POST /api/auth/logout
Logout and revoke refresh token.

**Request (Body - Optional):**
```json
{
  "refresh_token": "eyJ..."
}
```

**Headers (Required):**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

### POST /api/auth/logout-all
Logout from all devices (revoke all tokens).

**Headers (Required):**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Logged out from all devices successfully",
  "tokens_revoked": 3
}
```

## Configuration

### Environment Variables

```bash
# Token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=15    # Default: 15 minutes
REFRESH_TOKEN_EXPIRE_DAYS=7       # Default: 7 days

# Security
SECRET_KEY=your-secret-key-here   # Required: Generate with cryptography
ENVIRONMENT=production            # Enable secure cookies in production

# Database
DATABASE_URL=postgresql://...     # Required for refresh token storage
```

### Cookie Configuration

The system automatically configures cookies based on environment:

**Production (ENVIRONMENT=production):**
- `httpOnly=True` (always)
- `secure=True` (HTTPS only)
- `samesite="none"` (cross-origin)

**Development:**
- `httpOnly=True` (always)
- `secure=False` (allow HTTP)
- `samesite="lax"` (stricter)

## Security Best Practices

### ✅ DO

1. **Use HTTPS in production**
   - Secure cookies only work over HTTPS
   - Set `ENVIRONMENT=production`

2. **Set strong SECRET_KEY**
   ```bash
   # Generate secure key
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Configure CORS properly**
   ```python
   allow_origins=["https://yourdomain.com"]
   allow_credentials=True
   ```

4. **Monitor token usage**
   - Check login attempts
   - Alert on suspicious patterns
   - Review revoked tokens

5. **Cleanup expired tokens**
   ```python
   # Run periodically (cron job)
   await cleanup_expired_tokens(db)
   ```

### ❌ DON'T

1. **Never store tokens in localStorage**
   - Use HttpOnly cookies instead
   - Prevents XSS attacks

2. **Never log tokens**
   - Tokens in logs are security risks
   - Log only token metadata (user_id, exp)

3. **Never share SECRET_KEY**
   - Different key per environment
   - Rotate if compromised

4. **Never disable HttpOnly**
   - Always keep `httpOnly=True`
   - No JavaScript access to tokens

## Testing

### Run Tests

```bash
# Basic tests (no database required)
python backend/test_jwt_refresh_tokens.py

# Full test suite (requires database)
DATABASE_URL=postgresql://... python backend/test_jwt_refresh_tokens.py
```

### Test Coverage

- ✅ Token generation and validation
- ✅ Token hashing (SHA-256)
- ✅ Token storage and retrieval
- ✅ Token rotation pattern
- ✅ Token revocation (single & all)
- ✅ Cookie security configuration
- ✅ Expiration settings

## Migration

### Database Setup

Run the migration script to create the refresh_tokens table:

```bash
python create_refresh_tokens_table.py
```

This creates:
- `refresh_tokens` table
- Required indexes
- Foreign key to users table

### Frontend Integration

#### Browser (Cookie-Based)

Cookies are automatically included in requests. No client code needed.

```typescript
// Login
const response = await fetch('/api/auth/login', {
  method: 'POST',
  credentials: 'include',  // Important: include cookies
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

// Refresh (automatic)
const response = await fetch('/api/auth/refresh', {
  method: 'POST',
  credentials: 'include'  // Cookie sent automatically
});

// Logout
await fetch('/api/auth/logout', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Authorization': `Bearer ${accessToken}` }
});
```

#### API Client (Header-Based)

For non-browser clients (mobile apps, scripts):

```python
import requests

# Login
response = requests.post('https://api.example.com/api/auth/login', json={
    'email': 'user@example.com',
    'password': 'password123'
})
tokens = response.json()
access_token = tokens['access_token']
refresh_token = tokens['refresh_token']

# Use access token
response = requests.get('https://api.example.com/api/profile',
    headers={'Authorization': f'Bearer {access_token}'}
)

# Refresh
response = requests.post('https://api.example.com/api/auth/refresh',
    json={'refresh_token': refresh_token}
)
new_tokens = response.json()
```

## Monitoring

### Key Metrics

1. **Token Usage**
   - Active refresh tokens per user
   - Token refresh rate
   - Token revocation rate

2. **Security Events**
   - Failed token validations
   - Expired token attempts
   - Revoked token usage attempts

3. **Performance**
   - Token generation time
   - Database query time
   - Cookie overhead

### Database Queries

```sql
-- Active tokens per user
SELECT user_id, COUNT(*) 
FROM refresh_tokens 
WHERE revoked = false AND expires_at > NOW()
GROUP BY user_id;

-- Recently revoked tokens
SELECT * FROM refresh_tokens 
WHERE revoked = true 
ORDER BY revoked_at DESC 
LIMIT 100;

-- Expired tokens to clean
SELECT COUNT(*) FROM refresh_tokens 
WHERE expires_at < NOW() - INTERVAL '30 days';
```

## Troubleshooting

### Cookies Not Working

**Issue:** Cookies not being set/sent

**Solutions:**
1. Check CORS configuration includes `allow_credentials=True`
2. Verify frontend uses `credentials: 'include'`
3. Ensure HTTPS in production
4. Check cookie domain matches your domain

### Tokens Expiring Too Fast

**Issue:** Users logged out frequently

**Solutions:**
1. Increase `REFRESH_TOKEN_EXPIRE_DAYS`
2. Implement automatic token refresh in frontend
3. Check server clock synchronization

### Database Growing Too Large

**Issue:** Too many expired tokens

**Solutions:**
1. Run cleanup regularly: `cleanup_expired_tokens(db)`
2. Set up cron job for automatic cleanup
3. Adjust retention periods

## Performance Considerations

### Database Indexes

All critical queries are indexed:
- User ID lookup: `idx_refresh_tokens_user_id`
- Token hash lookup: `idx_refresh_tokens_token_hash`
- Expiration queries: `idx_refresh_tokens_expires_at`
- Revocation status: `idx_refresh_tokens_revoked`

### Optimization Tips

1. **Connection Pooling**
   - Use database connection pool
   - Reuse connections

2. **Caching**
   - Consider Redis for high-traffic sites
   - Cache user data, not tokens

3. **Cleanup Schedule**
   - Run during low-traffic periods
   - Batch delete expired tokens
   - Monitor query performance

## Compliance

### GDPR

- Users can revoke all tokens (logout all devices)
- Tokens include IP and user agent for audit trail
- Automatic cleanup of old tokens

### OWASP

Follows OWASP recommendations:
- Short-lived access tokens
- Secure token storage
- HttpOnly cookies
- Token rotation
- Proper CORS configuration

## Support

For issues or questions:
1. Check troubleshooting section
2. Review security best practices
3. Check test suite for examples
4. Review API documentation

## Change Log

### Version 1.0.0 (2024-12-16)
- Initial implementation
- JWT access tokens (15 min)
- Refresh tokens (7 days)
- Database storage with hashing
- HttpOnly secure cookies
- Token rotation pattern
- Logout endpoints
- OAuth support
- Comprehensive tests
- Full documentation
