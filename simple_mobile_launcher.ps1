# Heart Sound Analyzer - Mobile Access Launcher
Write-Host "Heart Sound Analyzer - Mobile Access Setup" -ForegroundColor Green
Write-Host "=================================================="

# Get local IP
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"})[0].IPAddress
if (-not $localIP) {
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne "127.0.0.1"})[0].IPAddress
}

Write-Host "Local IP: $localIP" -ForegroundColor Cyan

# Kill existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
try {
    Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
} catch {}

# Start servers
Write-Host "Starting Main Analyzer on port 8501..." -ForegroundColor Green
$mainJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
}

Write-Host "Starting Mobile Recorder on port 8502..." -ForegroundColor Green  
$mobileJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    streamlit run mobile_recorder.py --server.port 8502 --server.address 0.0.0.0 --server.headless true
}

Write-Host "Waiting for servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "ACCESS URLS:" -ForegroundColor Green
Write-Host "Main Analyzer: http://$localIP:8501" -ForegroundColor White
Write-Host "Mobile Recorder: http://$localIP:8502" -ForegroundColor White

Write-Host ""
Write-Host "MOBILE INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "1. Open http://$localIP:8501 in your browser"
Write-Host "2. Find the QR code on the page"  
Write-Host "3. Scan with your phone camera"
Write-Host "4. Phone should open mobile recorder"

Write-Host ""
Write-Host "Press Ctrl+C to stop servers" -ForegroundColor Red

try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host "Stopping servers..." -ForegroundColor Red
    Stop-Job -Job $mainJob, $mobileJob -ErrorAction SilentlyContinue
    Remove-Job -Job $mainJob, $mobileJob -ErrorAction SilentlyContinue
    Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue
    Write-Host "Servers stopped!" -ForegroundColor Green
}