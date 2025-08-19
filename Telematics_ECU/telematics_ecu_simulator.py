import pandas as pd
import json
import time
import threading
from datetime import datetime, timedelta
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging
import os
import sys

class TelematicsECUSimulator:
    """
    Telematics ECU Simulator that reads vehicle sensor data from CSV files
    and streams it to Kafka topics in real-time simulation
    """
    
    def __init__(self, config_file='config.json'):
        """Initialize the Telematics ECU Simulator"""
        self.config = self.load_config(config_file)
        self.producer = None
        self.datasets = {}
        self.running = False
        self.threads = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TelematicsECU')
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
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
                "core_sensor_data": "core_sensor_data.csv",
                "vehicle_health_data": "vehicle_health_data.csv",
                "driving_behavior_data": "driving_behavior_data.csv",
                "environmental_data": "environmental_data.csv"
            },
            "simulation": {
                "speed_multiplier": 1,  # 1 = real-time, 10 = 10x faster
                "replay_interval_seconds": 5,  # Send data every 5 seconds
                "batch_size": 1  # Number of records to send at once
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Could not load config file {config_file}: {e}")
                self.logger.info("Using default configuration")
        
        return default_config
    
    def connect_kafka(self):
        """Initialize Kafka producer connection"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            self.logger.info("Connected to Kafka successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    def load_datasets(self):
        """Load all CSV datasets into memory"""
        dataset_path = os.path.dirname(os.path.abspath(__file__))
        
        for dataset_name, filename in self.config['datasets'].items():
            file_path = os.path.join(dataset_path, filename)
            
            if not os.path.exists(file_path):
                self.logger.error(f"Dataset file not found: {file_path}")
                return False
            
            try:
                df = pd.read_csv(file_path)
                # Convert timestamp to datetime
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    # Sort by timestamp and vehicle_id
                    df = df.sort_values(['vehicle_id', 'timestamp'])
                
                self.datasets[dataset_name] = df
                self.logger.info(f"Loaded {len(df)} records from {filename}")
                
            except Exception as e:
                self.logger.error(f"Failed to load dataset {filename}: {e}")
                return False
        
        return True
    
    def preprocess_data(self, record, dataset_type):
        """Preprocess data record before sending to Kafka"""
        # Convert pandas timestamp to string
        if 'timestamp' in record and pd.notna(record['timestamp']):
            record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Add metadata
        record['dataset_type'] = dataset_type
        record['simulation_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Handle NaN values
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
        
        return record
    
    def send_to_kafka(self, topic, data, vehicle_id):
        """Send data to Kafka topic"""
        try:
            future = self.producer.send(
                topic,
                key=vehicle_id,
                value=data
            )
            
            # Wait for message to be sent (optional, for reliability)
            record_metadata = future.get(timeout=10)
            self.logger.debug(f"Sent to {topic}: partition {record_metadata.partition}, offset {record_metadata.offset}")
            return True
            
        except KafkaError as e:
            self.logger.error(f"Failed to send message to {topic}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending to {topic}: {e}")
            return False
    
    def simulate_real_time_streaming(self):
        """Simulate real-time data streaming from all datasets"""
        self.logger.info("Starting real-time data streaming simulation")
        
        # Get all unique timestamps across datasets
        all_timestamps = set()
        for df in self.datasets.values():
            if 'timestamp' in df.columns:
                all_timestamps.update(df['timestamp'].unique())
        
        sorted_timestamps = sorted(all_timestamps)
        
        start_time = datetime.now()
        interval = self.config['simulation']['replay_interval_seconds']
        
        for i, timestamp in enumerate(sorted_timestamps):
            if not self.running:
                break
            
            self.logger.info(f"Processing timestamp {timestamp} ({i+1}/{len(sorted_timestamps)})")
            
            # Send data for each dataset at this timestamp
            for dataset_name, df in self.datasets.items():
                if 'timestamp' not in df.columns:
                    continue
                
                # Get records for this timestamp
                records_at_timestamp = df[df['timestamp'] == timestamp]
                
                if len(records_at_timestamp) == 0:
                    continue
                
                # Determine Kafka topic
                topic_mapping = {
                    'core_sensor_data': self.config['kafka']['topics']['core_sensor'],
                    'vehicle_health_data': self.config['kafka']['topics']['vehicle_health'],
                    'driving_behavior_data': self.config['kafka']['topics']['driving_behavior'],
                    'environmental_data': self.config['kafka']['topics']['environmental']
                }
                
                topic = topic_mapping.get(dataset_name, 'default-topic')
                
                # Send each record
                for _, record in records_at_timestamp.iterrows():
                    record_dict = record.to_dict()
                    processed_record = self.preprocess_data(record_dict, dataset_name)
                    
                    vehicle_id = record_dict.get('vehicle_id', 'unknown')
                    
                    success = self.send_to_kafka(topic, processed_record, vehicle_id)
                    if success:
                        self.logger.debug(f"Sent {dataset_name} data for vehicle {vehicle_id}")
            
            # Wait for next interval (adjusted for simulation speed)
            adjusted_interval = interval / self.config['simulation']['speed_multiplier']
            time.sleep(adjusted_interval)
        
        self.logger.info("Finished streaming all data")
    
    def simulate_vehicle_streaming(self, vehicle_id):
        """Simulate streaming for a specific vehicle"""
        self.logger.info(f"Starting vehicle-specific streaming for {vehicle_id}")
        
        # Collect all data for this vehicle across datasets
        vehicle_data = {}
        for dataset_name, df in self.datasets.items():
            if 'vehicle_id' in df.columns:
                vehicle_records = df[df['vehicle_id'] == vehicle_id].copy()
                if len(vehicle_records) > 0:
                    vehicle_data[dataset_name] = vehicle_records.sort_values('timestamp')
        
        if not vehicle_data:
            self.logger.warning(f"No data found for vehicle {vehicle_id}")
            return
        
        # Get all timestamps for this vehicle
        timestamps = set()
        for df in vehicle_data.values():
            if 'timestamp' in df.columns:
                timestamps.update(df['timestamp'].unique())
        
        sorted_timestamps = sorted(timestamps)
        interval = self.config['simulation']['replay_interval_seconds']
        
        for timestamp in sorted_timestamps:
            if not self.running:
                break
            
            # Send data from each dataset for this timestamp
            for dataset_name, df in vehicle_data.items():
                records_at_timestamp = df[df['timestamp'] == timestamp]
                
                if len(records_at_timestamp) == 0:
                    continue
                
                topic_mapping = {
                    'core_sensor_data': self.config['kafka']['topics']['core_sensor'],
                    'vehicle_health_data': self.config['kafka']['topics']['vehicle_health'],
                    'driving_behavior_data': self.config['kafka']['topics']['driving_behavior'],
                    'environmental_data': self.config['kafka']['topics']['environmental']
                }
                
                topic = topic_mapping.get(dataset_name, 'default-topic')
                
                for _, record in records_at_timestamp.iterrows():
                    record_dict = record.to_dict()
                    processed_record = self.preprocess_data(record_dict, dataset_name)
                    
                    self.send_to_kafka(topic, processed_record, vehicle_id)
            
            # Wait for next interval
            adjusted_interval = interval / self.config['simulation']['speed_multiplier']
            time.sleep(adjusted_interval)
        
        self.logger.info(f"Finished streaming for vehicle {vehicle_id}")
    
    def start_simulation(self, mode='all_vehicles', vehicle_id=None):
        """Start the simulation"""
        self.logger.info("Starting Telematics ECU Simulator")
        
        # Load datasets
        if not self.load_datasets():
            self.logger.error("Failed to load datasets")
            return False
        
        # Connect to Kafka
        if not self.connect_kafka():
            self.logger.error("Failed to connect to Kafka")
            return False
        
        self.running = True
        
        if mode == 'all_vehicles':
            # Stream all vehicles in real-time simulation
            thread = threading.Thread(target=self.simulate_real_time_streaming)
            thread.start()
            self.threads.append(thread)
            
        elif mode == 'single_vehicle' and vehicle_id:
            # Stream specific vehicle
            thread = threading.Thread(target=self.simulate_vehicle_streaming, args=(vehicle_id,))
            thread.start()
            self.threads.append(thread)
            
        elif mode == 'multi_vehicle':
            # Stream multiple vehicles in parallel
            unique_vehicles = set()
            for df in self.datasets.values():
                if 'vehicle_id' in df.columns:
                    unique_vehicles.update(df['vehicle_id'].unique())
            
            self.logger.info(f"Starting parallel streaming for {len(unique_vehicles)} vehicles")
            
            for vid in list(unique_vehicles)[:5]:  # Limit to first 5 vehicles for demo
                thread = threading.Thread(target=self.simulate_vehicle_streaming, args=(vid,))
                thread.start()
                self.threads.append(thread)
        
        return True
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.logger.info("Stopping Telematics ECU Simulator")
        self.running = False
        
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join(timeout=5)
        
        # Close Kafka producer
        if self.producer:
            self.producer.close()
        
        self.logger.info("Telematics ECU Simulator stopped")
    
    def get_simulation_status(self):
        """Get current simulation status"""
        return {
            'running': self.running,
            'datasets_loaded': len(self.datasets),
            'active_threads': len([t for t in self.threads if t.is_alive()]),
            'kafka_connected': self.producer is not None
        }

if __name__ == "__main__":
    # Command line interface
    import argparse
    
    parser = argparse.ArgumentParser(description='Telematics ECU Simulator')
    parser.add_argument('--mode', choices=['all_vehicles', 'single_vehicle', 'multi_vehicle'], 
                      default='all_vehicles', help='Simulation mode')
    parser.add_argument('--vehicle-id', help='Vehicle ID for single vehicle mode')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--duration', type=int, help='Simulation duration in seconds')
    
    args = parser.parse_args()
    
    # Create and start simulator
    simulator = TelematicsECUSimulator(args.config)
    
    try:
        success = simulator.start_simulation(args.mode, args.vehicle_id)
        
        if success:
            print(f"Simulation started in {args.mode} mode")
            print("Press Ctrl+C to stop...")
            
            if args.duration:
                time.sleep(args.duration)
                simulator.stop_simulation()
            else:
                # Wait for keyboard interrupt
                while simulator.running:
                    time.sleep(1)
        else:
            print("Failed to start simulation")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        simulator.stop_simulation()
    except Exception as e:
        print(f"Error: {e}")
        simulator.stop_simulation()
        sys.exit(1)
