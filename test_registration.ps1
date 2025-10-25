# Test User Registration from Vercel Frontend
Write-Host "`n🧪 TESTING USER REGISTRATION" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Test credentials
$testEmail = "testuser$(Get-Random -Minimum 1000 -Maximum 9999)@gmail.com"
Write-Host "`n📧 Test Email: $testEmail" -ForegroundColor Yellow

# Registration data
$registrationData = @{
    email = $testEmail
    password = "TestPassword123!"
    first_name = "John"
    last_name = "Doe"
    user_type = "freelancer"
    location = "Nassau, Bahamas"
} | ConvertTo-Json

Write-Host "`n🔄 Testing Backend Registration Endpoint..." -ForegroundColor Cyan
Write-Host "Backend URL: https://hiremebahamas.onrender.com" -ForegroundColor Gray

try {
    # Test registration
    $response = Invoke-RestMethod `
        -Uri "https://hiremebahamas.onrender.com/api/auth/register" `
        -Method POST `
        -Body $registrationData `
        -ContentType "application/json" `
        -TimeoutSec 60
    
    Write-Host "`n✅ REGISTRATION SUCCESSFUL!" -ForegroundColor Green -BackgroundColor Black
    Write-Host "`nUser Details:" -ForegroundColor Yellow
    Write-Host "  ID: $($response.user.id)" -ForegroundColor Cyan
    Write-Host "  Email: $($response.user.email)" -ForegroundColor Cyan
    Write-Host "  Name: $($response.user.first_name) $($response.user.last_name)" -ForegroundColor Cyan
    Write-Host "  Type: $($response.user.user_type)" -ForegroundColor Cyan
    Write-Host "  Token: $($response.access_token.Substring(0, 20))..." -ForegroundColor Cyan
    
    Write-Host "`n🎉 SUCCESS! Users can now sign up!" -ForegroundColor Green -BackgroundColor Black
    Write-Host "`n📱 Frontend URL:" -ForegroundColor Yellow
    Write-Host "   https://frontend-mltv9qvqb-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Cyan
    Write-Host "`n✅ Registration is working on the website!" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ REGISTRATION FAILED" -ForegroundColor Red
    Write-Host "`nError Details:" -ForegroundColor Yellow
    Write-Host "  Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host "  API Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    
    Write-Host "`n⚠️  Note: Backend might be sleeping (Render free tier)" -ForegroundColor Yellow
    Write-Host "   First request can take 30-60 seconds to wake up" -ForegroundColor Yellow
}

Write-Host "`n" -ForegroundColor Gray
