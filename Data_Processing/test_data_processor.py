import json
import logging
import time
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ProcessedVehicleData:
    """Standardized processed vehicle data structure"""
    vehicle_id: str
    timestamp: str
    processing_time: str
    
    # Core metrics
    speed_kmh: float
    engine_temp_c: float
    fuel_level_percent: float
    mileage_km: int
    
    # Health scores (computed)
    engine_health_score: float
    brake_health_score: float
    tire_health_score: float
    overall_health_score: float
    
    # Behavior metrics (computed)
    driving_aggressiveness: float
    eco_driving_score: float
    maintenance_urgency: float
    
    # Context data
    location_lat: float
    location_lon: float
    weather_condition: str
    terrain_type: str
    
    # Flags
    maintenance_required: bool
    ad_targeting_eligible: bool
    anomaly_detected: bool

class DataProcessingServiceTest:
    """
    Test version of Data Processing Service that reads from JSON files
    instead of Kafka topics and demonstrates the three-branch routing
    """
    
    def __init__(self, config_file='config.json'):
        """Initialize the test Data Processing Service"""
        self.config = self.load_config(config_file)
        self.db_connection = None
        
        # Output directories for the three branches
        self.output_dirs = {
            'database': 'output/database',
            'ml_pipeline': 'output/ml_pipeline', 
            'ad_engine': 'output/ad_engine'
        }
        
        # Create output directories
        for output_dir in self.output_dirs.values():
            os.makedirs(output_dir, exist_ok=True)
        
        # Data processing components
        self.health_analyzer = HealthAnalyzer()
        self.behavior_analyzer = BehaviorAnalyzer() 
        self.anomaly_detector = AnomalyDetector()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DataProcessor_Test')
        
        # Statistics
        self.stats = {
            'messages_processed': 0,
            'records_stored': 0,
            'ml_predictions_sent': 0,
            'ad_recommendations_sent': 0,
            'anomalies_detected': 0,
            'errors_encountered': 0
        }
    
    def load_config(self, config_file):
        """Load configuration"""
        default_config = {
            "processing": {
                "health_score_threshold": 0.7,
                "maintenance_threshold": 0.3
            },
            "database": {
                "path": "test_vehicle_data.db"
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        return default_config
    
    def initialize_database(self):
        """Initialize local database for data storage"""
        db_path = self.config['database']['path']
        
        try:
            self.db_connection = sqlite3.connect(db_path)
            cursor = self.db_connection.cursor()
            
            # Create processed vehicle data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_vehicle_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT,
                    timestamp TEXT,
                    speed_kmh REAL,
                    engine_temp_c REAL,
                    engine_health_score REAL,
                    brake_health_score REAL,
                    tire_health_score REAL,
                    overall_health_score REAL,
                    driving_aggressiveness REAL,
                    eco_driving_score REAL,
                    maintenance_urgency REAL,
                    maintenance_required BOOLEAN,
                    anomaly_detected BOOLEAN,
                    location_lat REAL,
                    location_lon REAL,
                    weather_condition TEXT,
                    terrain_type TEXT,
                    processing_time TEXT
                )
            ''')
            
            # Create health alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    timestamp TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            self.db_connection.commit()
            self.logger.info("Test database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            return False
    
    def load_test_data(self, input_dir="../Telematics_ECU/output"):
        """Load test data from Telematics ECU output files"""
        test_data = {
            'sensor-data-topic': [],
            'health-data-topic': [],
            'behavior-topic': [],
            'environment-topic': []
        }
        
        topic_files = {
            'sensor-data-topic': 'sensor-data-topic_output.jsonl',
            'health-data-topic': 'health-data-topic_output.jsonl',
            'behavior-topic': 'behavior-topic_output.jsonl',
            'environment-topic': 'environment-topic_output.jsonl'
        }
        
        for topic, filename in topic_files.items():
            file_path = os.path.join(input_dir, filename)
            
            if not os.path.exists(file_path):
                self.logger.warning(f"Test data file not found: {file_path}")
                continue
            
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line.strip())
                            test_data[topic].append(data)
                
                self.logger.info(f"Loaded {len(test_data[topic])} records from {filename}")
                
            except Exception as e:
                self.logger.error(f"Error loading {filename}: {e}")
                return None
        
        return test_data
    
    def group_messages_by_vehicle_time(self, test_data):
        """Group messages by vehicle and timestamp"""
        grouped_data = {}
        
        for topic, messages in test_data.items():
            for message in messages:
                vehicle_id = message.get('vehicle_id')
                timestamp = message.get('timestamp')
                dataset_type = message.get('dataset_type')
                
                if not vehicle_id or not timestamp:
                    continue
                
                key = f"{vehicle_id}_{timestamp}"
                if key not in grouped_data:
                    grouped_data[key] = {}
                
                grouped_data[key][dataset_type] = message
        
        self.logger.info(f"Grouped {len(grouped_data)} unique vehicle-timestamp combinations")
        return grouped_data
    
    def create_processed_record(self, data_group: Dict) -> Optional[ProcessedVehicleData]:
        """Create a processed record from grouped sensor data"""
        try:
            # Extract data from different types
            core_data = data_group.get('core_sensor_data', {})
            health_data = data_group.get('vehicle_health_data', {})
            behavior_data = data_group.get('driving_behavior_data', {})
            env_data = data_group.get('environmental_data', {})
            
            if not core_data:
                return None
            
            vehicle_id = core_data.get('vehicle_id')
            timestamp = core_data.get('timestamp')
            
            if not vehicle_id or not timestamp:
                return None
            
            # Calculate health scores
            engine_health = self.health_analyzer.calculate_engine_health(core_data, health_data)
            brake_health = self.health_analyzer.calculate_brake_health(core_data, behavior_data)
            tire_health = self.health_analyzer.calculate_tire_health(health_data)
            overall_health = (engine_health + brake_health + tire_health) / 3
            
            # Calculate behavior metrics
            aggressiveness = self.behavior_analyzer.calculate_aggressiveness(behavior_data)
            eco_score = behavior_data.get('eco_driving_score', 50) / 100.0
            
            # Calculate maintenance urgency
            maintenance_urgency = self.calculate_maintenance_urgency(
                engine_health, brake_health, tire_health, core_data.get('mileage_km', 0)
            )
            
            # Detect anomalies
            anomaly_detected = self.anomaly_detector.detect_anomaly(core_data, health_data)
            
            if anomaly_detected:
                self.stats['anomalies_detected'] += 1
            
            # Create processed record
            processed_record = ProcessedVehicleData(
                vehicle_id=vehicle_id,
                timestamp=timestamp,
                processing_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                speed_kmh=core_data.get('speed_kmh', 0),
                engine_temp_c=core_data.get('engine_temp_c', 0),
                fuel_level_percent=core_data.get('fuel_level_percent', 0),
                mileage_km=core_data.get('mileage_km', 0),
                engine_health_score=engine_health,
                brake_health_score=brake_health,
                tire_health_score=tire_health,
                overall_health_score=overall_health,
                driving_aggressiveness=aggressiveness,
                eco_driving_score=eco_score,
                maintenance_urgency=maintenance_urgency,
                location_lat=core_data.get('latitude', 0),
                location_lon=core_data.get('longitude', 0),
                weather_condition=env_data.get('weather_condition', 'unknown'),
                terrain_type=env_data.get('terrain_type', 'unknown'),
                maintenance_required=maintenance_urgency > self.config['processing']['maintenance_threshold'],
                ad_targeting_eligible=overall_health > self.config['processing']['health_score_threshold'],
                anomaly_detected=anomaly_detected
            )
            
            return processed_record
            
        except Exception as e:
            self.logger.error(f"Error creating processed record: {e}")
            return None
    
    def calculate_maintenance_urgency(self, engine_health: float, brake_health: float, 
                                    tire_health: float, mileage: int) -> float:
        """Calculate maintenance urgency score (0-1, higher = more urgent)"""
        health_weight = 0.6
        mileage_weight = 0.4
        
        health_component = 1 - ((engine_health + brake_health + tire_health) / 3)
        mileage_factor = min(mileage / 200000, 1.0)
        
        urgency = (health_component * health_weight) + (mileage_factor * mileage_weight)
        return min(max(urgency, 0), 1)
    
    def store_to_database(self, processed_data: List[ProcessedVehicleData]):
        """Branch 1: Store processed data to local database"""
        if not self.db_connection or not processed_data:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            for record in processed_data:
                cursor.execute('''
                    INSERT INTO processed_vehicle_data 
                    (vehicle_id, timestamp, speed_kmh, engine_temp_c, engine_health_score,
                     brake_health_score, tire_health_score, overall_health_score,
                     driving_aggressiveness, eco_driving_score, maintenance_urgency,
                     maintenance_required, anomaly_detected, location_lat, location_lon,
                     weather_condition, terrain_type, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.vehicle_id, record.timestamp, record.speed_kmh, record.engine_temp_c,
                    record.engine_health_score, record.brake_health_score, record.tire_health_score,
                    record.overall_health_score, record.driving_aggressiveness, record.eco_driving_score,
                    record.maintenance_urgency, record.maintenance_required, record.anomaly_detected,
                    record.location_lat, record.location_lon, record.weather_condition,
                    record.terrain_type, record.processing_time
                ))
                
                # Create health alerts if needed
                if record.maintenance_required:
                    cursor.execute('''
                        INSERT INTO health_alerts (vehicle_id, alert_type, severity, message, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        record.vehicle_id, 'maintenance', 'high',
                        f'Maintenance required - urgency score: {record.maintenance_urgency:.2f}',
                        record.timestamp
                    ))
                
                if record.anomaly_detected:
                    cursor.execute('''
                        INSERT INTO health_alerts (vehicle_id, alert_type, severity, message, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        record.vehicle_id, 'anomaly', 'medium',
                        'Anomaly detected in vehicle data',
                        record.timestamp
                    ))
            
            self.db_connection.commit()
            self.stats['records_stored'] += len(processed_data)
            
            # Also save to file for verification
            output_file = os.path.join(self.output_dirs['database'], 'stored_records.jsonl')
            with open(output_file, 'a') as f:
                for record in processed_data:
                    f.write(json.dumps(asdict(record)) + '\n')
            
            self.logger.info(f"[BRANCH 1 - DATABASE] Stored {len(processed_data)} records")
            
        except Exception as e:
            self.logger.error(f"Error storing to database: {e}")
            self.stats['errors_encountered'] += 1
    
    def send_to_ml_pipeline(self, processed_data: List[ProcessedVehicleData]):
        """Branch 2: Send processed data to ML pipeline"""
        if not processed_data:
            return
        
        try:
            # Filter records that need ML processing
            ml_records = [record for record in processed_data 
                         if record.maintenance_required or record.anomaly_detected]
            
            if not ml_records:
                return
            
            # Save to ML pipeline output file
            output_file = os.path.join(self.output_dirs['ml_pipeline'], 'ml_input_data.jsonl')
            
            with open(output_file, 'a') as f:
                for record in ml_records:
                    ml_payload = {
                        'vehicle_id': record.vehicle_id,
                        'timestamp': record.timestamp,
                        'health_scores': {
                            'engine': record.engine_health_score,
                            'brake': record.brake_health_score,
                            'tire': record.tire_health_score,
                            'overall': record.overall_health_score
                        },
                        'maintenance_urgency': record.maintenance_urgency,
                        'anomaly_detected': record.anomaly_detected,
                        'vehicle_metrics': {
                            'speed': record.speed_kmh,
                            'engine_temp': record.engine_temp_c,
                            'mileage': record.mileage_km,
                            'fuel_level': record.fuel_level_percent
                        },
                        'context': {
                            'location': [record.location_lat, record.location_lon],
                            'weather': record.weather_condition,
                            'terrain': record.terrain_type
                        }
                    }
                    
                    f.write(json.dumps(ml_payload) + '\n')
            
            self.stats['ml_predictions_sent'] += len(ml_records)
            self.logger.info(f"[BRANCH 2 - ML PIPELINE] Sent {len(ml_records)} records for prediction")
            
        except Exception as e:
            self.logger.error(f"Error sending to ML pipeline: {e}")
            self.stats['errors_encountered'] += 1
    
    def send_to_ad_engine(self, processed_data: List[ProcessedVehicleData]):
        """Branch 3: Send user behavior data to Ad Engine"""
        if not processed_data:
            return
        
        try:
            # Filter records eligible for ad targeting
            ad_records = [record for record in processed_data 
                         if record.ad_targeting_eligible]
            
            if not ad_records:
                return
            
            # Save to Ad Engine output file
            output_file = os.path.join(self.output_dirs['ad_engine'], 'ad_input_data.jsonl')
            
            with open(output_file, 'a') as f:
                for record in ad_records:
                    ad_payload = {
                        'vehicle_id': record.vehicle_id,
                        'timestamp': record.timestamp,
                        'behavior_profile': {
                            'driving_aggressiveness': record.driving_aggressiveness,
                            'eco_driving_score': record.eco_driving_score,
                            'maintenance_needs': record.maintenance_required
                        },
                        'context': {
                            'location': [record.location_lat, record.location_lon],
                            'weather': record.weather_condition,
                            'terrain': record.terrain_type,
                            'speed': record.speed_kmh
                        },
                        'vehicle_profile': {
                            'mileage': record.mileage_km,
                            'health_score': record.overall_health_score
                        }
                    }
                    
                    f.write(json.dumps(ad_payload) + '\n')
            
            self.stats['ad_recommendations_sent'] += len(ad_records)
            self.logger.info(f"[BRANCH 3 - AD ENGINE] Sent {len(ad_records)} records for recommendations")
            
        except Exception as e:
            self.logger.error(f"Error sending to Ad Engine: {e}")
            self.stats['errors_encountered'] += 1
    
    def run_test_processing(self):
        """Run the test data processing demonstration"""
        self.logger.info("Starting Data Processing Service Test")
        
        # Initialize database
        if not self.initialize_database():
            return False
        
        # Load test data from Telematics ECU output
        test_data = self.load_test_data()
        if not test_data:
            self.logger.error("No test data found")
            return False
        
        # Clear output files
        for output_dir in self.output_dirs.values():
            for filename in os.listdir(output_dir):
                if filename.endswith(('.jsonl', '.json')):
                    os.remove(os.path.join(output_dir, filename))
        
        # Group messages by vehicle and timestamp
        grouped_data = self.group_messages_by_vehicle_time(test_data)
        
        # Process each group
        processed_records = []
        
        for key, data_group in grouped_data.items():
            processed_record = self.create_processed_record(data_group)
            if processed_record:
                processed_records.append(processed_record)
        
        self.stats['messages_processed'] = len(grouped_data)
        
        if processed_records:
            self.logger.info(f"Created {len(processed_records)} processed records")
            
            # Route to three branches
            self.store_to_database(processed_records)           # Branch 1
            self.send_to_ml_pipeline(processed_records)         # Branch 2  
            self.send_to_ad_engine(processed_records)           # Branch 3
            
            # Print final statistics
            self.logger.info("=== PROCESSING COMPLETE ===")
            self.logger.info("Three-branch routing results:")
            for key, value in self.stats.items():
                self.logger.info(f"  {key}: {value}")
            
            # Show output files
            self.logger.info("Generated output files:")
            for branch, output_dir in self.output_dirs.items():
                files = [f for f in os.listdir(output_dir) if f.endswith('.jsonl')]
                for file in files:
                    file_path = os.path.join(output_dir, file)
                    with open(file_path, 'r') as f:
                        line_count = len(f.readlines())
                    self.logger.info(f"  {branch}/{file}: {line_count} records")
        
        # Close database
        if self.db_connection:
            self.db_connection.close()
        
        return True

