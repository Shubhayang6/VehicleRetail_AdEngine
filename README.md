# Vehicle Retail Ad Engine 🚗

A comprehensive vehicle retail ecosystem with predictive maintenance, contextual advertising, and e-commerce integration. This system demonstrates the future of connected vehicle services through real-time telemetry, AI-powered recommendations, and seamless user experiences.

## 🌟 Overview

This project showcases a complete vehicle retail platform that combines:
- **Real-time vehicle telemetry** and health monitoring
- **AI-powered predictive maintenance** with service scheduling
- **Contextual advertising engine** based on vehicle condition and location
- **Integrated e-commerce platform** for automotive products and services
- **Multi-platform user interfaces** (Mobile app + In-vehicle infotainment)

## 🏗️ Architecture

The system consists of multiple microservices working together:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Vehicle Data   │───▶│  Data Processing │───▶│   ML Pipeline   │
│   Simulation    │    │     Service      │    │   (Predictions) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Mobile App     │◀───│  Ad & Recommendation │◀──│  Maintenance    │
│  (React)        │    │      Engine      │    │    Service      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Infotainment    │◀───│   E-commerce     │◀───│   Service       │
│   Display       │    │      API         │    │   Scheduler     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **PostgreSQL** (optional - using SQLite by default)
- **Apache Kafka** (optional - using mock data by default)

### 1. Clone the Repository

```bash
git clone https://github.com/Shubhayang6/VehicleRetail_AdEngine.git
cd VehicleRetail_AdEngine
```

### 2. Set Up Python Backend Services

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Start Backend Services

#### Start Data Processing Service
```bash
cd DataProcessing_Service
python app.py
# Service will run on http://localhost:5001
```

#### Start ML Pipeline (in new terminal)
```bash
cd ML_Pipeline
python app.py
# Service will run on http://localhost:5002
```

#### Start Predictive Maintenance Service (in new terminal)
```bash
cd PredictiveMaintenance_Service
python app.py
# Service will run on http://localhost:5003
```

#### Start Ad & Recommendation Engine (in new terminal)
```bash
cd Ad_RecommendationEngine
python app.py
# Service will run on http://localhost:5004
```

#### Start E-commerce API (in new terminal)
```bash
cd Ecommerce_API
python app.py
# Service will run on http://localhost:5005
```

### 4. Start Frontend Applications

#### Start Mobile App (in new terminal)
```bash
cd Android_App
npm install
npm run dev
# App will run on http://localhost:3000
```

#### Start Infotainment Display (in new terminal)
```bash
cd Infotainment_Display
npm install
npm run dev
# Display will run on http://localhost:3001
```

### 5. Access the Applications

- **📱 Mobile App**: http://localhost:3000 - Interactive Android-style mobile interface
- **🚗 Infotainment Display**: http://localhost:3001 - Car dashboard simulation with ads
- **🔧 Backend APIs**: Various endpoints on ports 5001-5005

## 📱 User Interfaces

### Mobile App Features
- **Dashboard**: Real-time vehicle telemetry and health monitoring
- **Maintenance**: Service alerts, scheduling, and health tracking
- **Shopping**: E-commerce with AI recommendations and cart functionality
- **Profile**: User analytics, achievements, and account management

### Infotainment Display Features
- **Navigation**: Route planning with contextual location-based ads
- **Media**: Music controls with integrated promotional content
- **Vehicle**: Comprehensive diagnostics and system status
- **Apps**: Connected services and smart recommendations

## 🛠️ API Endpoints

### Data Processing Service (Port 5001)
- `GET /health` - Service health check
- `POST /process` - Process vehicle telemetry data
- `GET /vehicle/{id}/status` - Get current vehicle status

### ML Pipeline (Port 5002)
- `GET /health` - Service health check
- `POST /predict/maintenance` - Predict maintenance needs
- `GET /models/status` - Get ML model status

### Predictive Maintenance (Port 5003)
- `GET /health` - Service health check
- `GET /vehicle/{id}/alerts` - Get maintenance alerts
- `POST /schedule` - Schedule maintenance appointment

