@echo off
echo Starting Heart Sound Analyzer servers...
echo.

REM Kill any existing streamlit processes
taskkill /f /im streamlit.exe >nul 2>&1

echo Starting Main Analyzer on port 8501...
start /min cmd /c "streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"

echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo Starting Mobile Recorder on port 8502...
start /min cmd /c "streamlit run mobile_recorder.py --server.port 8502 --server.address 0.0.0.0 --server.headless true"

echo Waiting 8 seconds for servers to start...
timeout /t 8 /nobreak >nul

echo.
echo =========================================
echo  HEART SOUND ANALYZER SERVERS RUNNING
echo =========================================
echo.
echo Main Analyzer: http://192.168.20.28:8501
echo Mobile Recorder: http://192.168.20.28:8502
echo.
echo QR Code Instructions:
echo 1. Open http://192.168.20.28:8501 in browser
echo 2. Scroll down to find QR code
echo 3. Scan QR code with phone
echo 4. Record heart sounds on mobile
echo.
echo Press any key to stop servers...
pause >nul

REM Stop servers when user presses key
taskkill /f /im streamlit.exe >nul 2>&1
echo Servers stopped.
pause