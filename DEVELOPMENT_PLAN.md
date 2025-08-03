# 🚀 Trading Bot Development Plan

## System Architecture

### Backend (Port 8080)
- **Framework**: Flask with CORS
- **Language**: Python 3.13+
- **Main File**: `backend/simple_app.py`
- **Environment**: Virtual environment in `backend/env/`
- **Dependencies**: Flask, Flask-CORS, python-dotenv, requests

### Frontend (Port 8000)
- **Framework**: Laravel with Inertia.js
- **Frontend Tech**: Vue.js 3, Tailwind CSS
- **Language**: PHP 8.2+, JavaScript (Vue)
- **Database**: SQLite
- **Build Tool**: Vite

## Development Workflow

### 1. Environment Setup
```bash
# Complete system startup
./start_complete_system.sh

# Individual components
./start_backend.sh    # Backend only
./start_frontend.sh   # Frontend only
```

### 2. Development Commands
```bash
# Backend development
cd backend
source env/bin/activate
python3 simple_app.py

# Frontend development  
cd frontend
php artisan serve --port=8000
npm run dev  # For hot reloading
```

### 3. Testing
```bash
# Run comprehensive tests
./test_system.sh

# Manual API testing
curl http://localhost:8080/health
curl http://localhost:8080/status
```

## API Endpoints

### Core Trading Endpoints
- `GET /` - API status
- `GET /health` - System health check
- `GET /status` - Trading status and portfolio
- `POST /start` - Start trading
- `POST /stop` - Stop trading
- `POST /switch-mode` - Switch paper/live mode

### Management Endpoints
- `GET /logs` - System logs
- `POST /configure` - Configure stocks
- `GET /evaluate/{symbol}` - Evaluate agent
- `POST /retrain/{symbol}` - Retrain agent

### Frontend Routes
- `/` - Welcome page
- `/login` - Authentication
- `/dashboard` - Main dashboard
- `/advanced` - Advanced AI dashboard
- `/analytics` - Analytics page
- `/logs` - System logs
- `/configuration` - Settings

## Configuration

### Backend Environment Variables
```env
# Alpaca API (Paper Trading)
ALPACA_PAPER_KEY=your_paper_key
ALPACA_PAPER_SECRET=your_paper_secret

# Trading Settings
MODE=paper
STOCKS=AAPL,TSLA,GOOGL,MSFT,NVDA
PORT=8080
```

### Frontend Environment Variables
```env
# Laravel Settings
APP_KEY=base64:generated_key
DB_CONNECTION=sqlite
DB_DATABASE=database/database.sqlite

# Backend Connection
BACKEND_URL=http://localhost:8080
```

## Development Best Practices

### 1. Code Changes
- Backend changes: Restart `python3 simple_app.py`
- Frontend PHP changes: Restart `php artisan serve`
- Frontend JS/CSS changes: Run `npm run build`

### 2. Testing Protocol
1. Run `./test_system.sh` after changes
2. Test authentication flow manually
3. Verify all dashboard features work
4. Check API endpoints with curl

### 3. Database Changes
```bash
cd frontend
php artisan migrate:fresh --seed
```

### 4. Asset Building
```bash
cd frontend
npm run build  # Production build
npm run dev    # Development with hot reload
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   ./stop_system.sh
   pkill -f simple_app.py
   pkill -f "php artisan serve"
   ```

2. **Backend Won't Start**
   ```bash
   cd backend
   source env/bin/activate
   pip install flask flask-cors python-dotenv requests
   ```

3. **Frontend Assets Missing**
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   npm run build
   ```

4. **Authentication Issues**
   ```bash
   cd frontend
   php artisan key:generate
   php artisan config:clear
   php artisan config:cache
   ```

### Log Locations
- Backend: Console output when running `simple_app.py`
- Frontend: Laravel logs in `frontend/storage/logs/`
- Web server: Browser developer tools

## Deployment Considerations

### Production Setup
1. Change `debug=False` in backend
2. Use proper web server (nginx + gunicorn)
3. Use production database (PostgreSQL/MySQL)
4. Set up proper SSL certificates
5. Configure environment variables securely

### Security
- Never commit API keys to git
- Use strong APP_KEY for Laravel
- Enable CSRF protection
- Use HTTPS in production
- Implement rate limiting

## Extensions and Customization

### Adding New Stocks
1. Update `STOCKS` environment variable
2. Restart backend
3. Test with `/configure` endpoint

### Adding New Features
1. Add API endpoint to `simple_app.py`
2. Add frontend route to `routes/web.php`
3. Create Vue component if needed
4. Update test script

### Monitoring
- Health check: `GET /health`
- System status: `GET /status`
- Logs: `GET /logs`
- Frontend monitoring via browser tools