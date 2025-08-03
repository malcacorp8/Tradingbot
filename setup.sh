#!/bin/bash

# Autonomous Trading Bot Setup Script
# This script sets up both the backend and frontend components

set -e  # Exit on any error

echo "=========================================="
echo "  Autonomous Trading Bot Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_status "Python 3 found"

if ! command_exists php; then
    print_error "PHP is not installed"
    exit 1
fi
print_status "PHP found"

if ! command_exists composer; then
    print_error "Composer is not installed"
    print_error "Please install Composer from https://getcomposer.org/"
    exit 1
fi
print_status "Composer found"

if ! command_exists npm; then
    print_error "Node.js/npm is not installed"
    print_error "Please install Node.js from https://nodejs.org/"
    exit 1
fi
print_status "Node.js/npm found"

# Setup Backend
echo ""
print_status "Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "env" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv env
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source env/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Setup configuration
if [ ! -f ".env" ] && [ -f "env_template" ]; then
    print_status "Creating .env file from template..."
    cp env_template .env
    print_warning "Please edit backend/.env with your Alpaca API keys!"
fi

# Create necessary directories
mkdir -p models logs tensorboard_logs

print_status "Backend setup completed!"
cd ..

# Setup Frontend
echo ""
print_status "Setting up Laravel frontend..."
cd frontend

# Install Composer dependencies (if not already done)
if [ ! -d "vendor" ]; then
    print_status "Installing Composer dependencies..."
    composer install --no-dev --optimize-autoloader
else
    print_status "Composer dependencies already installed"
fi

# Install npm dependencies
print_status "Installing npm dependencies..."
npm install --legacy-peer-deps

# Setup Laravel configuration
if [ ! -f ".env" ]; then
    print_status "Creating Laravel .env file..."
    cp .env.example .env
    # Add backend URL configuration
    echo "" >> .env
    echo "# Backend Configuration" >> .env
    echo "BACKEND_URL=http://localhost:5000" >> .env
fi

# Generate application key
print_status "Generating Laravel application key..."
php artisan key:generate --force

# Run database migrations
print_status "Running database migrations..."
php artisan migrate --force

# Build frontend assets
print_status "Building frontend assets..."
npm run build

print_status "Frontend setup completed!"
cd ..

# Final instructions
echo ""
echo "=========================================="
print_status "Setup completed successfully!"
echo "=========================================="
echo ""
echo "To start the trading bot system:"
echo ""
echo "1. Start the Python backend:"
echo "   cd backend"
echo "   source env/bin/activate"
echo "   python app.py"
echo ""
echo "2. In another terminal, start the Laravel frontend:"
echo "   cd frontend"
echo "   php artisan serve"
echo ""
echo "3. Open your browser and go to: http://localhost:8000"
echo ""
print_warning "IMPORTANT NOTES:"
echo "- Edit backend/.env with your Alpaca API keys before starting"
echo "- Start with paper trading mode for testing"
echo "- Only use live trading with small amounts after thorough testing"
echo "- This software is for educational purposes - trading involves risk"
echo ""
echo "For more information, see the README.md file."