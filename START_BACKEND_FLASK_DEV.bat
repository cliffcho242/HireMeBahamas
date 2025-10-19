@echo off
REM FINAL WORKING SOLUTION - Admin Login Fix
echo ============================================
echo HireMeBahamas Backend - Flask Dev Server
echo ============================================
echo.

cd /d "%~dp0"

call .venv\Scripts\activate.bat

echo Starting Flask development server...
echo Backend will be at: http://127.0.0.1:9999
echo.
echo Press Ctrl+C to stop
echo.

python -c "from final_backend import app; app.run(host='0.0.0.0', port=9999, debug=True, use_reloader=False)"

pause
