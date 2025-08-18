import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_VEHICLES = 50
NUM_RECORDS_PER_VEHICLE = 8  # 400 total records
START_DATE = datetime(2024, 1, 1)

# Vehicle configurations
VEHICLE_TYPES = ['sedan', 'suv', 'truck', 'hatchback']
TERRAIN_TYPES = ['city', 'highway', 'mountain', 'mixed']
WEATHER_CONDITIONS = ['clear', 'rain', 'snow', 'fog', 'hot']
ROAD_TYPES = ['asphalt', 'concrete', 'gravel', 'dirt']
LOCATION_TYPES = ['urban', 'suburban', 'rural', 'highway']

def generate_vehicle_profiles():
    """Generate vehicle profiles with consistent characteristics"""
    vehicles = []
    for i in range(NUM_VEHICLES):
        vehicle = {
            'vehicle_id': f'VEH_{i:03d}',
            'vehicle_type': random.choice(VEHICLE_TYPES),
            'base_mileage': random.randint(10000, 150000),
            'driving_style': random.choice(['aggressive', 'moderate', 'eco']),
            'primary_terrain': random.choice(TERRAIN_TYPES),
            'base_lat': round(random.uniform(40.0, 42.0), 6),  # New York area
            'base_lon': round(random.uniform(-74.5, -73.5), 6)
        }
        vehicles.append(vehicle)
    return vehicles

def generate_core_sensor_data(vehicles):
    """Generate core sensor data"""
    data = []
    
    for vehicle in vehicles:
        for record_num in range(NUM_RECORDS_PER_VEHICLE):
            # Time progression
            timestamp = START_DATE + timedelta(days=record_num*7, hours=random.randint(6, 20))
            
            # Location with some variance around base location
            lat_variance = random.uniform(-0.1, 0.1)
            lon_variance = random.uniform(-0.1, 0.1)
            latitude = vehicle['base_lat'] + lat_variance
            longitude = vehicle['base_lon'] + lon_variance
            
            # Speed based on terrain and driving style
            if vehicle['primary_terrain'] == 'highway':
                base_speed = random.uniform(80, 120)
            elif vehicle['primary_terrain'] == 'city':
                base_speed = random.uniform(20, 60)
            elif vehicle['primary_terrain'] == 'mountain':
                base_speed = random.uniform(40, 80)
            else:  # mixed
                base_speed = random.uniform(30, 90)
                
            # Adjust for driving style
            if vehicle['driving_style'] == 'aggressive':
                speed_kmh = base_speed * random.uniform(1.1, 1.3)
            elif vehicle['driving_style'] == 'eco':
                speed_kmh = base_speed * random.uniform(0.8, 0.95)
            else:
                speed_kmh = base_speed
                
            speed_kmh = max(0, min(speed_kmh, 160))  # Cap at reasonable limits
            
            # Acceleration based on driving style
            if vehicle['driving_style'] == 'aggressive':
                accel_x = random.uniform(-3.0, 3.0)
                accel_y = random.uniform(-2.0, 2.0)
            else:
                accel_x = random.uniform(-1.5, 1.5)
                accel_y = random.uniform(-1.0, 1.0)
            
            accel_z = random.uniform(-0.5, 0.5)
            
            # Engine RPM correlated with speed
            gear_position = min(6, max(1, int(speed_kmh / 20) + 1))
            engine_rpm = (speed_kmh * 30) + random.uniform(800, 1200)
            
            # Engine temperature based on load and external factors
            engine_temp_c = random.uniform(85, 105) + (speed_kmh * 0.1)
            
            # Other sensors
            fuel_level_percent = max(5, 100 - (record_num * 12) + random.uniform(-5, 5))
            brake_pressure_psi = random.uniform(0, 50) if random.random() > 0.7 else 0
            throttle_position_percent = min(100, (speed_kmh / 120) * 100 + random.uniform(-10, 10))
            mileage_km = vehicle['base_mileage'] + (record_num * random.randint(100, 500))
            
            record = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'vehicle_id': vehicle['vehicle_id'],
                'latitude': round(latitude, 6),
                'longitude': round(longitude, 6),
                'speed_kmh': round(speed_kmh, 2),
                'acceleration_x': round(accel_x, 3),
                'acceleration_y': round(accel_y, 3),
                'acceleration_z': round(accel_z, 3),
                'gyroscope_x': round(random.uniform(-50, 50), 3),
                'gyroscope_y': round(random.uniform(-50, 50), 3),
                'gyroscope_z': round(random.uniform(-50, 50), 3),
                'engine_rpm': round(engine_rpm, 0),
                'engine_temp_c': round(engine_temp_c, 1),
                'fuel_level_percent': round(fuel_level_percent, 1),
                'brake_pressure_psi': round(brake_pressure_psi, 1),
                'throttle_position_percent': round(throttle_position_percent, 1),
                'gear_position': gear_position,
                'mileage_km': mileage_km
            }
            data.append(record)
    
    return pd.DataFrame(data)