# Helper classes (same as main service)
class HealthAnalyzer:
    def calculate_engine_health(self, core_data: Dict, health_data: Dict) -> float:
        engine_temp = core_data.get('engine_temp_c', 90)
        oil_temp = health_data.get('engine_oil_temp_c', engine_temp * 0.9)
        engine_load = health_data.get('engine_load_percent', 50)
        
        temp_score = max(0, 1 - max(0, engine_temp - 95) / 20)
        oil_score = max(0, 1 - max(0, oil_temp - 85) / 25)
        load_score = max(0, 1 - max(0, engine_load - 80) / 20)
        
        return (temp_score + oil_score + load_score) / 3
    
    def calculate_brake_health(self, core_data: Dict, behavior_data: Dict) -> float:
        brake_pressure = core_data.get('brake_pressure_psi', 0)
        harsh_braking = behavior_data.get('harsh_braking_count', 0)
        
        pressure_score = min(1, brake_pressure / 50) if brake_pressure > 0 else 1
        braking_score = max(0, 1 - harsh_braking / 10)
        
        return (pressure_score + braking_score) / 2
    
    def calculate_tire_health(self, health_data: Dict) -> float:
        pressures = [
            health_data.get('tire_pressure_fl', 32),
            health_data.get('tire_pressure_fr', 32),
            health_data.get('tire_pressure_rl', 32),
            health_data.get('tire_pressure_rr', 32)
        ]
        
        avg_pressure = sum(pressures) / len(pressures)
        pressure_variance = sum((p - avg_pressure) ** 2 for p in pressures) / len(pressures)
        
        pressure_score = max(0, 1 - abs(avg_pressure - 32) / 10)
        variance_score = max(0, 1 - pressure_variance / 4)
        
        return (pressure_score + variance_score) / 2

