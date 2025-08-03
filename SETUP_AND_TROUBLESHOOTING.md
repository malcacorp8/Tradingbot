# Setup and Troubleshooting Guide

Complete guide for setting up and resolving issues with the Autonomous Trading Bot system.

## 🚀 **Prerequisites**

### **Required Software**
```bash
✅ Python 3.9+ (with pip)
✅ PHP 8.1+ (with Composer)  
✅ Node.js 16+ (with npm)
✅ Git (for cloning repository)
```

### **System Requirements**
- **OS**: macOS, Linux, or Windows
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for market data

---

## ⚡ **Quick Setup (Automated)**

### **Option 1: One-Click Complete Setup**
```bash
# Clone repository (if needed)
git clone <repository-url>
cd trading-bot

# Run complete system setup
chmod +x start_complete_system.sh
./start_complete_system.sh

# Expected output:
# 🚀 Starting Complete Trading Bot System...
# ✅ Backend Server is ready! (PID: XXXX)
# ✅ Frontend Server is ready! (PID: XXXX)
# 🎉 TRADING BOT SYSTEM READY!
```

### **Access Your System**
- **Frontend**: http://localhost:8000
- **Login**: admin@tradingbot.com / admin123
- **Backend API**: http://localhost:8080

---

## 🔧 **Manual Setup (Step-by-Step)**

### **Step 1: Backend Setup**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv env

# Activate virtual environment
source env/bin/activate  # macOS/Linux
# env\Scripts\activate   # Windows

# Install Python dependencies
pip install flask flask-cors python-dotenv requests sqlalchemy pandas numpy

# Verify Alpaca configuration (already configured)
python3 test_alpaca.py
# Expected: ✅ Alpaca API connection successful

# Start backend server
python3 simple_app.py
# Expected: * Running on http://127.0.0.1:8080
```

### **Step 2: Frontend Setup**
```bash
# Open new terminal and navigate to frontend
cd frontend

# Install PHP dependencies
composer install --no-dev --optimize-autoloader

# Generate application key
php artisan key:generate --force

# Clear and cache configuration
php artisan config:clear
php artisan config:cache

# Run database migrations
php artisan migrate --force

# Install Node.js dependencies
npm install --legacy-peer-deps

# Build frontend assets
npm run build

# Start frontend server
php artisan serve --port=8000
# Expected: Server running on [http://127.0.0.1:8000]
```

### **Step 3: System Verification**
```bash
# Test backend health
curl http://localhost:8080/health

# Test frontend access
curl http://localhost:8000

# Both should respond successfully
```

---

## 🛠️ **Common Issues & Solutions**

### **Issue 1: Backend Won't Start**

**Symptom**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
cd backend
source env/bin/activate
pip install flask flask-cors python-dotenv requests sqlalchemy pandas numpy
python3 simple_app.py
```

**Verification**:
```bash
curl http://localhost:8080/health
# Should return JSON with alpaca_connected: true
```

---

### **Issue 2: Port Already in Use**

**Symptom**: `Address already in use` or `Port XXXX is in use`

**For Backend (Port 8080)**:
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or kill by name
pkill -f simple_app
pkill -f python

# Restart backend
cd backend && source env/bin/activate && python3 simple_app.py
```

**For Frontend (Port 8000)**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or kill by name
pkill -f "artisan serve"

# Restart frontend
cd frontend && php artisan serve --port=8000
```

---

### **Issue 3: Frontend Shows "Backend Connection Error"**

**Symptom**: Dashboard shows connection errors or timeouts

**Diagnosis**:
```bash
# Check if backend is running
curl http://localhost:8080/health

# Check backend URL configuration
grep -n "BACKEND_URL" frontend/app/Http/Controllers/TradingBotController.php
# Should show: http://localhost:8080
```

**Solution**:
```bash
# If backend URL is wrong, fix it
sed -i 's/localhost:5000/localhost:8080/g' frontend/app/Http/Controllers/TradingBotController.php

# Clear Laravel cache
cd frontend
php artisan config:clear
php artisan cache:clear

# Restart frontend
php artisan serve --port=8000
```

---

### **Issue 4: "Start Trading" Button Not Working**

**Symptom**: Button click has no effect or shows errors

**✅ This Issue Was FIXED**:
The backend URL configuration was updated to use the correct port 8080.

**Verification**:
```bash
# Test direct backend API call
curl -X POST http://localhost:8080/start

# Should return: {"status": "started", ...}

# Test through frontend (requires login)
# Login at http://localhost:8000/login first
# admin@tradingbot.com / admin123
```

---

### **Issue 5: Alpaca API Connection Failed**

**Symptom**: `alpaca_connected: false` in health check

**Diagnosis**:
```bash
cd backend
python3 test_alpaca.py
```

**Solution**:
The system comes pre-configured with working Alpaca paper trading credentials. If connection fails:

