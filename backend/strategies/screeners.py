import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ScreenerType(Enum):
    MOMENTUM = "momentum"
    VALUE = "value"
    GROWTH = "growth"
    QUALITY = "quality"
    TECHNICAL = "technical"
    VOLATILITY = "volatility"
    DIVIDEND = "dividend"

@dataclass
class ScreenerCriteria:
    name: str
    description: str
    criteria: Dict
    weight: float = 1.0

class StockScreener:
    def __init__(self):
        self.strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> Dict[ScreenerType, List[ScreenerCriteria]]:
        """Initialize all screening strategies"""
        return {
            ScreenerType.MOMENTUM: self._momentum_strategies(),
            ScreenerType.VALUE: self._value_strategies(),
            ScreenerType.GROWTH: self._growth_strategies(),
            ScreenerType.QUALITY: self._quality_strategies(),
            ScreenerType.TECHNICAL: self._technical_strategies(),
            ScreenerType.VOLATILITY: self._volatility_strategies(),
            ScreenerType.DIVIDEND: self._dividend_strategies()
        }
    
    def _momentum_strategies(self) -> List[ScreenerCriteria]:
        """Momentum-based screening strategies"""
        return [
            ScreenerCriteria(
                name="Price Momentum",
                description="Stocks with strong recent price momentum",
                criteria={
                    'return_1m': {'min': 0.05, 'weight': 0.3},
                    'return_3m': {'min': 0.10, 'weight': 0.4},
                    'return_6m': {'min': 0.15, 'weight': 0.3}
                }
            ),
            ScreenerCriteria(
                name="Earnings Momentum",
                description="Companies with accelerating earnings growth",
                criteria={
                    'earnings_growth_qoq': {'min': 0.10, 'weight': 0.5},
                    'earnings_surprise': {'min': 0.05, 'weight': 0.5}
                }
            ),
            ScreenerCriteria(
                name="Relative Strength",
                description="Stocks outperforming the market",
                criteria={
                    'beta': {'min': 0.8, 'max': 1.5, 'weight': 0.3},
                    'relative_strength': {'min': 1.1, 'weight': 0.7}
                }
            )
        ]
    
    def _value_strategies(self) -> List[ScreenerCriteria]:
        """Value-based screening strategies"""
        return [
            ScreenerCriteria(
                name="Classic Value",
                description="Traditional value metrics",
                criteria={
                    'pe_ratio': {'max': 15, 'weight': 0.3},
                    'pb_ratio': {'max': 2.0, 'weight': 0.3},
                    'price_to_sales': {'max': 2.0, 'weight': 0.4}
                }
            ),
            ScreenerCriteria(
                name="Deep Value",
                description="Extremely undervalued stocks",
                criteria={
                    'pe_ratio': {'max': 10, 'weight': 0.25},
                    'pb_ratio': {'max': 1.0, 'weight': 0.25},
                    'ev_ebitda': {'max': 8, 'weight': 0.25},
                    'price_to_cash_flow': {'max': 10, 'weight': 0.25}
                }
            ),
            ScreenerCriteria(
                name="Value with Quality",
                description="Undervalued stocks with good fundamentals",
                criteria={
                    'pe_ratio': {'max': 20, 'weight': 0.3},
                    'roe': {'min': 0.12, 'weight': 0.3},
                    'debt_to_equity': {'max': 0.6, 'weight': 0.2},
                    'current_ratio': {'min': 1.2, 'weight': 0.2}
                }
            )
        ]
    
    def _growth_strategies(self) -> List[ScreenerCriteria]:
        """Growth-based screening strategies"""
        return [
            ScreenerCriteria(
                name="High Growth",
                description="Companies with strong growth metrics",
                criteria={
                    'revenue_growth': {'min': 0.15, 'weight': 0.4},
                    'earnings_growth': {'min': 0.20, 'weight': 0.4},
                    'eps_growth': {'min': 0.15, 'weight': 0.2}
                }
            ),
            ScreenerCriteria(
                name="GARP (Growth at Reasonable Price)",
                description="Growth stocks at reasonable valuations",
                criteria={
                    'peg_ratio': {'max': 1.5, 'weight': 0.4},
                    'revenue_growth': {'min': 0.10, 'weight': 0.3},
                    'pe_ratio': {'max': 25, 'weight': 0.3}
                }
            ),
            ScreenerCriteria(
                name="Small Cap Growth",
                description="Small cap stocks with high growth potential",
                criteria={
                    'market_cap': {'max': 2e9, 'weight': 0.2},
                    'revenue_growth': {'min': 0.20, 'weight': 0.4},
                    'earnings_growth': {'min': 0.25, 'weight': 0.4}
                }
            )
        ]
    
    def _quality_strategies(self) -> List[ScreenerCriteria]:
        """Quality-based screening strategies"""
        return [
            ScreenerCriteria(
                name="High Quality",
                description="Companies with superior business quality",
                criteria={
                    'roe': {'min': 0.15, 'weight': 0.25},
                    'roa': {'min': 0.08, 'weight': 0.25},
                    'gross_margin': {'min': 0.4, 'weight': 0.25},
                    'debt_to_equity': {'max': 0.3, 'weight': 0.25}
                }
            ),
            ScreenerCriteria(
                name="Dividend Aristocrats",
                description="Consistent dividend growers",
                criteria={
                    'dividend_growth_5y': {'min': 0.05, 'weight': 0.4},
                    'payout_ratio': {'max': 0.6, 'weight': 0.3},
                    'dividend_yield': {'min': 0.02, 'weight': 0.3}
                }
            ),
            ScreenerCriteria(
                name="Low Debt Quality",
                description="Quality companies with minimal debt",
                criteria={
                    'debt_to_equity': {'max': 0.2, 'weight': 0.3},
                    'interest_coverage': {'min': 10, 'weight': 0.3},
                    'current_ratio': {'min': 1.5, 'weight': 0.2},
                    'roe': {'min': 0.12, 'weight': 0.2}
                }
            )
        ]
    
    def _technical_strategies(self) -> List[ScreenerCriteria]:
        """Technical analysis-based screening strategies"""
        return [
            ScreenerCriteria(
                name="Breakout Pattern",
                description="Stocks breaking out of consolidation",
                criteria={
                    'price_vs_sma_50': {'min': 1.02, 'weight': 0.3},
                    'volume_surge': {'min': 1.5, 'weight': 0.3},
                    'rsi': {'min': 50, 'max': 70, 'weight': 0.4}
                }
            ),
            ScreenerCriteria(
                name="Golden Cross",
                description="50-day MA crossing above 200-day MA",
                criteria={
                    'sma_50_vs_sma_200': {'min': 1.01, 'weight': 0.4},
                    'price_vs_sma_50': {'min': 1.0, 'weight': 0.3},
                    'volume_trend': {'min': 1.2, 'weight': 0.3}
                }
            ),
            ScreenerCriteria(
                name="Oversold Bounce",
                description="Oversold stocks showing reversal signs",
                criteria={
                    'rsi': {'max': 30, 'weight': 0.4},
                    'price_vs_bb_lower': {'min': 0.95, 'weight': 0.3},
                    'recent_bounce': {'min': 0.02, 'weight': 0.3}
                }
            )
        ]
    
    def _volatility_strategies(self) -> List[ScreenerCriteria]:
        """Volatility-based screening strategies"""
        return [
            ScreenerCriteria(
                name="Low Volatility",
                description="Stable, low-volatility stocks",
                criteria={
                    'volatility_30d': {'max': 0.15, 'weight': 0.4},
                    'beta': {'max': 0.8, 'weight': 0.3},
                    'max_drawdown': {'max': 0.1, 'weight': 0.3}
                }
            ),
            ScreenerCriteria(
                name="Volatility Breakout",
                description="Low volatility stocks with increasing activity",
                criteria={
                    'volatility_ratio': {'min': 1.5, 'weight': 0.4},
                    'volume_surge': {'min': 2.0, 'weight': 0.3},
                    'price_momentum_1w': {'min': 0.03, 'weight': 0.3}
                }
            )
        ]
    
    def _dividend_strategies(self) -> List[ScreenerCriteria]:
        """Dividend-focused screening strategies"""
        return [
            ScreenerCriteria(
                name="High Dividend Yield",
                description="Stocks with attractive dividend yields",
                criteria={
                    'dividend_yield': {'min': 0.04, 'weight': 0.4},
                    'payout_ratio': {'max': 0.8, 'weight': 0.3},
                    'dividend_stability': {'min': 0.8, 'weight': 0.3}
                }
            ),
            ScreenerCriteria(
                name="Dividend Growth",
                description="Companies consistently growing dividends",
                criteria={
                    'dividend_growth_3y': {'min': 0.08, 'weight': 0.4},
                    'earnings_growth': {'min': 0.05, 'weight': 0.3},
                    'payout_ratio': {'max': 0.6, 'weight': 0.3}
                }
            )
        ]
    
    def calculate_metrics(self, symbol: str, price_data: pd.DataFrame, 
                         fundamental_data: Dict) -> Dict:
        """Calculate all metrics needed for screening"""
        metrics = {}
        
        if not price_data.empty:
            # Price-based metrics
            returns = price_data['Close'].pct_change()
            metrics.update({
                'return_1m': returns.tail(21).sum(),
                'return_3m': returns.tail(63).sum(),
                'return_6m': returns.tail(126).sum(),
                'volatility_30d': returns.tail(30).std() * np.sqrt(252),
                'max_drawdown': self._calculate_max_drawdown(price_data['Close']),
                'beta': fundamental_data.get('beta', 1.0),
                'rsi': price_data['RSI'].iloc[-1] if 'RSI' in price_data else 50,
                'price_vs_sma_50': price_data['Close'].iloc[-1] / price_data['SMA_50'].iloc[-1] if 'SMA_50' in price_data else 1.0,
                'volume_surge': price_data['Volume'].tail(5).mean() / price_data['Volume'].tail(30).mean()
            })
        
        # Fundamental metrics
        metrics.update({
            'pe_ratio': fundamental_data.get('pe_ratio', float('inf')),
            'pb_ratio': fundamental_data.get('pb_ratio', float('inf')),
            'market_cap': fundamental_data.get('market_cap', 0),
            'dividend_yield': fundamental_data.get('dividend_yield', 0),
            'roe': fundamental_data.get('roe', 0),
            'roa': fundamental_data.get('roa', 0)
        })
        
        return metrics
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return abs(drawdown.min())
    
    def screen_stocks(self, stock_data: Dict[str, Dict], 
                     screener_type: ScreenerType,
                     strategy_name: Optional[str] = None) -> pd.DataFrame:
        """Screen stocks based on selected strategy"""
        strategies = self.strategies[screener_type]
        
        if strategy_name:
            strategies = [s for s in strategies if s.name == strategy_name]
            if not strategies:
                raise ValueError(f"Strategy '{strategy_name}' not found")
        
        results = []
        
        for symbol, data in stock_data.items():
            try:
                price_data = data.get('price_data', pd.DataFrame())
                fundamental_data = data.get('fundamental_data', {})
                
                metrics = self.calculate_metrics(symbol, price_data, fundamental_data)
                
                for strategy in strategies:
                    score = self._calculate_strategy_score(metrics, strategy)
                    if score > 0:  # Only include stocks that pass some criteria
                        results.append({
                            'symbol': symbol,
                            'strategy': strategy.name,
                            'score': score,
                            'metrics': metrics
                        })
                        
            except Exception as e:
                logger.error(f"Error screening {symbol}: {e}")
                continue
        
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values('score', ascending=False)
        
        return df
    
    def _calculate_strategy_score(self, metrics: Dict, strategy: ScreenerCriteria) -> float:
        """Calculate score for a strategy based on metrics"""
        total_score = 0.0
        total_weight = 0.0
        
        for criterion, params in strategy.criteria.items():
            if criterion not in metrics:
                continue
                
            value = metrics[criterion]
            weight = params.get('weight', 1.0)
            
            # Check if value meets criteria
            passes_min = 'min' not in params or value >= params['min']
            passes_max = 'max' not in params or value <= params['max']
            
            if passes_min and passes_max:
                # Calculate normalized score (0-1)
                if 'min' in params and 'max' in params:
                    # Value should be between min and max
                    range_size = params['max'] - params['min']
                    normalized_score = 1.0 - abs(value - (params['min'] + range_size/2)) / (range_size/2)
                elif 'min' in params:
                    # Higher is better
                    normalized_score = min(1.0, (value - params['min']) / params['min']) if params['min'] > 0 else 1.0
                else:
                    # Lower is better
                    normalized_score = min(1.0, params['max'] / value) if value > 0 else 0.0
                
                total_score += normalized_score * weight
                total_weight += weight
            
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def get_top_picks(self, stock_data: Dict, top_n: int = 20) -> Dict[ScreenerType, pd.DataFrame]:
        """Get top picks for each screening strategy type"""
        top_picks = {}
        
        for screener_type in ScreenerType:
            try:
                results = self.screen_stocks(stock_data, screener_type)
                if not results.empty:
                    top_picks[screener_type] = results.head(top_n)
                else:
                    top_picks[screener_type] = pd.DataFrame()
            except Exception as e:
                logger.error(f"Error getting top picks for {screener_type}: {e}")
                top_picks[screener_type] = pd.DataFrame()
        
        return top_picks