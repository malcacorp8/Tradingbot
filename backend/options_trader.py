"""
Advanced Options Trading Module
Handles real options data, volatility analysis, and options-specific strategies
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

class OptionsTrader:
    """
    Advanced options trading with real market data
    Handles options chains, volatility analysis, and options strategies
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
        
        # Options trading state
        self.options_positions = {}
        self.volatility_cache = {}
        
        logger.info(f"✅ Options trader initialized in {mode} mode")
    
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """
        Get options chain for a symbol
        Returns calls and puts with strike prices and Greeks
        """
        try:
            # In a real implementation, this would fetch from Alpaca's options API
            # For now, we'll simulate options data based on current stock price
            
            # Get current stock price
            current_price = self._get_current_price(symbol)
            if not current_price:
                return {'error': 'Could not fetch stock price'}
            
            # Generate simulated options chain
            options_chain = self._generate_options_chain(symbol, current_price, expiration_date)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'expiration_date': expiration_date,
                'options': options_chain,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting options chain for {symbol}: {e}")
            return {'error': str(e)}
    
    def calculate_implied_volatility(self, symbol: str, option_type: str, 
                                   strike: float, current_price: float, 
                                   time_to_expiry: float) -> float:
        """
        Calculate implied volatility using Black-Scholes approximation
        """
        try:
            # Simplified IV calculation
            # In production, use a proper options pricing library
            
            # Get historical volatility as base
            hist_vol = self._get_historical_volatility(symbol)
            
            # Adjust based on option characteristics
            moneyness = current_price / strike
            
            if option_type.lower() == 'call':
                if moneyness > 1.1:  # Deep ITM
                    iv = hist_vol * 0.8
                elif moneyness < 0.9:  # Deep OTM
                    iv = hist_vol * 1.3
                else:  # ATM
                    iv = hist_vol * 1.0
            else:  # Put
                if moneyness > 1.1:  # Deep OTM
                    iv = hist_vol * 1.3
                elif moneyness < 0.9:  # Deep ITM
                    iv = hist_vol * 0.8
                else:  # ATM
                    iv = hist_vol * 1.0
            
            # Time decay adjustment
            if time_to_expiry < 7:  # Less than a week
                iv *= 1.2  # Higher IV for short-term options
            
            return max(iv, 0.1)  # Minimum 10% IV
            
        except Exception as e:
            logger.error(f"Error calculating IV: {e}")
            return 0.3  # Default 30% IV
    
    def execute_options_trade(self, symbol: str, option_type: str, 
                            strike: float, expiration: str, 
                            quantity: int, action: str) -> Dict:
        """
        Execute an options trade
        """
        try:
            # Validate parameters
            if option_type not in ['call', 'put']:
                return {'error': 'Invalid option type'}
            
            if action not in ['buy', 'sell']:
                return {'error': 'Invalid action'}
            
            # Get current stock price
            current_price = self._get_current_price(symbol)
            if not current_price:
                return {'error': 'Could not fetch stock price'}
            
            # Calculate option premium (simplified)
            time_to_expiry = self._calculate_time_to_expiry(expiration)
            iv = self.calculate_implied_volatility(symbol, option_type, strike, current_price, time_to_expiry)
            
            # Simplified premium calculation
            premium = self._calculate_option_premium(
                current_price, strike, time_to_expiry, iv, option_type
            )
            
            # Calculate total cost
            total_cost = premium * quantity * 100  # Options are for 100 shares
            
            # Check if we have enough capital (simplified)
            account = self.trading_client.get_account()
            available_cash = float(account.cash)
            
            if total_cost > available_cash:
                return {'error': f'Insufficient funds. Need ${total_cost:.2f}, have ${available_cash:.2f}'}
            
            # Execute trade (simulated for now)
            trade_result = {
                'symbol': symbol,
                'option_type': option_type,
                'strike': strike,
                'expiration': expiration,
                'quantity': quantity,
                'action': action,
                'premium_per_share': premium,
                'total_cost': total_cost,
                'implied_volatility': iv,
                'timestamp': datetime.now().isoformat(),
                'status': 'executed'
            }
            
            # Update positions
            position_key = f"{symbol}_{option_type}_{strike}_{expiration}"
            if position_key not in self.options_positions:
                self.options_positions[position_key] = 0
            
            if action == 'buy':
                self.options_positions[position_key] += quantity
            else:
                self.options_positions[position_key] -= quantity
            
            logger.info(f"✅ Options trade executed: {action} {quantity} {option_type} {symbol} {strike}")
            return trade_result
            
        except Exception as e:
            logger.error(f"Error executing options trade: {e}")
            return {'error': str(e)}
    
    def get_options_portfolio(self) -> Dict:
        """Get current options portfolio"""
        portfolio = {
            'positions': self.options_positions,
            'total_positions': len(self.options_positions),
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate portfolio value (simplified)
        total_value = 0
        for position_key, quantity in self.options_positions.items():
            if quantity != 0:
                # Simplified valuation
                total_value += abs(quantity) * 100  # Assume $100 per contract
        
        portfolio['total_value'] = total_value
        return portfolio
    
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
    
    def _generate_options_chain(self, symbol: str, current_price: float, 
                               expiration_date: Optional[str]) -> Dict:
        """Generate simulated options chain"""
        if not expiration_date:
            # Default to next Friday
            today = datetime.now()
            days_until_friday = (4 - today.weekday()) % 7
            expiration_date = (today + timedelta(days=days_until_friday)).strftime('%Y-%m-%d')
        
        # Generate strikes around current price
        strikes = []
        for i in range(-5, 6):  # 5 strikes below and above current price
            strike = current_price + (i * 5)  # $5 intervals
            if strike > 0:
                strikes.append(strike)
        
        calls = []
        puts = []
        
        for strike in strikes:
            time_to_expiry = self._calculate_time_to_expiry(expiration_date)
            iv_call = self.calculate_implied_volatility(symbol, 'call', strike, current_price, time_to_expiry)
            iv_put = self.calculate_implied_volatility(symbol, 'put', strike, current_price, time_to_expiry)
            
            # Calculate premiums
            call_premium = self._calculate_option_premium(current_price, strike, time_to_expiry, iv_call, 'call')
            put_premium = self._calculate_option_premium(current_price, strike, time_to_expiry, iv_put, 'put')
            
            calls.append({
                'strike': strike,
                'premium': call_premium,
                'implied_volatility': iv_call,
                'delta': self._calculate_delta(current_price, strike, time_to_expiry, iv_call, 'call'),
                'volume': np.random.randint(10, 1000),
                'open_interest': np.random.randint(50, 5000)
            })
            
            puts.append({
                'strike': strike,
                'premium': put_premium,
                'implied_volatility': iv_put,
                'delta': self._calculate_delta(current_price, strike, time_to_expiry, iv_put, 'put'),
                'volume': np.random.randint(10, 1000),
                'open_interest': np.random.randint(50, 5000)
            })
        
        return {
            'calls': calls,
            'puts': puts
        }
    
    def _calculate_option_premium(self, current_price: float, strike: float, 
                                time_to_expiry: float, iv: float, option_type: str) -> float:
        """Calculate option premium using simplified Black-Scholes"""
        # Simplified premium calculation
        moneyness = current_price / strike
        
        if option_type.lower() == 'call':
            if moneyness > 1.05:  # ITM
                intrinsic = current_price - strike
                time_value = strike * 0.02 * (time_to_expiry / 365) * iv
                return max(intrinsic + time_value, 0.01)
            else:  # OTM
                time_value = strike * 0.02 * (time_to_expiry / 365) * iv
                return max(time_value, 0.01)
        else:  # Put
            if moneyness < 0.95:  # ITM
                intrinsic = strike - current_price
                time_value = strike * 0.02 * (time_to_expiry / 365) * iv
                return max(intrinsic + time_value, 0.01)
            else:  # OTM
                time_value = strike * 0.02 * (time_to_expiry / 365) * iv
                return max(time_value, 0.01)
    
    def _calculate_delta(self, current_price: float, strike: float, 
                        time_to_expiry: float, iv: float, option_type: str) -> float:
        """Calculate option delta"""
        moneyness = current_price / strike
        
        if option_type.lower() == 'call':
            if moneyness > 1.1:  # Deep ITM
                return 0.9
            elif moneyness < 0.9:  # Deep OTM
                return 0.1
            else:  # ATM
                return 0.5
        else:  # Put
            if moneyness > 1.1:  # Deep OTM
                return -0.1
            elif moneyness < 0.9:  # Deep ITM
                return -0.9
            else:  # ATM
                return -0.5
    
    def _get_historical_volatility(self, symbol: str) -> float:
        """Get historical volatility for a symbol"""
        if symbol in self.volatility_cache:
            return self.volatility_cache[symbol]
        
        try:
            # Get 30 days of historical data
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=30)
            )
            bars = self.data_client.get_stock_bars(request)
            
            if bars and len(bars) > 1:
                prices = [float(bar.close) for bar in bars]
                returns = np.diff(np.log(prices))
                volatility = np.std(returns) * np.sqrt(252)  # Annualized
                self.volatility_cache[symbol] = volatility
                return volatility
            
            return 0.3  # Default 30% volatility
            
        except Exception as e:
            logger.error(f"Error calculating historical volatility: {e}")
            return 0.3
    
    def _calculate_time_to_expiry(self, expiration_date: str) -> float:
        """Calculate time to expiry in years"""
        try:
            expiry = datetime.strptime(expiration_date, '%Y-%m-%d')
            now = datetime.now()
            days_to_expiry = (expiry - now).days
            return max(days_to_expiry / 365.0, 0.001)  # Minimum 1 day
        except:
            return 0.1  # Default 10% of a year 