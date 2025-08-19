import React, { useState } from 'react';

const Profile = ({ vehicleData }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const userProfile = {
    name: "Alex Johnson",
    email: "alex.johnson@email.com",
    phone: "+1 (206) 555-0123",
    memberSince: "2023-01-15",
    loyaltyPoints: 2450,
    totalOrders: 12,
    totalSpent: 1247.65,
    preferredPayment: "**** 4892"
  };

  const recentOrders = [
    {
      id: "ORD-2025-001",
      date: "2025-08-15",
      items: ["Mobil 1 Synthetic Oil", "Air Filter"],
      total: 89.99,
      status: "Delivered"
    },
    {
      id: "ORD-2025-002", 
      date: "2025-07-20",
      items: ["Emergency Kit", "Phone Mount"],
      total: 74.98,
      status: "Delivered"
    }
  ];

  const drivingStats = {
    totalMiles: vehicleData?.vehicle?.mileage || 45672,
    avgMPG: 28.5,
    ecoScore: 85,
    safetyScore: 92
  };

  const achievements = [
    { icon: "🌱", title: "Eco Driver", description: "Maintained 25+ MPG for 3 months" },
    { icon: "🛡️", title: "Safety First", description: "No incidents for 12 months" },
    { icon: "⚡", title: "Tech Savvy", description: "Connected all smart features" },
    { icon: "🏆", title: "Loyal Customer", description: "Member for 2+ years" }
  ];

  if (!vehicleData) {
    return <div className="loading">Loading profile...</div>;
  }

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="dashboard-header">
        <h1 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '5px', color: '#fff' }}>
          My Profile
        </h1>
        <p style={{ color: '#888', fontSize: '14px' }}>
          Account settings and preferences
        </p>
      </div>

      {/* Profile Card */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
            fontWeight: '600',
            color: '#fff'
          }}>
            AJ
          </div>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '5px', color: '#fff' }}>
              {userProfile.name}
            </h3>
            <p style={{ color: '#888', fontSize: '14px' }}>
              Member since {new Date(userProfile.memberSince).toLocaleDateString()}
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginTop: '5px' }}>
              <span style={{ fontSize: '14px' }}>🏆</span>
              <span style={{ fontSize: '12px', color: '#ffa502' }}>
                {userProfile.loyaltyPoints} Loyalty Points
              </span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{ 
          display: 'flex', 
          gap: '10px', 
          marginBottom: '20px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          paddingBottom: '10px'
        }}>
          {[
            { key: 'overview', label: 'Overview', icon: '📊' },
            { key: 'vehicle', label: 'Vehicle', icon: '🚗' },
            { key: 'orders', label: 'Orders', icon: '💳' },
            { key: 'settings', label: 'Settings', icon: '⚙️' }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                background: activeTab === tab.key ? 'rgba(0, 255, 136, 0.1)' : 'transparent',
                color: activeTab === tab.key ? '#00ff88' : '#888',
                border: 'none',
                padding: '8px 12px',
                borderRadius: '8px',
                fontSize: '12px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.3s ease'
              }}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div>
            {/* Stats Grid */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr', 
              gap: '15px', 
              marginBottom: '20px' 
            }}>
              <div style={{
                background: 'rgba(0, 255, 136, 0.1)',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                borderRadius: '12px',
                padding: '15px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#00ff88', marginBottom: '5px' }}>
                  {userProfile.totalOrders}
                </div>
                <div style={{ fontSize: '12px', color: '#888' }}>Total Orders</div>
              </div>

              <div style={{
                background: 'rgba(255, 165, 2, 0.1)',
                border: '1px solid rgba(255, 165, 2, 0.3)',
                borderRadius: '12px',
                padding: '15px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#ffa502', marginBottom: '5px' }}>
                  ${userProfile.totalSpent}
                </div>
                <div style={{ fontSize: '12px', color: '#888' }}>Total Spent</div>
              </div>
            </div>

            {/* Driving Statistics */}
            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: '#fff' }}>
              Driving Statistics
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: '#888' }}>Total Miles</span>
                <span style={{ fontWeight: '600', color: '#fff' }}>{drivingStats.totalMiles.toLocaleString()}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: '#888' }}>Average MPG</span>
                <span style={{ fontWeight: '600', color: '#00ff88' }}>{drivingStats.avgMPG}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: '#888' }}>Eco Score</span>
                <span style={{ fontWeight: '600', color: '#00ff88' }}>{drivingStats.ecoScore}/100</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: '#888' }}>Safety Score</span>
                <span style={{ fontWeight: '600', color: '#00ff88' }}>{drivingStats.safetyScore}/100</span>
              </div>
            </div>

            {/* Achievements */}
            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: '#fff' }}>
              Achievements
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              {achievements.map((achievement, index) => (
                <div key={index} style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  padding: '10px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '20px', marginBottom: '5px' }}>{achievement.icon}</div>
                  <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '3px', color: '#fff' }}>
                    {achievement.title}
                  </div>
                  <div style={{ fontSize: '10px', color: '#888' }}>
                    {achievement.description}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'vehicle' && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
              <div style={{
                width: '50px',
                height: '50px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px'
              }}>
                🚗
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '5px', color: '#fff' }}>
                  {vehicleData.vehicle.year} {vehicleData.vehicle.make} {vehicleData.vehicle.model}
                </h3>
                <p style={{ fontSize: '12px', color: '#888' }}>
                  VIN: {vehicleData.vehicle.vin}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '14px', color: '#888' }}>Mileage</span>
                <span style={{ color: '#fff' }}>{vehicleData.vehicle.mileage.toLocaleString()} miles</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '14px', color: '#888' }}>Battery Health</span>
                <span style={{ color: '#00ff88' }}>{vehicleData.vehicle.batteryHealth}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '14px', color: '#888' }}>Engine Health</span>
                <span style={{ color: '#ffa502' }}>{vehicleData.vehicle.engineHealth}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '14px', color: '#888' }}>Last Service</span>
                <span style={{ color: '#fff' }}>{new Date(vehicleData.vehicle.lastService).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'orders' && (
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: '#fff' }}>
              Recent Orders
            </h4>
            {recentOrders.map(order => (
              <div key={order.id} style={{
                background: 'rgba(255, 255, 255, 0.03)',
                borderRadius: '8px',
                padding: '15px',
                marginBottom: '10px',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '600', color: '#fff' }}>{order.id}</span>
                  <span style={{ fontSize: '12px', color: order.status === 'Delivered' ? '#00ff88' : '#ffa502' }}>
                    {order.status}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: '#888', marginBottom: '5px' }}>
                  {new Date(order.date).toLocaleDateString()}
                </div>
                <div style={{ fontSize: '13px', marginBottom: '8px', color: '#ccc' }}>
                  {order.items.join(', ')}
                </div>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#00ff88' }}>
                  ${order.total}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'settings' && (
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: '#fff' }}>
              Contact Information
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span>📧</span>
                <span style={{ fontSize: '14px', color: '#fff' }}>{userProfile.email}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span>📞</span>
                <span style={{ fontSize: '14px', color: '#fff' }}>{userProfile.phone}</span>
              </div>
            </div>

            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: '#fff' }}>
              Payment Method
            </h4>
            <div style={{
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '8px',
              padding: '15px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}>
              <span style={{ fontSize: '20px' }}>💳</span>
              <div>
                <div style={{ fontSize: '14px', fontWeight: '500', color: '#fff' }}>
                  Credit Card {userProfile.preferredPayment}
                </div>
                <div style={{ fontSize: '12px', color: '#888' }}>
                  Expires 12/26
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div style={{ marginBottom: '100px' }}></div>
    </div>
  );
};

export default Profile;