def generate_vehicle_health_data(core_df, vehicles):
    """Generate vehicle health data correlated with core sensor data"""
    data = []
    
    for _, row in core_df.iterrows():
        # Find vehicle profile
        vehicle = next(v for v in vehicles if v['vehicle_id'] == row['vehicle_id'])
        
        # Oil temperature correlated with engine temperature
        engine_oil_temp_c = row['engine_temp_c'] * 0.9 + random.uniform(-5, 5)
        
        # Coolant temperature
        coolant_temp_c = row['engine_temp_c'] * 0.85 + random.uniform(-10, 10)
        
        # Transmission temperature
        transmission_temp_c = row['engine_temp_c'] * 0.8 + random.uniform(-15, 15)
        
        # Battery voltage (normal range 12-14.4V)
        battery_voltage = random.uniform(12.0, 14.4)
        
        # Engine load based on throttle position
        engine_load_percent = row['throttle_position_percent'] * 0.8 + random.uniform(-10, 10)
        engine_load_percent = max(0, min(100, engine_load_percent))
        
        # Other diagnostic data
        intake_air_temp_c = row['engine_temp_c'] * 0.6 + random.uniform(-20, 20)
        mass_air_flow_rate = random.uniform(2.0, 8.0)
        oxygen_sensor_voltage = random.uniform(0.1, 0.9)
        catalytic_converter_temp_c = row['engine_temp_c'] * 1.2 + random.uniform(-30, 30)
        
        # Tire pressures (degradation over time)
        base_pressure = 32  # PSI
        pressure_variance = random.uniform(-3, 3)
        tire_pressure_fl = base_pressure + pressure_variance
        tire_pressure_fr = base_pressure + pressure_variance
        tire_pressure_rl = base_pressure + pressure_variance
        tire_pressure_rr = base_pressure + pressure_variance
        
        # Fluid levels (decrease over time)
        brake_fluid_level = random.uniform(60, 100)
        windshield_washer_level = random.uniform(20, 100)
        
        record = {
            'timestamp': row['timestamp'],
            'vehicle_id': row['vehicle_id'],
            'engine_oil_temp_c': round(engine_oil_temp_c, 1),
            'coolant_temp_c': round(coolant_temp_c, 1),
            'transmission_temp_c': round(transmission_temp_c, 1),
            'battery_voltage': round(battery_voltage, 2),
            'engine_load_percent': round(engine_load_percent, 1),
            'intake_air_temp_c': round(intake_air_temp_c, 1),
            'mass_air_flow_rate': round(mass_air_flow_rate, 2),
            'oxygen_sensor_voltage': round(oxygen_sensor_voltage, 3),
            'catalytic_converter_temp_c': round(catalytic_converter_temp_c, 1),
            'tire_pressure_fl': round(tire_pressure_fl, 1),
            'tire_pressure_fr': round(tire_pressure_fr, 1),
            'tire_pressure_rl': round(tire_pressure_rl, 1),
            'tire_pressure_rr': round(tire_pressure_rr, 1),
            'brake_fluid_level': round(brake_fluid_level, 1),
            'windshield_washer_level': round(windshield_washer_level, 1)
        }
        data.append(record)
    
    return pd.DataFrame(data)

