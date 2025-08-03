# Start Your Trading Bot - Step by Step

Now that your Alpaca credentials are ready, let's get your autonomous trading bot running!

## Step 1: Configure Backend

Copy your Alpaca credentials to the backend environment:

```bash
cd backend
cp env_template .env
```

Then edit `backend/.env` and replace the placeholder values with:

```env
ALPACA_PAPER_KEY=PKO55CJ2SRBUAK3L06WW
ALPACA_PAPER_SECRET=kdsuJSXkdEOq8r0652U6yJs2LuQvH67ZXYv3dhZo
MODE=paper
STOCKS=AAPL,TSLA,GOOGL,MSFT,NVDA
DB_URL=sqlite:///trading_bot.db
POLLING_INTERVAL=10
```

## Step 2: Start the Backend (Terminal 1)

```bash
cd backend
source env/bin/activate
pip install -r requirements.txt
python app.py
```

You should see:
```
INFO - Starting Autonomous Trading Bot API Server
INFO - Agent manager initialized with stocks: ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA']
INFO - Starting server on port 5000
```

## Step 3: Configure Frontend

In another terminal, configure the Laravel frontend:

```bash
cd frontend
echo "" >> .env
echo "# Backend Configuration" >> .env
echo "BACKEND_URL=http://localhost:5000" >> .env
```

## Step 4: Start the Frontend (Terminal 2)

```bash
cd frontend
composer install
php artisan migrate
npm install --legacy-peer-deps
npm run build
php artisan serve
```

You should see:
```
Laravel development server started: http://127.0.0.1:8000
```

## Step 5: Access the Dashboard

1. Open your browser to: **http://localhost:8000**
2. Click **"Register"** to create an account
3. After registration, you'll be redirected to the **Dashboard**

## Step 6: Start Autonomous Trading

In the dashboard:

1. **Check Connection**: You should see a green dot "Connected to backend"
2. **Verify Mode**: Should show "Paper Trading" mode
3. **Check Stocks**: Should show 5 configured stocks (AAPL, TSLA, GOOGL, MSFT, NVDA)
4. **Click "Start Trading"**: The bot will begin autonomous operations

## What Happens Next

The autonomous trading bot will:

1. **Initialize Agents**: Create RL agents for each stock
2. **Fetch Market Data**: Get real-time prices and indicators
3. **Make Decisions**: Use AI to decide buy/sell/hold every 10 seconds
4. **Execute Trades**: Place paper trades through Alpaca
5. **Learn & Improve**: Update models based on outcomes

## Dashboard Features to Watch

- **Portfolio Overview**: See balance, positions, and trade counts per stock
- **Learning Progress**: Watch agents improve over time (episodes, learning cycles)
- **Real-time Updates**: Status refreshes every 10 seconds automatically
- **Performance Metrics**: Win rates, returns, and Sharpe ratios

## Expected Behavior

### First Hour
- Agents will make random/exploratory trades (this is normal!)
- You might see losses as the AI learns (this is expected)
- Trade frequency will be low initially

### After Several Hours
- Agents start recognizing patterns
- More consistent trading behavior
- Gradual performance improvement

### After Days/Weeks
- Agents become more sophisticated
- Better risk management
- Improved returns and win rates

## Monitoring Tips

1. **Check Logs**: Backend terminal shows detailed trading decisions
2. **Watch Learning**: "Learning Progress" section shows improvement metrics
3. **Portfolio Balance**: Monitor total balance changes over time
4. **Individual Stocks**: Each stock learns independently

## Safety Features Active

✅ **Paper Trading**: All trades are simulated (no real money)  
✅ **Small Positions**: Maximum 1% of capital per trade  
✅ **Stop Losses**: Automatic 5% loss limits  
✅ **Risk Penalties**: AI learns to avoid high-risk situations  
✅ **Manual Override**: You can stop anytime  

## Troubleshooting

### "Backend Disconnected"
- Check that backend is running on port 5000
- Verify no firewall blocking localhost connections

### "No Trades Happening"
- Ensure markets are open (9:30 AM - 4:00 PM ET, weekdays)
- Check that ALPACA_PAPER_KEY is correctly set
- Verify stocks are configured

### Backend Errors
- Check virtual environment is activated
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Alpaca API key format

## Next Steps

Once you see the system working:

1. **Monitor Learning**: Watch for improvement over days
2. **Experiment**: Try different stocks or risk parameters
3. **Analyze**: Use the analytics to understand agent behavior
4. **Scale**: Add more stocks or adjust trading frequency

Remember: This is your personal AI trading laboratory! The longer it runs, the smarter it gets. 

**Have fun watching your AI agents learn to trade! 🤖📈**