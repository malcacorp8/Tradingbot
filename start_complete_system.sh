#!/bin/bash

# Complete Trading Bot System Startup Script
# This script starts both backend and frontend automatically

echo "🚀 Starting Complete Trading Bot System..."
echo "=========================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Check for existing processes and clean up
echo "🧹 Cleaning up existing processes..."
pkill -f "simple_app.py" 2>/dev/null || true
pkill -f "php artisan serve" 2>/dev/null || true
sleep 2

# Start Backend
echo ""
echo "🔧 Starting Backend Server..."
echo "=============================="

cd backend

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate

# Install dependencies if needed
if [ ! -f "env/lib/python*/site-packages/flask/__init__.py" ]; then
    echo "📦 Installing backend dependencies..."
    pip install flask flask-cors python-dotenv requests
fi

# Check if .env exists, if not configure it
if [ ! -f ".env" ]; then
    echo "⚙️  Configuring backend environment..."
    python3 configure_alpaca.py
fi

# Test Alpaca connection
echo "🔍 Testing Alpaca connection..."
python3 test_alpaca.py

# Start backend server
echo "🚀 Starting backend server on port 8080..."
python3 simple_app.py &
BACKEND_PID=$!

# Wait for backend to be ready
if wait_for_service "http://localhost:8080/health" "Backend Server"; then
    echo "✅ Backend server started successfully (PID: $BACKEND_PID)"
else
    echo "❌ Backend server failed to start"
    exit 1
fi

# Start Frontend
echo ""
echo "🌐 Starting Frontend Server..."
echo "=============================="

cd ../frontend

# Install Composer dependencies if needed
if [ ! -d "vendor" ]; then
    echo "📦 Installing Composer dependencies..."
    composer install --no-dev --optimize-autoloader
fi

# Generate key if needed
if ! grep -q "APP_KEY=base64:" .env 2>/dev/null; then
    echo "🔑 Generating application key..."
    php artisan key:generate --force
fi

# Clear and cache config
echo "⚙️  Clearing and caching configuration..."
php artisan config:clear
php artisan config:cache

# Run migrations
echo "🗄️  Setting up database..."
php artisan migrate --force

# Ensure backend URL is configured
if ! grep -q "BACKEND_URL=http://localhost:8080" .env 2>/dev/null; then
    echo "⚙️  Configuring backend connection..."
    echo "BACKEND_URL=http://localhost:8080" >> .env
    php artisan config:clear
    php artisan config:cache
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install --legacy-peer-deps
fi

# Build Vite assets
echo "🏗️  Building frontend assets..."
npm run build

# Start frontend server
echo "🌐 Starting frontend server on port 8000..."
php artisan serve --port=8000 &
FRONTEND_PID=$!

# Wait for frontend to be ready
if wait_for_service "http://localhost:8000" "Frontend Server"; then
    echo "✅ Frontend server started successfully (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend server failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# System Ready
echo ""
echo "🎉 TRADING BOT SYSTEM READY!"
echo "=============================="
echo "🌐 Frontend: http://localhost:8000"
echo "🔧 Backend:  http://localhost:8080"
echo ""
echo "📧 Login Credentials:"
echo "   Email:    admin@tradingbot.com"
echo "   Password: admin123"
echo ""
echo "🔧 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "🛑 To stop the system, run: ./stop_system.sh"
echo ""

# Save PIDs for cleanup script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

echo "✨ System startup complete! You can now access the trading bot."