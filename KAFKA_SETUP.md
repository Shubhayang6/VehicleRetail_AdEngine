# Kafka Setup Guide for Vehicle Retail Ad Engine

## 🚀 Quick Setup Options

### Option 1: Docker (Recommended - Easiest)

1. **Install Docker Desktop**: https://www.docker.com/products/docker-desktop
2. **Start Kafka services**:
   ```bash
   start_kafka_docker.bat
   ```

### Option 2: Manual Kafka Installation

1. **Download Kafka**: https://kafka.apache.org/downloads
2. **Extract to project directory**
3. **Run**: `start_kafka.bat`

## 🐳 Docker Setup (Recommended)

### Prerequisites
- Docker Desktop installed and running
- At least 4GB RAM available for containers

### Quick Start
```bash
# Start Kafka with Docker
start_kafka_docker.bat

# Or manually
docker-compose up -d
```

### Verify Kafka is Running
```bash
# Check container status
docker ps

# Test Kafka connection
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

## 🔧 Manual Kafka Setup

If you prefer not to use Docker:

### Windows Manual Setup
1. Download Kafka 2.8.2: https://archive.apache.org/dist/kafka/2.8.2/kafka_2.13-2.8.2.tgz
2. Extract to `kafka_2.13-2.8.2` folder in project root
3. Run `start_kafka.bat`

### Linux/macOS Manual Setup
```bash
# Download and extract Kafka
wget https://archive.apache.org/dist/kafka/2.8.2/kafka_2.13-2.8.2.tgz
tar -xzf kafka_2.13-2.8.2.tgz

# Start Zookeeper
kafka_2.13-2.8.2/bin/zookeeper-server-start.sh kafka_2.13-2.8.2/config/zookeeper.properties

# Start Kafka (in new terminal)
kafka_2.13-2.8.2/bin/kafka-server-start.sh kafka_2.13-2.8.2/config/server.properties
```

## 🧪 Testing Kafka Connection

### Create Test Topic
```bash
# Docker
docker exec kafka kafka-topics --create --bootstrap-server localhost:9092 --topic test-topic --partitions 1 --replication-factor 1

# Manual
kafka_2.13-2.8.2/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic test-topic --partitions 1 --replication-factor 1
```

### Send Test Message
```bash
# Docker
docker exec -it kafka kafka-console-producer --bootstrap-server localhost:9092 --topic test-topic

# Manual
kafka_2.13-2.8.2/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic test-topic
```

### Consume Test Message
```bash
# Docker
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic test-topic --from-beginning

# Manual
kafka_2.13-2.8.2/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic --from-beginning
```

## 🚗 Vehicle Retail Integration

Once Kafka is running, the Telematics ECU Simulator will:

1. **Connect to Kafka** at `localhost:9092`
2. **Create topics automatically**:
   - `vehicle-telemetry`
   - `sensor-data`
   - `health-monitoring`
   - `driving-behavior`

3. **Stream real-time data** from CSV datasets

## 🐛 Troubleshooting

### Common Issues

**"NoBrokersAvailable" Error**
- Kafka is not running
- Check: `docker ps` or process list
- Solution: Run `start_kafka_docker.bat`

**"Connection Refused" Error**
- Kafka may be starting up
- Wait 30-60 seconds and try again
- Check Kafka logs for errors

**Docker Issues**
- Ensure Docker Desktop is running
- Check available memory (need 4GB+)
- Restart Docker Desktop if needed

**Port Conflicts**
- Default ports: 2181 (Zookeeper), 9092 (Kafka)
- Check if ports are in use: `netstat -ano | findstr :9092`
- Kill conflicting processes or change ports

### Viewing Logs

**Docker Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f kafka
docker-compose logs -f zookeeper
```

**Manual Setup Logs**
- Check terminal windows where Kafka/Zookeeper are running
- Look for startup completion messages

## 🔄 Starting/Stopping Services

### Docker Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Remove all data (clean start)
docker-compose down -v
```

### Manual Commands
- Close terminal windows to stop services
- Or use Ctrl+C in each terminal

## ✅ Verification Checklist

Before running the Vehicle Retail system:

- [ ] Kafka is running on port 9092
- [ ] Zookeeper is running on port 2181
- [ ] Can create/list topics successfully
- [ ] No "NoBrokersAvailable" errors
- [ ] Docker containers healthy (if using Docker)

## 🎯 Next Steps

Once Kafka is running:

1. **Run the full system**: `run_project.bat`
2. **Or start backend only**: `start_backend.bat`
3. **Monitor Telematics ECU logs** for successful data streaming
4. **Check vehicle data** flowing to downstream services

---

**Ready to stream vehicle data with Kafka!** 🚗💨
