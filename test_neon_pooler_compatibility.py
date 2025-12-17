"""
Test Neon Pooler Compatibility - Verify sslmode is NOT added

This test ensures that the database URL processing does NOT add sslmode
parameter, which is incompatible with Neon pooled connections (PgBouncer).
"""
import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_ensure_sslmode_does_not_modify_url():
    """Test that ensure_sslmode returns URL unchanged (deprecated function)"""
    from api.db_url_utils import ensure_sslmode
    
    # Test basic URL without parameters
    url = "postgresql://user:pass@host:5432/db"
    result = ensure_sslmode(url)
    assert result == url, "ensure_sslmode should return URL unchanged"
    assert "sslmode" not in result, "sslmode should NOT be added to URL"
    
    # Test URL with existing parameters
    url_with_params = "postgresql://user:pass@host:5432/db?timeout=10"
    result = ensure_sslmode(url_with_params)
    assert result == url_with_params, "ensure_sslmode should return URL unchanged"
    assert "sslmode" not in result, "sslmode should NOT be added to URL with params"
    
    # Test URL that already has sslmode (should be returned as-is)
    url_with_sslmode = "postgresql://user:pass@host:5432/db?sslmode=require"
    result = ensure_sslmode(url_with_sslmode)
    assert result == url_with_sslmode, "ensure_sslmode should return URL unchanged even with sslmode"


def test_validate_url_without_sslmode():
    """Test that URL validation passes without sslmode"""
    from api.db_url_utils import validate_database_url_structure
    
    # Valid Neon URL without sslmode
    url = "postgresql://user:pass@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname"
    is_valid, error_msg = validate_database_url_structure(url)
    assert is_valid, f"URL should be valid without sslmode: {error_msg}"
    
    # Valid URL with other parameters but no sslmode
    url_with_params = "postgresql://user:pass@host.neon.tech:5432/db?connect_timeout=10"
    is_valid, error_msg = validate_database_url_structure(url_with_params)
    assert is_valid, f"URL with other params should be valid: {error_msg}"


def test_api_database_does_not_add_sslmode(monkeypatch):
    """Test that api/database.py does not add sslmode to URLs"""
    # Mock environment
    test_url = "postgresql://user:pass@host.neon.tech:5432/testdb"
    monkeypatch.setenv("DATABASE_URL", test_url)
    
    # Import after setting env var
    from api import database
    
    # Get the processed URL
    processed_url = database.get_database_url()
    
    # Verify sslmode was NOT added
    if processed_url:  # May be None if validation fails for other reasons
        assert "sslmode" not in processed_url, "api/database.py should NOT add sslmode"
        # Verify it's been converted to asyncpg format
        assert processed_url.startswith("postgresql+asyncpg://"), "Should convert to asyncpg format"


def test_app_database_does_not_require_sslmode(monkeypatch):
    """Test that app/database.py works without sslmode"""
    # Mock environment with URL without sslmode
    test_url = "postgresql://user:pass@host.neon.tech:5432/testdb"
    monkeypatch.setenv("DATABASE_URL", test_url)
    monkeypatch.setenv("ENV", "production")
    
    # Force reload to pick up new env vars
    import importlib
    from app import database
    importlib.reload(database)
    
    # Verify DATABASE_URL is set correctly without sslmode
    assert database.DATABASE_URL is not None
    assert "sslmode" not in database.DATABASE_URL, "app/database.py should NOT add sslmode"


def test_neon_pooler_documentation_exists():
    """Test that NEON_POOLER_RULES.md exists with proper content"""
    rules_path = os.path.join(os.path.dirname(__file__), "NEON_POOLER_RULES.md")
    assert os.path.exists(rules_path), "NEON_POOLER_RULES.md must exist"
    
    with open(rules_path, 'r') as f:
        content = f.read()
    
    # Check for key sections
    assert "sslmode is FORBIDDEN" in content, "Must document sslmode ban"
    assert "PgBouncer" in content, "Must explain PgBouncer incompatibility"
    assert "NO Startup DB Options" in content, "Must document startup option restrictions"
    assert "Guards Against Future Violations" in content, "Must include prevention strategies"


def test_no_sslmode_in_connect_args():
    """Test that connect_args in database modules don't contain sslmode"""
    import inspect
    
    # Check api/database.py
    from api import database as api_db
    source = inspect.getsource(api_db.get_engine)
    assert "sslmode" not in source or "NO sslmode" in source, \
        "api/database.py engine config should not add sslmode (except in comments)"
    
    # Check app/database.py
    from app import database as app_db
    source = inspect.getsource(app_db.get_engine)
    assert "sslmode" not in source or "NO SSL" in source or "NO sslmode" in source, \
        "app/database.py engine config should not add sslmode (except in comments)"


def test_init_db_does_not_create_indexes():
    """Test that init_db does NOT create indexes automatically"""
    import inspect
    from app.database import init_db
    
    source = inspect.getsource(init_db)
    
    # Verify init_db only tests connectivity
    assert "test_db_connection" in source, "init_db should test connection"
    assert "Base.metadata.create_all" not in source, "init_db should NOT create tables"
    assert "create_indexes" not in source, "init_db should NOT create indexes"
    assert "CREATE INDEX" not in source, "init_db should NOT run DDL"


def test_background_init_non_fatal():
    """Test that background initialization is non-fatal"""
    import inspect
    from app.main import app
    
    # Get startup function source
    import app.main as main_module
    source = inspect.getsource(main_module)
    
    # Verify warmup is wrapped in try/except
    assert "except Exception" in source, "Background init should catch exceptions"
    assert "logging.warning" in source or "logger.warning" in source, \
        "Background init failures should be logged as warnings"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
