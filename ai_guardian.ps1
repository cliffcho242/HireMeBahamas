<#!
.SYNOPSIS
  AI-Powered HireBahamas Platform Guardian - Intelligent monitoring and auto-healing system

.DESCRIPTION
  Advanced AI system that continuously monitors frontend/backend health, detects issues,
  and automatically performs healing actions to keep the platform running smoothly.
  Features intelligent diagnostics, predictive maintenance, and automated recovery.

.PARAMETER Mode
  Operation mode: Monitor (continuous monitoring), Heal (one-time healing), or Full (monitor + heal)

.PARAMETER IntervalSeconds
  Monitoring interval in seconds (default 30)

.PARAMETER MaxRetries
  Maximum healing attempts before escalating (default 3)

.PARAMETER LogFile
  Path to log file (default guardian.log)

.PARAMETER Verbose
  Enable verbose logging

.EXAMPLE
  .\ai_guardian.ps1 -Mode Full -Verbose

.EXAMPLE
  .\ai_guardian.ps1 -Mode Monitor -IntervalSeconds 60
#>
param(
  [ValidateSet("Monitor", "Heal", "Full")]
  [string]$Mode = "Full",
  [int]$IntervalSeconds = 30,
  [int]$MaxRetries = 3,
  [string]$LogFile = "ai_guardian.log",
  [switch]$Verbose
)

$ErrorActionPreference = 'Continue'
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogPath = Join-Path $ScriptPath $LogFile

# AI Guardian Class
class HireBahamasGuardian {
  [string]$RootPath
  [string]$FrontendPath
  [hashtable]$HealthStatus
  [System.Collections.Generic.List[string]]$LogBuffer
  [int]$CycleCount
  [datetime]$StartTime
  [hashtable]$ServiceStats

  HireBahamasGuardian([string]$rootPath) {
    $this.RootPath = $rootPath
    $this.FrontendPath = Join-Path $rootPath "frontend"
    $this.HealthStatus = @{}
    $this.LogBuffer = New-Object System.Collections.Generic.List[string]
    $this.CycleCount = 0
    $this.StartTime = Get-Date
    $this.ServiceStats = @{
      FrontendRestarts = 0
      BackendRestarts = 0
      TotalIssues = 0
      LastFrontendDown = $null
      LastBackendDown = $null
      UptimePercent = 100.0
    }
  }

  [void]Log([string]$message, [string]$level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$level] $message"

    # Add to buffer
    $this.LogBuffer.Add($logEntry)

    # Keep buffer size manageable
    if ($this.LogBuffer.Count -gt 1000) {
      $this.LogBuffer.RemoveAt(0)
    }

    # Write to console if verbose
    if ($Verbose) {
      $color = switch ($level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "AI" { "Cyan" }
        default { "White" }
      }
      Write-Host $logEntry -ForegroundColor $color
    }

