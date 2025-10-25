# Test Posts Persistence
# Verify that posts are saved to database and persist after page refresh

Write-Host "`n=== TESTING POSTS PERSISTENCE ===`n" -ForegroundColor Cyan

$BACKEND_URL = "https://hiremebahamas.onrender.com"

# Step 1: Create test user
Write-Host "[1/5] Creating test user..." -ForegroundColor Yellow
$registerData = @{
    email = "posttest_$(Get-Random)@test.com"
    password = "Test1234!"
    first_name = "Post"
    last_name = "Tester"
    user_type = "freelancer"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/auth/register" -Method Post -Body $registerData -ContentType "application/json"
    $token = $registerResponse.token
    Write-Host "  ✅ SUCCESS: User created!" -ForegroundColor Green
    Write-Host "  Email: $($registerData | ConvertFrom-Json | Select-Object -ExpandProperty email)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Create first post
Write-Host "`n[2/5] Creating first post..." -ForegroundColor Yellow
$post1Data = @{
    content = "This is my first post! Testing persistence."
} | ConvertTo-Json

try {
    $createResponse1 = Invoke-RestMethod -Uri "$BACKEND_URL/api/posts" -Method Post -Body $post1Data -ContentType "application/json" -Headers @{Authorization = "Bearer $token"}
    $post1Id = $createResponse1.post.id
    Write-Host "  ✅ SUCCESS: Post created!" -ForegroundColor Green
    Write-Host "  Post ID: $post1Id" -ForegroundColor Gray
    Write-Host "  Content: $($createResponse1.post.content)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Create second post
Write-Host "`n[3/5] Creating second post..." -ForegroundColor Yellow
$post2Data = @{
    content = "This is my second post! Should appear after refresh."
} | ConvertTo-Json

try {
    $createResponse2 = Invoke-RestMethod -Uri "$BACKEND_URL/api/posts" -Method Post -Body $post2Data -ContentType "application/json" -Headers @{Authorization = "Bearer $token"}
    $post2Id = $createResponse2.post.id
    Write-Host "  ✅ SUCCESS: Post created!" -ForegroundColor Green
    Write-Host "  Post ID: $post2Id" -ForegroundColor Gray
    Write-Host "  Content: $($createResponse2.post.content)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Fetch all posts (simulating initial page load)
Write-Host "`n[4/5] Fetching all posts (simulating page load)..." -ForegroundColor Yellow
try {
    $postsResponse1 = Invoke-RestMethod -Uri "$BACKEND_URL/api/posts" -Method Get
    $allPosts1 = $postsResponse1.posts
    Write-Host "  ✅ SUCCESS: Retrieved $($allPosts1.Count) posts" -ForegroundColor Green
    
    # Find our posts
    $ourPost1 = $allPosts1 | Where-Object { $_.id -eq $post1Id }
    $ourPost2 = $allPosts1 | Where-Object { $_.id -eq $post2Id }
    
    if ($ourPost1) {
        Write-Host "  ✅ Post 1 found in feed" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Post 1 NOT found in feed" -ForegroundColor Red
    }
    
    if ($ourPost2) {
        Write-Host "  ✅ Post 2 found in feed" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Post 2 NOT found in feed" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 5: Simulate page refresh by fetching posts again
Write-Host "`n[5/5] Simulating page refresh (fetching posts again)..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $postsResponse2 = Invoke-RestMethod -Uri "$BACKEND_URL/api/posts" -Method Get
    $allPosts2 = $postsResponse2.posts
    Write-Host "  ✅ SUCCESS: Retrieved $($allPosts2.Count) posts after refresh" -ForegroundColor Green
    
    # Find our posts again
    $ourPost1AfterRefresh = $allPosts2 | Where-Object { $_.id -eq $post1Id }
    $ourPost2AfterRefresh = $allPosts2 | Where-Object { $_.id -eq $post2Id }
    
    if ($ourPost1AfterRefresh) {
        Write-Host "  ✅ Post 1 STILL found after refresh" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Post 1 DISAPPEARED after refresh" -ForegroundColor Red
    }
    
    if ($ourPost2AfterRefresh) {
        Write-Host "  ✅ Post 2 STILL found after refresh" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Post 2 DISAPPEARED after refresh" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Final verification
Write-Host "`n=== VERIFICATION RESULTS ===`n" -ForegroundColor Cyan

$persistence1 = if ($ourPost1AfterRefresh) { "YES ✅" } else { "NO ❌" }
$persistence2 = if ($ourPost2AfterRefresh) { "YES ✅" } else { "NO ❌" }

Write-Host "Post 1 persisted after refresh: $persistence1"
Write-Host "Post 2 persisted after refresh: $persistence2"

if ($ourPost1AfterRefresh -and $ourPost2AfterRefresh) {
    Write-Host "`n✅ SUCCESS: Posts are persisting correctly!`n" -ForegroundColor Green
    Write-Host "Posts are saved to the database and remain after page refresh." -ForegroundColor Gray
    exit 0
} else {
    Write-Host "`n❌ FAILURE: Posts are NOT persisting!`n" -ForegroundColor Red
    Write-Host "Posts are disappearing after page refresh. Backend issue detected." -ForegroundColor Gray
    exit 1
}
