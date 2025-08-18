import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import sqlite3
import os
import requests
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

class DataProcessingService:
    """
    Central data processing service that consumes from Kafka topics,
    processes and enriches vehicle data, then routes to appropriate services
    """
    
    def __init__(self, config_file='config.json'):
        """Initialize the Data Processing Service"""
        self.config = self.load_config(config_file)
        self.consumer = None
        self.producer = None
        self.db_connection = None
        self.running = False
        self.processing_threads = []
        
        # Data processing components
        self.data_enricher = DataEnricher()
        self.health_analyzer = HealthAnalyzer()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', {}).get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DataProcessor')
        
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
            "kafka": {
                "bootstrap_servers": ["localhost:9092"],
                "consumer_topics": [
                    "sensor-data-topic",
                    "health-data-topic", 
                    "behavior-topic",
                    "environment-topic"
                ],
                "producer_topics": {
                    "ml_pipeline": "ml-input-topic",
                    "ad_engine": "ad-input-topic",
                    "maintenance_alerts": "maintenance-topic"
                },
                "consumer_group": "data-processor-group"
            },
            "database": {
                "type": "sqlite",
                "path": "vehicle_data.db"
            },
            "processing": {
                "batch_size": 10,
                "processing_interval": 1.0,
                "enable_anomaly_detection": True,
                "health_score_threshold": 0.7,
                "maintenance_threshold": 0.3
            },
            "apis": {
                "ml_service_url": "http://localhost:5001",
                "ad_service_url": "http://localhost:5002",
                "maintenance_service_url": "http://localhost:5003"
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
            self.db_connection = sqlite3.connect(db_path, check_same_thread=False)
            
            # Create tables
            cursor = self.db_connection.cursor()
            
            # Raw sensor data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS raw_sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT,
                    timestamp TEXT,
                    data_type TEXT,
                    raw_data TEXT,
                    created_at TEXT
                )
            ''')
            
            # Processed vehicle data table
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
            
            # Health alerts table
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
            self.logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            return False
    
    def connect_kafka(self):
        """Initialize Kafka consumer and producer"""
        try:
            # Initialize consumer
            self.consumer = KafkaConsumer(
                *self.config['kafka']['consumer_topics'],
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                group_id=self.config['kafka']['consumer_group'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
            
            # Initialize producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all'
            )
            
            self.logger.info("Connected to Kafka successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    def process_sensor_data(self, message_batch: List[Dict]) -> List[ProcessedVehicleData]:
        """Process a batch of sensor messages"""
        processed_data = []
        
        # Group messages by vehicle and timestamp
        vehicle_data_groups = {}
        
        for message in message_batch:
            vehicle_id = message.get('vehicle_id')
            timestamp = message.get('timestamp')
            dataset_type = message.get('dataset_type')
            
            key = f"{vehicle_id}_{timestamp}"
            if key not in vehicle_data_groups:
                vehicle_data_groups[key] = {}
            
            vehicle_data_groups[key][dataset_type] = message
        
        # Process each vehicle's data at each timestamp
        for key, data_group in vehicle_data_groups.items():
            try:
                processed_record = self.create_processed_record(data_group)
                if processed_record:
                    processed_data.append(processed_record)
            except Exception as e:
                self.logger.error(f"Error processing data group {key}: {e}")
                self.stats['errors_encountered'] += 1
        
        return processed_data
    
    def create_processed_record(self, data_group: Dict) -> Optional[ProcessedVehicleData]:
        """Create a processed record from grouped sensor data"""
        try:
            # Extract core data (prioritize core_sensor_data)
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
        # Weight factors
        health_weight = 0.6
        mileage_weight = 0.4
        
        # Health component (inverted - lower health = higher urgency)
        health_component = 1 - ((engine_health + brake_health + tire_health) / 3)
        
        # Mileage component (higher mileage = higher urgency)
        mileage_factor = min(mileage / 200000, 1.0)  # Cap at 200k km
        
        urgency = (health_component * health_weight) + (mileage_factor * mileage_weight)
        return min(max(urgency, 0), 1)  # Clamp between 0 and 1
    
    def store_to_database(self, processed_data: List[ProcessedVehicleData]):
        """Store processed data to local database"""
        if not self.db_connection or not processed_data:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            for record in processed_data:
                # Store processed data
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
            self.logger.debug(f"Stored {len(processed_data)} records to database")
            
        except Exception as e:
            self.logger.error(f"Error storing to database: {e}")
            self.stats['errors_encountered'] += 1
    
    def send_to_ml_pipeline(self, processed_data: List[ProcessedVehicleData]):
        """Send processed data to ML pipeline"""
        if not processed_data:
            return
        
        try:
            # Filter records that need ML processing
            ml_records = [record for record in processed_data 
                         if record.maintenance_required or record.anomaly_detected]
            
            if not ml_records:
                return
            
            # Send to Kafka topic for ML pipeline
            topic = self.config['kafka']['producer_topics']['ml_pipeline']
            
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
                
                self.producer.send(topic, ml_payload)
            
            self.stats['ml_predictions_sent'] += len(ml_records)
            self.logger.debug(f"Sent {len(ml_records)} records to ML pipeline")
            
        except Exception as e:
            self.logger.error(f"Error sending to ML pipeline: {e}")
            self.stats['errors_encountered'] += 1
    
    def send_to_ad_engine(self, processed_data: List[ProcessedVehicleData]):
        """Send user behavior data to Ad Engine"""
        if not processed_data:
            return
        
        try:
            # Filter records eligible for ad targeting
            ad_records = [record for record in processed_data 
                         if record.ad_targeting_eligible]
            
            if not ad_records:
                return
            
            topic = self.config['kafka']['producer_topics']['ad_engine']
            
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
                
                self.producer.send(topic, ad_payload)
            
            self.stats['ad_recommendations_sent'] += len(ad_records)
            self.logger.debug(f"Sent {len(ad_records)} records to Ad Engine")
            
        except Exception as e:
            self.logger.error(f"Error sending to Ad Engine: {e}")
            self.stats['errors_encountered'] += 1
    
    def process_message_batch(self):
        """Main processing loop for consuming and processing messages"""
        message_batch = []
        batch_size = self.config['processing']['batch_size']
        processing_interval = self.config['processing']['processing_interval']
        
        while self.running:
            try:
                # Collect messages into batches
                message_poll = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_poll.items():
                    for message in messages:
                        message_batch.append(message.value)
                        
                        if len(message_batch) >= batch_size:
                            self.process_batch(message_batch)
                            message_batch = []
                
                # Process remaining messages if batch timeout reached
                if message_batch:
                    self.process_batch(message_batch)
                    message_batch = []
                
                time.sleep(processing_interval)
                
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
                self.stats['errors_encountered'] += 1
                time.sleep(5)  # Wait before retrying
    
    def process_batch(self, message_batch: List[Dict]):
        """Process a batch of messages"""
        if not message_batch:
            return
        
        try:
            # Process sensor data
            processed_data = self.process_sensor_data(message_batch)
            
            if processed_data:
                # Route to three branches
                self.store_to_database(processed_data)           # Branch 1: Database
                self.send_to_ml_pipeline(processed_data)         # Branch 2: ML Pipeline  
                self.send_to_ad_engine(processed_data)           # Branch 3: Ad Engine
                
                self.stats['messages_processed'] += len(message_batch)
                self.logger.info(f"Processed batch of {len(message_batch)} messages, "
                               f"created {len(processed_data)} processed records")
            
        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")
            self.stats['errors_encountered'] += 1
    
    def start_service(self):
        """Start the Data Processing Service"""
        self.logger.info("Starting Data Processing Service")
        
        # Initialize components
        if not self.initialize_database():
            return False
        
        if not self.connect_kafka():
            return False
        
        self.running = True
        
        # Start processing thread
        processing_thread = threading.Thread(target=self.process_message_batch)
        processing_thread.start()
        self.processing_threads.append(processing_thread)
        
        self.logger.info("Data Processing Service started successfully")
        return True
    
    def stop_service(self):
        """Stop the Data Processing Service"""
        self.logger.info("Stopping Data Processing Service")
        self.running = False
        
        # Wait for processing threads to complete
        for thread in self.processing_threads:
            thread.join(timeout=5)
        
        # Close connections
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()
        if self.db_connection:
            self.db_connection.close()
        
        # Print final statistics
        self.logger.info("=== PROCESSING STATISTICS ===")
        for key, value in self.stats.items():
            self.logger.info(f"{key}: {value}")
        
        self.logger.info("Data Processing Service stopped")
    
    def get_service_status(self):
        """Get current service status"""
        return {
            'running': self.running,
            'kafka_connected': self.consumer is not None and self.producer is not None,
            'database_connected': self.db_connection is not None,
            'active_threads': len([t for t in self.processing_threads if t.is_alive()]),
            'statistics': self.stats
        }

# Data processing helper classes

class DataEnricher:
    """Enriches raw sensor data with additional context"""
    
    def enrich_location_data(self, lat: float, lon: float) -> Dict:
        """Add location-based enrichment"""
        # Simple location categorization
        if 40.0 <= lat <= 42.0 and -75.0 <= lon <= -73.0:
            return {'region': 'northeast', 'urban_area': True}
        else:
            return {'region': 'unknown', 'urban_area': False}

class HealthAnalyzer:
    """Analyzes vehicle health metrics"""
    
    def calculate_engine_health(self, core_data: Dict, health_data: Dict) -> float:
        """Calculate engine health score (0-1)"""
        engine_temp = core_data.get('engine_temp_c', 90)
        oil_temp = health_data.get('engine_oil_temp_c', engine_temp * 0.9)
        engine_load = health_data.get('engine_load_percent', 50)
        
        # Normalize factors
        temp_score = max(0, 1 - max(0, engine_temp - 95) / 20)  # Penalty for high temp
        oil_score = max(0, 1 - max(0, oil_temp - 85) / 25)
        load_score = max(0, 1 - max(0, engine_load - 80) / 20)  # Penalty for high load
        
        return (temp_score + oil_score + load_score) / 3
    
    def calculate_brake_health(self, core_data: Dict, behavior_data: Dict) -> float:
        """Calculate brake health score (0-1)"""
        brake_pressure = core_data.get('brake_pressure_psi', 0)
        harsh_braking = behavior_data.get('harsh_braking_count', 0)
        
        # Normalize factors
        pressure_score = min(1, brake_pressure / 50) if brake_pressure > 0 else 1
        braking_score = max(0, 1 - harsh_braking / 10)  # Penalty for harsh braking
        
        return (pressure_score + braking_score) / 2
    
    def calculate_tire_health(self, health_data: Dict) -> float:
        """Calculate tire health score (0-1)"""
        pressures = [
            health_data.get('tire_pressure_fl', 32),
            health_data.get('tire_pressure_fr', 32),
            health_data.get('tire_pressure_rl', 32),
            health_data.get('tire_pressure_rr', 32)
        ]
        
        # Calculate average pressure and variance
        avg_pressure = sum(pressures) / len(pressures)
        pressure_variance = sum((p - avg_pressure) ** 2 for p in pressures) / len(pressures)
        
        # Score based on optimal pressure (32 PSI) and low variance
        pressure_score = max(0, 1 - abs(avg_pressure - 32) / 10)
        variance_score = max(0, 1 - pressure_variance / 4)
        
        return (pressure_score + variance_score) / 2

class BehaviorAnalyzer:
    """Analyzes driving behavior patterns"""
    
    def calculate_aggressiveness(self, behavior_data: Dict) -> float:
        """Calculate driving aggressiveness score (0-1)"""
        harsh_braking = behavior_data.get('harsh_braking_count', 0)
        harsh_acceleration = behavior_data.get('harsh_acceleration_count', 0)
        speeding = behavior_data.get('speeding_incidents', 0)
        
        # Weighted aggressiveness score
        aggressiveness = (harsh_braking * 0.4 + harsh_acceleration * 0.4 + speeding * 0.2) / 10
        return min(max(aggressiveness, 0), 1)

class AnomalyDetector:
    """Detects anomalies in vehicle data"""
    
    def detect_anomaly(self, core_data: Dict, health_data: Dict) -> bool:
        """Simple anomaly detection based on thresholds"""
        # Check for extreme values
        engine_temp = core_data.get('engine_temp_c', 0)
        speed = core_data.get('speed_kmh', 0)
        fuel_level = core_data.get('fuel_level_percent', 50)
        
        # Anomaly conditions
        if engine_temp > 120:  # Overheating
            return True
        if speed > 150:  # Excessive speed
            return True
        if fuel_level < 5:  # Very low fuel
            return True
        if fuel_level > 105:  # Sensor error (impossible fuel level)
            return True
        
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Processing Service')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--duration', type=int, help='Run duration in seconds')
    
    args = parser.parse_args()
    
    # Create and start service
    service = DataProcessingService(args.config)
    
    try:
        success = service.start_service()
        
        if success:
            print("Data Processing Service started successfully")
            print("Processing Kafka messages and routing to:")
            print("  1. Local Database (storage)")
            print("  2. ML Pipeline (predictions)")
            print("  3. Ad Engine (recommendations)")
            print("Press Ctrl+C to stop...")
            
            if args.duration:
                time.sleep(args.duration)
                service.stop_service()
            else:
                # Wait for keyboard interrupt
                while service.running:
                    time.sleep(1)
        else:
            print("Failed to start Data Processing Service")
            exit(1)
            
    except KeyboardInterrupt:
        print("\nStopping service...")
        service.stop_service()
    except Exception as e:
        print(f"Error: {e}")
        service.stop_service()
        exit(1)
