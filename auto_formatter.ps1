# Automated Code Formatter - PowerShell Version
# This script formats all code files in the workspace

param(
    [string]$WorkspaceRoot = ".",
    [switch]$PythonOnly,
    [switch]$JSOnly,
    [switch]$AllFiles
)

Write-Host "`n🚀 AUTOMATED CODE FORMATTER" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "=" * 50 -ForegroundColor Cyan

$stats = @{
    formatted = 0
    errors = 0
    skipped = 0
}

function Format-PythonFiles {
    Write-Host "`n🐍 Formatting Python files..." -ForegroundColor Yellow
    
    $pythonFiles = Get-ChildItem -Path $WorkspaceRoot -Recurse -Filter "*.py" | Where-Object {
        $_.FullName -notmatch "(__pycache__|\.git|node_modules|venv|\.venv)"
    }
    
    if ($pythonFiles.Count -eq 0) {
        Write-Host "   No Python files found" -ForegroundColor Gray
        return
    }
    
    Write-Host "   Found $($pythonFiles.Count) Python files" -ForegroundColor White
    
    # Try Black formatter
    try {
        $blackResult = python -m black --line-length 88 --quiet $WorkspaceRoot 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Formatted with Black" -ForegroundColor Green
            $script:stats.formatted += $pythonFiles.Count
        } else {
            throw "Black failed"
        }
    }
    catch {
        Write-Host "   ⚠️ Black failed, trying autopep8..." -ForegroundColor Yellow
        
        foreach ($file in $pythonFiles) {
            try {
                python -m autopep8 --in-place --aggressive --aggressive --max-line-length 88 $file.FullName
                $script:stats.formatted++
            }
            catch {
                Write-Host "     ❌ Failed to format: $($file.Name)" -ForegroundColor Red
                $script:stats.errors++
            }
        }
    }
    
    # Organize imports with isort
    try {
        Write-Host "   📚 Organizing imports..." -ForegroundColor Cyan
        python -m isort --profile black --line-length 88 $WorkspaceRoot 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Imports organized" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "   ⚠️ isort not available" -ForegroundColor Yellow
    }
}

function Format-JavaScriptFiles {
    Write-Host "`n📝 Formatting JavaScript/TypeScript files..." -ForegroundColor Yellow
    
    $jsFiles = Get-ChildItem -Path $WorkspaceRoot -Recurse -Include "*.js", "*.ts", "*.jsx", "*.tsx", "*.json", "*.css", "*.html" | Where-Object {
        $_.FullName -notmatch "(node_modules|\.git|dist|build)"
    }
    
    if ($jsFiles.Count -eq 0) {
        Write-Host "   No JS/TS files found" -ForegroundColor Gray
        return
    }
    
    Write-Host "   Found $($jsFiles.Count) JS/TS files" -ForegroundColor White
    
    # Check if prettier is available
    try {
        npx prettier --version > $null 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   📦 Installing Prettier..." -ForegroundColor Cyan
            npm install -g prettier
        }
        
        # Format files
        npx prettier --write --config .prettierrc '**/*.{js,ts,jsx,tsx,json,css,html}' 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Formatted with Prettier" -ForegroundColor Green
            $script:stats.formatted += $jsFiles.Count
        } else {
            Write-Host "   ❌ Prettier formatting failed" -ForegroundColor Red
            $script:stats.errors += $jsFiles.Count
        }
    }
    catch {
        Write-Host "   ❌ Failed to run Prettier" -ForegroundColor Red
        $script:stats.errors += $jsFiles.Count
    }
}

function Format-PowerShellFiles {
    Write-Host "`n💻 Checking PowerShell files..." -ForegroundColor Yellow
    
    $psFiles = Get-ChildItem -Path $WorkspaceRoot -Recurse -Filter "*.ps1"
    
    if ($psFiles.Count -eq 0) {
        Write-Host "   No PowerShell files found" -ForegroundColor Gray
        return
    }
    
    Write-Host "   Found $($psFiles.Count) PowerShell files" -ForegroundColor White
    Write-Host "   💡 Use VS Code PowerShell extension for formatting" -ForegroundColor Cyan
    $script:stats.skipped += $psFiles.Count
}

function Run-ESLintFix {
    Write-Host "`n🔧 Running ESLint fixes..." -ForegroundColor Yellow
    
    $frontendDir = Join-Path $WorkspaceRoot "frontend"
    if (Test-Path $frontendDir) {
        Push-Location $frontendDir
        try {
            npx eslint --fix '**/*.{js,ts,jsx,tsx}' 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ ESLint fixes applied" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ ESLint completed with warnings" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "   ❌ ESLint failed" -ForegroundColor Red
        }
        finally {
            Pop-Location
        }
    } else {
        Write-Host "   📝 No frontend directory found" -ForegroundColor Gray
    }
}

function Show-Summary {
    Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
    Write-Host "📊 FORMATTING SUMMARY" -ForegroundColor Cyan -BackgroundColor Black
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "✅ Files formatted: $($stats.formatted)" -ForegroundColor Green
    Write-Host "⚠️ Files skipped: $($stats.skipped)" -ForegroundColor Yellow
    Write-Host "❌ Errors: $($stats.errors)" -ForegroundColor Red
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    if ($stats.errors -eq 0) {
        Write-Host "🎉 All formatting completed successfully!" -ForegroundColor Green -BackgroundColor Black
    } else {
        Write-Host "⚠️ Some files had formatting issues." -ForegroundColor Yellow -BackgroundColor Black
    }
}

# Main execution
try {
    Set-Location $WorkspaceRoot
    
    if ($PythonOnly) {
        Format-PythonFiles
    }
    elseif ($JSOnly) {
        Format-JavaScriptFiles
    }
    else {
        Format-PythonFiles
        Format-JavaScriptFiles
        Format-PowerShellFiles
        Run-ESLintFix
    }
    
    Show-Summary
}
catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🚀 Formatting automation completed!`n" -ForegroundColor Cyan