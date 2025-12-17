"""
Tests for Safe Database Retry Logic

This test suite validates the db_retry decorator and retry_db_operation function,
ensuring they work correctly for idempotent read operations and follow safety rules.

Test Coverage:
- Successful execution without errors
- Retry on transient failures
- Maximum retry limit enforcement
- Delay between retries
- Logging of retry attempts
- Both decorator and function-based usage

Author: Copilot
Date: December 2025
"""

import pytest
import time
import logging
from unittest.mock import Mock, patch, call
from backend.app.core.db_retry import db_retry, retry_db_operation


class TestDbRetryDecorator:
    """Test suite for the db_retry decorator."""
    
    def test_successful_execution_no_retry(self):
        """Test that successful operations don't trigger retries."""
        # Create a mock function that succeeds on first call
        mock_func = Mock(return_value="success")
        
        # Decorate the mock function
        decorated_func = db_retry(mock_func, retries=3, delay=0.1)
        
        # Execute the function
        result = decorated_func()
        
        # Assert function was called exactly once (no retries)
        assert mock_func.call_count == 1
        assert result == "success"
    
    def test_retry_on_exception(self):
        """Test that function retries on exception."""
        # Create a mock that fails twice then succeeds
        mock_func = Mock(side_effect=[
            Exception("First failure"),
            Exception("Second failure"),
            "success"
        ])
        
        # Decorate with retry logic
        decorated_func = db_retry(mock_func, retries=3, delay=0.01)
        
        # Execute the function
        result = decorated_func()
        
        # Assert function was called 3 times (2 failures + 1 success)
        assert mock_func.call_count == 3
        assert result == "success"
    
    def test_max_retries_exceeded(self):
        """Test that exception is raised after max retries."""
        # Create a mock that always fails
        mock_func = Mock(side_effect=Exception("Persistent failure"))
        
        # Decorate with limited retries
        decorated_func = db_retry(mock_func, retries=3, delay=0.01)
        
        # Execute and expect exception
        with pytest.raises(Exception, match="Persistent failure"):
            decorated_func()
        
        # Assert function was called exactly 3 times (all failures)
        assert mock_func.call_count == 3
    
    def test_delay_between_retries(self):
        """Test that there is a delay between retry attempts."""
        # Create a mock that fails twice then succeeds
        call_times = []
        
        def failing_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("Temporary failure")
            return "success"
        
        # Decorate with retry logic and 0.1s delay
        decorated_func = db_retry(failing_func, retries=3, delay=0.1)
        
        # Execute the function
        result = decorated_func()
        
        # Assert we got success
        assert result == "success"
        assert len(call_times) == 3
        
        # Check delays between attempts (should be ~0.1s each)
        # Allow some tolerance for timing
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        assert 0.08 <= delay1 <= 0.15, f"First delay was {delay1}s, expected ~0.1s"
        assert 0.08 <= delay2 <= 0.15, f"Second delay was {delay2}s, expected ~0.1s"
    
    def test_logging_on_retry(self, caplog):
        """Test that retry attempts are logged."""
        # Set up logging capture
        caplog.set_level(logging.WARNING)
        
        # Create a mock that fails twice then succeeds
        mock_func = Mock(side_effect=[
            Exception("First failure"),
            Exception("Second failure"),
            "success"
        ])
        
        # Decorate with retry logic
        decorated_func = db_retry(mock_func, retries=3, delay=0.01)
        
        # Execute the function
        result = decorated_func()
        
        # Assert we got success
        assert result == "success"
        
        # Check that warnings were logged
        assert len(caplog.records) >= 2
        
        # Verify log messages contain attempt numbers
        log_messages = [record.message for record in caplog.records]
        assert any("attempt 1/3" in msg.lower() for msg in log_messages)
        assert any("attempt 2/3" in msg.lower() for msg in log_messages)
    
    def test_decorator_without_parameters(self):
        """Test using @db_retry without parameters."""
        # Test the default parameter syntax
        @db_retry
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"
    
    def test_decorator_with_parameters(self):
        """Test using @db_retry(retries=..., delay=...) syntax."""
        call_count = {"count": 0}
        
        @db_retry(retries=2, delay=0.01)
        def test_func():
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise Exception("Retry me")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert call_count["count"] == 2
    
    def test_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""
        @db_retry(retries=3, delay=0.1)
        def my_function():
            """My function docstring."""
            return "result"
        
        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My function docstring."
    
    def test_with_function_arguments(self):
        """Test that decorator works with functions that take arguments."""
        mock_func = Mock(return_value="success")
        decorated_func = db_retry(mock_func, retries=3, delay=0.01)
        
        # Call with various arguments
        result = decorated_func(1, 2, key="value")
        
        # Assert function received the arguments correctly
        assert result == "success"
        mock_func.assert_called_once_with(1, 2, key="value")
    
    def test_different_exception_types(self):
        """Test retry works with different exception types."""
        # Test with different exception types
        for exception_type in [ValueError, RuntimeError, ConnectionError]:
            mock_func = Mock(side_effect=[
                exception_type("error"),
                "success"
            ])
            
            decorated_func = db_retry(mock_func, retries=3, delay=0.01)
            result = decorated_func()
            
            assert result == "success"
            assert mock_func.call_count == 2
            mock_func.reset_mock()


