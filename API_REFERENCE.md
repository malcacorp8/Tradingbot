# Trading Bot API Reference

Complete reference for all API endpoints with working examples from comprehensive testing.

## 🔗 **Base URLs**

- **Backend API**: `http://localhost:8080`
- **Frontend API**: `http://localhost:8000/api/bot` (requires authentication)

---

## 🏥 **Health & Status Endpoints**

### **GET /health**
Returns system health and Alpaca connection status.

**Request:**
```bash
curl -s http://localhost:8080/health
```

**Response Example:**
```json
{
  "alpaca_connected": true,
  "alpaca_result": {
    "account_blocked": false,
    "account_number": "PA3G5ZX0M9BV",
    "cash": "100000",
    "buying_power": "200000",
    "equity": "100000",
    "status": "ACTIVE"
  },
  "configured_stocks": ["AAPL", "TSLA", "GOOGL", "MSFT", "NVDA"],
  "mode": "paper",
  "status": "healthy",
  "trading_active": false
}
```

### **GET /status**
Returns current trading status and portfolio information.

**Request:**
```bash
curl -s http://localhost:8080/status
```

**Response Example:**
```json
{
  "account_balance": "100000",
  "alpaca_connected": true,
  "learning_progress": {},
  "mode": "paper",
  "portfolio": {
    "AAPL": {
      "performance": {
        "balance": 20000.0,
        "position": 0,
        "total_return": 0,
        "total_trades": 0,
        "win_rate": 0
      }
    },
    "GOOGL": {
      "performance": {
        "balance": 20000.0,
        "position": 0,
        "total_return": 0,
        "total_trades": 0,
        "win_rate": 0
      }
    }
  },
  "stocks": ["AAPL", "TSLA", "GOOGL", "MSFT", "NVDA"],
  "timestamp": "2025-08-03T13:08:32.342289",
  "trading_active": false
}
```

---

## 🚀 **Trading Control Endpoints**

### **POST /start**
Starts autonomous trading.

**Request:**
```bash
curl -X POST -s http://localhost:8080/start
```

**Response Example:**
```json
{
  "account_info": {
    "cash": "100000",
    "buying_power": "200000",
    "equity": "100000",
    "status": "ACTIVE"
  },
  "mode": "paper",
  "status": "started",
  "stocks": ["AAPL", "TSLA", "GOOGL", "MSFT", "NVDA"],
  "timestamp": "2025-08-03T13:08:33.468008"
}
```

### **POST /stop**
Stops autonomous trading.

**Request:**
```bash
curl -X POST -s http://localhost:8080/stop
```

**Response Example:**
```json
{
  "status": "stopped",
  "timestamp": "2025-08-03T13:09:57.008825"
}
```

---

## ⚙️ **Configuration Endpoints**

### **POST /switch-mode**
Switches between paper and live trading modes.

**Request:**
```bash
curl -X POST -s http://localhost:8080/switch-mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "live"}'
```

**Body Parameters:**
- `mode` (string, required): "paper" or "live"

**Response Example:**
```json
{
  "mode": "live",
  "timestamp": "2025-08-03T13:10:11.383190",
  "trading_active": true
}
```

### **POST /configure**
Updates the list of stocks to trade.

**Request:**
```bash
curl -X POST -s http://localhost:8080/configure \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "MSFT", "AMD", "NFLX"]}'
```

**Body Parameters:**
- `stocks` (array, required): List of stock symbols

**Response Example:**
```json
{
  "message": "Successfully configured 4 stocks",
  "stocks": ["AAPL", "MSFT", "AMD", "NFLX"],
  "timestamp": "2025-08-03T13:10:14.541900",
  "trading_active": true
}
```

---

## 🤖 **AI Agent Endpoints**

### **GET /evaluate/{symbol}**
Evaluates the performance of a specific AI agent.

**Request:**
```bash
curl -s http://localhost:8080/evaluate/AAPL
```

**Response Example:**
```json
{
  "evaluation": {
    "episode_count": 100,
    "max_drawdown": -0.08,
    "mean_reward": 12.51,
    "sharpe_ratio": 1.42,
    "std_reward": 8.33,
    "success_rate": 0.68,
    "total_reward": 1250.75,
    "trades_count": 45,
    "volatility": 0.15,
    "win_rate": 0.67
  },
  "message": "Agent evaluation completed for AAPL",
  "symbol": "AAPL",
  "timestamp": "2025-08-03T13:10:24.004211"
}
```

### **POST /retrain/{symbol}**
Starts retraining for a specific AI agent.

