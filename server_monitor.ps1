param(
    [int]$MaxRetries = 10,
    [int]$RetryDelay = 5
)

$serverPath = "C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe"
$backendScript = "C:\Users\Dell\OneDrive\Desktop\HireBahamas\final_backend.py"
$healthUrl = "http://127.0.0.1:8008/health"

Write-Host "Starting HireMeBahamas Backend Server Monitor..." -ForegroundColor Green
Write-Host "Server Path: $serverPath" -ForegroundColor Yellow
Write-Host "Backend Script: $backendScript" -ForegroundColor Yellow
Write-Host "Health Check URL: $healthUrl" -ForegroundColor Yellow
Write-Host ""

$retryCount = 0

while ($retryCount -lt $MaxRetries) {
    try {
        Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Starting server (Attempt $($retryCount + 1)/$MaxRetries)..." -ForegroundColor Cyan

        # Start the server process
        $process = Start-Process -FilePath $serverPath -ArgumentList $backendScript -NoNewWindow -PassThru

        # Wait a moment for server to start
        Start-Sleep -Seconds 3

        # Check if server is responding
        $healthCheck = $false
        for ($i = 1; $i -le 10; $i++) {
            try {
                $response = Invoke-WebRequest -Uri $healthUrl -Method GET -TimeoutSec 5
                if ($response.StatusCode -eq 200) {
                    Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Server is healthy and responding!" -ForegroundColor Green
                    $healthCheck = $true
                    break
                }
            } catch {
                Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Health check attempt $i failed, retrying..." -ForegroundColor Yellow
                Start-Sleep -Seconds 2
            }
        }

        if ($healthCheck) {
            Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Server started successfully. Monitoring..." -ForegroundColor Green

            # Monitor the server
            while ($true) {
                try {
                    $response = Invoke-WebRequest -Uri $healthUrl -Method GET -TimeoutSec 10
                    if ($response.StatusCode -eq 200) {
                        # Server is still healthy
                        Start-Sleep -Seconds 30  # Check every 30 seconds
                        continue
                    }
                } catch {
                    Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Server health check failed!" -ForegroundColor Red
                    break
                }
            }
        } else {
            Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Server failed to respond to health checks" -ForegroundColor Red
        }

        # Stop the process if it's still running
        if (!$process.HasExited) {
            Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Stopping server process..." -ForegroundColor Yellow
            Stop-Process -Id $process.Id -Force
        }

    } catch {
        Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Error starting server: $($_.Exception.Message)" -ForegroundColor Red
    }

    $retryCount++
    if ($retryCount -lt $MaxRetries) {
        Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Waiting $RetryDelay seconds before retry..." -ForegroundColor Yellow
        Start-Sleep -Seconds $RetryDelay
    }
}

Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Maximum retries exceeded. Giving up." -ForegroundColor Red