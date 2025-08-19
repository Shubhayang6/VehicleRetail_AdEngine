@echo off
echo ==========================================
echo    Vehicle Retail Ad Engine Startup
echo ==========================================
echo.

echo [1/7] Setting up Python virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo [2/7] Installing Python dependencies...
pip install -r requirements.txt

echo [3/7] Starting Data Processing Service...
start "Data Processing" cmd /k "cd DataProcessing_Service && python app.py"
timeout /t 3

echo [4/7] Starting ML Pipeline...
start "ML Pipeline" cmd /k "cd ML_Pipeline && python app.py"
timeout /t 3

echo [5/7] Starting Predictive Maintenance Service...
start "Maintenance Service" cmd /k "cd PredictiveMaintenance_Service && python app.py"
timeout /t 3

echo [6/7] Starting Ad & Recommendation Engine...
start "Ad Engine" cmd /k "cd Ad_RecommendationEngine && python app.py"
timeout /t 3

echo [7/7] Starting E-commerce API...
start "E-commerce API" cmd /k "cd Ecommerce_API && python app.py"
timeout /t 3

echo.
echo ==========================================
echo Backend services are starting up...
echo.
echo Next steps:
echo 1. Open new terminal and run: cd Android_App ^&^& npm install ^&^& npm run dev
echo 2. Open another terminal and run: cd Infotainment_Display ^&^& npm install ^&^& npm run dev
echo.
echo Access URLs:
echo - Mobile App: http://localhost:3000
echo - Infotainment: http://localhost:3001
echo - Backend APIs: http://localhost:5001-5005
echo ==========================================
pause
