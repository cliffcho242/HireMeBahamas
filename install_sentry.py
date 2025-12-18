#!/usr/bin/env python3
"""
Automated Sentry Installation Script for HireMeBahamas
This script will:
1. Update requirements.txt with Sentry SDK
2. Create/update backend with Sentry integration
3. Update .env.example with Sentry configuration
4. Commit and push changes
"""

import os
import subprocess
import sys
from pathlib import Path

def print_step(step, message):
    """Print formatted step message"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {message}")
    print(f"{'='*60}\n")

def run_command(command, shell=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(command, shell=shell, check=True, 
                              capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Error output: {e.stderr}")
        return None

def update_requirements():
    """Add Sentry SDK to requirements.txt"""
    print_step(1, "Updating requirements.txt with Sentry SDK")
    
    requirements_file = Path("requirements.txt")
    
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Check if sentry-sdk is already in requirements
        if 'sentry-sdk' not in content:
            with open(requirements_file, 'a') as f:
                f.write('\nsentry-sdk[flask]==1.39.2\n')
            print("✓ Added sentry-sdk to requirements.txt")
        else:
            print("✓ sentry-sdk already in requirements.txt")
    else:
        # Create new requirements.txt
        with open(requirements_file, 'w') as f:
            f.write("""Flask==2.3.3
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
Flask-Caching==2.1.0
PyJWT==2.8.0
bcrypt==4.1.2
python-dotenv==1.0.0
gunicorn==21.2.0
waitress==2.1.2
Werkzeug==2.3.7
requests==2.31.0
psycopg2-binary==2.9.9
sentry-sdk[flask]==1.39.2
""")
            print("✓ Created requirements.txt with Sentry SDK")

def create_sentry_config():
    """Create Sentry configuration file"""
    print_step(2, "Creating Sentry configuration")
    
    sentry_config = """
"""
Sentry Configuration for HireMeBahamas
"""
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import os
import logging

def init_sentry(app=None):
    """
    Initialize Sentry SDK with Flask integration
    
    Args:
        app: Flask application instance (optional)
    """
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if not sentry_dsn:
        print("⚠️  WARNING: SENTRY_DSN not found in environment variables")
        print("   Sentry monitoring will NOT be active!")
        return False
    
    environment = os.getenv('ENVIRONMENT', 'production')
    
    # Configure logging integration
    logging_integration = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    # Initialize Sentry
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FlaskIntegration(),
            logging_integration,
        ],
        
        # Set traces_sample_rate to capture performance data
        # 1.0 = 100% of transactions, lower in production (e.g., 0.1 = 10%)
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '1.0')),
        
        # Set profiles_sample_rate for profiling
        profiles_sample_rate=float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE', '1.0')),
        
        # Environment name
        environment=environment,
        
        # Release version (optional)
        release=os.getenv('SENTRY_RELEASE', 'hiremebahamas@1.0.0'),
        
        # Send default PII (Personally Identifiable Information)
        send_default_pii=False,
        
        # Attach stack traces to messages
        attach_stacktrace=True,
        
        # Before send callback (filter sensitive data)
        before_send=filter_sensitive_data,
    )
    
    print(f"✓ Sentry initialized successfully!")
    print(f"  Environment: {environment}")
    print(f"  Traces Sample Rate: {os.getenv('SENTRY_TRACES_SAMPLE_RATE', '1.0')}")
    
    return True

def filter_sensitive_data(event, hint):
    """
    Filter sensitive data before sending to Sentry
    
    Args:
        event: The event dictionary
        hint: Additional information about the event
        
    Returns:
        Modified event or None to drop the event
    """
    # Remove password fields
    if 'request' in event:
        if 'data' in event['request']:
            data = event['request']['data']
            if isinstance(data, dict):
                for key in ['password', 'token', 'secret', 'api_key']:
                    if key in data:
                        data[key] = '[Filtered]'
    
    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        headers = event['request']['headers']
        for key in ['Authorization', 'Cookie', 'X-API-Key']:
            if key in headers:
                headers[key] = '[Filtered]'
    
    return event

def capture_message(message, level='info'):
    """
    Capture a message in Sentry
    
    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
    """
    sentry_sdk.capture_message(message, level=level)

def capture_exception(exception=None):
    """
    Capture an exception in Sentry
    
    Args:
        exception: The exception to capture (optional, captures current exception if None)
    """
    sentry_sdk.capture_exception(exception)

