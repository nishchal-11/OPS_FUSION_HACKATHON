@echo off
echo Adding Windows Firewall rule for Heart Sound Analyzer...
netsh advfirewall firewall add rule name="Heart Analyzer Streamlit" dir=in action=allow protocol=TCP localport=8501,8502
echo.
echo Firewall rule added successfully!
echo Now you can access the app from mobile devices on your network.
pause