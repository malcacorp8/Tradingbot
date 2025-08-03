"""
Comprehensive Analytics and Performance Reporting
Provides detailed analysis of trading performance, learning progress, and risk metrics
"""

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TradingAnalytics:
    """
    Comprehensive analytics for trading performance and learning progress
    """
    
    def __init__(self, db_url=None):
        self.db_url = db_url or os.getenv('DB_URL')
        if self.db_url:
            self.engine = create_engine(self.db_url)
        else:
            self.engine = None
            logger.warning("⚠️ Database not configured - analytics will be limited")
    
    def get_performance_summary(self, days: int = 30) -> Dict:
        """
        Get comprehensive performance summary
        """
        try:
            # Get trade data
            trades_df = self._get_trades_data(days)
            
            if trades_df.empty:
                return self._empty_performance_summary()
            
            # Calculate metrics
            total_trades = len(trades_df)
            winning_trades = len(trades_df[trades_df['pnl'] > 0])
            losing_trades = len(trades_df[trades_df['pnl'] < 0])
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            total_pnl = trades_df['pnl'].sum()
            avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
            
            # Calculate Sharpe ratio
            daily_returns = self._calculate_daily_returns(trades_df)
            sharpe_ratio = self._calculate_sharpe_ratio(daily_returns)
            
            # Calculate drawdown
            cumulative_returns = (1 + daily_returns).cumprod()
            drawdown = self._calculate_max_drawdown(cumulative_returns)
            
            # Performance by symbol
            symbol_performance = self._calculate_symbol_performance(trades_df)
            
            return {
                'summary': {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'total_pnl': total_pnl,
                    'avg_win': avg_win,
                    'avg_loss': avg_loss,
                    'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': drawdown,
                    'period_days': days
                },
                'symbol_performance': symbol_performance,
                'daily_returns': daily_returns.tolist(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return self._empty_performance_summary()
    
    def get_learning_progress(self, symbol: str = None) -> Dict:
        """
        Analyze learning progress and agent improvement
        """
        try:
            # Get learning data
            learning_data = self._get_learning_data(symbol)
            
            if not learning_data:
                return {'error': 'No learning data available'}
            
            # Calculate learning metrics
            episodes = len(learning_data)
            avg_reward = np.mean([d['reward'] for d in learning_data])
            reward_trend = self._calculate_trend([d['reward'] for d in learning_data])
            
            # Calculate improvement rate
            recent_rewards = [d['reward'] for d in learning_data[-10:]]  # Last 10 episodes
            early_rewards = [d['reward'] for d in learning_data[:10]]   # First 10 episodes
            
            if len(recent_rewards) >= 5 and len(early_rewards) >= 5:
                improvement_rate = (np.mean(recent_rewards) - np.mean(early_rewards)) / abs(np.mean(early_rewards)) if np.mean(early_rewards) != 0 else 0
            else:
                improvement_rate = 0
            
            return {
                'episodes': episodes,
                'avg_reward': avg_reward,
                'reward_trend': reward_trend,
                'improvement_rate': improvement_rate,
                'recent_performance': np.mean(recent_rewards) if recent_rewards else 0,
                'early_performance': np.mean(early_rewards) if early_rewards else 0,
                'learning_curve': [d['reward'] for d in learning_data],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting learning progress: {e}")
            return {'error': str(e)}
    
    def get_risk_analysis(self, days: int = 30) -> Dict:
        """
        Comprehensive risk analysis
        """
        try:
            trades_df = self._get_trades_data(days)
            
            if trades_df.empty:
                return {'error': 'No trade data available'}
            
            # Calculate risk metrics
            returns = trades_df['pnl'] / trades_df['pnl'].abs().sum() if trades_df['pnl'].abs().sum() > 0 else pd.Series([0])
            
            risk_metrics = {
                'volatility': returns.std() * np.sqrt(252),  # Annualized
                'var_95': np.percentile(returns, 5),  # 95% VaR
                'cvar_95': returns[returns <= np.percentile(returns, 5)].mean(),  # Conditional VaR
                'max_loss': returns.min(),
                'max_gain': returns.max(),
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis()
            }
            
            # Position concentration analysis
            symbol_concentration = trades_df.groupby('symbol')['pnl'].sum().abs()
            total_pnl = symbol_concentration.sum()
            if total_pnl > 0:
                concentration_risk = (symbol_concentration / total_pnl).max()
            else:
                concentration_risk = 0
            
            # Correlation analysis
            symbol_returns = self._calculate_symbol_returns(trades_df)
            correlation_matrix = symbol_returns.corr() if len(symbol_returns.columns) > 1 else pd.DataFrame()
            
            return {
                'risk_metrics': risk_metrics,
                'concentration_risk': concentration_risk,
                'correlation_matrix': correlation_matrix.to_dict() if not correlation_matrix.empty else {},
                'symbol_risk': self._calculate_symbol_risk(trades_df),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting risk analysis: {e}")
            return {'error': str(e)}
    
    def get_market_analysis(self, symbols: List[str]) -> Dict:
        """
        Market analysis including sentiment and volatility
        """
        try:
            from news_analyzer import NewsAnalyzer
            from risk_manager import RiskManager
            
            news_analyzer = NewsAnalyzer()
            risk_manager = RiskManager()
            
            market_data = {}
            
            for symbol in symbols:
                # Get sentiment data
                sentiment_data = news_analyzer.get_news_sentiment(symbol, hours_back=24)
                
                # Get volatility data
                volatility = risk_manager._get_volatility_adjustment(symbol)
                
                market_data[symbol] = {
                    'sentiment': sentiment_data.get('sentiment_score', 0.5),
                    'news_count': sentiment_data.get('news_count', 0),
                    'volatility': volatility,
                    'market_sentiment': sentiment_data.get('confidence', 0.0)
                }
            
            # Overall market sentiment
            overall_sentiment = news_analyzer.get_market_sentiment_summary(symbols)
            
            return {
                'symbol_data': market_data,
                'overall_sentiment': overall_sentiment.get('market_sentiment', 0.5),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market analysis: {e}")
            return {'error': str(e)}
    
    def generate_report(self, report_type: str = 'comprehensive', days: int = 30) -> Dict:
        """
        Generate comprehensive trading report
        """
        try:
            report = {
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'period_days': days
            }
            
            if report_type in ['comprehensive', 'performance']:
                report['performance'] = self.get_performance_summary(days)
            
            if report_type in ['comprehensive', 'learning']:
                report['learning'] = self.get_learning_progress()
            
            if report_type in ['comprehensive', 'risk']:
                report['risk'] = self.get_risk_analysis(days)
            
            if report_type in ['comprehensive', 'market']:
                # Get symbols from database or use defaults
                symbols = self._get_trading_symbols()
                report['market'] = self.get_market_analysis(symbols)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {'error': str(e)}
    
    def _get_trades_data(self, days: int) -> pd.DataFrame:
        """Get trades data from database"""
        if not self.engine:
            return pd.DataFrame()
        
        try:
            query = f"""
            SELECT * FROM trades 
            WHERE timestamp >= NOW() - INTERVAL {days} DAY
            ORDER BY timestamp DESC
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                trades = result.fetchall()
            
            if trades:
                return pd.DataFrame(trades)
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting trades data: {e}")
            return pd.DataFrame()
    
    def _get_learning_data(self, symbol: str = None) -> List[Dict]:
        """Get learning progress data"""
        # This would typically come from the RL model's learning history
        # For now, return mock data
        return [
            {'episode': i, 'reward': np.random.normal(0.1, 0.2), 'timestamp': datetime.now() - timedelta(hours=i)}
            for i in range(100)
        ]
    
    def _calculate_daily_returns(self, trades_df: pd.DataFrame) -> pd.Series:
        """Calculate daily returns from trades"""
        if trades_df.empty:
            return pd.Series()
        
        # Group by date and sum P&L
        trades_df['date'] = pd.to_datetime(trades_df['timestamp']).dt.date
        daily_pnl = trades_df.groupby('date')['pnl'].sum()
        
        # Convert to returns (assuming constant portfolio value for simplicity)
        portfolio_value = 100000  # Default value
        daily_returns = daily_pnl / portfolio_value
        
        return daily_returns
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        try:
            # Annualized Sharpe ratio
            excess_returns = returns - 0.02/252  # Assuming 2% risk-free rate
            return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        except:
            return 0.0
    
    def _calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        if len(cumulative_returns) < 2:
            return 0.0
        
        try:
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            return drawdown.min()
        except:
            return 0.0
    
    def _calculate_symbol_performance(self, trades_df: pd.DataFrame) -> Dict:
        """Calculate performance by symbol"""
        if trades_df.empty:
            return {}
        
        symbol_perf = {}
        
        for symbol in trades_df['symbol'].unique():
            symbol_trades = trades_df[trades_df['symbol'] == symbol]
            
            symbol_perf[symbol] = {
                'total_trades': len(symbol_trades),
                'total_pnl': symbol_trades['pnl'].sum(),
                'win_rate': len(symbol_trades[symbol_trades['pnl'] > 0]) / len(symbol_trades),
                'avg_trade': symbol_trades['pnl'].mean(),
                'best_trade': symbol_trades['pnl'].max(),
                'worst_trade': symbol_trades['pnl'].min()
            }
        
        return symbol_perf
    
    def _calculate_trend(self, data: List[float]) -> float:
        """Calculate trend in data"""
        if len(data) < 2:
            return 0.0
        
        try:
            x = np.arange(len(data))
            slope = np.polyfit(x, data, 1)[0]
            return slope
        except:
            return 0.0
    
    def _calculate_symbol_returns(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns by symbol"""
        if trades_df.empty:
            return pd.DataFrame()
        
        try:
            trades_df['date'] = pd.to_datetime(trades_df['timestamp']).dt.date
            symbol_returns = trades_df.pivot_table(
                index='date', 
                columns='symbol', 
                values='pnl', 
                aggfunc='sum'
            ).fillna(0)
            
            return symbol_returns
        except:
            return pd.DataFrame()
    
    def _calculate_symbol_risk(self, trades_df: pd.DataFrame) -> Dict:
        """Calculate risk metrics by symbol"""
        if trades_df.empty:
            return {}
        
        symbol_risk = {}
        
        for symbol in trades_df['symbol'].unique():
            symbol_trades = trades_df[trades_df['symbol'] == symbol]
            returns = symbol_trades['pnl'] / symbol_trades['pnl'].abs().sum() if symbol_trades['pnl'].abs().sum() > 0 else pd.Series([0])
            
            symbol_risk[symbol] = {
                'volatility': returns.std() * np.sqrt(252),
                'var_95': np.percentile(returns, 5),
                'max_loss': returns.min(),
                'max_gain': returns.max()
            }
        
        return symbol_risk
    
    def _get_trading_symbols(self) -> List[str]:
        """Get list of trading symbols"""
        return ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA']
    
    def _empty_performance_summary(self) -> Dict:
        """Return empty performance summary"""
        return {
            'summary': {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'period_days': 0
            },
            'symbol_performance': {},
            'daily_returns': [],
            'timestamp': datetime.now().isoformat()
        } 