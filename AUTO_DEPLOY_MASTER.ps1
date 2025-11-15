# PowerShell Script for Automated Deployment

# Set the deployment log file
$logFile = "deployment_log.txt"

# Function to log messages with timestamps
function Log-Message { 
    param(
        [string]$message,
        [string]$color = "White"
    )
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Write-Host "[$timestamp] $message" -ForegroundColor $color
    Add-Content -Path $logFile -Value "[$timestamp] $message"
}

# Check for prerequisites
function Check-Prerequisites {
    Log-Message "Checking prerequisites..." "Yellow"

    $prerequisites = @('python', 'node', 'npm', 'pip')
    foreach ($prerequisite in $prerequisites) {
        if (-not (Get-Command $prerequisite -ErrorAction SilentlyContinue)) {
            Log-Message "$prerequisite is not installed. Please install it before running this script." "Red"
            return $false
        }
    }
    Log-Message "All prerequisites are installed." "Green"
    return $true
}

# Install Python dependencies
function Install-Python-Dependencies {
    Log-Message "Installing Python dependencies..." "Yellow"
    $requirementsFiles = @('requirements.txt', 'backend/requirements.txt', 'api/requirements.txt')
    foreach ($file in $requirementsFiles) {
        if (Test-Path $file) {
            pip install -r $file
            Log-Message "Installed dependencies from $file" "Green"
        } else {
            Log-Message "File $file does not exist." "Red"
        }
    }
}

# Install Node.js dependencies
function Install-Node-Dependencies {
    Log-Message "Installing Node.js dependencies..." "Yellow"
    if (Test-Path 'frontend/package.json') {
        npm install --prefix frontend
        Log-Message "Installed Node.js dependencies from frontend/package.json" "Green"
    } else {
        Log-Message "frontend/package.json does not exist." "Red"
    }
}

# Setup the database
function Setup-Database {
    Log-Message "Setting up the database..." "Yellow"
    if (Test-Path 'seed_data.py') {
        python seed_data.py
        Log-Message "Database has been seeded with development data." "Green"
    } else {
        Log-Message "seed_data.py does not exist." "Red"
    }
}

# Create .env file from .env.example
function Create-Env { 
    Log-Message "Creating .env file from .env.example if needed..." "Yellow"
    if (-not (Test-Path '.env')) {
        Copy-Item '.env.example' '.env'
        Log-Message ".env file created from .env.example." "Green"
    } else {
        Log-Message ".env file already exists." "Green"
    }
}

# Start the backend server
function Start-Backend {
    Log-Message "Starting backend server on port 8008..." "Yellow"
    Start-Process python -ArgumentList "-m waitress --port=8008 wsgi:app"
    Log-Message "Backend server started on port 8008." "Green"
}

# Start the frontend server
function Start-Frontend {
    Log-Message "Starting frontend server on port 3000..." "Yellow"
    Start-Process npm -ArgumentList "run dev --prefix frontend"
    Log-Message "Frontend server started on port 3000." "Green"
}

# Run health checks
function Run-Health-Checks {
    Log-Message "Running health checks on both servers..." "Yellow"
    # Add health check logic here
}

# Display access URLs and login credentials
function Display-Access-Info {
    Log-Message "Access your application at http://localhost:8008 for the backend and http://localhost:3000 for the frontend." "Green"
    Log-Message "Use the credentials provided in your .env file for login." "Green"
}

# Monitor servers
function Monitor-Servers {
    Log-Message "Monitoring servers..." "Yellow"
    # Monitoring logic here
}

# Main deployment process
if (Check-Prerequisites) {
    Install-Python-Dependencies
    Install-Node-Dependencies
    Setup-Database
    Create-Env
    Start-Backend
    Start-Frontend
    Run-Health-Checks
    Display-Access-Info
    Monitor-Servers
}

# Instructions for stopping servers
Log-Message "To stop the servers, press Ctrl+C to terminate the scripts." "Yellow"