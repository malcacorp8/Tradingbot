#!/usr/bin/env node

/**
 * Test script for Browser MCP with Trading Bot Application
 * This script demonstrates how to use Browser MCP to test the trading bot
 */

const { spawn } = require('child_process');

console.log('🧪 Testing Browser MCP with Trading Bot Application');
console.log('==================================================');

// Test if the trading bot is running
async function testTradingBot() {
    console.log('\n🔍 Checking if trading bot is running...');
    
    try {
        const response = await fetch('http://localhost:8000');
        if (response.ok) {
            console.log('✅ Trading bot frontend is running on http://localhost:8000');
            return true;
        }
    } catch (error) {
        console.log('❌ Trading bot frontend is not running');
        return false;
    }
}

// Test if backend is running
async function testBackend() {
    console.log('\n🔍 Checking if backend is running...');
    
    try {
        const response = await fetch('http://localhost:8080/health');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend is running and healthy');
            console.log(`   Alpaca Connected: ${data.alpaca_connected ? '✅' : '❌'}`);
            console.log(`   Trading Mode: ${data.mode}`);
            return true;
        }
    } catch (error) {
        console.log('❌ Backend is not running');
        return false;
    }
}

// Instructions for using Browser MCP
function showBrowserMCPInstructions() {
    console.log('\n🌐 Browser MCP Setup Instructions');
    console.log('==================================');
    console.log('1. Browser MCP is now configured in your Cursor MCP settings');
    console.log('2. Restart Cursor to load the new MCP configuration');
    console.log('3. Once restarted, you can use Browser MCP commands like:');
    console.log('   - Navigate to http://localhost:8000');
    console.log('   - Test the login functionality');
    console.log('   - Test the Advanced Training page');
    console.log('   - Test stock search functionality');
    console.log('   - Test model training features');
    console.log('\n📝 Example Browser MCP Commands:');
    console.log('   - "Go to http://localhost:8000"');
    console.log('   - "Click the login button"');
    console.log('   - "Enter admin@tradingbot.com in the email field"');
    console.log('   - "Enter admin123 in the password field"');
    console.log('   - "Navigate to the Advanced Training page"');
    console.log('   - "Search for AAPL stock"');
}

// Main test function
async function main() {
    console.log('🚀 Starting Browser MCP Test...\n');
    
    const frontendRunning = await testTradingBot();
    const backendRunning = await testBackend();
    
    if (frontendRunning && backendRunning) {
        console.log('\n🎉 Trading Bot System is ready for Browser MCP testing!');
        showBrowserMCPInstructions();
    } else {
        console.log('\n⚠️  Please start the trading bot system first:');
        console.log('   Run: ./start_complete_system.sh');
        console.log('\nThen restart Cursor and try Browser MCP again.');
    }
}

// Run the test
main().catch(console.error); 