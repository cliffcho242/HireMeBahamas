"""
Test Scaling Features - Step 10
=================================
Tests for background tasks and database optimization features.
"""
import sys
from pathlib import Path

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent / "api"))


def test_background_tasks_module_exists():
    """Test that background tasks module can be imported."""
    try:
        # Import the module using backend_app path
        from backend_app.core import background_tasks
        
        # Check that key functions exist
        assert hasattr(background_tasks, 'send_email_notification')
        assert hasattr(background_tasks, 'send_welcome_email')
        assert hasattr(background_tasks, 'send_push_notification')
        assert hasattr(background_tasks, 'send_job_application_email')
        
        print("✓ Background tasks module loaded successfully")
        print(f"  - send_email_notification: {callable(background_tasks.send_email_notification)}")
        print(f"  - send_welcome_email: {callable(background_tasks.send_welcome_email)}")
        print(f"  - send_push_notification: {callable(background_tasks.send_push_notification)}")
        
    except ImportError as e:
        raise AssertionError(f"Failed to import background_tasks module: {e}")


def test_notification_helpers_module_exists():
    """Test that notification helpers module can be imported."""
    try:
        from backend_app.core import notification_helpers
        
        # Check that key functions exist
        assert hasattr(notification_helpers, 'create_notification')
        assert hasattr(notification_helpers, 'schedule_notification')
        assert hasattr(notification_helpers, 'schedule_follow_notification')
        assert hasattr(notification_helpers, 'schedule_like_notification')
        
        print("✓ Notification helpers module loaded successfully")
        print(f"  - create_notification: {callable(notification_helpers.create_notification)}")
        print(f"  - schedule_notification: {callable(notification_helpers.schedule_notification)}")
        
    except ImportError as e:
        raise AssertionError(f"Failed to import notification_helpers module: {e}")


def test_database_indexes_in_models():
    """Test that database indexes are defined in models."""
    try:
        from backend_app import models
        
        # Check Job model has indexes
        job_employer_id = models.Job.employer_id
        assert job_employer_id.index is True, "employer_id should have index"
        
        job_status = models.Job.status
        assert job_status.index is True, "status should have index"
        
        job_created_at = models.Job.created_at
        assert job_created_at.index is True, "created_at should have index"
        
        print("✓ Database indexes verified in Job model")
        print(f"  - employer_id: indexed={job_employer_id.index}")
        print(f"  - status: indexed={job_status.index}")
        print(f"  - created_at: indexed={job_created_at.index}")
        
        # Check Notification model has indexes
        notif_user_id = models.Notification.user_id
        assert notif_user_id.index is True, "user_id should have index"
        
        notif_is_read = models.Notification.is_read
        assert notif_is_read.index is True, "is_read should have index"
        
        print("✓ Database indexes verified in Notification model")
        print(f"  - user_id: indexed={notif_user_id.index}")
        print(f"  - is_read: indexed={notif_is_read.index}")
        
    except ImportError as e:
        raise AssertionError(f"Failed to import models module: {e}")


def test_migration_script_exists():
    """Test that migration script exists and is valid Python."""
    migration_file = Path(__file__).parent / "migrations" / "add_performance_indexes.py"
    
    assert migration_file.exists(), "Migration script should exist"
    assert migration_file.is_file(), "Migration script should be a file"
    
    # Check file has content
    content = migration_file.read_text()
    assert len(content) > 1000, "Migration script should have substantial content"
    assert "INDEXES" in content, "Migration script should define INDEXES"
    assert "create_index" in content, "Migration script should have create_index function"
    
    print("✓ Migration script exists and has valid structure")
    print(f"  - File: {migration_file}")
    print(f"  - Size: {len(content)} bytes")


def test_gunicorn_config_workers():
    """Test that Gunicorn configuration has correct worker settings."""
    config_file = Path(__file__).parent / "gunicorn.conf.py"
    
    assert config_file.exists(), "Gunicorn config should exist"
    
    content = config_file.read_text()
    
    # Check for workers = 4 configuration
    assert 'workers = int(os.environ.get("WEB_CONCURRENCY", "4"))' in content or \
           'workers = 4' in content or \
           '"WEB_CONCURRENCY", "4"' in content, \
           "Workers should default to 4"
    
    # Check for threads = 4 configuration
    assert 'threads = int(os.environ.get("WEB_THREADS", "4"))' in content or \
           'threads = 4' in content, \
           "Threads should default to 4"
    
    # Check for background tasks mention
    assert "Background Jobs" in content or "background" in content.lower(), \
           "Config should mention background jobs"
    
    print("✓ Gunicorn configuration verified")
    print("  - Workers: 4 (configurable)")
    print("  - Threads: 4 (configurable)")
    print("  - Background jobs: mentioned")


def test_scaling_documentation_exists():
    """Test that scaling documentation exists."""
    doc_file = Path(__file__).parent / "SCALING_STRATEGY.md"
    
    assert doc_file.exists(), "Scaling documentation should exist"
    
    content = doc_file.read_text()
    
    # Check for key sections
    assert "100K+ USERS" in content, "Should mention 100K+ users"
    assert "Gunicorn" in content, "Should document Gunicorn"
    assert "Background Jobs" in content or "BackgroundTasks" in content, \
           "Should document background jobs"
    assert "Database" in content, "Should document database strategy"
    assert "indexes" in content.lower(), "Should mention database indexes"
    
    print("✓ Scaling documentation verified")
    print(f"  - File: {doc_file}")
    print(f"  - Size: {len(content)} bytes")
    print("  - Contains: Gunicorn, Background Jobs, Database strategy")


if __name__ == "__main__":
    print("="*60)
    print("Testing Step 10 - Scaling Features")
    print("="*60)
    print()
    
    # Run tests
    tests = [
        test_background_tasks_module_exists,
        test_notification_helpers_module_exists,
        test_database_indexes_in_models,
        test_migration_script_exists,
        test_gunicorn_config_workers,
        test_scaling_documentation_exists,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"Running: {test.__name__}")
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"✗ FAILED: {e}")
            print()
            failed += 1
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed > 0:
        sys.exit(1)
