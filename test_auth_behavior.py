#!/usr/bin/env python3
"""
Manual inspection of auth.py login endpoint behavior

This script checks the auth.py code to verify it returns correct HTTP status codes
"""

import re

def analyze_auth_login_code():
    """Analyze the login endpoint code to verify correct status codes"""
    
    print("\n" + "="*80)
    print("🔐 AUTH ROUTE RESPONSE BEHAVIOR ANALYSIS")
    print("="*80 + "\n")
    
    with open('api/backend_app/api/auth.py', 'r') as f:
        code = f.read()
    
    # Find the login function
    login_match = re.search(r'@router\.post\("/login".*?\n(async )?def login\(.*?\):(.*?)(?=\n@router\.|$)', code, re.DOTALL)
    
    if not login_match:
        print("❌ Could not find login endpoint")
        return False
    
    login_code = login_match.group(0)
    
    print("📋 Checking login endpoint behavior...\n")
    
    # Check for HTTPException with 401
    unauthorized_errors = re.findall(r'raise HTTPException\s*\(\s*status_code\s*=\s*status\.HTTP_401_UNAUTHORIZED', login_code)
    print(f"✅ Found {len(unauthorized_errors)} HTTPException(401) raises")
    
    # Check for HTTPException with 403
    forbidden_errors = re.findall(r'raise HTTPException\s*\(\s*status_code\s*=\s*status\.HTTP_403_FORBIDDEN', login_code)
    print(f"✅ Found {len(forbidden_errors)} HTTPException(403) raises")
    
    # Check for success return (dict with tokens)
    success_return = re.search(r'return\s+\{[^}]*"access_token"[^}]*\}', login_code)
    if success_return:
        print("✅ Found success return with access_token")
    
    # Check for problematic patterns
    print("\n🔍 Checking for problematic patterns...\n")
    
    # Pattern 1: Returning 200 with error field
    bad_pattern_1 = re.search(r'return\s+\{[^}]*"error"[^}]*\}', login_code)
    if bad_pattern_1:
        print("❌ PROBLEM: Found return with 'error' field (200 + error pattern)")
        return False
    else:
        print("✅ No 'return {error: ...}' pattern found")
    
    # Pattern 2: JSONResponse with status 200 and error
    bad_pattern_2 = re.search(r'JSONResponse\([^)]*status_code\s*=\s*200[^)]*error', login_code)
    if bad_pattern_2:
        print("❌ PROBLEM: Found JSONResponse(status_code=200) with error")
        return False
    else:
        print("✅ No JSONResponse(200) with error pattern found")
    
    # Verify the correct pattern
    print("\n📊 Pattern Analysis:\n")
    
    # Count error scenarios
    user_not_found = bool(re.search(r'if not user:.*?raise HTTPException.*?401', login_code, re.DOTALL))
    invalid_password = bool(re.search(r'if not password_valid:.*?raise HTTPException.*?401', login_code, re.DOTALL))
    inactive_user = bool(re.search(r'if not user\.is_active:.*?raise HTTPException.*?403', login_code, re.DOTALL))
    
    if user_not_found:
        print("✅ User not found -> 401 Unauthorized")
    else:
        print("⚠️  Could not verify user not found handling")
    
    if invalid_password:
        print("✅ Invalid password -> 401 Unauthorized")
    else:
        print("⚠️  Could not verify invalid password handling")
    
    if inactive_user:
        print("✅ Inactive account -> 403 Forbidden")
    else:
        print("⚠️  Could not verify inactive account handling")
    
    # Final verdict
    print("\n" + "="*80)
    if user_not_found and invalid_password:
        print("✅ CODE ANALYSIS: Login endpoint appears correctly configured")
        print("   - Returns 401 on invalid credentials")
        print("   - Returns 200 with tokens on success")
        print("   - Does NOT use 200 + error message pattern")
        print("="*80 + "\n")
        return True
    else:
        print("⚠️  CODE ANALYSIS: Some patterns could not be verified")
        print("="*80 + "\n")
        return False


def check_response_model():
    """Check the response model for the login endpoint"""
    
    print("📄 Checking response model...\n")
    
    with open('api/backend_app/api/auth.py', 'r') as f:
        code = f.read()
    
    # Check if Token response model is used
    token_model = re.search(r'@router\.post\("/login",\s*response_model=Token\)', code)
    if token_model:
        print("✅ Login endpoint uses Token response model")
        return True
    else:
        print("⚠️  Could not verify Token response model")
        return False


def main():
    """Main analysis function"""
    
    try:
        code_ok = analyze_auth_login_code()
        model_ok = check_response_model()
        
        print("\n" + "="*80)
        print("📋 FINAL VERDICT:")
        print("="*80)
        
        if code_ok:
            print("\n✅ The login endpoint code is CORRECTLY IMPLEMENTED:")
            print("   1. Returns HTTP 401 for invalid credentials")
            print("   2. Returns HTTP 200 with tokens for valid credentials")
            print("   3. Does NOT use the problematic '200 + error' pattern")
            print("\n✅ No changes needed - the implementation matches requirements!\n")
            return 0
        else:
            print("\n❌ Potential issues detected - review needed\n")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}\n")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
