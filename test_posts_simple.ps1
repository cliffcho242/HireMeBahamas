# Test Posts Persistence - Simple Version
# Tests if posts actually persist

Write-Host "`n=== TESTING POSTS PERSISTENCE ===`n" -ForegroundColor Cyan

$BACKEND_URL = "https://hiremebahamas.onrender.com"

# Use admin credentials  
$loginData = @{
    email = "admin@hiremebahamas.com"
    password = "Admin123!"
} | ConvertTo-Json

Write-Host "[1/4] Logging in..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"
    $token = $loginResponse.token
    Write-Host "  ✅ Logged in successfully!" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Login failed" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Create a test post
$timestamp = Get-Date -Format "HH:mm:ss"
$postContent = "Test post created at $timestamp - Should persist after refresh!"

Write-Host "`n[2/4] Creating test post..." -ForegroundColor Yellow
$postData = @{
    content = $postContent
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/posts" -Method Post -Body $postData -ContentType "application/json" -Headers @{Authorization = "Bearer $token"}
    $postId = $createResponse.post.id
    Write-Host "  ✅ Post created!" -ForegroundColor Green
    Write-Host "  Post ID: $postId" -ForegroundColor Gray
    Write-Host "  Content: $postContent" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ Failed to create post" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Fetch posts immediately
Write-Host "`n[3/4] Fetching posts (immediately after creation)..." -ForegroundColor Yellow
try {
    $postsResponse1 = Invoke-RestMethod -Uri "$BACKEND_URL/api/posts" -Method Get
    $allPosts1 = $postsResponse1.posts
    Write-Host "  ✅ Retrieved $($allPosts1.Count) total posts" -ForegroundColor Green
    
    $ourPost = $allPosts1 | Where-Object { $_.id -eq $postId }
    if ($ourPost) {
        Write-Host "  ✅ Our post IS in the feed" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Our post NOT in feed" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Failed to fetch posts" -ForegroundColor Red
    exit 1
}

# Wait and fetch again (simulating refresh)
Write-Host "`n[4/4] Waiting 3 seconds and fetching again (simulating refresh)..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $postsResponse2 = Invoke-RestMethod -Uri "$BACKEND_URL/api/posts" -Method Get
    $allPosts2 = $postsResponse2.posts
    Write-Host "  ✅ Retrieved $($allPosts2.Count) total posts" -ForegroundColor Green
    
    $ourPostAfterRefresh = $allPosts2 | Where-Object { $_.id -eq $postId }
    if ($ourPostAfterRefresh) {
        Write-Host "  ✅ Our post IS STILL in the feed after refresh!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Our post DISAPPEARED after refresh!" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Failed to fetch posts" -ForegroundColor Red
    exit 1
}

# Results
Write-Host "`n=== RESULTS ===" -ForegroundColor Cyan
if ($ourPostAfterRefresh) {
    Write-Host "✅ SUCCESS: Posts ARE persisting!" -ForegroundColor Green
    Write-Host "Posts are saved to database and remain after 'refresh'" -ForegroundColor Gray
    Write-Host "`nPost ID $postId is still accessible after refresh." -ForegroundColor Gray
} else {
    Write-Host "❌ FAILURE: Posts are NOT persisting!" -ForegroundColor Red
    Write-Host "Posts disappear after refresh - database issue!" -ForegroundColor Gray
}

Write-Host ""
