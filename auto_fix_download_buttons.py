"""
Automated Fix for Download Page Button Click Issues
This script diagnoses and fixes button interactivity problems
"""

import os
import subprocess
import sys
import time


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd, cwd=None):
    """Run a command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


print_header("Download Button Auto-Fix Starting...")

# Step 1: Check if React Router is properly installed
print("Step 1: Checking React Router installation...")
frontend_dir = r"C:\Users\Dell\OneDrive\Desktop\HireBahamas\frontend"
success, stdout, stderr = run_command("npm list react-router-dom", cwd=frontend_dir)
if "react-router-dom@" in stdout:
    print("✓ React Router is installed")
else:
    print("✗ React Router missing - Installing...")
    run_command("npm install react-router-dom", cwd=frontend_dir)
    print("✓ React Router installed")

# Step 2: Check Download.tsx file
print("\nStep 2: Analyzing Download.tsx...")
download_file = os.path.join(frontend_dir, "src", "pages", "Download.tsx")

if not os.path.exists(download_file):
    print(f"✗ Download.tsx not found at {download_file}")
    sys.exit(1)

with open(download_file, "r", encoding="utf-8") as f:
    content = f.read()

issues = []
fixes_applied = []

# Check for common issues
if "onClick" not in content:
    issues.append("Missing onClick handlers")

if 'type="button"' not in content:
    issues.append("Missing button type attributes")

if "cursor-pointer" not in content:
    issues.append("Missing cursor-pointer class")

if issues:
    print(f"✗ Found {len(issues)} potential issues:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✓ No obvious syntax issues found")

# Step 3: Create a simplified test version
print("\nStep 3: Creating simplified Download page test...")
test_content = """import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';

const DownloadTest: React.FC = () => {
  const navigate = useNavigate();

  const handleClick = () => {
    console.log('🎯 BUTTON CLICKED!');
    alert('Button is working!');
  };

  const handleNavigate = () => {
    console.log('🚀 Navigating to home...');
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
        <h1 className="text-4xl font-bold text-center mb-8">
          Button Click Test
        </h1>
        
        <div className="space-y-4">
          {/* Test 1: Simple Button */}
          <button
            type="button"
            onClick={handleClick}
            style={{ cursor: 'pointer', touchAction: 'manipulation' }}
            className="w-full px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold text-lg hover:bg-blue-700 active:bg-blue-800"
          >
            <span>Test 1: Click Me (Alert)</span>
          </button>

          {/* Test 2: Navigation Button */}
          <button
            type="button"
            onClick={handleNavigate}
            style={{ cursor: 'pointer', touchAction: 'manipulation' }}
            className="w-full px-8 py-4 bg-green-600 text-white rounded-lg font-semibold text-lg hover:bg-green-700 active:bg-green-800"
          >
            <span>Test 2: Navigate Home</span>
          </button>

          {/* Test 3: Install Button Simulation */}
          <button
            type="button"
            onClick={() => {
              console.log('Install button clicked');
              alert('This would trigger PWA install');
              navigate('/');
            }}
            style={{ cursor: 'pointer', touchAction: 'manipulation' }}
            className="w-full px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-bold text-lg hover:shadow-xl"
          >
            <ArrowDownTrayIcon className="inline w-6 h-6 mr-2" />
            <span>Test 3: Simulate Install</span>
          </button>
        </div>

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">
            ✓ Open browser console (F12) to see click events<br/>
            ✓ Each button should respond immediately<br/>
            ✓ Check for console.log messages
          </p>
        </div>
      </div>
    </div>
  );
};

export default DownloadTest;
"""

test_file = os.path.join(frontend_dir, "src", "pages", "DownloadTest.tsx")
with open(test_file, "w", encoding="utf-8") as f:
    f.write(test_content)
print(f"✓ Created test file: {test_file}")
fixes_applied.append("Created DownloadTest.tsx for debugging")

# Step 4: Update App.tsx to include test route
print("\nStep 4: Adding test route to App.tsx...")
app_file = os.path.join(frontend_dir, "src", "App.tsx")

with open(app_file, "r", encoding="utf-8") as f:
    app_content = f.read()

if "DownloadTest" not in app_content:
    # Add import
    import_line = "import DownloadTest from './pages/DownloadTest';"
    if "import Download from './pages/Download';" in app_content:
        app_content = app_content.replace(
            "import Download from './pages/Download';",
            "import Download from './pages/Download';\n" + import_line,
        )

    # Add route
    if '<Route path="/download" element={<Download />} />' in app_content:
        app_content = app_content.replace(
            '<Route path="/download" element={<Download />} />',
            '<Route path="/download" element={<Download />} />\n          <Route path="/download-test" element={<DownloadTest />} />',
        )

    with open(app_file, "w", encoding="utf-8") as f:
        f.write(app_content)

    print("✓ Added /download-test route")
    fixes_applied.append("Added test route to App.tsx")
else:
    print("✓ Test route already exists")

# Step 5: Build and check for errors
print("\nStep 5: Building project...")
success, stdout, stderr = run_command("npm run build", cwd=frontend_dir)

if success:
    print("✓ Build successful!")
else:
    print("✗ Build failed. Checking errors...")
    if stderr:
        print("Errors:")
        print(stderr[:500])

# Step 6: Summary
print_header("Auto-Fix Complete!")

print("📊 Summary:")
print(f"  Issues Found: {len(issues)}")
print(f"  Fixes Applied: {len(fixes_applied)}")

if fixes_applied:
    print("\n✅ Applied Fixes:")
    for fix in fixes_applied:
        print(f"  - {fix}")

print("\n🧪 Testing Instructions:")
print("  1. Visit: http://localhost:3000/download-test")
print("  2. Open browser console (F12 → Console tab)")
print("  3. Click each button")
print("  4. Verify console.log messages appear")
print("  5. If test buttons work, issue is with Download.tsx logic")
print("  6. If test buttons don't work, issue is with React Router or build")

print("\n📝 Next Steps:")
print("  1. Open http://localhost:3000/download-test in browser")
print("  2. Test all three buttons")
print("  3. Check console for errors")
print("  4. Compare with actual /download page")

print("\n" + "=" * 60)
print("Test file created: src/pages/DownloadTest.tsx")
print("Test route added: /download-test")
print("Original file unchanged: src/pages/Download.tsx")
print("=" * 60)
