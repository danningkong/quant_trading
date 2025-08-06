# 🎯 Quant Trading Platform
no
A comprehensive quantitative trading platform featuring advanced stock screening strategies, backtesting capabilities, and an interactive web interface.

## ✨ Features

### 📊 Stock Screening
- **7 Advanced Screening Strategies:**
  - **Momentum**: Price momentum, earnings momentum, relative strength
  - **Value**: Classic value, deep value, value with quality
  - **Growth**: High growth, GARP (Growth at Reasonable Price), small cap growth
  - **Quality**: High quality metrics, dividend aristocrats, low debt quality
  - **Technical**: Breakout patterns, golden cross, oversold bounce
  - **Volatility**: Low volatility, volatility breakout strategies
  - **Dividend**: High yield, dividend growth strategies

### 🔄 Backtesting Engine
- **Performance Metrics**: Total return, annual return, Sharpe ratio, Sortino ratio
- **Risk Analysis**: Maximum drawdown, win rate, profit factor
- **Strategy Templates**: Momentum, equal weight, mean reversion
- **Flexible Parameters**: Custom rebalancing frequency, position sizing
- **Trade Analysis**: Detailed trade history and P&L tracking

### 🌐 Web Interface
- **Interactive Dashboard**: Real-time metrics and quick actions
- **Stock Screener**: Dynamic filtering with multiple criteria
- **Backtest Visualizer**: Equity curves and performance charts
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Internet connection for market data
- Corporate network access to artifactory (if behind corporate firewall)

### Installation & Launch

1. **Navigate to the project directory:**
   ```bash
   cd "C:\Dev\AI\Claude_Code\Quant Trading"
   ```

2. **Run the startup script:**
   ```bash
   python start_server.py
   ```

3. **Access the platform:**
   - 🌐 **Web Interface**: http://localhost:8000
   - 📡 **API Documentation**: http://localhost:8000/docs
   - ✅ **Health Check**: http://localhost:8000/api/health

The startup script will automatically:
- ✅ Check and install dependencies
- 🚀 Start the FastAPI server
- 🌐 Open your web browser
- 📊 Display the dashboard

## 📁 Project Structure

```
Quant Trading/
├── 🐍 backend/                 # Python backend
│   ├── 🔄 api/                 # FastAPI endpoints
│   │   └── main.py             # Main API server
│   ├── 📈 strategies/          # Trading strategies
│   │   ├── screeners.py        # Stock screening logic
│   │   └── backtest_engine.py  # Backtesting engine
│   ├── 📊 data_fetcher.py      # Market data fetching
│   ├── 📋 requirements.txt     # Python dependencies
│   ├── 🧪 test_simple.py       # Live data tests
│   └── 🧪 test_mock.py         # Mock data tests
├── 🌐 frontend/                # Web interface
│   ├── 🎨 src/                 # JavaScript source
│   │   └── app.js              # Main application logic
│   └── 📄 index.html           # Main web page
├── 📊 data/                    # Data storage
├── 📝 logs/                    # Application logs
├── 🚀 start_server.py          # Quick startup script
└── 📖 README.md               # This file
```

## 🔧 API Endpoints

### Market Data
- `GET /api/popular-symbols` - Get popular stocks and ETFs
- `GET /api/stock-info/{symbol}` - Detailed stock information

### Screening
- `GET /api/screener-types` - Available screening strategies
- `POST /api/screen-stocks` - Run stock screening

### Backtesting
- `POST /api/backtest` - Run strategy backtest

### System
- `GET /api/health` - System health check

## 💡 Usage Examples

### 1. Quick Momentum Screen
```python
# Via API
POST /api/screen-stocks
{
    "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN"],
    "screener_type": "momentum"
}
```

### 2. Strategy Backtest
```python
# Via API
POST /api/backtest
{
    "symbols": ["AAPL", "MSFT", "GOOGL"],
    "strategy_type": "momentum",
    "initial_capital": 100000,
    "rebalance_frequency": "monthly"
}
```

### 3. Using the Python Components Directly
```python
# Direct Python usage
from backend.data_fetcher import DataFetcher
from backend.strategies.screeners import StockScreener, ScreenerType

# Fetch data
fetcher = DataFetcher()
data = fetcher.get_stock_data("AAPL", "1y")

# Run screening
screener = StockScreener()
results = screener.screen_stocks(stock_data, ScreenerType.MOMENTUM)
```

## 🧪 Testing

The platform includes comprehensive testing:

### Run Live Tests (requires internet)
```bash
cd backend
python test_simple.py
```

### Run Mock Tests (offline)
```bash
cd backend
python test_mock.py
```

Both test suites verify:
- ✅ Data fetching functionality
- ✅ Technical indicator calculations  
- ✅ Stock screening strategies
- ✅ Backtesting engine
- ✅ Performance metric calculations

## 🏢 Corporate Environment

For corporate networks with proxy/firewall:

1. **Package Installation**: Uses your internal artifactory
   ```bash
   pip install package_name --index-url=https://artifactory.internal.cba/api/pypi/org.python.pypi/simple
   ```

2. **Network Access**: Ensure access to:
   - `yahoo.com` (for market data)
   - `en.wikipedia.org` (for S&P 500 list)

## 🔒 Security Features

- ✅ **Defensive Purpose Only**: Designed for analysis, not malicious use
- ✅ **No Secrets Exposed**: No API keys or sensitive data in code
- ✅ **Safe Data Sources**: Only uses public market data
- ✅ **CORS Protection**: Configured for secure web access

## 🛠️ Customization

### Adding New Screening Strategies
1. Extend the `ScreenerCriteria` class in `screeners.py`
2. Add your strategy to the appropriate strategy type
3. Define criteria and scoring logic

### Adding New Backtest Strategies  
1. Create strategy function in `StrategyTemplates` class
2. Return portfolio weights for given date/data
3. Register in the API endpoints

### Extending the Web Interface
1. Add new screens to `index.html`
2. Implement JavaScript functions in `app.js`
3. Create corresponding API endpoints

## 📊 Performance Notes

- **Data Caching**: Market data is cached to reduce API calls
- **Efficient Calculations**: Vectorized operations using pandas/numpy
- **Responsive UI**: Real-time updates with loading indicators
- **Memory Management**: Automatic cleanup of old data

## 🐛 Troubleshooting

### Common Issues

**1. "No module named 'yfinance'"**
```bash
# Solution: Install dependencies manually
pip install yfinance pandas numpy --index-url=https://artifactory.internal.cba/api/pypi/org.python.pypi/simple
```

**2. "Could not resolve host: yahoo.com"**
- Network connectivity issue
- Run mock tests instead: `python test_mock.py`

**3. "Port 8000 already in use"**
```bash
# Solution: Kill existing process or use different port
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**4. Web interface not loading**
- Check if server is running: http://localhost:8000/api/health
- Try refreshing browser or clearing cache

## 🆕 Future Enhancements

- 📈 **Real-time Data**: WebSocket connections for live updates  
- 🤖 **AI Integration**: Machine learning-based screening
- 📱 **Mobile App**: Native iOS/Android applications
- 🔗 **Broker Integration**: Paper trading capabilities
- 📧 **Alerts**: Email/SMS notifications for opportunities
- 📊 **Advanced Charts**: Candlestick and technical analysis charts

## 📄 License

This project is created for educational and research purposes. Please ensure compliance with all applicable financial regulations and data usage policies.

## 🤝 Support

For issues or questions:
1. Check this README for common solutions
2. Review the API documentation at `/docs`
3. Test with mock data if network issues persist
4. Check logs for detailed error messages

---

**🎯 Happy Trading! 📈**