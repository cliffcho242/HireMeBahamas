##############################################################################
#  HireBahamas Permanent Server Manager
##############################################################################

param(
    [switch]$Install,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status
)

$ErrorActionPreference = "Stop"

# Configuration
$BACKEND_PORT = 8008
$FRONTEND_PORT = 3000
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_SCRIPT = Join-Path $PROJECT_ROOT "clean_backend.py"
$FRONTEND_DIR = Join-Path $PROJECT_ROOT "frontend"
$LOG_FILE = Join-Path $PROJECT_ROOT "server_manager.log"

# Logging function
function Write-Log {
    param($Message, $Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $LOG_FILE -Append
    Write-Host $Message -ForegroundColor $Color
}

# Check if port is in use
function Test-PortInUse {
    param($Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $connection -ne $null
    } catch {
        return $false
    }
}

# Kill process on port
function Stop-ProcessOnPort {
    param($Port, $Name)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connection) {
            $processId = $connection.OwningProcess
            Write-Log "[WARNING] Stopping $Name process (PID: $processId) on port $Port" "Yellow"
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Write-Log "[SUCCESS] $Name process stopped" "Green"
            return $true
        }
    } catch {
        Write-Log "[WARNING] Could not stop process on port $Port" "Yellow"
    }
    return $false
}

# Test if backend is responding
function Test-Backend {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$BACKEND_PORT/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Test if frontend is responding
function Test-Frontend {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$FRONTEND_PORT" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Start backend server
function Start-Backend {
    Write-Log "[INFO] Starting backend server..." "Cyan"
    
    # Kill any existing process on the port
    if (Test-PortInUse -Port $BACKEND_PORT) {
        Stop-ProcessOnPort -Port $BACKEND_PORT -Name "Backend"
    }
    
    # Start new process
    $process = Start-Process -FilePath "python" -ArgumentList $BACKEND_SCRIPT `
        -WorkingDirectory $PROJECT_ROOT `
        -WindowStyle Minimized `
        -PassThru
    
    Write-Log "[INFO] Backend started with PID: $($process.Id)" "Cyan"
    
    # Wait and verify
    Start-Sleep -Seconds 5
    
    if (Test-Backend) {
        Write-Log "[SUCCESS] Backend is running on port $BACKEND_PORT" "Green"
        return $true
    } else {
        Write-Log "[ERROR] Backend failed to start properly" "Red"
        return $false
    }
}

# Start frontend server
function Start-Frontend {
    Write-Log "[INFO] Starting frontend server..." "Cyan"
    
    # Kill any existing process on the port
    if (Test-PortInUse -Port $FRONTEND_PORT) {
        Stop-ProcessOnPort -Port $FRONTEND_PORT -Name "Frontend"
    }
    
    # Start new process
    $process = Start-Process -FilePath "powershell" `
        -ArgumentList "-NoExit", "-Command", "cd '$FRONTEND_DIR'; npm run dev" `
        -WindowStyle Minimized `
        -PassThru
    
    Write-Log "[INFO] Frontend started with PID: $($process.Id)" "Cyan"
    
    # Wait and verify
    Start-Sleep -Seconds 10
    
    if (Test-Frontend) {
        Write-Log "[SUCCESS] Frontend is running on port $FRONTEND_PORT" "Green"
        return $true
    } else {
        Write-Log "[ERROR] Frontend failed to start properly" "Red"
        return $false
    }
}

# Stop all servers
function Stop-AllServers {
    Write-Log "[INFO] Stopping all servers..." "Cyan"
    
    Stop-ProcessOnPort -Port $BACKEND_PORT -Name "Backend"
    Stop-ProcessOnPort -Port $FRONTEND_PORT -Name "Frontend"
    
    # Kill all node and python processes related to the project
    Get-Process | Where-Object { $_.ProcessName -like "*node*" -or $_.ProcessName -like "*python*" } | ForEach-Object {
        try {
            if ($_.Path -like "*$PROJECT_ROOT*") {
                Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            }
        } catch {}
    }
    
    Write-Log "[SUCCESS] All servers stopped" "Green"
}

# Check server status
function Get-ServerStatus {
    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host "   HireBahamas Server Status" -ForegroundColor Cyan
    Write-Host "==========================================`n" -ForegroundColor Cyan
    
    # Backend status
    Write-Host "Backend (Port $BACKEND_PORT):" -ForegroundColor Yellow
    if (Test-Backend) {
        Write-Host "  [SUCCESS] Status: Running" -ForegroundColor Green
        Write-Host "  URL: http://127.0.0.1:$BACKEND_PORT" -ForegroundColor White
    } else {
        Write-Host "  [ERROR] Status: Not Running" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Frontend status
    Write-Host "Frontend (Port $FRONTEND_PORT):" -ForegroundColor Yellow
    if (Test-Frontend) {
        Write-Host "  [SUCCESS] Status: Running" -ForegroundColor Green
        Write-Host "  URL: http://localhost:$FRONTEND_PORT" -ForegroundColor White
    } else {
        Write-Host "  [ERROR] Status: Not Running" -ForegroundColor Red
    }
    
    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host ""
}

# Install as startup task
function Install-StartupTask {
    Write-Log "[INFO] Installing HireBahamas as startup task..." "Cyan"
    
    $scriptPath = $MyInvocation.MyCommand.Path
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -Start"
    
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    try {
        Register-ScheduledTask -TaskName "HireBahamas Auto-Start" `
            -Action $action `
            -Trigger $trigger `
            -Principal $principal `
            -Settings $settings `
            -Force | Out-Null
        
        Write-Log "[SUCCESS] Startup task installed successfully" "Green"
        Write-Log "[INFO] Servers will auto-start when you log in" "Cyan"
    } catch {
        Write-Log "[ERROR] Failed to install startup task: $_" "Red"
    }
}

# Main execution
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "  HireBahamas Permanent Server Manager" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

if ($Install) {
    Install-StartupTask
    Write-Host "Starting servers now...`n"
    Stop-AllServers
    Start-Sleep -Seconds 2
    $backendOk = Start-Backend
    $frontendOk = Start-Frontend
    
    if ($backendOk -and $frontendOk) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "  Installation Complete!" -ForegroundColor Green
        Write-Host "  Servers are running!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access your app at: http://localhost:$FRONTEND_PORT" -ForegroundColor Cyan
        Write-Host "Servers will auto-start on login" -ForegroundColor Yellow
        Write-Host ""
    }
}
elseif ($Start) {
    Stop-AllServers
    Start-Sleep -Seconds 2
    Start-Backend
    Start-Frontend
    Get-ServerStatus
}
elseif ($Stop) {
    Stop-AllServers
}
elseif ($Status) {
    Get-ServerStatus
}
else {
    # No parameter - show help
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\permanent_solution.ps1 -Install     Install and start servers" -ForegroundColor White
    Write-Host "  .\permanent_solution.ps1 -Start       Start servers manually" -ForegroundColor White
    Write-Host "  .\permanent_solution.ps1 -Stop        Stop all servers" -ForegroundColor White
    Write-Host "  .\permanent_solution.ps1 -Status      Check server status" -ForegroundColor White
    Write-Host ""
    Write-Host "Recommended: Run with -Install for permanent solution" -ForegroundColor Yellow
    Write-Host ""
}
