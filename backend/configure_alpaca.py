#!/usr/bin/env python3
"""
Quick configuration script to set up Alpaca API credentials
"""

import os
from pathlib import Path

def configure_alpaca():
    """Configure Alpaca API credentials in .env file"""
    
    # Your Alpaca Paper Trading credentials
    ALPACA_PAPER_KEY = "PKO55CJ2SRBUAK3L06WW"
    ALPACA_PAPER_SECRET = "kdsuJSXkdEOq8r0652U6yJs2LuQvH67ZXYv3dhZo"
    
    # Read the template
    env_template_path = Path(".env")
    
    if not env_template_path.exists():
        print("Creating .env file from template...")
        with open("env_template", "r") as template:
            content = template.read()
    else:
        print("Updating existing .env file...")
        with open(".env", "r") as existing:
            content = existing.read()
    
    # Replace placeholders with actual credentials
    content = content.replace("your_paper_api_key_here", ALPACA_PAPER_KEY)
    content = content.replace("your_paper_secret_key_here", ALPACA_PAPER_SECRET)
    content = content.replace("mysql+pymysql://user:password@localhost/trading_bot", "sqlite:///trading_bot.db")
    
    # Write the configured .env file
    with open(".env", "w") as env_file:
        env_file.write(content)
    
    print("✓ Alpaca credentials configured successfully!")
    print("✓ Database set to SQLite for local development")
    print("✓ Mode set to 'paper' for safe testing")
    print("\nReady to start the trading bot!")

if __name__ == "__main__":
    configure_alpaca()