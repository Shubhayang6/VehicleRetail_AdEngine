# Project Structure

```
VehicleRetail_AdEngine/
│
├── README.md                          # Main project documentation
├── requirements.txt                   # Python dependencies
├── start_backend.bat                 # Windows startup script for backend
├── start_frontend.bat                # Windows startup script for frontend
│
├── Architecture/                      # System architecture documentation
│   └── local_architecture.puml       # PlantUML architecture diagram
│
├── DataProcessing_Service/            # Core data processing microservice
│   ├── app.py                        # Flask application
│   ├── models.py                     # Data models
│   └── utils.py                      # Utility functions
│
├── ML_Pipeline/                       # Machine learning service
│   ├── app.py                        # ML API endpoints
│   ├── models/                       # Trained ML models
│   └── training/                     # Training scripts
│
├── PredictiveMaintenance_Service/     # Maintenance prediction service
│   ├── app.py                        # Maintenance API
│   ├── predictor.py                  # Prediction logic
│   └── scheduler.py                  # Service scheduling
│
├── Ad_RecommendationEngine/           # Advertisement and recommendation service
│   ├── app.py                        # Ad engine API
│   ├── ad_engine.py                  # Ad targeting logic
│   └── recommendation_engine.py      # Product recommendations
│
├── Ecommerce_API/                     # E-commerce platform service
│   ├── app.py                        # E-commerce API
│   ├── products.py                   # Product catalog
│   └── orders.py                     # Order management
│
├── Android_App/                       # Mobile application (React)
│   ├── package.json                  # Node.js dependencies
│   ├── vite.config.js                # Vite configuration
│   ├── index.html                    # HTML entry point
│   ├── src/
│   │   ├── main.jsx                  # React entry point
│   │   ├── App.jsx                   # Main app component
│   │   ├── index.css                 # Global styles
│   │   ├── components/
│   │   │   └── AndroidFrame.jsx      # Mobile device frame
│   │   └── pages/
│   │       ├── Dashboard.jsx         # Vehicle telemetry dashboard
│   │       ├── Maintenance.jsx       # Service and maintenance
│   │       ├── Shopping.jsx          # E-commerce interface
│   │       └── Profile.jsx           # User profile and settings
│   └── public/                       # Static assets
│
└── Infotainment_Display/             # In-vehicle display (React)
    ├── package.json                  # Node.js dependencies
    ├── vite.config.js                # Vite configuration
    ├── index.html                    # HTML entry point
    ├── src/
    │   ├── main.jsx                  # React entry point
    │   ├── App.jsx                   # Main app component
    │   ├── index.css                 # Automotive-styled CSS
    │   └── components/
    │       └── InfotainmentFrame.jsx # Car dashboard interface
    └── public/                       # Static assets
```

## Service Dependencies

```
Data Processing Service (5001)
├── Receives: Vehicle telemetry data
├── Processes: Data cleaning and validation
└── Outputs: Clean data to other services

ML Pipeline (5002)
├── Receives: Processed telemetry data
├── Processes: Predictive analytics
└── Outputs: Maintenance predictions

Maintenance Service (5003)
├── Receives: ML predictions
├── Processes: Service scheduling
└── Outputs: Maintenance alerts and appointments

Ad Engine (5004)
├── Receives: Vehicle data and user behavior
├── Processes: Contextual ad targeting
└── Outputs: Targeted advertisements

E-commerce API (5005)
├── Receives: Product requests and orders
├── Processes: Shopping cart and payments
└── Outputs: Order confirmations

Mobile App (3000)
├── Receives: Data from all backend services
├── Processes: User interactions
└── Outputs: Mobile-optimized interface

Infotainment Display (3001)
├── Receives: Data from all backend services
├── Processes: In-vehicle interactions
└── Outputs: Automotive dashboard interface
```

## Data Flow

1. **Vehicle Telemetry** → Data Processing Service
2. **Processed Data** → ML Pipeline for predictions
3. **Predictions** → Maintenance Service for alerts
4. **Vehicle Context** → Ad Engine for targeting
5. **User Behavior** → Recommendation Engine
6. **All Data** → Frontend Applications for display

## Technology Stack

### Backend Services
- **Framework**: Python Flask
- **Database**: SQLite (configurable to PostgreSQL)
- **ML**: Scikit-learn, Pandas, NumPy
- **APIs**: RESTful JSON APIs
- **Architecture**: Microservices

### Frontend Applications
- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router
- **Styling**: Custom CSS (Mobile-first design)
- **Icons**: Emoji-based (cross-platform compatibility)

### Development Tools
- **Version Control**: Git
- **Package Management**: npm (Node.js), pip (Python)
- **Development Server**: Vite (Frontend), Flask (Backend)
- **Testing**: Browser-based testing, API testing with curl
