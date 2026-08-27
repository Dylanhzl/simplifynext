# Start all CreatorLoop services for local UAT (Windows).
#   .\scripts\run_local.ps1
#   .\scripts\run_local.ps1 -Live
param(
  [switch]$Live
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$env:PYTHONPATH = "."
$env:DEMO_SPEED = if ($env:DEMO_SPEED) { $env:DEMO_SPEED } else { "1.0" }
if ($Live) {
  $env:USE_FIXTURES = "0"
} else {
  $env:USE_FIXTURES = if ($env:USE_FIXTURES) { $env:USE_FIXTURES } else { "1" }
}

if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
}

$py = if (Test-Path .\.venv\Scripts\python.exe) { ".\.venv\Scripts\python.exe" } else { "python" }

$jobs = @()
$jobs += Start-Process -PassThru -NoNewWindow $py -ArgumentList "-m","uvicorn","mcp.server:app","--port","8085"
$jobs += Start-Process -PassThru -NoNewWindow $py -ArgumentList "-m","uvicorn","opportunity_finder.app:app","--port","8081"
$jobs += Start-Process -PassThru -NoNewWindow $py -ArgumentList "-m","uvicorn","pipeline_manager.app:app","--port","8082"
$jobs += Start-Process -PassThru -NoNewWindow $py -ArgumentList "-m","uvicorn","engagement_listener.app:app","--port","8083"
$jobs += Start-Process -PassThru -NoNewWindow $py -ArgumentList "-m","uvicorn","cdr.app:app","--port","8084"
$jobs += Start-Process -PassThru -NoNewWindow $py -ArgumentList "ui_client\server.py"

Write-Host "UI http://localhost:8000  AG-UI POST :8084/ag-ui  MCP :8085"
Write-Host "Finder :8081  Pipeline :8082  Engagement :8083  CDR :8084"
Write-Host "USE_FIXTURES=$($env:USE_FIXTURES)"
Write-Host "PIDs: $($jobs.Id -join ', ')"
Write-Host "Press Ctrl+C to stop all..."

try {
  while ($true) {
    Start-Sleep -Seconds 2
    $dead = $jobs | Where-Object { $_.HasExited }
    if ($dead) {
      Write-Host "Process(es) exited: $($dead.Id -join ', ')"
      break
    }
  }
} finally {
  foreach ($p in $jobs) {
    if (-not $p.HasExited) {
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
