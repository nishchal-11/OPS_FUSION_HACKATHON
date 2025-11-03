@echo off
echo ========================================
echo   Heart Sound Mobile Analyzer
echo   Starting on Port 8503
echo ========================================
echo.
echo Desktop: http://localhost:8503
echo Mobile: http://192.168.20.26:8503
echo.
echo Press Ctrl+C to stop the server
echo ========================================
C:\Users\Nishc\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run mobile_app.py --server.port 8503
