import React, { useState } from 'react';

const InfotainmentFrame = ({ vehicleData }) => {
  const [activeTab, setActiveTab] = useState('navigation');
  const [climateSettings, setClimateSettings] = useState({
    temperature: vehicleData?.climate?.temperature || 72,
    fanSpeed: vehicleData?.climate?.fanSpeed || 3,
    acOn: vehicleData?.climate?.acOn || true,
    heatedSeats: vehicleData?.climate?.heatedSeats || false
  });

  const handleAdClick = (ad) => {
    alert(`Opening: ${ad.title}\n${ad.description}\nPrice: ${ad.price}`);
  };

  const toggleClimate = (setting) => {
    setClimateSettings(prev => ({
      ...prev,
      [setting]: !prev[setting]
    }));
  };

  const adjustTemperature = (increment) => {
    setClimateSettings(prev => ({
      ...prev,
      temperature: Math.max(60, Math.min(85, prev.temperature + increment))
    }));
  };

  if (!vehicleData) {
    return (
      <div className="infotainment-frame">
        <div className="infotainment-screen">
          <div className="loading">
            <div className="loading-spinner"></div>
            Loading vehicle data...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="infotainment-frame">
      <div className="infotainment-screen">
        {/* Header Bar */}
        <div className="header-bar">
          <div className="vehicle-info">
            <div className="vehicle-logo">🚗</div>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: '600' }}>
                {vehicleData.vehicle.year} {vehicleData.vehicle.make} {vehicleData.vehicle.model}
              </h2>
              <p style={{ fontSize: '12px', color: '#888' }}>
                {vehicleData.telematics.status} • {vehicleData.vehicle.location}
              </p>
            </div>
          </div>
          
          <div className="system-status">
            <div className="status-item">
              <div className="status-indicator"></div>
              <span>GPS Connected</span>
            </div>
            <div className="status-item">
              <div className="status-indicator"></div>
              <span>Engine Online</span>
            </div>
            <div className="status-item">
              <div className="status-indicator"></div>
              <span>Bluetooth</span>
            </div>
            <div style={{ fontSize: '16px', fontWeight: '600' }}>
              {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </div>

        {/* Left Panel - Vehicle Status */}
        <div className="left-panel">
          <h3 className="panel-title">Vehicle Status</h3>
          
          <div className="gauge-container">
            <div className="gauge">
              <div className="gauge-circle">
                <div className="gauge-value">{Math.round(vehicleData.telematics.speed)}</div>
              </div>
              <div className="gauge-label">MPH</div>
            </div>
            
            <div className="gauge">
              <div className="gauge-circle" style={{
                background: `conic-gradient(from 0deg, #ffa502 0deg ${(vehicleData.telematics.rpm / 6000) * 360}deg, rgba(255, 255, 255, 0.1) ${(vehicleData.telematics.rpm / 6000) * 360}deg 360deg)`
              }}>
                <div className="gauge-value">{Math.round(vehicleData.telematics.rpm)}</div>
              </div>
              <div className="gauge-label">RPM</div>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '14px', color: '#888' }}>Fuel Level</span>
              <span style={{ fontWeight: '600', color: '#00ff88' }}>{Math.round(vehicleData.vehicle.fuelLevel)}%</span>
            </div>
            <div style={{ 
              width: '100%', 
              height: '8px', 
              background: 'rgba(255, 255, 255, 0.1)', 
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${vehicleData.vehicle.fuelLevel}%`,
                height: '100%',
                background: vehicleData.vehicle.fuelLevel > 25 ? '#00ff88' : '#ff4757',
                transition: 'width 0.3s ease'
              }}></div>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '14px', color: '#888' }}>Battery Health</span>
              <span style={{ fontWeight: '600', color: '#00ff88' }}>{vehicleData.vehicle.batteryHealth}%</span>
            </div>
            <div style={{ 
              width: '100%', 
              height: '8px', 
              background: 'rgba(255, 255, 255, 0.1)', 
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${vehicleData.vehicle.batteryHealth}%`,
                height: '100%',
                background: '#00ff88',
                transition: 'width 0.3s ease'
              }}></div>
            </div>
          </div>

          <div style={{ textAlign: 'center', padding: '15px', background: 'rgba(0, 255, 136, 0.1)', borderRadius: '8px' }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#00ff88' }}>
              {vehicleData.telematics.fuelEfficiency.toFixed(1)} MPG
            </div>
            <div style={{ fontSize: '12px', color: '#888' }}>Current Efficiency</div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="main-content">
          <div className="content-tabs">
            <button 
              className={`tab-button ${activeTab === 'navigation' ? 'active' : ''}`}
              onClick={() => setActiveTab('navigation')}
            >
              🗺️ Navigation
            </button>
            <button 
              className={`tab-button ${activeTab === 'media' ? 'active' : ''}`}
              onClick={() => setActiveTab('media')}
            >
              🎵 Media
            </button>
            <button 
              className={`tab-button ${activeTab === 'vehicle' ? 'active' : ''}`}
              onClick={() => setActiveTab('vehicle')}
            >
              🚗 Vehicle
            </button>
            <button 
              className={`tab-button ${activeTab === 'apps' ? 'active' : ''}`}
              onClick={() => setActiveTab('apps')}
            >
              📱 Apps
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'navigation' && (
              <div className="navigation-view slide-in">
                <div className="map-display">
                  <div style={{ textAlign: 'center', color: '#fff' }}>
                    <div style={{ fontSize: '48px', marginBottom: '10px' }}>🗺️</div>
                    <div style={{ fontSize: '16px', fontWeight: '600' }}>
                      Route to {vehicleData.navigation.destination}
                    </div>
                    <div style={{ fontSize: '14px', opacity: '0.8' }}>
                      Via {vehicleData.navigation.route}
                    </div>
                  </div>
                </div>
                
                <div className="route-info">
                  <h4 style={{ fontSize: '16px', marginBottom: '15px', color: '#00ff88' }}>Route Information</h4>
                  <div className="route-item">
                    <span>🎯 Destination</span>
                    <span>{vehicleData.navigation.destination}</span>
                  </div>
                  <div className="route-item">
                    <span>⏱️ ETA</span>
                    <span style={{ color: '#00ff88' }}>{vehicleData.navigation.eta}</span>
                  </div>
                  <div className="route-item">
                    <span>📍 Distance</span>
                    <span>{vehicleData.navigation.distance}</span>
                  </div>
                  <div className="route-item">
                    <span>🛣️ Next Turn</span>
                    <span style={{ color: '#ffa502' }}>{vehicleData.navigation.nextTurn}</span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'media' && (
              <div className="media-view slide-in">
                <div className="now-playing">
                  <div className="album-art">🎵</div>
                  <div className="song-info">
                    <h3>{vehicleData.media.currentTrack}</h3>
                    <p>{vehicleData.media.artist}</p>
                    <p style={{ fontSize: '12px', color: '#666' }}>{vehicleData.media.album}</p>
                  </div>
                </div>

                <div className="media-controls">
                  <button className="control-btn">⏮️</button>
                  <button className="control-btn" style={{ background: vehicleData.media.isPlaying ? 'rgba(255, 71, 87, 0.2)' : 'rgba(0, 255, 136, 0.2)' }}>
                    {vehicleData.media.isPlaying ? '⏸️' : '▶️'}
                  </button>
                  <button className="control-btn">⏭️</button>
                </div>

                <div style={{ marginTop: '30px', textAlign: 'center' }}>
                  <div style={{ marginBottom: '10px', fontSize: '14px', color: '#888' }}>
                    Volume: {vehicleData.media.volume}%
                  </div>
                  <div style={{ 
                    width: '200px', 
                    height: '8px', 
                    background: 'rgba(255, 255, 255, 0.1)', 
                    borderRadius: '4px',
                    margin: '0 auto',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: `${vehicleData.media.volume}%`,
                      height: '100%',
                      background: '#00ff88',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'vehicle' && (
              <div className="slide-in" style={{ padding: '20px' }}>
                <h4 style={{ fontSize: '18px', marginBottom: '20px', color: '#00ff88' }}>Vehicle Diagnostics</h4>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
                  <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '15px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '14px', color: '#888', marginBottom: '5px' }}>Engine Temperature</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#00ff88' }}>
                      {vehicleData.telematics.engineTemp}°F
                    </div>
                  </div>
                  
                  <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '15px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '14px', color: '#888', marginBottom: '5px' }}>Tire Pressure</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#00ff88' }}>
                      {vehicleData.telematics.pressure} PSI
                    </div>
                  </div>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '20px', borderRadius: '12px' }}>
                  <h5 style={{ fontSize: '16px', marginBottom: '15px', color: '#fff' }}>System Status</h5>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>🔧 Engine Health</span>
                      <span style={{ color: '#00ff88' }}>{vehicleData.vehicle.engineHealth}%</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>🔋 Battery Health</span>
                      <span style={{ color: '#00ff88' }}>{vehicleData.vehicle.batteryHealth}%</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>⛽ Fuel Level</span>
                      <span style={{ color: vehicleData.vehicle.fuelLevel > 25 ? '#00ff88' : '#ff4757' }}>
                        {Math.round(vehicleData.vehicle.fuelLevel)}%
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>🛞 Tire Condition</span>
                      <span style={{ color: '#00ff88' }}>Good</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'apps' && (
              <div className="slide-in" style={{ padding: '20px' }}>
                <h4 style={{ fontSize: '18px', marginBottom: '20px', color: '#00ff88' }}>Connected Apps</h4>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '20px' }}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    <div style={{ fontSize: '32px', marginBottom: '10px' }}>☕</div>
                    <div style={{ fontSize: '14px', fontWeight: '600' }}>Starbucks</div>
                    <div style={{ fontSize: '12px', color: '#888' }}>Order ahead</div>
                  </div>
                  
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    <div style={{ fontSize: '32px', marginBottom: '10px' }}>⛽</div>
                    <div style={{ fontSize: '14px', fontWeight: '600' }}>Shell</div>
                    <div style={{ fontSize: '12px', color: '#888' }}>Pay at pump</div>
                  </div>
                  
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    <div style={{ fontSize: '32px', marginBottom: '10px' }}>🛒</div>
                    <div style={{ fontSize: '14px', fontWeight: '600' }}>AutoZone</div>
                    <div style={{ fontSize: '12px', color: '#888' }}>Shop parts</div>
                  </div>
                  
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    <div style={{ fontSize: '32px', marginBottom: '10px' }}>🏠</div>
                    <div style={{ fontSize: '14px', fontWeight: '600' }}>Home</div>
                    <div style={{ fontSize: '12px', color: '#888' }}>Smart control</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Advertisements */}
        <div className="right-panel">
          <h3 className="panel-title">Smart Recommendations</h3>
          
          <div className="ad-container">
            {vehicleData.ads.map(ad => (
              <div 
                key={ad.id}
                className={`ad-banner ${ad.category}`}
                onClick={() => handleAdClick(ad)}
                style={{
                  border: ad.urgent ? '2px solid #ff4757' : '1px solid rgba(255, 255, 255, 0.2)'
                }}
              >
                {ad.urgent && (
                  <div style={{ 
                    position: 'absolute', 
                    top: '-8px', 
                    right: '-8px', 
                    background: '#ff4757', 
                    borderRadius: '50%', 
                    width: '16px', 
                    height: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '10px'
                  }}>!</div>
                )}
                <div className="ad-title">{ad.title}</div>
                <div className="ad-description">{ad.description}</div>
                <div className="ad-price">{ad.price}</div>
              </div>
            ))}
          </div>

          <div style={{ 
            background: 'rgba(0, 255, 136, 0.1)', 
            borderRadius: '8px', 
            padding: '15px', 
            textAlign: 'center',
            border: '1px solid rgba(0, 255, 136, 0.3)'
          }}>
            <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '5px' }}>AI Assistant</div>
            <div style={{ fontSize: '12px', color: '#888', marginBottom: '10px' }}>
              "Based on your driving, I recommend checking your oil soon."
            </div>
            <button style={{
              background: '#00ff88',
              color: '#000',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: '600',
              cursor: 'pointer'
            }}>
              Ask AI
            </button>
          </div>
        </div>

        {/* Bottom Controls */}
        <div className="bottom-controls">
          <div className="climate-controls">
            <div className="climate-item">
              <button 
                className="control-btn"
                onClick={() => adjustTemperature(-1)}
                style={{ width: '40px', height: '40px', fontSize: '16px' }}
              >
                ❄️
              </button>
              <div className="climate-value">{climateSettings.temperature}°F</div>
              <div className="climate-label">Temperature</div>
            </div>
            
            <div className="climate-item">
              <button 
                className="control-btn"
                onClick={() => adjustTemperature(1)}
                style={{ width: '40px', height: '40px', fontSize: '16px' }}
              >
                🔥
              </button>
              <div className="climate-value">Fan {climateSettings.fanSpeed}</div>
              <div className="climate-label">Fan Speed</div>
            </div>
          </div>

          <div className="quick-actions">
            <button 
              className={`action-btn ${climateSettings.acOn ? 'active' : ''}`}
              onClick={() => toggleClimate('acOn')}
              title="Air Conditioning"
            >
              ❄️
            </button>
            <button 
              className={`action-btn ${climateSettings.heatedSeats ? 'active' : ''}`}
              onClick={() => toggleClimate('heatedSeats')}
              title="Heated Seats"
            >
              🔥
            </button>
            <button className="action-btn" title="Door Lock">
              🔒
            </button>
            <button className="action-btn" title="Emergency">
              🚨
            </button>
            <button className="action-btn" title="Phone">
              📞
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfotainmentFrame;
