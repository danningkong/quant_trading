@echo off
echo.
echo ========================================
echo    QUANT TRADING PLATFORM
echo ========================================
echo.
echo Starting server...
echo.
echo After you see "Uvicorn running on http://127.0.0.1:8000"
echo manually open your browser and go to:
echo.
echo    http://127.0.0.1:8000
echo    or
echo    http://localhost:8000
echo.
echo ========================================
echo.
cd backend
python run_server.py