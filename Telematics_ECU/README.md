# Telematics ECU Simulator

This module simulates a Telematics Electronic Control Unit (ECU) that reads vehicle sensor data from CSV datasets and streams it to Kafka topics according to the local architecture.

## Overview

The Telematics ECU Simulator serves as the entry point for data in our vehicle retail and predictive maintenance architecture. It:

1. **Reads CSV datasets** containing vehicle sensor data
2. **Processes and streams data** to Kafka topics in real-time simulation
3. **Supports multiple simulation modes** (all vehicles, single vehicle, multi-vehicle)
4. **Maintains data relationships** across different sensor types

## Architecture Role

```
CSV Datasets → Telematics ECU Simulator → Kafka Topics → Data Processing Service
```

According to the local architecture, this component:
- Reads from: `Simulated Sensors (CSV/JSON)`
- Outputs to: `Local Message Broker (Apache Kafka)`

## Files Structure

```
Telematics_ECU/
├── telematics_ecu_simulator.py    # Main simulator with Kafka integration
├── test_simulator.py              # Test simulator without Kafka dependencies
├── config.json                    # Configuration file
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Configuration

Edit `config.json` to customize:

```json
{
  "kafka": {
    "bootstrap_servers": ["localhost:9092"],
    "topics": {
      "core_sensor": "sensor-data-topic",
      "vehicle_health": "health-data-topic", 
      "driving_behavior": "behavior-topic",
      "environmental": "environment-topic"
    }
  },
  "datasets": {
    "core_sensor_data": "../Dataset/core_sensor_data.csv",
    "vehicle_health_data": "../Dataset/vehicle_health_data.csv",
    "driving_behavior_data": "../Dataset/driving_behavior_data.csv",
    "environmental_data": "../Dataset/environmental_data.csv"
  },
  "simulation": {
    "speed_multiplier": 1,      // 1=real-time, 10=10x faster
    "replay_interval_seconds": 5, // Send data every 5 seconds
    "batch_size": 1
  }
}
```

## Installation

### 1. Install Dependencies (Method 1: With Kafka)
```bash
# Install required packages including Kafka client
pip install pandas numpy kafka-python python-dateutil
```

### 2. Install Dependencies (Method 2: Test Mode Only)
```bash
# For testing without Kafka
pip install pandas numpy python-dateutil
```

## Usage

### Test Mode (Without Kafka)

Start with the test simulator to verify functionality without Kafka:

```bash
# Test with all vehicles (limited records)
python test_simulator.py --max-records 20

# Test with specific vehicle
python test_simulator.py --vehicle-id VEH_001 --max-records 10
```

**Output**: Creates `output/` directory with JSON files containing streamed data.

### Production Mode (With Kafka)

1. **Start Kafka** (ensure Kafka is running on localhost:9092)
2. **Run the simulator**:

```bash
# Stream all vehicles in real-time
python telematics_ecu_simulator.py --mode all_vehicles

# Stream specific vehicle
python telematics_ecu_simulator.py --mode single_vehicle --vehicle-id VEH_001

# Stream multiple vehicles in parallel
python telematics_ecu_simulator.py --mode multi_vehicle

# Run for specific duration
python telematics_ecu_simulator.py --mode all_vehicles --duration 300
```

## Data Flow

### Input Datasets
The simulator reads from 4 CSV files:
- `core_sensor_data.csv` → `sensor-data-topic`
- `vehicle_health_data.csv` → `health-data-topic`
- `driving_behavior_data.csv` → `behavior-topic`
- `environmental_data.csv` → `environment-topic`

### Output Format
Each Kafka message contains:
```json
{
  "timestamp": "2024-01-01 20:00:00",
  "vehicle_id": "VEH_001",
  "speed_kmh": 39.1,
  "engine_temp_c": 101.6,
  "dataset_type": "core_sensor_data",
  "simulation_time": "2024-08-18 15:30:45",
  // ... other sensor fields
}
```

## Simulation Modes

### 1. All Vehicles Mode
- Streams data from all vehicles chronologically
- Maintains temporal relationships across datasets
- Best for system-wide testing

### 2. Single Vehicle Mode  
- Focuses on one vehicle's complete data journey
- Useful for detailed analysis and debugging
- Maintains all data relationships for that vehicle

### 3. Multi-Vehicle Mode
- Parallel streaming of multiple vehicles
- Simulates realistic concurrent vehicle operations
- Limited to first 5 vehicles for performance

## Features

### Real-time Simulation
- Configurable speed multiplier (1x to 100x)
- Maintains timestamp relationships
- Adjustable replay intervals

### Data Processing
- Automatic timestamp conversion
- NaN value handling
- Metadata injection
- Vehicle ID keying for Kafka partitioning

### Error Handling
- Kafka connection retry logic
- Graceful degradation
- Comprehensive logging
- Clean shutdown on interruption

## Monitoring

### Logs
The simulator provides detailed logging:
- INFO: General operation status
- DEBUG: Individual message details  
- ERROR: Connection and processing failures

### Status Checking
```python
simulator = TelematicsECUSimulator()
status = simulator.get_simulation_status()
print(status)
# Output: {'running': True, 'datasets_loaded': 4, 'active_threads': 1, 'kafka_connected': True}
```

## Next Steps

Once the Telematics ECU Simulator is running:

1. **Verify Kafka Topics**: Check that messages are being published
2. **Start Data Processing Service**: Next component in the pipeline
3. **Monitor Data Flow**: Ensure proper message routing
4. **Tune Performance**: Adjust speed multiplier and batch size

## Troubleshooting

### Common Issues

1. **Dataset Not Found**
   - Check file paths in `config.json`
   - Ensure CSV files exist in Dataset directory

2. **Kafka Connection Failed**
   - Verify Kafka is running on localhost:9092
   - Check network connectivity
   - Review Kafka logs

3. **Memory Issues**
   - Reduce speed multiplier
   - Limit vehicle count in multi-vehicle mode
   - Monitor system resources

### Debug Mode
```bash
# Run with verbose logging
python telematics_ecu_simulator.py --mode single_vehicle --vehicle-id VEH_001
```

## Integration with Architecture

This component integrates with:
- **Input**: CSV datasets from `../Dataset/` directory
- **Output**: Kafka topics consumed by Data Processing Service
- **Configuration**: Shared config for topic names and connection details
- **Monitoring**: Logs compatible with centralized logging system

The Telematics ECU Simulator is the foundation for realistic vehicle data simulation in the local architecture.
