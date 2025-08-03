# Quick Start Guide - Autonomous Trading Bot

This guide will get you up and running with the autonomous trading bot in under 30 minutes.

## ⚠️ Important Disclaimers

- **This software is for educational purposes only**
- **Trading involves significant financial risk**
- **Always start with paper trading mode**
- **Not financial advice - consult a professional**
- **Test thoroughly before using real money**

## Prerequisites

Before starting, ensure you have:

- Python 3.9 or higher
- PHP 8.1 or higher  
- Composer
- Node.js and npm
- Git
- An Alpaca account (free at [alpaca.markets](https://alpaca.markets))

## Step 1: Get Alpaca API Keys

1. Sign up at [alpaca.markets](https://alpaca.markets)
2. Go to your dashboard and generate API keys
3. Note down both Paper Trading and Live Trading keys
4. **Start with Paper Trading keys only**

## Step 2: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd trading-bot

# Run the automated setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Check prerequisites
- Set up Python virtual environment
- Install all dependencies
- Configure Laravel
- Create necessary directories

## Step 3: Configure API Keys

Edit the backend configuration:

```bash
cd backend
nano .env  # or use your preferred editor
```

Add your Alpaca Paper Trading keys:

```env
ALPACA_PAPER_KEY=your_paper_api_key_here
ALPACA_PAPER_SECRET=your_paper_secret_key_here
MODE=paper
STOCKS=AAPL,TSLA,GOOGL
```

## Step 4: Start the System

### Terminal 1 - Backend (Python AI)
```bash
cd backend
source env/bin/activate
python app.py
```

You should see:
```
INFO - Starting Autonomous Trading Bot API Server
INFO - Starting server on port 5000
```

### Terminal 2 - Frontend (Laravel Dashboard)  
```bash
cd frontend
php artisan serve
```

You should see:
```
Laravel development server started: http://127.0.0.1:8000
```

## Step 5: Access the Dashboard

1. Open your browser to: http://localhost:8000
2. Register a new account or login
3. Go to the Dashboard

## Step 6: Start Trading (Paper Mode)

1. **Verify Connection**: Check that the backend shows "Connected" (green dot)
2. **Check Mode**: Ensure it shows "Paper Trading" mode
3. **Start Bot**: Click "Start Trading" button
4. **Monitor**: Watch the portfolio and learning progress sections

## What Happens Next

The autonomous trading bot will:

1. **Analyze Markets**: Fetch real-time data for configured stocks
2. **Make Decisions**: Use reinforcement learning to decide buy/sell/hold
3. **Execute Trades**: Place orders through Alpaca's paper trading
4. **Learn**: Update ML models based on outcomes (gets smarter over time)
5. **Repeat**: Continue the cycle every 10 seconds

## Dashboard Features

- **Real-time Status**: See if bot is active, mode, and connection status
- **Portfolio View**: Monitor positions, balance, trades, and performance per stock
- **Learning Progress**: Track how each stock's AI agent is improving
- **Controls**: Start/stop bot, switch modes, configure stocks

## Key Safety Features

- **Paper Trading Default**: Always starts in safe simulation mode
- **Small Position Sizes**: Limited to 1% of capital per trade by default
- **Risk Management**: Built-in stop losses and volatility penalties
- **Manual Override**: Can stop bot at any time

## Common Issues

### Backend Won't Start
- Check Python version: `python3 --version` (need 3.9+)
- Activate virtual environment: `source backend/env/bin/activate`
- Install dependencies: `pip install -r backend/requirements.txt`

### Frontend Won't Load
- Check PHP version: `php --version` (need 8.1+)
- Run migrations: `php artisan migrate`
- Build assets: `npm run build`

### "Backend Disconnected"
- Ensure backend is running on port 5000
- Check firewall settings
- Verify `BACKEND_URL=http://localhost:5000` in frontend/.env

### No Trades Happening
- Verify Alpaca API keys are correct
- Check that stocks are configured (default: AAPL, TSLA, GOOGL)
- Ensure markets are open (9:30 AM - 4:00 PM ET, weekdays)

## Advanced Configuration

### Add More Stocks
```bash
# In backend/.env
STOCKS=AAPL,TSLA,GOOGL,MSFT,NVDA,AMZN,META
```

### Adjust Trading Frequency
```bash
# In backend/.env
POLLING_INTERVAL=5  # Check every 5 seconds (default: 10)
```

### Risk Management
```bash
# In backend/.env
MAX_POSITION_SIZE=0.005  # 0.5% of capital per trade (default: 0.01)
STOP_LOSS_THRESHOLD=0.03  # 3% stop loss (default: 0.05)
```

## Going Live (Advanced Users Only)

⚠️ **Only after extensive paper trading and testing**

1. Add live API keys to backend/.env:
```env
ALPACA_LIVE_KEY=your_live_api_key
ALPACA_LIVE_SECRET=your_live_secret
```

2. Switch to live mode in the dashboard
3. **Start with very small amounts**
4. Monitor closely

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [Configuration Guide](docs/configuration.md)  
- Check out [Advanced Features](docs/advanced.md)
- Join our community for support and updates

## Getting Help

- Check the logs in the dashboard
- Review backend terminal output
- Consult the troubleshooting guide
- Open an issue on GitHub

Remember: This is educational software. Always trade responsibly!