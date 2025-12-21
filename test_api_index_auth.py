import os
from pathlib import Path

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
import api.index as api_index
from fastapi.testclient import TestClient
from sqlalchemy import text


def _init_test_db(tmp_path: Path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path/'auth.db'}"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"

    api_index.engine = None
    api_index.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    engine = api_index.get_engine()
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.execute(
            text(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
                """
            )
        )
    return api_index, engine


def test_register_and_login_flow(tmp_path):
    api_index, engine = _init_test_db(tmp_path)
    client = TestClient(api_index.app)

    register_resp = client.post(
        "/api/auth/register", json={"username": "alice", "password": "SuperSecret123!"}
    )
    assert register_resp.status_code == 200
    assert register_resp.json()["status"] == "success"

    duplicate_resp = client.post(
        "/api/auth/register", json={"username": "alice", "password": "SuperSecret123!"}
    )
    assert duplicate_resp.status_code == 400

    login_resp = client.post(
        "/api/auth/login", json={"username": "alice", "password": "SuperSecret123!"}
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data.get("token_type") == "bearer"

    bad_login_resp = client.post(
        "/api/auth/login", json={"username": "alice", "password": "wrong-password"}
    )
    assert bad_login_resp.status_code == 401

    engine.dispose()
    api_index.engine = None
