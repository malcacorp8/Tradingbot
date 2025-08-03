#!/bin/bash

# Start Trading Bot Backend
echo "🚀 Starting Trading Bot Backend..."

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
if [ ! -f "env/pyvenv.cfg" ] || [ ! -d "env/lib" ]; then
    echo "📦 Installing dependencies..."
    pip install flask flask-cors python-dotenv requests sqlalchemy pandas numpy
fi

# Check if .env exists, if not configure it
if [ ! -f ".env" ]; then
    echo "⚙️  Configuring environment..."
    python3 configure_alpaca.py
fi

# Test Alpaca connection
echo "🔍 Testing Alpaca connection..."
python3 test_alpaca.py

echo ""
echo "🚀 Starting backend server on port 8080..."
python3 simple_app.py