    # Write to file
    try {
      Add-Content -Path $LogPath -Value $logEntry -ErrorAction SilentlyContinue
    } catch {
      # Silently fail if log write fails
    }
  }

  [hashtable]TestService([string]$name, [string]$url, [int]$timeoutSeconds = 10) {
    $startTime = Get-Date
    $result = @{
      Name = $name
      Url = $url
      Status = "UNKNOWN"
      ResponseTime = 0
      Error = $null
      IsHealthy = $false
    }

    try {
      $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec $timeoutSeconds
      $result.Status = $response.StatusCode
      $result.ResponseTime = ((Get-Date) - $startTime).TotalMilliseconds
      $result.IsHealthy = $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
    } catch {
      $result.Status = "ERROR"
      $result.Error = $_.Exception.Message
      $result.ResponseTime = ((Get-Date) - $startTime).TotalMilliseconds
      $result.IsHealthy = $false
    }

    return $result
  }

  [void]DiagnoseIssue([string]$serviceName, [hashtable]$testResult) {
    $this.Log("AI: Analyzing $serviceName failure...", "AI")

    if ($serviceName -eq "Frontend") {
      # Frontend-specific diagnostics
      if ($testResult.Error -match "connection refused|timeout") {
        $this.Log("AI: Frontend port likely closed. Checking for running processes...", "AI")

        $nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
        if ($nodeProcesses) {
          $this.Log("AI: Found $($nodeProcesses.Count) node processes. Checking if any are Vite...", "AI")
          # Could add more specific checks here
        } else {
          $this.Log("AI: No node processes found. Frontend completely down.", "AI")
        }
      }
    } elseif ($serviceName -eq "Backend") {
      # Backend-specific diagnostics
      if ($testResult.Error -match "connection refused") {
        $this.Log("AI: Backend port closed. Checking Python processes...", "AI")

        $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
        if ($pythonProcesses) {
          $this.Log("AI: Found $($pythonProcesses.Count) Python processes.", "AI")
        } else {
          $this.Log("AI: No Python processes found. Backend completely down.", "AI")
        }
      }
    }
  }

  [bool]HealService([string]$serviceName, [int]$attemptNumber) {
    $this.Log("AI: Attempting to heal $serviceName (attempt $attemptNumber/$MaxRetries)", "AI")

    if ($serviceName -eq "Frontend") {
      return $this.HealFrontend($attemptNumber)
    } elseif ($serviceName -eq "Backend") {
      return $this.HealBackend($attemptNumber)
    }

    return $false
  }

  [bool]HealFrontend([int]$attemptNumber) {
    $this.Log("AI: Executing frontend healing protocol...", "AI")

    try {
      # Kill existing processes
      $this.Log("AI: Terminating existing frontend processes...", "AI")
      $nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
      foreach ($proc in $nodeProcesses) {
        try {
          Stop-Process -Id $proc.Id -Force -ErrorAction Stop
          $this.Log("AI: Killed node process $($proc.Id)", "AI")
        } catch {
          $this.Log("AI: Failed to kill process $($proc.Id): $($_.Exception.Message)", "WARN")
        }
      }

      # Clear caches on first attempt
      if ($attemptNumber -eq 1) {
        $this.Log("AI: Clearing Vite caches...", "AI")
        $cacheDirs = @(
          (Join-Path $this.FrontendPath "node_modules/.vite"),
          (Join-Path $this.FrontendPath "node_modules/.cache")
        )
        foreach ($dir in $cacheDirs) {
          if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
            $this.Log("AI: Cleared cache: $dir", "AI")
          }
        }
      }

      # Restart frontend
      $this.Log("AI: Starting frontend...", "AI")
      $startInfo = New-Object System.Diagnostics.ProcessStartInfo
      $startInfo.FileName = "powershell.exe"
      $startInfo.Arguments = "-ExecutionPolicy Bypass -File `"$(Join-Path $this.FrontendPath 'force_frontend_dev.ps1')`""
      $startInfo.WorkingDirectory = $this.FrontendPath
      $startInfo.UseShellExecute = $false
      $startInfo.CreateNoWindow = $true

      $process = New-Object System.Diagnostics.Process
      $process.StartInfo = $startInfo
      $null = $process.Start()

      $this.ServiceStats.FrontendRestarts++
      $this.Log("AI: Frontend restart initiated", "SUCCESS")
      return $true

    } catch {
      $this.Log("AI: Frontend healing failed: $($_.Exception.Message)", "ERROR")
      return $false
    }
  }

  [bool]HealBackend([int]$attemptNumber) {
    $this.Log("AI: Executing backend healing protocol...", "AI")

    try {
      # Kill existing processes
      $this.Log("AI: Terminating existing backend processes...", "AI")
      $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
      foreach ($proc in $pythonProcesses) {
        try {
          Stop-Process -Id $proc.Id -Force -ErrorAction Stop
          $this.Log("AI: Killed python process $($proc.Id)", "AI")
        } catch {
          $this.Log("AI: Failed to kill process $($proc.Id): $($_.Exception.Message)", "WARN")
        }
      }

      # Clean database on first attempt if issues persist
      if ($attemptNumber -eq 1) {
        $dbPath = Join-Path $this.RootPath "hirebahamas.db"
        if (Test-Path $dbPath) {
          $this.Log("AI: Backing up and recreating database...", "AI")
          $backupPath = "$dbPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
          Copy-Item $dbPath $backupPath -ErrorAction SilentlyContinue
          Remove-Item $dbPath -ErrorAction SilentlyContinue
          $this.Log("AI: Database backup created: $backupPath", "AI")
        }
      }

      # Restart backend
      $this.Log("AI: Starting backend...", "AI")
      $startInfo = New-Object System.Diagnostics.ProcessStartInfo
      $startInfo.FileName = "powershell.exe"
      $startInfo.Arguments = "-ExecutionPolicy Bypass -File `"$(Join-Path $this.RootPath 'force_backend.ps1')`" -ForceAll"
      $startInfo.WorkingDirectory = $this.RootPath
      $startInfo.UseShellExecute = $false
      $startInfo.CreateNoWindow = $true

      $process = New-Object System.Diagnostics.Process
      $process.StartInfo = $startInfo
      $null = $process.Start()

      $this.ServiceStats.BackendRestarts++
      $this.Log("AI: Backend restart initiated", "SUCCESS")
      return $true

    } catch {
      $this.Log("AI: Backend healing failed: $($_.Exception.Message)", "ERROR")
      return $false
    }
  }

  [void]MonitorServices() {
    $this.CycleCount++

    # Test services
    $frontendTest = $this.TestService("Frontend", "http://localhost:3000", 5)
    $backendTest = $this.TestService("Backend", "http://127.0.0.1:8008/health", 5)

    # Update health status
    $this.HealthStatus.Frontend = $frontendTest
    $this.HealthStatus.Backend = $backendTest

    # Check for issues
    $issuesFound = $false

    if (-not $frontendTest.IsHealthy) {
      $this.ServiceStats.TotalIssues++
      $this.ServiceStats.LastFrontendDown = Get-Date
      $this.Log("Frontend health check failed: $($frontendTest.Error)", "ERROR")
      $issuesFound = $true

      if ($Mode -eq "Full" -or $Mode -eq "Heal") {
        $this.DiagnoseIssue("Frontend", $frontendTest)
        $healed = $false
        for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
          if ($this.HealService("Frontend", $attempt)) {
            $healed = $true
            break
          }
          Start-Sleep -Seconds 5
        }
        if (-not $healed) {
          $this.Log("AI: CRITICAL - Frontend could not be healed after $MaxRetries attempts", "ERROR")
        }
      }
    }

    if (-not $backendTest.IsHealthy) {
      $this.ServiceStats.TotalIssues++
      $this.ServiceStats.LastBackendDown = Get-Date
      $this.Log("Backend health check failed: $($backendTest.Error)", "ERROR")
      $issuesFound = $true

      if ($Mode -eq "Full" -or $Mode -eq "Heal") {
        $this.DiagnoseIssue("Backend", $backendTest)
        $healed = $false
        for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
          if ($this.HealService("Backend", $attempt)) {
            $healed = $true
            break
          }
          Start-Sleep -Seconds 5
        }
        if (-not $healed) {
          $this.Log("AI: CRITICAL - Backend could not be healed after $MaxRetries attempts", "ERROR")
        }
      }
    }

    # Log healthy status
    if (-not $issuesFound) {
      if ($this.CycleCount % 10 -eq 0) { # Log every 10 cycles when healthy
        $this.Log("All services healthy - Frontend: $($frontendTest.ResponseTime)ms, Backend: $($backendTest.ResponseTime)ms", "SUCCESS")
      }
    }

    # Update uptime calculation
    $totalTime = (Get-Date) - $this.StartTime
    $downtime = 0
    if ($this.ServiceStats.LastFrontendDown) {
      $downtime += ((Get-Date) - $this.ServiceStats.LastFrontendDown).TotalSeconds
    }
    if ($this.ServiceStats.LastBackendDown) {
      $downtime += ((Get-Date) - $this.ServiceStats.LastBackendDown).TotalSeconds
    }
    $this.ServiceStats.UptimePercent = [math]::Max(0, (1 - ($downtime / $totalTime.TotalSeconds)) * 100)
  }

  [void]DisplayStatus() {
    Clear-Host
    Write-Host "🤖 HIREBAHAMAS AI GUARDIAN - PLATFORM MONITOR" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Yellow
    Write-Host "Mode: $Mode | Cycles: $($this.CycleCount) | Uptime: $([math]::Round($this.ServiceStats.UptimePercent, 1))%" -ForegroundColor White
    Write-Host ""

    # Frontend Status
    $frontendStatus = if ($this.HealthStatus.Frontend.IsHealthy) { "HEALTHY" } else { "DOWN" }
    $frontendTime = if ($this.HealthStatus.Frontend.ResponseTime -gt 0) { "$([math]::Round($this.HealthStatus.Frontend.ResponseTime, 0))ms" } else { "N/A" }
    Write-Host "Frontend (localhost:3000): $frontendStatus | Response: $frontendTime | Restarts: $($this.ServiceStats.FrontendRestarts)" -ForegroundColor $(if ($this.HealthStatus.Frontend.IsHealthy) { "Green" } else { "Red" })

    # Backend Status
    $backendStatus = if ($this.HealthStatus.Backend.IsHealthy) { "HEALTHY" } else { "DOWN" }
    $backendTime = if ($this.HealthStatus.Backend.ResponseTime -gt 0) { "$([math]::Round($this.HealthStatus.Backend.ResponseTime, 0))ms" } else { "N/A" }
    Write-Host "Backend (127.0.0.1:8008): $backendStatus | Response: $backendTime | Restarts: $($this.ServiceStats.BackendRestarts)" -ForegroundColor $(if ($this.HealthStatus.Backend.IsHealthy) { "Green" } else { "Red" })

    Write-Host ""
    Write-Host "Recent Activity:" -ForegroundColor Yellow
    $recentLogs = $this.LogBuffer | Select-Object -Last 5
    foreach ($log in $recentLogs) {
      Write-Host "  $log" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "Commands: [Q]uit | [R]estart All | [F]orce Frontend | [B]ackend | [L]ogs" -ForegroundColor Cyan
  }

  [void]Run() {
    $this.Log("AI Guardian starting in $Mode mode", "AI")
    $this.Log("Monitoring interval: ${IntervalSeconds}s | Max retries: $MaxRetries", "AI")

    if ($Mode -eq "Heal") {
      $this.Log("Running one-time healing cycle...", "AI")
      $this.MonitorServices()
      return
    }

    # Continuous monitoring
    while ($true) {
      $this.MonitorServices()
      $this.DisplayStatus()

      # Check for keyboard input (non-blocking)
      if ([Console]::KeyAvailable) {
        $key = [Console]::ReadKey($true)
        switch ($key.Key) {
          'Q' {
            $this.Log("AI Guardian shutting down by user request", "AI")
            return
          }
          'R' {
            $this.Log("Manual restart of all services initiated", "WARN")
            $this.HealService("Frontend", 1)
            $this.HealService("Backend", 1)
          }
          'F' {
            $this.Log("Manual frontend restart initiated", "WARN")
            $this.HealService("Frontend", 1)
          }
          'B' {
            $this.Log("Manual backend restart initiated", "WARN")
            $this.HealService("Backend", 1)
          }
          'L' {
            $this.Log("Displaying full log buffer", "INFO")
            Write-Host "`n=== FULL LOG BUFFER ===" -ForegroundColor Yellow
            foreach ($log in $this.LogBuffer) {
              Write-Host $log -ForegroundColor Gray
            }
            Write-Host "=== END LOG ===`n" -ForegroundColor Yellow
            Read-Host "Press Enter to continue"
          }
        }
      }

      Start-Sleep -Seconds $IntervalSeconds
    }
  }
}

# Main execution
$guardian = [HireBahamasGuardian]::new($ScriptPath)

if ($Mode -eq "Monitor") {
  $guardian.Log("Starting continuous monitoring mode", "AI")
  $guardian.Run()
} elseif ($Mode -eq "Heal") {
  $guardian.Log("Starting one-time healing mode", "AI")
  $guardian.Run()
} elseif ($Mode -eq "Full") {
  $guardian.Log("Starting full AI guardian mode (monitor + auto-heal)", "AI")
  $guardian.Run()
}