### Ad & Recommendation Engine (Port 5004)
- `GET /health` - Service health check
- `GET /ads/contextual` - Get contextual advertisements
- `POST /recommendations` - Get product recommendations

### E-commerce API (Port 5005)
- `GET /health` - Service health check
- `GET /products` - Get product catalog
- `POST /cart/add` - Add items to cart
- `POST /orders` - Place orders

## 📊 Demo Data

The system includes comprehensive mock data for demonstration:

- **Vehicle Telemetry**: Speed, RPM, fuel level, battery health, engine temperature
- **Maintenance Alerts**: Oil change, tire rotation, brake inspection notifications
- **Product Catalog**: Automotive parts, accessories, and services (6 categories)
- **User Profiles**: Driving statistics, purchase history, loyalty points
- **Contextual Ads**: Location-based, condition-based, and promotional content

## 🧪 Testing the System

### 1. End-to-End User Journey Test
1. Open mobile app (localhost:3000)
2. Navigate through all tabs to see real-time data
3. Add items to shopping cart and complete checkout
4. Open infotainment display (localhost:3001)
5. Click on contextual ads to see integration

### 2. Backend API Testing
```bash
# Test data processing
curl http://localhost:5001/health

# Test ML predictions
curl http://localhost:5002/predict/maintenance

# Test maintenance alerts
curl http://localhost:5003/vehicle/VEHICLE_001/alerts

# Test recommendations
curl http://localhost:5004/ads/contextual

# Test e-commerce
curl http://localhost:5005/products
```

### 3. Real-time Data Flow Test
- Watch the dashboard for live telemetry updates (every 3 seconds)
- Observe how maintenance alerts trigger contextual ads
- Test shopping cart persistence across page refreshes

## 🔧 Configuration

### Environment Variables
Create `.env` files in each service directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vehicle_retail
DB_USER=your_username
DB_PASSWORD=your_password

# API Configuration
API_PORT=5001
DEBUG=true

# Kafka Configuration (optional)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### Port Configuration
Default ports can be changed in respective `app.py` and `package.json` files:
- Data Processing: 5001
- ML Pipeline: 5002
- Maintenance Service: 5003
- Ad Engine: 5004
- E-commerce API: 5005
- Mobile App: 3000
- Infotainment: 3001

## 📚 Documentation

### Research Paper Context
This system was developed to demonstrate:
- **Connected Vehicle Ecosystems**: Integration of telematics with commercial services
- **Contextual Advertising**: Location and condition-based ad targeting
- **Predictive Maintenance**: AI-driven service recommendations
- **Multi-Platform UX**: Seamless mobile and in-vehicle experiences

### Technical Stack
- **Backend**: Python Flask, SQLite/PostgreSQL, Kafka (optional)
- **Frontend**: React, Vite, React Router
- **ML/AI**: Scikit-learn, Pandas, NumPy
- **Styling**: Custom CSS with automotive-inspired design
- **Architecture**: Microservices with REST APIs

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port
netstat -ano | findstr :3000
# Kill process (Windows)
taskkill /PID <process_id> /F
```

**Python Dependencies**
```bash
# Upgrade pip and reinstall
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Node Dependencies**
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Database Connection Issues**
- Check if SQLite database files are created in service directories
- Ensure proper file permissions
- Verify database initialization scripts ran successfully

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Research Context**: Developed for academic research on connected vehicle ecosystems
- **Design Inspiration**: Modern automotive infotainment systems
- **Data Sources**: Simulated vehicle telemetry based on industry standards

## 📞 Support

For questions or issues:
- **GitHub Issues**: [Create an issue](https://github.com/Shubhayang6/VehicleRetail_AdEngine/issues)
- **Documentation**: Check individual service README files
- **Demo Videos**: See `/docs` folder for visual guides

---

**🚗 Ready to explore the future of connected vehicle retail? Start with the Quick Start Guide above!** 🚀