class BehaviorAnalyzer:
    def calculate_aggressiveness(self, behavior_data: Dict) -> float:
        harsh_braking = behavior_data.get('harsh_braking_count', 0)
        harsh_acceleration = behavior_data.get('harsh_acceleration_count', 0)
        speeding = behavior_data.get('speeding_incidents', 0)
        
        aggressiveness = (harsh_braking * 0.4 + harsh_acceleration * 0.4 + speeding * 0.2) / 10
        return min(max(aggressiveness, 0), 1)

class AnomalyDetector:
    def detect_anomaly(self, core_data: Dict, health_data: Dict) -> bool:
        engine_temp = core_data.get('engine_temp_c', 0)
        speed = core_data.get('speed_kmh', 0)
        fuel_level = core_data.get('fuel_level_percent', 50)
        
        if engine_temp > 120:
            return True
        if speed > 150:
            return True
        if fuel_level < 5:
            return True
        if fuel_level > 105:
            return True
        
        return False

if __name__ == "__main__":
    # Run test processing service
    service = DataProcessingServiceTest()
    
    try:
        print("Starting Data Processing Service Test...")
        print("This will demonstrate the three-branch routing:")
        print("  1. Database Storage")
        print("  2. ML Pipeline") 
        print("  3. Ad Engine")
        print()
        
        success = service.run_test_processing()
        
        if success:
            print("\nTest completed successfully!")
            print("Check the 'output' directory for generated files:")
            print("  - output/database/: Database storage branch")
            print("  - output/ml_pipeline/: ML pipeline branch")
            print("  - output/ad_engine/: Ad engine branch")
        else:
            print("Test failed!")
            exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
