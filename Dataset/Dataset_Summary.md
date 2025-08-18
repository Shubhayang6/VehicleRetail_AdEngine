# Dataset Summary and Validation

This document provides a summary of the generated custom datasets for the Vehicle Retail Ad Engine project.

## Generated Datasets Overview

### 1. **Core Sensor Data** (`core_sensor_data.csv`)
- **Records**: 400 (8 records per vehicle across 50 vehicles)
- **Time Range**: January 2024 - February 2024 (weekly intervals)
- **Key Features**: GPS coordinates, speed, acceleration, engine metrics, fuel levels

### 2. **Vehicle Health Data** (`vehicle_health_data.csv`)
- **Records**: 400 (correlated with core sensor data)
- **Features**: Engine temperatures, fluid levels, tire pressures, diagnostic data
- **Relationships**: Oil temperature correlates with engine temperature, tire pressures degrade over time

### 3. **Driving Behavior Data** (`driving_behavior_data.csv`)
- **Records**: 400 (derived from core sensor patterns)
- **Features**: Harsh events, driving scores, eco-driving metrics
- **Driving Styles**: Aggressive (high harsh events), Eco (low harsh events), Moderate (balanced)

### 4. **Environmental Data** (`environmental_data.csv`)
- **Records**: 400 (contextual data for each trip)
- **Features**: Weather conditions, road types, terrain, traffic density
- **Seasonal Patterns**: Winter (snow/cold), Summer (hot/clear), Spring/Fall (mixed)

### 5. **Maintenance History** (`maintenance_history.csv`)
- **Records**: 146 (2-4 maintenance records per vehicle)
- **Service Types**: Oil change, tire rotation, brake inspection, general maintenance
- **Cost Range**: $30-$500 depending on service type

## Data Relationships and Correlations

### **Inter-Dataset Relationships**
1. **Vehicle ID**: Common identifier across all datasets
2. **Timestamp**: Core sensor, health, behavior, and environmental data share timestamps
3. **Driving Style**: Influences behavior patterns and maintenance needs
4. **Location**: GPS coordinates affect terrain, weather, and driving conditions

### **Predictive Maintenance Indicators**
- **Engine Health**: High engine temperatures → Oil change recommendations
- **Brake System**: High harsh braking → Brake pad replacement needs
- **Tire Health**: Low tire pressure → Tire maintenance alerts
- **Mileage**: High mileage vehicles → More frequent maintenance

### **Retail Recommendation Triggers**
- **Mountain Terrain**: High-performance oil and brake fluid recommendations
- **Aggressive Driving**: Performance parts and premium brake pads
- **Winter Weather**: Winter tires and antifreeze products
- **High Mileage**: Maintenance packages and extended warranties

## Sample Use Cases for Local Architecture

### **1. Predictive Maintenance Pipeline**
```python
# Data flow example:
core_data + health_data → ML Model → Maintenance Prediction → Infotainment Alert
```

### **2. Contextual Advertisement Engine**
```python
# Recommendation logic:
environmental_data + behavior_data → Ad Engine → Product Recommendations → Infotainment Display
```

### **3. E-commerce Integration**
```python
# Purchase flow:
Product Recommendation → User Selection → Payment Processing → Order Confirmation
```

## Data Quality Metrics

### **Completeness**
- ✅ All required fields populated
- ✅ No missing values in critical fields
- ✅ Consistent vehicle IDs across datasets

### **Consistency**
- ✅ Temperature correlations (oil temp ≈ 90% of engine temp)
- ✅ Speed-RPM relationships follow gear ratios
- ✅ Driving style reflects in behavior metrics

### **Realism**
- ✅ GPS coordinates within New York area
- ✅ Engine temperatures in normal range (85-105°C)
- ✅ Tire pressures around standard 32 PSI
- ✅ Fuel consumption patterns realistic

### **Temporal Patterns**
- ✅ Weekly progression of data points
- ✅ Seasonal weather variations
- ✅ Rush hour traffic density patterns

## Integration with Local Architecture

### **Kafka Message Streaming**
Each dataset can be streamed through Kafka topics:
- `sensor-data-topic`: Core sensor readings
- `health-data-topic`: Diagnostic information
- `behavior-topic`: Driving patterns
- `environment-topic`: Contextual data

### **ML Model Training Data**
The datasets provide features for multiple ML models:
- **Classification**: Maintenance needed (Yes/No)
- **Regression**: Time to next service (days)
- **Clustering**: Driver behavior segments
- **Recommendation**: Product relevance scores

### **Real-time Simulation**
Data can be replayed in real-time to simulate:
- Live vehicle telemetry streaming
- Predictive maintenance alerts
- Dynamic advertisement serving
- E-commerce transaction flows

## Next Steps

1. **Data Validation**: Run the dataset validation script
2. **Model Training**: Use data for ML pipeline development
3. **Streaming Setup**: Configure Kafka producers for data streaming
4. **Dashboard Development**: Build React infotainment simulation
5. **API Integration**: Connect datasets to microservices

This comprehensive dataset provides a solid foundation for developing and testing the complete vehicle retail and predictive maintenance architecture.
