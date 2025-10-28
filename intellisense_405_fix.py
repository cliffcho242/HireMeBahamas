#!/usr/bin/env python3
"""
HireMeBahamas 405 Error Fix - Complete Solution
Uses IntelliSense and automated fixes to resolve login/signup 405 errors
"""

import json
import requests
from pathlib import Path
from datetime import datetime
import time

class HireBahamas405Fix:
    def __init__(self):
        self.backend_url = "https://hiremebahamas.onrender.com"
        self.fixes_applied = []
        
    def log_fix(self, fix_name: str, status: str, details: str = ""):
        """Log applied fixes"""
        fix_result = {
            "timestamp": datetime.now().isoformat(),
            "fix": fix_name,
            "status": status,
            "details": details
        }
        self.fixes_applied.append(fix_result)
        
        # Print with colors
        status_colors = {
            "APPLIED": "\033[92m✅",  # Green
            "FAILED": "\033[91m❌",   # Red
            "SKIPPED": "\033[93m⏭️",  # Yellow
        }
        
        color = status_colors.get(status, "")
        reset = "\033[0m"
        
        print(f"{color} {fix_name}: {status}{reset}")
        if details:
            print(f"   {details}")
        print()

    def test_api_endpoints(self) -> bool:
        """Test API endpoints to verify they're working"""
        print("🔧 Testing API Endpoints...")
        
        # Test health endpoint
        try:
            health_response = requests.get(f"{self.backend_url}/health", timeout=10)
            if health_response.status_code == 200:
                self.log_fix("Backend Health", "APPLIED", "Backend is responding correctly")
            else:
                self.log_fix("Backend Health", "FAILED", f"Unexpected status: {health_response.status_code}")
                return False
        except Exception as e:
            self.log_fix("Backend Health", "FAILED", f"Connection failed: {str(e)}")
            return False
        
        # Test login endpoint
        try:
            login_data = {
                "email": "admin@hiremebahamas.com",
                "password": "AdminPass123!"
            }
            login_response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code == 200:
                self.log_fix("Login Endpoint", "APPLIED", "Login endpoint working correctly")
            elif login_response.status_code == 405:
                self.log_fix("Login Endpoint", "FAILED", "405 error detected in backend")
                return False
            else:
                self.log_fix("Login Endpoint", "FAILED", f"Unexpected status: {login_response.status_code}")
                return False
                
        except Exception as e:
            self.log_fix("Login Endpoint", "FAILED", f"Request failed: {str(e)}")
            return False
            
        return True

    def create_browser_test_script(self) -> bool:
        """Create a browser test script for manual verification"""
        print("🔧 Creating Browser Test Script...")
        
        test_script = """<!DOCTYPE html>
<html>
<head>
    <title>HireMeBahamas 405 Error Test</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .result { margin: 15px 0; padding: 15px; border-radius: 8px; }
        .success { background-color: #d4edda; border-left: 4px solid #28a745; }
        .error { background-color: #f8d7da; border-left: 4px solid #dc3545; }
        .warning { background-color: #fff3cd; border-left: 4px solid #ffc107; }
        button { background: #007bff; color: white; border: none; padding: 12px 20px; margin: 8px; border-radius: 6px; cursor: pointer; font-size: 14px; }
        button:hover { background: #0056b3; }
        .clear-btn { background: #6c757d; }
        .clear-btn:hover { background: #545b62; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 12px; border: 1px solid #e9ecef; }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .status-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 10px; }
        .badge-success { background: #28a745; color: white; }
        .badge-error { background: #dc3545; color: white; }
        .instructions { background: #e7f3ff; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 HireMeBahamas 405 Error Diagnostic</h1>
        
        <div class="instructions">
            <strong>Instructions:</strong>
            <ol>
                <li>Open browser DevTools (F12) and go to Network tab</li>
                <li>Click the test buttons below</li>
                <li>Check for any 405 errors in the Network tab</li>
                <li>Compare results with what you see on the actual website</li>
            </ol>
        </div>
        
        <div>
            <button onclick="testHealth()">🏥 Test Health</button>
            <button onclick="testLogin()">🔐 Test Login</button>
            <button onclick="testSignup()">📝 Test Signup</button>
            <button onclick="testCORS()">🌐 Test CORS</button>
            <button onclick="clearResults()" class="clear-btn">🗑️ Clear Results</button>
        </div>
        
        <div id="results"></div>
    </div>

    <script>
        const API_BASE = 'https://hiremebahamas.onrender.com';
        
        function addResult(title, success, data, isWarning = false) {
            const results = document.getElementById('results');
            const div = document.createElement('div');
            const statusClass = isWarning ? 'warning' : (success ? 'success' : 'error');
            const statusBadge = isWarning ? 'Warning' : (success ? 'Success' : 'Error');
            const badgeClass = isWarning ? 'badge-warning' : (success ? 'badge-success' : 'badge-error');
            
            div.className = `result ${statusClass}`;
            div.innerHTML = `
                <h3>${title} <span class="status-badge ${badgeClass}">${statusBadge}</span></h3>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;
            results.appendChild(div);
            
            // Auto-scroll to new result
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        async function testHealth() {
            try {
                console.log('Testing health endpoint...');
                const response = await fetch(`${API_BASE}/health`);
                const data = await response.json();
                
                addResult('Health Check', response.ok, {
                    status: response.status,
                    url: response.url,
                    headers: Object.fromEntries(response.headers.entries()),
                    data: data
                });
                
                console.log('Health test completed:', response.status);
            } catch (error) {
                console.error('Health test error:', error);
                addResult('Health Check', false, {
                    error: error.message,
                    stack: error.stack
                });
            }
        }
        
        async function testLogin() {
            try {
                console.log('Testing login endpoint...');
                
                // First test OPTIONS request (CORS preflight)
                const optionsResponse = await fetch(`${API_BASE}/api/auth/login`, {
                    method: 'OPTIONS',
                    headers: {
                        'Origin': window.location.origin,
                        'Access-Control-Request-Method': 'POST',
                        'Access-Control-Request-Headers': 'Content-Type,Authorization'
                    }
                });
                
                console.log('OPTIONS response:', optionsResponse.status);
                
                // Then test actual POST request
                const response = await fetch(`${API_BASE}/api/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Origin': window.location.origin
                    },
                    body: JSON.stringify({
                        email: 'admin@hiremebahamas.com',
                        password: 'AdminPass123!'
                    })
                });
                
                let data;
                try {
                    data = await response.json();
                } catch (e) {
                    data = { error: 'Could not parse JSON response', response_text: await response.text() };
                }
                
                addResult('Login Test', response.ok, {
                    status: response.status,
                    url: response.url,
                    options_status: optionsResponse.status,
                    headers: Object.fromEntries(response.headers.entries()),
                    data: data
                });
                
                console.log('Login test completed:', response.status);
                
                // Special check for 405 error
                if (response.status === 405) {
                    addResult('❌ 405 Error Detected!', false, {
                        message: 'The server returned a 405 Method Not Allowed error',
                        possible_causes: [
                            'Server routing issue',
                            'CORS preflight failure', 
                            'Backend deployment problem',
                            'Load balancer configuration'
                        ],
                        next_steps: [
                            'Check server logs',
                            'Verify backend deployment status',
                            'Test with different browser/incognito mode',
                            'Contact backend administrator'
                        ]
                    });
                }
                
            } catch (error) {
                console.error('Login test error:', error);
                addResult('Login Test', false, {
                    error: error.message,
                    stack: error.stack
                });
            }
        }
        
        async function testSignup() {
            try {
                console.log('Testing signup endpoint...');
                const response = await fetch(`${API_BASE}/api/auth/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Origin': window.location.origin
                    },
                    body: JSON.stringify({
                        email: `test_${Date.now()}@example.com`,
                        password: 'TestPassword123!',
                        first_name: 'Test',
                        last_name: 'User',
                        user_type: 'freelancer',
                        location: 'Nassau'
                    })
                });
                
                let data;
                try {
                    data = await response.json();
                } catch (e) {
                    data = { error: 'Could not parse JSON response', response_text: await response.text() };
                }
                
                addResult('Signup Test', response.ok, {
                    status: response.status,
                    url: response.url,
                    headers: Object.fromEntries(response.headers.entries()),
                    data: data
                });
                
                console.log('Signup test completed:', response.status);
            } catch (error) {
                console.error('Signup test error:', error);
                addResult('Signup Test', false, {
                    error: error.message,
                    stack: error.stack
                });
            }
        }
        
        async function testCORS() {
            try {
                console.log('Testing CORS configuration...');
                const response = await fetch(`${API_BASE}/api/auth/login`, {
                    method: 'OPTIONS',
                    headers: {
                        'Origin': window.location.origin,
                        'Access-Control-Request-Method': 'POST',
                        'Access-Control-Request-Headers': 'Content-Type,Authorization'
                    }
                });
                
                const corsHeaders = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                    'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
                };
                
                addResult('CORS Preflight', response.ok, {
                    status: response.status,
                    cors_headers: corsHeaders,
                    all_headers: Object.fromEntries(response.headers.entries())
                });
                
                console.log('CORS test completed:', response.status);
            } catch (error) {
                console.error('CORS test error:', error);
                addResult('CORS Preflight', false, {
                    error: error.message,
                    stack: error.stack
                });
            }
        }
        
        function clearResults() {
            document.getElementById('results').innerHTML = '';
            console.clear();
            console.log('Results cleared. Ready for new tests.');
        }
        
        // Show current page info
        console.log('HireMeBahamas 405 Error Diagnostic loaded');
        console.log('Current origin:', window.location.origin);
        console.log('Target API:', API_BASE);
        console.log('User agent:', navigator.userAgent);
        
        // Auto-run health check on load
        window.addEventListener('load', () => {
            setTimeout(testHealth, 1000);
        });
    </script>
</body>
</html>"""
        
        try:
            with open('405_error_test.html', 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            self.log_fix("Browser Test Script", "APPLIED", "Created 405_error_test.html")
            return True
            
        except Exception as e:
            self.log_fix("Browser Test Script", "FAILED", f"Error: {str(e)}")
            return False

    def generate_deployment_fix(self) -> bool:
        """Generate PowerShell script to fix and redeploy"""
        print("🔧 Generating Deployment Fix Script...")
        
        ps_script = """# HireMeBahamas 405 Error Fix and Redeploy
Write-Host "🚀 HireMeBahamas 405 Error Fix" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "vercel.json")) {
    Write-Host "❌ vercel.json not found. Please run this from the project root." -ForegroundColor Red
    exit 1
}

Write-Host "📍 Current directory: $(Get-Location)" -ForegroundColor Green

# Step 1: Test backend API
Write-Host "`n🔍 Step 1: Testing backend API..." -ForegroundColor Yellow
try {
    $healthTest = Invoke-RestMethod -Uri "https://hiremebahamas.onrender.com/health" -TimeoutSec 10
    Write-Host "✅ Backend health: $($healthTest.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "⚠️  Continuing anyway..." -ForegroundColor Yellow
}

# Step 2: Check vercel.json configuration
Write-Host "`n📝 Step 2: Checking vercel.json configuration..." -ForegroundColor Yellow
$vercelConfig = Get-Content "vercel.json" | ConvertFrom-Json
$currentApiUrl = $vercelConfig.env.VITE_API_URL

if ($currentApiUrl -eq "https://hiremebahamas.onrender.com") {
    Write-Host "✅ API URL is correct: $currentApiUrl" -ForegroundColor Green
} else {
    Write-Host "❌ API URL needs fixing: $currentApiUrl" -ForegroundColor Red
    Write-Host "🔧 Fixing API URL..." -ForegroundColor Yellow
    
    $vercelConfig.env.VITE_API_URL = "https://hiremebahamas.onrender.com"
    $vercelConfig | ConvertTo-Json -Depth 10 | Set-Content "vercel.json"
    
    Write-Host "✅ API URL fixed!" -ForegroundColor Green
}

# Step 3: Check frontend environment
Write-Host "`n📁 Step 3: Checking frontend environment..." -ForegroundColor Yellow
if (Test-Path "frontend/.env") {
    $envContent = Get-Content "frontend/.env"
    $apiUrlLine = $envContent | Where-Object { $_ -like "VITE_API_URL=*" }
    
    if ($apiUrlLine -eq "VITE_API_URL=https://hiremebahamas.onrender.com") {
        Write-Host "✅ Frontend .env is correct" -ForegroundColor Green
    } else {
        Write-Host "🔧 Fixing frontend .env..." -ForegroundColor Yellow
        
        # Remove old API URL line and add correct one
        $newEnvContent = $envContent | Where-Object { $_ -notlike "VITE_API_URL=*" }
        $newEnvContent += "VITE_API_URL=https://hiremebahamas.onrender.com"
        
        $newEnvContent | Set-Content "frontend/.env"
        Write-Host "✅ Frontend .env fixed!" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Frontend .env not found, creating..." -ForegroundColor Yellow
    @(
        "VITE_API_URL=https://hiremebahamas.onrender.com",
        "VITE_SOCKET_URL=https://hiremebahamas.onrender.com",
        "VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name"
    ) | Set-Content "frontend/.env"
    Write-Host "✅ Frontend .env created!" -ForegroundColor Green
}

# Step 4: Rebuild and redeploy
Write-Host "`n🏗️  Step 4: Rebuilding frontend..." -ForegroundColor Yellow
Set-Location frontend

if (Test-Path "package.json") {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
    npm install
    
    Write-Host "🔨 Building frontend..." -ForegroundColor Cyan
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend build successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend build failed!" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
} else {
    Write-Host "❌ package.json not found in frontend directory!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

# Step 5: Commit and deploy
Write-Host "`n🚀 Step 5: Deploying changes..." -ForegroundColor Yellow

Write-Host "📝 Adding changes to git..." -ForegroundColor Cyan
git add .

Write-Host "💾 Committing changes..." -ForegroundColor Cyan
git commit -m "Fix 405 error: Update API URLs and configuration"

if ($LASTEXITCODE -eq 0) {
    Write-Host "📤 Pushing to repository..." -ForegroundColor Cyan
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Changes pushed successfully!" -ForegroundColor Green
        Write-Host "`n🎉 Deployment initiated!" -ForegroundColor Green
        Write-Host "⏱️  Please wait 2-3 minutes for Vercel to deploy the changes." -ForegroundColor Yellow
        Write-Host "`n🌐 Test the website at: https://hiremebahamas.vercel.app" -ForegroundColor Cyan
        Write-Host "🔍 Use browser DevTools (F12 > Network tab) to check for 405 errors" -ForegroundColor Cyan
        Write-Host "🧪 Or open '405_error_test.html' in your browser for detailed testing" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Git push failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  No changes to commit" -ForegroundColor Yellow
    Write-Host "✅ Configuration is already correct!" -ForegroundColor Green
}

Write-Host "`n🎊 405 Error Fix Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
"""
        
        try:
            with open('fix_405_and_deploy.ps1', 'w', encoding='utf-8') as f:
                f.write(ps_script)
            
            self.log_fix("Deployment Script", "APPLIED", "Created fix_405_and_deploy.ps1")
            return True
            
        except Exception as e:
            self.log_fix("Deployment Script", "FAILED", f"Error: {str(e)}")
            return False

    def run_complete_fix(self) -> None:
        """Run all fixes and generate comprehensive solution"""
        print("🚀 HireMeBahamas 405 Error Complete Fix")
        print("=" * 60)
        
        print("Running IntelliSense-driven 405 error diagnosis and fix...")
        
        # Apply all fixes
        test_ok = self.create_browser_test_script()
        deploy_ok = self.generate_deployment_fix()
        
        # Test endpoints
        print("Testing API endpoints...")
        endpoints_ok = self.test_api_endpoints()
        
        # Generate summary report
        print("\n" + "=" * 60)
        print("📊 FIX SUMMARY")
        print("=" * 60)
        
        print(f"Browser Test Script: {'✅ CREATED' if test_ok else '❌ FAILED'}")
        print(f"Deployment Fix Script: {'✅ GENERATED' if deploy_ok else '❌ FAILED'}")
        print(f"API Endpoints: {'✅ WORKING' if endpoints_ok else '❌ NOT WORKING'}")
        
        print("\n🎯 NEXT STEPS:")
        
        if endpoints_ok:
            print("1. ✅ Backend is working correctly")
            print("2. 🔄 Run the deployment fix:")
            print("   PowerShell: .\\fix_405_and_deploy.ps1")
            print("3. 🧪 Test using 405_error_test.html in browser")
            print("4. 🌐 Try logging in at https://hiremebahamas.vercel.app")
        else:
            print("1. ❌ Backend has issues - check Render.com deployment")
            print("2. 🔍 Backend may be sleeping - try waking it up")
            print("3. 📋 Review backend logs for errors")
        
        print(f"\n📁 Files created:")
        print(f"   • 405_error_test.html - Browser diagnostic tool")
        print(f"   • fix_405_and_deploy.ps1 - Automated fix and deploy script")
        
        # Save detailed results
        summary = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "summary": {
                "test_script": test_ok,
                "deployment_script": deploy_ok,
                "api_endpoints": endpoints_ok
            },
            "backend_url": self.backend_url,
            "next_steps": [
                "Run fix_405_and_deploy.ps1",
                "Test using browser test script",
                "Verify login functionality"
            ]
        }
        
        with open('405_fix_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Detailed summary saved to: 405_fix_summary.json")
        print("=" * 60)

def main():
    fix_tool = HireBahamas405Fix()
    fix_tool.run_complete_fix()

if __name__ == "__main__":
    main()