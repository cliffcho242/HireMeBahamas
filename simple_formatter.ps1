# Simple Automated Code Formatter
Write-Host "🚀 AUTOMATED CODE FORMATTER" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

# Format Python files with Black
Write-Host "`n🐍 Formatting Python files..." -ForegroundColor Yellow
try {
    $pythonFiles = Get-ChildItem -Recurse -Filter "*.py" | Where-Object { $_.FullName -notmatch "__pycache__|\.git|node_modules" }
    if ($pythonFiles.Count -gt 0) {
        Write-Host "   Found $($pythonFiles.Count) Python files" -ForegroundColor White
        C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/python.exe -m black --line-length 88 .
        Write-Host "   ✅ Python files formatted with Black" -ForegroundColor Green
    } else {
        Write-Host "   No Python files found" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Error formatting Python files: $($_.Exception.Message)" -ForegroundColor Red
}

# Format JavaScript/TypeScript files with Prettier
Write-Host "`n📝 Formatting JS/TS files..." -ForegroundColor Yellow
try {
    $jsFiles = Get-ChildItem -Recurse -Include "*.js", "*.ts", "*.jsx", "*.tsx", "*.json" | Where-Object { $_.FullName -notmatch "node_modules|\.git|dist" }
    if ($jsFiles.Count -gt 0) {
        Write-Host "   Found $($jsFiles.Count) JS/TS files" -ForegroundColor White
        if (Test-Path "frontend") {
            Set-Location "frontend"
            npx prettier --write 'src/**/*.{js,ts,jsx,tsx,json,css}'
            Set-Location ".."
            Write-Host "   ✅ Frontend files formatted with Prettier" -ForegroundColor Green
        }
    } else {
        Write-Host "   No JS/TS files found" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Error formatting JS/TS files: $($_.Exception.Message)" -ForegroundColor Red
}

# Organize Python imports
Write-Host "`n📚 Organizing Python imports..." -ForegroundColor Yellow
try {
    C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/python.exe -m isort --profile black .
    Write-Host "   ✅ Python imports organized" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Could not organize imports" -ForegroundColor Yellow
}

Write-Host "`n🎉 Code formatting completed!" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Cyan