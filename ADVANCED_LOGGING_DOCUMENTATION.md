# Advanced Trading Logs Documentation

## Overview

The Advanced Trading Logs system provides comprehensive logging, filtering, and download capabilities for trading bot activities. It supports daily, stock-specific, and bot-specific log organization with advanced filtering and archival features.

## Features

### 📊 Log Organization
- **Daily Logs**: All trading activities organized by date
- **Stock-Specific Logs**: Activities filtered by individual stocks
- **Bot-Specific Logs**: Activities filtered by bot type (PPO, DQN, A2C, SAC)
- **Structured JSON Format**: Consistent, machine-readable log entries

### 🔍 Advanced Filtering
- **Date Range Filtering**: Filter logs by start and end dates
- **Multi-level Organization**: Daily/Stock/Bot hierarchical structure
- **Action Type Filtering**: Filter by buy, sell, hold, train, import, simulate
- **Real-time Summary Statistics**: Live activity counts and metrics

### 📥 Download Capabilities
- **Filtered Downloads**: Download specific log subsets
- **Multiple Formats**: JSON export with metadata
- **Batch Operations**: Download logs for multiple criteria
- **File Size Optimization**: Efficient data compression

## System Architecture

### Backend Components

#### AdvancedTradingLogger Class
```python
class AdvancedTradingLogger:
    """Advanced logging system for trading bot activities"""
    
    def __init__(self, base_log_dir="logs/trading"):
        self.base_log_dir = Path(base_log_dir)
        self.daily_logs_dir = self.base_log_dir / "daily"
        self.stock_logs_dir = self.base_log_dir / "stocks"
        self.bot_logs_dir = self.base_log_dir / "bots"
        self.archived_logs_dir = self.base_log_dir / "archived"
    
    def log_trading_activity(self, stock_symbol, bot_type, action, details, timestamp=None):
        """Log activity to daily, stock, and bot specific files"""
        
    def get_logs(self, log_type="daily", identifier=None, start_date=None, end_date=None):
        """Retrieve logs with filtering"""
        
    def archive_old_logs(self, days_to_keep=90):
        """Archive logs older than specified days"""
```

#### Log Entry Structure
```json
{
    "timestamp": "2025-08-05T14:30:15.123456",
    "stock": "AAPL",
    "bot_type": "PPO",
    "action": "buy",
    "details": {
        "price": 214.05,
        "quantity": 10,
        "portfolio_value": 10150.25,
        "profit_loss": 23.50,
        "confidence": 0.85
    }
}
```

### API Endpoints

#### Get Advanced Logs
```http
GET /api/logs/advanced?type=bot&identifier=PPO&start_date=2024-07-01&end_date=2025-08-05
```

#### Get Log Summary
```http
GET /api/logs/summary?start_date=2024-07-01&end_date=2025-08-05
```

#### Download Logs
```http
GET /api/logs/download?type=stock&identifier=AAPL&start_date=2024-07-01&end_date=2025-08-05
```

#### Get Available Options
```http
GET /api/logs/stocks  # Returns list of stocks with logs
GET /api/logs/bots    # Returns list of bot types with logs
```

#### Archive Old Logs
```http
POST /api/logs/archive
Content-Type: application/json

{
    "days_to_keep": 90
}
```

## Frontend Interface

### Log Summary Dashboard
- **Total Activities**: Count of all logged activities
- **Active Stocks**: Number of stocks with trading logs
- **Bot Types**: Number of different bot types active
- **Action Types**: Variety of actions logged

### Advanced Filtering Controls
- **Log Type Selector**: Daily, Stock-Specific, Bot-Specific
- **Dynamic Dropdowns**: Stock and bot type selection
- **Date Range Pickers**: Start and end date selection
- **Filter Actions**: Apply, Reset, Download, Archive

### Log Display
- **Structured View**: Organized, readable log entries
- **Color Coding**: Different colors for different action types
- **Pagination**: Handle large log datasets
- **Real-time Updates**: Live log streaming

## Log Types and Data

### Daily Logs
```
logs/trading/daily/2025-08-05.json
```
- All trading activities for a specific date
- Comprehensive daily summary
- Cross-stock and cross-bot activities

### Stock-Specific Logs
```
logs/trading/stocks/AAPL/2025-08-05.json
```
- All activities for a specific stock
- Multi-bot trading decisions
- Stock-specific performance metrics

### Bot-Specific Logs
```
logs/trading/bots/PPO/2025-08-05.json
```
- All activities for a specific bot type
- Cross-stock bot performance
- Bot-specific decision patterns

## Sample Data Structure

### Log Summary Response
```json
{
    "success": true,
    "summary": {
        "total_activities": 280,
        "date_range": {
            "start": "2025-07-06",
            "end": "2025-08-05"
        },
        "stocks": {
            "AAPL": 32,
            "TSLA": 41,
            "GOOGL": 42,
            "MSFT": 38,
            "NVDA": 35,
            "META": 45,
            "AMZN": 47
        },
        "bots": {
            "PPO": 79,
            "DQN": 66,
            "A2C": 72,
            "SAC": 63
        },
        "actions": {
            "buy": 68,
            "sell": 71,
            "hold": 89,
            "train_model": 21,
            "import_data": 16,
            "simulation_run": 15
        }
    }
}
```

