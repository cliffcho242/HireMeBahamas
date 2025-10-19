#!/usr/bin/env python3
"""
HireBahamas Auto-Restart Service
Automatically restarts servers if they crash or stop responding
"""

import subprocess
import time
import requests
import sys
import os
from datetime import datetime

# Configuration
BACKEND_PORT = 8008
FRONTEND_PORT = 3000
BACKEND_SCRIPT = "clean_backend.py"
CHECK_INTERVAL = 30  # Check every 30 seconds
MAX_RESTART_ATTEMPTS = 5

class ServerMonitor:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_restart_count = 0
        self.frontend_restart_count = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_backend(self):
        """Check if backend is responding"""
        try:
            response = requests.get(f"http://127.0.0.1:{BACKEND_PORT}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def check_frontend(self):
        """Check if frontend is responding"""
        try:
            response = requests.get(f"http://localhost:{FRONTEND_PORT}", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def start_backend(self):
        """Start the backend server"""
        try:
            self.log("Starting backend server...")
            self.backend_process = subprocess.Popen(
                [sys.executable, BACKEND_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            time.sleep(5)  # Wait for server to start
            
            if self.check_backend():
                self.log("✅ Backend started successfully", "SUCCESS")
                self.backend_restart_count = 0
                return True
            else:
                self.log("❌ Backend failed to start", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error starting backend: {e}", "ERROR")
            return False
            
    def start_frontend(self):
        """Start the frontend server"""
        try:
            self.log("Starting frontend server...")
            frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
            
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=frontend_dir,
                shell=True
            )
            time.sleep(8)  # Wait for Vite to start
            
            if self.check_frontend():
                self.log("✅ Frontend started successfully", "SUCCESS")
                self.frontend_restart_count = 0
                return True
            else:
                self.log("❌ Frontend failed to start", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error starting frontend: {e}", "ERROR")
            return False
            
    def stop_backend(self):
        """Stop the backend server"""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                self.log("Backend stopped")
            except:
                self.backend_process.kill()
                
    def stop_frontend(self):
        """Stop the frontend server"""
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                self.log("Frontend stopped")
            except:
                self.frontend_process.kill()
                
    def restart_backend(self):
        """Restart the backend server"""
        if self.backend_restart_count >= MAX_RESTART_ATTEMPTS:
            self.log(f"❌ Max restart attempts ({MAX_RESTART_ATTEMPTS}) reached for backend", "ERROR")
            return False
            
        self.backend_restart_count += 1
        self.log(f"Restarting backend (attempt {self.backend_restart_count}/{MAX_RESTART_ATTEMPTS})...", "WARNING")
        self.stop_backend()
        time.sleep(2)
        return self.start_backend()
        
    def restart_frontend(self):
        """Restart the frontend server"""
        if self.frontend_restart_count >= MAX_RESTART_ATTEMPTS:
            self.log(f"❌ Max restart attempts ({MAX_RESTART_ATTEMPTS}) reached for frontend", "ERROR")
            return False
            
        self.frontend_restart_count += 1
        self.log(f"Restarting frontend (attempt {self.frontend_restart_count}/{MAX_RESTART_ATTEMPTS})...", "WARNING")
        self.stop_frontend()
        time.sleep(2)
        return self.start_frontend()
        
    def monitor(self):
        """Main monitoring loop"""
        self.log("=" * 60)
        self.log("HireBahamas Auto-Restart Service Started")
        self.log("=" * 60)
        
        # Initial start
        if not self.check_backend():
            self.start_backend()
        else:
            self.log("Backend is already running")
            
        if not self.check_frontend():
            self.start_frontend()
        else:
            self.log("Frontend is already running")
            
        self.log(f"Monitoring servers (checking every {CHECK_INTERVAL} seconds)...")
        self.log("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(CHECK_INTERVAL)
                
                # Check backend
                if not self.check_backend():
                    self.log("⚠️  Backend not responding!", "WARNING")
                    self.restart_backend()
                else:
                    self.log("✅ Backend: OK")
                    
                # Check frontend
                if not self.check_frontend():
                    self.log("⚠️  Frontend not responding!", "WARNING")
                    self.restart_frontend()
                else:
                    self.log("✅ Frontend: OK")
                    
        except KeyboardInterrupt:
            self.log("\nShutting down...")
            self.stop_backend()
            self.stop_frontend()
            self.log("Goodbye!")
            
if __name__ == "__main__":
    monitor = ServerMonitor()
    monitor.monitor()
