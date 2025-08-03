#!/usr/bin/env python3
"""
Setup script for the Trading Bot Backend
Installs dependencies and sets up the environment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description or command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("Error: Python 3.9 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists('env'):
        if not run_command('python3 -m venv env', "Creating virtual environment"):
            return False
    else:
        print("✓ Virtual environment already exists")
    
    # Check if we're in a virtual environment
    if 'VIRTUAL_ENV' not in os.environ:
        print("\nTo activate the virtual environment, run:")
        if os.name == 'nt':  # Windows
            print("env\\Scripts\\activate")
        else:  # Unix/MacOS
            print("source env/bin/activate")
        return True
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    # First, upgrade pip
    if not run_command('pip install --upgrade pip', "Upgrading pip"):
        return False
    
    # Install main dependencies
    if not run_command('pip install -r requirements.txt', "Installing Python dependencies"):
        return False
    
    return True

def setup_configuration():
    """Set up configuration files"""
    env_template = Path('env_template')
    env_file = Path('.env')
    
    if not env_file.exists() and env_template.exists():
        print("\nCopying environment template...")
        env_file.write_text(env_template.read_text())
        print("✓ .env file created from template")
        print("\n⚠️  IMPORTANT: Please edit .env file with your Alpaca API keys!")
    else:
        print("✓ .env file already exists")
    
    # Create necessary directories
    directories = ['models', 'logs', 'tensorboard_logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def verify_installation():
    """Verify that key dependencies are working"""
    print("\nVerifying installation...")
    
    # Test imports
    try:
        import torch
        print("✓ PyTorch installed successfully")
    except ImportError:
        print("✗ PyTorch not found")
        return False
    
    try:
        import stable_baselines3
        print("✓ Stable Baselines 3 installed successfully")
    except ImportError:
        print("✗ Stable Baselines 3 not found")
        return False
    
    try:
        import flask
        print("✓ Flask installed successfully")
    except ImportError:
        print("✗ Flask not found")
        return False
    
    return True

def main():
    """Main setup function"""
    print("Trading Bot Backend Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("Failed to set up virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies")
        sys.exit(1)
    
    # Setup configuration
    setup_configuration()
    
    # Verify installation
    if not verify_installation():
        print("Installation verification failed")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✓ Backend setup completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Edit .env file with your Alpaca API keys")
    print("2. Activate virtual environment: source env/bin/activate")
    print("3. Run the backend: python app.py")
    print("\nFor paper trading, you can start with the default configuration.")
    print("For live trading, make sure to set up your live API keys and start with small amounts!")

if __name__ == "__main__":
    main()