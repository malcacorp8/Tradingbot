#!/usr/bin/env python3
"""
Test Alpaca API Connection
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_alpaca():
    print("🔄 Testing Alpaca API Connection...")
    print("=" * 50)
    
    # Get credentials
    api_key = os.getenv('ALPACA_PAPER_KEY')
    secret_key = os.getenv('ALPACA_PAPER_SECRET')
    
    print(f"API Key: {api_key[:8]}..." if api_key else "API Key: Not found")
    print(f"Secret: {secret_key[:8]}..." if secret_key else "Secret: Not found")
    
    if not api_key or not secret_key:
        print("❌ ERROR: API keys not configured!")
        return False
    
    headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': secret_key
    }
    
    try:
        # Test account endpoint
        print("\n🔄 Testing account access...")
        response = requests.get(
            'https://paper-api.alpaca.markets/v2/account',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account = response.json()
            print("✅ Account Access: SUCCESS")
            print(f"   Cash: ${float(account.get('cash', 0)):,.2f}")
            print(f"   Buying Power: ${float(account.get('buying_power', 0)):,.2f}")
            print(f"   Account Status: {account.get('status', 'Unknown')}")
        else:
            print(f"❌ Account Access: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            return False
        
        # Test positions
        print("\n🔄 Testing positions access...")
        response = requests.get(
            'https://paper-api.alpaca.markets/v2/positions',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            positions = response.json()
            print(f"✅ Positions Access: SUCCESS ({len(positions)} positions)")
        else:
            print(f"❌ Positions Access: FAILED ({response.status_code})")
        
        # Test market data (quote)
        print("\n🔄 Testing market data access...")
        response = requests.get(
            'https://data.alpaca.markets/v2/stocks/AAPL/quotes/latest',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            quote = response.json()
            print("✅ Market Data Access: SUCCESS")
            if 'quote' in quote:
                print(f"   AAPL: ${quote['quote'].get('ap', 'N/A')} (ask)")
        else:
            print(f"❌ Market Data Access: FAILED ({response.status_code})")
        
        print("\n" + "=" * 50)
        print("🎉 Your Alpaca API is working perfectly!")
        print("✅ Ready for autonomous trading!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    success = test_alpaca()
    if success:
        print("\n🚀 You can now start the trading bot!")
        print("   Run: python simple_app.py")
    else:
        print("\n🔧 Please check your API keys and try again.")