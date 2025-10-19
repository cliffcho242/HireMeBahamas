@echo off
REM Automated API Key Configuration for HireBahamas AI System
REM This script helps configure OpenAI, Anthropic, and Google AI API keys

echo ========================================
echo 🤖 HireBahamas AI - API Key Setup
echo ========================================
echo.

echo This script will help you configure API keys for:
echo • OpenAI (GPT-4, GPT-3.5)
echo • Anthropic (Claude-3)
echo • Google (Gemini)
echo.

echo You can either:
echo 1. Quick Setup (set environment variables)
echo 2. Enter keys manually (interactive)
echo 3. Auto-detect from existing environment variables
echo.

set /p choice="Choose option (1=quick, 2=manual, 3=auto): "

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto manual
if "%choice%"=="3" goto auto

echo Invalid choice. Exiting.
pause
exit /b 1

:quick
echo.
echo Starting Quick API Key Setup...
call quick_api_setup.bat
goto end

:manual
echo.
echo Starting interactive API key configuration...
python configure_api_keys.py
goto end

:auto
echo.
echo Attempting auto-configuration from environment variables...
echo Make sure you have set these environment variables:
echo • OPENAI_API_KEY
echo • ANTHROPIC_API_KEY
echo • GOOGLE_API_KEY
echo.
python configure_api_keys.py --auto
goto end

:end
echo.
echo Configuration complete!
echo Run 'python advanced_ai_launcher.py' to start your AI system.
pause