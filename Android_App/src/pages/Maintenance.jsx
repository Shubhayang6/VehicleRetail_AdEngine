import React, { useState } from 'react';

const Maintenance = ({ vehicleData }) => {
  const [selectedAlert, setSelectedAlert] = useState(null);

  const mockAlerts = [
    {
      id: 1,
      type: "Oil Change",
      priority: "medium",
      dueDate: "2025-09-15",
      description: "Oil change recommended based on driving patterns"
    },
    {
      id: 2,
      type: "Tire Rotation", 
      priority: "low",
      dueDate: "2025-10-01",
      description: "Regular tire rotation for even wear"
    }
  ];

  const mockAppointments = [
    {
      id: 1,
      serviceName: "Premium Auto Care",
      date: "2025-09-15",
      time: "10:00 AM",
      address: "123 Main St, Seattle, WA",
      phone: "(206) 555-0123",
      rating: 4.8,
      estimatedCost: 89.99,
      estimatedTime: "45 mins"
    },
    {
      id: 2,
      serviceName: "QuickLube Express",
      date: "2025-09-16", 
      time: "2:30 PM",
      address: "456 Oak Ave, Seattle, WA",
      phone: "(206) 555-0456",
      rating: 4.5,
      estimatedCost: 59.99,
      estimatedTime: "30 mins"
    }
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ff4757';
      case 'medium': return '#ffa502';
      case 'low': return '#00ff88';
      default: return '#888';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return '🚨';
      case 'medium': return '⚠️';
      case 'low': return '✅';
      default: return '⏰';
    }
  };

  const bookAppointment = (appointment) => {
    alert(`✅ Appointment booked with ${appointment.serviceName} for ${appointment.date} at ${appointment.time}\n\nEstimated cost: $${appointment.estimatedCost}\nDuration: ${appointment.estimatedTime}`);
  };

  if (!vehicleData) {
    return <div className="loading">Loading maintenance data...</div>;
  }

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="dashboard-header">
        <h1 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '5px', color: '#fff' }}>
          Maintenance & Service
        </h1>
        <p style={{ color: '#888', fontSize: '14px' }}>
          AI-powered predictive maintenance
        </p>
      </div>

      {/* Active Alerts */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Active Alerts</h3>
          <span style={{ 
            background: '#ff4757', 
            color: '#fff', 
            padding: '4px 8px', 
            borderRadius: '12px', 
            fontSize: '12px' 
          }}>
            {mockAlerts.length}
          </span>
        </div>

        {mockAlerts.map((alert) => (
          <div 
            key={alert.id} 
            className="card" 
            style={{ 
              margin: '10px 0', 
              cursor: 'pointer',
              border: selectedAlert?.id === alert.id ? '2px solid #00ff88' : '1px solid rgba(255, 255, 255, 0.1)'
            }}
            onClick={() => setSelectedAlert(selectedAlert?.id === alert.id ? null : alert)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <span style={{ fontSize: '20px' }}>{getPriorityIcon(alert.priority)}</span>
                <div>
                  <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '5px', color: '#fff' }}>
                    {alert.type}
                  </h4>
                  <p style={{ fontSize: '14px', color: '#ccc', marginBottom: '8px' }}>
                    {alert.description}
                  </p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <span style={{ fontSize: '14px' }}>📅</span>
                    <span style={{ fontSize: '12px', color: '#888' }}>
                      Due: {new Date(alert.dueDate).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              <span 
                style={{ 
                  fontSize: '12px', 
                  fontWeight: '600', 
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  color: getPriorityColor(alert.priority)
                }}
              >
                {alert.priority}
              </span>
            </div>

            {selectedAlert?.id === alert.id && (
              <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <h5 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '10px', color: '#fff' }}>
                  Recommended Actions:
                </h5>
                <ul style={{ fontSize: '13px', color: '#ccc', paddingLeft: '20px' }}>
                  <li>Schedule service appointment within 2 weeks</li>
                  <li>Use high-quality synthetic oil (5W-30)</li>
                  <li>Request multi-point inspection</li>
                </ul>
                <button 
                  className="btn" 
                  style={{ marginTop: '10px', width: '100%', fontSize: '12px' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    document.getElementById('appointments')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  Find Service Centers
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* AI Predictions */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">🤖 AI Predictions</h3>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div style={{ 
            background: 'rgba(0, 255, 136, 0.1)', 
            border: '1px solid rgba(0, 255, 136, 0.3)',
            borderRadius: '12px',
            padding: '15px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span style={{ fontSize: '16px' }}>🔧</span>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#fff' }}>Brake Prediction</span>
            </div>
            <p style={{ fontSize: '13px', color: '#ccc' }}>
              Based on your driving patterns, brake pads have 85% life remaining. 
              Estimated replacement needed in 6-8 months.
            </p>
          </div>

          <div style={{ 
            background: 'rgba(255, 165, 2, 0.1)', 
            border: '1px solid rgba(255, 165, 2, 0.3)',
            borderRadius: '12px',
            padding: '15px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span style={{ fontSize: '16px' }}>⚠️</span>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#fff' }}>Transmission Alert</span>
            </div>
            <p style={{ fontSize: '13px', color: '#ccc' }}>
              Minor increase in shift response time detected. 
              Monitor for next 500 miles. No immediate action needed.
            </p>
          </div>
        </div>
      </div>

      {/* Service Centers */}
      <div id="appointments" className="card">
        <div className="card-header">
          <h3 className="card-title">Nearby Service Centers</h3>
        </div>

        {mockAppointments.map((appointment) => (
          <div 
            key={appointment.id}
            style={{ 
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: '12px',
              padding: '15px',
              margin: '10px 0',
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
              <div>
                <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '5px', color: '#fff' }}>
                  {appointment.serviceName}
                </h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '5px' }}>
                  <span style={{ fontSize: '14px' }}>⭐</span>
                  <span style={{ fontSize: '13px', color: '#ccc' }}>
                    {appointment.rating} rating
                  </span>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#00ff88' }}>
                  ${appointment.estimatedCost}
                </div>
                <div style={{ fontSize: '12px', color: '#888' }}>
                  {appointment.estimatedTime}
                </div>
              </div>
            </div>

            <div style={{ fontSize: '13px', color: '#ccc', marginBottom: '10px' }}>
              <div style={{ marginBottom: '3px' }}>
                📍 {appointment.address}
              </div>
              <div style={{ marginBottom: '3px' }}>
                📞 {appointment.phone}
              </div>
              <div>
                📅 Available: {appointment.date} at {appointment.time}
              </div>
            </div>

            <button 
              className="btn" 
              style={{ width: '100%', fontSize: '12px' }}
              onClick={() => bookAppointment(appointment)}
            >
              Book Appointment
            </button>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: '100px' }}></div>
    </div>
  );
};

export default Maintenance;
