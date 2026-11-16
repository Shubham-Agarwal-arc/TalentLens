$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$python = Join-Path $backend "venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Backend environment not found. Run: cd backend; python -m venv venv; pip install -r requirements.txt"
}

$backendProcess = $null
$frontendProcess = $null

try {
    Write-Host "Starting AI Resume Matcher..." -ForegroundColor Cyan
    $backendProcess = Start-Process -FilePath $python `
        -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 8000" `
        -WorkingDirectory $backend -PassThru

    $frontendProcess = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c npm run dev -- --host 127.0.0.1" `
        -WorkingDirectory $frontend -PassThru

    $backendReady = $false
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2
            if ($health.status -eq "ok") {
                $backendReady = $true
                break
            }
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }

    if (-not $backendReady) {
        throw "Backend did not become ready at http://127.0.0.1:8000"
    }

    $frontendReady = $false
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try {
            $request = [System.Net.WebRequest]::Create("http://127.0.0.1:5173")
            $response = $request.GetResponse()
            $response.Close()
            $frontendReady = $true
            break
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }

    if (-not $frontendReady) {
        throw "Frontend did not become ready at http://127.0.0.1:5173"
    }

    Write-Host "Backend ready:  http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "Frontend ready: http://127.0.0.1:5173" -ForegroundColor Green
    Start-Process "http://localhost:5173"
    Write-Host "The app is open in your browser. Press Ctrl+C here to stop both services." -ForegroundColor Yellow
    Wait-Process -Id $backendProcess.Id
} finally {
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendProcess -and -not $frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
