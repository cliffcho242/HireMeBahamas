@echo off
REM ================================================================
REM HireMeBahamas - Complete Dependency Installation Script (Windows)
REM ================================================================
REM This script installs ALL dependencies for the HireMeBahamas
REM application on Windows with ZERO manual intervention.
REM
REM Prerequisites:
REM   - Chocolatey package manager (will be installed if missing)
REM   - Administrator privileges
REM
REM Usage: install_all_dependencies.bat [options]
REM Options:
REM   /help          Show this help message
REM   /skip-system   Skip system package installation
REM   /skip-python   Skip Python package installation
REM   /skip-node     Skip Node.js package installation
REM ================================================================

setlocal EnableDelayedExpansion

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%\.."
set "LOG_FILE=%PROJECT_ROOT%\installation.log"
set "SKIP_SYSTEM=0"
set "SKIP_PYTHON=0"
set "SKIP_NODE=0"

REM Colors (limited in cmd, using echo for now)
set "COLOR_SUCCESS=[92m"
set "COLOR_ERROR=[91m"
set "COLOR_WARNING=[93m"
set "COLOR_INFO=[94m"
set "COLOR_RESET=[0m"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :after_args
if /i "%~1"=="/help" (
    type "%~f0" | findstr /R "^REM"
    exit /b 0
)
if /i "%~1"=="/skip-system" (
    set "SKIP_SYSTEM=1"
    shift
    goto :parse_args
)
if /i "%~1"=="/skip-python" (
    set "SKIP_PYTHON=1"
    shift
    goto :parse_args
)
if /i "%~1"=="/skip-node" (
    set "SKIP_NODE=1"
    shift
    goto :parse_args
)
echo Unknown option: %~1
echo Use /help for usage information
exit /b 1
:after_args

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ERROR: This script requires administrator privileges
    echo Please run as administrator
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   HireMeBahamas - Complete Dependency Installation (Windows)
echo ================================================================================
echo.
echo Log file: %LOG_FILE%
echo.

REM Start logging
echo Installation started at %date% %time% > "%LOG_FILE%"

REM Check if Chocolatey is installed
call :print_header "Checking Chocolatey Package Manager"
where choco >nul 2>&1
if %errorLevel% neq 0 (
    call :print_info "Chocolatey not found. Installing..."
    
    REM Install Chocolatey
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    
    if %errorLevel% neq 0 (
        call :print_error "Failed to install Chocolatey"
        exit /b 1
    )
    
    REM Refresh environment
    call refreshenv
    call :print_success "Chocolatey installed successfully"
) else (
    call :print_success "Chocolatey is already installed"
)

REM Install system dependencies
if %SKIP_SYSTEM% equ 0 (
    call :print_header "Installing System Dependencies"
    
    call :print_progress "Installing Python..."
    choco install python --version=3.12.0 -y
    
    call :print_progress "Installing Node.js..."
    choco install nodejs-lts -y
    
    call :print_progress "Installing PostgreSQL..."
    choco install postgresql15 -y --params '/Password:postgres'
    
    call :print_progress "Installing Redis..."
    choco install redis-64 -y
    
    call :print_progress "Installing Git..."
    choco install git -y
    
    call :print_progress "Installing build tools..."
    choco install visualstudio2022buildtools -y
    choco install visualstudio2022-workload-vctools -y
    
    call refreshenv
    call :print_success "System dependencies installed"
) else (
    call :print_warning "Skipping system dependencies (/skip-system)"
)

REM Install Python dependencies
if %SKIP_PYTHON% equ 0 (
    call :print_header "Installing Python Dependencies"
    
    REM Ensure pip is up to date
    call :print_progress "Upgrading pip..."
    python -m pip install --upgrade pip
    
    REM Install from requirements.txt
    if exist "%PROJECT_ROOT%\requirements.txt" (
        call :print_progress "Installing Python packages from requirements.txt..."
        pip install -r "%PROJECT_ROOT%\requirements.txt"
        call :print_success "Python dependencies installed"
    ) else (
        call :print_warning "requirements.txt not found"
    )
    
    REM Install additional packages
    call :print_progress "Installing additional Python packages..."
    pip install psycopg2-binary redis sentry-sdk gunicorn flask-cors flask-limiter flask-caching flask-socketio flask-compress flask-talisman python-dotenv bcrypt pyjwt
    
    call :print_success "All Python dependencies installed"
) else (
    call :print_warning "Skipping Python dependencies (/skip-python)"
)

