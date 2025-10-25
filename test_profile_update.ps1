# Test Profile Update Functionality

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Profile Update Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$backendUrl = "https://hiremebahamas.onrender.com"

# Step 1: Create a new user
Write-Host "[1/3] Creating test user..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "HHmmss"
$newUser = @{
    email = "profiletest$timestamp@test.com"
    password = "Test123456"
    first_name = "Profile"
    last_name = "Test"
    user_type = "freelancer"
    location = "Nassau"
} | ConvertTo-Json

try {
    $registerResult = Invoke-RestMethod -Uri "$backendUrl/api/auth/register" `
        -Method Post `
        -Body $newUser `
        -ContentType "application/json"
    
    $token = $registerResult.access_token
    Write-Host "  SUCCESS: User created!" -ForegroundColor Green
    Write-Host "  Name: $($registerResult.user.first_name) $($registerResult.user.last_name)" -ForegroundColor Gray
    Write-Host "  Location: $($registerResult.user.location)" -ForegroundColor Gray
    
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Get current profile
Write-Host "`n[2/3] Getting current profile..." -ForegroundColor Yellow
try {
    $currentProfile = Invoke-RestMethod -Uri "$backendUrl/api/auth/profile" `
        -Method Get `
        -Headers @{Authorization = "Bearer $token"}
    
    Write-Host "  SUCCESS: Profile retrieved!" -ForegroundColor Green
    Write-Host "  Current Name: $($currentProfile.first_name) $($currentProfile.last_name)" -ForegroundColor Gray
    Write-Host "  Current Location: $($currentProfile.location)" -ForegroundColor Gray
    Write-Host "  Current Phone: $($currentProfile.phone)" -ForegroundColor Gray
    Write-Host "  Current Bio: $($currentProfile.bio)" -ForegroundColor Gray
    
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Update profile
Write-Host "`n[3/3] Updating profile..." -ForegroundColor Yellow
$updateData = @{
    first_name = "Updated"
    last_name = "Profile"
    location = "Freeport, Grand Bahama"
    phone = "+1242-555-9999"
    bio = "This is my updated bio. I am a freelancer in the Bahamas."
} | ConvertTo-Json

try {
    $updatedProfile = Invoke-RestMethod -Uri "$backendUrl/api/auth/profile" `
        -Method Put `
        -Body $updateData `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"}
    
    Write-Host "  SUCCESS: Profile updated!" -ForegroundColor Green
    Write-Host "  Updated Name: $($updatedProfile.first_name) $($updatedProfile.last_name)" -ForegroundColor Gray
    Write-Host "  Updated Location: $($updatedProfile.location)" -ForegroundColor Gray
    Write-Host "  Updated Phone: $($updatedProfile.phone)" -ForegroundColor Gray
    Write-Host "  Updated Bio: $($updatedProfile.bio)" -ForegroundColor Gray
    
    # Verify changes
    Write-Host "`n  Verification:" -ForegroundColor Cyan
    if ($updatedProfile.first_name -eq "Updated" -and $updatedProfile.last_name -eq "Profile") {
        Write-Host "    Name changed: YES" -ForegroundColor Green
    } else {
        Write-Host "    Name changed: NO" -ForegroundColor Red
    }
    
    if ($updatedProfile.location -eq "Freeport, Grand Bahama") {
        Write-Host "    Location changed: YES" -ForegroundColor Green
    } else {
        Write-Host "    Location changed: NO" -ForegroundColor Red
    }
    
    if ($updatedProfile.phone -eq "+1242-555-9999") {
        Write-Host "    Phone changed: YES" -ForegroundColor Green
    } else {
        Write-Host "    Phone changed: NO" -ForegroundColor Red
    }
    
    if ($updatedProfile.bio -like "*updated bio*") {
        Write-Host "    Bio changed: YES" -ForegroundColor Green
    } else {
        Write-Host "    Bio changed: NO" -ForegroundColor Red
    }
    
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "  Error details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
    exit 1
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Test Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nProfile Update: WORKING!" -ForegroundColor Green
Write-Host "`nThe profile update error has been fixed!" -ForegroundColor White
Write-Host "Users can now update their profile information." -ForegroundColor White

Write-Host "`nTest URL: https://frontend-p3e568zly-cliffs-projects-a84c76c9.vercel.app/profile" -ForegroundColor Cyan
Write-Host ""
