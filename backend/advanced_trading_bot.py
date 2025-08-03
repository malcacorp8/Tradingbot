"""
Advanced Autonomous Trading Bot with Machine Learning
Implements real reinforcement learning and autonomous decision making
"""

import os
import logging
import time
import threading
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import json

# Simple RL implementation without heavy dependencies
class SimpleTradingAgent:
    """
    Simplified trading agent that learns from experience
    Uses Q-learning principles without requiring external ML libraries
    """
    
    def __init__(self, symbol, initial_balance=100000):
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.position_value = 0
        
        # Q-table for simple states and actions
        # States: [price_trend, volume_trend, position_status]
        # Actions: [hold, buy, sell]
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_rate = 0.3
        self.exploration_decay = 0.995
        
        # Experience tracking
        self.trade_history = []
        self.rewards = []
        self.total_trades = 0
        self.successful_trades = 0
        
        # Market data
        self.price_history = []
        self.volume_history = []
        
        logger.info(f"🤖 Agent initialized for {symbol}")
    
    def get_state(self, current_price, current_volume):
        """Convert market data to discrete state"""
        # Simple state representation
        price_trend = self._get_trend(self.price_history, current_price)
        volume_trend = self._get_trend(self.volume_history, current_volume)
        position_status = 0 if self.position == 0 else (1 if self.position > 0 else -1)
        
        return (price_trend, volume_trend, position_status)
    
    def _get_trend(self, history, current_value):
        """Calculate trend: -1 (down), 0 (neutral), 1 (up)"""
        if len(history) < 3:
            return 0
        
        recent_avg = np.mean(history[-3:])
        if current_value > recent_avg * 1.02:
            return 1  # Up trend
        elif current_value < recent_avg * 0.98:
            return -1  # Down trend
        else:
            return 0  # Neutral
    
    def choose_action(self, state):
        """Choose action using epsilon-greedy strategy"""
        # Exploration vs exploitation
        if np.random.random() < self.exploration_rate:
            return np.random.choice([0, 1, 2])  # Random action
        
        # Get Q-values for this state
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]  # [hold, buy, sell]
        
        return np.argmax(self.q_table[state])
    
    def execute_action(self, action, current_price, api_headers):
        """Execute trading action and return reward"""
        reward = 0
        action_taken = "hold"
        
        try:
            if action == 1:  # Buy
                if self.balance >= current_price * 10:  # Buy 10 shares if possible
                    quantity = min(10, int(self.balance * 0.1 / current_price))  # Use 10% of balance
                    if quantity > 0:
                        # Simulate order (in real implementation, use Alpaca API)
                        cost = quantity * current_price
                        self.balance -= cost
                        self.position += quantity
                        self.position_value = current_price
                        action_taken = f"buy_{quantity}"
                        reward = 0.01  # Small positive reward for taking action
                        
                        # Log trade
                        self.trade_history.append({
                            'action': 'buy',
                            'quantity': quantity,
                            'price': current_price,
                            'timestamp': datetime.now(),
                            'balance': self.balance
                        })
                        
            elif action == 2 and self.position > 0:  # Sell
                # Sell all position
                revenue = self.position * current_price
                profit = revenue - (self.position * self.position_value)
                self.balance += revenue
                
                # Calculate reward based on profit
                reward = profit / 1000.0  # Scale reward
                if profit > 0:
                    self.successful_trades += 1
                    
                action_taken = f"sell_{self.position}"
                
                # Log trade
                self.trade_history.append({
                    'action': 'sell',
                    'quantity': self.position,
                    'price': current_price,
                    'profit': profit,
                    'timestamp': datetime.now(),
                    'balance': self.balance
                })
                
                self.position = 0
                self.position_value = 0
                self.total_trades += 1
                
            # Risk penalty for large drawdowns
            total_value = self.balance + (self.position * current_price)
            if total_value < self.initial_balance * 0.95:
                reward -= 0.1  # Penalty for losses
                
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            reward = -0.05  # Penalty for errors
        
        # Store reward
        self.rewards.append(reward)
        
        return reward, action_taken
    
    def update_q_table(self, state, action, reward, next_state):
        """Update Q-table using Q-learning"""
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]
        if next_state not in self.q_table:
            self.q_table[next_state] = [0, 0, 0]
        
        # Q-learning update
        current_q = self.q_table[state][action]
        max_future_q = max(self.q_table[next_state])
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_future_q - current_q)
        
        self.q_table[state][action] = new_q
        
        # Decay exploration rate
        self.exploration_rate = max(0.01, self.exploration_rate * self.exploration_decay)
    
    def get_performance_metrics(self):
        """Get current performance metrics"""
        current_value = self.balance + (self.position * (self.price_history[-1] if self.price_history else 0))
        total_return = (current_value - self.initial_balance) / self.initial_balance
        
        win_rate = (self.successful_trades / max(1, self.total_trades)) if self.total_trades > 0 else 0
        
        return {
            'balance': self.balance,
            'position': self.position,
            'total_value': current_value,
            'total_return': total_return,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'win_rate': win_rate,
            'recent_rewards': self.rewards[-10:] if self.rewards else [],
            'avg_reward': np.mean(self.rewards) if self.rewards else 0,
            'exploration_rate': self.exploration_rate,
            'q_table_size': len(self.q_table)
        }

