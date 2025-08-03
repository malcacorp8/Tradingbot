"""
Advanced Risk Management System
Handles portfolio-level risk controls, position sizing, and safety mechanisms
"""

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Advanced risk management with portfolio-level controls
    Handles position sizing, stop losses, and portfolio concentration limits
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
        
        # Risk parameters
        self.max_position_size = float(os.getenv('MAX_POSITION_SIZE', 0.01))  # 1% default
        self.max_portfolio_concentration = float(os.getenv('MAX_PORTFOLIO_CONCENTRATION', 0.20))  # 20% default
        self.stop_loss_threshold = float(os.getenv('STOP_LOSS_THRESHOLD', 0.05))  # 5% default
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', 100))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', 0.02))  # 2% default
        
        # Risk tracking
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.positions = {}
        self.risk_history = []
        
        logger.info(f"✅ Risk manager initialized in {mode} mode")
    
    def calculate_position_size(self, symbol: str, price: float, 
                              confidence: float = 1.0) -> int:
        """
        Calculate optimal position size based on risk parameters
        """
        try:
            # Get account information
            account = self.trading_client.get_account()
            total_value = float(account.portfolio_value)
            
            # Base position size (percentage of portfolio)
            base_size = total_value * self.max_position_size
            
            # Adjust for confidence level
            adjusted_size = base_size * confidence
            
            # Adjust for volatility
            volatility = self._get_volatility_adjustment(symbol)
            final_size = adjusted_size * volatility
            
            # Calculate number of shares
            shares = int(final_size / price)
            
            # Ensure minimum and maximum limits
            min_shares = 1
            max_shares = int(total_value * self.max_position_size / price)
            
            shares = max(min_shares, min(shares, max_shares))
            
            logger.info(f"📊 Position size for {symbol}: {shares} shares (${shares * price:.2f})")
            return shares
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 1  # Minimum position
    
    def check_risk_limits(self, symbol: str, action: str, 
                         quantity: int, price: float) -> Dict:
        """
        Check if a trade meets risk management criteria
        """
        try:
            risk_check = {
                'approved': True,
                'warnings': [],
                'rejections': []
            }
            
            # Get current portfolio state
            portfolio = self._get_portfolio_state()
            total_value = portfolio['total_value']
            
            # 1. Check daily trade limit
            if self.daily_trades >= self.max_daily_trades:
                risk_check['approved'] = False
                risk_check['rejections'].append(f"Daily trade limit exceeded ({self.max_daily_trades})")
            
            # 2. Check daily loss limit
            if self.daily_pnl < -total_value * self.max_daily_loss:
                risk_check['approved'] = False
                risk_check['rejections'].append(f"Daily loss limit exceeded ({self.max_daily_loss * 100}%)")
            
            # 3. Check position size limit
            trade_value = quantity * price
            if trade_value > total_value * self.max_position_size:
                risk_check['approved'] = False
                risk_check['rejections'].append(f"Position size exceeds limit ({self.max_position_size * 100}%)")
            
            # 4. Check portfolio concentration
            current_concentration = self._calculate_concentration(symbol, portfolio)
            new_concentration = current_concentration + (trade_value / total_value)
            
            if new_concentration > self.max_portfolio_concentration:
                risk_check['approved'] = False
                risk_check['rejections'].append(f"Portfolio concentration limit exceeded ({self.max_portfolio_concentration * 100}%)")
            
            # 5. Check market volatility
            volatility = self._get_volatility_adjustment(symbol)
            if volatility < 0.5:  # High volatility warning
                risk_check['warnings'].append(f"High volatility detected for {symbol}")
            
            # 6. Check market hours (if applicable)
            if not self._is_market_open():
                risk_check['warnings'].append("Trading outside market hours")
            
            return risk_check
            
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return {
                'approved': False,
                'rejections': [f"Risk check error: {str(e)}"]
            }
    
    def update_risk_metrics(self, symbol: str, action: str, 
                           quantity: int, price: float, pnl: float = 0):
        """
        Update risk tracking metrics after a trade
        """
        try:
            # Update daily metrics
            self.daily_trades += 1
            self.daily_pnl += pnl
            
            # Update position tracking
            if symbol not in self.positions:
                self.positions[symbol] = {
                    'quantity': 0,
                    'avg_price': 0,
                    'total_value': 0,
                    'last_trade': None
                }
            
            position = self.positions[symbol]
            
            if action == 'buy':
                # Update average price
                total_cost = position['quantity'] * position['avg_price'] + quantity * price
                total_quantity = position['quantity'] + quantity
                position['avg_price'] = total_cost / total_quantity if total_quantity > 0 else price
                position['quantity'] = total_quantity
            elif action == 'sell':
                position['quantity'] = max(0, position['quantity'] - quantity)
            
            position['total_value'] = position['quantity'] * price
            position['last_trade'] = datetime.now()
            
            # Record risk event
            self.risk_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'pnl': pnl,
                'daily_trades': self.daily_trades,
                'daily_pnl': self.daily_pnl
            })
            
            logger.info(f"📈 Risk metrics updated: {action} {quantity} {symbol} @ ${price:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating risk metrics: {e}")
    
    def check_stop_losses(self) -> List[Dict]:
        """
        Check for stop loss triggers across all positions
        """
        stop_losses = []
        
        try:
            for symbol, position in self.positions.items():
                if position['quantity'] <= 0:
                    continue
                
                # Get current price
                current_price = self._get_current_price(symbol)
                if not current_price:
                    continue
                
                # Calculate unrealized P&L
                unrealized_pnl = (current_price - position['avg_price']) * position['quantity']
                unrealized_pnl_pct = (current_price - position['avg_price']) / position['avg_price']
                
                # Check stop loss
                if unrealized_pnl_pct < -self.stop_loss_threshold:
                    stop_losses.append({
                        'symbol': symbol,
                        'quantity': position['quantity'],
                        'avg_price': position['avg_price'],
                        'current_price': current_price,
                        'unrealized_pnl': unrealized_pnl,
                        'unrealized_pnl_pct': unrealized_pnl_pct,
                        'stop_loss_threshold': -self.stop_loss_threshold
                    })
            
            return stop_losses
            
        except Exception as e:
            logger.error(f"Error checking stop losses: {e}")
            return []
    
    def get_risk_summary(self) -> Dict:
        """
        Get comprehensive risk summary
        """
        try:
            portfolio = self._get_portfolio_state()
            
            # Calculate portfolio metrics
            total_value = portfolio['total_value']
            total_positions = len([p for p in portfolio['positions'] if p['quantity'] > 0])
            
            # Calculate concentration metrics
            concentrations = []
            for position in portfolio['positions']:
                if position['quantity'] > 0:
                    concentration = position['market_value'] / total_value
                    concentrations.append(concentration)
            
            max_concentration = max(concentrations) if concentrations else 0
            
            # Calculate volatility metrics
            portfolio_volatility = self._calculate_portfolio_volatility(portfolio)
            
            return {
                'total_value': total_value,
                'total_positions': total_positions,
                'daily_trades': self.daily_trades,
                'daily_pnl': self.daily_pnl,
                'daily_pnl_pct': self.daily_pnl / total_value if total_value > 0 else 0,
                'max_concentration': max_concentration,
                'portfolio_volatility': portfolio_volatility,
                'risk_limits': {
                    'max_position_size': self.max_position_size,
                    'max_concentration': self.max_portfolio_concentration,
                    'stop_loss_threshold': self.stop_loss_threshold,
                    'max_daily_trades': self.max_daily_trades,
                    'max_daily_loss': self.max_daily_loss
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting risk summary: {e}")
            return {'error': str(e)}
    
    def reset_daily_metrics(self):
        """Reset daily risk metrics (call at start of trading day)"""
        self.daily_trades = 0
        self.daily_pnl = 0.0
        logger.info("🔄 Daily risk metrics reset")
    
    def _get_portfolio_state(self) -> Dict:
        """Get current portfolio state"""
        try:
            account = self.trading_client.get_account()
            positions = self.trading_client.get_all_positions()
            
            portfolio = {
                'total_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'positions': []
            }
            
            for position in positions:
                portfolio['positions'].append({
                    'symbol': position.symbol,
                    'quantity': int(position.qty),
                    'avg_price': float(position.avg_entry_price),
                    'market_value': float(position.market_value),
                    'unrealized_pnl': float(position.unrealized_pl)
                })
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting portfolio state: {e}")
            return {
                'total_value': 100000,  # Default value
                'cash': 100000,
                'positions': []
            }
    
    def _calculate_concentration(self, symbol: str, portfolio: Dict) -> float:
        """Calculate current concentration for a symbol"""
        total_value = portfolio['total_value']
        
        for position in portfolio['positions']:
            if position['symbol'] == symbol:
                return position['market_value'] / total_value
        
        return 0.0
    
    def _get_volatility_adjustment(self, symbol: str) -> float:
        """Get volatility adjustment factor for position sizing"""
        try:
            # Get 20 days of historical data
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=20)
            )
            bars = self.data_client.get_stock_bars(request)
            
            if bars and len(bars) > 1:
                prices = [float(bar.close) for bar in bars]
                returns = np.diff(np.log(prices))
                volatility = np.std(returns) * np.sqrt(252)  # Annualized
                
                # Adjust position size based on volatility
                # Higher volatility = smaller position
                if volatility > 0.5:  # High volatility
                    return 0.5
                elif volatility > 0.3:  # Medium volatility
                    return 0.75
                else:  # Low volatility
                    return 1.0
            
            return 1.0  # Default adjustment
            
        except Exception as e:
            logger.error(f"Error calculating volatility adjustment: {e}")
            return 1.0
    
    def _calculate_portfolio_volatility(self, portfolio: Dict) -> float:
        """Calculate overall portfolio volatility"""
        try:
            if not portfolio['positions']:
                return 0.0
            
            # Simplified portfolio volatility calculation
            volatilities = []
            weights = []
            
            for position in portfolio['positions']:
                if position['quantity'] > 0:
                    vol = self._get_volatility_adjustment(position['symbol'])
                    volatilities.append(vol)
                    weights.append(position['market_value'])
            
            if weights:
                # Weighted average volatility
                total_weight = sum(weights)
                weighted_vol = sum(v * w for v, w in zip(volatilities, weights)) / total_weight
                return weighted_vol
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating portfolio volatility: {e}")
            return 0.0
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price"""
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                start=datetime.now() - timedelta(minutes=5)
            )
            bars = self.data_client.get_stock_bars(request)
            
            if bars and len(bars) > 0:
                return float(bars[-1].close)
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def _is_market_open(self) -> bool:
        """Check if market is currently open"""
        try:
            # Simplified market hours check
            now = datetime.now()
            
            # Check if it's a weekday
            if now.weekday() >= 5:  # Saturday or Sunday
                return False
            
            # Check if it's between 9:30 AM and 4:00 PM ET
            # This is a simplified check - in production, use Alpaca's calendar API
            hour = now.hour
            if 9 <= hour < 16:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking market hours: {e}")
            return True  # Assume open if we can't check 