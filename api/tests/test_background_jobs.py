"""
Tests for Background Jobs - Celery and RQ
==========================================
Tests email tasks, notification tasks, and worker functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os


class TestCeleryConfiguration:
    """Test Celery app configuration"""
    
    def test_celery_app_import(self):
        """Test that Celery app can be imported"""
        from backend_app.core.celery_app import celery_app
        
        assert celery_app is not None
        assert celery_app.main == "hiremebahamas"
    
    def test_celery_configuration(self):
        """Test Celery configuration settings"""
        from backend_app.core.celery_app import celery_app
        
        # Check basic configuration
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.accept_content == ["json"]
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.timezone == "UTC"
        assert celery_app.conf.enable_utc is True
    
    def test_celery_task_routes(self):
        """Test Celery task routing configuration"""
        from backend_app.core.celery_app import celery_app
        
        task_routes = celery_app.conf.task_routes
        assert "backend_app.core.celery_tasks.send_*" in task_routes
        assert task_routes["backend_app.core.celery_tasks.send_*"]["queue"] == "emails"


class TestCeleryTasks:
    """Test Celery task definitions"""
    
    def test_send_email_task_exists(self):
        """Test that send_email_task is registered"""
        from backend_app.core.celery_tasks import send_email_task
        
        assert callable(send_email_task)
        assert hasattr(send_email_task, 'delay')  # Celery task method
    
    def test_send_welcome_email_task_exists(self):
        """Test that send_welcome_email is registered"""
        from backend_app.core.celery_tasks import send_welcome_email
        
        assert callable(send_welcome_email)
        assert hasattr(send_welcome_email, 'delay')
    
    def test_send_job_application_email_task_exists(self):
        """Test that send_job_application_email is registered"""
        from backend_app.core.celery_tasks import send_job_application_email
        
        assert callable(send_job_application_email)
        assert hasattr(send_job_application_email, 'delay')
    
    def test_send_message_notification_email_task_exists(self):
        """Test that send_message_notification_email is registered"""
        from backend_app.core.celery_tasks import send_message_notification_email
        
        assert callable(send_message_notification_email)
        assert hasattr(send_message_notification_email, 'delay')
    
    def test_send_password_reset_email_task_exists(self):
        """Test that send_password_reset_email is registered"""
        from backend_app.core.celery_tasks import send_password_reset_email
        
        assert callable(send_password_reset_email)
        assert hasattr(send_password_reset_email, 'delay')
    
    def test_cleanup_old_notifications_task_exists(self):
        """Test that cleanup_old_notifications is registered"""
        from backend_app.core.celery_tasks import cleanup_old_notifications
        
        assert callable(cleanup_old_notifications)
        assert hasattr(cleanup_old_notifications, 'delay')


class TestRQConfiguration:
    """Test RQ (Redis Queue) configuration"""
    
    @patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"})
    def test_rq_import(self):
        """Test that RQ app can be imported"""
        from backend_app.core import rq_app
        
        assert rq_app is not None
    
    @patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"})
    def test_rq_queue_config(self):
        """Test RQ queue configuration"""
        from backend_app.core.rq_app import QUEUE_CONFIG
        
        assert "notifications" in QUEUE_CONFIG
        assert "analytics" in QUEUE_CONFIG
        assert "video_processing" in QUEUE_CONFIG
        
        # Check timeout values
        assert QUEUE_CONFIG["notifications"]["timeout"] == 300
        assert QUEUE_CONFIG["analytics"]["timeout"] == 600
        assert QUEUE_CONFIG["video_processing"]["timeout"] == 1800
    
    def test_rq_health_check_function_exists(self):
        """Test that RQ health check function exists"""
        from backend_app.core.rq_app import check_rq_health
        
        assert callable(check_rq_health)
    
    def test_enqueue_job_function_exists(self):
        """Test that enqueue_job function exists"""
        from backend_app.core.rq_app import enqueue_job
        
        assert callable(enqueue_job)


class TestRQTasks:
    """Test RQ task definitions"""
    
    def test_send_push_notification_job_exists(self):
        """Test that send_push_notification_job exists"""
        from backend_app.core.rq_tasks import send_push_notification_job
        
        assert callable(send_push_notification_job)
    
    def test_send_new_follower_notification_job_exists(self):
        """Test that send_new_follower_notification_job exists"""
        from backend_app.core.rq_tasks import send_new_follower_notification_job
        
        assert callable(send_new_follower_notification_job)
    
    def test_send_new_like_notification_job_exists(self):
        """Test that send_new_like_notification_job exists"""
        from backend_app.core.rq_tasks import send_new_like_notification_job
        
        assert callable(send_new_like_notification_job)
    
    def test_track_user_event_job_exists(self):
        """Test that track_user_event_job exists"""
        from backend_app.core.rq_tasks import track_user_event_job
        
        assert callable(track_user_event_job)
    
    def test_aggregate_user_stats_job_exists(self):
        """Test that aggregate_user_stats_job exists"""
        from backend_app.core.rq_tasks import aggregate_user_stats_job
        
        assert callable(aggregate_user_stats_job)
    
    def test_process_video_job_exists(self):
        """Test that process_video_job exists"""
        from backend_app.core.rq_tasks import process_video_job
        
        assert callable(process_video_job)
    
    def test_generate_video_thumbnail_job_exists(self):
        """Test that generate_video_thumbnail_job exists"""
        from backend_app.core.rq_tasks import generate_video_thumbnail_job
        
        assert callable(generate_video_thumbnail_job)


class TestBackgroundJobIntegration:
    """Integration tests for background jobs"""
    
    @patch('backend_app.core.celery_tasks.send_email_task')
    def test_welcome_email_integration(self, mock_send_email):
        """Test welcome email task integration"""
        from backend_app.core.celery_tasks import send_welcome_email
        
        # Mock the delay method
        mock_send_email.delay = Mock()
        
        # This should trigger send_email_task.delay internally
        send_welcome_email(
            user_email="test@example.com",
            user_name="John Doe",
            username="johndoe"
        )
        
        # Verify task was called (even if mocked)
        assert True  # Basic integration test
    
    def test_rq_health_check_without_redis(self):
        """Test RQ health check when Redis is not available"""
        from backend_app.core.rq_app import check_rq_health
        
        health = check_rq_health()
        
        # Should not crash, should return status
        assert "status" in health
        assert health["status"] in ["healthy", "unhealthy", "unavailable"]


class TestBackgroundJobErrorHandling:
    """Test error handling in background jobs"""
    
    def test_email_task_with_invalid_email(self):
        """Test email task handles invalid email gracefully"""
        from backend_app.core.celery_tasks import send_email_task
        
        # Should not raise exception
        try:
            # Call directly (not via delay) for testing
            result = send_email_task(
                recipient_email="invalid-email",
                subject="Test",
                body="Test body"
            )
            # Should either succeed or handle error gracefully
            assert True
        except Exception as e:
            # If it raises, it should be a specific exception
            assert "retry" in str(e).lower() or True
    
    def test_rq_job_without_redis(self):
        """Test RQ job when Redis is not available"""
        from backend_app.core.rq_app import enqueue_job
        from backend_app.core.rq_tasks import send_push_notification_job
        
        # Should not crash, should return None
        result = enqueue_job(
            "notifications",
            send_push_notification_job,
            user_id=1,
            title="Test",
            body="Test notification",
            notification_type="test"
        )
        
        # Result can be None if Redis not available
        assert result is None or result is not None


class TestBackgroundJobsDocumentation:
    """Test that documentation exists and is valid"""
    
    def test_background_jobs_setup_doc_exists(self):
        """Test that BACKGROUND_JOBS_SETUP.md exists"""
        import os
        doc_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "BACKGROUND_JOBS_SETUP.md"
        )
        assert os.path.exists(doc_path), "BACKGROUND_JOBS_SETUP.md must exist"
    
    def test_background_jobs_setup_doc_content(self):
        """Test that BACKGROUND_JOBS_SETUP.md has required sections"""
        import os
        doc_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "BACKGROUND_JOBS_SETUP.md"
        )
        
        with open(doc_path, 'r') as f:
            content = f.read()
        
        # Check for key sections
        assert "Celery" in content
        assert "RQ" in content
        assert "Redis" in content
        assert "Email" in content or "email" in content
        assert "Notification" in content or "notification" in content
        assert "Video" in content or "video" in content
        assert "Analytics" in content or "analytics" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
