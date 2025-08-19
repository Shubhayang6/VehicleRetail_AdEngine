@echo off
echo ==========================================
echo   Vehicle Retail Frontend Applications
echo ==========================================
echo.

echo [1/4] Installing Mobile App dependencies...
cd Android_App
call npm install
echo.

echo [2/4] Installing Infotainment Display dependencies...
cd ..\Infotainment_Display
call npm install
echo.

echo [3/4] Starting Mobile App (Android simulation)...
start "Mobile App" cmd /k "npm run dev"
timeout /t 5

echo [4/4] Starting Infotainment Display...
start "Infotainment Display" cmd /k "npm run dev"

echo.
echo ==========================================
echo Frontend applications are starting up...
echo.
echo Access URLs:
echo - Mobile App: http://localhost:3000
echo - Infotainment Display: http://localhost:3001
echo.
echo Make sure backend services are running first!
echo (Run start_backend.bat if not already running)
echo ==========================================
pause
