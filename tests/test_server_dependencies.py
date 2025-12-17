"""
Test suite to verify critical server dependencies are properly installed.
This prevents random deployment errors from missing gunicorn, uvicorn, or fastapi.

These tests ensure:
1. gunicorn, uvicorn, and fastapi are installed
2. Versions meet minimum requirements
3. Modules can be imported successfully
4. Basic functionality works as expected
"""

import importlib.metadata
import pytest
import sys


class TestServerDependencies:
    """Test critical server dependencies for deployment."""
    
    def test_gunicorn_installed(self):
        """Verify gunicorn is installed with correct version."""
        try:
            version = importlib.metadata.version("gunicorn")
            assert version is not None, "gunicorn version should not be None"
            # Check minimum version (23.0.0)
            major, minor, patch = map(int, version.split('.')[:3])
            assert major >= 23, f"gunicorn version {version} is below minimum 23.0.0"
            print(f"✅ gunicorn {version} is installed")
        except importlib.metadata.PackageNotFoundError:
            pytest.fail("❌ CRITICAL: gunicorn is NOT installed - deployment will fail!")
    
    def test_uvicorn_installed(self):
        """Verify uvicorn is installed with correct version."""
        try:
            version = importlib.metadata.version("uvicorn")
            assert version is not None, "uvicorn version should not be None"
            # Check minimum version (0.31.0)
            major, minor, patch = map(int, version.split('.')[:3])
            assert minor >= 31, f"uvicorn version {version} is below minimum 0.31.0"
            print(f"✅ uvicorn {version} is installed")
        except importlib.metadata.PackageNotFoundError:
            pytest.fail("❌ CRITICAL: uvicorn is NOT installed - deployment will fail!")
    
    def test_fastapi_installed(self):
        """Verify fastapi is installed with correct version."""
        try:
            version = importlib.metadata.version("fastapi")
            assert version is not None, "fastapi version should not be None"
            # Check minimum version (0.115.0)
            major, minor, patch = map(int, version.split('.')[:3])
            assert minor >= 115, f"fastapi version {version} is below minimum 0.115.0"
            print(f"✅ fastapi {version} is installed")
        except importlib.metadata.PackageNotFoundError:
            pytest.fail("❌ CRITICAL: fastapi is NOT installed - deployment will fail!")
    
    def test_gunicorn_import(self):
        """Verify gunicorn module can be imported."""
        try:
            import gunicorn
            assert hasattr(gunicorn, '__version__'), "gunicorn should have __version__ attribute"
            print("✅ gunicorn module imports successfully")
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: gunicorn cannot be imported: {e}")
    
    def test_uvicorn_import(self):
        """Verify uvicorn module can be imported."""
        try:
            import uvicorn
            assert hasattr(uvicorn, 'run'), "uvicorn should have run() function"
            print("✅ uvicorn module imports successfully")
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: uvicorn cannot be imported: {e}")
    
    def test_fastapi_import(self):
        """Verify fastapi module can be imported."""
        try:
            import fastapi
            assert hasattr(fastapi, 'FastAPI'), "fastapi should have FastAPI class"
            print("✅ fastapi module imports successfully")
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: fastapi cannot be imported: {e}")
    
    def test_fastapi_app_creation(self):
        """Verify a basic FastAPI app can be created."""
        try:
            from fastapi import FastAPI
            app = FastAPI()
            assert app is not None, "FastAPI app should be created"
            print("✅ FastAPI app creation works")
        except Exception as e:
            pytest.fail(f"❌ CRITICAL: Cannot create FastAPI app: {e}")
    
    def test_uvicorn_config(self):
        """Verify uvicorn Config class is available."""
        try:
            from uvicorn.config import Config
            assert Config is not None, "uvicorn.config.Config should be available"
            print("✅ uvicorn Config class is available")
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: Cannot import uvicorn.config: {e}")
    
    def test_gunicorn_workers(self):
        """Verify gunicorn workers module is available."""
        try:
            from gunicorn.workers import base
            assert base is not None, "gunicorn.workers.base should be available"
            print("✅ gunicorn workers module is available")
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: Cannot import gunicorn.workers: {e}")


class TestDependencyConsistency:
    """Test that all requirements files have consistent versions."""
    
    def test_requirements_files_have_gunicorn(self):
        """Verify all requirements.txt files include gunicorn."""
        import os
        from pathlib import Path
        
        repo_root = Path(__file__).parent.parent
        requirements_files = [
            "requirements.txt",
            "requirements_immortal.txt",
            "requirements-psycopg.txt",
            "backend/requirements.txt",
            "backend/requirements_bulletproof.txt",
            "api/requirements.txt",
        ]
        
        for req_file in requirements_files:
            req_path = repo_root / req_file
            if req_path.exists():
                content = req_path.read_text()
                assert "gunicorn" in content, f"❌ {req_file} is missing gunicorn!"
                print(f"✅ {req_file} includes gunicorn")
    
    def test_requirements_files_have_uvicorn(self):
        """Verify all requirements.txt files include uvicorn."""
        import os
        from pathlib import Path
        
        repo_root = Path(__file__).parent.parent
        requirements_files = [
            "requirements.txt",
            "requirements_immortal.txt",
            "requirements-psycopg.txt",
            "backend/requirements.txt",
            "backend/requirements_bulletproof.txt",
            "api/requirements.txt",
        ]
        
        for req_file in requirements_files:
            req_path = repo_root / req_file
            if req_path.exists():
                content = req_path.read_text()
                assert "uvicorn" in content, f"❌ {req_file} is missing uvicorn!"
                print(f"✅ {req_file} includes uvicorn")
    
    def test_requirements_files_have_fastapi(self):
        """Verify all requirements.txt files include fastapi."""
        import os
        from pathlib import Path
        
        repo_root = Path(__file__).parent.parent
        requirements_files = [
            "requirements.txt",
            "requirements_immortal.txt",
            "requirements-psycopg.txt",
            "backend/requirements.txt",
            "backend/requirements_bulletproof.txt",
            "api/requirements.txt",
        ]
        
        for req_file in requirements_files:
            req_path = repo_root / req_file
            if req_path.exists():
                content = req_path.read_text()
                assert "fastapi" in content, f"❌ {req_file} is missing fastapi!"
                print(f"✅ {req_file} includes fastapi")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
