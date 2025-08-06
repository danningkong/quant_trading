#!/usr/bin/env python3
"""
Test script for the Quant Trading project
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from data_fetcher import DataFetcher
from strategies.screeners import StockScreener, ScreenerType
from strategies.backtest_engine import BacktestEngine, StrategyTemplates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_data_fetcher():
    """Test the data fetcher functionality"""
    print("Testing Data Fetcher...")
    
    fetcher = DataFetcher()
    
    # Test single stock data fetch
    print("  Fetching AAPL data...")
    aapl_data = fetcher.get_stock_data("AAPL", "6mo")
    if not aapl_data.empty:
        print(f"  [SUCCESS] Fetched {len(aapl_data)} days of AAPL data")
        print(f"  Latest close price: ${aapl_data['Close'].iloc[-1]:.2f}")
    else:
        print("  [FAILED] Failed to fetch AAPL data")
        return False
    
    # Test technical indicators
    print("  Adding technical indicators...")
    aapl_with_indicators = fetcher.calculate_technical_indicators(aapl_data)
    indicators = ['SMA_20', 'RSI', 'MACD', 'BB_Upper', 'BB_Lower']
    missing_indicators = [ind for ind in indicators if ind not in aapl_with_indicators.columns]
    
    if not missing_indicators:
        print("  [SUCCESS] All technical indicators calculated successfully")
        print(f"  Current RSI: {aapl_with_indicators['RSI'].iloc[-1]:.2f}")
    else:
        print(f"  [FAILED] Missing indicators: {missing_indicators}")
        return False
    
    # Test multiple stocks
    print("  Fetching multiple stock data...")
    symbols = ["AAPL", "MSFT", "GOOGL"]
    multi_data = fetcher.get_multiple_stocks(symbols, "3mo")
    
    if len(multi_data) >= 2:
        print(f"  [SUCCESS] Fetched data for {len(multi_data)} stocks")
    else:
        print(f"  [FAILED] Only fetched data for {len(multi_data)} stocks")
        return False
    
    return True, multi_data

def test_stock_screener(stock_data):
    """Test the stock screening functionality"""
    print("\n🔍 Testing Stock Screener...")
    
    screener = StockScreener()
    
    # Prepare data for screener (add fundamental data)
    screener_data = {}
    for symbol, price_data in stock_data.items():
        screener_data[symbol] = {
            'price_data': price_data,
            'fundamental_data': {
                'pe_ratio': np.random.uniform(10, 30),
                'pb_ratio': np.random.uniform(1, 5),
                'market_cap': np.random.uniform(1e9, 1e12),
                'dividend_yield': np.random.uniform(0, 0.05),
                'beta': np.random.uniform(0.5, 2.0),
                'roe': np.random.uniform(0.05, 0.25)
            }
        }
    
    # Test different screening strategies
    strategies_to_test = [
        ScreenerType.MOMENTUM,
        ScreenerType.VALUE,
        ScreenerType.TECHNICAL
    ]
    
    results = {}
    for strategy_type in strategies_to_test:
        print(f"  📈 Testing {strategy_type.value} screening...")
        try:
            screen_results = screener.screen_stocks(screener_data, strategy_type)
            if not screen_results.empty:
                print(f"  ✅ {strategy_type.value} screening found {len(screen_results)} results")
                print(f"  🏆 Top pick: {screen_results.iloc[0]['symbol']} (score: {screen_results.iloc[0]['score']:.3f})")
                results[strategy_type] = screen_results
            else:
                print(f"  ⚠️  {strategy_type.value} screening returned no results")
        except Exception as e:
            print(f"  ❌ Error in {strategy_type.value} screening: {e}")
            return False
    
    return True, results

def test_backtest_engine(stock_data):
    """Test the backtesting engine"""
    print("\n📊 Testing Backtest Engine...")
    
    engine = BacktestEngine(initial_capital=100000)
    
    # Test with momentum strategy
    print("  🚀 Running momentum strategy backtest...")
    momentum_strategy = StrategyTemplates.momentum_strategy(lookback_days=20, top_n=2)
    
    try:
        # Run backtest for 3 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        results = engine.run_backtest(
            strategy_func=momentum_strategy,
            data=stock_data,
            start_date=start_date,
            end_date=end_date,
            rebalance_frequency='weekly'
        )
        
        print(f"  ✅ Backtest completed successfully!")
        print(f"  💰 Initial Capital: ${results.initial_capital:,.2f}")
        print(f"  💰 Final Capital: ${results.final_capital:,.2f}")
        print(f"  📈 Total Return: {results.total_return:.2%}")
        print(f"  📊 Annual Return: {results.annual_return:.2%}")
        print(f"  📉 Max Drawdown: {results.max_drawdown:.2%}")
        print(f"  ⚡ Sharpe Ratio: {results.sharpe_ratio:.2f}")
        print(f"  🎯 Win Rate: {results.win_rate:.2%}")
        print(f"  🔢 Number of Trades: {len(results.trades)}")
        
        return True, results
        
    except Exception as e:
        print(f"  ❌ Backtest failed: {e}")
        return False, None

def test_equal_weight_strategy(stock_data):
    """Test equal weight strategy as a simple baseline"""
    print("\n⚖️  Testing Equal Weight Strategy...")
    
    engine = BacktestEngine(initial_capital=50000)
    equal_weight_strategy = StrategyTemplates.equal_weight_strategy()
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        results = engine.run_backtest(
            strategy_func=equal_weight_strategy,
            data=stock_data,
            start_date=start_date,
            end_date=end_date,
            rebalance_frequency='monthly'
        )
        
        print(f"  ✅ Equal weight backtest completed!")
        print(f"  📈 Total Return: {results.total_return:.2%}")
        print(f"  📊 Sharpe Ratio: {results.sharpe_ratio:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Equal weight backtest failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Starting Quant Trading Project Tests\n")
    print("=" * 50)
    
    # Test 1: Data Fetcher
    try:
        success, stock_data = test_data_fetcher()
        if not success:
            print("❌ Data fetcher tests failed!")
            return
    except Exception as e:
        print(f"❌ Data fetcher test error: {e}")
        return
    
    # Test 2: Stock Screener
    try:
        success, screening_results = test_stock_screener(stock_data)
        if not success:
            print("❌ Stock screener tests failed!")
            return
    except Exception as e:
        print(f"❌ Stock screener test error: {e}")
        return
    
    # Test 3: Backtest Engine
    try:
        success, backtest_results = test_backtest_engine(stock_data)
        if not success:
            print("❌ Backtest engine tests failed!")
            return
    except Exception as e:
        print(f"❌ Backtest engine test error: {e}")
        return
    
    # Test 4: Simple Strategy
    try:
        success = test_equal_weight_strategy(stock_data)
        if not success:
            print("❌ Equal weight strategy test failed!")
            return
    except Exception as e:
        print(f"❌ Equal weight strategy test error: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! 🎉")
    print("✅ Data fetching works correctly")
    print("✅ Stock screening strategies are functional") 
    print("✅ Backtesting engine runs successfully")
    print("✅ Strategy templates work as expected")
    print("\n🚀 Your Quant Trading project is ready to use!")

if __name__ == "__main__":
    main()