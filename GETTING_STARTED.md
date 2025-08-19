# Getting Started Checklist ✅

Follow this checklist to get the Vehicle Retail Ad Engine up and running quickly!

## ⚡ Quick Setup (Windows)

### Option 1: Automated Setup
```bash
# 1. Clone and enter directory
git clone https://github.com/Shubhayang6/VehicleRetail_AdEngine.git
cd VehicleRetail_AdEngine

# 2. Run automated backend setup
start_backend.bat

# 3. Run automated frontend setup (in new terminal)
start_frontend.bat
```

### Option 2: Manual Setup

#### Prerequisites Check
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] Git installed (`git --version`)

#### Backend Services (5 terminals)
- [ ] **Terminal 1**: Data Processing
  ```bash
  cd DataProcessing_Service
  python app.py
  ```
- [ ] **Terminal 2**: ML Pipeline
  ```bash
  cd ML_Pipeline
  python app.py
  ```
- [ ] **Terminal 3**: Maintenance Service
  ```bash
  cd PredictiveMaintenance_Service
  python app.py
  ```
- [ ] **Terminal 4**: Ad Engine
  ```bash
  cd Ad_RecommendationEngine
  python app.py
  ```
- [ ] **Terminal 5**: E-commerce API
  ```bash
  cd Ecommerce_API
  python app.py
  ```

#### Frontend Applications (2 terminals)
- [ ] **Terminal 6**: Mobile App
  ```bash
  cd Android_App
  npm install
  npm run dev
  ```
- [ ] **Terminal 7**: Infotainment Display
  ```bash
  cd Infotainment_Display
  npm install
  npm run dev
  ```

## 🧪 Verification Steps

### Backend Health Check
- [ ] Data Processing: http://localhost:5001/health
- [ ] ML Pipeline: http://localhost:5002/health
- [ ] Maintenance: http://localhost:5003/health
- [ ] Ad Engine: http://localhost:5004/health
- [ ] E-commerce: http://localhost:5005/health

### Frontend Access
- [ ] Mobile App: http://localhost:3000
- [ ] Infotainment: http://localhost:3001

### Functionality Test
- [ ] Mobile app loads and shows vehicle dashboard
- [ ] Real-time data updates every 3 seconds
- [ ] Navigation between tabs works
- [ ] Shopping cart adds/removes items
- [ ] Infotainment shows contextual ads
- [ ] Climate controls are interactive

## 🚨 Troubleshooting

### Common Issues
- **Port in use**: Check if services are already running
- **Python not found**: Ensure Python is in PATH
- **npm not found**: Ensure Node.js is properly installed
- **Blank screen**: Check browser console for errors

### Quick Fixes
```bash
# Kill processes on Windows
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Restart with clean slate
npm cache clean --force
pip cache purge
```

## 📊 Demo Scenarios

### Scenario 1: Maintenance Alert Flow
1. [ ] Open mobile app → Dashboard
2. [ ] Notice "Oil Change Due" alert
3. [ ] Go to Maintenance tab → View alert details
4. [ ] Open infotainment → See contextual oil change ad
5. [ ] Click ad → Verify interaction

### Scenario 2: Shopping Journey
1. [ ] Open mobile app → Shopping tab
2. [ ] Browse products → Add to cart
3. [ ] Proceed to checkout → Complete order
4. [ ] Verify cart persistence across refreshes

### Scenario 3: Multi-Platform Experience
1. [ ] Open both mobile app and infotainment
2. [ ] Compare data synchronization
3. [ ] Test interactions on both platforms
4. [ ] Verify contextual ads appear correctly

## 📈 Success Criteria

### Technical Success
- [ ] All 5 backend services running without errors
- [ ] Both frontend applications accessible
- [ ] Real-time data flowing correctly
- [ ] APIs responding with valid JSON

### User Experience Success
- [ ] Smooth navigation and interactions
- [ ] Contextual ads relevant to vehicle state
- [ ] Shopping cart functionality complete
- [ ] Mobile and automotive UX patterns evident

### Research Demo Success
- [ ] Complete user journey demonstrable
- [ ] Multi-platform ecosystem visible
- [ ] AI-powered recommendations working
- [ ] Connected vehicle concept clear

## 🎯 Next Steps

After successful setup:
1. [ ] Explore all features in both interfaces
2. [ ] Test API endpoints with curl/Postman
3. [ ] Review code structure and architecture
4. [ ] Customize for your research needs
5. [ ] Document your findings

---

**✅ Ready to demo your connected vehicle retail ecosystem!** 

If you encounter issues, check the main [README.md](README.md) for detailed troubleshooting steps.