def generate_driving_behavior_data(core_df, vehicles):
    """Generate driving behavior data based on core sensor data"""
    data = []
    
    for _, row in core_df.iterrows():
        vehicle = next(v for v in vehicles if v['vehicle_id'] == row['vehicle_id'])
        
        # Calculate harsh events based on acceleration and driving style
        if vehicle['driving_style'] == 'aggressive':
            harsh_braking_count = random.randint(2, 8)
            harsh_acceleration_count = random.randint(3, 10)
            sharp_turn_count = random.randint(5, 15)
            speeding_incidents = random.randint(1, 5)
        elif vehicle['driving_style'] == 'eco':
            harsh_braking_count = random.randint(0, 2)
            harsh_acceleration_count = random.randint(0, 3)
            sharp_turn_count = random.randint(0, 5)
            speeding_incidents = random.randint(0, 1)
        else:  # moderate
            harsh_braking_count = random.randint(1, 4)
            harsh_acceleration_count = random.randint(1, 5)
            sharp_turn_count = random.randint(2, 8)
            speeding_incidents = random.randint(0, 2)
        
        # Trip statistics
        idle_time_minutes = random.randint(5, 30)
        avg_speed_trip = row['speed_kmh'] * random.uniform(0.7, 1.0)
        max_speed_trip = row['speed_kmh'] * random.uniform(1.1, 1.5)
        
        # Driving scores (0-100)
        if vehicle['driving_style'] == 'aggressive':
            driving_score = random.randint(40, 70)
            eco_driving_score = random.randint(20, 50)
            aggressive_driving_flag = 1
        elif vehicle['driving_style'] == 'eco':
            driving_score = random.randint(80, 95)
            eco_driving_score = random.randint(75, 95)
            aggressive_driving_flag = 0
        else:
            driving_score = random.randint(65, 85)
            eco_driving_score = random.randint(50, 75)
            aggressive_driving_flag = 0
        
        record = {
            'timestamp': row['timestamp'],
            'vehicle_id': row['vehicle_id'],
            'harsh_braking_count': harsh_braking_count,
            'harsh_acceleration_count': harsh_acceleration_count,
            'sharp_turn_count': sharp_turn_count,
            'speeding_incidents': speeding_incidents,
            'idle_time_minutes': idle_time_minutes,
            'avg_speed_trip': round(avg_speed_trip, 2),
            'max_speed_trip': round(max_speed_trip, 2),
            'driving_score': driving_score,
            'aggressive_driving_flag': aggressive_driving_flag,
            'eco_driving_score': eco_driving_score
        }
        data.append(record)
    
    return pd.DataFrame(data)

def generate_environmental_data(core_df, vehicles):
    """Generate environmental context data"""
    data = []
    
    for _, row in core_df.iterrows():
        vehicle = next(v for v in vehicles if v['vehicle_id'] == row['vehicle_id'])
        
        # Weather based on season and location
        timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
        month = timestamp.month
        
        if month in [12, 1, 2]:  # Winter
            weather_condition = random.choice(['snow', 'fog', 'clear'])
            temperature_outside_c = random.uniform(-10, 5)
        elif month in [6, 7, 8]:  # Summer
            weather_condition = random.choice(['clear', 'hot', 'rain'])
            temperature_outside_c = random.uniform(20, 35)
        else:  # Spring/Fall
            weather_condition = random.choice(['clear', 'rain', 'fog'])
            temperature_outside_c = random.uniform(5, 25)
        
        # Road and terrain based on vehicle profile
        road_type = random.choice(ROAD_TYPES)
        terrain_type = vehicle['primary_terrain']
        
        # Traffic density based on location and time
        hour = timestamp.hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            traffic_density = random.choice(['heavy', 'moderate'])
        else:
            traffic_density = random.choice(['light', 'moderate'])
        
        # Location type based on coordinates
        if abs(row['latitude'] - vehicle['base_lat']) < 0.02:
            location_type = 'urban'
        else:
            location_type = random.choice(LOCATION_TYPES)
        
        # Altitude and other environmental factors
        altitude_m = random.randint(0, 500)  # Sea level to moderate elevation
        humidity_percent = random.randint(30, 80)
        
        # Road surface condition
        if weather_condition in ['rain', 'snow']:
            road_surface_condition = random.choice(['wet', 'slippery'])
        else:
            road_surface_condition = random.choice(['dry', 'good'])
        
        record = {
            'timestamp': row['timestamp'],
            'vehicle_id': row['vehicle_id'],
            'weather_condition': weather_condition,
            'temperature_outside_c': round(temperature_outside_c, 1),
            'road_type': road_type,
            'terrain_type': terrain_type,
            'traffic_density': traffic_density,
            'location_type': location_type,
            'altitude_m': altitude_m,
            'humidity_percent': humidity_percent,
            'road_surface_condition': road_surface_condition
        }
        data.append(record)
    
    return pd.DataFrame(data)

