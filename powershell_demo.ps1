# PowerShell Code Runner Demo
# This script demonstrates Code Runner with PowerShell

Write-Host "`n🚀 PowerShell Code Runner Demo" -ForegroundColor Cyan
Write-Host "=" * 35 -ForegroundColor Cyan

# Function to test Code Runner
function Test-CodeRunner {
    param(
        [string]$Message
    )
    
    Write-Host "`n📝 Testing: $Message" -ForegroundColor Yellow
    
    # Simulate some work
    for ($i = 1; $i -le 3; $i++) {
        Write-Host "   Step $i..." -ForegroundColor Gray
        Start-Sleep -Milliseconds 500
    }
    
    Write-Host "   ✅ Completed!" -ForegroundColor Green
}

# Main execution
Write-Host "`nStarting PowerShell tests..." -ForegroundColor White

Test-CodeRunner "File operations"
Test-CodeRunner "Network connectivity" 
Test-CodeRunner "System information"

# System info
Write-Host "`n📊 System Information:" -ForegroundColor Magenta
Write-Host "   PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor Gray
Write-Host "   Current Directory: $(Get-Location)" -ForegroundColor Gray
Write-Host "   Current User: $env:USERNAME" -ForegroundColor Gray

Write-Host "`n🎉 PowerShell demo completed successfully!" -ForegroundColor Green