```bash
# Check .env file exists
ls -la backend/.env

# Verify credentials format
grep ALPACA backend/.env
# Should show:
# ALPACA_PAPER_KEY=PKO55CJ2...
# ALPACA_PAPER_SECRET=kdsuJSXk...

# Test connection manually
cd backend && source env/bin/activate && python3 test_alpaca.py
```

---

### **Issue 6: Frontend Login Not Working**

**Symptom**: Cannot login with provided credentials

**Solution**:
```bash
# Reset Laravel application
cd frontend
php artisan key:generate --force
php artisan migrate:fresh --force

# Clear all caches
php artisan config:clear
php artisan cache:clear
php artisan view:clear

# Restart server
php artisan serve --port=8000
```

**Default Credentials**:
- Email: `admin@tradingbot.com`
- Password: `admin123`

---

### **Issue 7: Virtual Environment Issues**

**Symptom**: `source: no such file or directory: env/bin/activate`

**Solution**:
```bash
# Recreate virtual environment
cd backend
rm -rf env
python3 -m venv env
source env/bin/activate
pip install flask flask-cors python-dotenv requests sqlalchemy pandas numpy
```

---

## 🔍 **Diagnostic Commands**

### **System Status Check**
```bash
# Check all running processes
ps aux | grep -E "(python|artisan)" | grep -v grep

# Check port usage
lsof -i :8080  # Backend
lsof -i :8000  # Frontend

# Test connectivity
curl -s http://localhost:8080/health | jq '.alpaca_connected'
curl -s http://localhost:8000 | head -5
```

### **Backend Diagnostics**
```bash
cd backend

# Check Python environment
which python3
python3 --version

# Check installed packages
pip list | grep -E "(flask|requests)"

# Test Alpaca connection
python3 test_alpaca.py

# Check backend logs (when running)
# Backend outputs logs to console
```

### **Frontend Diagnostics**
```bash
cd frontend

# Check PHP version
php --version

# Check Laravel status
php artisan --version

# Check routes
php artisan route:list | grep bot

# Check configuration
php artisan config:show | grep -A5 -B5 BACKEND
```

---

## 🚨 **Emergency Reset**

If all else fails, perform a complete system reset:

```bash
# Stop all services
./stop_system.sh 2>/dev/null || true
pkill -f simple_app
pkill -f "artisan serve"
pkill -f python

# Clean backend
cd backend
rm -rf env __pycache__ *.pyc
python3 -m venv env
source env/bin/activate
pip install flask flask-cors python-dotenv requests sqlalchemy pandas numpy

# Clean frontend
cd ../frontend
composer install --no-dev
php artisan key:generate --force
php artisan config:clear
php artisan cache:clear
npm install --legacy-peer-deps
npm run build

# Restart system
cd ..
./start_complete_system.sh
```

---

## 📊 **Performance Optimization**

### **Backend Performance**
```bash
# Monitor backend CPU/memory usage
top -p $(pgrep -f simple_app)

# Check API response times
time curl -s http://localhost:8080/health > /dev/null
```

### **Frontend Performance**  
```bash
# Monitor frontend response times
time curl -s http://localhost:8000 > /dev/null

# Check asset build
cd frontend && npm run build
```

---

## 🔒 **Security Considerations**

### **Development Environment**
- ✅ **Paper Trading**: Uses virtual money only
- ✅ **Localhost Only**: Services bound to localhost
- ⚠️ **No HTTPS**: HTTP only (development setup)
- ⚠️ **Default Credentials**: Change for production use

### **Production Recommendations**
- Use HTTPS with SSL certificates
- Change default login credentials
- Implement proper authentication
- Use environment variables for sensitive data
- Set up proper logging and monitoring

---

## 📞 **Getting Help**

### **Self-Help Resources**
1. **Check this troubleshooting guide** first
2. **Review system logs** for error messages
3. **Test individual components** (backend, frontend separately)
4. **Use diagnostic commands** above

### **Common Resolution Steps**
1. **Restart services** (`./stop_system.sh` then `./start_complete_system.sh`)
2. **Check port conflicts** (kill competing processes)
3. **Verify dependencies** (Python packages, PHP extensions)
4. **Clear caches** (Laravel config cache, browser cache)

### **System Information for Support**
When seeking help, provide:
```bash
# System info
uname -a
python3 --version
php --version
node --version

# Service status
lsof -i :8080
lsof -i :8000

# Error messages
# Include any error output from terminal
```

---

## ✅ **Success Checklist**

After setup, verify these work:

- [ ] Backend responds: `curl http://localhost:8080/health`
- [ ] Frontend loads: Open `http://localhost:8000` in browser
- [ ] Login works: admin@tradingbot.com / admin123
- [ ] Dashboard shows: Alpaca connected, $100K balance
- [ ] Trading works: "Start Trading" button functions
- [ ] Real-time updates: Status changes appear on dashboard

**🎉 If all items check out, your system is fully operational!**

---

*Last Updated: August 3, 2025*  
*Covers all known issues and solutions*