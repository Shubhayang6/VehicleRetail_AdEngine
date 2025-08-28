@echo off
echo ==========================================
echo    Starting Kafka with Docker
echo ==========================================
echo.

echo Checking if Docker is running...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and make sure it's running
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✓ Docker is available

echo.
echo Starting Kafka and Zookeeper containers...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start Docker containers
    echo Make sure Docker Desktop is running and try again
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Waiting for Kafka to be ready...
echo ==========================================
echo.

timeout /t 20

echo Testing Kafka connection...
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Kafka is ready and accessible on localhost:9092
) else (
    echo ⚠ Kafka may still be starting up...
    echo Wait a few more seconds and try running your services
)

echo.
echo ==========================================
echo Kafka Services Status:
echo - Zookeeper: localhost:2181
echo - Kafka Broker: localhost:9092
echo.
echo To stop Kafka: docker-compose down
echo To view logs: docker-compose logs -f
echo ==========================================
pause
