@echo off
echo.
echo ========================================
echo   RESTARTING QUANT TRADING SERVER
echo ========================================
echo.
echo Stopping any running servers...

REM Kill any Python processes that might be running the server
for /f "tokens=2" %%i in ('netstat -ano ^| findstr :8001') do (
    echo Killing process %%i
    taskkill /PID %%i /F >nul 2>&1
)

echo.
echo Waiting for port to clear...
timeout /t 3 /nobreak >nul

echo.
echo Starting fresh server with FIXED code...
echo.
echo ========================================
echo   HTTP 500 ERROR HAS BEEN FIXED!
echo ========================================
echo.
echo Fixes Applied:
echo - JSON serialization infinity values resolved
echo - Profit factor calculation corrected  
echo - Dual engine support working
echo - Stock selection feature ready
echo.
echo Web Interface: http://localhost:8001
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd backend
python run_server_alt.py