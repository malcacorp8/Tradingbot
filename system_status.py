#!/usr/bin/env python3
"""
System Status Checker for Trading Bot
Checks all components and services
"""

import requests
import subprocess
import json
from datetime import datetime

def check_service(name, url, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, response.json() if 'application/json' in response.headers.get('content-type', '') else 'OK'
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def check_processes():
    """Check running processes"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        python_procs = [line for line in processes.split('\n') if 'python' in line and 'app.py' in line]
        php_procs = [line for line in processes.split('\n') if 'artisan serve' in line]
        
        return python_procs, php_procs
    except Exception as e:
        return [], []

def main():
    print("🔍 Trading Bot System Status Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check processes
    print("📊 Process Status:")
    python_procs, php_procs = check_processes()
    
    if python_procs:
        print(f"  ✅ Python Backend: {len(python_procs)} process(es) running")
        for proc in python_procs:
            print(f"     {proc.split()[1]} - {' '.join(proc.split()[10:])}")
    else:
        print("  ❌ Python Backend: No processes found")
    
    if php_procs:
        print(f"  ✅ PHP Frontend: {len(php_procs)} process(es) running")
        for proc in php_procs:
            print(f"     {proc.split()[1]} - {' '.join(proc.split()[10:])}")
    else:
        print("  ❌ PHP Frontend: No processes found")
    
    print()
    
    # Check services
    print("🌐 Service Status:")
    
    # Basic backend
    basic_status, basic_data = check_service("Basic Backend", "http://localhost:8080/health")
    if basic_status:
        print("  ✅ Basic Backend (8080): HEALTHY")
        if isinstance(basic_data, dict):
            print(f"     Alpaca: {'✅' if basic_data.get('alpaca_connected') else '❌'}")
            print(f"     Trading: {'✅' if basic_data.get('trading_active') else '⭕'}")
            print(f"     Mode: {basic_data.get('mode', 'Unknown')}")
    else:
        print(f"  ❌ Basic Backend (8080): {basic_data}")
    
    # Advanced backend
    advanced_status, advanced_data = check_service("Advanced Backend", "http://localhost:8081/")
    if advanced_status:
        print("  ✅ Advanced AI Backend (8081): HEALTHY")
        if isinstance(advanced_data, dict):
            print(f"     Version: {advanced_data.get('version', 'Unknown')}")
            print(f"     AI Active: {'✅' if advanced_data.get('active') else '⭕'}")
    else:
        print(f"  ❌ Advanced AI Backend (8081): {advanced_data}")
    
    # Frontend
    frontend_status, frontend_data = check_service("Frontend", "http://localhost:8000/")
    if frontend_status:
        print("  ✅ Laravel Frontend (8000): HEALTHY")
    else:
        print(f"  ❌ Laravel Frontend (8000): {frontend_data}")
    
    print()
    
    # Overall status
    all_healthy = basic_status and frontend_status
    if all_healthy:
        print("🎉 SYSTEM STATUS: FULLY OPERATIONAL")
        print("   Your trading bot is ready to use!")
        print("   Dashboard: http://localhost:8000")
        if advanced_status:
            print("   Advanced AI: http://localhost:8000/advanced")
    else:
        print("⚠️  SYSTEM STATUS: PARTIAL")
        print("   Some services need attention")
    
    print()
    print("📋 Quick Actions:")
    if not basic_status:
        print("   Start Basic Backend: cd backend && source env/bin/activate && python3 simple_app.py")
    if not advanced_status:
        print("   Start Advanced AI: cd backend && source env/bin/activate && python3 advanced_trading_bot.py")
    if not frontend_status:
        print("   Start Frontend: cd frontend && php artisan serve")

if __name__ == "__main__":
    main()