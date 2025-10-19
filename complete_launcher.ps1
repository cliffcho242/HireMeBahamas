# HireBahamas Complete Platform Launcher
# Simple launcher that starts both services

param(
    [switch]$Monitor,
    [switch]$CleanCache,
    [switch]$Verbose
)

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

# Main execution
Write-ColorOutput "🎯 HireBahamas Platform Launcher" $Cyan
Write-ColorOutput "=" * 50 $White

Write-ColorOutput "🚀 Starting Backend Server..." $Cyan
# Kill existing Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend
$backendScript = Join-Path $ProjectRoot "ULTIMATE_BACKEND_FIXED.py"
Start-Process -FilePath "python" -ArgumentList $backendScript -NoNewWindow
Write-ColorOutput "✅ Backend started" $Green

Write-ColorOutput "🚀 Starting Frontend Server..." $Cyan
# Kill existing Node processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start frontend using force launcher
$frontendDir = Join-Path $ProjectRoot "frontend"
$forceScript = Join-Path $frontendDir "force_frontend_dev.ps1"

Push-Location $frontendDir
try {
    $launchArgs = @("-ExecutionPolicy", "Bypass", "-File", $forceScript, "-PrimaryPort", "3000")
    if ($CleanCache) {
        $launchArgs += "-CleanCache"
    }
    if ($Verbose) {
        $launchArgs += "-Verbose"
    }

    Start-Process -FilePath "powershell" -ArgumentList $launchArgs -NoNewWindow
    Write-ColorOutput "✅ Frontend started with force launcher" $Green
} finally {
    Pop-Location
}

Write-ColorOutput "`n🎉 Services starting up!" $Green
Write-ColorOutput "🌐 Frontend: http://localhost:3000" $Cyan
Write-ColorOutput "🔧 Backend: http://localhost:8008" $Cyan

if ($Monitor) {
    Write-ColorOutput "`n🔍 Starting service monitoring..." $Yellow
    $monitorScript = Join-Path $ProjectRoot "service_monitor.ps1"
    $launchArgs = @("-ExecutionPolicy", "Bypass", "-File", $monitorScript)
    if ($Verbose) {
        $launchArgs += "-Verbose"
    }
    Start-Process -FilePath "powershell" -ArgumentList $launchArgs -NoNewWindow
    Write-ColorOutput "✅ Platform is now running with monitoring" $Green
}

Write-ColorOutput "`n🚀 HireBahamas Platform is starting!" $Green