### Download File Structure
```json
{
    "export_info": {
        "exported_at": "2025-08-05T13:04:11.174760",
        "type": "bot",
        "identifier": "PPO",
        "date_range": {
            "start": "2024-07-01",
            "end": "2025-08-05"
        },
        "total_records": 79
    },
    "logs": [
        {
            "timestamp": "2025-08-05T16:37:13.283947",
            "stock": "AMZN",
            "bot_type": "PPO",
            "action": "import_data",
            "details": {
                "data_points": 2265,
                "time_range_days": 2,
                "success": true
            }
        }
    ]
}
```

## Testing Results

### API Performance
- **All Bot Types**: Successfully tested PPO, DQN, A2C, SAC
- **Stock Downloads**: Verified AAPL, TSLA, GOOGL downloads
- **Daily Logs**: 280 total logs across 30 days
- **File Sizes**: 20KB-25KB per bot type download

### Download Verification
```bash
# Bot-specific downloads
✅ A2C: 72 logs, 22,682 bytes downloaded
✅ DQN: 66 logs, 21,414 bytes downloaded  
✅ PPO: 79 logs, 25,154 bytes downloaded
✅ SAC: 63 logs, 20,535 bytes downloaded

# Stock-specific downloads
✅ AAPL: 32 logs, 10,254 bytes downloaded
✅ TSLA: 41 logs, 13,308 bytes downloaded
✅ GOOGL: 42 logs, 13,828 bytes downloaded

# Daily logs download
✅ All Daily Logs: 280 total logs, 89,064 bytes downloaded
```

## Usage Instructions

### Accessing Logs
1. Navigate to the **Logs** page in the dashboard
2. View the summary dashboard for overview statistics
3. Use advanced filters to narrow down log entries

### Filtering Logs
1. **Select Log Type**: Choose Daily, Stock-Specific, or Bot-Specific
2. **Choose Identifier**: Select specific stock or bot type (if applicable)
3. **Set Date Range**: Choose start and end dates
4. **Apply Filters**: Click "Filter Logs" to update display

### Downloading Logs
1. **Set Filters**: Configure desired log criteria
2. **Click Download**: Use "📥 Download" button
3. **File Opens**: Download file opens in new tab
4. **JSON Format**: Structured data with export metadata

### Archiving Logs
1. **Click Archive**: Use "📦 Archive Old" button
2. **Set Retention**: Enter days to keep (default: 90)
3. **Confirm Action**: Archive moves old logs to compressed storage
4. **Free Space**: Reduces active log storage usage

## Configuration

### Log Directories
```
logs/trading/
├── daily/           # Daily organized logs
├── stocks/          # Stock-specific logs
├── bots/            # Bot-specific logs
└── archived/        # Compressed old logs
```

### Sample Log Generation
The system includes sample log generation for demonstration:
- **30 Days**: Historical sample data
- **7 Stocks**: AAPL, TSLA, GOOGL, MSFT, NVDA, META, AMZN
- **4 Bot Types**: PPO, DQN, A2C, SAC
- **6 Action Types**: buy, sell, hold, train_model, import_data, simulation_run

## Security and Privacy

### Data Protection
- **Local Storage**: All logs stored locally
- **No External Transmission**: Logs remain on server
- **Structured Access**: API-controlled log access
- **Archival Compression**: Old logs compressed with gzip

### Access Control
- **Authentication Required**: Web routes protected
- **API Endpoints**: Read operations unrestricted, write operations protected
- **Download Security**: Direct file serving with proper headers

## Troubleshooting

### Common Issues
1. **No Logs Found**: Check date range and filter criteria
2. **Download Fails**: Verify API endpoint accessibility
3. **Large File Sizes**: Use date filtering to reduce dataset
4. **Missing Data**: Ensure trading activities have been logged

### Debug Steps
1. Check log summary for data availability
2. Verify API endpoints return successful responses
3. Confirm log files exist in directory structure
4. Test with smaller date ranges first

## Future Enhancements

### Planned Features
- **Real-time Log Streaming**: Live activity updates
- **Advanced Search**: Full-text search within log details
- **Log Analytics**: Trend analysis and pattern recognition
- **Export Formats**: CSV, Excel, PDF export options
- **Log Visualization**: Charts and graphs for log data
- **Automated Archival**: Scheduled log cleanup

### Performance Optimizations
- **Database Integration**: Move from file-based to database storage
- **Indexing**: Add search indexes for faster queries
- **Caching**: Cache frequently accessed log summaries
- **Compression**: Real-time log compression

## Conclusion

The Advanced Trading Logs system provides comprehensive visibility into trading bot activities with:
- **Complete Audit Trail**: Every action logged with details
- **Flexible Filtering**: Multiple ways to slice and dice data
- **Easy Downloads**: Export capabilities for analysis
- **Efficient Storage**: Organized structure with archival support
- **User-Friendly Interface**: Intuitive web-based log management

This system enables thorough analysis of trading bot performance and decision-making patterns across different timeframes, stocks, and bot configurations.