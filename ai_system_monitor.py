#!/usr/bin/env python3
"""
🤖 AI-Powered System Monitor & Auto-Healer
Real-time monitoring, error detection, and automatic fixes for HireBahamas platform
"""
import asyncio
import threading
import time
import requests
import sqlite3
import bcrypt
import subprocess
import psutil
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import schedule

# Install required packages
required_packages = [
    'psutil',
    'schedule', 
    'watchdog',
    'redis',
    'flask-socketio'
]

def install_packages():
    """Install required packages for enhanced monitoring"""
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.run([
                "C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/pip.exe",
                "install", package
            ], check=True)

# Try to install packages
try:
    install_packages()
except Exception as e:
    print(f"Package installation note: {e}")

# Enhanced imports after installation
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    pass

@dataclass
class SystemHealth:
    """System health status"""
    backend_status: bool = False
    frontend_status: bool = False
    database_status: bool = False
    login_endpoint_status: bool = False
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    disk_usage: float = 0.0
    active_connections: int = 0
    last_check: datetime = None
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.last_check is None:
            self.last_check = datetime.now()

class AISystemMonitor:
    """AI-Powered System Monitor with Auto-Healing"""
    
    def __init__(self):
        self.base_path = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
        self.running = False
        self.health = SystemHealth()
        
        # AI Learning Data
        self.error_patterns = {}
        self.fix_success_rate = {}
        self.performance_history = []
        
        # Setup logging
        self.setup_logging()
        
        # Monitoring intervals
        self.check_interval = 30  # seconds
        self.deep_scan_interval = 300  # 5 minutes
        self.ai_analysis_interval = 900  # 15 minutes
        
        # Auto-fix enabled flags
        self.auto_fix_enabled = True
        self.ai_learning_enabled = True
        
        self.log("🤖 AI System Monitor initialized", "SUCCESS")
    
    def setup_logging(self):
        """Setup enhanced logging"""
        log_file = self.base_path / "logs" / "ai_monitor.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with AI context - Windows compatible"""
        colors = {
            "INFO": "[INFO]",
            "SUCCESS": "[SUCCESS]", 
            "ERROR": "[ERROR]",
            "WARNING": "[WARNING]",
            "FIX": "[FIX]",
            "AI": "[AI]"
        }
        
        formatted_message = f"{colors.get(level, '[LOG]')} {message}"
        
        # Print safely to console
        try:
            print(formatted_message)
        except UnicodeEncodeError:
            # Fallback for Windows console
            safe_message = message.encode('ascii', 'ignore').decode('ascii')
            print(f"{colors.get(level, '[LOG]')} {safe_message}")
        
        # Log to file
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    async def check_system_health(self) -> SystemHealth:
        """Comprehensive system health check"""
        health = SystemHealth()
        
        # Check backend
        health.backend_status = await self.check_backend()
        
        # Check frontend  
        health.frontend_status = await self.check_frontend()
        
        # Check database
        health.database_status = await self.check_database()
        
        # Check login endpoint specifically
        health.login_endpoint_status = await self.check_login_endpoint()
        
        # System resources
        health.memory_usage = psutil.virtual_memory().percent
        health.cpu_usage = psutil.cpu_percent(interval=1)
        health.disk_usage = psutil.disk_usage('/').percent
        
        # Count active connections
        health.active_connections = len([
            conn for conn in psutil.net_connections() 
            if conn.laddr.port in [3000, 8008]
        ])
        
        health.last_check = datetime.now()
        self.health = health
        
        return health
    
    async def check_backend(self) -> bool:
        """Check backend health"""
        try:
            response = await asyncio.to_thread(
                requests.get, 
                "http://127.0.0.1:8008/health", 
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def check_frontend(self) -> bool:
        """Check frontend health"""
        try:
            response = await asyncio.to_thread(
                requests.get, 
                "http://localhost:3000", 
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def check_database(self) -> bool:
        """Check database health"""
        try:
            db_path = self.base_path / "backend" / "hirebahamas.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            conn.close()
            return count >= 1  # At least admin user exists
        except Exception:
            return False
    
    async def check_login_endpoint(self) -> bool:
        """Specifically test login endpoint"""
        try:
            response = await asyncio.to_thread(
                requests.post,
                "http://127.0.0.1:8008/api/auth/login",
                json={"email": "admin@hirebahamas.com", "password": "admin123"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def ai_analyze_issues(self, health: SystemHealth):
        """AI-powered issue analysis and prediction"""
        current_time = datetime.now()
        
        # Identify patterns
        issues = []
        
        if not health.backend_status:
            issues.append("backend_down")
            self.record_error_pattern("backend_down", current_time)
        
        if not health.frontend_status:
            issues.append("frontend_down")
            self.record_error_pattern("frontend_down", current_time)
        
        if not health.database_status:
            issues.append("database_issues")
            self.record_error_pattern("database_issues", current_time)
            
        if not health.login_endpoint_status:
            issues.append("login_failure")
            self.record_error_pattern("login_failure", current_time)
        
        # Resource issues
        if health.memory_usage > 80:
            issues.append("high_memory")
        if health.cpu_usage > 80:
            issues.append("high_cpu")
        if health.disk_usage > 90:
            issues.append("disk_full")
        
        health.issues = issues
        
        # AI Prediction: Look for patterns
        if self.ai_learning_enabled:
            await self.predict_future_issues(issues)
        
        return issues
    
    def record_error_pattern(self, error_type: str, timestamp: datetime):
        """Record error patterns for AI learning"""
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = []
        
        self.error_patterns[error_type].append(timestamp)
        
        # Keep only last 100 entries
        if len(self.error_patterns[error_type]) > 100:
            self.error_patterns[error_type] = self.error_patterns[error_type][-100:]
    
    async def predict_future_issues(self, current_issues: List[str]):
        """AI prediction of future issues"""
        for issue in current_issues:
            if issue in self.error_patterns:
                recent_occurrences = [
                    t for t in self.error_patterns[issue]
                    if datetime.now() - t < timedelta(hours=24)
                ]
                
                if len(recent_occurrences) >= 3:
                    self.log(f"AI Prediction: {issue} recurring pattern detected", "AI")
                    await self.apply_proactive_fix(issue)
    
    async def apply_proactive_fix(self, issue_type: str):
        """Apply proactive fixes based on AI predictions"""
        fixes = {
            "backend_down": self.fix_backend,
            "frontend_down": self.fix_frontend,
            "database_issues": self.fix_database,
            "login_failure": self.fix_login_system
        }
        
        if issue_type in fixes and self.auto_fix_enabled:
            self.log(f"Applying proactive fix for {issue_type}", "AI")
            success = await fixes[issue_type]()
            
            # Record fix success rate
            if issue_type not in self.fix_success_rate:
                self.fix_success_rate[issue_type] = []
            self.fix_success_rate[issue_type].append(success)
    
    async def auto_heal_system(self, issues: List[str]):
        """Automatic system healing"""
        if not self.auto_fix_enabled:
            return
        
        self.log("🔧 Starting auto-healing process", "FIX")
        
        for issue in issues:
            self.log(f"Fixing: {issue}", "FIX")
            
            if issue == "backend_down":
                await self.fix_backend()
            elif issue == "frontend_down":
                await self.fix_frontend()
            elif issue == "database_issues":
                await self.fix_database()
            elif issue == "login_failure":
                await self.fix_login_system()
            elif issue == "high_memory":
                await self.optimize_memory()
            elif issue == "high_cpu":
                await self.optimize_cpu()
    
    async def fix_backend(self) -> bool:
        """Fix backend issues"""
        try:
            self.log("Restarting backend server", "FIX")
            
            # Kill existing processes
            await asyncio.to_thread(
                subprocess.run,
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True
            )
            
            await asyncio.sleep(2)
            
            # Start new backend
            backend_script = self.base_path / "facebook_like_backend.py"
            await asyncio.to_thread(
                subprocess.Popen,
                [
                    "C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/python.exe",
                    str(backend_script)
                ],
                cwd=str(self.base_path)
            )
            
            # Wait and verify
            await asyncio.sleep(5)
            return await self.check_backend()
            
        except Exception as e:
            self.log(f"Backend fix failed: {e}", "ERROR")
            return False
    
    async def fix_frontend(self) -> bool:
        """Fix frontend issues"""
        try:
            self.log("Checking frontend status", "FIX")
            
            # Check if frontend process exists
            frontend_dir = self.base_path / "frontend"
            if not frontend_dir.exists():
                return False
            
            # Frontend should be managed separately
            # This is a placeholder for frontend restart logic
            return True
            
        except Exception as e:
            self.log(f"Frontend fix failed: {e}", "ERROR")
            return False
    
    async def fix_database(self) -> bool:
        """Fix database issues"""
        try:
            self.log("Running database repair", "FIX")
            
            # Run database fix script
            fix_script = self.base_path / "ultimate_database_fix.py"
            if fix_script.exists():
                result = await asyncio.to_thread(
                    subprocess.run,
                    [
                        "C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/python.exe",
                        str(fix_script)
                    ],
                    capture_output=True,
                    text=True,
                    cwd=str(self.base_path)
                )
                return result.returncode == 0
            
            return False
            
        except Exception as e:
            self.log(f"Database fix failed: {e}", "ERROR")
            return False
    
    async def fix_login_system(self) -> bool:
        """Fix login system specifically"""
        try:
            self.log("Fixing login system", "FIX")
            
            # Check admin user
            db_path = self.base_path / "backend" / "hirebahamas.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Verify admin user exists and password works
            cursor.execute(
                "SELECT id, email, password_hash FROM users WHERE email = ?",
                ("admin@hirebahamas.com",)
            )
            user = cursor.fetchone()
            
            if not user:
                # Create admin user
                password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
                cursor.execute("""
                    INSERT INTO users (email, password_hash, username, full_name, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    "admin@hirebahamas.com",
                    password_hash.decode('utf-8'),
                    "admin",
                    "Platform Administrator",
                    True
                ))
                conn.commit()
            else:
                # Verify password
                if not bcrypt.checkpw("admin123".encode('utf-8'), user[2].encode('utf-8')):
                    # Fix password
                    new_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
                    cursor.execute(
                        "UPDATE users SET password_hash = ? WHERE email = ?",
                        (new_hash.decode('utf-8'), "admin@hirebahamas.com")
                    )
                    conn.commit()
            
            conn.close()
            
            # Restart backend to apply changes
            await self.fix_backend()
            
            return True
            
        except Exception as e:
            self.log(f"Login fix failed: {e}", "ERROR")
            return False
    
    async def optimize_memory(self):
        """Optimize memory usage"""
        try:
            # Restart backend to free memory
            await self.fix_backend()
            self.log("Memory optimization completed", "FIX")
        except Exception as e:
            self.log(f"Memory optimization failed: {e}", "ERROR")
    
    async def optimize_cpu(self):
        """Optimize CPU usage"""
        try:
            # Lower process priorities if needed
            for proc in psutil.process_iter(['pid', 'name']):
                if 'python' in proc.info['name'].lower():
                    try:
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    except:
                        pass
            self.log("CPU optimization completed", "FIX")
        except Exception as e:
            self.log(f"CPU optimization failed: {e}", "ERROR")
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        health = await self.check_system_health()
        
        # AI insights
        insights = []
        if health.memory_usage > 70:
            insights.append("Memory usage approaching critical levels")
        if health.cpu_usage > 70:
            insights.append("CPU usage is high, consider optimization")
        if not health.login_endpoint_status:
            insights.append("CRITICAL: Login system not functioning")
        
        # Calculate uptime score
        scores = [
            health.backend_status,
            health.frontend_status, 
            health.database_status,
            health.login_endpoint_status
        ]
        uptime_score = (sum(scores) / len(scores)) * 100
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "uptime_score": uptime_score,
            "system_health": {
                "backend": health.backend_status,
                "frontend": health.frontend_status,
                "database": health.database_status,
                "login": health.login_endpoint_status
            },
            "resources": {
                "memory": health.memory_usage,
                "cpu": health.cpu_usage,
                "disk": health.disk_usage,
                "connections": health.active_connections
            },
            "issues": health.issues,
            "ai_insights": insights,
            "fix_success_rates": self.fix_success_rate
        }
        
        return report
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        self.log("🤖 AI System Monitor started", "SUCCESS")
        
        while self.running:
            try:
                # Health check
                health = await self.check_system_health()
                
                # AI analysis
                issues = await self.ai_analyze_issues(health)
                
                # Auto-healing
                if issues:
                    self.log(f"Issues detected: {issues}", "WARNING")
                    await self.auto_heal_system(issues)
                
                # Performance tracking
                self.performance_history.append({
                    "timestamp": datetime.now(),
                    "uptime_score": sum([
                        health.backend_status,
                        health.frontend_status,
                        health.database_status,
                        health.login_endpoint_status
                    ]) / 4 * 100,
                    "memory": health.memory_usage,
                    "cpu": health.cpu_usage
                })
                
                # Keep only last 288 entries (24 hours at 5min intervals)
                if len(self.performance_history) > 288:
                    self.performance_history = self.performance_history[-288:]
                
                # Status report
                if not issues:
                    self.log("System healthy - all services operational", "SUCCESS")
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.log(f"Monitor loop error: {e}", "ERROR")
                await asyncio.sleep(10)
    
    def start_monitoring(self):
        """Start the monitoring system"""
        self.running = True
        
        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start monitoring
        loop.run_until_complete(self.monitor_loop())
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        self.log("AI System Monitor stopped", "INFO")

# Global monitor instance
monitor = None

def start_ai_monitor():
    """Start AI monitoring in background thread"""
    global monitor
    if monitor is None:
        monitor = AISystemMonitor()
        thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
        thread.start()
        return monitor
    return monitor

def get_system_health():
    """Get current system health"""
    global monitor
    if monitor:
        return asyncio.run(monitor.generate_health_report())
    return {"error": "Monitor not running"}

if __name__ == "__main__":
    # Start monitoring
    monitor = AISystemMonitor()
    monitor.start_monitoring()