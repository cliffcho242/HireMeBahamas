"""Test that return_db_connection properly rolls back aborted transactions.

This test verifies the fix for the PostgreSQL error:
"ERROR: current transaction is aborted, commands ignored until end of transaction block"

The issue occurs when a query fails within a transaction, leaving the connection
in an aborted state. Without a rollback, subsequent queries on that connection
will fail until the transaction is properly rolled back.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestReturnDbConnectionRollback:
    """Tests for return_db_connection rollback behavior."""

    def test_rollback_called_for_postgresql_connections(self):
        """Test that rollback is called when returning PostgreSQL connections."""
        with patch('final_backend_postgresql.USE_POSTGRESQL', True):
            with patch('final_backend_postgresql._get_connection_pool') as mock_pool:
                from final_backend_postgresql import return_db_connection
                
                # Create a mock connection
                mock_conn = Mock()
                mock_conn.rollback = Mock()
                
                # Create a mock pool
                mock_pool_instance = Mock()
                mock_pool.return_value = mock_pool_instance
                
                # Call return_db_connection
                return_db_connection(mock_conn)
                
                # Verify rollback was called
                mock_conn.rollback.assert_called_once()
                # Verify connection was returned to pool
                mock_pool_instance.putconn.assert_called_once_with(mock_conn)

    def test_connection_discarded_when_rollback_fails(self):
        """Test that connection is discarded if rollback fails."""
        with patch('final_backend_postgresql.USE_POSTGRESQL', True):
            with patch('final_backend_postgresql._get_connection_pool') as mock_pool:
                from final_backend_postgresql import return_db_connection
                
                # Create a mock connection where rollback raises an exception
                mock_conn = Mock()
                mock_conn.rollback = Mock(side_effect=Exception("Connection broken"))
                mock_conn.close = Mock()
                
                # Call return_db_connection
                return_db_connection(mock_conn)
                
                # Verify rollback was attempted
                mock_conn.rollback.assert_called_once()
                # Verify connection was closed (not returned to pool)
                mock_conn.close.assert_called_once()

    def test_none_connection_handled_gracefully(self):
        """Test that None connection is handled without error."""
        from final_backend_postgresql import return_db_connection
        
        # Should not raise any exception
        return_db_connection(None)

    def test_discard_true_skips_pool_return(self):
        """Test that discard=True causes connection to be closed, not pooled."""
        with patch('final_backend_postgresql.USE_POSTGRESQL', True):
            with patch('final_backend_postgresql._get_connection_pool') as mock_pool:
                from final_backend_postgresql import return_db_connection
                
                # Create a mock connection
                mock_conn = Mock()
                mock_conn.rollback = Mock()
                mock_conn.close = Mock()
                
                # Create a mock pool
                mock_pool_instance = Mock()
                mock_pool.return_value = mock_pool_instance
                
                # Call return_db_connection with discard=True
                return_db_connection(mock_conn, discard=True)
                
                # Verify rollback was called
                mock_conn.rollback.assert_called_once()
                # Verify connection was NOT returned to pool
                mock_pool_instance.putconn.assert_not_called()
                # Verify connection was closed
                mock_conn.close.assert_called_once()


class TestTransactionAbortedRecovery:
    """Tests for recovering from aborted transaction state."""

    def test_aborted_transaction_cleared_on_return(self):
        """
        Simulate the scenario where a connection has an aborted transaction
        and verify that rollback clears it for reuse.
        """
        # This is a conceptual test - in real scenario, we'd need a database
        # The key behavior is that rollback() is called before pool return
        
        with patch('final_backend_postgresql.USE_POSTGRESQL', True):
            with patch('final_backend_postgresql._get_connection_pool') as mock_pool:
                from final_backend_postgresql import return_db_connection
                
                # Create a connection that simulates aborted transaction state
                mock_conn = Mock()
                mock_conn.rollback = Mock()
                
                # Create a mock pool
                mock_pool_instance = Mock()
                mock_pool.return_value = mock_pool_instance
                
                # Return connection to pool
                return_db_connection(mock_conn)
                
                # Verify rollback was called to clear any aborted transaction
                mock_conn.rollback.assert_called_once()
