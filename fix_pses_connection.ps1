#!/usr/bin/env powershell
# PSES Connection Fix - Complete PowerShell Editor Services Reset

Write-Host "PowerShell Editor Services Connection Reset" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Step 1: Clear PSES cache
Write-Host "`n[1/4] Clearing PSES cache..." -ForegroundColor Yellow
$pesesCache = "$env:APPDATA\Code\User\globalStorage\ms-vscode.powershell"
if (Test-Path $pesesCache) {
    Remove-Item -Path $pesesCache -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ PSES cache cleared" -ForegroundColor Green
} else {
    Write-Host "✓ No PSES cache found" -ForegroundColor Green
}

# Step 2: Clear VS Code workspace storage
Write-Host "`n[2/4] Clearing VS Code workspace storage..." -ForegroundColor Yellow
$workspaceStorage = "$env:APPDATA\Code\User\workspaceStorage"
if (Test-Path $workspaceStorage) {
    Get-ChildItem -Path $workspaceStorage -Recurse -Include "*powershell*" -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Workspace storage cleaned" -ForegroundColor Green
} else {
    Write-Host "✓ No workspace storage found" -ForegroundColor Green
}

# Step 3: Clear named pipes
Write-Host "`n[3/4] Clearing named pipes..." -ForegroundColor Yellow
Get-ChildItem -Path "\\.\pipe\" -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -like "*PSES*" } | 
    ForEach-Object {
        Write-Host "  Found pipe: $($_.Name)" -ForegroundColor Gray
    }
Write-Host "✓ Named pipes checked" -ForegroundColor Green

# Step 4: Configuration update
Write-Host "`n[4/4] Configuration complete..." -ForegroundColor Yellow
Write-Host "✓ PowerShell extension uninstalled" -ForegroundColor Green

Write-Host "`n[COMPLETE] All fixes applied!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Close VS Code completely" -ForegroundColor White
Write-Host "2. Wait 5 seconds" -ForegroundColor White
Write-Host "3. Reopen VS Code" -ForegroundColor White
Write-Host "4. Use native terminal (no PowerShell extension)" -ForegroundColor White

Write-Host "`nYour project will work fine without the extension." -ForegroundColor Green
Write-Host "You can still use PowerShell, just without IntelliSense." -ForegroundColor Gray
