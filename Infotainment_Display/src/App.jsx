import React, { useState, useEffect } from 'react';
import InfotainmentFrame from './components/InfotainmentFrame';
import './index.css';

function App() {
  const [vehicleData, setVehicleData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulate loading vehicle data from backend
  useEffect(() => {
    const loadVehicleData = async () => {
      try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
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
            speed: 65,
            rpm: 2200,
            temperature: 72,
            pressure: 32,
            status: "Driving",
            fuelEfficiency: 28.5,
            engineTemp: 195
          },
          navigation: {
            destination: "Bellevue Square Mall",
            eta: "15 mins",
            distance: "8.2 miles",
            route: "I-405 North",
            nextTurn: "Exit 13A in 2.1 miles"
          },
          media: {
            currentTrack: "Blinding Lights",
            artist: "The Weeknd",
            album: "After Hours",
            isPlaying: true,
            volume: 75
          },
          climate: {
            temperature: 72,
            fanSpeed: 3,
            acOn: true,
            heatedSeats: false
          },
          ads: [
            {
              id: 1,
              type: "maintenance",
              title: "Oil Change Due",
              description: "Schedule your next oil change today",
              price: "$29.99",
              urgent: true,
              category: "service"
            },
            {
              id: 2,
              type: "promotion",
              title: "20% Off Tires",
              description: "Premium Michelin tires on sale",
              price: "Save $60",
              urgent: false,
              category: "promotion"
            },
            {
              id: 3,
              type: "location",
              title: "Starbucks Nearby",
              description: "Get your coffee fix - 0.3 miles",
              price: "Order ahead",
              urgent: false,
              category: "location"
            },
            {
              id: 4,
              type: "service",
              title: "Tire Pressure Check",
              description: "Free inspection at QuickLube",
              price: "Free",
              urgent: false,
              category: "service"
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

    // Simulate real-time data updates
    const interval = setInterval(() => {
      setVehicleData(prevData => {
        if (!prevData) return prevData;
        
        return {
          ...prevData,
          telematics: {
            ...prevData.telematics,
            speed: Math.max(0, prevData.telematics.speed + (Math.random() - 0.5) * 10),
            rpm: Math.max(800, prevData.telematics.rpm + (Math.random() - 0.5) * 400),
            fuelEfficiency: Math.max(15, Math.min(35, prevData.telematics.fuelEfficiency + (Math.random() - 0.5) * 2))
          },
          vehicle: {
            ...prevData.vehicle,
            fuelLevel: Math.max(0, Math.min(100, prevData.vehicle.fuelLevel - Math.random() * 0.1))
          }
        };
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="infotainment-frame">
        <div className="infotainment-screen">
          <div className="loading">
            <div className="loading-spinner"></div>
            Initializing Vehicle Systems...
          </div>
        </div>
      </div>
    );
  }

  return <InfotainmentFrame vehicleData={vehicleData} />;
}

export default App;
