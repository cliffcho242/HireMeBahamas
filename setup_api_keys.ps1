# Automated API Key Configuration for HireBahamas AI System
# This script helps configure OpenAI, Anthropic, and Google AI API keys

param(
    [switch]$Auto,
    [switch]$NoValidate,
    [string]$EnvFile = ".env.ai"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🤖 HireBahamas AI - API Key Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Auto) {
    Write-Host "Attempting auto-configuration from environment variables..." -ForegroundColor Yellow
    Write-Host "Make sure you have set these environment variables:" -ForegroundColor Yellow
    Write-Host "• OPENAI_API_KEY" -ForegroundColor White
    Write-Host "• ANTHROPIC_API_KEY" -ForegroundColor White
    Write-Host "• GOOGLE_API_KEY" -ForegroundColor White
    Write-Host ""

    & python configure_api_keys.py --auto --env-file $EnvFile
} else {
    Write-Host "This script will help you configure API keys for:" -ForegroundColor Green
    Write-Host "• OpenAI (GPT-4, GPT-3.5)" -ForegroundColor White
    Write-Host "• Anthropic (Claude-3)" -ForegroundColor White
    Write-Host "• Google (Gemini)" -ForegroundColor White
    Write-Host ""

    Write-Host "Choose option:" -ForegroundColor Green
    Write-Host "1. Quick Setup (set environment variables)" -ForegroundColor White
    Write-Host "2. Manual Interactive (Python script)" -ForegroundColor White
    Write-Host "3. Auto-detect from existing environment variables" -ForegroundColor White
    Write-Host ""

    $choice = Read-Host "Choose option (1=quick, 2=manual, 3=auto)"

    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "Starting Quick API Key Setup..." -ForegroundColor Green
            & .\quick_api_setup.ps1
        }
        "2" {
            Write-Host ""
            Write-Host "Starting interactive API key configuration..." -ForegroundColor Green
            & python configure_api_keys.py --env-file $EnvFile
        }
        "3" {
            Write-Host ""
            Write-Host "Attempting auto-configuration from environment variables..." -ForegroundColor Yellow
            & python configure_api_keys.py --auto --env-file $EnvFile
        }
        default {
            Write-Host "Invalid choice. Exiting." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "Configuration complete!" -ForegroundColor Green
Write-Host "Run 'python advanced_ai_launcher.py' to start your AI system." -ForegroundColor Cyan