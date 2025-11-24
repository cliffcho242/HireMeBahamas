#!/usr/bin/env python3
"""
Test to verify that all required upload directories are created.
This test ensures the fix for profile picture upload issue is working.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))


def test_upload_directories_created():
    """Test that all upload directories are created when the upload module is imported"""
    from app.core.upload import UPLOAD_DIR
    
    required_directories = [
        'avatars',
        'portfolio',
        'documents',
        'profile_pictures',  # This was missing and caused the upload failure
    ]
    
    # Check that base upload directory exists
    assert os.path.exists(UPLOAD_DIR), f"Base upload directory '{UPLOAD_DIR}' does not exist"
    assert os.path.isdir(UPLOAD_DIR), f"'{UPLOAD_DIR}' is not a directory"
    
    # Check that all required subdirectories exist
    for directory in required_directories:
        dir_path = os.path.join(UPLOAD_DIR, directory)
        assert os.path.exists(dir_path), f"Upload subdirectory '{directory}' does not exist at {dir_path}"
        assert os.path.isdir(dir_path), f"'{dir_path}' is not a directory"
        
        # Verify directory is writable
        assert os.access(dir_path, os.W_OK), f"Upload directory '{directory}' is not writable"
    
    print(f"✅ All upload directories created successfully:")
    for directory in required_directories:
        print(f"   - {UPLOAD_DIR}/{directory}")


def test_profile_pictures_directory_exists():
    """Specific test for profile_pictures directory that was causing the upload failure"""
    from app.core.upload import UPLOAD_DIR
    
    profile_pictures_dir = os.path.join(UPLOAD_DIR, 'profile_pictures')
    
    assert os.path.exists(profile_pictures_dir), \
        "profile_pictures directory does not exist - this will cause upload failures!"
    assert os.path.isdir(profile_pictures_dir), \
        "profile_pictures path exists but is not a directory!"
    assert os.access(profile_pictures_dir, os.W_OK), \
        "profile_pictures directory exists but is not writable!"
    
    print(f"✅ profile_pictures directory is ready at: {profile_pictures_dir}")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Upload Directories")
    print("=" * 70)
    
    try:
        test_upload_directories_created()
        print()
        test_profile_pictures_directory_exists()
        print()
        print("=" * 70)
        print("✅ All tests passed! Upload functionality should work correctly.")
        print("=" * 70)
        sys.exit(0)
    except AssertionError as e:
        print()
        print("=" * 70)
        print(f"❌ Test failed: {e}")
        print("=" * 70)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Unexpected error: {e}")
        print("=" * 70)
        sys.exit(1)
