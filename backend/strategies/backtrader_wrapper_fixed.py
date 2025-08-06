"""
Backtrader integration wrapper for the quant trading platform
Install backtrader from your internal artifactory before using this module
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Backtrader will be imported dynamically to handle missing dependency gracefully
try:
    import backtrader as bt
    BACKTRADER_AVAILABLE = True
except ImportError:
    BACKTRADER_AVAILABLE = False
    logger.warning("Backtrader not available. Install from internal artifactory: pip install backtrader")

@dataclass
class BacktraderSettings:
    """Backtrader-specific settings"""
    cash: float = 100000
    commission: float = 0.001  # 0.1%
    stake: int = 100  # Number of shares per trade
    plot: bool = False
    trade_when_true: bool = True
    trade_when_false: bool = False
    
    # Strategy-specific settings
    rsi_period: int = 14
    rsi_lower: float = 30
    rsi_upper: float = 70
    sma_period: int = 20
    momentum_period: int = 10
    momentum_threshold: float = 0.05

# Define classes only if Backtrader is available
ScreeningMomentumStrategy = None
BacktraderEngine = None

if BACKTRADER_AVAILABLE:
    class ScreeningMomentumStrategy(bt.Strategy):
        """Momentum strategy based on screening results"""
        
        params = (
            ('rsi_period', 14),
            ('rsi_lower', 30),
            ('rsi_upper', 70),
            ('momentum_period', 10),
            ('momentum_threshold', 0.05),
            ('max_positions', 5),
            ('position_size', 0.2),  # 20% per position
        )
        
        def __init__(self):
            self.indicators = {}
            self.data_names = {}
            
            for i, data in enumerate(self.datas):
                # Create indicators for each data feed
                self.indicators[data] = {
                    'rsi': bt.indicators.RSI(data.close, period=self.params.rsi_period),
                    'sma': bt.indicators.SimpleMovingAverage(data.close, period=20),
                    'momentum': bt.indicators.RateOfChange(data.close, period=self.params.momentum_period)
                }
                # Store data names for reference
                self.data_names[data] = data._name if hasattr(data, '_name') else f"DATA{i}"
        
        def next(self):
            # Get current positions
            current_positions = len([pos for pos in self.broker.positions if self.broker.positions[pos].size > 0])
            
            for data in self.datas:
                indicators = self.indicators[data]
                data_name = self.data_names[data]
                
                # Check if we have enough data
                if len(data) < max(self.params.rsi_period, self.params.momentum_period, 20):
                    continue
                    
                position = self.getposition(data)
                
                # Entry conditions: Strong momentum + not overbought
                if (not position and 
                    current_positions < self.params.max_positions and
                    indicators['momentum'][0] > self.params.momentum_threshold * 100 and  # Convert to percentage
                    indicators['rsi'][0] < self.params.rsi_upper and
                    data.close[0] > indicators['sma'][0]):
                    
                    # Calculate position size
                    target_value = self.broker.cash * self.params.position_size
                    size = int(target_value / data.close[0])
                    
                    if size > 0:
                        self.buy(data=data, size=size)
                        logger.info(f"BUY signal for {data_name}: Size={size}, Price={data.close[0]:.2f}")
                
                # Exit conditions: Weak momentum or overbought
                elif (position.size > 0 and 
                      (indicators['momentum'][0] < -self.params.momentum_threshold * 100 or
                       indicators['rsi'][0] > self.params.rsi_upper or
                       data.close[0] < indicators['sma'][0])):
                    
                    self.close(data=data)
                    logger.info(f"SELL signal for {data_name}: Price={data.close[0]:.2f}")

    class BacktraderEngine:
        """Wrapper for Backtrader backtesting engine"""
        
        def __init__(self):
            self.cerebro = None
            self.results = None
        
        def run_backtest(self, 
                        data: Dict[str, pd.DataFrame], 
                        settings: BacktraderSettings,
                        screener_type: str = 'momentum') -> Dict[str, Any]:
            """
            Run backtest using Backtrader engine
            
            Args:
                data: Dictionary of stock data DataFrames
                settings: BacktraderSettings object
                screener_type: Type of screening strategy used
                
            Returns:
                Dict containing backtest results
            """
            try:
                # Initialize Cerebro
                self.cerebro = bt.Cerebro()
                
                # Set broker settings
                self.cerebro.broker.setcash(settings.cash)
                self.cerebro.broker.setcommission(commission=settings.commission)
                
                # Add strategy with settings
                strategy_params = {
                    'rsi_period': settings.rsi_period,
                    'rsi_lower': settings.rsi_lower,
                    'rsi_upper': settings.rsi_upper,
                    'momentum_period': settings.momentum_period,
                    'momentum_threshold': settings.momentum_threshold,
                    'max_positions': min(len(data), 5),
                    'position_size': 1.0 / min(len(data), 5)  # Equal weight
                }
                
                self.cerebro.addstrategy(ScreeningMomentumStrategy, **strategy_params)
                
                # Add data feeds
                for symbol, df in data.items():
                    # Prepare data for Backtrader
                    bt_data = self._prepare_data(df, symbol)
                    if bt_data is not None:
                        self.cerebro.adddata(bt_data, name=symbol)
                
                # Add analyzers
                self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
                self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
                self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
                self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
                self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn')
                
                # Run backtest
                initial_value = self.cerebro.broker.getvalue()
                logger.info(f"Starting Backtrader backtest with ${initial_value:,.2f}")
                
                results = self.cerebro.run()
                final_value = self.cerebro.broker.getvalue()
                
                # Extract results
                strat = results[0]
                return self._format_results(strat, initial_value, final_value, screener_type, data)
                
            except Exception as e:
                logger.error(f"Backtrader backtest failed: {e}")
                return {
                    'engine': 'backtrader',
                    'success': False,
                    'error': str(e)
                }
        
        def _prepare_data(self, df: pd.DataFrame, symbol: str):
            """Convert pandas DataFrame to Backtrader data format"""
            try:
                # Ensure required columns exist
                required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                
                if not all(col in df.columns for col in required_columns):
                    logger.warning(f"Missing required columns for {symbol}. Skipping.")
                    return None
                
                # Prepare data
                data_df = df[required_columns].copy()
                data_df.index = pd.to_datetime(data_df.index)
                
                # Create Backtrader data feed
                bt_data = bt.feeds.PandasData(
                    dataname=data_df,
                    datetime=None,  # Use index
                    open='Open',
                    high='High', 
                    low='Low',
                    close='Close',
                    volume='Volume',
                    openinterest=None
                )
                
                return bt_data
                
            except Exception as e:
                logger.error(f"Error preparing data for {symbol}: {e}")
                return None
        
        def _format_results(self, strategy, initial_value: float, final_value: float, 
                           screener_type: str, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
            """Format Backtrader results to match our standard format"""
            
            try:
                # Get analyzer results
                returns_analyzer = strategy.analyzers.returns.get_analysis()
                sharpe_analyzer = strategy.analyzers.sharpe.get_analysis()
                drawdown_analyzer = strategy.analyzers.drawdown.get_analysis()
                trades_analyzer = strategy.analyzers.trades.get_analysis()
                timereturn_analyzer = strategy.analyzers.timereturn.get_analysis()
                
                # Calculate metrics
                total_return = (final_value - initial_value) / initial_value
                annual_return = returns_analyzer.get('rnorm100', 0) / 100 if returns_analyzer else 0
                
                # Get trade statistics
                trade_stats = trades_analyzer
                total_trades = trade_stats.get('total', {}).get('total', 0)
                winning_trades = trade_stats.get('won', {}).get('total', 0)
                win_rate = winning_trades / total_trades if total_trades > 0 else 0
                
                # Calculate profit factor
                gross_profit = trade_stats.get('won', {}).get('pnl', {}).get('total', 0)
                gross_loss = abs(trade_stats.get('lost', {}).get('pnl', {}).get('total', 0))
                profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
                
                # Create equity curve from time returns
                equity_curve_data = []
                if timereturn_analyzer:
                    cumulative_value = initial_value
                    for date, return_pct in timereturn_analyzer.items():
                        cumulative_value *= (1 + return_pct)
                        equity_curve_data.append({
                            "date": date.isoformat() if hasattr(date, 'isoformat') else str(date),
                            "value": float(cumulative_value)
                        })
                
                return {
                    'engine': 'backtrader',
                    'success': True,
                    'performance': {
                        'initial_capital': float(initial_value),
                        'final_capital': float(final_value),
                        'total_return': float(total_return),
                        'annual_return': float(annual_return),
                        'max_drawdown': float(drawdown_analyzer.get('max', {}).get('drawdown', 0)),
                        'sharpe_ratio': float(sharpe_analyzer.get('sharperatio', 0) or 0),
                        'sortino_ratio': 0.0,  # Backtrader doesn't have built-in Sortino
                        'win_rate': float(win_rate),
                        'profit_factor': float(profit_factor) if profit_factor != float('inf') else 0.0,
                        'number_of_trades': int(total_trades)
                    },
                    'equity_curve': equity_curve_data,
                    'trades': [],  # Would need custom trade recorder for detailed trades
                    'strategy_info': {
                        'type': 'backtrader_momentum',
                        'screener_type': screener_type,
                        'engine': 'Backtrader',
                        'symbols_used': list(data.keys())
                    },
                    'backtrader_stats': {
                        'total_trades': total_trades,
                        'winning_trades': winning_trades,
                        'losing_trades': trade_stats.get('lost', {}).get('total', 0),
                        'avg_win': trade_stats.get('won', {}).get('pnl', {}).get('average', 0),
                        'avg_loss': trade_stats.get('lost', {}).get('pnl', {}).get('average', 0),
                        'largest_win': trade_stats.get('won', {}).get('pnl', {}).get('max', 0),
                        'largest_loss': trade_stats.get('lost', {}).get('pnl', {}).get('min', 0)
                    }
                }
                
            except Exception as e:
                logger.error(f"Error formatting Backtrader results: {e}")
                return {
                    'engine': 'backtrader',
                    'success': False,
                    'error': str(e)
                }

def create_backtrader_settings_from_dict(settings_dict: Dict[str, Any]) -> BacktraderSettings:
    """Convert dictionary to BacktraderSettings object"""
    bt_settings = BacktraderSettings()
    
    # Map standard settings
    if 'initial_capital' in settings_dict:
        bt_settings.cash = settings_dict['initial_capital']
    if 'commission' in settings_dict:
        bt_settings.commission = settings_dict['commission']
    
    # Map Backtrader-specific settings
    bt_specific = settings_dict.get('backtrader_settings', {})
    
    if 'rsi_period' in bt_specific:
        bt_settings.rsi_period = bt_specific['rsi_period']
    if 'rsi_lower' in bt_specific:
        bt_settings.rsi_lower = bt_specific['rsi_lower']
    if 'rsi_upper' in bt_specific:
        bt_settings.rsi_upper = bt_specific['rsi_upper']
    if 'sma_period' in bt_specific:
        bt_settings.sma_period = bt_specific['sma_period']
    if 'momentum_period' in bt_specific:
        bt_settings.momentum_period = bt_specific['momentum_period']
    if 'momentum_threshold' in bt_specific:
        bt_settings.momentum_threshold = bt_specific['momentum_threshold']
    
    return bt_settings

# Convenience function for external use
def is_backtrader_available() -> bool:
    """Check if Backtrader is available"""
    return BACKTRADER_AVAILABLE

def get_installation_instructions() -> str:
    """Get installation instructions for Backtrader"""
    return (
        "Backtrader is not installed. Please install from your internal artifactory:\n\n"
        "pip install backtrader --index-url YOUR_INTERNAL_ARTIFACTORY_URL\n\n"
        "Or contact your IT department for the correct artifactory URL."
    )