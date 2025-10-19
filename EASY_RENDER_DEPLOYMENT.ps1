# HireMeBahamas - Render.com Backend Deployment Guide
# This will prepare everything for a 5-minute deployment

Write-Host "`n🚀 RENDER.COM DEPLOYMENT PREPARATION" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""
Write-Host "This is EASIER than ngrok - permanent URL, no authentication needed!" -ForegroundColor Green
Write-Host ""

# Create render.yaml for easy deployment
Write-Host "[1/3] Creating Render configuration..." -ForegroundColor Yellow

$renderConfig = @"
services:
  - type: web
    name: hiremebahamas-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn final_backend:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHONUNBUFFERED
        value: true
    healthCheckPath: /health
"@

$renderConfig | Out-File -FilePath "render.yaml" -Encoding UTF8
Write-Host "✅ Created render.yaml`n" -ForegroundColor Green

# Create requirements.txt if needed
Write-Host "[2/3] Checking requirements.txt..." -ForegroundColor Yellow
if (-not (Test-Path "requirements.txt")) {
    $requirements = @"
Flask==2.3.3
Flask-CORS==4.0.0
Flask-Limiter==3.3.1
Flask-Caching==2.0.2
PyJWT==2.8.0
bcrypt==4.0.1
gunicorn==21.2.0
python-dotenv==1.0.0
"@
    $requirements | Out-File -FilePath "requirements.txt" -Encoding UTF8
    Write-Host "✅ Created requirements.txt`n" -ForegroundColor Green
} else {
    Write-Host "✅ requirements.txt already exists`n" -ForegroundColor Green
}

# Create .gitignore if needed
Write-Host "[3/3] Creating .gitignore..." -ForegroundColor Yellow
$gitignore = @"
.venv/
__pycache__/
*.pyc
*.db
.env
.env.local
node_modules/
.vercel/
*.log
uploads/
"@
$gitignore | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "✅ Created .gitignore`n" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   READY FOR RENDER.COM!" -ForegroundColor White -BackgroundColor DarkGreen
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "FILES CREATED:" -ForegroundColor Cyan
Write-Host "  ✅ render.yaml (deployment config)" -ForegroundColor Green
Write-Host "  ✅ requirements.txt (Python dependencies)" -ForegroundColor Green
Write-Host "  ✅ .gitignore (for clean repository)`n" -ForegroundColor Green

Write-Host "DEPLOYMENT STEPS (5 MINUTES):" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Create GitHub Repository (2 min)" -ForegroundColor Cyan
Write-Host "   a. Visit: https://github.com/new" -ForegroundColor White
Write-Host "   b. Name: HireMeBahamas" -ForegroundColor White
Write-Host "   c. Click 'Create repository'`n" -ForegroundColor White

Write-Host "2️⃣  Push Your Code (1 min)" -ForegroundColor Cyan
Write-Host "   Run these commands:" -ForegroundColor White
Write-Host ""
Write-Host "   git init" -ForegroundColor Gray
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m 'Initial commit'" -ForegroundColor Gray
Write-Host "   git branch -M main" -ForegroundColor Gray
Write-Host "   git remote add origin YOUR_GITHUB_URL" -ForegroundColor Gray
Write-Host "   git push -u origin main`n" -ForegroundColor Gray

Write-Host "3️⃣  Deploy to Render (2 min)" -ForegroundColor Cyan
Write-Host "   a. Visit: https://dashboard.render.com/register" -ForegroundColor White
Write-Host "   b. Sign up with GitHub (free)" -ForegroundColor White
Write-Host "   c. Click 'New +' → 'Web Service'" -ForegroundColor White
Write-Host "   d. Connect your HireMeBahamas repository" -ForegroundColor White
Write-Host "   e. Render auto-detects settings!" -ForegroundColor White
Write-Host "   f. Click 'Create Web Service'" -ForegroundColor White
Write-Host "   g. Wait 2-3 minutes for deployment`n" -ForegroundColor White

Write-Host "4️⃣  Get Your URL" -ForegroundColor Cyan
Write-Host "   After deployment, Render gives you a URL like:" -ForegroundColor White
Write-Host "   https://hiremebahamas-backend.onrender.com`n" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "   EASIER ALTERNATIVE: LOCAL + NGROK" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "If you prefer to use ngrok (local backend):" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Sign up at: https://dashboard.ngrok.com/signup" -ForegroundColor White
Write-Host "2. Get your authtoken from dashboard" -ForegroundColor White
Write-Host "3. Run: ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Gray
Write-Host "4. Then run: ngrok http 9999`n" -ForegroundColor Gray

Write-Host ""
Write-Host "WHICH DO YOU PREFER?" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""
Write-Host "  [A] Render.com (Permanent URL, professional)" -ForegroundColor Green
Write-Host "  [B] Ngrok (Quick test, temporary URL)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Tell me your choice and I'll automate the rest!" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
