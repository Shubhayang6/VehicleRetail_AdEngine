import React, { useState, useEffect } from 'react';

const Dashboard = ({ vehicleData }) => {
  const [liveData, setLiveData] = useState({
    speed: 0,
    rpm: 0,
    temperature: 72,
    isRunning: false
  });

  // Simulate live telemetry data
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveData(prev => ({
        speed: prev.isRunning ? Math.random() * 60 + 20 : 0,
        rpm: prev.isRunning ? Math.random() * 2000 + 1000 : 0,
        temperature: 70 + Math.random() * 10,
        isRunning: Math.random() > 0.7 ? !prev.isRunning : prev.isRunning
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getHealthColor = (value) => {
    if (value >= 90) return '#00ff88';
    if (value >= 70) return '#ffa502';
    return '#ff4757';
  };

  if (!vehicleData) {
    return <div className="loading">Loading vehicle data...</div>;
  }

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="dashboard-header">
        <h1 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '5px', color: '#fff' }}>
          {vehicleData.vehicle.year} {vehicleData.vehicle.make} {vehicleData.vehicle.model}
        </h1>
        <p style={{ color: '#888', fontSize: '14px' }}>
          📍 {vehicleData.vehicle.location}
        </p>
      </div>

      {/* Vehicle Status Card */}
      <div className="vehicle-status">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#fff' }}>Vehicle Status</h2>
          <div style={{ 
            background: liveData.isRunning ? '#00ff88' : '#666', 
            width: '12px', 
            height: '12px', 
            borderRadius: '50%',
            animation: liveData.isRunning ? 'pulse 2s infinite' : 'none'
          }}></div>
        </div>

        <div className="status-grid">
          <div className="status-item">
            <div className="status-value">{Math.round(liveData.speed)}</div>
            <div className="status-label">
              ⚡ Speed (mph)
            </div>
          </div>
          
          <div className="status-item">
            <div className="status-value">{Math.round(liveData.rpm)}</div>
            <div className="status-label">
              📈 RPM
            </div>
          </div>
          
          <div className="status-item">
            <div className="status-value">{vehicleData.vehicle.fuelLevel}%</div>
            <div className="status-label">
              ⛽ Fuel Level
            </div>
          </div>
          
          <div className="status-item">
            <div className="status-value">{Math.round(liveData.temperature)}°F</div>
            <div className="status-label">
              🌡️ Engine Temp
            </div>
          </div>
        </div>
      </div>

      {/* Health Status */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">System Health</h3>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '16px' }}>🔋</span>
              <span style={{ color: '#fff' }}>Battery Health</span>
            </div>
            <span style={{ color: getHealthColor(vehicleData.vehicle.batteryHealth), fontWeight: '600' }}>
              {vehicleData.vehicle.batteryHealth}%
            </span>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '16px' }}>🚗</span>
              <span style={{ color: '#fff' }}>Engine Health</span>
            </div>
            <span style={{ color: getHealthColor(vehicleData.vehicle.engineHealth), fontWeight: '600' }}>
              {vehicleData.vehicle.engineHealth}%
            </span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Activity</h3>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
            <span style={{ color: '#888' }}>Total Mileage</span>
            <span style={{ color: '#fff' }}>{vehicleData.vehicle.mileage.toLocaleString()} mi</span>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
            <span style={{ color: '#888' }}>Last Service</span>
            <span style={{ color: '#fff' }}>{new Date(vehicleData.vehicle.lastService).toLocaleDateString()}</span>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
            <span style={{ color: '#888' }}>Next Service</span>
            <span style={{ color: '#ffa502' }}>
              📅 Sep 15, 2025
            </span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Quick Actions</h3>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <button 
            className="btn btn-secondary" 
            style={{ fontSize: '12px', padding: '10px' }}
            onClick={() => alert('🚗 Remote start activated!')}
          >
            ⚡ Remote Start
          </button>
          
          <button 
            className="btn btn-secondary" 
            style={{ fontSize: '12px', padding: '10px' }}
            onClick={() => alert('📍 Vehicle located at Downtown Seattle')}
          >
            📍 Find Vehicle
          </button>
        </div>
      </div>

      {/* AI Insights */}
      <div className="card" style={{ marginBottom: '100px' }}>
        <div className="card-header">
          <h3 className="card-title">AI Insights</h3>
        </div>
        
        <div style={{ fontSize: '14px', lineHeight: '1.5', color: '#ccc' }}>
          <p style={{ marginBottom: '10px' }}>
            🤖 Based on your driving patterns, we recommend scheduling an oil change within the next 2 weeks.
          </p>
          <p style={{ marginBottom: '10px' }}>
            📊 Your fuel efficiency has improved by 12% this month compared to last month.
          </p>
          <p>
            🛡️ No anomalies detected in your vehicle's performance. All systems operating normally.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
