# 🧪 Trading Bot Testing Plan

## Automated Testing Strategy

### 1. System Health Tests
- **Objective**: Verify both frontend and backend are operational
- **Frequency**: Before any manual testing
- **Tools**: `test_system.sh`, curl commands

```bash
# Quick health check
curl http://localhost:8080/health
curl http://localhost:8000
```

### 2. API Endpoint Tests
- **Objective**: Validate all backend endpoints function correctly
- **Coverage**: 100% of API endpoints
- **Method**: Automated via `test_system.sh`

#### Core Endpoints Testing Matrix

| Endpoint | Method | Test Data | Expected Result |
|----------|--------|-----------|-----------------|
| `/` | GET | - | `Autonomous Trading Bot API` |
| `/health` | GET | - | `"status": "healthy"` |
| `/status` | GET | - | Portfolio and trading status |
| `/start` | POST | - | Trading started confirmation |
| `/stop` | POST | - | Trading stopped confirmation |
| `/switch-mode` | POST | `{"mode": "paper"}` | Mode switched |
| `/logs` | GET | - | System logs array |
| `/configure` | POST | `{"stocks": ["AAPL"]}` | Configuration updated |
| `/evaluate/AAPL` | GET | - | Agent evaluation data |
| `/retrain/AAPL` | POST | `{"timesteps": 10000}` | Retraining started |

### 3. Frontend Testing

#### Authentication Flow
1. **Login Page Access**
   - Navigate to `/login`
   - Verify form elements present
   - Check CSRF token generation

2. **Login Process**
   - Submit valid credentials
   - Verify redirect to dashboard
   - Check session persistence

3. **Dashboard Access**
   - Verify authenticated access to `/dashboard`
   - Check API data loading
   - Validate UI components

#### Page-by-Page Testing

| Page | URL | Key Elements | API Calls |
|------|-----|--------------|-----------|
| **Welcome** | `/` | Login/Register links | - |
| **Login** | `/login` | Email/Password form | Authentication |
| **Dashboard** | `/dashboard` | Trading controls, Status | `/api/bot/status` |
| **Advanced** | `/advanced` | AI metrics, Agent controls | `/api/bot/status` |
| **Analytics** | `/analytics` | Charts, Performance data | `/api/bot/status` |
| **Logs** | `/logs` | System log display | `/api/bot/logs` |
| **Configuration** | `/configuration` | Stock settings | `/api/bot/configure` |

## Manual Testing Procedures

### 1. Complete System Test (15 minutes)

#### Step 1: System Startup
```bash
# Clean startup
./stop_system.sh
./start_complete_system.sh
# Wait for "System startup complete" message
```

#### Step 2: Backend Verification
```bash
# Run automated tests
./test_system.sh
# Should show >90% success rate
```

#### Step 3: Frontend Authentication
1. Open browser to `http://localhost:8000`
2. Click "Login"
3. Enter credentials:
   - Email: `admin@tradingbot.com`
   - Password: `admin123`
4. Verify redirect to dashboard

#### Step 4: Dashboard Functionality
1. **Connection Status**: Should show green/connected
2. **Trading Controls**: 
   - Click "Start Trading" → Should succeed
   - Click "Stop Trading" → Should succeed
   - Switch mode → Should update status
3. **Stock Management**: 
   - View portfolio data
   - Click "Evaluate Agent" for AAPL
   - Click "Retrain Agent" for any stock

#### Step 5: Advanced Features
1. Navigate to Advanced Dashboard
2. Verify AI system status display
3. Check performance metrics
4. Test agent individual controls

#### Step 6: System Pages
1. **Analytics**: Verify charts/metrics load
2. **Logs**: Check system logs display
3. **Configuration**: Test stock configuration

### 2. Load Testing (5 minutes)

