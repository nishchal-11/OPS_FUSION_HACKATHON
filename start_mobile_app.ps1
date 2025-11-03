# Heart Sound Mobile Analyzer - Simple Startup Script
# Only runs the mobile app on port 8503

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Heart Sound Mobile Analyzer" -ForegroundColor Green
Write-Host "  Starting on Port 8503" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Desktop: http://localhost:8503" -ForegroundColor Yellow
Write-Host "Mobile: http://192.168.20.26:8503" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

C:\Users\Nishc\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run mobile_app.py --server.port 8503
