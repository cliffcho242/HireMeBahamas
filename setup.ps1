# HireBahamas Setup Script for Windows
Write-Host "🇧🇸 Setting up HireBahamas - The Ultimate Bahaman Job Platform!" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

function Write-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param($Message)
    Write-Host "ℹ $Message" -ForegroundColor Blue
}

# Check if Docker is installed
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerInstalled) {
    Write-Error "Docker is not installed. Please install Docker Desktop for Windows first."
    exit 1
}

$dockerComposeInstalled = Get-Command docker-compose -ErrorAction SilentlyContinue
if (-not $dockerComposeInstalled) {
    Write-Error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
}

Write-Success "Docker and Docker Compose are installed"

# Create environment files
Write-Info "Creating environment files..."

# Generate random secret key
$secretKey = -join ((1..64) | ForEach-Object { '{0:X}' -f (Get-Random -Max 16) })

# Backend environment
$backendEnv = @"
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/hirebahamas
SECRET_KEY=your-super-secret-key-change-this-in-production-$secretKey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
CLOUDINARY_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
"@

$frontendEnv = @"
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name
"@

# Write environment files
$backendEnv | Out-File -FilePath "backend\.env" -Encoding utf8
$frontendEnv | Out-File -FilePath "frontend\.env" -Encoding utf8

Write-Success "Environment files created"

# Install frontend dependencies
Write-Info "Installing frontend dependencies..."
Set-Location frontend
$npmInstall = npm install
if ($LASTEXITCODE -eq 0) {
    Write-Success "Frontend dependencies installed"
} else {
    Write-Error "Failed to install frontend dependencies"
    exit 1
}
Set-Location ..

# Install backend dependencies
Write-Info "Installing backend dependencies..."
Set-Location backend
python -m pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Success "Backend dependencies installed"
} else {
    Write-Error "Failed to install backend dependencies"
    exit 1
}
Set-Location ..

# Build and start services with Docker Compose
Write-Info "Building and starting services with Docker Compose..."
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Success "Services started successfully!"
    
    Write-Host ""
    Write-Host "🎉 HireBahamas is now running!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Frontend (React): http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "PostgreSQL: localhost:5432" -ForegroundColor Cyan
    Write-Host "Redis: localhost:6379" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 To view logs:" -ForegroundColor Yellow
    Write-Host "  docker-compose logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "🛑 To stop services:" -ForegroundColor Yellow
    Write-Host "  docker-compose down" -ForegroundColor White
    Write-Host ""
    Write-Host "🔄 To restart services:" -ForegroundColor Yellow
    Write-Host "  docker-compose restart" -ForegroundColor White
    Write-Host ""
    Write-Warning "Remember to update your environment variables with real values!"
    Write-Warning "Especially DATABASE_URL, SECRET_KEY, and Cloudinary settings for production."
    
} else {
    Write-Error "Failed to start services"
    Write-Host "Check the logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}