import React, { useState, useEffect } from 'react';
import './index.css';

// Simple mock data
const mockVehicleData = {
  vehicle: {
    id: "VEHICLE_001",
    make: "Toyota",
    model: "Camry",
    year: 2023,
    vin: "1HGCM82633A123456",
    mileage: 45672,
    fuelLevel: 78,
    batteryHealth: 92,
    engineHealth: 85,
    location: "Downtown Seattle",
    lastService: "2025-07-15"
  },
  telematics: {
    speed: 0,
    rpm: 0,
    temperature: 72,
    pressure: 32,
    status: "Parked"
  }
};

// Simple Android Frame Component
const SimpleAndroidFrame = ({ children }) => {
  return (
    <div className="android-frame">
      <div className="android-screen">
        {/* Status Bar */}
        <div className="status-bar">
          <div className="time">{new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })}</div>
          <div className="battery-status">
            <span>📶 📶 🔋 85%</span>
          </div>
        </div>

        {/* Page Content */}
        <div className="page-content">
          {children}
        </div>
      </div>
    </div>
  );
};

// Simple Dashboard Component
const SimpleDashboard = ({ vehicleData }) => {
  const [liveData, setLiveData] = useState({
    speed: 0,
    rpm: 0,
    temperature: 72,
    isRunning: false
  });

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
            <div className="status-label">Speed (mph)</div>
          </div>
          
          <div className="status-item">
            <div className="status-value">{Math.round(liveData.rpm)}</div>
            <div className="status-label">RPM</div>
          </div>
          
          <div className="status-item">
            <div className="status-value">{vehicleData.vehicle.fuelLevel}%</div>
            <div className="status-label">Fuel Level</div>
          </div>
          
          <div className="status-item">
            <div className="status-value">{Math.round(liveData.temperature)}°F</div>
            <div className="status-label">Engine Temp</div>
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
            <span style={{ color: '#fff' }}>🔋 Battery Health</span>
            <span style={{ color: '#00ff88', fontWeight: '600' }}>
              {vehicleData.vehicle.batteryHealth}%
            </span>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#fff' }}>🚗 Engine Health</span>
            <span style={{ color: '#ffa502', fontWeight: '600' }}>
              {vehicleData.vehicle.engineHealth}%
            </span>
          </div>
        </div>
      </div>

      {/* Simple Navigation */}
      <div style={{
        position: 'fixed',
        bottom: '10px',
        left: '50%',
        transform: 'translateX(-50%)',
        width: '355px',
        height: '60px',
        background: 'rgba(0, 0, 0, 0.9)',
        borderRadius: '25px',
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <button style={{ background: 'none', border: 'none', color: '#00ff88', fontSize: '24px' }}>🚗</button>
        <button style={{ background: 'none', border: 'none', color: '#666', fontSize: '24px' }}>🔧</button>
        <button style={{ background: 'none', border: 'none', color: '#666', fontSize: '24px' }}>🛒</button>
        <button style={{ background: 'none', border: 'none', color: '#666', fontSize: '24px' }}>👤</button>
      </div>
    </div>
  );
};

function App() {
  const [vehicleData, setVehicleData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadVehicleData = async () => {
      try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        setVehicleData(mockVehicleData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading vehicle data:', error);
        setLoading(false);
      }
    };

    loadVehicleData();
  }, []);

  if (loading) {
    return (
      <SimpleAndroidFrame>
        <div className="loading">
          <div className="loading-spinner"></div>
          <p style={{ color: '#fff', marginTop: '20px' }}>Loading Vehicle Data...</p>
        </div>
      </SimpleAndroidFrame>
    );
  }

  return (
    <SimpleAndroidFrame>
      <SimpleDashboard vehicleData={vehicleData} />
    </SimpleAndroidFrame>
  );
}

export default App;
