#!/usr/bin/env python3
"""
Automated startup script for HireBahamas platform
Handles backend and frontend startup with error handling and process management
"""

import subprocess
import time
import os
import sys
import signal
import requests
import threading
from pathlib import Path

class HireBahamasLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.workspace_root = Path(__file__).parent
        self.venv_python = self.workspace_root / ".venv" / "Scripts" / "python.exe"
        self.backend_dir = self.workspace_root / "backend"
        self.frontend_dir = self.workspace_root / "frontend"
        
    def kill_existing_processes(self):
        """Kill any existing processes on ports 8005 and 3000"""
        print("🔄 Checking for existing processes...")
        
        # Kill processes on port 8005 (backend)
        try:
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if ':8005' in line and 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        print(f"✅ Killed process {pid} on port 8005")
                    except:
                        pass
        except:
            pass
            
        # Kill processes on port 3000 (frontend)
        try:
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if ':3000' in line and 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        print(f"✅ Killed process {pid} on port 3000")
                    except:
                        pass
        except:
            pass
    
    def install_backend_dependencies(self):
        """Install required backend dependencies"""
        print("📦 Installing backend dependencies...")
        deps = [
            "fastapi", "uvicorn", "python-decouple", "sqlalchemy", 
            "aiosqlite", "python-jose[cryptography]", "passlib[bcrypt]",
            "python-multipart"
        ]
        
        try:
            subprocess.run([
                str(self.venv_python), "-m", "pip", "install"
            ] + deps, check=True, cwd=self.workspace_root)
            print("✅ Backend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install backend dependencies")
            return False
        return True
    
    def create_database(self):
        """Create database tables if they don't exist"""
        print("🗄️ Setting up database...")
        try:
            # Run create_tables.py from backend directory
            subprocess.run([
                str(self.venv_python), "create_tables.py"
            ], check=True, cwd=self.backend_dir)
            print("✅ Database tables created")
        except subprocess.CalledProcessError:
            print("❌ Failed to create database tables")
            return False
        return True
    
    def create_minimal_backend(self):
        """Create a minimal backend that won't shut down"""
        print("🔧 Creating stable backend configuration...")
        
        minimal_main = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HireBahamas API",
    description="Job platform API for the Bahamas",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "HireBahamas API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HireBahamas API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Simple auth endpoint for testing
@app.post("/auth/register")
async def register():
    return {"message": "Registration endpoint - ready for implementation"}

@app.post("/auth/login")
async def login():
    return {"message": "Login endpoint - ready for implementation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)
'''
        
        # Write minimal main.py
        minimal_main_path = self.backend_dir / "app" / "minimal_main.py"
        with open(minimal_main_path, 'w') as f:
            f.write(minimal_main)
        
        print("✅ Created minimal backend configuration")
        return True
    
    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting backend server...")
        
        try:
            # Use Flask with Waitress for better stability on Windows
            self.backend_process = subprocess.Popen([
                str(self.venv_python), "-c",
                "from waitress import serve; from app.flask_backend import app; serve(app, host='0.0.0.0', port=8005)"
            ], cwd=self.backend_dir, shell=True)
            
            # Wait for backend to start
            for i in range(30):  # 30 second timeout
                try:
                    response = requests.get("http://localhost:8005/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ Backend server started successfully on http://localhost:8005")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    if i % 5 == 0:
                        print(f"⏳ Waiting for backend... ({i+1}/30)")
            
            print("❌ Backend failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def install_frontend_dependencies(self):
        """Install frontend dependencies"""
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], check=True, cwd=self.frontend_dir)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return False
        return True
    
    def start_frontend(self):
        """Start the frontend server"""
        print("🚀 Starting frontend server...")
        
        try:
            self.frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=self.frontend_dir)
            
            # Wait for frontend to start
            for i in range(30):  # 30 second timeout
                try:
                    response = requests.get("http://localhost:3000", timeout=1)
                    if response.status_code == 200:
                        print("✅ Frontend server started successfully on http://localhost:3000")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    if i % 5 == 0:
                        print(f"⏳ Waiting for frontend... ({i+1}/30)")
            
            print("❌ Frontend failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def test_connectivity(self):
        """Test that both servers are responding"""
        print("🔍 Testing server connectivity...")
        
        # Test backend
        try:
            response = requests.get("http://localhost:8005/health")
            if response.status_code == 200:
                print("✅ Backend health check passed")
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Backend connectivity failed: {e}")
        
        # Test frontend
        try:
            response = requests.get("http://localhost:3000")
            if response.status_code == 200:
                print("✅ Frontend connectivity test passed")
            else:
                print(f"❌ Frontend connectivity failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Frontend connectivity failed: {e}")
    
    def cleanup(self):
        """Clean up processes on exit"""
        print("\n🛑 Shutting down servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print("✅ Backend server stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("🔨 Backend server force-killed")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend server stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("🔨 Frontend server force-killed")
    
    def run(self):
        """Main execution method"""
        print("🎯 HireBahamas Automated Launcher Starting...")
        print("=" * 50)
        
        try:
            # Step 1: Clean up existing processes
            self.kill_existing_processes()
            
            # Step 2: Install dependencies
            if not self.install_backend_dependencies():
                return False
            
            # Step 3: Create database
            if not self.create_database():
                return False
            
            # Step 4: Create stable backend
            if not self.create_minimal_backend():
                return False
            
            # Step 5: Start backend
            if not self.start_backend():
                return False
            
            # Step 6: Install frontend dependencies
            if not self.install_frontend_dependencies():
                return False
            
            # Step 7: Start frontend
            if not self.start_frontend():
                return False
            
            # Step 8: Test connectivity
            self.test_connectivity()
            
            print("\n" + "=" * 50)
            print("🎉 HireBahamas Platform Started Successfully!")
            print("📱 Frontend: http://localhost:3000")
            print("🔧 Backend API: http://localhost:8005")
            print("📚 API Docs: http://localhost:8005/docs")
            print("💚 Health Check: http://localhost:8005/health")
            print("=" * 50)
            print("\n⏳ Servers are running. Press Ctrl+C to stop...")
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⚡ Received shutdown signal...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.cleanup()
            print("\n👋 HireBahamas Launcher stopped.")

def main():
    launcher = HireBahamasLauncher()
    
    # Setup signal handlers for clean shutdown
    def signal_handler(signum, frame):
        launcher.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    launcher.run()

if __name__ == "__main__":
    main()