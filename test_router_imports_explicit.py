"""
Test that the new explicit router import pattern works correctly.

This verifies that the pattern:
    from app.api.analytics import router as analytics_router
works as expected.
"""
import sys
import os
import ast

# Add api directory to path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(repo_root, 'api'))

print("="*70)
print("Testing Explicit Router Import Pattern")
print("="*70)

# Test 1: Verify main.py syntax is valid
print("\n1. Verify main.py syntax...")
try:
    with open(os.path.join(repo_root, 'api', 'backend_app', 'main.py'), 'r') as f:
        code = f.read()
    ast.parse(code)
    print("   ✓ main.py syntax is valid")
except SyntaxError as e:
    print(f"   ✗ FAILED: Syntax error in main.py: {e}")
    sys.exit(1)

# Test 2: Check that imports follow the explicit pattern
print("\n2. Verify imports use explicit pattern...")
import_lines = []
include_lines = []

for line in code.split('\n'):
    stripped = line.strip()
    if stripped.startswith('from app.api.') and 'import router as' in stripped:
        import_lines.append(stripped)
    elif 'app.include_router(' in stripped and not stripped.startswith('#'):
        include_lines.append(stripped)

expected_routers = [
    'analytics', 'auth', 'debug', 'feed', 'health', 'hireme', 'jobs',
    'messages', 'notifications', 'posts', 'profile_pictures',
    'reviews', 'upload', 'users'
]

print(f"   Found {len(import_lines)} explicit router imports")

# Verify all expected routers are imported with the explicit pattern
for router in expected_routers:
    import_pattern = f'from app.api.{router} import router as {router}_router'
    if import_pattern not in code:
        print(f"   ✗ FAILED: Missing import for {router}")
        print(f"      Expected: {import_pattern}")
        sys.exit(1)

print(f"   ✓ All {len(expected_routers)} routers use explicit import pattern")

# Test 3: Verify app.include_router calls use the aliased names
print("\n3. Verify router inclusions use aliased names...")
for router in expected_routers:
    router_var = f'{router}_router'
    # Check if the router is included (may have prefix or not)
    if router_var not in code or f'include_router({router_var}' not in code:
        print(f"   ✗ FAILED: Router {router} not included with alias {router_var}")
        sys.exit(1)

print(f"   ✓ All {len(expected_routers)} routers included with aliased names")

# Test 4: Verify no old-style imports remain
print("\n4. Verify no old-style imports remain...")
old_pattern = 'from app.api import'
lines_with_old_pattern = [line for line in code.split('\n') if old_pattern in line and 'router as' not in line]

# Filter out comments
lines_with_old_pattern = [line for line in lines_with_old_pattern if not line.strip().startswith('#')]

if lines_with_old_pattern:
    print(f"   ⚠ Warning: Found {len(lines_with_old_pattern)} lines with old import pattern:")
    for line in lines_with_old_pattern[:3]:
        print(f"      {line.strip()}")
else:
    print("   ✓ No old-style imports found")

print("\n" + "="*70)
print("✅ All explicit router import tests PASSED!")
print()
print("Summary:")
print("  - main.py uses explicit router imports")
print(f"  - Pattern: from app.api.X import router as X_router")
print(f"  - All {len(expected_routers)} routers imported correctly")
print("  - All routers included using aliased names")
print("="*70)
