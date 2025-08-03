"""
Simplified Trading Bot Backend for Testing Alpaca Connection
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
trading_active = False

def test_alpaca_connection():
    """Test connection to Alpaca API"""
    try:
        api_key = os.getenv('ALPACA_PAPER_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET')
        
        if not api_key or not secret_key:
            return False, "API keys not configured"
        
        headers = {
            'APCA-API-KEY-ID': api_key,
            'APCA-API-SECRET-KEY': secret_key
        }
        
        # Test account endpoint
        response = requests.get(
            'https://paper-api.alpaca.markets/v2/account',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account_data = response.json()
            return True, account_data
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    # Test Alpaca connection
    connected, result = test_alpaca_connection()
    
    return jsonify({
        'status': 'healthy' if connected else 'warning',
        'timestamp': datetime.now().isoformat(),
        'trading_active': trading_active,
        'alpaca_connected': connected,
        'alpaca_result': result if isinstance(result, dict) else str(result),
        'mode': os.getenv('MODE', 'paper'),
        'configured_stocks': os.getenv('STOCKS', 'AAPL,TSLA').split(',')
    })

@app.route('/start', methods=['POST'])
def start_trading():
    """Start trading simulation"""
    global trading_active
    
    try:
        # Test Alpaca connection first
        connected, result = test_alpaca_connection()
        
        if not connected:
            return jsonify({
                'success': False,
                'error': f'Cannot start trading: {result}'
            }), 400
        
        trading_active = True
        
        logger.info("Trading simulation started")
        
        return jsonify({
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'mode': os.getenv('MODE', 'paper'),
            'stocks': os.getenv('STOCKS', 'AAPL,TSLA').split(','),
            'account_info': result
        })
        
    except Exception as e:
        logger.error(f"Error starting trading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_trading():
    """Stop trading simulation"""
    global trading_active
    
    trading_active = False
    logger.info("Trading simulation stopped")
    
    return jsonify({
        'status': 'stopped',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Get current trading status"""
    try:
        # Get account info if connected
        connected, account_data = test_alpaca_connection()
        
        portfolio = {}
        if connected and isinstance(account_data, dict):
            # Create mock portfolio data
            stocks = os.getenv('STOCKS', 'AAPL,TSLA,GOOGL,MSFT,NVDA').split(',')
            for stock in stocks:
                portfolio[stock] = {
                    'performance': {
                        'balance': float(account_data.get('cash', 100000)) / len(stocks),
                        'position': 0,
                        'total_trades': 0,
                        'win_rate': 0,
                        'total_return': 0
                    }
                }
        
        return jsonify({
            'trading_active': trading_active,
            'mode': os.getenv('MODE', 'paper'),
            'stocks': os.getenv('STOCKS', 'AAPL,TSLA').split(','),
            'portfolio': portfolio,
            'learning_progress': {},
            'timestamp': datetime.now().isoformat(),
            'alpaca_connected': connected,
            'account_balance': account_data.get('cash') if isinstance(account_data, dict) else 'N/A'
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/switch-mode', methods=['POST'])
def switch_mode():
    """Switch trading mode"""
    try:
        data = request.get_json()
        new_mode = data.get('mode')
        
        if new_mode not in ['paper', 'live']:
            return jsonify({'error': 'Invalid mode'}), 400
        
        # Update environment variable (in memory)
        os.environ['MODE'] = new_mode
        
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
        
        # Update environment variable (in memory)
        os.environ['STOCKS'] = ','.join(new_stocks)
        
        logger.info(f"Reconfigured stocks: {new_stocks}")
        
        return jsonify({
            'stocks': new_stocks,
            'timestamp': datetime.now().isoformat(),
            'trading_active': trading_active,
            'message': f'Successfully configured {len(new_stocks)} stocks'
        })
        
    except Exception as e:
        logger.error(f"Error configuring stocks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/evaluate/<symbol>', methods=['GET'])
def evaluate_agent(symbol):
    """Evaluate specific agent performance (mock implementation)"""
    try:
        # Mock evaluation data
        evaluation = {
            'total_reward': 1250.75,
            'episode_count': 100,
            'mean_reward': 12.51,
            'std_reward': 8.33,
            'success_rate': 0.68,
            'trades_count': 45,
            'win_rate': 0.67,
            'sharpe_ratio': 1.42,
            'max_drawdown': -0.08,
            'volatility': 0.15
        }
        
        return jsonify({
            'symbol': symbol,
            'evaluation': evaluation,
            'timestamp': datetime.now().isoformat(),
            'message': f'Agent evaluation completed for {symbol}'
        })
        
    except Exception as e:
        logger.error(f"Error evaluating agent {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/retrain/<symbol>', methods=['POST'])
def retrain_agent(symbol):
    """Retrain specific agent (mock implementation)"""
    try:
        data = request.get_json() or {}
        timesteps = data.get('timesteps', 50000)
        
        # Mock retraining response
        return jsonify({
            'symbol': symbol,
            'status': 'retraining_started',
            'timesteps': timesteps,
            'estimated_duration': '10-15 minutes',
            'timestamp': datetime.now().isoformat(),
            'message': f'Retraining started for {symbol} with {timesteps} timesteps'
        })
        
    except Exception as e:
        logger.error(f"Error starting retraining for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent trading logs (mock implementation)"""
    try:
        # Mock log data
        logs = [
            {
                'timestamp': (datetime.now()).isoformat(),
                'level': 'INFO',
                'message': 'Trading system operational',
                'symbol': 'SYSTEM'
            },
            {
                'timestamp': (datetime.now()).isoformat(),
                'level': 'INFO', 
                'message': f'Alpaca connection verified - Account active',
                'symbol': 'SYSTEM'
            },
            {
                'timestamp': (datetime.now()).isoformat(),
                'level': 'INFO',
                'message': f'Portfolio balance: $100,000',
                'symbol': 'PORTFOLIO'
            },
            {
                'timestamp': (datetime.now()).isoformat(),
                'level': 'INFO',
                'message': 'AAPL agent ready for trading',
                'symbol': 'AAPL'
            },
            {
                'timestamp': (datetime.now()).isoformat(),
                'level': 'INFO',
                'message': 'TSLA agent ready for trading',
                'symbol': 'TSLA'
            }
        ]
        
        return jsonify({
            'logs': logs,
            'count': len(logs),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'error': str(e)}), 500

# Training System Integration
from advanced_training_system import AdvancedTrainingSystem

# Initialize training system
training_system = AdvancedTrainingSystem()

@app.route('/training/search-stocks', methods=['GET'])
def search_stocks():
    """Search for stocks by symbol or company name"""
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        stocks = training_system.search_stocks(query)
        return jsonify({
            'stocks': stocks,
            'query': query,
            'count': len(stocks),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/training/stock-info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """Get detailed information about a specific stock"""
    try:
        stock_info = training_system.get_stock_info(symbol)
        return jsonify({
            'stock': stock_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting stock info for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/training/import-data', methods=['POST'])
def import_data():
    """Import historical data for training"""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol')
        months = data.get('months', 3)
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        result = training_system.import_historical_data(symbol, months)
        return jsonify({
            'import_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/training/train-model', methods=['POST'])
def train_model():
    """Train advanced AI model"""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol')
        model_type = data.get('model_type', 'PPO')
        training_steps = data.get('training_steps', 50000)
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        result = training_system.train_advanced_model(symbol, model_type, training_steps)
        return jsonify({
            'training_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/training/simulation', methods=['POST'])
def run_simulation():
    """Run trading simulation"""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol')
        days = data.get('days', 30)
        model_path = data.get('model_path')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        result = training_system.run_simulation(symbol, days, model_path)
        return jsonify({
            'simulation_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/training/status', methods=['GET'])
def get_training_status():
    """Get training status"""
    try:
        training_id = request.args.get('training_id')
        status = training_system.get_training_status(training_id)
        return jsonify({
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/training/models', methods=['GET'])
def get_available_models():
    """Get available trained models"""
    try:
        models = training_system.get_available_models()
        return jsonify({
            'models': models,
            'count': len(models),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Simplified Trading Bot API Server")
    
    # Test Alpaca connection on startup
    connected, result = test_alpaca_connection()
    if connected:
        logger.info("✓ Alpaca API connection successful")
        if isinstance(result, dict):
            logger.info(f"Account Cash: ${result.get('cash', 'N/A')}")
    else:
        logger.warning(f"⚠️  Alpaca API connection failed: {result}")
    
    port = int(os.getenv('PORT', 8080))  # Use port 8080
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)