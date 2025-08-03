"""
Advanced AI Training System
Allows importing 3-6 months of historical data, stock search, and simulation training
"""

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import requests
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from stable_baselines3 import PPO, A2C, SAC
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
import gymnasium as gym
from dotenv import load_dotenv
import json
import threading
import time

load_dotenv()
logger = logging.getLogger(__name__)

class AdvancedTrainingSystem:
    """
    Advanced AI training system with historical data import and simulation capabilities
    """
    
    def __init__(self, mode='paper'):
        self.mode = mode
        self.trading_client = TradingClient(
            api_key=os.getenv(f'ALPACA_{mode.upper()}_KEY'),
            secret_key=os.getenv(f'ALPACA_{mode.upper()}_SECRET'),
            paper=mode == 'paper'
        )
        self.data_client = StockHistoricalDataClient(
            api_key=os.getenv(f'ALPACA_{mode.upper()}_KEY'),
            secret_key=os.getenv(f'ALPACA_{mode.upper()}_SECRET')
        )
        
        # Training configuration
        self.training_config = {
            'default_months': 3,
            'max_months': 6,
            'min_data_points': 1000,
            'validation_split': 0.2,
            'simulation_days': 30
        }
        
        # Model storage
        self.models_dir = 'advanced_models'
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Training state
        self.training_jobs = {}
        self.simulation_results = {}
        
        logger.info("✅ Advanced Training System initialized")
    
    def search_stocks(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for stocks by symbol or company name
        """
        try:
            # Get all active stocks from Alpaca
            assets = self.trading_client.get_all_assets()
            
            # Filter by query (case insensitive)
            query_lower = query.lower()
            matching_stocks = []
            
            for asset in assets:
                if (query_lower in asset.symbol.lower() or 
                    query_lower in asset.name.lower()):
                    matching_stocks.append({
                        'symbol': asset.symbol,
                        'name': asset.name,
                        'exchange': asset.exchange,
                        'status': asset.status,
                        'tradable': asset.tradable
                    })
                    
                    if len(matching_stocks) >= limit:
                        break
            
            return matching_stocks
            
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        Get detailed information about a specific stock
        """
        try:
            # Get asset details
            asset = self.trading_client.get_asset(symbol)
            
            # Get current price
            current_price = self._get_current_price(symbol)
            
            # Get recent performance
            performance = self._get_recent_performance(symbol)
            
            return {
                'symbol': symbol,
                'name': asset.name,
                'exchange': asset.exchange,
                'status': asset.status,
                'tradable': asset.tradable,
                'current_price': current_price,
                'performance': performance
            }
            
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {e}")
            return {}
    
    def import_historical_data(self, symbol: str, months: int = 3) -> Dict:
        """
        Import historical data for training (3-6 months)
        """
        try:
            if months < 1 or months > 6:
                return {'error': 'Months must be between 1 and 6'}
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            logger.info(f"📊 Importing {months} months of data for {symbol}")
            
            # Fetch historical data with 5-minute intervals
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute(5),
                start=start_date,
                end=end_date
            )
            
            bars = self.data_client.get_stock_bars(request)
            
            if not bars or not hasattr(bars, 'df') or len(bars.df) == 0:
                return {'error': f'No data available for {symbol}'}
            
            # Convert to DataFrame
            df = bars.df.reset_index()
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            
            # Add technical indicators
            df = self._add_technical_indicators(df)
            
            # Save data
            data_file = f"{self.models_dir}/{symbol}_data_{months}m.csv"
            df.to_csv(data_file, index=False)
            
            # Calculate statistics
            stats = self._calculate_data_statistics(df)
            
            return {
                'success': True,
                'symbol': symbol,
                'months': months,
                'data_points': len(df),
                'date_range': {
                    'start': df.index[0].strftime('%Y-%m-%d'),
                    'end': df.index[-1].strftime('%Y-%m-%d')
                },
                'statistics': stats,
                'data_file': data_file
            }
            
        except Exception as e:
            logger.error(f"Error importing data for {symbol}: {e}")
            return {'error': str(e)}
    
    def train_advanced_model(self, symbol: str, model_type: str = 'PPO', 
                           training_steps: int = 50000) -> Dict:
        """
        Train an advanced AI model on historical data
        """
        try:
            # Check if data exists
            data_files = [f for f in os.listdir(self.models_dir) 
                         if f.startswith(f"{symbol}_data_") and f.endswith('.csv')]
            
            if not data_files:
                return {'error': f'No historical data found for {symbol}. Import data first.'}
            
            # Use the most recent data file
            data_file = sorted(data_files)[-1]
            data_path = f"{self.models_dir}/{data_file}"
            
            logger.info(f"🤖 Training {model_type} model for {symbol}")
            
            # Load and prepare data
            df = pd.read_csv(data_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Create training environment
            env = self._create_training_environment(df, symbol)
            
            # Select model type
            if model_type == 'PPO':
                model = PPO(
                    "MlpPolicy",
                    env,
                    verbose=1,
                    learning_rate=0.0003,
                    tensorboard_log=f"{self.models_dir}/tensorboard/{symbol}/"
                )
            elif model_type == 'A2C':
                model = A2C(
                    "MlpPolicy",
                    env,
                    verbose=1,
                    learning_rate=0.0007,
                    tensorboard_log=f"{self.models_dir}/tensorboard/{symbol}/"
                )
            elif model_type == 'SAC':
                model = SAC(
                    "MlpPolicy",
                    env,
                    verbose=1,
                    learning_rate=0.0003,
                    tensorboard_log=f"{self.models_dir}/tensorboard/{symbol}/"
                )
            else:
                return {'error': f'Unknown model type: {model_type}'}
            
            # Setup callbacks
            eval_env = self._create_training_environment(df, symbol)
            eval_callback = EvalCallback(
                eval_env,
                best_model_save_path=f"{self.models_dir}/{symbol}_best/",
                log_path=f"{self.models_dir}/{symbol}_logs/",
                eval_freq=1000,
                deterministic=True,
                render=False
            )
            
            checkpoint_callback = CheckpointCallback(
                save_freq=5000,
                save_path=f"{self.models_dir}/{symbol}_checkpoints/",
                name_prefix=f"{symbol}_{model_type}"
            )
            
            # Start training
            training_id = f"{symbol}_{model_type}_{int(time.time())}"
            self.training_jobs[training_id] = {
                'status': 'training',
                'progress': 0,
                'start_time': datetime.now(),
                'symbol': symbol,
                'model_type': model_type
            }
            
            # Train in separate thread
            def train_thread():
                try:
                    model.learn(
                        total_timesteps=training_steps,
                        callback=[eval_callback, checkpoint_callback],
                        progress_bar=True
                    )
                    
                    # Save final model
                    model_path = f"{self.models_dir}/{symbol}_{model_type}_final.zip"
                    model.save(model_path)
                    
                    # Update training status
                    self.training_jobs[training_id]['status'] = 'completed'
                    self.training_jobs[training_id]['progress'] = 100
                    self.training_jobs[training_id]['model_path'] = model_path
                    
                    logger.info(f"✅ Training completed for {symbol} ({model_type})")
                    
                except Exception as e:
                    logger.error(f"Training error for {symbol}: {e}")
                    self.training_jobs[training_id]['status'] = 'failed'
                    self.training_jobs[training_id]['error'] = str(e)
            
            thread = threading.Thread(target=train_thread)
            thread.daemon = True
            thread.start()
            
            return {
                'success': True,
                'training_id': training_id,
                'symbol': symbol,
                'model_type': model_type,
                'training_steps': training_steps,
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {e}")
            return {'error': str(e)}
    
    def run_simulation(self, symbol: str, days: int = 30, 
                      model_path: str = None) -> Dict:
        """
        Run a simulation using trained model
        """
        try:
            # Load model
            if not model_path:
                # Find best model
                model_files = [f for f in os.listdir(self.models_dir) 
                              if f.startswith(f"{symbol}_") and f.endswith('.zip')]
                if not model_files:
                    return {'error': f'No trained model found for {symbol}'}
                model_path = f"{self.models_dir}/{sorted(model_files)[-1]}"
            
            # Load model
            if 'PPO' in model_path:
                model = PPO.load(model_path)
            elif 'A2C' in model_path:
                model = A2C.load(model_path)
            elif 'SAC' in model_path:
                model = SAC.load(model_path)
            else:
                return {'error': 'Unknown model type'}
            
            # Get recent data for simulation
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute(5),
                start=start_date,
                end=end_date
            )
            
            bars = self.data_client.get_stock_bars(request)
            
            if not bars or not hasattr(bars, 'df') or len(bars.df) == 0:
                return {'error': f'No recent data available for {symbol}'}
            
            # Prepare simulation data
            df = bars.df.reset_index()
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            
            df = self._add_technical_indicators(df)
            
            # Run simulation
            simulation_results = self._run_model_simulation(model, df, symbol)
            
            # Save simulation results
            simulation_id = f"{symbol}_sim_{int(time.time())}"
            self.simulation_results[simulation_id] = simulation_results
            
            return {
                'success': True,
                'simulation_id': simulation_id,
                'symbol': symbol,
                'days': days,
                'results': simulation_results
            }
            
        except Exception as e:
            logger.error(f"Error running simulation for {symbol}: {e}")
            return {'error': str(e)}
    
    def get_training_status(self, training_id: str = None) -> Dict:
        """
        Get training status and progress
        """
        if training_id:
            return self.training_jobs.get(training_id, {})
        else:
            return {
                'active_jobs': len([j for j in self.training_jobs.values() 
                                   if j['status'] == 'training']),
                'completed_jobs': len([j for j in self.training_jobs.values() 
                                      if j['status'] == 'completed']),
                'failed_jobs': len([j for j in self.training_jobs.values() 
                                   if j['status'] == 'failed']),
                'jobs': self.training_jobs
            }
    
    def get_available_models(self) -> List[Dict]:
        """
        Get list of available trained models
        """
        models = []
        
        for file in os.listdir(self.models_dir):
            if file.endswith('.zip'):
                parts = file.replace('.zip', '').split('_')
                if len(parts) >= 2:
                    models.append({
                        'filename': file,
                        'symbol': parts[0],
                        'model_type': parts[1],
                        'path': f"{self.models_dir}/{file}",
                        'size': os.path.getsize(f"{self.models_dir}/{file}")
                    })
        
        return models
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price"""
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute(1),
                start=datetime.now() - timedelta(minutes=5)
            )
            bars = self.data_client.get_stock_bars(request)
            
            if bars and hasattr(bars, 'df') and len(bars.df) > 0:
                return float(bars.df['close'].iloc[-1])
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def _get_recent_performance(self, symbol: str) -> Dict:
        """Get recent performance metrics"""
        try:
            # Get 30 days of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            
            bars = self.data_client.get_stock_bars(request)
            
            if bars and hasattr(bars, 'df') and len(bars.df) > 0:
                df = bars.df
                prices = df['close'].tolist()
                
                if len(prices) >= 2:
                    return {
                        'current_price': float(prices[-1]),
                        'price_change': float(prices[-1] - prices[0]),
                        'price_change_pct': float((prices[-1] - prices[0]) / prices[0] * 100),
                        'volatility': float(np.std(prices)),
                        'volume_avg': float(df['volume'].mean())
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting performance for {symbol}: {e}")
            return {}
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to DataFrame"""
        try:
            # RSI
            df['RSI'] = self._calculate_rsi(df['Close'])
            
            # MACD
            df['MACD'], df['Signal'] = self._calculate_macd(df['Close'])
            
            # Moving averages
            df['MA_20'] = df['Close'].rolling(window=20).mean()
            df['MA_50'] = df['Close'].rolling(window=50).mean()
            
            # Bollinger Bands
            df['BB_upper'], df['BB_lower'] = self._calculate_bollinger_bands(df['Close'])
            
            # Volume indicators
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
            
            # Fill NaN values
            df.fillna(method='bfill', inplace=True)
            df.fillna(0, inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd, signal_line
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        return upper, lower
    
    def _calculate_data_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate statistics for imported data"""
        try:
            return {
                'total_points': len(df),
                'date_range': {
                    'start': df.index[0].strftime('%Y-%m-%d'),
                    'end': df.index[-1].strftime('%Y-%m-%d')
                },
                'price_stats': {
                    'min': float(df['Close'].min()),
                    'max': float(df['Close'].max()),
                    'mean': float(df['Close'].mean()),
                    'std': float(df['Close'].std())
                },
                'volume_stats': {
                    'total': float(df['Volume'].sum()),
                    'mean': float(df['Volume'].mean()),
                    'max': float(df['Volume'].max())
                }
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def _create_training_environment(self, df: pd.DataFrame, symbol: str):
        """Create training environment from historical data"""
        # This would create a custom Gym environment
        # For now, return a simple environment
        from trading_env import TradingEnvironment
        return TradingEnvironment(symbol, mode=self.mode)
    
    def _run_model_simulation(self, model, df: pd.DataFrame, symbol: str) -> Dict:
        """Run simulation using trained model"""
        try:
            # Create simulation environment
            env = self._create_training_environment(df, symbol)
            
            # Run simulation
            obs = env.reset()
            total_reward = 0
            trades = []
            portfolio_values = []
            
            for step in range(len(df) - 1):
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, info = env.step(action)
                
                total_reward += reward
                portfolio_values.append(env.balance + env.position * df['Close'].iloc[step])
                
                if action in [1, 2]:  # Buy or Sell
                    trades.append({
                        'step': step,
                        'action': 'buy' if action == 1 else 'sell',
                        'price': float(df['Close'].iloc[step]),
                        'reward': float(reward)
                    })
                
                if done:
                    break
            
            # Calculate simulation metrics
            initial_value = portfolio_values[0] if portfolio_values else 0
            final_value = portfolio_values[-1] if portfolio_values else 0
            total_return = ((final_value - initial_value) / initial_value * 100) if initial_value > 0 else 0
            
            return {
                'total_reward': float(total_reward),
                'total_return_pct': float(total_return),
                'initial_value': float(initial_value),
                'final_value': float(final_value),
                'total_trades': len(trades),
                'trades': trades,
                'portfolio_values': portfolio_values
            }
            
        except Exception as e:
            logger.error(f"Error in simulation: {e}")
            return {'error': str(e)} 