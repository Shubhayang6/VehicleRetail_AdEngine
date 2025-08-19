import pandas as pd
import json
import time
import logging
from datetime import datetime
import os
import sys

class TelematicsECUSimulator_NoKafka:
    """
    Simplified Telematics ECU Simulator for testing without Kafka
    Outputs to console and files instead of Kafka topics
    """
    
    def __init__(self, config_file='config.json'):
        """Initialize the Telematics ECU Simulator"""
        self.config = self.load_config(config_file)
        self.datasets = {}
        self.running = False
        self.output_dir = "output"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TelematicsECU_Test')
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "datasets": {
                "core_sensor_data": "../Dataset/core_sensor_data.csv",
                "vehicle_health_data": "../Dataset/vehicle_health_data.csv",
                "driving_behavior_data": "../Dataset/driving_behavior_data.csv",
                "environmental_data": "../Dataset/environmental_data.csv"
            },
            "simulation": {
                "speed_multiplier": 10,  # 10x faster for testing
                "replay_interval_seconds": 1,  # Send data every 1 second
                "batch_size": 1
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Could not load config file {config_file}: {e}")
        
        return default_config
    
    def load_datasets(self):
        """Load all CSV datasets into memory"""
        for dataset_name, filename in self.config['datasets'].items():
            # Handle relative paths
            if not os.path.isabs(filename):
                file_path = os.path.join(os.path.dirname(__file__), filename)
            else:
                file_path = filename
            
            if not os.path.exists(file_path):
                self.logger.error(f"Dataset file not found: {file_path}")
                return False
            
            try:
                df = pd.read_csv(file_path)
                # Convert timestamp to datetime
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values(['vehicle_id', 'timestamp'])
                
                self.datasets[dataset_name] = df
                self.logger.info(f"Loaded {len(df)} records from {filename}")
                
            except Exception as e:
                self.logger.error(f"Failed to load dataset {filename}: {e}")
                return False
        
        return True
    
    def preprocess_data(self, record, dataset_type):
        """Preprocess data record before output"""
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
    
    def output_data(self, topic, data, vehicle_id):
        """Output data to console and file"""
        try:
            # Console output (limited)
            self.logger.info(f"[{topic}] Vehicle {vehicle_id}: {data.get('timestamp', 'N/A')}")
            
            # File output
            output_file = os.path.join(self.output_dir, f"{topic}_output.jsonl")
            with open(output_file, 'a') as f:
                f.write(json.dumps(data) + '\n')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to output data for {topic}: {e}")
            return False
    
    def simulate_streaming(self, vehicle_id=None, max_records=50):
        """Simulate data streaming"""
        self.logger.info("Starting data streaming simulation")
        
        # Clear output files
        for topic in ['sensor-data-topic', 'health-data-topic', 'behavior-topic', 'environment-topic']:
            output_file = os.path.join(self.output_dir, f"{topic}_output.jsonl")
            if os.path.exists(output_file):
                os.remove(output_file)
        
        # Get all unique timestamps
        all_timestamps = set()
        for df in self.datasets.values():
            if 'timestamp' in df.columns:
                all_timestamps.update(df['timestamp'].unique())
        
        sorted_timestamps = sorted(all_timestamps)[:max_records]  # Limit for testing
        
        records_sent = 0
        
        for timestamp in sorted_timestamps:
            if not self.running:
                break
            
            self.logger.info(f"Processing timestamp {timestamp}")
            
            # Send data for each dataset at this timestamp
            for dataset_name, df in self.datasets.items():
                if 'timestamp' not in df.columns:
                    continue
                
                # Filter by vehicle if specified
                if vehicle_id:
                    records_at_timestamp = df[(df['timestamp'] == timestamp) & (df['vehicle_id'] == vehicle_id)]
                else:
                    records_at_timestamp = df[df['timestamp'] == timestamp]
                
                if len(records_at_timestamp) == 0:
                    continue
                
                # Determine topic
                topic_mapping = {
                    'core_sensor_data': 'sensor-data-topic',
                    'vehicle_health_data': 'health-data-topic',
                    'driving_behavior_data': 'behavior-topic',
                    'environmental_data': 'environment-topic'
                }
                
                topic = topic_mapping.get(dataset_name, 'default-topic')
                
                # Send each record
                for _, record in records_at_timestamp.iterrows():
                    record_dict = record.to_dict()
                    processed_record = self.preprocess_data(record_dict, dataset_name)
                    
                    vid = record_dict.get('vehicle_id', 'unknown')
                    success = self.output_data(topic, processed_record, vid)
                    
                    if success:
                        records_sent += 1
            
            # Wait for next interval
            interval = self.config['simulation']['replay_interval_seconds']
            adjusted_interval = interval / self.config['simulation']['speed_multiplier']
            time.sleep(adjusted_interval)
        
        self.logger.info(f"Finished streaming. Total records sent: {records_sent}")
        return records_sent
    
    def start_test_simulation(self, vehicle_id=None, max_records=20):
        """Start a test simulation"""
        self.logger.info("Starting Telematics ECU Test Simulation")
        
        # Load datasets
        if not self.load_datasets():
            self.logger.error("Failed to load datasets")
            return False
        
        self.running = True
        records_sent = self.simulate_streaming(vehicle_id, max_records)
        
        # Show summary
        self.logger.info("=== SIMULATION SUMMARY ===")
        self.logger.info(f"Total records sent: {records_sent}")
        self.logger.info(f"Output directory: {os.path.abspath(self.output_dir)}")
        
        # Show sample output files
        for filename in os.listdir(self.output_dir):
            if filename.endswith('_output.jsonl'):
                file_path = os.path.join(self.output_dir, filename)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    self.logger.info(f"{filename}: {len(lines)} records")
        
        return True
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Telematics ECU Test Simulator')
    parser.add_argument('--vehicle-id', help='Vehicle ID for single vehicle test')
    parser.add_argument('--max-records', type=int, default=20, help='Maximum records to process')
    
    args = parser.parse_args()
    
    # Create and start test simulator
    simulator = TelematicsECUSimulator_NoKafka()
    
    try:
        print("Starting Telematics ECU Test Simulation...")
        print(f"Processing up to {args.max_records} records")
        if args.vehicle_id:
            print(f"Filtering for vehicle: {args.vehicle_id}")
        
        success = simulator.start_test_simulation(args.vehicle_id, args.max_records)
        
        if success:
            print("Test simulation completed successfully!")
            print(f"Check the 'output' directory for generated files")
        else:
            print("Test simulation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        simulator.stop_simulation()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
