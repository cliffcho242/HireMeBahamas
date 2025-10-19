# HireBahamas Complete Launch Script
Write-Host "Starting HireBahamas Platform..." -ForegroundColor Green

# Start backend in new window
Write-Host "Launching backend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd 'c:\Users\Dell\OneDrive\Desktop\HireBahamas'; python final_backend.py; pause"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window  
Write-Host "Launching frontend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd 'c:\Users\Dell\OneDrive\Desktop\HireBahamas\frontend'; npm run dev; pause"

# Wait for frontend to start
Start-Sleep -Seconds 5

# Check backend health
Write-Host "Checking backend health..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8008/health" -Method GET
    Write-Host "Backend Status: $($health.status)" -ForegroundColor Green
    Write-Host "Database: $($health.database)" -ForegroundColor Green
} catch {
    Write-Host "Backend not responding yet..." -ForegroundColor Red
}

# Open browser to frontend
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3001"

Write-Host "`nPlatform launched successfully!" -ForegroundColor Green
Write-Host "Backend: http://127.0.0.1:8008" -ForegroundColor White
Write-Host "Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "Admin Login: admin@hirebahamas.com / AdminPass123!" -ForegroundColor White

pause