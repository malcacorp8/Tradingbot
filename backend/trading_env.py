"""
Reinforcement Learning Trading Environment
Implements a Gym environment for autonomous trading with self-learning capabilities
"""

import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces
import yfinance as yf
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import ta
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import new components
from news_analyzer import NewsAnalyzer
from risk_manager import RiskManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingEnvironment(gym.Env):
    """
    Custom Gym environment for stock trading with sentiment analysis and technical indicators
    Supports autonomous learning and per-stock optimization
    """
    
    def __init__(self, symbol, initial_balance=100000, max_steps=1000, transaction_fee=0.001, mode='paper'):
        super().__init__()
        
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.max_steps = max_steps
        self.transaction_fee = transaction_fee
        self.mode = mode
        
        # Initialize components
        self.news_analyzer = NewsAnalyzer()
        self.risk_manager = RiskManager(mode=mode)
        
        # Initialize sentiment analysis model (FinBERT)
        try:
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            self.sentiment_pipeline = pipeline("sentiment-analysis", 
                                              model=self.sentiment_model, 
                                              tokenizer=self.sentiment_tokenizer)
        except Exception as e:
            logger.warning(f"Could not load FinBERT model: {e}. Using default sentiment.")
            self.sentiment_pipeline = None
        
        # Action space: 0=Hold, 1=Buy, 2=Sell, 3=Buy Call, 4=Buy Put
        self.action_space = spaces.Discrete(5)
        
        # Enhanced observation space: [price, volume, rsi, macd, sentiment, position, balance_ratio, volatility, news_count]
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(9,), 
            dtype=np.float32
        )
        
        # Trading state
        self.reset()
        
        # Historical data for learning
        self.history = []
        self.performance_history = []
        
    def reset(self, seed=None):
        """Reset the environment to initial state"""
        super().reset(seed=seed)
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0  # Number of shares held
        self.position_value = 0
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit = 0
        
        # Fetch recent market data
        self._fetch_market_data()
        
        return self._get_observation(), {}
    
    def _fetch_market_data(self):
        """Fetch real-time market data for the symbol"""
        try:
            # Get recent data (last 30 days for technical indicators)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            self.data = yf.download(self.symbol, start=start_date, end=end_date, interval="1m")
            
            if len(self.data) == 0:
                logger.error(f"No data available for {self.symbol}")
                # Create dummy data for testing
                self.data = pd.DataFrame({
                    'Open': [100] * 100,
                    'High': [101] * 100,
                    'Low': [99] * 100,
                    'Close': [100] * 100,
                    'Volume': [1000] * 100
                })
            
            # Calculate technical indicators
            self._calculate_indicators()
            
        except Exception as e:
            logger.error(f"Error fetching data for {self.symbol}: {e}")
            # Fallback to dummy data
            self.data = pd.DataFrame({
                'Open': [100] * 100,
                'High': [101] * 100,
                'Low': [99] * 100,
                'Close': [100] * 100,
                'Volume': [1000] * 100
            })
            self._calculate_indicators()
    
    def _calculate_indicators(self):
        """Calculate technical indicators"""
        if len(self.data) < 20:
            # Not enough data for indicators
            self.data['RSI'] = 50
            self.data['MACD'] = 0
            self.data['Signal'] = 0
            return
        
        # RSI
        self.data['RSI'] = ta.momentum.RSIIndicator(self.data['Close']).rsi()
        
        # MACD
        macd_indicator = ta.trend.MACD(self.data['Close'])
        self.data['MACD'] = macd_indicator.macd()
        self.data['Signal'] = macd_indicator.macd_signal()
        
        # Moving averages
        self.data['MA_20'] = ta.trend.SMAIndicator(self.data['Close'], window=20).sma_indicator()
        
        # Fill NaN values
        self.data.fillna(method='bfill', inplace=True)
        self.data.fillna(0, inplace=True)
    
    def _get_sentiment_score(self):
        """Get sentiment score using real-time news analysis"""
        try:
            # Get real-time news sentiment
            sentiment_data = self.news_analyzer.get_news_sentiment(self.symbol, hours_back=24)
            return sentiment_data.get('sentiment_score', 0.5)
        except Exception as e:
            logger.warning(f"Error getting sentiment: {e}")
            return 0.5
    
    def _get_observation(self):
        """Get current observation state"""
        if len(self.data) == 0:
            return np.zeros(9, dtype=np.float32) # Updated shape
        
        current_idx = min(self.current_step, len(self.data) - 1)
        
        # Current market data
        current_price = float(self.data['Close'].iloc[current_idx])
        volume = float(self.data['Volume'].iloc[current_idx])
        rsi = float(self.data['RSI'].iloc[current_idx])
        macd = float(self.data['MACD'].iloc[current_idx])
        
        # Sentiment analysis
        sentiment = self._get_sentiment_score()
        
        # Trading state
        position_ratio = self.position / 100.0  # Normalize position
        balance_ratio = self.balance / self.initial_balance
        
        # Risk management and news analysis
        volatility = self._calculate_volatility()
        news_data = self.news_analyzer.get_news_sentiment(self.symbol, hours_back=24)
        news_count = news_data.get('news_count', 0) / 100.0  # Normalize news count
        
        observation = np.array([
            current_price / 100.0,  # Normalize price
            volume / 1000.0,       # Normalize volume
            rsi / 100.0,           # Normalize RSI
            np.tanh(macd),         # Normalize MACD
            sentiment,             # Sentiment score [0,1]
            position_ratio,        # Position ratio
            balance_ratio,         # Balance ratio
            volatility,            # Volatility
            news_count             # News count
        ], dtype=np.float32)
        
        return observation
    
    def step(self, action):
        """Execute a trading action and return new state"""
        if len(self.data) == 0:
            return self._get_observation(), 0, True, True, {}
        
        current_idx = min(self.current_step, len(self.data) - 1)
        current_price = float(self.data['Close'].iloc[current_idx])
        
        reward = 0
        info = {}
        
        # Execute action
        if action == 1:  # Buy
            reward = self._execute_buy(current_price)
            info['action'] = 'buy'
        elif action == 2:  # Sell
            reward = self._execute_sell(current_price)
            info['action'] = 'sell'
        elif action == 3:  # Buy Call (simplified)
            reward = self._execute_options(current_price, 'call')
            info['action'] = 'buy_call'
        elif action == 4:  # Buy Put (simplified)
            reward = self._execute_options(current_price, 'put')
            info['action'] = 'buy_put'
        else:  # Hold
            reward = self._calculate_holding_reward(current_price)
            info['action'] = 'hold'
        
        # Risk management penalties
        reward -= self._calculate_risk_penalty()
        
        # Update step
        self.current_step += 1
        
        # Check if episode is done
        done = (self.current_step >= self.max_steps or 
                self.current_step >= len(self.data) or
                self.balance <= 0)
        
        # Store performance data
        self.performance_history.append({
            'step': self.current_step,
            'balance': self.balance,
            'position': self.position,
            'action': action,
            'reward': reward,
            'price': current_price
        })
        
        info.update({
            'balance': self.balance,
            'position': self.position,
            'total_trades': self.total_trades,
            'profit': self.total_profit,
            'price': current_price
        })
        
        return self._get_observation(), reward, done, False, info
    
    def _execute_buy(self, price):
        """Execute buy action with enhanced risk management"""
        if self.balance < price * (1 + self.transaction_fee):
            return -0.1  # Penalty for invalid trade
        
        # Calculate position size using risk manager
        quantity = self.risk_manager.calculate_position_size(self.symbol, price)
        
        if quantity <= 0:
            return -0.1
        
        # Check risk limits
        risk_check = self.risk_manager.check_risk_limits(self.symbol, 'buy', quantity, price)
        if not risk_check['approved']:
            logger.warning(f"Risk check failed for {self.symbol}: {risk_check['rejections']}")
            return -0.2  # Penalty for risk limit violation
        
        # Execute trade
        cost = quantity * price * (1 + self.transaction_fee)
        if cost <= self.balance:
            self.balance -= cost
            self.position += quantity
            self.position_value = price
            self.total_trades += 1
            
            # Update risk metrics
            self.risk_manager.update_risk_metrics(self.symbol, 'buy', quantity, price)
            
            return 0.01  # Small positive reward for successful trade
        else:
            return -0.1  # Penalty for insufficient funds
    
    def _execute_sell(self, price):
        """Execute sell order"""
        if self.position <= 0:
            return -0.1  # Penalty for invalid trade
        
        # Sell all shares
        revenue = self.position * price * (1 - self.transaction_fee)
        self.balance += revenue
        
        # Calculate profit
        profit = revenue - (self.position * self.position_value)
        self.total_profit += profit
        
        if profit > 0:
            self.successful_trades += 1
            reward = profit / 1000.0  # Scale reward
        else:
            reward = profit / 1000.0  # Negative reward for loss
        
        self.position = 0
        self.total_trades += 1
        
        return reward
    
    def _execute_options(self, price, option_type):
        """Simplified options trading"""
        if self.balance < price * 0.1:  # Options premium
            return -0.1
        
        premium = price * 0.05  # Simplified premium calculation
        self.balance -= premium
        self.total_trades += 1
        
        # Simplified profit calculation based on volatility
        volatility_reward = np.random.normal(0, 0.02)
        
        if option_type == 'call':
            return volatility_reward * 2  # Amplified for options
        else:  # put
            return -volatility_reward * 2
    
    def _calculate_holding_reward(self, current_price):
        """Calculate reward for holding position"""
        if self.position > 0:
            # Small positive reward for holding profitable positions
            price_change = (current_price - self.position_value) / self.position_value if self.position_value > 0 else 0
            return price_change * 0.1
        return 0
    
    def _calculate_volatility(self):
        """Calculate current volatility"""
        if len(self.data) < 5:
            return 0.0
        
        try:
            # Calculate rolling volatility
            returns = self.data['Close'].pct_change().dropna()
            if len(returns) > 0:
                volatility = returns.std() * np.sqrt(252)  # Annualized
                return min(volatility, 1.0)  # Cap at 100%
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
    def _calculate_risk_penalty(self):
        """Calculate risk-based penalties"""
        penalty = 0
        
        # Portfolio concentration penalty
        if self.position > 0:
            position_value = self.position * self.data['Close'].iloc[min(self.current_step, len(self.data)-1)]
            concentration = position_value / (self.balance + position_value)
            if concentration > 0.2:  # More than 20% in one stock
                penalty += (concentration - 0.2) * 0.1
        
        # High volatility penalty
        if len(self.data) > 5:
            recent_volatility = self.data['Close'].tail(5).std()
            if recent_volatility > 5:  # High volatility
                penalty += 0.01
        
        return penalty
    
    def get_performance_metrics(self):
        """Get current performance metrics"""
        if self.total_trades == 0:
            return {'win_rate': 0, 'total_return': 0, 'sharpe_ratio': 0}
        
        win_rate = self.successful_trades / self.total_trades
        total_return = (self.balance - self.initial_balance) / self.initial_balance
        
        # Simple Sharpe ratio calculation
        if len(self.performance_history) > 1:
            returns = [p['reward'] for p in self.performance_history]
            sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-6)
        else:
            sharpe_ratio = 0
        
        return {
            'win_rate': win_rate,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': self.total_trades,
            'balance': self.balance,
            'position': self.position
        }