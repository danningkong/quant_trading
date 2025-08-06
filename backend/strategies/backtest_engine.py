import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class Position:
    symbol: str
    shares: float
    entry_price: float
    entry_date: datetime
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    
    def update_price(self, price: float):
        self.current_price = price
        self.unrealized_pnl = (price - self.entry_price) * self.shares

@dataclass
class Trade:
    symbol: str
    shares: float
    entry_price: float
    exit_price: float
    entry_date: datetime
    exit_date: datetime
    pnl: float = 0.0
    pnl_pct: float = 0.0
    
    def __post_init__(self):
        self.pnl = (self.exit_price - self.entry_price) * self.shares
        self.pnl_pct = (self.exit_price - self.entry_price) / self.entry_price

@dataclass
class BacktestResults:
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    profit_factor: float
    trades: List[Trade] = field(default_factory=list)
    daily_returns: pd.Series = field(default_factory=pd.Series)
    equity_curve: pd.Series = field(default_factory=pd.Series)
    positions_history: List[Dict] = field(default_factory=list)

class BacktestEngine:
    def __init__(self, initial_capital: float = 100000, 
                 commission: float = 0.001,
                 slippage: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission  # 0.1% commission
        self.slippage = slippage     # 0.1% slippage
        self.reset()
    
    def reset(self):
        """Reset the backtesting engine"""
        self.current_capital = self.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_history: List[Tuple[datetime, float]] = []
        self.current_date = None
    
    def run_backtest(self, 
                    strategy_func: Callable,
                    data: Dict[str, pd.DataFrame],
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    rebalance_frequency: str = 'monthly') -> BacktestResults:
        """
        Run a backtest with the given strategy
        
        Args:
            strategy_func: Function that returns portfolio weights
            data: Dictionary of price data for each symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            rebalance_frequency: How often to rebalance ('daily', 'weekly', 'monthly')
        """
        self.reset()
        
        # Align all data and get date range
        aligned_data = self._align_data(data, start_date, end_date)
        if not aligned_data:
            raise ValueError("No valid data found for backtesting")
        
        dates = sorted(set().union(*[df.index for df in aligned_data.values()]))
        
        rebalance_dates = self._get_rebalance_dates(dates, rebalance_frequency)
        
        for i, date in enumerate(dates):
            self.current_date = date
            
            # Get current prices
            current_prices = {}
            for symbol, df in aligned_data.items():
                if date in df.index:
                    current_prices[symbol] = df.loc[date, 'Close']
            
            # Update position values
            self._update_positions(current_prices)
            
            # Rebalance if needed
            if date in rebalance_dates:
                try:
                    # Get historical data up to current date for strategy
                    historical_data = {}
                    for symbol, df in aligned_data.items():
                        hist_data = df[df.index <= date]
                        if not hist_data.empty:
                            historical_data[symbol] = hist_data
                    
                    # Get new portfolio weights from strategy
                    if historical_data:
                        weights = strategy_func(historical_data, date)
                        self._rebalance_portfolio(weights, current_prices)
                
                except Exception as e:
                    logger.warning(f"Strategy error on {date}: {e}")
                    continue
            
            # Record equity value
            total_value = self._calculate_total_portfolio_value(current_prices)
            self.equity_history.append((date, total_value))
        
        return self._generate_results()
    
    def _align_data(self, data: Dict[str, pd.DataFrame], 
                   start_date: Optional[datetime],
                   end_date: Optional[datetime]) -> Dict[str, pd.DataFrame]:
        """Align all data to common date range"""
        aligned_data = {}
        
        for symbol, df in data.items():
            if df.empty:
                continue
                
            # Ensure datetime index
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            # Filter by date range
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
            
            if not df.empty:
                aligned_data[symbol] = df
        
        return aligned_data
    
    def _get_rebalance_dates(self, dates: List[datetime], frequency: str) -> List[datetime]:
        """Get rebalancing dates based on frequency"""
        rebalance_dates = []
        
        if frequency == 'daily':
            return dates
        elif frequency == 'weekly':
            # Rebalance every Monday
            for date in dates:
                if date.weekday() == 0:  # Monday
                    rebalance_dates.append(date)
        elif frequency == 'monthly':
            # Rebalance on first trading day of each month
            current_month = None
            for date in dates:
                if current_month != date.month:
                    rebalance_dates.append(date)
                    current_month = date.month
        
        return rebalance_dates
    
    def _update_positions(self, current_prices: Dict[str, float]):
        """Update position values with current prices"""
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position.update_price(current_prices[symbol])
    
    def _rebalance_portfolio(self, target_weights: Dict[str, float], 
                           current_prices: Dict[str, float]):
        """Rebalance portfolio to target weights"""
        total_value = self._calculate_total_portfolio_value(current_prices)
        
        # Close positions not in target weights
        positions_to_close = []
        for symbol in self.positions:
            if symbol not in target_weights or target_weights[symbol] == 0:
                positions_to_close.append(symbol)
        
        for symbol in positions_to_close:
            self._close_position(symbol, current_prices[symbol])
        
        # Open/adjust positions based on target weights
        for symbol, weight in target_weights.items():
            if weight > 0 and symbol in current_prices:
                target_value = total_value * weight
                self._adjust_position(symbol, target_value, current_prices[symbol])
    
    def _adjust_position(self, symbol: str, target_value: float, current_price: float):
        """Adjust position to target value"""
        # Apply slippage and commission
        effective_price = current_price * (1 + self.slippage)
        target_shares = target_value / effective_price
        
        if symbol in self.positions:
            # Adjust existing position
            current_shares = self.positions[symbol].shares
            shares_diff = target_shares - current_shares
            
            if abs(shares_diff) > 0.01:  # Only trade if significant difference
                commission_cost = abs(shares_diff * effective_price * self.commission)
                self.current_capital -= commission_cost
                
                if shares_diff > 0:
                    # Buy more shares
                    additional_cost = shares_diff * effective_price
                    if self.current_capital >= additional_cost:
                        self.current_capital -= additional_cost
                        self.positions[symbol].shares = target_shares
                else:
                    # Sell shares
                    proceeds = abs(shares_diff) * effective_price
                    self.current_capital += proceeds
                    self.positions[symbol].shares = target_shares
        else:
            # Open new position
            commission_cost = target_shares * effective_price * self.commission
            total_cost = target_shares * effective_price + commission_cost
            
            if self.current_capital >= total_cost:
                self.current_capital -= total_cost
                self.positions[symbol] = Position(
                    symbol=symbol,
                    shares=target_shares,
                    entry_price=effective_price,
                    entry_date=self.current_date,
                    current_price=current_price
                )
    
    def _close_position(self, symbol: str, current_price: float):
        """Close a position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        effective_price = current_price * (1 - self.slippage)
        proceeds = position.shares * effective_price
        commission_cost = proceeds * self.commission
        
        self.current_capital += proceeds - commission_cost
        
        # Record trade
        trade = Trade(
            symbol=symbol,
            shares=position.shares,
            entry_price=position.entry_price,
            exit_price=effective_price,
            entry_date=position.entry_date,
            exit_date=self.current_date
        )
        self.trades.append(trade)
        
        del self.positions[symbol]
    
    def _calculate_total_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        positions_value = 0
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                positions_value += position.shares * current_prices[symbol]
        
        return self.current_capital + positions_value
    
    def _generate_results(self) -> BacktestResults:
        """Generate backtest results"""
        if not self.equity_history:
            raise ValueError("No equity history available")
        
        # Convert equity history to DataFrame
        equity_df = pd.DataFrame(self.equity_history, columns=['date', 'equity'])
        equity_df.set_index('date', inplace=True)
        
        # Calculate returns
        returns = equity_df['equity'].pct_change().dropna()
        
        # Performance metrics
        start_date = equity_df.index[0]
        end_date = equity_df.index[-1]
        days = (end_date - start_date).days
        years = days / 365.25
        
        total_return = (equity_df['equity'].iloc[-1] / self.initial_capital) - 1
        annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        # Risk metrics
        max_drawdown = self._calculate_max_drawdown(equity_df['equity'])
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        sortino_ratio = self._calculate_sortino_ratio(returns)
        
        # Trade metrics
        if self.trades:
            winning_trades = [t for t in self.trades if t.pnl > 0]
            win_rate = len(winning_trades) / len(self.trades)
            
            total_gains = sum(t.pnl for t in self.trades if t.pnl > 0)
            total_losses = abs(sum(t.pnl for t in self.trades if t.pnl < 0))
            profit_factor = total_gains / total_losses if total_losses > 0 else 999.99  # Use large number instead of inf
        else:
            win_rate = 0
            profit_factor = 0
        
        return BacktestResults(
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=equity_df['equity'].iloc[-1],
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            trades=self.trades,
            daily_returns=returns,
            equity_curve=equity_df['equity']
        )
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return abs(drawdown.min())
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if returns.empty or returns.std() == 0:
            return 0
        
        excess_return = returns.mean() * 252 - risk_free_rate
        return excess_return / (returns.std() * np.sqrt(252))
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        if returns.empty:
            return 0
        
        downside_returns = returns[returns < 0]
        if downside_returns.empty:
            return np.inf
        
        excess_return = returns.mean() * 252 - risk_free_rate
        downside_std = downside_returns.std() * np.sqrt(252)
        
        return excess_return / downside_std if downside_std > 0 else 0


class StrategyTemplates:
    """Pre-built strategy templates for backtesting"""
    
    @staticmethod
    def momentum_strategy(lookback_days: int = 30, top_n: int = 10):
        """Simple momentum strategy"""
        def strategy(data: Dict[str, pd.DataFrame], current_date: datetime) -> Dict[str, float]:
            weights = {}
            momentum_scores = {}
            
            for symbol, df in data.items():
                if len(df) >= lookback_days:
                    recent_return = df['Close'].iloc[-1] / df['Close'].iloc[-lookback_days] - 1
                    momentum_scores[symbol] = recent_return
            
            # Select top N momentum stocks
            top_stocks = sorted(momentum_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            weight_per_stock = 1.0 / len(top_stocks) if top_stocks else 0
            
            for symbol, _ in top_stocks:
                weights[symbol] = weight_per_stock
            
            return weights
        
        return strategy
    
    @staticmethod
    def mean_reversion_strategy(lookback_days: int = 20, z_threshold: float = 2.0):
        """Mean reversion strategy based on Z-score"""
        def strategy(data: Dict[str, pd.DataFrame], current_date: datetime) -> Dict[str, float]:
            weights = {}
            
            for symbol, df in data.items():
                if len(df) >= lookback_days:
                    prices = df['Close'].tail(lookback_days)
                    mean_price = prices.mean()
                    std_price = prices.std()
                    
                    if std_price > 0:
                        z_score = (prices.iloc[-1] - mean_price) / std_price
                        
                        # Buy if oversold (negative z-score below threshold)
                        if z_score < -z_threshold:
                            weights[symbol] = 0.1  # Small position size
            
            # Normalize weights
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v/total_weight for k, v in weights.items()}
            
            return weights
        
        return strategy
    
    @staticmethod
    def equal_weight_strategy():
        """Simple equal weight strategy"""
        def strategy(data: Dict[str, pd.DataFrame], current_date: datetime) -> Dict[str, float]:
            symbols = list(data.keys())
            if not symbols:
                return {}
            
            weight_per_stock = 1.0 / len(symbols)
            return {symbol: weight_per_stock for symbol in symbols}
        
        return strategy