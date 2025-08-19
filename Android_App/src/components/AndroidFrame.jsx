import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const AndroidFrame = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [currentTime] = useState(() => {
    return new Date().toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  });

  const navItems = [
    { path: '/dashboard', icon: '🚗', label: 'Vehicle' },
    { path: '/maintenance', icon: '🔧', label: 'Service' },
    { path: '/shopping', icon: '🛒', label: 'Shop' },
    { path: '/profile', icon: '👤', label: 'Profile' }
  ];

  return (
    <div className="android-frame">
      <div className="android-screen">
        {/* Status Bar */}
        <div className="status-bar">
          <div className="time">{currentTime}</div>
          <div className="battery-status">
            <span>📶 📶 🔋 85%</span>
          </div>
        </div>

        {/* Page Content */}
        <div className="page-content">
          {children}
        </div>

        {/* Bottom Navigation */}
        <div className="bottom-nav">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            
            return (
              <div
                key={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '8px',
                  borderRadius: '12px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  color: isActive ? '#00ff88' : '#666',
                  background: isActive ? 'rgba(0, 255, 136, 0.1)' : 'transparent'
                }}
              >
                <span style={{ fontSize: '20px' }}>{item.icon}</span>
                <span style={{ fontSize: '10px', fontWeight: '500' }}>{item.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AndroidFrame;
