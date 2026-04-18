[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$VITE   = "C:\smartclass\frontend\node_modules\vite\bin\vite.js"
$VROOT  = "C:\smartclass\frontend"
$BROOT  = "C:\smartclass\backend"

function stop-all {
    Write-Host "[*] Stopping old processes..."
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep 2
    Write-Host "[OK] All stopped"
}

function wait-port($port, $sec = 20) {
    $end = (Get-Date).AddSeconds($sec)
    while ((Get-Date) -lt $end) {
        $listening = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if ($listening) { return $true }
        Start-Sleep 1
    }
    return $false
}

function start-backend {
    Write-Host "[*] Starting Flask (port 5000)..."
    Start-Process python -ArgumentList "app.py" -WorkingDirectory $BROOT -WindowStyle Hidden
    if (wait-port 5000 15) {
        Write-Host "[OK] Flask running (port 5000)" -ForegroundColor Green
        return $true
    }
    Write-Host "[X] Flask failed - check $BROOT\flask_err.log" -ForegroundColor Red
    return $false
}

function start-vite($port, $name) {
    Write-Host "[*] Starting $name (port $port)..."
    Start-Process node -ArgumentList $VITE, "--port", "$port", "--host", "0.0.0.0" `
        -WorkingDirectory $VROOT -WindowStyle Hidden
    if (wait-port $port 25) {
        Write-Host "[OK] $name started (port $port)" -ForegroundColor Green
        return $true
    }
    Write-Host "[X] $name failed on port $port" -ForegroundColor Red
    return $false
}

# ---- MAIN ----
Clear-Host
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  SmartClass - Restart All Services" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "[*] Checking MySQL..."
$svc = Get-Service -Name "MySQL" -ErrorAction SilentlyContinue
if ($svc.Status -ne "Running") {
    Start-Service -Name "MySQL" -ErrorAction SilentlyContinue
    Start-Sleep 2
}
if ((Get-Service -Name "MySQL").Status -eq "Running") {
    Write-Host "[OK] MySQL running" -ForegroundColor Green
} else {
    Write-Host "[X] MySQL not running" -ForegroundColor Red
}
Write-Host ""

stop-all
Write-Host ""

$ok = start-backend
Write-Host ""

if ($ok) { $ok = $ok -and (start-vite 5173 "Admin")   }
if ($ok) { $ok = $ok -and (start-vite 5174 "Teacher") }
if ($ok) { $ok = $ok -and (start-vite 5175 "Student") }
Write-Host ""

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Done" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  Admin    http://localhost:5173/admin.html"   -ForegroundColor Yellow
Write-Host "  Teacher  http://localhost:5174/teacher.html" -ForegroundColor Yellow
Write-Host "  Student  http://localhost:5175/student.html"  -ForegroundColor Yellow
Write-Host "  Backend  http://localhost:5000"                  -ForegroundColor Yellow
Write-Host ""
if ($ok) { Write-Host "All services started!" -ForegroundColor Green }
else { Write-Host "Some services failed!" -ForegroundColor Red }
