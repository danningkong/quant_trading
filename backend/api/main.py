from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_fetcher import DataFetcher
from strategies.screeners import StockScreener, ScreenerType
from strategies.backtest_engine import BacktestEngine, StrategyTemplates
from strategies.screener_backtest_integration import ScreenerBacktestIntegrator, BacktestConfigurationHelper
from strategies.backtrader_wrapper import is_backtrader_available, get_installation_instructions
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import json
import logging
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def clean_numeric_values(obj: Any) -> Any:
    """Clean numeric values to avoid JSON serialization issues"""
    if isinstance(obj, dict):
        return {k: clean_numeric_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_numeric_values(v) for v in obj]
    elif isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0 if math.isnan(obj) else 999.99  # Replace inf/nan with safe values
        return float(obj)
    elif isinstance(obj, (int, np.integer)):
        return int(obj)
    else:
        return obj

app = FastAPI(title="Quant Trading API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
else:
    print(f"Warning: Frontend directory not found at {frontend_path}")

# Initialize components
data_fetcher = DataFetcher()
stock_screener = StockScreener()
screener_backtester = ScreenerBacktestIntegrator()

# Simple logging solution to avoid conflicts
from collections import deque
from datetime import datetime as dt
import threading

# Simple in-memory log storage
_log_storage = deque(maxlen=500)  # Keep last 500 log entries
_log_lock = threading.Lock()

def add_api_log(level: str, message: str):
    """Add a log entry to our simple storage"""
    with _log_lock:
        _log_storage.append({
            'timestamp': dt.now().isoformat(),
            'level': level,
            'logger': 'api',
            'message': message
        })

def get_api_logs(limit: int = 100):
    """Get recent API logs"""
    with _log_lock:
        logs = list(_log_storage)[-limit:]
        return logs

# Add initial log
add_api_log('INFO', 'API logging system initialized')

# Pydantic models for API
class ScreeningRequest(BaseModel):
    symbols: List[str]
    screener_type: str
    strategy_name: Optional[str] = None

class BacktestRequest(BaseModel):
    symbols: List[str]
    strategy_type: str
    initial_capital: float = 100000
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    rebalance_frequency: str = "monthly"

class ScreeningResult(BaseModel):
    symbol: str
    strategy: str
    score: float
    metrics: Dict

class BacktestResult(BaseModel):
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    number_of_trades: int

class IntegratedBacktestRequest(BaseModel):
    symbols: List[str]
    screener_type: str
    backtest_settings: Dict

@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    if os.path.exists(frontend_path):
        return FileResponse(os.path.join(frontend_path, "index.html"))
    else:
        return {"message": "Quant Trading API", "status": "running", "docs": "/docs"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/screener-types")
async def get_screener_types():
    """Get available screener types"""
    try:
        screener_info = {}
        for screener_type in ScreenerType:
            strategies = stock_screener.strategies[screener_type]
            screener_info[screener_type.value] = {
                "name": screener_type.value.title(),
                "strategies": [
                    {
                        "name": strategy.name,
                        "description": strategy.description
                    }
                    for strategy in strategies
                ]
            }
        return screener_info
    except Exception as e:
        logger.error(f"Error getting screener types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/popular-symbols")
async def get_popular_symbols():
    """Get popular stock and ETF symbols"""
    try:
        stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "JPM", "V"]
        etfs = data_fetcher.get_popular_etfs()[:10]  # Top 10 ETFs
        
        return {
            "stocks": stocks,
            "etfs": etfs,
            "combined": stocks + etfs
        }
    except Exception as e:
        logger.error(f"Error getting popular symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/screen-stocks")
async def screen_stocks(request: ScreeningRequest):
    """Screen stocks based on selected criteria"""
    try:
        add_api_log('INFO', f'Starting stock screening for {len(request.symbols)} symbols with {request.screener_type} strategy')
        # Validate screener type
        try:
            screener_type = ScreenerType(request.screener_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid screener type: {request.screener_type}")
        
        # Fetch stock data
        logger.info(f"Fetching data for symbols: {request.symbols}")
        stock_data_dict = {}
        
        for symbol in request.symbols:
            try:
                price_data = data_fetcher.get_stock_data(symbol, "1y")
                if not price_data.empty:
                    price_data = data_fetcher.calculate_technical_indicators(price_data)
                    fundamental_data = data_fetcher.get_stock_info(symbol)
                    
                    stock_data_dict[symbol] = {
                        'price_data': price_data,
                        'fundamental_data': fundamental_data
                    }
                else:
                    logger.warning(f"No data found for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                continue
        
        if not stock_data_dict:
            raise HTTPException(status_code=404, detail="No valid stock data found")
        
        # Run screening
        results = stock_screener.screen_stocks(
            stock_data_dict,
            screener_type,
            request.strategy_name
        )
        
        if results.empty:
            return {"results": [], "message": "No stocks passed the screening criteria"}
        
        # Convert results to JSON-serializable format
        screening_results = []
        for _, row in results.head(20).iterrows():  # Top 20 results
            screening_results.append({
                "symbol": row['symbol'],
                "strategy": row['strategy'],
                "score": float(row['score']),
                "metrics": {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                          for k, v in row['metrics'].items()}
            })
        
        response_data = {
            "results": screening_results,
            "total_screened": len(stock_data_dict),
            "total_results": len(results)
        }
        
        add_api_log('INFO', f'Stock screening completed: {len(results)} results from {len(stock_data_dict)} stocks')
        
        # Clean numeric values to prevent JSON serialization errors
        return clean_numeric_values(response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stock screening: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    """Run backtest on selected strategy"""
    try:
        # Fetch stock data
        logger.info(f"Running backtest for symbols: {request.symbols}")
        stock_data = {}
        
        for symbol in request.symbols:
            try:
                data = data_fetcher.get_stock_data(symbol, "2y")  # 2 years for backtest
                if not data.empty:
                    stock_data[symbol] = data
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                continue
        
        if not stock_data:
            raise HTTPException(status_code=404, detail="No valid stock data found for backtesting")
        
        # Initialize backtest engine
        engine = BacktestEngine(initial_capital=request.initial_capital)
        
        # Get strategy function
        if request.strategy_type == "momentum":
            strategy_func = StrategyTemplates.momentum_strategy(lookback_days=30, top_n=min(3, len(stock_data)))
        elif request.strategy_type == "equal_weight":
            strategy_func = StrategyTemplates.equal_weight_strategy()
        elif request.strategy_type == "mean_reversion":
            strategy_func = StrategyTemplates.mean_reversion_strategy(lookback_days=20)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid strategy type: {request.strategy_type}")
        
        # Set date range
        if request.start_date:
            start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        else:
            start_date = datetime.now() - timedelta(days=365)  # 1 year ago
            
        if request.end_date:
            end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
        else:
            end_date = datetime.now()
        
        # Run backtest
        results = engine.run_backtest(
            strategy_func=strategy_func,
            data=stock_data,
            start_date=start_date,
            end_date=end_date,
            rebalance_frequency=request.rebalance_frequency
        )
        
        # Prepare equity curve data for charting
        equity_curve_data = []
        for date, value in zip(results.equity_curve.index, results.equity_curve.values):
            equity_curve_data.append({
                "date": date.isoformat(),
                "value": float(value)
            })
        
        # Prepare trade data
        trade_data = []
        for trade in results.trades:
            trade_data.append({
                "symbol": trade.symbol,
                "shares": float(trade.shares),
                "entry_price": float(trade.entry_price),
                "exit_price": float(trade.exit_price),
                "entry_date": trade.entry_date.isoformat(),
                "exit_date": trade.exit_date.isoformat(),
                "pnl": float(trade.pnl),
                "pnl_pct": float(trade.pnl_pct)
            })
        
        return {
            "performance": {
                "initial_capital": float(results.initial_capital),
                "final_capital": float(results.final_capital),
                "total_return": float(results.total_return),
                "annual_return": float(results.annual_return),
                "max_drawdown": float(results.max_drawdown),
                "sharpe_ratio": float(results.sharpe_ratio),
                "sortino_ratio": float(results.sortino_ratio),
                "win_rate": float(results.win_rate),
                "profit_factor": float(results.profit_factor),
                "number_of_trades": len(results.trades)
            },
            "equity_curve": equity_curve_data,
            "trades": trade_data,
            "period": {
                "start_date": results.start_date.isoformat(),
                "end_date": results.end_date.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in backtesting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock-info/{symbol}")
async def get_stock_info(symbol: str):
    """Get detailed information about a specific stock"""
    try:
        # Get price data
        price_data = data_fetcher.get_stock_data(symbol, "1y")
        if price_data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Add technical indicators
        price_data = data_fetcher.calculate_technical_indicators(price_data)
        
        # Get fundamental data
        fundamental_data = data_fetcher.get_stock_info(symbol)
        
        # Calculate recent performance
        current_price = float(price_data['Close'].iloc[-1])
        price_1m_ago = float(price_data['Close'].iloc[-21]) if len(price_data) >= 21 else current_price
        price_3m_ago = float(price_data['Close'].iloc[-63]) if len(price_data) >= 63 else current_price
        
        return_1m = (current_price - price_1m_ago) / price_1m_ago
        return_3m = (current_price - price_3m_ago) / price_3m_ago
        
        # Recent price data for mini chart
        recent_prices = []
        for date, price in zip(price_data.index[-30:], price_data['Close'].tail(30)):
            recent_prices.append({
                "date": date.isoformat(),
                "price": float(price)
            })
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "performance": {
                "return_1m": float(return_1m),
                "return_3m": float(return_3m)
            },
            "fundamental": fundamental_data,
            "technical": {
                "rsi": float(price_data['RSI'].iloc[-1]) if 'RSI' in price_data else None,
                "sma_20": float(price_data['SMA_20'].iloc[-1]) if 'SMA_20' in price_data else None,
                "sma_50": float(price_data['SMA_50'].iloc[-1]) if 'SMA_50' in price_data else None,
            },
            "recent_prices": recent_prices
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stock info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get-backtest-suggestions")
async def get_backtest_suggestions(screening_results: Dict):
    """Get backtest parameter suggestions based on screening results"""
    try:
        # Convert dict back to DataFrame
        if not screening_results.get('results'):
            return {"suggestions": BacktestConfigurationHelper.get_default_settings()}
        
        results_df = pd.DataFrame(screening_results['results'])
        suggestions = screener_backtester.get_screening_backtest_suggestions(results_df)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error getting backtest suggestions: {e}")
        return {"suggestions": BacktestConfigurationHelper.get_default_settings()}

@app.post("/api/run-integrated-backtest")
async def run_integrated_backtest(request: IntegratedBacktestRequest):
    """Run backtest using screening results"""
    try:
        # Validate screener type
        try:
            screener_type = ScreenerType(request.screener_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid screener type: {request.screener_type}")
        
        # Validate and clean settings
        settings = BacktestConfigurationHelper.validate_settings(request.backtest_settings)
        
        # Fetch stock data
        logger.info(f"Running integrated backtest for symbols: {request.symbols}")
        stock_data = {}
        
        for symbol in request.symbols:
            try:
                data = data_fetcher.get_stock_data(symbol, settings.get('lookback_period', '2y'))
                if not data.empty:
                    # Add technical indicators
                    data = data_fetcher.calculate_technical_indicators(data)
                    stock_data[symbol] = data
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                continue
        
        if not stock_data:
            raise HTTPException(status_code=404, detail="No valid stock data found")
        
        # Set date range
        if 'start_date' in settings and isinstance(settings['start_date'], str):
            settings['start_date'] = datetime.fromisoformat(settings['start_date'].replace('Z', '+00:00'))
        if 'end_date' in settings and isinstance(settings['end_date'], str):
            settings['end_date'] = datetime.fromisoformat(settings['end_date'].replace('Z', '+00:00'))
        
        # Run integrated backtest
        result = screener_backtester.run_integrated_backtest(
            symbols=request.symbols,
            screener_type=screener_type,
            stock_data=stock_data,
            backtest_settings=settings
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        # Format results similar to regular backtest
        backtest_results = result['backtest_results']
        
        # Prepare equity curve data
        equity_curve_data = []
        for date, value in zip(backtest_results.equity_curve.index, backtest_results.equity_curve.values):
            equity_curve_data.append({
                "date": date.isoformat(),
                "value": float(value)
            })
        
        # Prepare trade data
        trade_data = []
        for trade in backtest_results.trades:
            trade_data.append({
                "symbol": trade.symbol,
                "shares": float(trade.shares),
                "entry_price": float(trade.entry_price),
                "exit_price": float(trade.exit_price),
                "entry_date": trade.entry_date.isoformat(),
                "exit_date": trade.exit_date.isoformat(),
                "pnl": float(trade.pnl),
                "pnl_pct": float(trade.pnl_pct)
            })
        
        response_data = {
            "performance": {
                "initial_capital": float(backtest_results.initial_capital),
                "final_capital": float(backtest_results.final_capital),
                "total_return": float(backtest_results.total_return),
                "annual_return": float(backtest_results.annual_return),
                "max_drawdown": float(backtest_results.max_drawdown),
                "sharpe_ratio": float(backtest_results.sharpe_ratio),
                "sortino_ratio": float(backtest_results.sortino_ratio),
                "win_rate": float(backtest_results.win_rate),
                "profit_factor": float(backtest_results.profit_factor),
                "number_of_trades": len(backtest_results.trades)
            },
            "equity_curve": equity_curve_data,
            "trades": trade_data,
            "strategy_info": {
                "type": result['strategy_type'],
                "screener_type": request.screener_type,
                "symbols_used": result['symbols_used'],
                "settings": settings
            },
            "period": {
                "start_date": backtest_results.start_date.isoformat(),
                "end_date": backtest_results.end_date.isoformat()
            }
        }
        
        # Clean numeric values to prevent JSON serialization errors
        return clean_numeric_values(response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in integrated backtesting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest-presets")
async def get_backtest_presets():
    """Get predefined backtest configuration presets"""
    return {
        "conservative": {
            "initial_capital": 50000,
            "max_positions": 5,
            "rebalance_frequency": "monthly",
            "commission": 0.001,
            "slippage": 0.001,
            "risk_level": "low"
        },
        "moderate": {
            "initial_capital": 100000,
            "max_positions": 10,
            "rebalance_frequency": "monthly", 
            "commission": 0.001,
            "slippage": 0.001,
            "risk_level": "moderate"
        },
        "aggressive": {
            "initial_capital": 200000,
            "max_positions": 15,
            "rebalance_frequency": "weekly",
            "commission": 0.0005,
            "slippage": 0.0005,
            "risk_level": "high"
        }
    }

@app.get("/api/engine-status")
async def get_engine_status():
    """Get status of available backtesting engines"""
    return {
        "engines": {
            "custom": {
                "available": True,
                "name": "Custom Engine",
                "description": "Fast pandas/numpy based backtesting",
                "features": ["Basic order management", "Performance metrics", "Fast execution"]
            },
            "backtrader": {
                "available": is_backtrader_available(),
                "name": "Backtrader",
                "description": "Advanced backtesting with sophisticated indicators",
                "features": ["Technical indicators", "Advanced order types", "Risk management"],
                "installation_required": not is_backtrader_available(),
                "installation_instructions": get_installation_instructions() if not is_backtrader_available() else None
            }
        },
        "default_engine": "custom"
    }

@app.get("/api/test-logs")
async def test_logs():
    """Test endpoint for log functionality"""
    return {
        "log_manager_available": LOG_MANAGER_AVAILABLE,
        "message": "Log functionality test endpoint"
    }

@app.get("/api/logs")
async def get_logs(limit: int = 100, level: str = None):
    """Get recent log entries"""
    try:
        logs = get_api_logs(limit)
        
        # Filter by level if specified
        if level:
            logs = [log for log in logs if log['level'] == level or 
                   (level == 'WARNING' and log['level'] in ['WARNING', 'ERROR']) or
                   (level == 'INFO' and log['level'] in ['INFO', 'WARNING', 'ERROR'])]
        
        return {
            "logs": logs,
            "total": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/stats")
async def get_log_stats():
    """Get log statistics"""
    try:
        logs = get_api_logs(500)  # Get all logs for stats
        
        level_counts = {}
        for log in logs:
            level = log['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        recent_errors = [log for log in logs if log['level'] in ['ERROR', 'CRITICAL']]
        
        return {
            'total_logs': len(logs),
            'level_counts': level_counts,
            'recent_errors': recent_errors[-10:],  # Last 10 errors
            'last_update': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting log stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/stream")
async def stream_logs():
    """Stream logs in real-time using Server-Sent Events (simplified)"""
    async def simple_log_stream():
        # For now, just send periodic updates with current logs
        import asyncio
        last_count = 0
        
        while True:
            try:
                current_logs = get_api_logs(10)  # Get last 10 logs
                if len(current_logs) > last_count:
                    # Send new logs
                    for log in current_logs[last_count:]:
                        yield f"data: {json.dumps(log)}\n\n"
                    last_count = len(current_logs)
                else:
                    # Send keepalive
                    yield f"data: {json.dumps({'type': 'keepalive', 'timestamp': datetime.now().isoformat()})}\n\n"
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in log stream: {e}")
                break
    
    return StreamingResponse(
        simple_log_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)