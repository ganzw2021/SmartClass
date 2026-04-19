# SmartClass 停止所有后端进程脚本

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "  正在停止所有后端进程..." -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# 停止所有 Python 进程中包含 backend 的
$stopped = $false

Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        if ($_.MainWindowTitle -like "*smartclass*" -or $_.MainWindowTitle -like "*app.py*" -or $_.MainWindowTitle -like "*backend*") {
            Write-Host "  停止进程: $($_.Id) - $($_.MainWindowTitle)" -ForegroundColor Gray
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            $stopped = $true
        }
    } catch {}
}

if ($stopped) {
    Write-Host ""
    Write-Host "  ✅ 所有后端进程已停止" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ℹ️  没有发现运行中的后端进程" -ForegroundColor Yellow
}

Write-Host ""
