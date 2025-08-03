"""
Agent Manager for Multi-Stock Autonomous Trading
Manages individual RL agents for each stock with self-learning capabilities
"""

import os
import pickle
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from trading_env import TradingEnvironment
import logging
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manages multiple RL agents for different stocks
    Handles autonomous learning and decision making
    """
    
    def __init__(self, symbols, mode='paper', model_dir='models'):
        self.symbols = symbols
        self.mode = mode
        self.model_dir = model_dir
        self.agents = {}
        self.environments = {}
        self.learning_stats = {}
        self.is_running = False
        
        # Create model directory
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize agents for each symbol
        self._initialize_agents()
        
        logger.info(f"Initialized AgentManager with {len(symbols)} symbols in {mode} mode")
    
    def _initialize_agents(self):
        """Initialize RL agents for each symbol"""
        for symbol in self.symbols:
            logger.info(f"Initializing agent for {symbol}")
            
            # Create environment
            env = TradingEnvironment(symbol)
            vec_env = DummyVecEnv([lambda: env])
            self.environments[symbol] = vec_env
            
            # Load existing model or create new one
            model_path = os.path.join(self.model_dir, f"{symbol}_ppo_model.zip")
            
            if os.path.exists(model_path):
                logger.info(f"Loading existing model for {symbol}")
                model = PPO.load(model_path, env=vec_env)
            else:
                logger.info(f"Creating new model for {symbol}")
                model = PPO(
                    "MlpPolicy",
                    vec_env,
                    verbose=1,
                    learning_rate=0.0003,
                    n_steps=2048,
                    batch_size=64,
                    n_epochs=10,
                    gamma=0.99,
                    gae_lambda=0.95,
                    clip_range=0.2,
                    tensorboard_log=f"./tensorboard_logs/{symbol}/"
                )
                
                # Initial training on historical data
                logger.info(f"Initial training for {symbol}")
                model.learn(total_timesteps=10000)
                self.save_model(symbol)
            
            self.agents[symbol] = model
            self.learning_stats[symbol] = {
                'total_episodes': 0,
                'total_rewards': [],
                'last_performance': {},
                'learning_cycles': 0
            }
    
    def predict_and_execute(self, symbol):
        """
        Make prediction and execute trade for a specific symbol
        Includes online learning for continuous improvement
        """
        if symbol not in self.agents:
            logger.error(f"No agent found for {symbol}")
            return None, 0
        
        try:
            env = self.environments[symbol].envs[0]
            model = self.agents[symbol]
            
            # Get current observation
            obs = env._get_observation()
            
            # Predict action
            action, _states = model.predict(obs, deterministic=False)
            
            # Execute action in environment
            new_obs, reward, done, truncated, info = env.step(action)
            
            # Store experience for learning
            self.learning_stats[symbol]['total_rewards'].append(reward)
            
            # Periodic online learning (every 100 steps)
            if len(self.learning_stats[symbol]['total_rewards']) % 100 == 0:
                self._online_learning(symbol)
            
            # Reset environment if done
            if done:
                performance = env.get_performance_metrics()
                self.learning_stats[symbol]['last_performance'] = performance
                self.learning_stats[symbol]['total_episodes'] += 1
                env.reset()
                
                logger.info(f"{symbol} Episode complete - Performance: {performance}")
            
            return action, reward, info
            
        except Exception as e:
            logger.error(f"Error in predict_and_execute for {symbol}: {e}")
            return None, 0, {}
    
    def _online_learning(self, symbol):
        """
        Perform online learning to improve agent performance
        This is where the agent gets 'smarter' over time
        """
        try:
            model = self.agents[symbol]
            
            # Online learning with recent experiences
            logger.info(f"Performing online learning for {symbol}")
            model.learn(total_timesteps=1000)  # Incremental learning
            
            self.learning_stats[symbol]['learning_cycles'] += 1
            
            # Save updated model
            if self.learning_stats[symbol]['learning_cycles'] % 10 == 0:
                self.save_model(symbol)
                logger.info(f"Model saved for {symbol} after {self.learning_stats[symbol]['learning_cycles']} learning cycles")
            
        except Exception as e:
            logger.error(f"Error in online learning for {symbol}: {e}")
    
    def evaluate_agent(self, symbol, n_eval_episodes=5):
        """Evaluate agent performance"""
        if symbol not in self.agents:
            return None
        
        model = self.agents[symbol]
        env = self.environments[symbol]
        
        mean_reward, std_reward = evaluate_policy(
            model, env, n_eval_episodes=n_eval_episodes, deterministic=True
        )
        
        return {
            'mean_reward': float(mean_reward),
            'std_reward': float(std_reward),
            'n_episodes': n_eval_episodes
        }
    
    def get_portfolio_status(self):
        """Get current status of all agents"""
        status = {}
        
        for symbol in self.symbols:
            if symbol in self.environments:
                env = self.environments[symbol].envs[0]
                performance = env.get_performance_metrics()
                
                status[symbol] = {
                    'performance': performance,
                    'learning_stats': self.learning_stats.get(symbol, {}),
                    'mode': self.mode
                }
        
        return status
    
    def save_model(self, symbol):
        """Save model to disk"""
        if symbol in self.agents:
            model_path = os.path.join(self.model_dir, f"{symbol}_ppo_model.zip")
            self.agents[symbol].save(model_path)
            
            # Save learning stats
            stats_path = os.path.join(self.model_dir, f"{symbol}_stats.pkl")
            with open(stats_path, 'wb') as f:
                pickle.dump(self.learning_stats[symbol], f)
    
    def load_model(self, symbol):
        """Load model from disk"""
        model_path = os.path.join(self.model_dir, f"{symbol}_ppo_model.zip")
        if os.path.exists(model_path) and symbol in self.environments:
            self.agents[symbol] = PPO.load(model_path, env=self.environments[symbol])
            
            # Load learning stats
            stats_path = os.path.join(self.model_dir, f"{symbol}_stats.pkl")
            if os.path.exists(stats_path):
                with open(stats_path, 'rb') as f:
                    self.learning_stats[symbol] = pickle.load(f)
            
            return True
        return False
    
    def switch_mode(self, new_mode):
        """Switch between paper and live trading modes"""
        logger.info(f"Switching from {self.mode} to {new_mode} mode")
        self.mode = new_mode
        
        # In a real implementation, you would reinitialize with different API endpoints
        # For now, we'll just update the mode flag
        logger.warning("Mode switching implemented - connect to appropriate APIs in production")
    
    def start_autonomous_trading(self):
        """Start autonomous trading loop"""
        self.is_running = True
        logger.info("Starting autonomous trading mode")
        
        def trading_loop():
            while self.is_running:
                try:
                    for symbol in self.symbols:
                        if not self.is_running:
                            break
                        
                        action, reward, info = self.predict_and_execute(symbol)
                        
                        if action is not None:
                            logger.info(f"{symbol}: Action={action}, Reward={reward:.4f}, Info={info}")
                    
                    # Wait before next cycle (configurable polling interval) - increased to reduce frequency
                    time.sleep(int(os.getenv('POLLING_INTERVAL', 30)))  # Changed from 10 to 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error in trading loop: {e}")
                    time.sleep(5)  # Wait before retrying
        
        # Start trading in separate thread
        self.trading_thread = threading.Thread(target=trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
    
    def stop_autonomous_trading(self):
        """Stop autonomous trading loop"""
        logger.info("Stopping autonomous trading mode")
        self.is_running = False
        
        if hasattr(self, 'trading_thread'):
            self.trading_thread.join(timeout=5)
    
    def get_learning_progress(self):
        """Get learning progress for all agents"""
        progress = {}
        
        for symbol in self.symbols:
            if symbol in self.learning_stats:
                stats = self.learning_stats[symbol]
                
                # Calculate improvement metrics
                recent_rewards = stats['total_rewards'][-100:] if len(stats['total_rewards']) > 100 else stats['total_rewards']
                early_rewards = stats['total_rewards'][:100] if len(stats['total_rewards']) > 100 else []
                
                improvement = 0
                if early_rewards and recent_rewards:
                    improvement = np.mean(recent_rewards) - np.mean(early_rewards)
                
                progress[symbol] = {
                    'total_episodes': stats['total_episodes'],
                    'learning_cycles': stats['learning_cycles'],
                    'recent_avg_reward': np.mean(recent_rewards) if recent_rewards else 0,
                    'improvement': improvement,
                    'last_performance': stats.get('last_performance', {})
                }
        
        return progress
    
    def retrain_agent(self, symbol, timesteps=50000):
        """Retrain a specific agent from scratch"""
        logger.info(f"Retraining agent for {symbol}")
        
        if symbol in self.agents:
            # Reset environment
            env = self.environments[symbol]
            
            # Create new model
            model = PPO(
                "MlpPolicy",
                env,
                verbose=1,
                learning_rate=0.0003,
                tensorboard_log=f"./tensorboard_logs/{symbol}/"
            )
            
            # Train
            model.learn(total_timesteps=timesteps)
            
            # Update agent
            self.agents[symbol] = model
            
            # Reset stats
            self.learning_stats[symbol] = {
                'total_episodes': 0,
                'total_rewards': [],
                'last_performance': {},
                'learning_cycles': 0
            }
            
            # Save
            self.save_model(symbol)
            
            logger.info(f"Retraining complete for {symbol}")