@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    Vehicle Retail Ad Engine Launcher
echo ==========================================
echo.
echo This script will set up and launch the complete
echo Vehicle Retail Ad Engine ecosystem following
echo the README.md setup guide.
echo.
echo Components to be started:
echo - 5 Backend Services (Python Flask APIs)
echo - 2 Frontend Applications (React Apps)
echo.
echo Make sure you have installed:
echo - Python 3.8+ with pip
echo - Node.js 16+ with npm
echo.
pause

echo.
echo ==========================================
echo [STEP 2/9] Starting Kafka Services
echo ==========================================
echo.

echo Checking if Docker is available for Kafka...
docker --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✓ Docker found - Starting Kafka with Docker
    docker-compose up -d
    if !errorlevel! equ 0 (
        echo ✓ Kafka services started with Docker
        echo Waiting for Kafka to be ready...
        timeout /t 20 /nobreak >nul
    ) else (
        echo ⚠ Docker Kafka startup failed - continuing without Kafka
    )
) else (
    echo ⚠ Docker not found - Kafka services will need manual setup
    echo Please run start_kafka_docker.bat or install Kafka manually
)

echo.
echo ==========================================
echo [STEP 3/9] Setting up Python Environment
echo ==========================================
echo.

echo Creating Python virtual environment...
if not exist ".venv" (
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed and in PATH
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created successfully
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo ERROR: Failed to install Python dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)
echo ✓ Python dependencies installed successfully

echo.
echo ==========================================
echo [STEP 4/9] Starting Backend Services
echo ==========================================
echo.

echo Starting Telematics ECU Simulator...
start "Telematics ECU" cmd /k "title Telematics ECU Simulator && call .venv\Scripts\activate.bat && cd Telematics_ECU && echo Starting Telematics ECU Simulator... && python telematics_ecu_simulator.py"
timeout /t 3 /nobreak >nul

echo Starting Data Processing Service (Port 5001)...
start "Data Processing Service" cmd /k "title Data Processing Service && call .venv\Scripts\activate.bat && cd Data_Processing && echo Starting Data Processing Service... && python data_processing_service.py"
timeout /t 3 /nobreak >nul

echo Starting ML Pipeline (Port 5002)...
start "ML Pipeline" cmd /k "title ML Pipeline && call .venv\Scripts\activate.bat && cd ML_Pipeline && echo Starting ML Pipeline... && python predictive_maintenance_service.py"
timeout /t 3 /nobreak >nul

echo Starting Ad ^& Recommendation Engine (Port 5004)...
start "Ad Engine" cmd /k "title Ad Engine && call .venv\Scripts\activate.bat && cd Ad_Engine && echo Starting Ad Engine... && python ad_engine_service.py"
timeout /t 3 /nobreak >nul

echo Starting E-commerce API (Port 5005)...
start "E-commerce API" cmd /k "title E-commerce API && call .venv\Scripts\activate.bat && cd Ecommerce_API && echo Starting E-commerce API... && python ecommerce_api.py"
timeout /t 3 /nobreak >nul

echo ✓ All backend services are starting up...

echo.
echo ==========================================
echo [STEP 5/9] Waiting for Backend Services
echo ==========================================
echo.
echo Waiting 15 seconds for backend services to initialize...
timeout /t 15 /nobreak >nul

echo.
echo ==========================================
echo [STEP 6/9] Testing Backend Health
echo ==========================================
echo.

echo Testing backend service health...
echo Checking Data Processing Service...
curl -s http://localhost:5001/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✓ Data Processing Service is running
) else (
    echo ⚠ Data Processing Service may still be starting
)

curl -s http://localhost:5002/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✓ ML Pipeline is running
) else (
    echo ⚠ ML Pipeline may still be starting
)

curl -s http://localhost:5003/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✓ Predictive Maintenance Service is running
) else (
    echo ⚠ Predictive Maintenance Service may still be starting
)