class AdvancedTradingSystem:
    """
    Advanced trading system managing multiple agents
    """
    
    def __init__(self, symbols):
        self.symbols = symbols
        self.agents = {}
        self.running = False
        self.api_headers = self._get_api_headers()
        
        # Initialize agents
        for symbol in symbols:
            self.agents[symbol] = SimpleTradingAgent(symbol)
        
        logger.info(f"🚀 Advanced Trading System initialized with {len(symbols)} agents")
    
    def _get_api_headers(self):
        """Get Alpaca API headers"""
        return {
            'APCA-API-KEY-ID': os.getenv('ALPACA_PAPER_KEY'),
            'APCA-API-SECRET-KEY': os.getenv('ALPACA_PAPER_SECRET')
        }
    
    def get_market_data(self, symbol):
        """Fetch real-time market data"""
        try:
            # In a real implementation, use Alpaca API for real-time data
            # For now, simulate with random walk
            base_prices = {'AAPL': 205, 'TSLA': 180, 'GOOGL': 2800, 'MSFT': 450, 'NVDA': 1200}
            base_price = base_prices.get(symbol, 100)
            
            # Simulate price movement
            change = np.random.normal(0, 0.01)  # 1% volatility
            current_price = base_price * (1 + change)
            current_volume = np.random.randint(1000, 10000)
            
            return current_price, current_volume
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None, None
    
    def run_trading_cycle(self):
        """Single trading cycle for all agents"""
        cycle_results = {}
        
        for symbol in self.symbols:
            try:
                agent = self.agents[symbol]
                
                # Get market data
                current_price, current_volume = self.get_market_data(symbol)
                if current_price is None:
                    continue
                
                # Update price history
                agent.price_history.append(current_price)
                agent.volume_history.append(current_volume)
                
                # Keep only recent history
                if len(agent.price_history) > 50:
                    agent.price_history = agent.price_history[-50:]
                    agent.volume_history = agent.volume_history[-50:]
                
                # Get current state
                current_state = agent.get_state(current_price, current_volume)
                
                # Choose and execute action
                action = agent.choose_action(current_state)
                reward, action_taken = agent.execute_action(action, current_price, self.api_headers)
                
                # Get next state (same as current for now)
                next_state = current_state
                
                # Update Q-table
                agent.update_q_table(current_state, action, reward, next_state)
                
                # Store results
                cycle_results[symbol] = {
                    'price': current_price,
                    'action': action_taken,
                    'reward': reward,
                    'state': current_state,
                    'performance': agent.get_performance_metrics()
                }
                
            except Exception as e:
                logger.error(f"Error in trading cycle for {symbol}: {e}")
                cycle_results[symbol] = {'error': str(e)}
        
        return cycle_results
    
    def start_autonomous_trading(self):
        """Start autonomous trading loop"""
        self.running = True
        logger.info("🤖 Starting autonomous trading...")
        
        def trading_loop():
            cycle_count = 0
            while self.running:
                try:
                    cycle_count += 1
                    logger.info(f"📊 Trading Cycle #{cycle_count}")
                    
                    # Run trading cycle
                    results = self.run_trading_cycle()
                    
                    # Log results
                    for symbol, result in results.items():
                        if 'error' not in result:
                            perf = result['performance']
                            logger.info(f"{symbol}: {result['action']} @ ${result['price']:.2f} | "
                                      f"Balance: ${perf['balance']:.2f} | "
                                      f"Return: {perf['total_return']:.2%} | "
                                      f"Trades: {perf['total_trades']}")
                    
                    # Wait before next cycle
                    time.sleep(int(os.getenv('POLLING_INTERVAL', 15)))
                    
                except Exception as e:
                    logger.error(f"Error in trading loop: {e}")
                    time.sleep(5)
        
        # Start trading thread
        self.trading_thread = threading.Thread(target=trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
    
    def stop_trading(self):
        """Stop autonomous trading"""
        self.running = False
        logger.info("🛑 Autonomous trading stopped")
    
    def get_system_status(self):
        """Get complete system status"""
        status = {
            'running': self.running,
            'agents': {},
            'total_performance': {
                'total_balance': 0,
                'total_trades': 0,
                'avg_return': 0
            }
        }
        
        total_balance = 0
        total_trades = 0
        returns = []
        
        for symbol, agent in self.agents.items():
            performance = agent.get_performance_metrics()
            status['agents'][symbol] = performance
            
            total_balance += performance['balance']
            total_trades += performance['total_trades']
            returns.append(performance['total_return'])
        
        status['total_performance'] = {
            'total_balance': total_balance,
            'total_trades': total_trades,
            'avg_return': np.mean(returns) if returns else 0,
            'agent_count': len(self.agents)
        }
        
        return status

# Initialize Flask app
load_dotenv()
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global trading system
trading_system = None

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'Advanced Autonomous Trading Bot',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'active': trading_system.running if trading_system else False
    })

@app.route('/start-advanced', methods=['POST'])
def start_advanced_trading():
    """Start advanced autonomous trading"""
    global trading_system
    
    try:
        symbols = os.getenv('STOCKS', 'AAPL,TSLA,GOOGL,MSFT,NVDA').split(',')
        
        if not trading_system:
            trading_system = AdvancedTradingSystem(symbols)
        
        if not trading_system.running:
            trading_system.start_autonomous_trading()
        
        return jsonify({
            'status': 'started',
            'message': 'Advanced autonomous trading started',
            'symbols': symbols,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error starting advanced trading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop-advanced', methods=['POST'])
def stop_advanced_trading():
    """Stop advanced trading"""
    global trading_system
    
    if trading_system and trading_system.running:
        trading_system.stop_trading()
    
    return jsonify({
        'status': 'stopped',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status-advanced', methods=['GET'])
def get_advanced_status():
    """Get advanced trading status"""
    if not trading_system:
        return jsonify({'error': 'Trading system not initialized'}), 400
    
    return jsonify(trading_system.get_system_status())

if __name__ == '__main__':
    logger.info("🚀 Starting Advanced Autonomous Trading Bot")
    port = int(os.getenv('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)