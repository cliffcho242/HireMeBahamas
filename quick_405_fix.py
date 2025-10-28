#!/usr/bin/env python3
"""Quick 405 Fix Script"""

import re
from pathlib import Path

def fix_backend_routes():
    """Add OPTIONS to auth routes"""
    print("Fixing backend routes...")
    
    # Target the main backend file
    backend_file = Path("ULTIMATE_BACKEND_FIXED.py")
    if not backend_file.exists():
        backend_file = Path("final_backend.py") 
    if not backend_file.exists():
        print("❌ No main backend file found")
        return
        
    with open(backend_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Fix routes missing OPTIONS
    original_content = content
    content = re.sub(
        r'methods\s*=\s*\["POST"\]',
        'methods=["POST", "OPTIONS"]',
        content
    )
    content = re.sub(
        r"methods\s*=\s*\['POST'\]",
        "methods=['POST', 'OPTIONS']",
        content
    )
    
    if content != original_content:
        with open(backend_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed routes in {backend_file.name}")
    else:
        print("ℹ️ No route fixes needed")

def fix_frontend_api():
    """Add 405 error handling to frontend"""
    print("Fixing frontend API...")
    
    api_file = Path("frontend/src/services/api.ts")
    if not api_file.exists():
        print("❌ Frontend API file not found")
        return
        
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "status === 405" not in content:
        # Add 405 handling in error interceptor
        error_handler = """
    // Handle 405 Method Not Allowed
    if (error.response?.status === 405) {
      console.error('405 Method Not Allowed:', error.config?.url);
      throw new Error('Service temporarily unavailable. Please try again.');
    }
"""
        
        # Insert before existing error handling
        if "console.error('API Error':" in content:
            content = content.replace(
                "console.error('API Error':",
                error_handler + "\n    console.error('API Error':"
            )
            
            with open(api_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Added 405 error handling to frontend")
        else:
            print("⚠️ Could not find insertion point for error handler")
    else:
        print("ℹ️ 405 error handling already present")

if __name__ == "__main__":
    print("🔧 Applying quick fixes for 405 errors...")
    fix_backend_routes() 
    fix_frontend_api()
    print("✅ Fixes applied! Test the login again.")
