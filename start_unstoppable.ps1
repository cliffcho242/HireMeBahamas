# HireBahamas AI-Powered UNSTOPPABLE Platform Launcher
# Advanced error prevention and auto-recovery system

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "        🤖 HireBahamas AI-Powered UNSTOPPABLE Platform" -ForegroundColor Green
Write-Host "              Advanced Auto-Fix System" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "🤖 AI INITIALIZATION: Starting advanced error prevention system..." -ForegroundColor Cyan
Write-Host ""
Write-Host "This AI-powered system provides:" -ForegroundColor Yellow
Write-Host "  ✓ Intelligent error prediction and prevention" -ForegroundColor Green
Write-Host "  ✓ Automatic detection and fixing of connection issues" -ForegroundColor Green  
Write-Host "  ✓ Continuous system health monitoring" -ForegroundColor Green
Write-Host "  ✓ Smart recovery protocols with learning capabilities" -ForegroundColor Green
Write-Host "  ✓ Unstoppable platform operation" -ForegroundColor Green
Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta

# Set location and run the AI system
Set-Location "c:\Users\Dell\OneDrive\Desktop\HireBahamas"

try {
    Write-Host "🚀 Launching AI-Powered Platform Manager..." -ForegroundColor Yellow
    & "C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe" unstoppable_platform.py
} catch {
    Write-Host "❌ Error running AI system: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔄 Falling back to standard launcher..." -ForegroundColor Yellow
    
    # Fallback to standard launch
    & ".\launch_complete.bat"
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "              🤖 AI SYSTEM EXECUTION COMPLETE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "The AI-powered platform manager has finished execution." -ForegroundColor White
Write-Host "Your platform should now be running unstoppably!" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  🎯 Application: http://localhost:3001" -ForegroundColor Yellow
Write-Host "  🔧 API Health: http://127.0.0.1:8008/health" -ForegroundColor Yellow
Write-Host "  👤 Admin Login: admin@hirebahamas.com / AdminPass123!" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")