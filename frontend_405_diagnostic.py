"""
Frontend 405 Error Diagnostic Script
Identifies browser-side issues causing 405 errors in HireMeBahamas
"""

import subprocess
import json
import time
from pathlib import Path

class Frontend405Diagnostics:
    def __init__(self):
        self.frontend_path = Path("frontend")
        self.issues_found = []
        
    def check_frontend_environment(self):
        """Check frontend environment and configuration"""
        print("🔍 Checking Frontend Environment...")
        
        # Check if frontend directory exists
        if not self.frontend_path.exists():
            self.issues_found.append("Frontend directory not found")
            print("❌ Frontend directory not found")
            return False
            
        # Check package.json
        package_json = self.frontend_path / "package.json"
        if not package_json.exists():
            self.issues_found.append("package.json not found")
            print("❌ package.json not found")
            return False
        
        print("✅ Frontend directory and package.json found")
        
        # Check environment variables
        env_files = [".env", ".env.local", ".env.production"]
        env_found = False
        
        for env_file in env_files:
            env_path = self.frontend_path / env_file
            if env_path.exists():
                print(f"✅ Found environment file: {env_file}")
                env_found = True
                
                # Read and check API URL
                try:
                    with open(env_path, 'r') as f:
                        content = f.read()
                        if "VITE_API_URL" in content:
                            print("✅ VITE_API_URL found in environment")
                        else:
                            print("⚠️ VITE_API_URL not found in environment file")
                except Exception as e:
                    print(f"⚠️ Could not read {env_file}: {e}")
        
        if not env_found:
            print("⚠️ No environment files found - using default configuration")
            
        return True
    
    def check_api_configuration(self):
        """Check API configuration in frontend code"""
        print("\n🔍 Checking API Configuration...")
        
        api_file = self.frontend_path / "src" / "services" / "api.ts"
        if not api_file.exists():
            self.issues_found.append("API service file not found")
            print("❌ API service file not found")
            return False
            
        try:
            with open(api_file, 'r') as f:
                content = f.read()
                
            # Check API base URL configuration
            if "hiremebahamas.onrender.com" in content:
                print("✅ Production API URL found in code")
            else:
                print("⚠️ Production API URL not found in code")
                
            # Check axios configuration
            if "axios.create" in content:
                print("✅ Axios instance configuration found")
            else:
                print("⚠️ Axios instance configuration not found")
                
            # Check retry logic
            if "retry" in content.lower():
                print("✅ Retry logic found in API service")
            else:
                print("⚠️ No retry logic found")
                
            # Check error handling
            if "405" in content:
                print("✅ 405 error handling found in code")
            else:
                print("⚠️ No specific 405 error handling")
                
        except Exception as e:
            print(f"❌ Could not read API service file: {e}")
            return False
            
        return True
    
    def check_build_configuration(self):
        """Check build and deployment configuration"""
        print("\n🔍 Checking Build Configuration...")
        
        # Check vite.config
        vite_configs = ["vite.config.ts", "vite.config.js"]
        vite_found = False
        
        for config_file in vite_configs:
            config_path = self.frontend_path / config_file
            if config_path.exists():
                print(f"✅ Found Vite config: {config_file}")
                vite_found = True
                break
                
        if not vite_found:
            print("⚠️ Vite configuration not found")
            
        # Check vercel.json
        vercel_config = Path("vercel.json")
        if vercel_config.exists():
            print("✅ Vercel configuration found")
            try:
                with open(vercel_config, 'r') as f:
                    vercel_data = json.load(f)
                    
                if "rewrites" in vercel_data:
                    print("✅ Vercel rewrites configured (good for SPA)")
                else:
                    print("⚠️ No Vercel rewrites - may cause routing issues")
                    
            except Exception as e:
                print(f"⚠️ Could not parse vercel.json: {e}")
        else:
            print("⚠️ Vercel configuration not found")
            
        return True
    
    def generate_frontend_fixes(self):
        """Generate specific fixes for frontend issues"""
        print("\n🔧 FRONTEND-SPECIFIC FIXES:")
        
        fixes = [
            "1. Clear Browser Cache and Storage:",
            "   - Open browser DevTools (F12)",
            "   - Go to Application/Storage tab",
            "   - Clear localStorage and sessionStorage",
            "   - Hard refresh (Ctrl+Shift+R)",
            "",
            "2. Check Network Tab in DevTools:",
            "   - Open Network tab before attempting login",
            "   - Look for failed requests or 405 responses",
            "   - Check if OPTIONS preflight is successful",
            "",
            "3. Verify API Base URL:",
            "   - Check console logs for '[API] Base URL'",
            "   - Should show: https://hiremebahamas.onrender.com",
            "   - If wrong URL, check environment variables",
            "",
            "4. Test in Different Browser:",
            "   - Try Chrome, Firefox, Safari",
            "   - Disable browser extensions",
            "   - Use incognito/private mode",
            "",
            "5. Check CORS Headers:",
            "   - In Network tab, click on failed request",
            "   - Check Response Headers section",
            "   - Look for Access-Control-* headers",
            "",
            "6. Verify Frontend Build:",
            "   - Rebuild frontend: npm run build",
            "   - Redeploy to Vercel",
            "   - Check deployment logs for errors"
        ]
        
        for fix in fixes:
            print(fix)
    
    def create_test_html(self):
        """Create a simple test HTML file to test API directly"""
        test_html = """<!DOCTYPE html>
<html>
<head>
    <title>HireMeBahamas API Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background-color: #d4edda; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; border: 1px solid #f5c6cb; }
        button { padding: 10px 15px; margin: 5px; cursor: pointer; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>HireMeBahamas API Test</h1>
    <p>This tool tests the API directly from the browser to identify 405 errors.</p>
    
    <button onclick="testHealth()">Test Health</button>
    <button onclick="testLogin()">Test Login</button>
    <button onclick="testCORS()">Test CORS</button>
    <button onclick="clearResults()">Clear Results</button>
    
    <div id="results"></div>

    <script>
        const API_BASE = 'https://hiremebahamas.onrender.com';
        
        function addResult(title, success, data) {
            const results = document.getElementById('results');
            const div = document.createElement('div');
            div.className = `result ${success ? 'success' : 'error'}`;
            div.innerHTML = `
                <h3>${title}</h3>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;
            results.appendChild(div);
        }
        
        async function testHealth() {
            try {
                const response = await fetch(`${API_BASE}/health`);
                const data = await response.json();
                addResult('Health Check', response.ok, {
                    status: response.status,
                    data: data
                });
            } catch (error) {
                addResult('Health Check', false, {
                    error: error.message
                });
            }
        }
        
        async function testLogin() {
            try {
                const response = await fetch(`${API_BASE}/api/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: 'admin@hiremebahamas.com',
                        password: 'AdminPass123!'
                    })
                });
                
                const data = await response.json();
                addResult('Login Test', response.ok, {
                    status: response.status,
                    headers: Object.fromEntries(response.headers.entries()),
                    data: data
                });
            } catch (error) {
                addResult('Login Test', false, {
                    error: error.message
                });
            }
        }
        
        async function testCORS() {
            try {
                const response = await fetch(`${API_BASE}/api/auth/login`, {
                    method: 'OPTIONS',
                    headers: {
                        'Origin': window.location.origin,
                        'Access-Control-Request-Method': 'POST',
                        'Access-Control-Request-Headers': 'Content-Type,Authorization'
                    }
                });
                
                addResult('CORS Preflight', response.ok, {
                    status: response.status,
                    headers: Object.fromEntries(response.headers.entries())
                });
            } catch (error) {
                addResult('CORS Preflight', false, {
                    error: error.message
                });
            }
        }
        
        function clearResults() {
            document.getElementById('results').innerHTML = '';
        }
        
        // Auto-run tests on page load
        window.onload = function() {
            console.log('API Test page loaded. Click buttons to test endpoints.');
        };
    </script>
</body>
</html>"""
        
        with open('api_test.html', 'w') as f:
            f.write(test_html)
            
        print(f"\n📄 Created API test file: api_test.html")
        print("   Open this file in a browser to test API directly")
        print("   This will help identify if the issue is in the frontend code or browser")

    def run_diagnostic(self):
        """Run complete frontend diagnostic"""
        print("🔍 Frontend 405 Error Diagnostic")
        print("=" * 50)
        
        # Run checks
        env_ok = self.check_frontend_environment()
        api_ok = self.check_api_configuration()
        build_ok = self.check_build_configuration()
        
        # Create test file
        self.create_test_html()
        
        # Generate fixes
        self.generate_frontend_fixes()
        
        # Summary
        print(f"\n📊 Frontend Diagnostic Summary:")
        print(f"Environment Setup: {'✅' if env_ok else '❌'}")
        print(f"API Configuration: {'✅' if api_ok else '❌'}")
        print(f"Build Configuration: {'✅' if build_ok else '❌'}")
        
        if self.issues_found:
            print(f"\n⚠️ Issues Found:")
            for issue in self.issues_found:
                print(f"   • {issue}")
        else:
            print(f"\n✅ No major frontend issues detected")
            print(f"   The 405 error is likely a browser/network issue")

def main():
    diagnostics = Frontend405Diagnostics()
    diagnostics.run_diagnostic()

if __name__ == "__main__":
    main()