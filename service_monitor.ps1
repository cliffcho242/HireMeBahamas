# HireBahamas Service Monitor and Auto-Restart
# Monitors both backend and frontend services and restarts them if they fail

param(
    [int]$CheckInterval = 30,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"
$White = "White"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-Port {
    param([int]$Port)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("127.0.0.1", $Port)
        $tcpClient.Close()
        return $true
    } catch {
        return $false
    }
}

function Test-BackendHealth {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8008/api/health" -Method GET -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            return $data.status -eq "healthy"
        }
    } catch {
        if ($Verbose) {
            Write-ColorOutput "Backend health check failed: $($_.Exception.Message)" $Red
        }
    }
    return $false
}

function Restart-Backend {
    Write-ColorOutput "🔄 Restarting Backend Server..." $Yellow

    # Kill existing Python processes
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # Start backend
    $backendScript = Join-Path $ProjectRoot "ULTIMATE_BACKEND_FIXED.py"
    $venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

    if (Test-Path $venvPython) {
        $pythonCmd = $venvPython
    } else {
        $pythonCmd = "python"
    }

    $pythonwCmd = $pythonCmd -replace "python.exe", "pythonw.exe"
    if (Test-Path $pythonwCmd) {
        Start-Process -FilePath $pythonwCmd -ArgumentList $backendScript -NoNewWindow
        Write-ColorOutput "Backend restarted with pythonw.exe" $Green
    } else {
        Start-Process -FilePath $pythonCmd -ArgumentList $backendScript -NoNewWindow
        Write-ColorOutput "Backend restarted with python.exe" $Green
    }
}

function Restart-Frontend {
    Write-ColorOutput "🔄 Restarting Frontend Server..." $Yellow

    # Kill existing Node processes
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # Start frontend using the force launcher
    $frontendDir = Join-Path $ProjectRoot "frontend"
    $forceScript = Join-Path $frontendDir "force_frontend_dev.ps1"

    Push-Location $frontendDir
    try {
        Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $forceScript, "-PrimaryPort", "3000", "-CleanCache" -NoNewWindow
        Write-ColorOutput "Frontend restart initiated with force launcher" $Green
    } finally {
        Pop-Location
    }
}

function Show-Status {
    $backendUp = Test-Port 8008
    $frontendUp = Test-Port 3000
    $backendHealthy = if ($backendUp) { Test-BackendHealth } else { $false }

    Write-ColorOutput "`n📊 SERVICE STATUS $(Get-Date -Format 'HH:mm:ss')" $Cyan
    Write-ColorOutput "=" * 50 $White

    $backendStatus = if ($backendHealthy) { "✅ HEALTHY" } elseif ($backendUp) { "⚠️ RUNNING (UNHEALTHY)" } else { "❌ DOWN" }
    Write-ColorOutput "Backend (Port 8008): $backendStatus" $(if ($backendHealthy) { $Green } elseif ($backendUp) { $Yellow } else { $Red })

    $frontendStatus = if ($frontendUp) { "✅ RUNNING" } else { "❌ DOWN" }
    Write-ColorOutput "Frontend (Port 3000): $frontendStatus" $(if ($frontendUp) { $Green } else { $Red })

    return @{
        BackendHealthy = $backendHealthy
        BackendUp = $backendUp
        FrontendUp = $frontendUp
    }
}

# Main monitoring loop
Write-ColorOutput "🤖 HireBahamas Service Monitor Started" $Cyan
Write-ColorOutput "Checking services every $CheckInterval seconds..." $White
Write-ColorOutput "Press Ctrl+C to stop monitoring" $Yellow

$restartCount = @{
    Backend = 0
    Frontend = 0
}

while ($true) {
    $status = Show-Status

    # Check backend
    if (-not $status.BackendHealthy) {
        Write-ColorOutput "Backend is not healthy, restarting..." $Red
        Restart-Backend
        $restartCount.Backend++
        Start-Sleep -Seconds 10  # Wait for restart
    }

    # Check frontend
    if (-not $status.FrontendUp) {
        Write-ColorOutput "Frontend is not running, restarting..." $Red
        Restart-Frontend
        $restartCount.Frontend++
        Start-Sleep -Seconds 15  # Wait for restart
    }

    # Show restart stats
    if ($restartCount.Backend -gt 0 -or $restartCount.Frontend -gt 0) {
        Write-ColorOutput "🔄 Restarts: Backend=$($restartCount.Backend), Frontend=$($restartCount.Frontend)" $Yellow
    }

    # Wait for next check
    if ($Verbose) {
        Write-ColorOutput "Next check in $CheckInterval seconds..." $White
    }
    Start-Sleep -Seconds $CheckInterval
}

# This shouldn't be reached, but just in case
Write-ColorOutput "Monitor stopped" $Yellow