def add_breadcrumb(message, category='default', level='info', data=None):
    """
    Add a breadcrumb for better error context
    
    Args:
        message: Breadcrumb message
        category: Breadcrumb category
        level: Severity level
        data: Additional data dictionary
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )

def set_user(user_id=None, username=None, email=None):
    """
    Set user context for Sentry events
    
    Args:
        user_id: User ID
        username: Username
        email: User email
    """
    sentry_sdk.set_user({
        "id": user_id,
        "username": username,
        "email": email,
    })

def set_context(name, data):
    """
    Set additional context for Sentry events
    
    Args:
        name: Context name
        data: Context data dictionary
    """
    sentry_sdk.set_context(name, data)

def set_tag(key, value):
    """
    Set a tag for Sentry events
    
    Args:
        key: Tag key
        value: Tag value
    """
    sentry_sdk.set_tag(key, value)
"""
    
    with open('sentry_config.py', 'w') as f:
        f.write(sentry_config)
    
    print("✓ Created sentry_config.py")

def update_backend_files():
    """Update backend files to import Sentry"""
    print_step(3, "Updating backend files with Sentry integration")
    
    # Find main backend files
    backend_files = [
        'backend/app.py',
        'facebook_like_backend.py',
        'final_backend_postgresql.py',
        'backend.py',
    ]
    
    sentry_import = """
# Sentry Error Tracking
try:
    from sentry_config import init_sentry
    sentry_enabled = init_sentry()
except ImportError:
    print("⚠️  Sentry configuration not found. Error tracking disabled.")
    sentry_enabled = False
"""
    
    updated_count = 0
    for file_path in backend_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if Sentry is already configured
            if 'sentry_config' not in content and 'sentry_sdk' not in content:
                # Find where to insert (after imports, before app creation)
                lines = content.split('\n')
                insert_index = 0
                
                # Find last import statement
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_index = i + 1
                
                # Insert Sentry import
                lines.insert(insert_index, sentry_import)
                
                # Write back
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                print(f"✓ Updated {file_path} with Sentry integration")
                updated_count += 1
    
    if updated_count == 0:
        print("✓ No backend files needed updates (already configured or not found)")
    else:
        print(f"✓ Updated {updated_count} backend file(s)")

def update_env_example():
    """Update .env.example with Sentry variables"""
    print_step(4, "Updating .env.example with Sentry configuration")
    
    sentry_env = """
# Sentry Configuration
SENTRY_DSN=your_sentry_dsn_here
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
SENTRY_RELEASE=hiremebahamas@1.0.0
ENVIRONMENT=production
"""
    
    env_example_file = Path('.env.example')
    
    if env_example_file.exists():
        with open(env_example_file, 'r') as f:
            content = f.read()
        
        if 'SENTRY_DSN' not in content:
            with open(env_example_file, 'a') as f:
                f.write(sentry_env)
            print("✓ Added Sentry configuration to .env.example")
        else:
            print("✓ Sentry configuration already in .env.example")
    else:
        with open(env_example_file, 'w') as f:
            f.write(sentry_env)
        print("✓ Created .env.example with Sentry configuration")

def create_env_file():
    """Prompt user to create .env file with Sentry DSN"""
    print_step(5, "Configuring .env file")
    
    env_file = Path('.env')
    
    print("\n📝 To complete Sentry setup, you need to add your Sentry DSN to .env file")
    print("\nYou can find your Sentry DSN at:")
    print("  https://sentry.io/settings/[your-org]/projects/[your-project]/keys/")
    
    if not env_file.exists():
        print("\n.env file not found. Creating one...")
        create_env = input("Would you like to enter your Sentry DSN now? (y/n): ").lower()
        
        if create_env == 'y':
            sentry_dsn = input("Enter your Sentry DSN: ").strip()
            environment = input("Enter environment (default: production): ").strip() or "production"
            
            with open(env_file, 'w') as f:
                f.write(f"SENTRY_DSN={sentry_dsn}\n")
                f.write(f"ENVIRONMENT={environment}\n")
                f.write("SENTRY_TRACES_SAMPLE_RATE=0.1\n")
                f.write("SENTRY_PROFILES_SAMPLE_RATE=0.1\n")
            
            print("✓ Created .env file with Sentry configuration")
        else:
            print("⚠️  Please manually add SENTRY_DSN to your .env file")
    else:
        with open(env_file, 'r') as f:
            content = f.read()
        
        if 'SENTRY_DSN' not in content:
            print("\n.env file exists but missing Sentry DSN")
            add_sentry = input("Would you like to add your Sentry DSN now? (y/n): ").lower()
            
            if add_sentry == 'y':
                sentry_dsn = input("Enter your Sentry DSN: ").strip()
                
                with open(env_file, 'a') as f:
                    f.write(f"\n# Sentry Configuration\n")
                    f.write(f"SENTRY_DSN={sentry_dsn}\n")
                    f.write("SENTRY_TRACES_SAMPLE_RATE=0.1\n")
                    f.write("SENTRY_PROFILES_SAMPLE_RATE=0.1\n")
                
                print("✓ Added Sentry configuration to .env file")
            else:
                print("⚠️  Please manually add SENTRY_DSN to your .env file")
        else:
            print("✓ .env file already has Sentry configuration")

