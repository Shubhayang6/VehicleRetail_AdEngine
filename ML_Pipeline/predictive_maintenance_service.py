import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class MaintenanceAlert:
    """Maintenance alert for infotainment system"""
    alert_id: str
    vehicle_id: str
    alert_type: str
    severity: str  # low, medium, high, critical
    title: str
    message: str
    recommended_actions: List[str]
    estimated_cost: Optional[float]
    urgency_days: int
    created_at: str
    expires_at: str
    
@dataclass
class ServiceAppointment:
    """Service appointment request"""
    appointment_id: str
    vehicle_id: str
    service_type: str
    preferred_date: str
    service_center_id: str
    estimated_duration: str
    services_requested: List[str]
    priority: str
    notes: str

class PredictiveMaintenanceService:
    """
    Service that processes ML predictions and generates user-facing alerts
    and service scheduling recommendations according to the architecture
    """
    
    def __init__(self, config_file='../ML_Pipeline/ml_config.json'):
        """Initialize the service"""
        self.config = self.load_config(config_file)
        
        # Create output directories
        for dir_path in ['alerts', 'appointments', 'notifications']:
            os.makedirs(dir_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PredictiveMaintenanceService')
        
        # Service pricing (mock data)
        self.service_pricing = {
            'oil_change': 75.0,
            'filter_replacement': 45.0,
            'cooling_system': 150.0,
            'brake_pad_replacement': 200.0,
            'brake_fluid': 80.0,
            'rotor_service': 300.0,
            'tire_rotation': 50.0,
            'pressure_check': 25.0,
            'alignment': 120.0,
            'inspection': 100.0,
            'battery_check': 60.0,
            'fluid_top_up': 40.0
        }
        
        # Service centers (mock data)
        self.service_centers = {
            'SC001': {'name': 'Downtown Auto Center', 'location': 'Downtown', 'distance': 5.2},
            'SC002': {'name': 'Highway Service Station', 'location': 'Highway 401', 'distance': 12.8},
            'SC003': {'name': 'Northside Automotive', 'location': 'North Plaza', 'distance': 8.7},
            'SC004': {'name': 'Express Auto Care', 'location': 'Mall District', 'distance': 6.4}
        }
        
        # Statistics
        self.service_stats = {
            'alerts_generated': 0,
            'appointments_scheduled': 0,
            'notifications_sent': 0,
            'cost_estimates_provided': 0
        }
    
    def load_config(self, config_file):
        """Load configuration"""
        default_config = {
            'ml_predictions_path': '../ML_Pipeline/predictions/',
            'alert_thresholds': {
                'critical': 0.9,
                'high': 0.7,
                'medium': 0.4,
                'low': 0.2
            },
            'service_scheduling': {
                'advance_booking_days': 7,
                'preferred_times': ['09:00', '13:00', '15:00']
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def load_latest_predictions(self) -> List[Dict]:
        """Load the latest ML predictions"""
        predictions_dir = self.config['ml_predictions_path']
        
        if not os.path.exists(predictions_dir):
            self.logger.error(f"Predictions directory not found: {predictions_dir}")
            return []
        
        # Find the latest predictions file
        prediction_files = [f for f in os.listdir(predictions_dir) if f.startswith('maintenance_predictions_')]
        
        if not prediction_files:
            self.logger.warning("No prediction files found")
            return []
        
        # Sort by timestamp and get the latest
        latest_file = sorted(prediction_files)[-1]
        file_path = os.path.join(predictions_dir, latest_file)
        
        predictions = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        predictions.append(json.loads(line.strip()))
            
            self.logger.info(f"Loaded {len(predictions)} predictions from {latest_file}")
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error loading predictions: {e}")
            return []
    
    def determine_alert_severity(self, failure_prob: float, urgency: float, days_until: int) -> str:
        """Determine alert severity based on ML predictions"""
        max_risk = max(failure_prob, urgency)
        
        if max_risk >= self.config['alert_thresholds']['critical'] or days_until <= 1:
            return 'critical'
        elif max_risk >= self.config['alert_thresholds']['high'] or days_until <= 7:
            return 'high'
        elif max_risk >= self.config['alert_thresholds']['medium'] or days_until <= 30:
            return 'medium'
        else:
            return 'low'
    
    def calculate_service_cost(self, recommended_actions: List[str]) -> float:
        """Calculate estimated service cost"""
        total_cost = 0.0
        
        for action in recommended_actions:
            # Extract service type from action description
            action_lower = action.lower()
            for service, cost in self.service_pricing.items():
                if service.replace('_', ' ') in action_lower:
                    total_cost += cost
                    break
        
        return total_cost
    
    def find_nearest_service_center(self, vehicle_location: Optional[str] = None) -> str:
        """Find the nearest service center (mock implementation)"""
        # In a real implementation, this would use actual location data
        # For now, return the closest mock service center
        return min(self.service_centers.keys(), 
                  key=lambda x: self.service_centers[x]['distance'])
    
    def generate_maintenance_alert(self, prediction: Dict) -> MaintenanceAlert:
        """Generate user-facing maintenance alert"""
        vehicle_id = prediction['vehicle_id']
        failure_prob = prediction['failure_probability']
        urgency = prediction['maintenance_urgency']
        days_until = prediction['days_until_maintenance']
        recommendations = prediction['recommended_actions']
        
        # Determine severity
        severity = self.determine_alert_severity(failure_prob, urgency, days_until)
        
        # Create alert ID
        alert_id = f"ALT_{vehicle_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate title and message based on severity
        if severity == 'critical':
            title = "🚨 CRITICAL: Immediate Service Required"
            message = f"Vehicle {vehicle_id} requires immediate attention. High failure risk detected."
        elif severity == 'high':
            title = "⚠️  HIGH PRIORITY: Service Recommended Soon"
            message = f"Vehicle {vehicle_id} should be serviced within {days_until} days."
        elif severity == 'medium':
            title = "📅 Maintenance Reminder"
            message = f"Vehicle {vehicle_id} maintenance due in {days_until} days."
        else:
            title = "ℹ️  Routine Maintenance Notice"
            message = f"Vehicle {vehicle_id} scheduled maintenance in {days_until} days."
        
        # Calculate estimated cost
        estimated_cost = self.calculate_service_cost(recommendations)
        
        # Set expiration
        expires_at = (datetime.now() + timedelta(days=days_until + 7)).strftime('%Y-%m-%d %H:%M:%S')
        
        alert = MaintenanceAlert(
            alert_id=alert_id,
            vehicle_id=vehicle_id,
            alert_type='maintenance_required',
            severity=severity,
            title=title,
            message=message,
            recommended_actions=recommendations,
            estimated_cost=estimated_cost if estimated_cost > 0 else None,
            urgency_days=days_until,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            expires_at=expires_at
        )
        
        self.service_stats['alerts_generated'] += 1
        if estimated_cost > 0:
            self.service_stats['cost_estimates_provided'] += 1
        
        return alert
    
    def create_service_appointment(self, alert: MaintenanceAlert, 
                                 user_preferences: Optional[Dict] = None) -> ServiceAppointment:
        """Create service appointment recommendation"""
        
        # Calculate preferred appointment date
        advance_days = self.config['service_scheduling']['advance_booking_days']
        if alert.severity == 'critical':
            advance_days = 1
        elif alert.severity == 'high':
            advance_days = 3
        
        preferred_date = (datetime.now() + timedelta(days=advance_days)).strftime('%Y-%m-%d')
        
        # Find service center
        service_center_id = self.find_nearest_service_center()
        
        # Estimate duration based on services
        service_count = len(alert.recommended_actions)
        if service_count >= 3:
            duration = "3-4 hours"
        elif service_count >= 2:
            duration = "2-3 hours"
        else:
            duration = "1-2 hours"
        
        # Generate appointment ID
        appointment_id = f"APT_{alert.vehicle_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        appointment = ServiceAppointment(
            appointment_id=appointment_id,
            vehicle_id=alert.vehicle_id,
            service_type='predictive_maintenance',
            preferred_date=preferred_date,
            service_center_id=service_center_id,
            estimated_duration=duration,
            services_requested=alert.recommended_actions,
            priority=alert.severity,
            notes=f"Predictive maintenance based on ML analysis. Failure probability: {alert.alert_id}"
        )
        
        self.service_stats['appointments_scheduled'] += 1
        return appointment
    
    def generate_infotainment_notification(self, alert: MaintenanceAlert) -> Dict:
        """Generate notification for infotainment system"""
        notification = {
            'notification_id': f"NOTIF_{alert.alert_id}",
            'vehicle_id': alert.vehicle_id,
            'type': 'maintenance_alert',
            'display_type': 'popup' if alert.severity in ['critical', 'high'] else 'banner',
            'title': alert.title,
            'message': alert.message,
            'actions': [
                {
                    'label': 'Schedule Service',
                    'action': 'schedule_appointment',
                    'data': {'alert_id': alert.alert_id}
                },
                {
                    'label': 'View Details', 
                    'action': 'view_alert_details',
                    'data': {'alert_id': alert.alert_id}
                }
            ],
            'estimated_cost': alert.estimated_cost,
            'urgency_days': alert.urgency_days,
            'created_at': alert.created_at,
            'expires_at': alert.expires_at
        }
        
        self.service_stats['notifications_sent'] += 1
        return notification
    
    def generate_web_portal_notification(self, alert: MaintenanceAlert, 
                                      appointment: ServiceAppointment) -> Dict:
        """Generate notification for web/mobile portal"""
        service_center = self.service_centers.get(appointment.service_center_id, {})
        
        notification = {
            'notification_id': f"WEB_{alert.alert_id}",
            'vehicle_id': alert.vehicle_id,
            'type': 'maintenance_summary',
            'alert_details': asdict(alert),
            'appointment_recommendation': asdict(appointment),
            'service_center_info': {
                'id': appointment.service_center_id,
                'name': service_center.get('name', 'Unknown'),
                'location': service_center.get('location', 'Unknown'),
                'distance_km': service_center.get('distance', 0)
            },
            'next_steps': [
                'Review maintenance recommendations',
                'Schedule appointment at recommended service center',
                'Prepare vehicle for service appointment'
            ],
            'contact_options': [
                {'method': 'phone', 'value': '1-800-SERVICE'},
                {'method': 'email', 'value': 'service@vehicle.com'},
                {'method': 'chat', 'value': 'Live chat available 24/7'}
            ]
        }
        
        return notification
    
    def process_maintenance_predictions(self):
        """Main processing function - generates alerts and notifications"""
        self.logger.info("Processing maintenance predictions...")
        
        # Load latest predictions
        predictions = self.load_latest_predictions()
        
        if not predictions:
            self.logger.warning("No predictions to process")
            return
        
        alerts = []
        appointments = []
        infotainment_notifications = []
        web_notifications = []
        
        # Process each prediction
        for prediction in predictions:
            try:
                # Generate maintenance alert
                alert = self.generate_maintenance_alert(prediction)
                alerts.append(alert)
                
                # Create service appointment recommendation
                appointment = self.create_service_appointment(alert)
                appointments.append(appointment)
                
                # Generate notifications for different interfaces
                infotainment_notif = self.generate_infotainment_notification(alert)
                infotainment_notifications.append(infotainment_notif)
                
                web_notif = self.generate_web_portal_notification(alert, appointment)
                web_notifications.append(web_notif)
                
                self.logger.info(f"Processed {alert.vehicle_id}: {alert.severity} severity, "
                               f"{alert.urgency_days} days until maintenance")
                
            except Exception as e:
                self.logger.error(f"Error processing prediction for {prediction.get('vehicle_id', 'unknown')}: {e}")
        
        # Save all outputs
        self.save_alerts(alerts)
        self.save_appointments(appointments)
        self.save_notifications(infotainment_notifications, 'infotainment')
        self.save_notifications(web_notifications, 'web_portal')
        
        # Generate service summary
        self.generate_service_summary(alerts, appointments)
        
        self.logger.info(f"Processing complete: {len(alerts)} alerts, {len(appointments)} appointments")
    
    def save_alerts(self, alerts: List[MaintenanceAlert]):
        """Save maintenance alerts"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        output_file = f"alerts/maintenance_alerts_{timestamp}.jsonl"
        with open(output_file, 'w') as f:
            for alert in alerts:
                f.write(json.dumps(asdict(alert)) + '\n')
        
        self.logger.info(f"Saved {len(alerts)} alerts to {output_file}")
    
    def save_appointments(self, appointments: List[ServiceAppointment]):
        """Save service appointments"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        output_file = f"appointments/service_appointments_{timestamp}.jsonl"
        with open(output_file, 'w') as f:
            for appointment in appointments:
                f.write(json.dumps(asdict(appointment)) + '\n')
        
        self.logger.info(f"Saved {len(appointments)} appointments to {output_file}")
    
    def save_notifications(self, notifications: List[Dict], platform: str):
        """Save notifications for specific platform"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        output_file = f"notifications/{platform}_notifications_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(notifications, f, indent=2)
        
        self.logger.info(f"Saved {len(notifications)} {platform} notifications to {output_file}")
    
    def generate_service_summary(self, alerts: List[MaintenanceAlert], 
                                appointments: List[ServiceAppointment]):
        """Generate service summary report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Calculate summary statistics
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        total_estimated_cost = 0.0
        
        for alert in alerts:
            severity_counts[alert.severity] += 1
            if alert.estimated_cost:
                total_estimated_cost += alert.estimated_cost
        
        # Service center utilization
        center_bookings = {}
        for appointment in appointments:
            center_id = appointment.service_center_id
            center_bookings[center_id] = center_bookings.get(center_id, 0) + 1
        
        summary = {
            'summary_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vehicles_processed': len(alerts),
            'severity_distribution': severity_counts,
            'financial_summary': {
                'total_estimated_service_cost': round(total_estimated_cost, 2),
                'average_cost_per_vehicle': round(total_estimated_cost / len(alerts) if alerts else 0, 2)
            },
            'service_center_utilization': center_bookings,
            'processing_statistics': self.service_stats,
            'next_actions': [
                'Send notifications to vehicle infotainment systems',
                'Update web/mobile portal with alerts',
                'Schedule appointments with service centers',
                'Monitor vehicle health for changes'
            ]
        }
        
        output_file = f"service_summary_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Generated service summary: {output_file}")

if __name__ == "__main__":
    # Run predictive maintenance service
    service = PredictiveMaintenanceService()
    
    try:
        print("Starting Predictive Maintenance Service...")
        print("This service processes ML predictions and generates:")
        print("  1. Maintenance alerts for drivers")
        print("  2. Service appointment recommendations") 
        print("  3. Infotainment system notifications")
        print("  4. Web/mobile portal notifications")
        print()
        
        # Process predictions
        service.process_maintenance_predictions()
        
        print("\n=== SERVICE PROCESSING COMPLETE ===")
        print("Generated outputs:")
        print("  - alerts/: Maintenance alerts for vehicles")
        print("  - appointments/: Service appointment recommendations")
        print("  - notifications/: Platform-specific notifications")
        print("  - service_summary_*.json: Overall service summary")
        
    except Exception as e:
        print(f"Service processing failed: {e}")
        import traceback
        traceback.print_exc()
