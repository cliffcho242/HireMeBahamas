"""
Focused tests for the Render/Neon-safe api/index.py template.
Verifies lazy database initialization, health stability, and core routes.
"""
import importlib
import os
import sys

from fastapi.testclient import TestClient

# Ensure the api directory is on the path for importing index.py
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.join(PROJECT_ROOT, "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)


def reload_index():
    """Reload api/index.py with a clean module state."""
    if "index" in sys.modules:
        del sys.modules["index"]
    return importlib.import_module("index")


def test_health_returns_ok_plain_text():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    index = reload_index()
    client = TestClient(index.app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.text == "ok"

    head_response = client.head("/health")
    assert head_response.status_code == 200


def test_routes_lazy_load_engine():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    index = reload_index()
    index.engine = None
    client = TestClient(index.app)

    # Engine should be created on first route call
    assert index.engine is None
    login_response = client.post("/api/auth/login")
    assert login_response.status_code == 200
    assert login_response.json()["status"] == "success"
    assert index.engine is not None

    # Subsequent routes reuse the same engine
    users_response = client.get("/api/users")
    assert users_response.status_code == 200
    assert "users" in users_response.json()


def test_get_db_engine_alias():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    index = reload_index()
    index.engine = None

    # Alias should delegate to get_engine
    engine = index.get_db_engine()
    assert engine is index.engine