curl -s http://localhost:5004/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✓ Ad Engine is running
) else (
    echo ⚠ Ad Engine may still be starting
)

curl -s http://localhost:5005/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✓ E-commerce API is running
) else (
    echo ⚠ E-commerce API may still be starting
)

echo.
echo ==========================================
echo [STEP 7/9] Setting up Mobile App
echo ==========================================
echo.

echo Installing Mobile App dependencies...
cd Android_App
if not exist "node_modules" (
    echo Running npm install for Mobile App...
    call npm install
    if !errorlevel! neq 0 (
        echo ERROR: Failed to install Mobile App dependencies
        echo Make sure Node.js and npm are installed
        pause
        cd ..
        exit /b 1
    )
    echo ✓ Mobile App dependencies installed
) else (
    echo ✓ Mobile App dependencies already installed
)
cd ..

echo.
echo ==========================================
echo [STEP 8/9] Setting up Infotainment Display
echo ==========================================
echo.

echo Installing Infotainment Display dependencies...
cd Infotainment_Display
if not exist "node_modules" (
    echo Running npm install for Infotainment Display...
    call npm install
    if !errorlevel! neq 0 (
        echo ERROR: Failed to install Infotainment Display dependencies
        echo Make sure Node.js and npm are installed
        pause
        cd ..
        exit /b 1
    )
    echo ✓ Infotainment Display dependencies installed
) else (
    echo ✓ Infotainment Display dependencies already installed
)
cd ..

echo.
echo ==========================================
echo [STEP 9/9] Starting Frontend Applications
echo ==========================================
echo.

echo Starting Mobile App (Port 3000)...
start "Mobile App" cmd /k "title Mobile App - Android Simulation && cd Android_App && echo Starting Mobile App on http://localhost:3000... && call npm run dev"
timeout /t 5 /nobreak >nul

echo Starting Infotainment Display (Port 3001)...
start "Infotainment Display" cmd /k "title Infotainment Display - Car Dashboard && cd Infotainment_Display && echo Starting Infotainment Display on http://localhost:3001... && call npm run dev"
timeout /t 5 /nobreak >nul

echo ✓ Frontend applications are starting up...

echo.
echo ==========================================
echo [STEP 9/9] Launch Complete!
echo ==========================================
echo.
echo 🎉 Vehicle Retail Ad Engine is now running!
echo.
echo 📱 FRONTEND APPLICATIONS:
echo    Mobile App:           http://localhost:3000
echo    Infotainment Display: http://localhost:3001
echo.
echo 🔧 BACKEND API SERVICES:
echo    Data Processing:      http://localhost:5001
echo    ML Pipeline:          http://localhost:5002
echo    Maintenance Service:  http://localhost:5003
echo    Ad Engine:            http://localhost:5004
echo    E-commerce API:       http://localhost:5005
echo.
echo 🧪 QUICK TESTING:
echo    Test all services:    curl http://localhost:5001/health
echo    Get recommendations:  curl http://localhost:5004/ads/contextual
echo    View products:        curl http://localhost:5005/products
echo.
echo 📚 DEMO SCENARIOS:
echo    1. Open Mobile App - Navigate all tabs
echo    2. Open Infotainment - Check contextual ads
echo    3. Test shopping cart - Add/remove items
echo    4. Monitor real-time data updates
echo.
echo ⚠️  NOTE: 
echo    - Frontend apps may take 30-60 seconds to fully load
echo    - All windows will remain open for monitoring
echo    - Close this window to keep services running
echo.
echo 🚗 Ready to explore the future of connected vehicle retail!
echo.

echo Opening applications in 10 seconds...
timeout /t 10 /nobreak >nul

echo Opening Mobile App...
start http://localhost:3000

timeout /t 3 /nobreak >nul

echo Opening Infotainment Display...
start http://localhost:3001

echo.
echo ==========================================
echo    All systems are now operational!
echo    Check the opened browser tabs
echo ==========================================
echo.
pause