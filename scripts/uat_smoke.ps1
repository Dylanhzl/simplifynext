# Smoke / UAT checks for CreatorLoop frozen HTTP contracts.
# Assumes services are already running on default ports.
#   .\scripts\uat_smoke.ps1

$ErrorActionPreference = "Continue"
$fail = 0

function Check($name, $script) {
  try {
    $r = & $script
    Write-Host "PASS $name : $r"
  } catch {
    $script:fail++
    Write-Host "FAIL $name : $($_.Exception.Message)"
  }
}

Check "mcp /health" { (Invoke-RestMethod http://localhost:8085/health).status }
Check "mcp /mcp/tools" { "$((Invoke-RestMethod http://localhost:8085/mcp/tools).tools.Count) tools" }
Check "finder /health" { (Invoke-RestMethod http://localhost:8081/health).status }
Check "pipeline /health" { (Invoke-RestMethod http://localhost:8082/health).status }
Check "engagement /health" { (Invoke-RestMethod http://localhost:8083/health).status }
Check "cdr /health" { (Invoke-RestMethod http://localhost:8084/health).status }
Check "ui /" {
  $r = Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing
  "HTTP $($r.StatusCode)"
}

Check "finder search (fixtures)" {
  $body = @{ niche = "hawker"; city = "Singapore"; limit = 5 } | ConvertTo-Json
  $r = Invoke-RestMethod -Method Post -Uri http://localhost:8081/tools/find_opportunities -ContentType "application/json" -Body $body
  "$($r.opportunities.Count) opps mode=$($r.mode)"
}

Check "pipeline upsert" {
  $opp = @{
    id = "uat_opp_1"
    type = "brand"
    title = "UAT Laksa Lab"
    score = 90
    status = "new"
    niche = "hawker"
    city = "Singapore"
    why_now = "UAT smoke test"
    source_agent = "uat"
  }
  $r = Invoke-RestMethod -Method Post -Uri http://localhost:8082/pipeline/upsert -ContentType "application/json" -Body ($opp | ConvertTo-Json)
  if (-not $r.ok -or $r.id -ne "uat_opp_1") { throw "upsert failed: $($r | ConvertTo-Json -Compress)" }
  "ok=$($r.ok) id=$($r.id) kind=$($r.record_kind)"
}

Check "pipeline list" {
  $r = Invoke-RestMethod http://localhost:8082/pipeline/opportunities
  if ($r.opportunities.Count -lt 1) { throw "expected >=1 opportunities" }
  "$($r.opportunities.Count) opportunities"
}

Check "pipeline persist_and_schedule" {
  $body = @{
    id = "uat_opp_sched"
    type = "trend"
    title = "UAT schedule me"
    score = 80
    why_now = "calendar path"
    city = "Singapore"
    niche = "hawker"
    source_agent = "uat"
    run_id = "uat-run"
  } | ConvertTo-Json
  $r = Invoke-RestMethod -Method Post -Uri http://localhost:8082/tools/persist_and_schedule -ContentType "application/json" -Body $body
  if (-not $r.ok) { throw ($r | ConvertTo-Json -Compress) }
  "id=$($r.id) slots=$($r.calendar_slots.Count)"
}

Check "engagement inbox" {
  $r = Invoke-RestMethod http://localhost:8083/engagement/inbox
  "$($r.items.Count) inbox items"
}

Check "engagement replay week2" {
  $r = Invoke-RestMethod -Method Post -Uri http://localhost:8083/engagement/replay_maya_week2 -ContentType "application/json" -Body "{}"
  if (-not $r.ok) { throw ($r | ConvertTo-Json -Compress) }
  "replies=$($r.replies.Count) memory_keys=$($r.memory.PSObject.Properties.Name -join ',')"
}

Check "mcp search_web" {
  $body = @{ name = "search_web"; arguments = @{ query = "singapore laksa"; limit = 2 } } | ConvertTo-Json -Depth 5
  $r = Invoke-RestMethod -Method Post -Uri http://localhost:8085/mcp/call -ContentType "application/json" -Body $body
  if ($r.error) { throw $r.error }
  "ok"
}

Check "cdr /cdr/run" {
  $body = @{ profile_id = "maya"; niche = "hawker"; city = "Singapore"; week = 1 } | ConvertTo-Json
  $r = Invoke-RestMethod -Method Post -Uri http://localhost:8084/cdr/run -ContentType "application/json" -Body $body
  if (-not $r.run_id) { throw ($r | ConvertTo-Json -Compress) }
  "run_id=$($r.run_id)"
}

Check "ui POST /ag-ui (fixtures)" {
  $out = & .\.venv\Scripts\python.exe .\scripts\uat_agui_peek.py
  if ($LASTEXITCODE -ne 0) { throw $out }
  "$out"
}

if ($fail -gt 0) {
  Write-Host "`nUAT FAILED: $fail check(s)"
  exit 1
}
Write-Host "`nUAT PASSED"
exit 0
