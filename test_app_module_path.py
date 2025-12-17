"""
Test script to verify the app module path structure.

Requirements from Issue #4: APP MODULE PATH CHECK
- Project must have backend/app/ directory
- backend/app/ must contain __init__.py
- backend/app/ must contain main.py
- main.py must contain app = FastAPI()
"""
import os
import sys


def test_backend_directory_exists():
    """Test that backend/ directory exists."""
    print("Testing backend/ directory exists...")
    backend_path = os.path.join(os.path.dirname(__file__), "backend")
    assert os.path.exists(backend_path), "backend/ directory does not exist"
    assert os.path.isdir(backend_path), "backend/ is not a directory"
    print("✓ backend/ directory exists")
    return True


def test_app_directory_exists():
    """Test that backend/app/ directory exists."""
    print("\nTesting backend/app/ directory exists...")
    app_path = os.path.join(os.path.dirname(__file__), "backend", "app")
    assert os.path.exists(app_path), "backend/app/ directory does not exist"
    assert os.path.isdir(app_path), "backend/app/ is not a directory"
    print("✓ backend/app/ directory exists")
    return True


def test_init_file_exists():
    """Test that backend/app/__init__.py exists."""
    print("\nTesting backend/app/__init__.py exists...")
    init_path = os.path.join(os.path.dirname(__file__), "backend", "app", "__init__.py")
    assert os.path.exists(init_path), "backend/app/__init__.py does not exist"
    assert os.path.isfile(init_path), "backend/app/__init__.py is not a file"
    print("✓ backend/app/__init__.py exists")
    return True


def test_main_file_exists():
    """Test that backend/app/main.py exists."""
    print("\nTesting backend/app/main.py exists...")
    main_path = os.path.join(os.path.dirname(__file__), "backend", "app", "main.py")
    assert os.path.exists(main_path), "backend/app/main.py does not exist"
    assert os.path.isfile(main_path), "backend/app/main.py is not a file"
    print("✓ backend/app/main.py exists")
    return True


def test_main_contains_fastapi_app():
    """Test that main.py contains app = FastAPI()."""
    print("\nTesting main.py contains 'app = FastAPI()'...")
    main_path = os.path.join(os.path.dirname(__file__), "backend", "app", "main.py")
    
    with open(main_path, 'r') as f:
        lines = f.readlines()
    
    # Look for the exact pattern: app = FastAPI( at the beginning of a line (excluding whitespace)
    found = False
    matched_line = None
    for line in lines:
        stripped = line.strip()
        # Must start with 'app = FastAPI(' to avoid false positives
        if stripped.startswith('app = FastAPI('):
            found = True
            matched_line = stripped
            break
    
    assert found, \
        "main.py does not contain 'app = FastAPI()' at the beginning of a line"
    
    print("✓ main.py contains 'app = FastAPI()'")
    if matched_line:
        # Show first 60 chars of the matched line
        display_line = matched_line if len(matched_line) <= 60 else matched_line[:57] + "..."
        print(f"  Found: {display_line}")
    return True


def test_complete_structure():
    """Test the complete structure matches requirements."""
    print("\nVerifying complete structure...")
    
    base_path = os.path.dirname(__file__)
    expected_structure = {
        "backend": True,
        "backend/app": True,
        "backend/app/__init__.py": True,
        "backend/app/main.py": True,
    }
    
    for path_str, should_exist in expected_structure.items():
        full_path = os.path.join(base_path, *path_str.split('/'))
        exists = os.path.exists(full_path)
        assert exists == should_exist, \
            f"Path '{path_str}' existence mismatch: expected {should_exist}, got {exists}"
        print(f"  ✓ {path_str}")
    
    print("\n✓ Complete structure verified")
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("APP MODULE PATH CHECK - Structure Validation Test")
    print("=" * 70)
    print("\nRequirements:")
    print("  1. backend/ directory must exist")
    print("  2. backend/app/ directory must exist")
    print("  3. backend/app/__init__.py must exist")
    print("  4. backend/app/main.py must exist")
    print("  5. main.py must contain 'app = FastAPI()'")
    print("=" * 70)
    
    try:
        # Run all tests - each test will raise AssertionError if it fails
        test_backend_directory_exists()
        test_app_directory_exists()
        test_init_file_exists()
        test_main_file_exists()
        test_main_contains_fastapi_app()
        test_complete_structure()
        
        # If we reach here, all tests passed
        print("\n" + "=" * 70)
        if True:
            print("✓ ALL TESTS PASSED!")
            print("=" * 70)
            print("\nProject structure meets all requirements:")
            print("  backend/")
            print("   └── app/")
            print("       ├── main.py (contains app = FastAPI())")
            print("       └── __init__.py")
            print("=" * 70)
            sys.exit(0)
        else:
            print("✗ SOME TESTS FAILED")
            print("=" * 70)
            sys.exit(1)
            
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        print("=" * 70)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)