#### Basic Concurrency Test
```bash
# Test concurrent API requests
for i in {1..10}; do
    curl -s http://localhost:8080/status &
done
wait

# Test frontend under load
for i in {1..5}; do
    curl -s http://localhost:8000/dashboard &
done
wait
```

#### Extended Session Test
1. Keep dashboard open for 30 minutes
2. Perform various actions every 5 minutes
3. Verify no memory leaks or session issues

### 3. Error Condition Testing

#### Backend Error Tests
```bash
# Test invalid requests
curl -X POST http://localhost:8080/configure -d '{"invalid": "data"}'
curl http://localhost:8080/evaluate/INVALID
curl -X POST http://localhost:8080/switch-mode -d '{"mode": "invalid"}'
```

#### Frontend Error Tests
1. Try invalid login credentials
2. Access protected pages without authentication
3. Test with backend temporarily down

### 4. Integration Testing

#### API-Frontend Integration
1. Start trading via API: `curl -X POST http://localhost:8080/start`
2. Verify dashboard reflects change immediately
3. Configure stocks via API: `curl -X POST http://localhost:8080/configure -d '{"stocks": ["AAPL"]}'`
4. Verify configuration page shows update

#### Real-time Updates
1. Start trading in dashboard
2. Monitor status in another browser tab
3. Verify consistent state across sessions

## Continuous Testing Strategy

### Pre-Commit Testing
```bash
# Before any code changes
./test_system.sh
```

### Post-Change Testing
```bash
# After any modifications
./stop_system.sh
./start_complete_system.sh
./test_system.sh
# Manual verification of changed features
```

### Daily Health Check
```bash
# Morning system verification
./start_complete_system.sh
./test_system.sh
# Verify login flow manually
```

## Performance Benchmarks

### Response Time Targets
- API endpoints: < 500ms
- Page loads: < 2 seconds
- Authentication: < 1 second

### Reliability Targets
- System uptime: 99.9%
- API success rate: 99.5%
- Frontend availability: 99.9%

## Test Data Management

### Default Test Data
- **User**: admin@tradingbot.com / admin123
- **Stocks**: AAPL, TSLA, GOOGL, MSFT, NVDA
- **Mode**: Paper trading
- **Balance**: $100,000

### Test Environment Reset
```bash
cd frontend
php artisan migrate:fresh --seed
php artisan config:clear
php artisan config:cache
```

## Regression Testing Checklist

### After Backend Changes
- [ ] All API endpoints respond correctly
- [ ] Authentication still works
- [ ] Trading controls function
- [ ] Configuration saves properly
- [ ] Logs display correctly

### After Frontend Changes
- [ ] All pages load without errors
- [ ] Navigation works correctly
- [ ] Forms submit successfully
- [ ] API integration intact
- [ ] Responsive design maintained

### After Configuration Changes
- [ ] Environment variables applied
- [ ] Database connections work
- [ ] API endpoints accessible
- [ ] Assets build correctly
- [ ] Dependencies resolved

## Bug Reporting Template

```markdown
## Bug Report

**Environment**: Development/Production
**Date**: YYYY-MM-DD
**Severity**: High/Medium/Low

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Result**: What should happen
**Actual Result**: What actually happened
**Error Messages**: Any console/log errors
**Browser/OS**: If frontend issue
**API Response**: If backend issue

**Additional Context**: Screenshots, logs, etc.
```

## Testing Tools

### Required Tools
- `curl` - API testing
- Web browser - Frontend testing
- Terminal - Script execution

### Optional Tools
- Postman - Advanced API testing
- Browser dev tools - Frontend debugging
- Artillery/k6 - Load testing
- Lighthouse - Performance auditing

## Success Criteria

### System is considered HEALTHY when:
- `./test_system.sh` shows >95% success rate
- All manual testing steps pass
- No critical errors in logs
- Response times within targets
- User can complete full workflow

### System requires ATTENTION when:
- Test success rate <90%
- Any critical functionality fails
- Consistent slow response times
- Authentication issues
- Data corruption signs