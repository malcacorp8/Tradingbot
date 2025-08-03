"""
Database Models and Connection Management
Handles trade logging, configuration storage, and performance tracking
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DB_URL', 'sqlite:///trading_bot.db')

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Models

class Trade(Base):
    """Trade execution records"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    action = Column(String(20))  # buy, sell, hold, buy_call, buy_put
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    mode = Column(String(10))  # paper or live
    reward = Column(Float)
    balance_before = Column(Float)
    balance_after = Column(Float)
    position_before = Column(Integer)
    position_after = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

class AgentPerformance(Base):
    """Agent performance tracking"""
    __tablename__ = "agent_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    episode_number = Column(Integer)
    total_reward = Column(Float)
    win_rate = Column(Float)
    total_return = Column(Float)
    sharpe_ratio = Column(Float)
    total_trades = Column(Integer)
    successful_trades = Column(Integer)
    balance = Column(Float)
    learning_cycle = Column(Integer)

class TradingSession(Base):
    """Trading session records"""
    __tablename__ = "trading_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    mode = Column(String(10))
    initial_balance = Column(Float)
    final_balance = Column(Float, nullable=True)
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    symbols_traded = Column(Text)  # JSON string of symbols
    is_active = Column(Boolean, default=True)

class SystemLog(Base):
    """System logs and events"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String(10))  # INFO, WARNING, ERROR
    message = Column(Text)
    symbol = Column(String(10), nullable=True)
    component = Column(String(50))  # agent, api, trading_env, etc.

class Configuration(Base):
    """System configuration settings"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Database functions

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Error getting database session: {e}")
        db.close()
        raise

def log_trade(symbol: str, action: str, quantity: int, price: float, 
              mode: str, reward: float, balance_before: float, balance_after: float,
              position_before: int, position_after: int, success: bool = True,
              error_message: str = None):
    """Log a trade execution"""
    try:
        db = get_db()
        
        trade = Trade(
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            mode=mode,
            reward=reward,
            balance_before=balance_before,
            balance_after=balance_after,
            position_before=position_before,
            position_after=position_after,
            success=success,
            error_message=error_message
        )
        
        db.add(trade)
        db.commit()
        db.refresh(trade)
        db.close()
        
        logger.info(f"Trade logged: {symbol} {action} {quantity}@{price}")
        return trade.id
        
    except Exception as e:
        logger.error(f"Error logging trade: {e}")
        if db:
            db.close()
        return None

def log_agent_performance(symbol: str, episode_number: int, performance_metrics: dict,
                         learning_cycle: int):
    """Log agent performance metrics"""
    try:
        db = get_db()
        
        performance = AgentPerformance(
            symbol=symbol,
            episode_number=episode_number,
            total_reward=performance_metrics.get('total_return', 0),
            win_rate=performance_metrics.get('win_rate', 0),
            total_return=performance_metrics.get('total_return', 0),
            sharpe_ratio=performance_metrics.get('sharpe_ratio', 0),
            total_trades=performance_metrics.get('total_trades', 0),
            successful_trades=performance_metrics.get('total_trades', 0) * performance_metrics.get('win_rate', 0),
            balance=performance_metrics.get('balance', 0),
            learning_cycle=learning_cycle
        )
        
        db.add(performance)
        db.commit()
        db.close()
        
        logger.info(f"Performance logged for {symbol}: episode {episode_number}")
        
    except Exception as e:
        logger.error(f"Error logging performance: {e}")
        if db:
            db.close()

def start_trading_session(mode: str, initial_balance: float, symbols: list):
    """Start a new trading session"""
    try:
        db = get_db()
        
        session = TradingSession(
            mode=mode,
            initial_balance=initial_balance,
            symbols_traded=','.join(symbols)
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        db.close()
        
        logger.info(f"Trading session started: {session.id}")
        return session.id
        
    except Exception as e:
        logger.error(f"Error starting trading session: {e}")
        if db:
            db.close()
        return None

def end_trading_session(session_id: int, final_balance: float, 
                       total_trades: int, successful_trades: int):
    """End a trading session"""
    try:
        db = get_db()
        
        session = db.query(TradingSession).filter(TradingSession.id == session_id).first()
        if session:
            session.end_time = datetime.utcnow()
            session.final_balance = final_balance
            session.total_trades = total_trades
            session.successful_trades = successful_trades
            session.is_active = False
            
            db.commit()
            
        db.close()
        logger.info(f"Trading session ended: {session_id}")
        
    except Exception as e:
        logger.error(f"Error ending trading session: {e}")
        if db:
            db.close()

def log_system_event(level: str, message: str, symbol: str = None, component: str = "system"):
    """Log system events"""
    try:
        db = get_db()
        
        log_entry = SystemLog(
            level=level,
            message=message,
            symbol=symbol,
            component=component
        )
        
        db.add(log_entry)
        db.commit()
        db.close()
        
    except Exception as e:
        logger.error(f"Error logging system event: {e}")
        if db:
            db.close()

def get_recent_trades(limit: int = 100, symbol: str = None):
    """Get recent trades"""
    try:
        db = get_db()
        
        query = db.query(Trade).order_by(Trade.timestamp.desc())
        
        if symbol:
            query = query.filter(Trade.symbol == symbol)
        
        trades = query.limit(limit).all()
        db.close()
        
        return [
            {
                'id': trade.id,
                'symbol': trade.symbol,
                'action': trade.action,
                'quantity': trade.quantity,
                'price': trade.price,
                'timestamp': trade.timestamp.isoformat(),
                'mode': trade.mode,
                'reward': trade.reward,
                'success': trade.success
            }
            for trade in trades
        ]
        
    except Exception as e:
        logger.error(f"Error getting recent trades: {e}")
        if db:
            db.close()
        return []

def get_performance_history(symbol: str = None, limit: int = 100):
    """Get performance history"""
    try:
        db = get_db()
        
        query = db.query(AgentPerformance).order_by(AgentPerformance.timestamp.desc())
        
        if symbol:
            query = query.filter(AgentPerformance.symbol == symbol)
        
        performances = query.limit(limit).all()
        db.close()
        
        return [
            {
                'symbol': perf.symbol,
                'timestamp': perf.timestamp.isoformat(),
                'episode_number': perf.episode_number,
                'total_reward': perf.total_reward,
                'win_rate': perf.win_rate,
                'total_return': perf.total_return,
                'sharpe_ratio': perf.sharpe_ratio,
                'total_trades': perf.total_trades,
                'balance': perf.balance,
                'learning_cycle': perf.learning_cycle
            }
            for perf in performances
        ]
        
    except Exception as e:
        logger.error(f"Error getting performance history: {e}")
        if db:
            db.close()
        return []

def get_system_logs(limit: int = 100, level: str = None):
    """Get system logs"""
    try:
        db = get_db()
        
        query = db.query(SystemLog).order_by(SystemLog.timestamp.desc())
        
        if level:
            query = query.filter(SystemLog.level == level)
        
        logs = query.limit(limit).all()
        db.close()
        
        return [
            {
                'timestamp': log.timestamp.isoformat(),
                'level': log.level,
                'message': log.message,
                'symbol': log.symbol,
                'component': log.component
            }
            for log in logs
        ]
        
    except Exception as e:
        logger.error(f"Error getting system logs: {e}")
        if db:
            db.close()
        return []

# Initialize database on import
try:
    create_tables()
except Exception as e:
    logger.error(f"Error initializing database: {e}")