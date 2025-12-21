import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text


def _init_test_db(tmp_path: Path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path/'auth.db'}"
    import api.index as api_index

    api_index.engine = None
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


@pytest.mark.parametrize("username,password", [("alice", "SuperSecret123!")])
def test_register_and_login_flow(tmp_path, username, password):
    api_index, engine = _init_test_db(tmp_path)
    client = TestClient(api_index.app)

    register_resp = client.post(
        "/api/auth/register", json={"username": username, "password": password}
    )
    assert register_resp.status_code == 200
    assert register_resp.json()["status"] == "success"

    duplicate_resp = client.post(
        "/api/auth/register", json={"username": username, "password": password}
    )
    assert duplicate_resp.status_code == 400

    login_resp = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data.get("token_type") == "bearer"

    bad_login_resp = client.post(
        "/api/auth/login", json={"username": username, "password": "wrong-password"}
    )
    assert bad_login_resp.status_code == 401

    engine.dispose()
    api_index.engine = None
