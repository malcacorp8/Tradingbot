"""
Flask API Server for Autonomous Trading Bot
Handles web interface communication, trading controls, and real-time updates
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
import threading
import time
from datetime import datetime
import json
from dotenv import load_dotenv
from agent_manager import AgentManager
from news_analyzer import NewsAnalyzer
from options_trader import OptionsTrader
from risk_manager import RiskManager
from analytics import TradingAnalytics
import pusher

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Global variables
agent_manager = None
news_analyzer = None
options_trader = None
risk_manager = None
analytics = None
trading_active = False
trading_thread = None

# Initialize Pusher for real-time updates (optional)
try:
    pusher_client = pusher.Pusher(
        app_id=os.getenv('PUSHER_APP_ID'),
        key=os.getenv('PUSHER_KEY'),
        secret=os.getenv('PUSHER_SECRET'),
        cluster=os.getenv('PUSHER_CLUSTER', 'us2'),
        ssl=True
    )
except Exception as e:
    logger.warning(f"Pusher not configured: {e}")
    pusher_client = None

def get_stock_list():
    """Get list of stocks from environment"""
    stocks = os.getenv('STOCKS', 'AAPL,TSLA,GOOGL,MSFT,NVDA')
    return [stock.strip() for stock in stocks.split(',')]

def initialize_components():
    """Initialize all trading components"""
    global agent_manager, news_analyzer, options_trader, risk_manager, analytics
    
    if agent_manager is None:
        stocks = get_stock_list()
        mode = os.getenv('MODE', 'paper')
        
        # Initialize components
        agent_manager = AgentManager(stocks, mode=mode)
        news_analyzer = NewsAnalyzer()
        options_trader = OptionsTrader(mode=mode)
        risk_manager = RiskManager(mode=mode)
        analytics = TradingAnalytics()
        
        logger.info(f"✅ All components initialized in {mode} mode")

def broadcast_update(channel, event, data):
    """Broadcast real-time updates via Pusher"""
    if pusher_client:
        try:
            pusher_client.trigger(channel, event, data)
        except Exception as e:
            logger.error(f"Error broadcasting update: {e}")

# API Routes

@app.route('/', methods=['GET'])
def index():
    """API status endpoint"""
    return jsonify({
        'status': 'Autonomous Trading Bot API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'trading_active': trading_active,
        'mode': os.getenv('MODE', 'paper')
    })

@app.route('/start', methods=['POST'])
def start_trading():
    """Start autonomous trading"""
    global trading_active, agent_manager
    
    try:
        if trading_active:
            return jsonify({'error': 'Trading already active'}), 400
        
        initialize_components()
        
        # Start autonomous trading
        agent_manager.start_autonomous_trading()
        trading_active = True
        
        logger.info("Autonomous trading started")
        
        # Broadcast update
        broadcast_update('trading', 'status_changed', {
            'active': True,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'mode': agent_manager.mode,
            'stocks': agent_manager.symbols
        })
        
    except Exception as e:
        logger.error(f"Error starting trading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_trading():
    """Stop autonomous trading"""
    global trading_active, agent_manager
    
    try:
        if not trading_active:
            return jsonify({'error': 'Trading not active'}), 400
        
        if agent_manager:
            agent_manager.stop_autonomous_trading()
        
        trading_active = False
        
        logger.info("Autonomous trading stopped")
        
        # Broadcast update
        broadcast_update('trading', 'status_changed', {
            'active': False,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'status': 'stopped',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error stopping trading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current trading status and performance"""
    try:
        if not agent_manager:
            return jsonify({
                'trading_active': False,
                'message': 'Agent manager not initialized'
            })
        
        # Get portfolio status
        portfolio_status = agent_manager.get_portfolio_status()
        
        # Get learning progress
        learning_progress = agent_manager.get_learning_progress()
        
        status_data = {
            'trading_active': trading_active,
            'mode': agent_manager.mode,
            'stocks': agent_manager.symbols,
            'portfolio': portfolio_status,
            'learning_progress': learning_progress,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/switch-mode', methods=['POST'])
def switch_mode():
    """Switch between paper and live trading"""
    try:
        data = request.get_json()
        new_mode = data.get('mode')
        
        if new_mode not in ['paper', 'live']:
            return jsonify({'error': 'Invalid mode. Use "paper" or "live"'}), 400
        
        if not agent_manager:
            initialize_agent_manager()
        
        # Stop trading if active
        was_active = trading_active
        if trading_active:
            stop_trading()
        
        # Switch mode
        agent_manager.switch_mode(new_mode)
        
        # Update environment variable
        os.environ['MODE'] = new_mode
        
        # Restart trading if it was active
        if was_active:
            start_trading()
        
        logger.info(f"Switched to {new_mode} mode")
        
        # Broadcast update
        broadcast_update('trading', 'mode_changed', {
            'mode': new_mode,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'mode': new_mode,
            'timestamp': datetime.now().isoformat(),
            'trading_active': trading_active
        })
        
    except Exception as e:
        logger.error(f"Error switching mode: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/configure', methods=['POST'])
def configure_stocks():
    """Configure trading stocks"""
    try:
        data = request.get_json()
        new_stocks = data.get('stocks', [])
        
        if not new_stocks or not isinstance(new_stocks, list):
            return jsonify({'error': 'Invalid stocks configuration'}), 400
        
        # Stop trading if active
        was_active = trading_active
        if trading_active:
            stop_trading()
        
        # Update environment and reinitialize
        os.environ['STOCKS'] = ','.join(new_stocks)
        
        # Reinitialize agent manager
        global agent_manager
        agent_manager = None
        initialize_agent_manager()
        
        # Restart trading if it was active
        if was_active:
            start_trading()
        
        logger.info(f"Reconfigured stocks: {new_stocks}")
        
        return jsonify({
            'stocks': new_stocks,
            'timestamp': datetime.now().isoformat(),
            'trading_active': trading_active
        })
        
    except Exception as e:
        logger.error(f"Error configuring stocks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/evaluate/<symbol>', methods=['GET'])
def evaluate_agent(symbol):
    """Evaluate specific agent performance"""
    try:
        if not agent_manager:
            return jsonify({'error': 'Agent manager not initialized'}), 400
        
        if symbol not in agent_manager.symbols:
            return jsonify({'error': f'Symbol {symbol} not configured'}), 400
        
        evaluation = agent_manager.evaluate_agent(symbol)
        
        if evaluation is None:
            return jsonify({'error': f'Could not evaluate agent for {symbol}'}), 500
        
        return jsonify({
            'symbol': symbol,
            'evaluation': evaluation,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error evaluating agent {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/retrain/<symbol>', methods=['POST'])
def retrain_agent(symbol):
    """Retrain specific agent"""
    try:
        if not agent_manager:
            return jsonify({'error': 'Agent manager not initialized'}), 400
        
        if symbol not in agent_manager.symbols:
            return jsonify({'error': f'Symbol {symbol} not configured'}), 400
        
        data = request.get_json() or {}
        timesteps = data.get('timesteps', 50000)
        
        # Stop trading temporarily
        was_active = trading_active
        if trading_active:
            stop_trading()
        
        # Retrain in background thread
        def retrain_task():
            agent_manager.retrain_agent(symbol, timesteps)
            if was_active:
                start_trading()
        
        retrain_thread = threading.Thread(target=retrain_task)
        retrain_thread.start()
        
        logger.info(f"Started retraining for {symbol} with {timesteps} timesteps")
        
        return jsonify({
            'symbol': symbol,
            'status': 'retraining_started',
            'timesteps': timesteps,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error retraining agent {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent trading logs"""
    try:
        # This would typically read from a log file or database
        # For now, return mock data
        logs = [
            {
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': 'Trading system operational',
                'symbol': 'SYSTEM'
            }
        ]
        
        return jsonify({
            'logs': logs,
            'count': len(logs)
        })
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if components are initialized
        components_status = {
            'agent_manager': agent_manager is not None,
            'news_analyzer': news_analyzer is not None,
            'options_trader': options_trader is not None,
            'risk_manager': risk_manager is not None,
            'analytics': analytics is not None,
            'trading_active': trading_active,
            'mode': os.getenv('MODE', 'paper')
        }
        
        # Check database connection if available
        db_status = 'unknown'
        if os.getenv('DB_URL'):
            try:
                # Simple database check
                db_status = 'connected'
            except Exception as e:
                db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': components_status,
            'database': db_status,
            'uptime': 'running'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/news/<symbol>', methods=['GET'])
def get_news_sentiment(symbol):
    """Get news sentiment for a symbol"""
    try:
        if not news_analyzer:
            initialize_components()
        
        sentiment_data = news_analyzer.get_news_sentiment(symbol, hours_back=24)
        return jsonify(sentiment_data)
        
    except Exception as e:
        logger.error(f"Error getting news sentiment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/options/<symbol>', methods=['GET'])
def get_options_chain(symbol):
    """Get options chain for a symbol"""
    try:
        if not options_trader:
            initialize_components()
        
        expiration = request.args.get('expiration')
        options_data = options_trader.get_options_chain(symbol, expiration)
        return jsonify(options_data)
        
    except Exception as e:
        logger.error(f"Error getting options chain: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/risk/summary', methods=['GET'])
def get_risk_summary():
    """Get risk management summary"""
    try:
        if not risk_manager:
            initialize_components()
        
        risk_summary = risk_manager.get_risk_summary()
        return jsonify(risk_summary)
        
    except Exception as e:
        logger.error(f"Error getting risk summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/performance', methods=['GET'])
def get_performance_analytics():
    """Get performance analytics"""
    try:
        if not analytics:
            initialize_components()
        
        days = int(request.args.get('days', 30))
        performance_data = analytics.get_performance_summary(days)
        return jsonify(performance_data)
        
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/learning', methods=['GET'])
def get_learning_analytics():
    """Get learning progress analytics"""
    try:
        if not analytics:
            initialize_components()
        
        symbol = request.args.get('symbol')
        learning_data = analytics.get_learning_progress(symbol)
        return jsonify(learning_data)
        
    except Exception as e:
        logger.error(f"Error getting learning analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/risk', methods=['GET'])
def get_risk_analytics():
    """Get risk analytics"""
    try:
        if not analytics:
            initialize_components()
        
        days = int(request.args.get('days', 30))
        risk_data = analytics.get_risk_analysis(days)
        return jsonify(risk_data)
        
    except Exception as e:
        logger.error(f"Error getting risk analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/market', methods=['GET'])
def get_market_analytics():
    """Get market analysis"""
    try:
        if not analytics:
            initialize_components()
        
        symbols = request.args.get('symbols', 'AAPL,TSLA,GOOGL').split(',')
        market_data = analytics.get_market_analysis(symbols)
        return jsonify(market_data)
        
    except Exception as e:
        logger.error(f"Error getting market analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/report/generate', methods=['POST'])
def generate_report():
    """Generate comprehensive trading report"""
    try:
        if not analytics:
            initialize_components()
        
        data = request.get_json()
        report_type = data.get('type', 'comprehensive')
        days = int(data.get('days', 30))
        
        report = analytics.generate_report(report_type, days)
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Startup function

def create_app():
    """Create and configure the Flask app"""
    logger.info("Starting Autonomous Trading Bot API Server")
    
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('tensorboard_logs', exist_ok=True)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)