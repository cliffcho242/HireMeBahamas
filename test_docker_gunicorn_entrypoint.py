"""
Verify the Dockerfile starts Gunicorn with the FastAPI app in api/index.py.
"""
from pathlib import Path


def test_dockerfile_targets_api_index():
    dockerfile = Path(__file__).parent / "Dockerfile"
    content = dockerfile.read_text()

    assert "gunicorn api.index:app" in content, (
        "Dockerfile should start Gunicorn using api.index:app"
    )
    assert "api.backend_app.main:app" not in content, (
        "Dockerfile should not reference api.backend_app.main:app"
    )


if __name__ == "__main__":
    print("Running Dockerfile Gunicorn entrypoint test...")
    test_dockerfile_targets_api_index()
    print("✅ Dockerfile Gunicorn entrypoint test passed")
