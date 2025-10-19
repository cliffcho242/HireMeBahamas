@echo off
REM Quick API Key Setup Helper
REM Sets environment variables for AI API keys

echo ========================================
echo 🔑 Quick API Key Setup Helper
echo ========================================
echo.

echo This will help you set API keys as environment variables.
echo These keys will be available for the current session only.
echo.

echo Required API Keys:
echo 1. OpenAI API Key (for GPT-4)
echo 2. Anthropic API Key (for Claude-3)
echo 3. Google AI API Key (for Gemini)
echo.

set /p OPENAI_KEY="Enter OpenAI API Key (or press Enter to skip): "
if defined OPENAI_KEY (
    setx OPENAI_API_KEY "%OPENAI_KEY%" /M
    echo ✅ OpenAI API Key set
) else (
    echo ⚠️ OpenAI API Key skipped
)

echo.
set /p ANTHROPIC_KEY="Enter Anthropic API Key (or press Enter to skip): "
if defined ANTHROPIC_KEY (
    setx ANTHROPIC_API_KEY "%ANTHROPIC_KEY%" /M
    echo ✅ Anthropic API Key set
) else (
    echo ⚠️ Anthropic API Key skipped
)

echo.
set /p GOOGLE_KEY="Enter Google AI API Key (or press Enter to skip): "
if defined GOOGLE_KEY (
    setx GOOGLE_API_KEY "%GOOGLE_KEY%" /M
    echo ✅ Google AI API Key set
) else (
    echo ⚠️ Google AI API Key skipped
)

echo.
echo ========================================
echo 🎉 API Keys Setup Complete!
echo ========================================
echo.
echo Your API keys have been saved as system environment variables.
echo You may need to restart your command prompt for changes to take effect.
echo.
echo Next steps:
echo 1. Close and reopen this command prompt
echo 2. Run: python configure_api_keys.py --auto
echo 3. Run: AUTO_LAUNCH_HIREBAHAMAS.bat
echo.
pause