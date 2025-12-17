"""
Simple test to verify the database warmup fix.

This test verifies that:
1. init_db() is properly awaited
2. warmup_db() is called without engine parameter
3. The code structure is correct
"""
import ast
import sys


def check_background_init_function():
    """Check that background_init properly awaits init_db."""
    print("Checking app/main.py for correct async/await usage...")
    
    with open("app/main.py", "r") as f:
        content = f.read()
    
    # Parse the file
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"✗ Syntax error in app/main.py: {e}")
        return False
    
    # Find the background_init function
    background_init = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "background_init":
            background_init = node
            break
    
    if not background_init:
        print("✗ Could not find background_init function")
        return False
    
    print("✓ Found background_init function")
    
    # Check for proper await usage with init_db()
    found_await_init_db = False
    found_warmup_call = False
    
    for node in ast.walk(background_init):
        # Check for: success = await init_db()
        if isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                if node.targets[0].id == "success":
                    if isinstance(node.value, ast.Await):
                        if isinstance(node.value.value, ast.Call):
                            if isinstance(node.value.value.func, ast.Name):
                                if node.value.value.func.id == "init_db":
                                    found_await_init_db = True
                                    print("✓ Found: success = await init_db()")
        
        # Check for: await warmup_db() with no arguments
        if isinstance(node, ast.Await):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name):
                    if node.value.func.id == "warmup_db":
                        # Check that warmup_db is called with no arguments
                        if len(node.value.args) == 0 and len(node.value.keywords) == 0:
                            found_warmup_call = True
                            print("✓ Found: await warmup_db() with no arguments")
                        else:
                            print(f"⚠ warmup_db called with arguments: {len(node.value.args)} args, {len(node.value.keywords)} kwargs")
    
    if not found_await_init_db:
        print("✗ Did not find 'success = await init_db()'")
        return False
    
    if not found_warmup_call:
        print("✗ Did not find 'await warmup_db()' with no arguments")
        return False
    
    print("\n✅ All checks passed!")
    print("   - init_db() is properly awaited")
    print("   - Result is stored in 'success' variable")
    print("   - warmup_db() is called without engine parameter")
    return True


def check_no_coroutine_errors():
    """Check that the common error patterns are not present."""
    print("\nChecking for common error patterns...")
    
    with open("app/main.py", "r") as f:
        content = f.read()
    
    # Check for the old incorrect pattern: engine = init_db()
    if "engine = init_db()" in content and "await" not in content[:content.index("engine = init_db()")]:
        print("✗ Found old pattern: engine = init_db() without await")
        return False
    
    print("✓ No old error patterns found")
    return True


def main():
    """Run all checks."""
    print("=" * 70)
    print("Database Warmup Fix Verification")
    print("=" * 70)
    print()
    
    checks = [
        ("Background init function structure", check_background_init_function),
        ("No coroutine error patterns", check_no_coroutine_errors),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n[CHECK] {name}")
        try:
            if not check_func():
                all_passed = False
                print(f"[FAIL] {name}")
        except Exception as e:
            all_passed = False
            print(f"[ERROR] {name}: {e}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("SUCCESS: All checks passed!")
        print("The database warmup coroutine error has been fixed.")
    else:
        print("FAILURE: Some checks failed.")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
