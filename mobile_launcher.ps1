# Heart Sound Analyzer - Mobile Access Launcher
# This script configures and launches the mobile-accessible version

Write-Host "🫀 Heart Sound Analyzer - Mobile Access Setup" -ForegroundColor Green
Write-Host "=" * 50

# Get local IP
$localIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Wi-Fi* | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*"})[0].IPAddress
if (-not $localIP) {
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne "127.0.0.1" -and $_.IPAddress -notlike "169.254.*"})[0].IPAddress
}

Write-Host "🌐 Local IP: $localIP" -ForegroundColor Cyan

# Kill existing Streamlit processes
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
try {
    Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
} catch {
    # Ignore errors
}

# Start main analyzer
Write-Host "🚀 Starting Main Analyzer on port 8501..." -ForegroundColor Green
$mainJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --server.runOnSave false
}

# Start mobile recorder  
Write-Host "📱 Starting Mobile Recorder on port 8502..." -ForegroundColor Green
$mobileJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    streamlit run mobile_recorder.py --server.port 8502 --server.address 0.0.0.0 --server.headless true --server.runOnSave false
}

# Wait for startup
Write-Host "⏳ Waiting for servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Test connectivity
Write-Host "🔍 Testing connectivity..." -ForegroundColor Cyan
$urls = @{
    "Main Analyzer (localhost)" = "http://localhost:8501"
    "Mobile Recorder (localhost)" = "http://localhost:8502"
    "Main Analyzer (network)" = "http://$localIP:8501"
    "Mobile Recorder (network)" = "http://$localIP:8502"
}

foreach ($name in $urls.Keys) {
    try {
        $response = Invoke-WebRequest -Uri $urls[$name] -Method Head -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ $name : Status $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $name : Failed" -ForegroundColor Red
    }
}

# Show access information
Write-Host ""
Write-Host "🎯 ACCESS URLS:" -ForegroundColor Green
Write-Host "📊 Main Analyzer: http://$localIP:8501" -ForegroundColor White
Write-Host "📱 Mobile Recorder: http://$localIP:8502" -ForegroundColor White

Write-Host ""
Write-Host "📱 MOBILE INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "1. Open http://$localIP:8501 in your browser" -ForegroundColor White
Write-Host "2. Scroll down to find the QR code" -ForegroundColor White  
Write-Host "3. Scan QR code with your phone camera" -ForegroundColor White
Write-Host "4. Your phone should open the mobile recorder" -ForegroundColor White

Write-Host ""
Write-Host "🛠️ TROUBLESHOOTING:" -ForegroundColor Yellow
Write-Host "- Make sure phone and computer are on same WiFi network" -ForegroundColor White
Write-Host "- If connection fails, run 'add_firewall_rule.bat' as Administrator" -ForegroundColor White
Write-Host "- Try using mobile hotspot if WiFi doesn't work" -ForegroundColor White

Write-Host ""
Write-Host "⏹️ Press Ctrl+C to stop servers" -ForegroundColor Red
Write-Host "🔄 Servers are running in background..." -ForegroundColor Cyan

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
        # Check if jobs are still running
        if ($mainJob.State -eq "Failed" -or $mobileJob.State -eq "Failed") {
            Write-Host "❌ One or more servers failed!" -ForegroundColor Red
            break
        }
    }
} catch {
    Write-Host ""
    Write-Host "🛑 Stopping servers..." -ForegroundColor Red
    Stop-Job -Job $mainJob, $mobileJob -ErrorAction SilentlyContinue
    Remove-Job -Job $mainJob, $mobileJob -ErrorAction SilentlyContinue
    Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue
    Write-Host "Servers stopped!" -ForegroundColor Green
}