class TestRetryDbOperation:
    """Test suite for the retry_db_operation function."""
    
    def test_successful_execution(self):
        """Test successful execution without retry."""
        mock_func = Mock(return_value="success")
        
        result = retry_db_operation(mock_func, retries=3, delay=0.01)
        
        assert mock_func.call_count == 1
        assert result == "success"
    
    def test_retry_on_failure(self):
        """Test retry on transient failure."""
        mock_func = Mock(side_effect=[
            Exception("Failure"),
            "success"
        ])
        
        result = retry_db_operation(mock_func, retries=3, delay=0.01)
        
        assert mock_func.call_count == 2
        assert result == "success"
    
    def test_max_retries_exceeded(self):
        """Test exception raised after max retries."""
        mock_func = Mock(side_effect=Exception("Persistent failure"))
        
        with pytest.raises(Exception, match="Persistent failure"):
            retry_db_operation(mock_func, retries=3, delay=0.01)
        
        assert mock_func.call_count == 3
    
    def test_with_arguments(self):
        """Test passing arguments to the operation."""
        mock_func = Mock(return_value="success")
        
        result = retry_db_operation(
            mock_func,
            1, 2, 3,
            retries=3,
            delay=0.01,
            key="value"
        )
        
        assert result == "success"
        mock_func.assert_called_once_with(1, 2, 3, key="value")
    
    def test_lambda_operation(self):
        """Test with lambda function."""
        counter = {"value": 0}
        
        def operation():
            counter["value"] += 1
            if counter["value"] < 2:
                raise Exception("Retry needed")
            return "success"
        
        result = retry_db_operation(operation, retries=3, delay=0.01)
        
        assert result == "success"
        assert counter["value"] == 2
    
    def test_logging_on_retry(self, caplog):
        """Test that retry attempts are logged."""
        caplog.set_level(logging.WARNING)
        
        mock_func = Mock(side_effect=[
            Exception("First failure"),
            "success"
        ])
        
        result = retry_db_operation(mock_func, retries=3, delay=0.01)
        
        assert result == "success"
        assert len(caplog.records) >= 1
        assert any("attempt 1/3" in record.message.lower() for record in caplog.records)


class TestSafetyAndBestPractices:
    """Test suite for safety rules and best practices documentation."""
    
    def test_module_has_safety_documentation(self):
        """Test that module docstring contains safety warnings."""
        from backend.app.core import db_retry as module
        
        docstring = module.__doc__
        assert docstring is not None
        
        # Check for key safety concepts in documentation
        assert "idempotent" in docstring.lower()
        assert "read" in docstring.lower()
        assert "never" in docstring.lower() or "not" in docstring.lower()
        assert "write" in docstring.lower()
    
    def test_decorator_has_usage_examples(self):
        """Test that decorator docstring contains usage examples."""
        docstring = db_retry.__doc__
        assert docstring is not None
        
        # Check for usage examples
        assert "example" in docstring.lower()
        assert "@db_retry" in docstring
    
    def test_retry_db_operation_has_examples(self):
        """Test that function has usage examples."""
        docstring = retry_db_operation.__doc__
        assert docstring is not None
        
        # Check for usage examples
        assert "example" in docstring.lower()
        assert "retry_db_operation" in docstring


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    def test_zero_retries(self):
        """Test behavior with zero retries."""
        mock_func = Mock(side_effect=Exception("Immediate failure"))
        
        decorated_func = db_retry(mock_func, retries=1, delay=0.01)
        
        with pytest.raises(Exception, match="Immediate failure"):
            decorated_func()
        
        # Should be called exactly once (no retries with retries=1)
        assert mock_func.call_count == 1
    
    def test_very_small_delay(self):
        """Test with very small delay (performance test)."""
        mock_func = Mock(side_effect=[
            Exception("Error"),
            "success"
        ])
        
        start_time = time.time()
        decorated_func = db_retry(mock_func, retries=3, delay=0.001)
        result = decorated_func()
        elapsed = time.time() - start_time
        
        assert result == "success"
        # Should complete quickly (within 0.1 seconds)
        assert elapsed < 0.1
    
    def test_return_none(self):
        """Test that None can be returned successfully."""
        mock_func = Mock(return_value=None)
        decorated_func = db_retry(mock_func, retries=3, delay=0.01)
        
        result = decorated_func()
        
        assert result is None
        assert mock_func.call_count == 1
    
    def test_return_complex_objects(self):
        """Test that complex objects can be returned."""
        complex_result = {
            "data": [1, 2, 3],
            "nested": {"key": "value"},
            "tuple": (1, 2)
        }
        
        mock_func = Mock(return_value=complex_result)
        decorated_func = db_retry(mock_func, retries=3, delay=0.01)
        
        result = decorated_func()
        
        assert result == complex_result
        assert result is complex_result  # Should be same object


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