def install_dependencies():
    """Install Python dependencies"""
    print_step(6, "Installing Python dependencies")
    
    print("Installing sentry-sdk...")
    result = run_command("pip install sentry-sdk[flask]==1.39.2")
    
    if result is not None:
        print("✓ Successfully installed sentry-sdk")
    else:
        print("⚠️  Please manually run: pip install sentry-sdk[flask]==1.39.2")

def git_commit_changes():
    """Commit changes to git"""
    print_step(7, "Committing changes to Git")
    
    commit = input("\nWould you like to commit these changes to Git? (y/n): ").lower()
    
    if commit == 'y':
        run_command("git add requirements.txt sentry_config.py .env.example")
        run_command('git commit -m "feat: Add Sentry error tracking integration"')
        
        push = input("Would you like to push to GitHub? (y/n): ").lower()
        if push == 'y':
            run_command("git push")
            print("✓ Pushed changes to GitHub")
        else:
            print("✓ Changes committed locally. Push manually when ready.")
    else:
        print("⚠️  Changes not committed. Commit manually when ready.")

def create_test_endpoint():
    """Create a test file to verify Sentry is working"""
    print_step(8, "Creating Sentry test file")
    
    test_file = """#!/usr/bin/env python3
"""
Sentry Test Script
Run this to verify Sentry is working correctly
"""\nimport os
from sentry_config import init_sentry, capture_message, capture_exception, add_breadcrumb

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_sentry():
    print("\n🧪 Testing Sentry Integration\n")
    
    # Initialize Sentry
    if not init_sentry():
        print("❌ Sentry initialization failed!")
        print("   Make sure SENTRY_DSN is set in your .env file")
        return False
    
    # Test 1: Capture a message
    print("Test 1: Capturing a test message...")
    capture_message("🎉 Sentry test message from HireMeBahamas!", level='info')
    print("✓ Test message sent to Sentry")
    
    # Test 2: Add breadcrumbs
    print("\nTest 2: Adding breadcrumbs...")
    add_breadcrumb("User navigated to test page", category="navigation")
    add_breadcrumb("Test action performed", category="action", data={"test": "value"})
    print("✓ Breadcrumbs added")
    
    # Test 3: Capture an exception
    print("\nTest 3: Capturing a test exception...")
    try:
        # This will trigger an error
        result = 1 / 0
    except Exception as e:
        capture_exception(e)
        print("✓ Test exception sent to Sentry")
    
    print("\n✅ All tests completed!")
    print("\n📊 Check your Sentry dashboard at: https://sentry.io/")
    print("   You should see:")
    print("   - 1 error (division by zero)")
    print("   - 1 message (test message)")
    print("   - Breadcrumbs attached to the error")
    
    return True

if __name__ == "__main__":
    test_sentry()
"""
    
    with open('test_sentry.py', 'w') as f:
        f.write(test_file)
    
    os.chmod('test_sentry.py', 0o755)
    print("✓ Created test_sentry.py")
    
    run_test = input("\nWould you like to run the Sentry test now? (y/n): ").lower()
    if run_test == 'y':
        run_command("python test_sentry.py")

def main():
    """Main installation function"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🔧 SENTRY AUTOMATED INSTALLATION SCRIPT 🔧           ║
║            for HireMeBahamas Platform                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    print("This script will automatically:")
    print("  1. Update requirements.txt with Sentry SDK")
    print("  2. Create Sentry configuration file")
    print("  3. Update backend files with Sentry integration")
    print("  4. Update .env.example with Sentry variables")
    print("  5. Configure your .env file")
    print("  6. Install dependencies")
    print("  7. Commit changes to Git")
    print("  8. Create test file to verify Sentry")
    
    proceed = input("\nProceed with installation? (y/n): ").lower()
    
    if proceed != 'y':
        print("Installation cancelled.")
        sys.exit(0)
    
    try:
        update_requirements()
        create_sentry_config()
        update_backend_files()
        update_env_example()
        create_env_file()
        install_dependencies()
        git_commit_changes()
        create_test_endpoint()
        
        print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         ✅ SENTRY INSTALLATION COMPLETED! ✅             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

📝 Next Steps:
   1. Make sure your SENTRY_DSN is in .env file
   2. Run 'python test_sentry.py' to test the integration
   3. Deploy to Render (changes will auto-deploy)
   4. Check your Sentry dashboard for events

📊 Sentry Dashboard: https://sentry.io/

💡 Tips:
   - Adjust SENTRY_TRACES_SAMPLE_RATE in production (0.1 = 10%)
   - Monitor your error quota in Sentry settings
   - Use sentry_config functions in your code for custom tracking

🎉 Happy monitoring!
""")
        
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()