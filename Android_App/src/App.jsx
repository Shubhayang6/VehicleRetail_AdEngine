import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AndroidFrame from './components/AndroidFrame';
import Dashboard from './pages/Dashboard';
import MaintenanceSimple from './pages/MaintenanceSimple';
import ShoppingSimple from './pages/ShoppingSimple';
import ProfileSimple from './pages/ProfileSimple';
import './index.css';

function App() {
  const [vehicleData, setVehicleData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulate loading vehicle data from our backend
  useEffect(() => {
    const loadVehicleData = async () => {
      try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Mock data based on our actual backend data
        const mockData = {
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
          },
          maintenance: {
            nextService: "2025-09-15",
            alerts: [
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
            ]
          },
          recommendations: [
            {
              id: 1,
              name: "Mobil 1 Synthetic Oil",
              price: 29.99,
              category: "Maintenance",
              rating: 4.8,
              image: "🛢️"
            },
            {
              id: 2,
              name: "Michelin Tires",
              price: 145.00,
              category: "Tires",
              rating: 4.9,
              image: "🛞"
            },
            {
              id: 3,
              name: "Emergency Kit",
              price: 49.99,
              category: "Safety",
              rating: 4.7,
              image: "🚨"
            },
            {
              id: 4,
              name: "Phone Mount",
              price: 24.99,
              category: "Accessories",
              rating: 4.6,
              image: "📱"
            }
          ]
        };
        
        setVehicleData(mockData);
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
      <div className="android-frame">
        <div className="android-screen">
          <div className="loading">
            <div className="loading-spinner"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <AndroidFrame>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard vehicleData={vehicleData} />} />
          <Route path="/maintenance" element={<MaintenanceSimple vehicleData={vehicleData} />} />
          <Route path="/shopping" element={<ShoppingSimple vehicleData={vehicleData} />} />
          <Route path="/profile" element={<ProfileSimple vehicleData={vehicleData} />} />
        </Routes>
      </AndroidFrame>
    </Router>
  );
}

export default App;