**Request:**
```bash
curl -X POST -s http://localhost:8080/retrain/MSFT \
  -H "Content-Type: application/json" \
  -d '{"timesteps": 1000}'
```

**Body Parameters:**
- `timesteps` (integer, optional): Number of training steps (default: 50000)

**Response Example:**
```json
{
  "estimated_duration": "10-15 minutes",
  "message": "Retraining started for MSFT with 1000 timesteps",
  "status": "retraining_started",
  "symbol": "MSFT",
  "timestamp": "2025-08-03T13:10:25.717290",
  "timesteps": 1000
}
```

---

## 📋 **Logging Endpoints**

### **GET /logs**
Retrieves recent system logs.

**Request:**
```bash
curl -s http://localhost:8080/logs
```

**Response Example:**
```json
{
  "logs": [
    {
      "level": "INFO",
      "message": "Trading simulation started",
      "timestamp": "2025-08-03 13:08:33"
    },
    {
      "level": "INFO", 
      "message": "Trading simulation stopped",
      "timestamp": "2025-08-03 13:09:57"
    }
  ],
  "count": 5,
  "timestamp": "2025-08-03T13:10:37.318203"
}
```

---

## 🌐 **Frontend API Endpoints**

All frontend API endpoints require authentication (login session) and proxy to the backend.

### **Authentication Required**
All `/api/bot/*` endpoints require a valid Laravel session. Login at `http://localhost:8000/login`.

**Login Credentials:**
- Email: `admin@tradingbot.com`
- Password: `admin123`

### **Frontend Endpoint Mapping**
```
GET  /api/bot/health    → Backend: GET  /health
POST /api/bot/start     → Backend: POST /start  
POST /api/bot/stop      → Backend: POST /stop
GET  /api/bot/status    → Backend: GET  /status
POST /api/bot/switch-mode → Backend: POST /switch-mode
POST /api/bot/configure → Backend: POST /configure
GET  /api/bot/evaluate/{symbol} → Backend: GET /evaluate/{symbol}
POST /api/bot/retrain/{symbol} → Backend: POST /retrain/{symbol}
GET  /api/bot/logs      → Backend: GET  /logs
```

### **Example Frontend API Call**
```javascript
// From authenticated frontend session
fetch('/api/bot/start', {
  method: 'POST',
  headers: {
    'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 🔧 **Error Handling**

### **Common HTTP Status Codes**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `500` - Internal Server Error
- `405` - Method Not Allowed
- `302` - Redirect (authentication required for frontend APIs)

### **Error Response Format**
```json
{
  "error": "Error description",
  "timestamp": "2025-08-03T13:10:25.717290"
}
```

### **Common Errors**
1. **415 Unsupported Media Type**: Missing `Content-Type: application/json` header
2. **500 Internal Server Error**: Backend service not available
3. **302 Redirect**: Authentication required (frontend APIs only)

---

## 🧪 **Testing Examples**

### **Complete Trading Workflow Test**
```bash
# 1. Check system health
curl -s http://localhost:8080/health | jq '.alpaca_connected'

# 2. Configure stocks
curl -X POST -s http://localhost:8080/configure \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "GOOGL", "TSLA"]}' | jq '.stocks'

# 3. Start trading
curl -X POST -s http://localhost:8080/start | jq '.status'

# 4. Check status
curl -s http://localhost:8080/status | jq '.trading_active'

# 5. Stop trading
curl -X POST -s http://localhost:8080/stop | jq '.status'
```

### **AI Agent Testing**
```bash
# Evaluate AAPL agent
curl -s http://localhost:8080/evaluate/AAPL | jq '.evaluation.win_rate'

# Start retraining MSFT agent
curl -X POST -s http://localhost:8080/retrain/MSFT \
  -H "Content-Type: application/json" \
  -d '{"timesteps": 1000}' | jq '.status'
```

---

## 📊 **Rate Limits & Performance**

- **No rate limits** currently implemented
- **Response times**: < 100ms for most endpoints
- **Long-running operations**: `/retrain/{symbol}` may take 10-15 minutes
- **Real-time updates**: Frontend polls every 5 seconds

---

## 🔒 **Security Notes**

1. **Backend API**: No authentication (localhost only)
2. **Frontend API**: Laravel session-based authentication required
3. **CORS**: Enabled for frontend-backend communication
4. **HTTPS**: Not configured (development environment)
5. **API Keys**: Alpaca credentials stored in backend/.env

---

*Last Updated: August 3, 2025*  
*All endpoints tested and verified as working*