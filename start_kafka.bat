@echo off
echo ==========================================
echo    Kafka Setup and Startup Script
echo ==========================================
echo.

set KAFKA_DIR=kafka_2.13-2.8.2
set KAFKA_URL=https://archive.apache.org/dist/kafka/2.8.2/kafka_2.13-2.8.2.tgz

echo Checking if Kafka is already installed...
if exist "%KAFKA_DIR%" (
    echo ✓ Kafka is already installed in %KAFKA_DIR%
    goto start_kafka
)

echo.
echo Kafka is not installed. Please download and extract Kafka manually:
echo.
echo 1. Download Kafka from: %KAFKA_URL%
echo 2. Extract to this directory as: %KAFKA_DIR%
echo 3. Run this script again
echo.
echo Alternative: Install using Windows Subsystem for Linux (WSL)
echo or use Docker to run Kafka
echo.
pause
exit /b 1

:start_kafka
echo.
echo ==========================================
echo Starting Kafka Services
echo ==========================================
echo.

echo [1/2] Starting Zookeeper...
start "Zookeeper" cmd /k "cd %KAFKA_DIR% && bin\windows\zookeeper-server-start.bat config\zookeeper.properties"
echo Waiting for Zookeeper to start...
timeout /t 10

echo [2/2] Starting Kafka Broker...
start "Kafka Broker" cmd /k "cd %KAFKA_DIR% && bin\windows\kafka-server-start.bat config\server.properties"
echo Waiting for Kafka Broker to start...
timeout /t 15

echo.
echo ==========================================
echo Kafka Services Started Successfully!
echo.
echo Zookeeper: localhost:2181
echo Kafka Broker: localhost:9092
echo.
echo You can now run the Vehicle Retail services
echo ==========================================
pause
