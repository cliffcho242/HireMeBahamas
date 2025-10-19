# Quick API Key Setup Helper
# Sets environment variables for AI API keys

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔑 Quick API Key Setup Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will help you set API keys as environment variables." -ForegroundColor Yellow
Write-Host "These keys will be available for the current session only." -ForegroundColor Yellow
Write-Host ""

Write-Host "Required API Keys:" -ForegroundColor Green
Write-Host "1. OpenAI API Key (for GPT-4)" -ForegroundColor White
Write-Host "2. Anthropic API Key (for Claude-3)" -ForegroundColor White
Write-Host "3. Google AI API Key (for Gemini)" -ForegroundColor White
Write-Host ""

# OpenAI API Key
$openaiKey = Read-Host "Enter OpenAI API Key (or press Enter to skip)"
if ($openaiKey) {
    [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $openaiKey, "User")
    Write-Host "✅ OpenAI API Key set" -ForegroundColor Green
} else {
    Write-Host "⚠️ OpenAI API Key skipped" -ForegroundColor Yellow
}

Write-Host ""

# Anthropic API Key
$anthropicKey = Read-Host "Enter Anthropic API Key (or press Enter to skip)"
if ($anthropicKey) {
    [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $anthropicKey, "User")
    Write-Host "✅ Anthropic API Key set" -ForegroundColor Green
} else {
    Write-Host "⚠️ Anthropic API Key skipped" -ForegroundColor Yellow
}

Write-Host ""

# Google AI API Key
$googleKey = Read-Host "Enter Google AI API Key (or press Enter to skip)"
if ($googleKey) {
    [Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $googleKey, "User")
    Write-Host "✅ Google AI API Key set" -ForegroundColor Green
} else {
    Write-Host "⚠️ Google AI API Key skipped" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 API Keys Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your API keys have been saved as user environment variables." -ForegroundColor White
Write-Host "You may need to restart your PowerShell session for changes to take effect." -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Restart PowerShell or open a new terminal" -ForegroundColor White
Write-Host "2. Run: python configure_api_keys.py --auto" -ForegroundColor White
Write-Host "3. Run: .\AUTO_LAUNCH_HIREBAHAMAS.bat" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"