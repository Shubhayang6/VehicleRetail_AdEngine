# Data Processing Service - Three-Branch Architecture Summary

## Overview
The Data Processing Service successfully demonstrates the three-branch routing architecture you identified:

1. **Branch 1: Database Storage** - Stores processed vehicle data and health alerts
2. **Branch 2: ML Pipeline** - Routes data requiring predictions (maintenance/anomalies)  
3. **Branch 3: Ad Engine** - Routes behavior data for retail recommendations

## Test Results Summary

### Input Processing
- **Source**: Telematics ECU simulator output (80 total messages across 4 topics)
- **Processing**: 20 unique vehicle-timestamp combinations processed
- **Success Rate**: 100% (no errors encountered)

### Three-Branch Routing Results

#### Branch 1: Database Storage
- **Records Stored**: 20 complete vehicle records
- **Health Alerts**: Generated for vehicles requiring maintenance
- **Output**: `output/database/stored_records.jsonl` (20 records)
- **Database**: SQLite with processed_vehicle_data and health_alerts tables

#### Branch 2: ML Pipeline  
- **Records Sent**: 5 vehicles requiring ML predictions
- **Criteria**: Vehicles with maintenance_required=true OR anomaly_detected=true
- **Output**: `output/ml_pipeline/ml_input_data.jsonl` (5 records)
- **Data Format**: Health scores, maintenance urgency, vehicle metrics, context

#### Branch 3: Ad Engine
- **Records Sent**: 18 vehicles eligible for ad targeting
- **Criteria**: Vehicles with health_score > 0.7 (configurable threshold)
- **Output**: `output/ad_engine/ad_input_data.jsonl` (18 records)  
- **Data Format**: Behavior profile, context, vehicle profile

## Key Processing Features

### Health Analysis
- **Engine Health**: Temperature, oil temp, load analysis
- **Brake Health**: Pressure and harsh braking detection
- **Tire Health**: Pressure monitoring and variance detection
- **Overall Score**: Weighted average of all health metrics

### Behavior Analysis
- **Driving Aggressiveness**: Harsh braking/acceleration, speeding incidents
- **Eco-Driving Score**: Fuel efficiency and environmental impact
- **Maintenance Urgency**: Combined health and mileage-based scoring

### Anomaly Detection
- Engine overheating (>120°C)
- Excessive speed (>150 km/h)
- Fuel level anomalies (<5% or >105%)

## Data Flow Architecture

```
Telematics ECU Output
        ↓
Data Processing Service
        ↓
   [Processing Engine]
   - Health Analysis
   - Behavior Analysis  
   - Anomaly Detection
        ↓
    Three Branches:
        ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   Database      │   ML Pipeline   │   Ad Engine     │
│   Storage       │   Routing       │   Routing       │
│                 │                 │                 │
│ • All records   │ • Maintenance   │ • High health   │
│ • Health alerts │   required      │   vehicles      │
│ • Anomalies     │ • Anomalies     │ • Behavior data │
│                 │ • Health scores │ • Context data  │
└─────────────────┴─────────────────┴─────────────────┘
```

## Configuration Options

The service uses a JSON configuration file with:
- Health score thresholds
- Maintenance urgency thresholds  
- Database settings
- Kafka topic configurations

## Next Steps

This Data Processing Service provides the foundation for:

1. **Real-time ML Predictions**: The ML Pipeline branch can connect to predictive maintenance models
2. **Targeted Advertising**: The Ad Engine branch enables contextual retail recommendations
3. **Fleet Management**: The Database branch supports comprehensive vehicle monitoring
4. **Scalability**: The three-branch architecture allows independent scaling of each component

The service successfully processes vehicle telemetry data and intelligently routes it to the appropriate downstream systems based on the vehicle's health status, behavior patterns, and maintenance needs.
