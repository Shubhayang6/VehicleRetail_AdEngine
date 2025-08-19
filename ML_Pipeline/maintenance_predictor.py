import pandas as pd
import numpy as np
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict

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

@dataclass
class ComponentFailure:
    """Component-specific failure prediction"""
    component: str
    failure_probability: float
    estimated_days_to_failure: int
    recommended_action: str
    severity: str

class MaintenancePredictor:
    """
    Predictive Maintenance Service that processes ML Pipeline input data
    and generates maintenance predictions without requiring sklearn
    """
    
    def __init__(self, config_file='ml_config.json'):
        """Initialize the maintenance predictor"""
        self.config = self.load_config(config_file)
        
        # Create output directories
        for dir_path in ['predictions', 'alerts', 'reports']:
            os.makedirs(dir_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('MaintenancePredictor')
        
        # Rule-based prediction parameters
        self.health_thresholds = self.config['feature_engineering']['health_thresholds']
        self.prediction_thresholds = self.config['prediction_thresholds']
        self.maintenance_categories = self.config['maintenance_categories']
        
        # Statistics tracking
        self.prediction_stats = {
            'total_predictions': 0,
            'high_risk_vehicles': 0,
            'medium_risk_vehicles': 0,
            'low_risk_vehicles': 0,
            'maintenance_alerts_generated': 0
        }
    
    def load_config(self, config_file):
        """Load ML configuration"""
        default_config = {
            "feature_engineering": {
                "health_thresholds": {
                    "engine": 0.6,
                    "brake": 0.7,
                    "tire": 0.8
                }
            },
            "prediction_thresholds": {
                "high_risk": 0.8,
                "medium_risk": 0.5,
                "low_risk": 0.2
            },
            "maintenance_categories": {
                "engine": ["oil_change", "filter_replacement", "cooling_system"],
                "brake": ["brake_pad_replacement", "brake_fluid", "rotor_service"],
                "tire": ["tire_rotation", "pressure_check", "alignment"],
                "general": ["inspection", "battery_check", "fluid_top_up"]
            },
            "data_sources": {
                "input_path": "../Data_Processing/output/ml_pipeline/ml_input_data.jsonl"
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return default_config
    
    def load_ml_input_data(self) -> List[Dict]:
        """Load data from ML Pipeline branch"""
        input_path = self.config['data_sources']['input_path']
        
        if not os.path.exists(input_path):
            self.logger.warning(f"ML input data not found: {input_path}")
            return []
        
        ml_data = []
        try:
            with open(input_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        ml_data.append(data)
            
            self.logger.info(f"Loaded {len(ml_data)} records from ML pipeline")
            return ml_data
            
        except Exception as e:
            self.logger.error(f"Error loading ML input data: {e}")
            return []
    
    def calculate_failure_probability(self, vehicle_data: Dict) -> float:
        """Calculate failure probability using rule-based approach"""
        health_scores = vehicle_data.get('health_scores', {})
        metrics = vehicle_data.get('vehicle_metrics', {})
        
        # Health score component (40% weight)
        overall_health = health_scores.get('overall', 0.8)
        health_risk = 1 - overall_health
        
        # Engine temperature risk (25% weight)
        engine_temp = metrics.get('engine_temp', 90)
        temp_risk = max(0, (engine_temp - 100) / 30)  # Risk starts at 100°C
        
        # Mileage risk (20% weight)
        mileage = metrics.get('mileage', 50000)
        mileage_risk = min(1, mileage / 200000)  # Full risk at 200k km
        
        # Fuel level risk (10% weight)
        fuel_level = metrics.get('fuel_level', 50)
        fuel_risk = max(0, (20 - fuel_level) / 20) if fuel_level < 20 else 0
        
        # Speed risk (5% weight)
        speed = metrics.get('speed', 60)
        speed_risk = max(0, (speed - 120) / 50) if speed > 120 else 0
        
        # Calculate weighted failure probability
        failure_prob = (
            health_risk * 0.4 +
            temp_risk * 0.25 +
            mileage_risk * 0.2 +
            fuel_risk * 0.1 +
            speed_risk * 0.05
        )
        
        return min(max(failure_prob, 0), 1)
    
    def calculate_maintenance_urgency(self, vehicle_data: Dict, failure_prob: float) -> float:
        """Calculate maintenance urgency score"""
        health_scores = vehicle_data.get('health_scores', {})
        metrics = vehicle_data.get('vehicle_metrics', {})
        
        # Base urgency from failure probability
        base_urgency = failure_prob * 0.6
        
        # Component health urgency
        engine_health = health_scores.get('engine', 0.8)
        brake_health = health_scores.get('brake', 0.8)
        tire_health = health_scores.get('tire', 0.8)
        
        component_urgency = (
            (1 - engine_health) * 0.4 +
            (1 - brake_health) * 0.3 +
            (1 - tire_health) * 0.3
        ) * 0.4
        
        total_urgency = base_urgency + component_urgency
        return min(max(total_urgency, 0), 1)
    
    def predict_component_health(self, vehicle_data: Dict) -> Dict[str, float]:
        """Predict future component health"""
        current_health = vehicle_data.get('health_scores', {})
        metrics = vehicle_data.get('vehicle_metrics', {})
        
        # Degradation factors
        mileage = metrics.get('mileage', 50000)
        engine_temp = metrics.get('engine_temp', 90)
        
        # Calculate degradation rates
        mileage_factor = mileage / 100000  # Higher mileage = faster degradation
        temp_factor = max(1, engine_temp / 100)  # Higher temp = faster degradation
        
        # Predict health degradation over next 30 days
        degradation_rate = 0.01 * mileage_factor * temp_factor
        
        predictions = {}
        for component in ['engine', 'brake', 'tire']:
            current = current_health.get(component, 0.8)
            predicted = max(0.1, current - degradation_rate)
            predictions[f'{component}_health_prediction'] = predicted
        
        return predictions
    
    def generate_recommendations(self, vehicle_data: Dict, failure_prob: float, 
                                urgency: float, component_predictions: Dict) -> List[str]:
        """Generate maintenance recommendations"""
        recommendations = []
        health_scores = vehicle_data.get('health_scores', {})
        
        # High urgency recommendations
        if urgency > self.prediction_thresholds['high_risk']:
            recommendations.append("URGENT: Schedule immediate inspection")
        
        # Component-specific recommendations
        for component in ['engine', 'brake', 'tire']:
            health = health_scores.get(component, 0.8)
            threshold = self.health_thresholds.get(component, 0.7)
            
            if health < threshold:
                component_actions = self.maintenance_categories.get(component, [])
                if component_actions:
                    recommendations.extend([f"{component.title()}: {action}" for action in component_actions[:2]])
        
        # Mileage-based recommendations
        mileage = vehicle_data.get('vehicle_metrics', {}).get('mileage', 0)
        if mileage > 100000 and mileage % 10000 < 1000:  # Every 10k km after 100k
            recommendations.extend(self.maintenance_categories['general'])
        
        # Temperature-based recommendations
        engine_temp = vehicle_data.get('vehicle_metrics', {}).get('engine_temp', 90)
        if engine_temp > 105:
            recommendations.append("Engine: Cooling system check - high temperature detected")
        
        return list(set(recommendations))  # Remove duplicates
    
    def calculate_days_until_maintenance(self, urgency: float, failure_prob: float) -> int:
        """Calculate estimated days until maintenance needed"""
        if urgency > self.prediction_thresholds['high_risk']:
            return 3  # Immediate
        elif urgency > self.prediction_thresholds['medium_risk']:
            return 14  # Two weeks
        elif failure_prob > 0.3:
            return 30  # One month
        else:
            return 90  # Quarterly
    
    def determine_risk_level(self, failure_prob: float, urgency: float) -> str:
        """Determine overall risk level"""
        max_risk = max(failure_prob, urgency)
        
        if max_risk > self.prediction_thresholds['high_risk']:
            return 'high'
        elif max_risk > self.prediction_thresholds['medium_risk']:
            return 'medium'
        else:
            return 'low'
    
    def make_prediction(self, vehicle_data: Dict) -> MaintenancePrediction:
        """Generate comprehensive maintenance prediction"""
        vehicle_id = vehicle_data.get('vehicle_id', 'unknown')
        timestamp = vehicle_data.get('timestamp', datetime.now().isoformat())
        
        # Calculate core predictions
        failure_prob = self.calculate_failure_probability(vehicle_data)
        urgency = self.calculate_maintenance_urgency(vehicle_data, failure_prob)
        component_predictions = self.predict_component_health(vehicle_data)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            vehicle_data, failure_prob, urgency, component_predictions
        )
        
        # Calculate timing and risk
        days_until = self.calculate_days_until_maintenance(urgency, failure_prob)
        risk_level = self.determine_risk_level(failure_prob, urgency)
        
        # Calculate confidence (simplified)
        confidence = 0.8 if len(recommendations) > 0 else 0.6
        
        # Create prediction object
        prediction = MaintenancePrediction(
            vehicle_id=vehicle_id,
            timestamp=timestamp,
            prediction_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            failure_probability=failure_prob,
            maintenance_urgency=urgency,
            engine_health_prediction=component_predictions.get('engine_health_prediction', 0.8),
            brake_health_prediction=component_predictions.get('brake_health_prediction', 0.8),
            tire_health_prediction=component_predictions.get('tire_health_prediction', 0.8),
            recommended_actions=recommendations,
            risk_level=risk_level,
            days_until_maintenance=days_until,
            prediction_confidence=confidence
        )
        
        # Update statistics
        self.prediction_stats['total_predictions'] += 1
        self.prediction_stats[f'{risk_level}_risk_vehicles'] += 1
        if len(recommendations) > 0:
            self.prediction_stats['maintenance_alerts_generated'] += 1
        
        return prediction
    
    def process_all_predictions(self) -> List[MaintenancePrediction]:
        """Process all vehicles in ML input data"""
        self.logger.info("Starting predictive maintenance analysis...")
        
        # Load ML input data
        ml_data = self.load_ml_input_data()
        
        if not ml_data:
            self.logger.warning("No ML input data found")
            return []
        
        # Generate predictions for each vehicle
        predictions = []
        for vehicle_data in ml_data:
            try:
                prediction = self.make_prediction(vehicle_data)
                predictions.append(prediction)
                
                self.logger.info(f"Prediction for {prediction.vehicle_id}: "
                               f"Risk={prediction.risk_level}, "
                               f"Failure_Prob={prediction.failure_probability:.3f}, "
                               f"Days={prediction.days_until_maintenance}")
                
            except Exception as e:
                self.logger.error(f"Error processing vehicle {vehicle_data.get('vehicle_id', 'unknown')}: {e}")
        
        # Save predictions
        self.save_predictions(predictions)
        
        # Generate alerts for high-risk vehicles
        self.generate_maintenance_alerts(predictions)
        
        # Generate summary report
        self.generate_prediction_report(predictions)
        
        self.logger.info(f"Processed {len(predictions)} maintenance predictions")
        return predictions
    
    def save_predictions(self, predictions: List[MaintenancePrediction]):
        """Save predictions to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSONL
        output_file = f"predictions/maintenance_predictions_{timestamp}.jsonl"
        with open(output_file, 'w') as f:
            for prediction in predictions:
                f.write(json.dumps(asdict(prediction)) + '\n')
        
        self.logger.info(f"Saved {len(predictions)} predictions to {output_file}")
    
    def generate_maintenance_alerts(self, predictions: List[MaintenancePrediction]):
        """Generate alerts for high-risk vehicles"""
        high_risk_predictions = [p for p in predictions if p.risk_level == 'high']
        
        if not high_risk_predictions:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        alert_file = f"alerts/maintenance_alerts_{timestamp}.json"
        
        alerts = []
        for prediction in high_risk_predictions:
            alert = {
                'vehicle_id': prediction.vehicle_id,
                'alert_type': 'maintenance_required',
                'severity': 'high',
                'failure_probability': prediction.failure_probability,
                'days_until_maintenance': prediction.days_until_maintenance,
                'recommended_actions': prediction.recommended_actions,
                'generated_at': prediction.prediction_time
            }
            alerts.append(alert)
        
        with open(alert_file, 'w') as f:
            json.dump(alerts, f, indent=2)
        
        self.logger.info(f"Generated {len(alerts)} high-priority maintenance alerts")
    
    def generate_prediction_report(self, predictions: List[MaintenancePrediction]):
        """Generate comprehensive prediction report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Calculate summary statistics
        total_predictions = len(predictions)
        if total_predictions == 0:
            return
        
        avg_failure_prob = sum(p.failure_probability for p in predictions) / total_predictions
        avg_urgency = sum(p.maintenance_urgency for p in predictions) / total_predictions
        avg_confidence = sum(p.prediction_confidence for p in predictions) / total_predictions
        
        risk_distribution = {
            'high': len([p for p in predictions if p.risk_level == 'high']),
            'medium': len([p for p in predictions if p.risk_level == 'medium']),
            'low': len([p for p in predictions if p.risk_level == 'low'])
        }
        
        # Component health summary
        avg_engine_health = sum(p.engine_health_prediction for p in predictions) / total_predictions
        avg_brake_health = sum(p.brake_health_prediction for p in predictions) / total_predictions
        avg_tire_health = sum(p.tire_health_prediction for p in predictions) / total_predictions
        
        report = {
            'report_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_vehicles_analyzed': total_predictions,
                'average_failure_probability': round(avg_failure_prob, 3),
                'average_maintenance_urgency': round(avg_urgency, 3),
                'average_prediction_confidence': round(avg_confidence, 3)
            },
            'risk_distribution': risk_distribution,
            'component_health_outlook': {
                'average_engine_health': round(avg_engine_health, 3),
                'average_brake_health': round(avg_brake_health, 3),
                'average_tire_health': round(avg_tire_health, 3)
            },
            'processing_statistics': self.prediction_stats
        }
        
        report_file = f"reports/prediction_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Generated prediction report: {report_file}")

if __name__ == "__main__":
    # Run predictive maintenance analysis
    predictor = MaintenancePredictor()
    
    try:
        print("Starting Predictive Maintenance Analysis...")
        print("Processing data from ML Pipeline branch...")
        print()
        
        # Process all predictions
        predictions = predictor.process_all_predictions()
        
        if predictions:
            print("\n=== PREDICTIVE MAINTENANCE RESULTS ===")
            print(f"Total vehicles analyzed: {len(predictions)}")
            
            # Risk distribution
            risk_counts = {'high': 0, 'medium': 0, 'low': 0}
            for pred in predictions:
                risk_counts[pred.risk_level] += 1
            
            print("Risk Distribution:")
            for risk, count in risk_counts.items():
                print(f"  {risk.title()} Risk: {count} vehicles")
            
            # High-risk vehicles detail
            high_risk = [p for p in predictions if p.risk_level == 'high']
            if high_risk:
                print(f"\nHigh-Risk Vehicles ({len(high_risk)}):")
                for pred in high_risk:
                    print(f"  {pred.vehicle_id}: Failure Prob={pred.failure_probability:.3f}, "
                          f"Days Until Maintenance={pred.days_until_maintenance}")
            
            print(f"\nGenerated files:")
            print(f"  - Predictions: predictions/ directory")
            print(f"  - Alerts: alerts/ directory") 
            print(f"  - Reports: reports/ directory")
        else:
            print("No predictions generated - check ML input data")
            
    except Exception as e:
        print(f"Prediction analysis failed: {e}")
        import traceback
        traceback.print_exc()
