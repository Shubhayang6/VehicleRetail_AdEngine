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

echo [3/7] Starting Telematics ECU Simulator...
start "Telematics ECU" cmd /k "cd Telematics_ECU && python telematics_ecu_simulator.py"
timeout /t 3

echo [4/7] Starting Data Processing Service...
start "Data Processing" cmd /k "cd Data_Processing && python data_processing_service.py"
timeout /t 3

echo [5/7] Starting ML Pipeline Service...
start "ML Pipeline" cmd /k "cd ML_Pipeline && python predictive_maintenance_service.py"
timeout /t 3

echo [6/7] Starting Ad & Recommendation Engine...
start "Ad Engine" cmd /k "cd Ad_Engine && python ad_engine_service.py"
timeout /t 3

echo [7/7] Starting E-commerce API...
start "E-commerce API" cmd /k "cd Ecommerce_API && python ecommerce_api.py"
timeout /t 3

echo.
echo ==========================================
echo Backend services are starting up...
echo.
echo Services and their files:
echo - Telematics ECU:       Telematics_ECU/telematics_ecu_simulator.py
echo - Data Processing:     Data_Processing/data_processing_service.py
echo - ML Pipeline:         ML_Pipeline/predictive_maintenance_service.py
echo - Ad Engine:           Ad_Engine/ad_engine_service.py
echo - E-commerce API:      Ecommerce_API/ecommerce_api.py
echo.
echo Next steps:
echo 1. Open new terminal and run: cd Android_App ^&^& npm install ^&^& npm run dev
echo 2. Open another terminal and run: cd Infotainment_Display ^&^& npm install ^&^& npm run dev
echo.
echo Frontend Access URLs:
echo - Mobile App: http://localhost:3000
echo - Infotainment: http://localhost:3001
echo.
echo Note: Check individual terminal windows for service status and ports
echo ==========================================
pause