REM Install Node.js dependencies
if %SKIP_NODE% equ 0 (
    call :print_header "Installing Node.js Dependencies"
    
    REM Check Node.js version
    call :print_info "Checking Node.js version..."
    node --version
    npm --version
    
    REM Install global packages
    call :print_progress "Installing global npm packages..."
    call npm install -g vite
    
    REM Install root dependencies
    if exist "%PROJECT_ROOT%\package.json" (
        call :print_progress "Installing root npm dependencies..."
        cd /d "%PROJECT_ROOT%"
        call npm install
    )
    
    REM Install frontend dependencies
    if exist "%PROJECT_ROOT%\frontend" (
        call :print_progress "Installing frontend dependencies..."
        cd /d "%PROJECT_ROOT%\frontend"
        call npm install --legacy-peer-deps
        call :print_success "Frontend dependencies installed"
        cd /d "%PROJECT_ROOT%"
    ) else (
        call :print_warning "Frontend directory not found"
    )
) else (
    call :print_warning "Skipping Node.js dependencies (/skip-node)"
)

REM Configure services
call :print_header "Configuring Services"

call :print_progress "Starting PostgreSQL service..."
net start postgresql-x64-15 2>nul
if %errorLevel% neq 0 (
    call :print_warning "PostgreSQL service may already be running or not installed"
) else (
    call :print_success "PostgreSQL service started"
)

call :print_progress "Starting Redis service..."
net start Redis 2>nul
if %errorLevel% neq 0 (
    call :print_warning "Redis service may already be running or not installed"
) else (
    call :print_success "Redis service started"
)

REM Create database
call :print_progress "Creating database..."
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE hiremebahamas;" 2>nul
if %errorLevel% neq 0 (
    call :print_info "Database may already exist"
) else (
    call :print_success "Database created"
)

REM Create environment files
call :print_header "Creating Environment Files"

if not exist "%PROJECT_ROOT%\backend\.env" (
    call :print_progress "Creating backend\.env file..."
    (
        echo DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hiremebahamas
        echo SECRET_KEY=change-this-to-a-secure-random-key-in-production
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=43200
        echo REDIS_URL=redis://localhost:6379
        echo ENVIRONMENT=development
        echo # Add your Cloudinary credentials:
        echo # CLOUDINARY_NAME=your_cloudinary_name
        echo # CLOUDINARY_API_KEY=your_api_key
        echo # CLOUDINARY_API_SECRET=your_api_secret
    ) > "%PROJECT_ROOT%\backend\.env"
    call :print_success "Backend .env file created"
) else (
    call :print_info "Backend .env file already exists"
)

if not exist "%PROJECT_ROOT%\frontend\.env" (
    call :print_progress "Creating frontend\.env file..."
    (
        echo VITE_API_URL=http://localhost:8000
        echo VITE_SOCKET_URL=http://localhost:8000
        echo # Add your Cloudinary cloud name:
        echo # VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name
    ) > "%PROJECT_ROOT%\frontend\.env"
    call :print_success "Frontend .env file created"
) else (
    call :print_info "Frontend .env file already exists"
)

REM Verify installation
call :print_header "Verifying Installation"

if exist "%SCRIPT_DIR%\verify_installation.py" (
    call :print_progress "Running verification script..."
    python "%SCRIPT_DIR%\verify_installation.py"
) else (
    call :print_info "Running basic verification..."
    
    python --version
    if %errorLevel% neq 0 (
        call :print_error "Python not found"
    ) else (
        call :print_success "Python installed"
    )
    
    node --version
    if %errorLevel% neq 0 (
        call :print_error "Node.js not found"
    ) else (
        call :print_success "Node.js installed"
    )
    
    npm --version
    if %errorLevel% neq 0 (
        call :print_error "npm not found"
    ) else (
        call :print_success "npm installed"
    )
)

REM Final summary
call :print_header "Installation Complete!"

echo.
echo All dependencies installed successfully!
echo.
echo Next Steps:
echo   1. Review and update environment variables in:
echo      - backend\.env
echo      - frontend\.env
echo.
echo   2. Start the backend server:
echo      cd backend ^&^& python app.py
echo.
echo   3. Start the frontend development server:
echo      cd frontend ^&^& npm run dev
echo.
echo   4. Visit: http://localhost:3000
echo.
echo Service Status:
echo   PostgreSQL: localhost:5432
echo   Redis: localhost:6379
echo.
echo Troubleshooting:
echo   - Check logs: type %LOG_FILE%
echo   - Verify installation: python scripts\verify_installation.py
echo.

echo Installation completed at %date% %time% >> "%LOG_FILE%"

pause
exit /b 0

REM ================================================================
REM Helper Functions
REM ================================================================

:print_header
echo.
echo ================================================================================
echo   %~1
echo ================================================================================
echo.
echo [%date% %time%] === %~1 === >> "%LOG_FILE%"
exit /b 0

:print_success
echo [OK] %~1
echo [SUCCESS] %~1 >> "%LOG_FILE%"
exit /b 0

:print_error
echo [ERROR] %~1
echo [ERROR] %~1 >> "%LOG_FILE%"
exit /b 0

:print_warning
echo [WARN] %~1
echo [WARNING] %~1 >> "%LOG_FILE%"
exit /b 0

:print_info
echo [INFO] %~1
echo [INFO] %~1 >> "%LOG_FILE%"
exit /b 0

:print_progress
echo [*] %~1
echo [PROGRESS] %~1 >> "%LOG_FILE%"
exit /b 0
