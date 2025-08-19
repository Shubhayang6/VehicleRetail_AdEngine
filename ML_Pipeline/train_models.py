import pandas as pd
import numpy as np
import json
import os
import logging
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict

from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MaintenancePrediction:
    """Maintenance prediction result"""
    vehicle_id: str
    timestamp: str
    prediction_time: str
    
    # Risk scores (0-1)
    failure_probability: float
    maintenance_urgency: float
    
    # Component health predictions
    engine_health_prediction: float
    brake_health_prediction: float
    tire_health_prediction: float
    
    # Maintenance recommendations
    recommended_actions: List[str]
    risk_level: str  # low, medium, high
    days_until_maintenance: int
    
    # Confidence scores
    prediction_confidence: float
    model_accuracy: float

@dataclass
class ComponentFailure:
    """Component-specific failure prediction"""
    component: str
    failure_probability: float
    estimated_days_to_failure: int
    recommended_action: str
    severity: str

class FeatureEngineer:
    """Extract and engineer features for ML models"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('FeatureEngineer')
    
    def load_training_data(self) -> pd.DataFrame:
        """Load and combine all training datasets"""
        datasets_path = self.config['data_sources']['training_data']
        
        # Load all CSV files
        datasets = {}
        csv_files = [
            'core_sensor_data.csv',
            'vehicle_health_data.csv', 
            'driving_behavior_data.csv',
            'environmental_data.csv',
            'maintenance_history.csv'
        ]
        
        for file in csv_files:
            file_path = os.path.join(datasets_path, file)
            if os.path.exists(file_path):
                datasets[file.replace('.csv', '')] = pd.read_csv(file_path)
                self.logger.info(f"Loaded {file}: {len(datasets[file.replace('.csv', '')])} records")
        
        # Merge datasets on vehicle_id and timestamp
        if not datasets:
            raise ValueError("No training datasets found")
        
        # Start with core sensor data
        merged_df = datasets['core_sensor_data'].copy()
        
        # Merge other datasets
        merge_keys = ['vehicle_id', 'timestamp']
        for name, df in datasets.items():
            if name != 'core_sensor_data':
                merged_df = merged_df.merge(df, on=merge_keys, how='left', suffixes=('', f'_{name}'))
        
        self.logger.info(f"Merged training data: {len(merged_df)} records, {len(merged_df.columns)} features")
        return merged_df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create engineered features for ML models"""
        engineered_df = df.copy()
        
        # Convert timestamp to datetime
        engineered_df['timestamp'] = pd.to_datetime(engineered_df['timestamp'])
        
        # Time-based features
        engineered_df['hour'] = engineered_df['timestamp'].dt.hour
        engineered_df['day_of_week'] = engineered_df['timestamp'].dt.dayofweek
        engineered_df['month'] = engineered_df['timestamp'].dt.month
        
        # Health ratio features
        if 'engine_temp_c' in engineered_df.columns:
            engineered_df['temp_ratio'] = engineered_df['engine_temp_c'] / 100.0
        
        if 'fuel_level_percent' in engineered_df.columns:
            engineered_df['fuel_efficiency'] = engineered_df['fuel_level_percent'] / (engineered_df.get('mileage_km', 1) + 1)
        
        # Tire pressure variance
        tire_cols = [col for col in engineered_df.columns if 'tire_pressure' in col]
        if len(tire_cols) >= 4:
            tire_pressures = engineered_df[tire_cols]
            engineered_df['tire_pressure_mean'] = tire_pressures.mean(axis=1)
            engineered_df['tire_pressure_std'] = tire_pressures.std(axis=1)
            engineered_df['tire_pressure_variance'] = engineered_df['tire_pressure_std'] / engineered_df['tire_pressure_mean']
        
        # Driving behavior aggregates
        behavior_cols = [col for col in engineered_df.columns if any(x in col for x in ['harsh', 'speeding', 'sudden'])]
        if behavior_cols:
            engineered_df['total_violations'] = engineered_df[behavior_cols].sum(axis=1)
        
        # Age-based features (from mileage)
        if 'mileage_km' in engineered_df.columns:
            engineered_df['vehicle_age_factor'] = engineered_df['mileage_km'] / 100000  # Normalize by 100k km
        
        # Engine load efficiency
        if 'engine_load_percent' in engineered_df.columns and 'speed_kmh' in engineered_df.columns:
            engineered_df['load_speed_ratio'] = engineered_df['engine_load_percent'] / (engineered_df['speed_kmh'] + 1)
        
        self.logger.info(f"Feature engineering complete: {len(engineered_df.columns)} total features")
        return engineered_df
    
    def create_target_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target variables for supervised learning"""
        target_df = df.copy()
        
        # Failure prediction target (binary classification)
        # Based on multiple health indicators being below thresholds
        health_cols = [col for col in df.columns if 'health_score' in col or 'condition' in col]
        if health_cols:
            health_scores = df[health_cols].fillna(0.5)  # Fill missing with neutral
            target_df['will_fail_soon'] = (health_scores < 0.4).any(axis=1).astype(int)
        else:
            # Fallback: use engine temperature and other indicators
            target_df['will_fail_soon'] = (
                (df.get('engine_temp_c', 90) > 110) |
                (df.get('fuel_level_percent', 50) < 10) |
                (df.get('mileage_km', 0) > 150000)
            ).astype(int)
        
        # Maintenance urgency target (regression 0-1)
        target_df['maintenance_urgency_target'] = 0.5  # Default medium urgency
        
        if 'mileage_km' in df.columns:
            # Higher mileage = higher urgency
            target_df['maintenance_urgency_target'] += (df['mileage_km'] / 200000) * 0.3
        
        if 'engine_temp_c' in df.columns:
            # Higher temp = higher urgency
            target_df['maintenance_urgency_target'] += ((df['engine_temp_c'] - 90) / 30) * 0.2
        
        # Clamp to 0-1 range
        target_df['maintenance_urgency_target'] = target_df['maintenance_urgency_target'].clip(0, 1)
        
        # Component health targets
        for component in ['engine', 'brake', 'tire']:
            col_name = f'{component}_health_target'
            if f'{component}_health_score' in df.columns:
                target_df[col_name] = df[f'{component}_health_score']
            else:
                # Generate synthetic health based on available data
                base_health = 0.8
                if component == 'engine' and 'engine_temp_c' in df.columns:
                    temp_penalty = (df['engine_temp_c'] - 90) / 50
                    target_df[col_name] = (base_health - temp_penalty).clip(0, 1)
                elif component == 'tire' and 'tire_pressure_mean' in target_df.columns:
                    pressure_health = 1 - abs(target_df['tire_pressure_mean'] - 32) / 15
                    target_df[col_name] = pressure_health.clip(0, 1)
                else:
                    target_df[col_name] = base_health
        
        self.logger.info("Target variables created for supervised learning")
        return target_df

class PredictiveMaintenanceML:
    """Main ML pipeline for predictive maintenance"""
    
    def __init__(self, config_file='ml_config.json'):
        """Initialize ML pipeline"""
        self.config = self.load_config(config_file)
        self.models = {}
        self.scalers = {}
        self.feature_columns = {}
        
        # Create output directories
        for dir_path in ['models', 'predictions', 'reports']:
            os.makedirs(dir_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PredictiveMaintenanceML')
        
        # Initialize components
        self.feature_engineer = FeatureEngineer(self.config)
        
        # Performance tracking
        self.model_performance = {}
    
    def load_config(self, config_file):
        """Load ML configuration"""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
        """Load and prepare training data"""
        self.logger.info("Loading and preparing training data...")
        
        # Load raw training data
        raw_df = self.feature_engineer.load_training_data()
        
        # Engineer features
        feature_df = self.feature_engineer.engineer_features(raw_df)
        
        # Create targets
        target_df = self.feature_engineer.create_target_variables(feature_df)
        
        # Extract target variables
        targets = {
            'failure': target_df['will_fail_soon'],
            'urgency': target_df['maintenance_urgency_target'],
            'engine_health': target_df['engine_health_target'],
            'brake_health': target_df['brake_health_target'],
            'tire_health': target_df['tire_health_target']
        }
        
        # Select feature columns (exclude targets and metadata)
        exclude_cols = ['vehicle_id', 'timestamp'] + [col for col in target_df.columns if 'target' in col or col == 'will_fail_soon']
        feature_columns = [col for col in target_df.columns if col not in exclude_cols]
        
        # Handle categorical variables
        categorical_cols = target_df[feature_columns].select_dtypes(include=['object']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            target_df[col] = le.fit_transform(target_df[col].astype(str))
        
        # Fill missing values
        feature_df_clean = target_df[feature_columns].fillna(target_df[feature_columns].mean())
        
        self.feature_columns['all'] = feature_columns
        self.logger.info(f"Training data prepared: {len(feature_df_clean)} samples, {len(feature_columns)} features")
        
        return feature_df_clean, targets
    
    def train_failure_prediction_model(self, X: pd.DataFrame, y: pd.Series) -> float:
        """Train binary classification model for failure prediction"""
        self.logger.info("Training failure prediction model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config['model_settings']['failure_prediction']['test_size'], 
            random_state=self.config['model_settings']['failure_prediction']['random_state']
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model_config = self.config['model_settings']['failure_prediction']
        model = RandomForestClassifier(
            n_estimators=model_config['n_estimators'],
            max_depth=model_config['max_depth'],
            random_state=model_config['random_state']
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Cross validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        
        self.models['failure_prediction'] = model
        self.scalers['failure_prediction'] = scaler
        
        performance = {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
        self.model_performance['failure_prediction'] = performance
        
        self.logger.info(f"Failure prediction model trained - Test accuracy: {test_score:.3f}")
        return test_score
    
    def train_maintenance_urgency_model(self, X: pd.DataFrame, y: pd.Series) -> float:
        """Train regression model for maintenance urgency"""
        self.logger.info("Training maintenance urgency model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model_config = self.config['model_settings']['maintenance_urgency']
        model = GradientBoostingRegressor(
            n_estimators=model_config['n_estimators'],
            learning_rate=model_config['learning_rate'],
            max_depth=model_config['max_depth']
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train_scaled)
        test_pred = model.predict(X_test_scaled)
        
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        
        self.models['maintenance_urgency'] = model
        self.scalers['maintenance_urgency'] = scaler
        
        performance = {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'test_mse': test_mse
        }
        self.model_performance['maintenance_urgency'] = performance
        
        self.logger.info(f"Maintenance urgency model trained - Test R²: {test_r2:.3f}")
        return test_r2
    
    def train_component_health_models(self, X: pd.DataFrame, targets: Dict[str, pd.Series]) -> Dict[str, float]:
        """Train component-specific health prediction models"""
        self.logger.info("Training component health models...")
        
        component_performance = {}
        
        for component in ['engine', 'brake', 'tire']:
            target_key = f'{component}_health'
            if target_key not in targets:
                continue
                
            self.logger.info(f"Training {component} health model...")
            
            y = targets[target_key]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train SVR model
            model_config = self.config['model_settings']['component_health']
            model = SVR(
                kernel=model_config['kernel'],
                C=model_config['C'],
                gamma=model_config['gamma']
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            test_pred = model.predict(X_test_scaled)
            test_r2 = r2_score(y_test, test_pred)
            test_mse = mean_squared_error(y_test, test_pred)
            
            self.models[f'{component}_health'] = model
            self.scalers[f'{component}_health'] = scaler
            
            performance = {
                'test_r2': test_r2,
                'test_mse': test_mse
            }
            self.model_performance[f'{component}_health'] = performance
            component_performance[component] = test_r2
            
            self.logger.info(f"{component.title()} health model trained - Test R²: {test_r2:.3f}")
        
        return component_performance
    
    def train_all_models(self):
        """Train all ML models"""
        self.logger.info("Starting model training pipeline...")
        
        # Prepare training data
        X, targets = self.prepare_training_data()
        
        # Train all models
        failure_acc = self.train_failure_prediction_model(X, targets['failure'])
        urgency_r2 = self.train_maintenance_urgency_model(X, targets['urgency'])
        component_r2s = self.train_component_health_models(X, targets)
        
        # Save models
        self.save_models()
        
        # Generate training report
        self.generate_training_report()
        
        self.logger.info("All models trained successfully!")
        return {
            'failure_accuracy': failure_acc,
            'urgency_r2': urgency_r2,
            'component_r2s': component_r2s
        }
    
    def save_models(self):
        """Save trained models and scalers"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for name, model in self.models.items():
            model_path = f"models/{name}_model_{timestamp}.joblib"
            joblib.dump(model, model_path)
            
            scaler_path = f"models/{name}_scaler_{timestamp}.joblib"
            joblib.dump(self.scalers[name], scaler_path)
            
            self.logger.info(f"Saved {name} model and scaler")
        
        # Save feature columns
        feature_path = f"models/feature_columns_{timestamp}.joblib"
        joblib.dump(self.feature_columns, feature_path)
        
        # Save model metadata
        metadata = {
            'timestamp': timestamp,
            'model_performance': self.model_performance,
            'config': self.config
        }
        
        with open(f"models/model_metadata_{timestamp}.json", 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def generate_training_report(self):
        """Generate comprehensive training report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = {
            'training_timestamp': timestamp,
            'model_performance': self.model_performance,
            'training_summary': {
                'total_models_trained': len(self.models),
                'feature_count': len(self.feature_columns.get('all', [])),
                'best_failure_accuracy': self.model_performance.get('failure_prediction', {}).get('test_accuracy', 0),
                'best_urgency_r2': self.model_performance.get('maintenance_urgency', {}).get('test_r2', 0)
            }
        }
        
        # Save report
        with open(f"reports/training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Training report generated: {len(self.models)} models trained")

if __name__ == "__main__":
    # Initialize and train ML pipeline
    ml_pipeline = PredictiveMaintenanceML()
    
    try:
        print("Starting ML Pipeline Training...")
        print("This will train models for:")
        print("  1. Failure Prediction (Classification)")
        print("  2. Maintenance Urgency (Regression)")
        print("  3. Component Health (Engine, Brake, Tire)")
        print()
        
        # Train all models
        results = ml_pipeline.train_all_models()
        
        print("\n=== TRAINING COMPLETE ===")
        print("Model Performance Summary:")
        print(f"  Failure Prediction Accuracy: {results['failure_accuracy']:.3f}")
        print(f"  Maintenance Urgency R²: {results['urgency_r2']:.3f}")
        print("  Component Health R² Scores:")
        for component, r2 in results['component_r2s'].items():
            print(f"    {component.title()}: {r2:.3f}")
        
        print("\nModels saved to 'models/' directory")
        print("Training reports saved to 'reports/' directory")
        
    except Exception as e:
        print(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
