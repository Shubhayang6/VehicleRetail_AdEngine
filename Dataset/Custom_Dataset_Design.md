# Custom Vehicle Sensor Dataset Design

Based on the PVS (Passive Vehicular Sensors) dataset reference and our architecture requirements, here's a comprehensive dataset design for predictive maintenance and retail recommendations.

## Dataset Structure

### **1. Core Sensor Data (Real-time)**
```csv
timestamp,vehicle_id,latitude,longitude,speed_kmh,acceleration_x,acceleration_y,acceleration_z,gyroscope_x,gyroscope_y,gyroscope_z,engine_rpm,engine_temp_c,fuel_level_percent,brake_pressure_psi,throttle_position_percent,gear_position,mileage_km
```

### **2. Vehicle Health Data (Diagnostic)**
```csv
timestamp,vehicle_id,engine_oil_temp_c,coolant_temp_c,transmission_temp_c,battery_voltage,engine_load_percent,intake_air_temp_c,mass_air_flow_rate,oxygen_sensor_voltage,catalytic_converter_temp_c,tire_pressure_fl,tire_pressure_fr,tire_pressure_rl,tire_pressure_rr,brake_fluid_level,windshield_washer_level
```

### **3. Driving Behavior Data (Derived)**
```csv
timestamp,vehicle_id,harsh_braking_count,harsh_acceleration_count,sharp_turn_count,speeding_incidents,idle_time_minutes,avg_speed_trip,max_speed_trip,driving_score,aggressive_driving_flag,eco_driving_score
```

### **4. Environmental Context Data**
```csv
timestamp,vehicle_id,weather_condition,temperature_outside_c,road_type,terrain_type,traffic_density,location_type,altitude_m,humidity_percent,road_surface_condition
```

### **5. Maintenance History Data**
```csv
vehicle_id,service_date,service_type,mileage_at_service,parts_replaced,cost,next_service_due_km,oil_change_due_km,tire_rotation_due_km,brake_inspection_due_km
```

---

## Key Features for Predictive Maintenance

### **Engine Health Indicators**
- `engine_oil_temp_c`: Oil temperature (overheating detection)
- `engine_temp_c`: Engine temperature
- `engine_rpm`: RPM patterns for wear analysis
- `engine_load_percent`: Engine stress levels
- `oxygen_sensor_voltage`: Combustion efficiency

### **Brake System Indicators**
- `brake_pressure_psi`: Brake system pressure
- `brake_fluid_level`: Fluid level monitoring
- `harsh_braking_count`: Brake wear estimation

### **Tire Health Indicators**
- `tire_pressure_fl/fr/rl/rr`: Individual tire pressures
- `sharp_turn_count`: Tire wear patterns
- `road_surface_condition`: Wear factor

### **Transmission Indicators**
- `transmission_temp_c`: Transmission health
- `gear_position`: Shift patterns
- `throttle_position_percent`: Usage patterns

---

## Features for Retail Recommendations

### **Location-Based Recommendations**
- `latitude/longitude`: GPS coordinates
- `terrain_type`: Hills, city, highway (for oil/parts recommendations)
- `road_type`: Surface conditions affecting parts wear
- `altitude_m`: Mountain driving conditions

### **Driving Style Based**
- `aggressive_driving_flag`: High-performance parts recommendations
- `eco_driving_score`: Eco-friendly product suggestions
- `harsh_braking_count`: Brake pad recommendations
- `avg_speed_trip`: Highway vs city driving products

### **Seasonal/Weather Based**
- `weather_condition`: Rain, snow, heat (tire/fluid recommendations)
- `temperature_outside_c`: Seasonal product suggestions
- `humidity_percent`: Corrosion protection products

---

## Sample Data Generation Strategy

### **1. Base Vehicle Data (from Kaggle PVS)**
- Use existing GPS, accelerometer, gyroscope data
- Extract speed, acceleration patterns

### **2. Synthetic Engine Data**
```python
# Engine temperature based on load and ambient temperature
engine_temp = base_temp + (engine_load * 0.8) + ambient_temp_factor

# Oil temperature correlation with engine temp
oil_temp = engine_temp * 0.9 + random_noise

# RPM patterns based on speed and gear
engine_rpm = (speed_kmh / gear_ratio) * 60 + idle_rpm
```

### **3. Maintenance Prediction Labels**
```python
# Generate maintenance flags based on:
- High engine temperature patterns
- Low fluid levels
- High mileage intervals
- Aggressive driving patterns
- Environmental stress factors
```

### **4. Retail Recommendation Context**
```python
# Generate product recommendation triggers:
- Mountain driving → High-performance oil
- City driving → Brake pad wear
- Hot climate → Cooling system products
- High mileage → Maintenance packages
```

---

## Dataset Size Recommendations

- **Training Data**: 50,000+ vehicle trips
- **Time Period**: 6-12 months of data
- **Vehicles**: 100-500 different vehicles
- **Sampling Rate**: 1 Hz for real-time data, hourly for diagnostic data

---

## Integration with Architecture

### **Data Flow**
1. **CSV/JSON files** → Telematics ECU Simulator
2. **Kafka streams** → Data Processing Service
3. **ML Pipeline** → Maintenance predictions
4. **Ad Engine** → Product recommendations based on context

### **ML Model Inputs**
- Engine health scores
- Driving behavior patterns
- Environmental factors
- Maintenance history
- Location context

This dataset design provides comprehensive data for both predictive maintenance and contextual retail recommendations while being realistic for simulation purposes.
