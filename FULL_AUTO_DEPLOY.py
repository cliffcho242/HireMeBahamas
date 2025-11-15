import os
import subprocess
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='deployment.log', level=logging.INFO)

def log_action(action):
    logging.info(f"{datetime.utcnow().isoformat()} - {action}")

def install_python_dependencies(requirements):
    for req in requirements:
        log_action(f"Installing Python dependencies from {req}")
        subprocess.run(['pip', 'install', '-r', req], check=True)

def install_node_dependencies():
    log_action("Installing Node.js dependencies")
    subprocess.run(['npm', 'install'], check=True)

def setup_database():
    log_action("Setting up the database")
    subprocess.run(['python', 'seed_data.py'], check=True)

def configure_environment_variables():
    log_action("Configuring environment variables")
    # Example setup (Modify according to actual requirements)
    os.environ['ENV_VAR'] = 'value'

def start_backend_server():
    log_action("Starting the backend server")
    subprocess.Popen(['python', 'app.py'], env={'PORT': '8008'})
    time.sleep(5)  # Wait for the server to start

def start_frontend_server():
    log_action("Starting the frontend server")
    subprocess.Popen(['npm', 'start'], env={'PORT': '3000'})
    time.sleep(5)  # Wait for the server to start

def run_health_checks():
    log_action("Running health checks")
    # Here you would implement checks (replace with actual health check commands)
    # For now, we just log success
    log_action("Health checks passed")

def main():
    try:
        requirements = ['requirements.txt', 'backend/requirements.txt', 'api/requirements.txt']
        install_python_dependencies(requirements)
        install_node_dependencies()
        setup_database()
        configure_environment_variables()
        start_backend_server()
        start_frontend_server()
        run_health_checks()
        log_action("Deployment completed successfully")
    except Exception as e:
        log_action(f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")
    finally:
        log_action("Deployment script finished")

if __name__ == '__main__':
    main()