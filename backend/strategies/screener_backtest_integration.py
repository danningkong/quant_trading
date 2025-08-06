"""
Integration module for screening + backtesting workflow
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from .screeners import StockScreener, ScreenerType
from .backtest_engine import BacktestEngine, StrategyTemplates
from .backtrader_wrapper import BacktraderEngine, BacktraderSettings, create_backtrader_settings_from_dict, is_backtrader_available

logger = logging.getLogger(__name__)

class ScreenerBacktestIntegrator:
    """Integrates stock screening with backtesting functionality"""
    
    def __init__(self):
        self.screener = StockScreener()
        
    def create_screener_based_strategy(self, 
                                     screener_type: ScreenerType,
                                     top_n: int = 10,
                                     rebalance_threshold: float = 0.1):
        """
        Create a backtesting strategy based on screening results
        
        Args:
            screener_type: Type of screening strategy to use
            top_n: Number of top stocks to select
            rebalance_threshold: Minimum score change to trigger rebalancing
        """
        def screener_strategy(data: Dict[str, pd.DataFrame], current_date: datetime) -> Dict[str, float]:
            try:
                # Prepare data for screening (add fundamental data simulation)
                screener_data = {}
                for symbol, price_data in data.items():
                    # Get data up to current date
                    historical_data = price_data[price_data.index <= current_date]
                    if len(historical_data) < 50:  # Need enough history
                        continue
                        
                    # Simulate fundamental data (in real implementation, this would be actual data)
                    fundamental_data = self._simulate_fundamental_data(symbol, historical_data)
                    
                    screener_data[symbol] = {
                        'price_data': historical_data,
                        'fundamental_data': fundamental_data
                    }
                
                if not screener_data:
                    return {}
                
                # Run screening
                results = self.screener.screen_stocks(screener_data, screener_type)
                
                if results.empty:
                    return {}
                
                # Select top N stocks
                top_stocks = results.head(top_n)
                
                # Calculate weights based on scores (higher score = higher weight)
                total_score = top_stocks['score'].sum()
                if total_score > 0:
                    weights = {}
                    for _, row in top_stocks.iterrows():
                        weights[row['symbol']] = row['score'] / total_score
                    
                    logger.info(f"Screener strategy selected {len(weights)} stocks on {current_date.date()}")
                    return weights
                else:
                    # Equal weight fallback
                    equal_weight = 1.0 / len(top_stocks)
                    return {row['symbol']: equal_weight for _, row in top_stocks.iterrows()}
                    
            except Exception as e:
                logger.error(f"Screener strategy error on {current_date}: {e}")
                return {}
        
        return screener_strategy
    
    def _simulate_fundamental_data(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """Simulate fundamental data for backtesting (replace with real data in production)"""
        np.random.seed(hash(symbol) % 2147483647)  # Consistent per symbol
        
        # Calculate some metrics from price data
        returns = price_data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        
        return {
            'pe_ratio': np.random.uniform(8, 35),
            'pb_ratio': np.random.uniform(0.5, 8),
            'market_cap': np.random.uniform(1e9, 1e12),
            'dividend_yield': np.random.uniform(0, 0.08),
            'beta': volatility * np.random.uniform(0.8, 1.2),
            'roe': np.random.uniform(0.05, 0.30),
            'roa': np.random.uniform(0.02, 0.15),
            'debt_to_equity': np.random.uniform(0, 2),
            'current_ratio': np.random.uniform(0.8, 3),
            'return_1m': returns.tail(21).sum() if len(returns) >= 21 else 0,
            'return_3m': returns.tail(63).sum() if len(returns) >= 63 else 0,
            'return_6m': returns.tail(126).sum() if len(returns) >= 126 else 0,
            'volatility_30d': returns.tail(30).std() * np.sqrt(252) if len(returns) >= 30 else volatility,
            'rsi': 50 + np.random.normal(0, 15),  # Simulate RSI around 50
            'volume_surge': np.random.uniform(0.5, 3.0)
        }
    
    def run_integrated_backtest(self,
                              symbols: List[str],
                              screener_type: ScreenerType,
                              stock_data: Dict[str, pd.DataFrame],
                              backtest_settings: Dict) -> Dict:
        """
        Run a backtest using screener-based strategy with engine selection
        
        Args:
            symbols: List of symbols to consider
            screener_type: Type of screening strategy
            stock_data: Historical price data
            backtest_settings: Backtest configuration (including engine choice)
        """
        try:
            # Filter data to only include requested symbols
            filtered_data = {symbol: data for symbol, data in stock_data.items() 
                           if symbol in symbols}
            
            if not filtered_data:
                raise ValueError("No valid data for provided symbols")
            
            # Get engine choice (default to 'custom')
            engine_type = backtest_settings.get('engine', 'custom')
            
            # Route to appropriate engine
            if engine_type == 'backtrader':
                return self._run_backtrader_backtest(symbols, screener_type, filtered_data, backtest_settings)
            else:
                return self._run_custom_backtest(symbols, screener_type, filtered_data, backtest_settings)
                
        except Exception as e:
            logger.error(f"Integrated backtest failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'engine': backtest_settings.get('engine', 'custom')
            }
    
    def _run_custom_backtest(self, symbols: List[str], screener_type: ScreenerType, 
                           filtered_data: Dict[str, pd.DataFrame], backtest_settings: Dict) -> Dict:
        """Run backtest using custom engine"""
        try:
            # Create screener-based strategy
            strategy_func = self.create_screener_based_strategy(
                screener_type=screener_type,
                top_n=backtest_settings.get('max_positions', 10),
                rebalance_threshold=backtest_settings.get('rebalance_threshold', 0.1)
            )
            
            # Initialize backtest engine
            engine = BacktestEngine(
                initial_capital=backtest_settings.get('initial_capital', 100000),
                commission=backtest_settings.get('commission', 0.001),
                slippage=backtest_settings.get('slippage', 0.001)
            )
            
            # Set date range
            start_date = backtest_settings.get('start_date')
            end_date = backtest_settings.get('end_date')
            
            if not start_date:
                # Default to 1 year ago
                end_date_obj = datetime.now() if not end_date else end_date
                start_date = end_date_obj - timedelta(days=365)
            
            # Run backtest
            results = engine.run_backtest(
                strategy_func=strategy_func,
                data=filtered_data,
                start_date=start_date,
                end_date=end_date,
                rebalance_frequency=backtest_settings.get('rebalance_frequency', 'monthly')
            )
            
            return {
                'success': True,
                'backtest_results': results,
                'strategy_type': f"screener_{screener_type.value}",
                'symbols_used': list(filtered_data.keys()),
                'settings_used': backtest_settings,
                'engine': 'custom'
            }
            
        except Exception as e:
            logger.error(f"Custom backtest failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'strategy_type': f"screener_{screener_type.value}",
                'symbols_used': symbols,
                'engine': 'custom'
            }
    
    def _run_backtrader_backtest(self, symbols: List[str], screener_type: ScreenerType, 
                               filtered_data: Dict[str, pd.DataFrame], backtest_settings: Dict) -> Dict:
        """Run backtest using Backtrader engine"""
        try:
            if not is_backtrader_available():
                return {
                    'success': False,
                    'error': 'Backtrader not installed. Please install from your internal artifactory.',
                    'engine': 'backtrader',
                    'installation_required': True
                }
            
            # Create Backtrader settings
            bt_settings = create_backtrader_settings_from_dict(backtest_settings)
            
            # Initialize Backtrader engine  
            bt_engine = BacktraderEngine()
            
            # Run backtest
            result = bt_engine.run_backtest(
                data=filtered_data,
                settings=bt_settings,
                screener_type=screener_type.value
            )
            
            # Add our standard metadata
            if result.get('success', True):
                result.update({
                    'success': True,
                    'strategy_type': f"backtrader_screener_{screener_type.value}",
                    'symbols_used': symbols,
                    'settings_used': backtest_settings,
                    'backtest_results': self._convert_backtrader_to_standard_format(result)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Backtrader backtest failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'strategy_type': f"backtrader_screener_{screener_type.value}",
                'symbols_used': symbols,
                'engine': 'backtrader'
            }
    
    def _convert_backtrader_to_standard_format(self, bt_result: Dict) -> object:
        """Convert Backtrader result to our standard BacktestResults-like object"""
        from types import SimpleNamespace
        from datetime import datetime
        
        # Create a simple object that mimics our BacktestResults structure
        perf = bt_result.get('performance', {})
        
        result = SimpleNamespace()
        result.start_date = datetime.now() - timedelta(days=365)  # Default
        result.end_date = datetime.now()
        result.initial_capital = perf.get('initial_capital', 100000)
        result.final_capital = perf.get('final_capital', 100000)
        result.total_return = perf.get('total_return', 0)
        result.annual_return = perf.get('annual_return', 0)
        result.max_drawdown = perf.get('max_drawdown', 0)
        result.sharpe_ratio = perf.get('sharpe_ratio', 0)
        result.sortino_ratio = perf.get('sortino_ratio', 0)
        result.win_rate = perf.get('win_rate', 0)
        result.profit_factor = perf.get('profit_factor', 0)
        result.trades = []  # Backtrader trades would need separate handling
        result.equity_curve = SimpleNamespace()
        result.equity_curve.index = []
        result.equity_curve.values = []
        
        return result
    
    def get_screening_backtest_suggestions(self, screening_results: pd.DataFrame) -> Dict:
        """
        Provide backtest parameter suggestions based on screening results
        """
        if screening_results.empty:
            return {}
        
        # Analyze screening results
        num_results = len(screening_results)
        avg_score = screening_results['score'].mean()
        top_score = screening_results['score'].max()
        
        # Generate suggestions
        suggestions = {
            'max_positions': min(max(5, num_results // 2), 15),  # 5-15 positions
            'rebalance_frequency': 'monthly' if num_results > 10 else 'weekly',
            'initial_capital': 100000,
            'commission': 0.001,
            'slippage': 0.001,
            'lookback_period': '1y' if avg_score > 0.5 else '2y',
            'risk_level': 'moderate' if top_score < 0.8 else 'aggressive',
            'recommended_symbols': screening_results.head(10)['symbol'].tolist()
        }
        
        return suggestions

class BacktestConfigurationHelper:
    """Helper class for generating backtest configurations"""
    
    @staticmethod
    def get_default_settings() -> Dict:
        """Get default backtest settings"""
        return {
            'initial_capital': 100000,
            'max_positions': 10,
            'rebalance_frequency': 'monthly',
            'commission': 0.001,  # 0.1%
            'slippage': 0.001,    # 0.1%
            'rebalance_threshold': 0.1,  # 10% score change
            'lookback_period': '1y',
            'risk_management': {
                'max_position_size': 0.2,  # 20% max per stock
                'stop_loss': None,         # No stop loss by default
                'take_profit': None        # No take profit by default
            }
        }
    
    @staticmethod
    def validate_settings(settings: Dict) -> Dict:
        """Validate and clean backtest settings"""
        defaults = BacktestConfigurationHelper.get_default_settings()
        
        # Merge with defaults
        validated = {**defaults, **settings}
        
        # Validate ranges
        validated['initial_capital'] = max(1000, validated['initial_capital'])
        validated['max_positions'] = max(1, min(50, validated['max_positions']))
        validated['commission'] = max(0, min(0.01, validated['commission']))
        validated['slippage'] = max(0, min(0.01, validated['slippage']))
        
        return validated