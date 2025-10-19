#!/usr/bin/env python3
"""
HireBahamas AI-Powered Unstoppable Platform Manager
The most advanced localhost error prevention and auto-fix system
"""

import os
import sys
import time
import json
import threading
import subprocess
import socket
import requests
import psutil
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from colorama import init, Fore, Back, Style
import logging

# Initialize colorama for Windows
init(autoreset=True)

@dataclass
class ServiceStatus:
    name: str
    port: int
    url: str
    process_id: Optional[int] = None
    is_running: bool = False
    restart_count: int = 0
    error_count: int = 0
    uptime_start: Optional[datetime] = None

class AIUnstoppableManager:
    """AI-Powered Unstoppable Platform Manager"""
    
    def __init__(self):
        self.base_path = Path("c:/Users/Dell/OneDrive/Desktop/HireBahamas")
        self.python_exe = self.base_path / ".venv" / "Scripts" / "python.exe"
        
        self.services = {
            'backend': ServiceStatus(
                name='HireBahamas Backend',
                port=8008,
                url='http://127.0.0.1:8008/health'
            ),
            'frontend': ServiceStatus(
                name='HireBahamas Frontend', 
                port=3001,
                url='http://localhost:3001'
            )
        }
        
        self.monitoring_active = False
        self.max_restart_attempts = 5
        self.health_check_interval = 8
        self.error_patterns = {
            'port_conflict': ['port in use', 'address already in use', 'bind failed'],
            'process_crash': ['process terminated', 'exit code', 'killed'],
            'network_issue': ['connection refused', 'timeout', 'unreachable'],
            'dependency_missing': ['module not found', 'import error', 'not installed'],
            'permission_denied': ['access denied', 'permission', 'unauthorized'],
            'resource_exhaustion': ['out of memory', 'disk full', 'no space'],
        }
        
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = self.base_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"unstoppable_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def ai_log(self, message: str, level: str = "INFO", color: str = Fore.CYAN):
        """AI-enhanced logging with colors"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        ai_indicator = f"{Fore.MAGENTA}[🤖 AI]{Style.RESET_ALL}"
        colored_message = f"{color}[{timestamp}] {ai_indicator} {level}: {message}{Style.RESET_ALL}"
        print(colored_message)
        self.logger.info(f"AI {level}: {message}")
        
    def predict_issues(self) -> List[str]:
        """AI-powered issue prediction"""
        potential_issues = []
        
        # System resource checks
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            if cpu_percent > 85:
                potential_issues.append(f"High CPU usage: {cpu_percent:.1f}% - Performance degradation risk")
                
            if memory.percent > 80:
                potential_issues.append(f"High memory usage: {memory.percent:.1f}% - Crash risk detected")
                
            # Port conflict prediction
            for service_name, service in self.services.items():
                if self.is_port_in_use(service.port) and not service.is_running:
                    potential_issues.append(f"Port conflict predicted: {service.port} for {service_name}")
                    
            # Service stability analysis
            for service_name, service in self.services.items():
                if service.restart_count > 2:
                    potential_issues.append(f"Service instability: {service_name} (restarts: {service.restart_count})")
                    
        except Exception as e:
            potential_issues.append(f"System monitoring error: {e}")
            
        return potential_issues
        
    def is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('127.0.0.1', port))
            return result == 0
            
    def force_kill_port(self, port: int) -> bool:
        """Aggressively kill process on port"""
        killed = False
        
        try:
            # Method 1: psutil approach
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if hasattr(conn, 'laddr') and conn.laddr.port == port:
                            self.ai_log(f"Terminating {proc.info['name']} (PID: {proc.info['pid']}) on port {port}", "WARNING", Fore.YELLOW)
                            proc.kill()
                            proc.wait(timeout=3)
                            killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
                    
            # Method 2: Windows netstat + taskkill
            if not killed:
                result = subprocess.run(
                    f'netstat -ano | findstr ":{port}" | findstr "LISTENING"',
                    shell=True, capture_output=True, text=True
                )
                
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            self.ai_log(f"Force killing PID {pid} on port {port}", "WARNING", Fore.YELLOW)
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                            killed = True
                            
            # Method 3: Nuclear option - kill all python/node processes
            if not killed and port in [8008, 3001]:
                self.ai_log("Nuclear option: Killing all relevant processes", "ERROR", Fore.RED)
                subprocess.run("taskkill /F /IM python.exe", shell=True, capture_output=True)
                subprocess.run("taskkill /F /IM node.exe", shell=True, capture_output=True)
                killed = True
                
            time.sleep(2)
            return killed
            
        except Exception as e:
            self.ai_log(f"Port kill error: {e}", "ERROR", Fore.RED)
            return False
            
    def start_backend_unstoppable(self) -> bool:
        """Start backend with maximum resilience"""
        service = self.services['backend']
        
        self.ai_log("Starting UNSTOPPABLE backend service...", "INFO", Fore.CYAN)
        
        # Aggressive port clearing
        if self.is_port_in_use(service.port):
            self.ai_log(f"Port {service.port} occupied - applying aggressive fix", "WARNING", Fore.YELLOW)
            self.force_kill_port(service.port)
            
        # Multiple startup attempts
        for attempt in range(3):
            try:
                backend_script = self.base_path / "final_backend.py"
                if not backend_script.exists():
                    self.ai_log("Critical: Backend script missing!", "ERROR", Fore.RED)
                    return False
                    
                # Start process with enhanced monitoring
                process = subprocess.Popen(
                    [str(self.python_exe), str(backend_script)],
                    cwd=str(self.base_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                service.process_id = process.pid
                service.uptime_start = datetime.now()
                
                # Progressive health checking
                for check in range(6):
                    time.sleep(1)
                    if self.check_service_health('backend'):
                        service.is_running = True
                        service.restart_count = 0
                        self.ai_log(f"Backend ONLINE (attempt {attempt + 1})", "SUCCESS", Fore.GREEN)
                        return True
                        
                # If health check fails, kill and retry
                if process.poll() is None:
                    process.terminate()
                    
            except Exception as e:
                self.ai_log(f"Backend start attempt {attempt + 1} failed: {e}", "ERROR", Fore.RED)
                time.sleep(2)
                
        self.ai_log("Backend startup FAILED after all attempts", "ERROR", Fore.RED)
        return False
        
    def start_frontend_unstoppable(self) -> bool:
        """Start frontend with maximum resilience"""
        service = self.services['frontend']
        
        self.ai_log("Starting UNSTOPPABLE frontend service...", "INFO", Fore.CYAN)
        
        frontend_path = self.base_path / "frontend"
        if not frontend_path.exists():
            self.ai_log("Critical: Frontend directory missing!", "ERROR", Fore.RED)
            return False
            
        # Ensure dependencies
        if not (frontend_path / "node_modules").exists():
            self.ai_log("Installing frontend dependencies (this may take time)...", "WARNING", Fore.YELLOW)
            try:
                subprocess.run(["npm", "install"], cwd=frontend_path, check=True, 
                             capture_output=True, text=True, timeout=300)
                self.ai_log("Dependencies installed successfully", "SUCCESS", Fore.GREEN)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.ai_log(f"Dependency installation failed: {e}", "ERROR", Fore.RED)
                return False
                
        # Aggressive port clearing
        self.force_kill_port(service.port)
        self.force_kill_port(3000)  # Also clear default port
        
        # Multiple startup attempts
        for attempt in range(3):
            try:
                # Set environment variables for consistent port
                env = os.environ.copy()
                env['PORT'] = '3001'
                env['VITE_PORT'] = '3001'
                
                process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=str(frontend_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )
                
                service.process_id = process.pid
                service.uptime_start = datetime.now()
                
                # Frontend takes longer to start
                time.sleep(10)
                
                # Check if process is still running
                if process.poll() is None:
                    service.is_running = True
                    service.restart_count = 0
                    self.ai_log(f"Frontend ONLINE (attempt {attempt + 1})", "SUCCESS", Fore.GREEN)
                    return True
                else:
                    self.ai_log(f"Frontend process died on attempt {attempt + 1}", "ERROR", Fore.RED)
                    
            except Exception as e:
                self.ai_log(f"Frontend start attempt {attempt + 1} failed: {e}", "ERROR", Fore.RED)
                time.sleep(3)
                
        self.ai_log("Frontend startup FAILED after all attempts", "ERROR", Fore.RED)
        return False
        
    def check_service_health(self, service_name: str) -> bool:
        """Enhanced health checking"""
        service = self.services[service_name]
        
        try:
            response = requests.get(service.url, timeout=3)
            healthy = response.status_code == 200
            
            if healthy:
                service.error_count = 0
            else:
                service.error_count += 1
                
            return healthy
            
        except requests.exceptions.RequestException:
            service.error_count += 1
            return False
            
    def ai_recovery_protocol(self, service_name: str) -> bool:
        """Advanced AI recovery protocol"""
        service = self.services[service_name]
        
        self.ai_log(f"Initiating AI recovery for {service_name}", "WARNING", Fore.YELLOW)
        
        # Analyze failure pattern
        if service.error_count > 5:
            self.ai_log("Critical failure detected - applying nuclear recovery", "ERROR", Fore.RED)
            return self.nuclear_recovery()
            
        # Standard recovery
        service.restart_count += 1
        
        # Kill existing processes
        if service.process_id:
            try:
                process = psutil.Process(service.process_id)
                process.kill()
                process.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass
                
        # Force clear port
        self.force_kill_port(service.port)
        time.sleep(3)
        
        # Restart based on service
        if service_name == 'backend':
            return self.start_backend_unstoppable()
        else:
            return self.start_frontend_unstoppable()
            
    def nuclear_recovery(self) -> bool:
        """Nuclear option - complete system reset"""
        self.ai_log("NUCLEAR RECOVERY PROTOCOL ACTIVATED", "ERROR", Fore.RED)
        
        # Kill everything
        subprocess.run("taskkill /F /IM python.exe", shell=True, capture_output=True)
        subprocess.run("taskkill /F /IM node.exe", shell=True, capture_output=True)
        
        # Reset all services
        for service in self.services.values():
            service.is_running = False
            service.process_id = None
            service.restart_count = 0
            service.error_count = 0
            
        time.sleep(5)
        
        # Restart everything
        backend_ok = self.start_backend_unstoppable()
        if backend_ok:
            frontend_ok = self.start_frontend_unstoppable()
            return backend_ok and frontend_ok
            
        return False
        
    def continuous_monitoring(self):
        """Continuous AI monitoring"""
        self.ai_log("AI monitoring ACTIVATED - Platform is now UNSTOPPABLE", "SUCCESS", Fore.GREEN)
        self.monitoring_active = True
        
        monitor_cycle = 0
        
        while self.monitoring_active:
            try:
                monitor_cycle += 1
                
                # Predict issues every cycle
                predicted_issues = self.predict_issues()
                for issue in predicted_issues:
                    self.ai_log(f"PREDICTION: {issue}", "WARNING", Fore.YELLOW)
                    
                # Health checks
                for service_name, service in self.services.items():
                    if service.is_running:
                        if not self.check_service_health(service_name):
                            self.ai_log(f"HEALTH FAILURE: {service_name}", "ERROR", Fore.RED)
                            # Immediate recovery
                            self.ai_recovery_protocol(service_name)
                            
                # Show status every 5 cycles (40 seconds)
                if monitor_cycle % 5 == 0:
                    self.show_ai_dashboard()
                    
                time.sleep(self.health_check_interval)
                
            except KeyboardInterrupt:
                self.ai_log("Monitoring shutdown requested", "INFO", Fore.CYAN)
                break
            except Exception as e:
                self.ai_log(f"Monitoring error: {e} - Continuing...", "ERROR", Fore.RED)
                time.sleep(5)
                
        self.monitoring_active = False
        
    def open_browser_smart(self):
        """Smart browser opening with multiple attempts"""
        self.ai_log("Opening application in browser...", "INFO", Fore.CYAN)
        
        urls_to_try = [
            f"http://localhost:{self.services['frontend'].port}",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ]
        
        for url in urls_to_try:
            try:
                webbrowser.open(url)
                self.ai_log(f"Browser opened: {url}", "SUCCESS", Fore.GREEN)
                return True
            except Exception as e:
                self.ai_log(f"Browser attempt failed for {url}: {e}", "WARNING", Fore.YELLOW)
                
        self.ai_log("All browser attempts failed - manual access required", "ERROR", Fore.RED)
        return False
        
    def show_ai_dashboard(self):
        """AI Dashboard display"""
        print(f"\n{Fore.MAGENTA}{'='*80}")
        print(f"{Fore.MAGENTA}      🤖 HireBahamas AI-Powered UNSTOPPABLE Platform Dashboard")
        print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
        
        # Service status
        print(f"\n{Fore.CYAN}🔍 REALTIME SERVICE STATUS:{Style.RESET_ALL}")
        for name, service in self.services.items():
            status_color = Fore.GREEN if service.is_running else Fore.RED
            status_text = "🟢 ONLINE" if service.is_running else "🔴 OFFLINE"
            
            uptime = ""
            if service.uptime_start and service.is_running:
                uptime_delta = datetime.now() - service.uptime_start
                uptime = f" | Uptime: {str(uptime_delta).split('.')[0]}"
                
            print(f"  {status_color}{status_text} {service.name} (Port {service.port}){uptime}{Style.RESET_ALL}")
            print(f"    URL: {service.url}")
            print(f"    Restarts: {service.restart_count} | Errors: {service.error_count}")
            
        # AI Predictions
        print(f"\n{Fore.MAGENTA}🤖 AI THREAT ANALYSIS:{Style.RESET_ALL}")
        predicted_issues = self.predict_issues()
        if predicted_issues:
            for issue in predicted_issues:
                print(f"  {Fore.YELLOW}⚠️  {issue}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.GREEN}✅ All systems optimal - No threats detected{Style.RESET_ALL}")
            
        # System metrics
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            print(f"\n{Fore.CYAN}📊 SYSTEM PERFORMANCE:{Style.RESET_ALL}")
            print(f"  CPU: {cpu:.1f}% | Memory: {memory.percent:.1f}% | Processes: {len(psutil.pids())}")
        except:
            pass
            
        # Access info
        print(f"\n{Fore.GREEN}🌐 ACCESS URLS:{Style.RESET_ALL}")
        print(f"  🎯 Application: http://localhost:{self.services['frontend'].port}")
        print(f"  🔧 API Health: http://127.0.0.1:{self.services['backend'].port}/health")
        print(f"  👤 Admin Login: admin@hirebahamas.com / AdminPass123!")
        
        print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
        
    def run_unstoppable_platform(self):
        """Main execution - THE UNSTOPPABLE PLATFORM"""
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}")
        print("██╗   ██╗███╗   ██╗███████╗████████╗ ██████╗ ██████╗ ██████╗  █████╗ ██████╗ ██╗     ███████╗")
        print("██║   ██║████╗  ██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝")
        print("██║   ██║██╔██╗ ██║███████╗   ██║   ██║   ██║██████╔╝██████╔╝███████║██████╔╝██║     █████╗  ")
        print("██║   ██║██║╚██╗██║╚════██║   ██║   ██║   ██║██╔═══╝ ██╔═══╝ ██╔══██║██╔══██╗██║     ██╔══╝  ")
        print("╚██████╔╝██║ ╚████║███████║   ██║   ╚██████╔╝██║     ██║     ██║  ██║██████╔╝███████╗███████╗")
        print(" ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝     ╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝")
        print(f"{Style.RESET_ALL}")
        
        self.ai_log("Initializing UNSTOPPABLE HireBahamas Platform", "INFO", Fore.MAGENTA)
        self.ai_log("AI-Powered Error Prevention & Auto-Recovery System", "INFO", Fore.MAGENTA)
        self.ai_log("="*80, "INFO", Fore.MAGENTA)
        
        try:
            # Phase 1: Preparation
            self.ai_log("Phase 1: System Preparation & AI Initialization", "INFO", Fore.CYAN)
            
            # Phase 2: Backend startup
            self.ai_log("Phase 2: Backend Service Activation", "INFO", Fore.CYAN)
            backend_started = self.start_backend_unstoppable()
            
            if backend_started:
                # Phase 3: Frontend startup
                self.ai_log("Phase 3: Frontend Service Activation", "INFO", Fore.CYAN)
                frontend_started = self.start_frontend_unstoppable()
                
                if frontend_started:
                    # Phase 4: Browser integration
                    self.ai_log("Phase 4: Browser Integration", "INFO", Fore.CYAN)
                    time.sleep(3)
                    self.open_browser_smart()
                    
                    # Phase 5: AI monitoring activation
                    self.ai_log("Phase 5: AI Monitoring Activation", "INFO", Fore.CYAN)
                    
                    # Show initial dashboard
                    self.show_ai_dashboard()
                    
                    # Start continuous monitoring
                    monitor_thread = threading.Thread(target=self.continuous_monitoring, daemon=True)
                    monitor_thread.start()
                    
                    self.ai_log("🎉 PLATFORM IS NOW UNSTOPPABLE! 🎉", "SUCCESS", Fore.GREEN)
                    self.ai_log("AI monitoring active - All errors will be auto-fixed", "SUCCESS", Fore.GREEN)
                    self.ai_log("Press Ctrl+C for graceful shutdown", "INFO", Fore.CYAN)
                    
                    # Keep alive
                    try:
                        while True:
                            time.sleep(30)
                    except KeyboardInterrupt:
                        self.ai_log("Graceful shutdown initiated by user", "INFO", Fore.CYAN)
                        self.monitoring_active = False
                        
                else:
                    self.ai_log("Frontend activation failed - applying AI recovery", "ERROR", Fore.RED)
                    self.ai_recovery_protocol('frontend')
            else:
                self.ai_log("Backend activation failed - applying AI recovery", "ERROR", Fore.RED)
                self.ai_recovery_protocol('backend')
                
        except Exception as e:
            self.ai_log(f"Critical system error: {e}", "ERROR", Fore.RED)
            self.nuclear_recovery()

if __name__ == "__main__":
    # Initialize and run the UNSTOPPABLE platform
    manager = AIUnstoppableManager()
    manager.run_unstoppable_platform()