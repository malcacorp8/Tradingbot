#!/bin/bash

# Stop Trading Bot System Script

echo "🛑 Stopping Trading Bot System..."
echo "================================="

# Function to stop a process by PID
stop_process() {
    local pid=$1
    local name=$2
    
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "🛑 Stopping $name (PID: $pid)..."
        kill "$pid"
        
        # Wait for process to stop
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            echo "⚠️  Force killing $name..."
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        echo "✅ $name stopped"
    else
        echo "ℹ️  $name was not running"
    fi
}

# Read PIDs from files
BACKEND_PID=""
FRONTEND_PID=""

if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
fi

# Stop processes
stop_process "$BACKEND_PID" "Backend Server"
stop_process "$FRONTEND_PID" "Frontend Server"

# Additional cleanup for any remaining processes
echo "🧹 Additional cleanup..."
pkill -f "simple_app.py" 2>/dev/null || true
pkill -f "php artisan serve" 2>/dev/null || true

# Clean up PID files
rm -f .backend.pid .frontend.pid

echo ""
echo "✅ Trading Bot System stopped successfully!"
echo "   All processes have been terminated."