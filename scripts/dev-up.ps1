# Bring up the local IDC dev stack idempotently: Postgres container,
# backend API on :8000, frontend dev server on :5173. Safe to re-run -
# anything already listening is left alone. Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File scripts\dev-up.ps1

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

function Test-Port([int]$port) {
    return [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}

# 1. Database container
docker compose -f (Join-Path $repo "docker-compose.yml") up -d db | Out-Null
Write-Host "db: container ensured (port 5455)"

# 2. Backend API
if (Test-Port 8000) {
    Write-Host "backend: already listening on 8000"
} else {
    $log = Join-Path $env:TEMP "idc-backend.log"
    Start-Process -WindowStyle Hidden -WorkingDirectory (Join-Path $repo "backend") `
        -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000" `
        -RedirectStandardOutput $log -RedirectStandardError "$log.err"
    Start-Sleep -Seconds 5
    Write-Host "backend: started (log: $log)"
}

# 3. Frontend dev server
if (Test-Port 5173) {
    Write-Host "frontend: already listening on 5173"
} else {
    $flog = Join-Path $env:TEMP "idc-frontend.log"
    Start-Process -WindowStyle Hidden -WorkingDirectory (Join-Path $repo "frontend") `
        -FilePath "cmd" -ArgumentList "/c", "npm run dev" `
        -RedirectStandardOutput $flog -RedirectStandardError "$flog.err"
    Start-Sleep -Seconds 5
    Write-Host "frontend: started (log: $flog)"
}

# 4. Health check
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 10
    Write-Host "health: $($health.status) (env=$($health.env), edition=$($health.edition))"
} catch {
    Write-Warning "backend health check failed - inspect $env:TEMP\idc-backend.log.err"
    exit 1
}