def generate_maintenance_history(vehicles):
    """Generate maintenance history for vehicles"""
    data = []
    
    for vehicle in vehicles:
        # Generate 2-4 maintenance records per vehicle
        num_services = random.randint(2, 4)
        
        for i in range(num_services):
            service_date = START_DATE + timedelta(days=random.randint(30, 300))
            service_types = ['oil_change', 'tire_rotation', 'brake_inspection', 'general_maintenance', 'transmission_service']
            service_type = random.choice(service_types)
            
            mileage_at_service = vehicle['base_mileage'] + random.randint(1000, 10000)
            
            # Parts replaced based on service type
            if service_type == 'oil_change':
                parts_replaced = 'engine_oil,oil_filter'
                cost = random.randint(50, 100)
            elif service_type == 'tire_rotation':
                parts_replaced = 'none'
                cost = random.randint(30, 60)
            elif service_type == 'brake_inspection':
                parts_replaced = random.choice(['none', 'brake_pads', 'brake_fluid'])
                cost = random.randint(100, 300)
            else:
                parts_replaced = random.choice(['air_filter', 'spark_plugs', 'transmission_fluid'])
                cost = random.randint(150, 500)
            
            # Next service due dates
            next_service_due_km = mileage_at_service + random.randint(5000, 15000)
            oil_change_due_km = mileage_at_service + random.randint(3000, 8000)
            tire_rotation_due_km = mileage_at_service + random.randint(8000, 12000)
            brake_inspection_due_km = mileage_at_service + random.randint(15000, 25000)
            
            record = {
                'vehicle_id': vehicle['vehicle_id'],
                'service_date': service_date.strftime('%Y-%m-%d'),
                'service_type': service_type,
                'mileage_at_service': mileage_at_service,
                'parts_replaced': parts_replaced,
                'cost': cost,
                'next_service_due_km': next_service_due_km,
                'oil_change_due_km': oil_change_due_km,
                'tire_rotation_due_km': tire_rotation_due_km,
                'brake_inspection_due_km': brake_inspection_due_km
            }
            data.append(record)
    
    return pd.DataFrame(data)

# Generate all datasets
print("Generating vehicle profiles...")
vehicles = generate_vehicle_profiles()

print("Generating core sensor data...")
core_sensor_df = generate_core_sensor_data(vehicles)

print("Generating vehicle health data...")
vehicle_health_df = generate_vehicle_health_data(core_sensor_df, vehicles)

print("Generating driving behavior data...")
driving_behavior_df = generate_driving_behavior_data(core_sensor_df, vehicles)

print("Generating environmental data...")
environmental_df = generate_environmental_data(core_sensor_df, vehicles)

print("Generating maintenance history...")
maintenance_history_df = generate_maintenance_history(vehicles)

# Save datasets
print("Saving datasets...")
core_sensor_df.to_csv('core_sensor_data.csv', index=False)
vehicle_health_df.to_csv('vehicle_health_data.csv', index=False)
driving_behavior_df.to_csv('driving_behavior_data.csv', index=False)
environmental_df.to_csv('environmental_data.csv', index=False)
maintenance_history_df.to_csv('maintenance_history.csv', index=False)

print(f"Generated datasets:")
print(f"- Core Sensor Data: {len(core_sensor_df)} records")
print(f"- Vehicle Health Data: {len(vehicle_health_df)} records")
print(f"- Driving Behavior Data: {len(driving_behavior_df)} records")
print(f"- Environmental Data: {len(environmental_df)} records")
print(f"- Maintenance History: {len(maintenance_history_df)} records")
print(f"Total vehicles: {NUM_VEHICLES}")
