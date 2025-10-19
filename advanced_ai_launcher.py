#!/usr/bin/env python3
"""
🚀 Advanced AI System Launcher for HireBahamas
100x Enhanced AI Platform with Multi-Modal Intelligence
"""

import subprocess
import time
import threading
import os
import sys
import signal
import logging
from pathlib import Path
from datetime import datetime
import requests
import json
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 🚀 AI Launcher - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_system_launcher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AdvancedAISystemLauncher:
    """
    🚀 Advanced AI System Launcher
    Manages all AI services and ensures 100x enhanced performance
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        self.services = {
            'ai_api_server': {
                'command': [sys.executable, 'ai_api_server.py'],
                'port': 8009,
                'health_endpoint': 'http://127.0.0.1:8009/api/ai/health',
                'description': '🤖 Advanced AI API Server'
            },
            'ai_orchestrator': {
                'command': [sys.executable, 'advanced_ai_orchestrator.py'],
                'port': None,
                'health_endpoint': None,
                'description': '🎯 AI Orchestrator Core'
            },
            'backend': {
                'command': [sys.executable, 'final_backend.py'],
                'port': 8008,
                'health_endpoint': 'http://127.0.0.1:8008/health',
                'description': '⚙️ HireBahamas Backend'
            },
            'frontend': {
                'command': ['npm', 'run', 'dev'],
                'cwd': self.project_root / 'frontend',
                'port': 3000,
                'health_endpoint': 'http://127.0.0.1:3000',
                'description': '🎨 React Frontend'
            }
        }

        self.monitoring_active = True
        self.start_time = datetime.now()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        self.stop_all_services()

    def start_service(self, service_name: str) -> bool:
        """Start a specific AI service"""
        if service_name not in self.services:
            logger.error(f"❌ Unknown service: {service_name}")
            return False

        service_config = self.services[service_name]

        try:
            logger.info(f"🚀 Starting {service_config['description']}...")

            # Prepare command
            cmd = service_config['command']
            cwd = service_config.get('cwd', self.project_root)

            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.processes[service_name] = {
                'process': process,
                'config': service_config,
                'start_time': datetime.now(),
                'status': 'starting'
            }

            # Start output monitoring thread
            threading.Thread(
                target=self._monitor_process_output,
                args=(service_name, process),
                daemon=True
            ).start()

            logger.info(f"✅ {service_config['description']} started (PID: {process.pid})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            return False

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.processes:
            logger.warning(f"⚠️ Service {service_name} not running")
            return False

        try:
            process_info = self.processes[service_name]
            process = process_info['process']

            logger.info(f"🛑 Stopping {process_info['config']['description']}...")

            # Terminate process tree
            self._terminate_process_tree(process.pid)

            # Wait for process to terminate
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {service_name}")
                process.kill()

            del self.processes[service_name]
            logger.info(f"✅ {process_info['config']['description']} stopped")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop {service_name}: {e}")
            return False

    def _terminate_process_tree(self, pid: int):
        """Terminate a process and all its children"""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            # Terminate children first
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass

            # Terminate parent
            try:
                parent.terminate()
            except psutil.NoSuchProcess:
                pass

            # Wait a bit
            time.sleep(2)

            # Force kill if still running
            for child in children:
                try:
                    if child.is_running():
                        child.kill()
                except psutil.NoSuchProcess:
                    pass

            try:
                if parent.is_running():
                    parent.kill()
            except psutil.NoSuchProcess:
                pass

        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            logger.error(f"Error terminating process tree: {e}")

    def _monitor_process_output(self, service_name: str, process: subprocess.Popen):
        """Monitor process output and log it"""
        try:
            while self.monitoring_active and process.poll() is None:
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        logger.info(f"📝 {service_name}: {line.strip()}")

                if process.stderr:
                    error_line = process.stderr.readline()
                    if error_line:
                        logger.error(f"❌ {service_name}: {error_line.strip()}")

                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error monitoring {service_name}: {e}")

    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        if service_name not in self.services:
            return False

        service_config = self.services[service_name]
        health_endpoint = service_config.get('health_endpoint')

        if not health_endpoint:
            # For services without health endpoints, check if process is running
            return service_name in self.processes and \
                   self.processes[service_name]['process'].poll() is None

        try:
            response = requests.get(health_endpoint, timeout=5)
            return response.status_code == 200
        except:
            return False

    def wait_for_service(self, service_name: str, timeout: int = 30) -> bool:
        """Wait for a service to become healthy"""
        logger.info(f"⏳ Waiting for {service_name} to be ready...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_service_health(service_name):
                logger.info(f"✅ {service_name} is ready!")
                return True
            time.sleep(2)

        logger.error(f"❌ {service_name} failed to start within {timeout} seconds")
        return False

    def start_all_services(self) -> bool:
        """Start all AI services in the correct order"""
        logger.info("🚀 Starting Advanced AI System (100x Enhanced)...")
        logger.info("=" * 60)

        # Start services in dependency order
        startup_order = [
            'ai_orchestrator',  # Core AI engine first
            'ai_api_server',   # AI API endpoints
            'backend',          # Flask backend
            'frontend'          # React frontend
        ]

        success_count = 0

        for service_name in startup_order:
            if self.start_service(service_name):
                # Wait for service to be ready
                if self.wait_for_service(service_name, timeout=60):
                    success_count += 1
                else:
                    logger.error(f"❌ {service_name} failed health check")
            else:
                logger.error(f"❌ Failed to start {service_name}")

        logger.info(f"📊 Started {success_count}/{len(startup_order)} services")

        if success_count == len(startup_order):
            logger.info("🎉 Advanced AI System fully operational!")
            logger.info("🌐 Access your enhanced platform at:")
            logger.info("   • Frontend: http://127.0.0.1:3000")
            logger.info("   • Backend API: http://127.0.0.1:8008")
            logger.info("   • AI API: http://127.0.0.1:8009/api/ai")
            return True
        else:
            logger.error("❌ Some services failed to start")
            return False

    def stop_all_services(self):
        """Stop all running services"""
        logger.info("🛑 Stopping all AI services...")

        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)

        logger.info("✅ All services stopped")

    def monitor_system(self):
        """Monitor the entire AI system health"""
        while self.monitoring_active:
            try:
                # Check all services
                healthy_services = 0
                total_services = len(self.services)

                for service_name in self.services:
                    if self.check_service_health(service_name):
                        healthy_services += 1
                    else:
                        logger.warning(f"⚠️ {service_name} is not healthy")

                # System status
                uptime = datetime.now() - self.start_time
                status = "🟢 Excellent" if healthy_services == total_services else \
                        "🟡 Degraded" if healthy_services > total_services // 2 else "🔴 Critical"

                logger.info(f"📊 System Status: {status} | Services: {healthy_services}/{total_services} | Uptime: {uptime}")

                # AI-specific monitoring
                self._monitor_ai_performance()

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                time.sleep(10)

    def _monitor_ai_performance(self):
        """Monitor AI system performance metrics"""
        try:
            # Check AI API health
            if self.check_service_health('ai_api_server'):
                # Get AI analytics
                try:
                    response = requests.get('http://127.0.0.1:8009/api/ai/analytics', timeout=5)
                    if response.status_code == 200:
                        analytics = response.json().get('analytics', {})
                        logger.info(f"🤖 AI Analytics: {analytics.get('total_users_analyzed', 0)} users analyzed, "
                                  f"{analytics.get('ai_services_status', {}).get('openai', False) and 'OpenAI' or 'No OpenAI'} available")
                except:
                    pass

        except Exception as e:
            logger.debug(f"AI performance monitoring error: {e}")

    def run_system_diagnostics(self):
        """Run comprehensive system diagnostics"""
        logger.info("🔍 Running AI System Diagnostics...")
        logger.info("=" * 50)

        diagnostics = {
            'services': {},
            'ai_capabilities': {},
            'performance': {},
            'recommendations': []
        }

        # Check each service
        for service_name, service_config in self.services.items():
            is_healthy = self.check_service_health(service_name)
            diagnostics['services'][service_name] = {
                'healthy': is_healthy,
                'description': service_config['description'],
                'port': service_config.get('port')
            }

            if not is_healthy:
                diagnostics['recommendations'].append(f"Restart {service_name} service")

        # Check AI capabilities
        try:
            response = requests.get('http://127.0.0.1:8009/api/ai/health', timeout=5)
            if response.status_code == 200:
                ai_health = response.json()
                diagnostics['ai_capabilities'] = {
                    'status': ai_health.get('status'),
                    'capabilities': ai_health.get('capabilities', []),
                    'online': True
                }
            else:
                diagnostics['ai_capabilities'] = {'online': False}
                diagnostics['recommendations'].append("AI API server is not responding")
        except:
            diagnostics['ai_capabilities'] = {'online': False}
            diagnostics['recommendations'].append("Cannot connect to AI API server")

        # Performance metrics
        diagnostics['performance'] = {
            'uptime': str(datetime.now() - self.start_time),
            'services_running': len(self.processes),
            'total_services': len(self.services)
        }

        # Print diagnostics
        logger.info("📋 System Diagnostics Results:")
        logger.info(f"   Services: {diagnostics['performance']['services_running']}/{diagnostics['performance']['total_services']} running")
        logger.info(f"   AI Status: {'🟢 Online' if diagnostics['ai_capabilities'].get('online') else '🔴 Offline'}")
        logger.info(f"   Uptime: {diagnostics['performance']['uptime']}")

        if diagnostics['recommendations']:
            logger.info("💡 Recommendations:")
            for rec in diagnostics['recommendations']:
                logger.info(f"   • {rec}")

        return diagnostics

    def interactive_menu(self):
        """Interactive management menu"""
        while True:
            print("\n🚀 Advanced AI System Manager")
            print("=" * 40)
            print("1. Start All Services")
            print("2. Stop All Services")
            print("3. Check System Health")
            print("4. Run Diagnostics")
            print("5. Restart Failed Services")
            print("6. View Service Logs")
            print("7. Exit")

            try:
                choice = input("Choose an option (1-7): ").strip()

                if choice == '1':
                    self.start_all_services()
                elif choice == '2':
                    self.stop_all_services()
                elif choice == '3':
                    self.run_system_diagnostics()
                elif choice == '4':
                    diagnostics = self.run_system_diagnostics()
                    print(json.dumps(diagnostics, indent=2))
                elif choice == '5':
                    # Restart failed services
                    for service_name in self.services:
                        if not self.check_service_health(service_name):
                            logger.info(f"🔄 Restarting {service_name}...")
                            self.stop_service(service_name)
                            time.sleep(2)
                            self.start_service(service_name)
                elif choice == '6':
                    # Show recent logs
                    try:
                        with open('ai_system_launcher.log', 'r') as f:
                            lines = f.readlines()[-20:]  # Last 20 lines
                            print("\n📋 Recent Logs:")
                            for line in lines:
                                print(line.strip())
                    except FileNotFoundError:
                        print("No log file found")
                elif choice == '7':
                    logger.info("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice")

            except KeyboardInterrupt:
                logger.info("👋 Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Menu error: {e}")

def main():
    """Main entry point"""
    print("🚀 Advanced AI System Launcher for HireBahamas")
    print("100x Enhanced AI Platform with Multi-Modal Intelligence")
    print("=" * 60)

    launcher = AdvancedAISystemLauncher()

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'start':
            success = launcher.start_all_services()
            if success:
                # Start monitoring in background
                monitor_thread = threading.Thread(target=launcher.monitor_system, daemon=True)
                monitor_thread.start()

                # Keep running
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    launcher.stop_all_services()
            else:
                sys.exit(1)

        elif command == 'stop':
            launcher.stop_all_services()

        elif command == 'status':
            launcher.run_system_diagnostics()

        elif command == 'diagnostics':
            diagnostics = launcher.run_system_diagnostics()
            print(json.dumps(diagnostics, indent=2))

        else:
            print(f"❌ Unknown command: {command}")
            print("Usage: python advanced_ai_launcher.py [start|stop|status|diagnostics]")
            sys.exit(1)
    else:
        # Interactive mode
        launcher.interactive_menu()

if __name__ == "__main__":
    main()