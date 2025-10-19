# HireBahamas Startup Script
# This script automatically starts both backend and frontend servers

Write-Host "🚀 Starting HireBahamas Application..." -ForegroundColor Green

# Change to project directory
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectPath

Write-Host "📁 Project directory: $projectPath" -ForegroundColor Cyan

# Kill any existing processes
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend server
Write-Host "🔧 Starting backend server..." -ForegroundColor Blue
$backendJob = Start-Job -ScriptBlock {
    param($projectPath)
    Set-Location $projectPath
    & ".\.venv\Scripts\Activate.ps1"
    Set-Location "backend"
    python -m app.main
} -ArgumentList $projectPath

# Wait a moment for backend to start
Start-Sleep -Seconds 5

# Start frontend server
Write-Host "🌐 Starting frontend server..." -ForegroundColor Magenta  
$frontendJob = Start-Job -ScriptBlock {
    param($projectPath)
    Set-Location "$projectPath\frontend"
    npm run dev
} -ArgumentList $projectPath

# Wait for both servers to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ HireBahamas Application Started Successfully!" -ForegroundColor Green
Write-Host "📊 Backend API: http://localhost:8005" -ForegroundColor Cyan
Write-Host "📋 API Documentation: http://localhost:8005/docs" -ForegroundColor Cyan  
Write-Host "🌐 Frontend Application: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to stop all servers..." -ForegroundColor Yellow

# Wait for user input
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop servers
Write-Host ""
Write-Host "🛑 Stopping servers..." -ForegroundColor Red
Stop-Job $backendJob -ErrorAction SilentlyContinue
Stop-Job $frontendJob -ErrorAction SilentlyContinue
Remove-Job $backendJob -ErrorAction SilentlyContinue  
Remove-Job $frontendJob -ErrorAction SilentlyContinue

# Kill any remaining processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "✅ All servers stopped successfully!" -ForegroundColor Green