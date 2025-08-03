#!/bin/bash

# Comprehensive System Testing Script
# Tests all functionality of the trading bot system

echo "🧪 Trading Bot System Comprehensive Test"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "🔍 Testing $test_name... "
    
    # Run the test command
    result=$(eval "$test_command" 2>/dev/null)
    
    # Check if the expected pattern is found
    if echo "$result" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "   Expected: $expected_pattern"
        echo "   Got: $result"
        return 1
    fi
}

# Function to test API endpoint
test_api() {
    local endpoint="$1"
    local method="$2"
    local data="$3"
    local expected="$4"
    
    if [ "$method" = "POST" ]; then
        run_test "$endpoint ($method)" "curl -s -X POST http://localhost:8080$endpoint -H 'Content-Type: application/json' -d '$data'" "$expected"
    else
        run_test "$endpoint ($method)" "curl -s http://localhost:8080$endpoint" "$expected"
    fi
}

# Function to test frontend endpoint
test_frontend() {
    local endpoint="$1"
    local expected="$2"
    
    run_test "Frontend $endpoint" "curl -s http://localhost:8000$endpoint" "$expected"
}

echo ""
echo "📋 Pre-Test Checks"
echo "=================="

# Check if backend is running
if ! curl -s http://localhost:8080/health > /dev/null; then
    echo -e "${RED}❌ Backend server is not running on port 8080${NC}"
    echo "   Please run: ./start_complete_system.sh"
    exit 1
else
    echo -e "${GREEN}✅ Backend server is running${NC}"
fi

# Check if frontend is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo -e "${RED}❌ Frontend server is not running on port 8000${NC}"
    echo "   Please run: ./start_complete_system.sh"
    exit 1
else
    echo -e "${GREEN}✅ Frontend server is running${NC}"
fi

echo ""
echo "🔧 Backend API Tests"
echo "==================="

# Core endpoints
test_api "/" "GET" "" "Autonomous Trading Bot API"
test_api "/health" "GET" "" "healthy"
test_api "/status" "GET" "" "trading_active"

# Trading controls
test_api "/start" "POST" "" "started"
test_api "/stop" "POST" "" "stopped"
test_api "/switch-mode" "POST" '{"mode": "paper"}' "paper"

# New endpoints
test_api "/logs" "GET" "" "logs"
test_api "/configure" "POST" '{"stocks": ["AAPL", "TSLA"]}' "Successfully configured"
test_api "/evaluate/AAPL" "GET" "" "evaluation"
test_api "/retrain/AAPL" "POST" '{"timesteps": 10000}' "retraining_started"

echo ""
echo "🌐 Frontend Tests"
echo "================"

# Frontend pages
test_frontend "/" "Laravel"
test_frontend "/login" "Login"

echo ""
echo "🔐 Authentication Test"
echo "====================="

# Test login functionality
echo "🔍 Testing login system..."

# Get CSRF token
CSRF_TOKEN=$(curl -s http://localhost:8000/login | grep -o 'csrf-token.*content="[^"]*"' | sed 's/.*content="\([^"]*\)".*/\1/' | head -1)

if [ -n "$CSRF_TOKEN" ]; then
    echo -e "${GREEN}✅ CSRF token retrieved${NC}"
    
    # Test login
    LOGIN_RESULT=$(curl -s -c cookies.txt -b cookies.txt -X POST http://localhost:8000/login \
        -d "email=admin@tradingbot.com&password=admin123&_token=$CSRF_TOKEN" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -w "%{http_code}")
    
    if echo "$LOGIN_RESULT" | grep -q "302"; then
        echo -e "${GREEN}✅ Login successful (redirect received)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ Login failed${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${RED}❌ Could not retrieve CSRF token${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""
echo "📊 Load Test (Basic)"
echo "==================="

echo "🔍 Running basic load test..."

# Test multiple concurrent requests
for i in {1..5}; do
    curl -s http://localhost:8080/status > /dev/null &
done
wait

echo -e "${GREEN}✅ Concurrent request test completed${NC}"

echo ""
echo "📈 Test Results Summary"
echo "======================"

echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

# Calculate success rate
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Success Rate: $SUCCESS_RATE%"
    
    if [ $SUCCESS_RATE -ge 90 ]; then
        echo -e "${GREEN}🎉 EXCELLENT: System is functioning very well!${NC}"
        exit 0
    elif [ $SUCCESS_RATE -ge 75 ]; then
        echo -e "${YELLOW}⚠️  GOOD: System is mostly functional with minor issues${NC}"
        exit 0
    else
        echo -e "${RED}❌ POOR: System has significant issues that need attention${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ No tests were run${NC}"
    exit 1
fi