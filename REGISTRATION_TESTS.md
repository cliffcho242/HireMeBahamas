# Registration Testing Documentation

## Overview
This document describes the comprehensive test suite for the HireMeBahamas user registration functionality.

## Test Suite: `test_registration.py`

The registration test suite contains **17 comprehensive test cases** that validate all aspects of the user registration process.

### Running the Tests

#### Locally
```bash
# Install dependencies
pip install pytest pytest-flask
pip install -r requirements.txt

# Run all registration tests
python -m pytest test_registration.py -v

# Run specific test
python -m pytest test_registration.py::TestRegistration::test_successful_registration -v

# Run with detailed output
python -m pytest test_registration.py -v --tb=short
```

#### In CI/CD
The tests are automatically run as part of the CI pipeline on every push and pull request to the `main` branch.

### Test Coverage

#### ✅ Success Cases (2 tests)
1. **test_successful_registration**
   - Validates successful registration with all required fields
   - Checks user data is correctly saved
   - Verifies JWT token generation
   - Status Code: 201 Created

2. **test_registration_with_optional_fields**
   - Tests registration with optional fields (phone, bio)
   - Verifies optional data is saved correctly
   - Status Code: 201 Created

#### ❌ Validation Errors (14 tests)

##### Missing Required Fields (6 tests)
3. **test_registration_missing_email** - Status Code: 400
4. **test_registration_missing_password** - Status Code: 400
5. **test_registration_missing_first_name** - Status Code: 400
6. **test_registration_missing_last_name** - Status Code: 400
7. **test_registration_missing_user_type** - Status Code: 400
8. **test_registration_missing_location** - Status Code: 400

##### Password Strength Validation (3 tests)
9. **test_registration_weak_password_too_short**
   - Password must be at least 8 characters
   - Status Code: 400

10. **test_registration_weak_password_no_number**
    - Password must contain at least one number
    - Status Code: 400

11. **test_registration_weak_password_no_letter**
    - Password must contain at least one letter
    - Status Code: 400

##### Duplicate Email Handling (2 tests)
12. **test_registration_duplicate_email**
    - Prevents registration with existing email
    - Status Code: 409 Conflict

13. **test_registration_email_case_insensitive**
    - Email comparison is case-insensitive
    - `Test@Example.com` == `test@example.com`
    - Status Code: 409 Conflict

##### Data Validation (3 tests)
14. **test_registration_empty_string_fields**
    - Empty strings are treated as missing fields
    - Status Code: 400

15. **test_registration_whitespace_trimming**
    - Leading/trailing whitespace is automatically trimmed
    - Email is lowercased
    - Status Code: 201 Created

#### 🔒 Security & Token Tests (2 tests)
16. **test_registration_token_generation**
    - Verifies JWT token is generated on successful registration
    - Validates token format (3 parts: header.payload.signature)
    - Checks token expiration (7 days)

17. **test_registration_options_request**
    - Validates CORS OPTIONS request handling
    - Required for frontend CORS support
    - Status Code: 200 OK

## Registration Endpoint

### URL
```
POST /api/auth/register
```

### Required Fields
- `email` (string): User's email address (unique, case-insensitive)
- `password` (string): Must be ≥8 characters with ≥1 letter and ≥1 number
- `first_name` (string): User's first name
- `last_name` (string): User's last name
- `user_type` (string): Type of user (e.g., "freelancer", "employer")
- `location` (string): User's location (e.g., "Nassau, Bahamas")

### Optional Fields
- `phone` (string): Phone number
- `bio` (string): User biography

### Request Example
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "freelancer",
  "location": "Nassau, Bahamas",
  "phone": "+1-242-555-1234",
  "bio": "Experienced software developer"
}
```

### Success Response (201 Created)
```json
{
  "success": true,
  "message": "Registration successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 123,
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "freelancer",
    "location": "Nassau, Bahamas",
    "phone": "+1-242-555-1234",
    "bio": "Experienced software developer",
    "avatar_url": "",
    "is_available_for_hire": false
  }
}
```

### Error Response Examples

#### Missing Required Field (400 Bad Request)
```json
{
  "success": false,
  "message": "Email is required"
}
```

#### Weak Password (400 Bad Request)
```json
{
  "success": false,
  "message": "Password must be at least 8 characters with at least one letter and one number"
}
```

#### Duplicate Email (409 Conflict)
```json
{
  "success": false,
  "message": "User with this email already exists"
}
```

#### Server Error (500 Internal Server Error)
```json
{
  "success": false,
  "message": "Registration failed: [error details]"
}
```

## Test Implementation Details

### Test Isolation
- Each test uses a temporary SQLite database
- Database is created before each test and cleaned up after
- No shared state between tests

### Test Database Schema
The test database includes all fields from the production users table:
- `id` (INTEGER PRIMARY KEY)
- `email` (TEXT UNIQUE NOT NULL)
- `password_hash` (TEXT NOT NULL)
- `first_name`, `last_name`, `user_type`, `location`
- `phone`, `bio`, `avatar_url`
- `is_active`, `is_available_for_hire`
- `created_at`, `last_login` (TIMESTAMP)

### Password Hashing
- Passwords are hashed using bcrypt
- Salt is automatically generated for each password
- Original passwords are never stored in the database

### JWT Token
- Tokens are signed using HS256 algorithm
- Token payload includes: `user_id`, `email`, `exp` (expiration)
- Token expires 7 days after creation
- Token is returned on successful registration for immediate login

## Continuous Integration

The registration tests run automatically in GitHub Actions:
- On every push to `main` branch
- On every pull request to `main` branch
- After backend dependencies are installed
- Results visible in GitHub Actions tab

### CI Workflow Steps
1. Checkout code
2. Install system dependencies (build-essential, libpq-dev, python3-dev)
3. Setup Python 3.11
4. Install pytest and pytest-flask
5. Install backend dependencies
6. Run backend tests
7. **Run registration tests** ← New step

## Future Improvements

Potential enhancements to the test suite:
- [ ] Test email format validation
- [ ] Test phone number format validation
- [ ] Test rate limiting on registration endpoint
- [ ] Test registration with special characters in names
- [ ] Test maximum field length validation
- [ ] Integration tests with real PostgreSQL database
- [ ] Performance tests for concurrent registrations
- [ ] Test account activation/verification flow
- [ ] Test registration with OAuth providers
- [ ] Test username generation and uniqueness

## Related Files
- `test_registration.py` - Main test suite
- `final_backend.py` - Registration implementation
- `.github/workflows/ci.yml` - CI/CD configuration
- `test_registration.ps1` - PowerShell test script for manual testing
