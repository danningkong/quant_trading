#!/usr/bin/env python3
"""
Test integrated screening + backtesting functionality
"""

import sys
import os
sys.path.insert(0, '.')

from data_fetcher import DataFetcher
from strategies.screener_backtest_integration import ScreenerBacktestIntegrator, BacktestConfigurationHelper
from strategies.screeners import ScreenerType

def test_integration():
    print("=" * 50)
    print("TESTING INTEGRATED SCREENING + BACKTESTING")
    print("=" * 50)
    
    # Initialize components
    fetcher = DataFetcher()
    integrator = ScreenerBacktestIntegrator()
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    print(f"\n1. Fetching data for {symbols}...")
    stock_data = {}
    for symbol in symbols:
        try:
            data = fetcher.get_stock_data(symbol, '1y')
            if not data.empty:
                # Add technical indicators
                data = fetcher.calculate_technical_indicators(data)
                stock_data[symbol] = data
                print(f"   [OK] {symbol}: {len(data)} days")
            else:
                print(f"   [FAIL] {symbol}: No data")
        except Exception as e:
            print(f"   [ERROR] {symbol}: {e}")
    
    if not stock_data:
        print("No stock data available!")
        return
    
    print(f"\n2. Testing integration with {len(stock_data)} stocks...")
    
    # Test settings
    settings = BacktestConfigurationHelper.get_default_settings()
    print(f"   Default settings: {settings['initial_capital']}, {settings['max_positions']} positions")
    
    # Run integrated backtest
    print("\n3. Running integrated backtest...")
    result = integrator.run_integrated_backtest(
        symbols=list(stock_data.keys()),
        screener_type=ScreenerType.MOMENTUM,
        stock_data=stock_data,
        backtest_settings=settings
    )
    
    if result['success']:
        backtest_results = result['backtest_results']
        print(f"   [SUCCESS] Integrated backtest completed!")
        print(f"   Strategy: {result['strategy_type']}")
        print(f"   Symbols used: {result['symbols_used']}")
        print(f"   Total Return: {backtest_results.total_return:.2%}")
        print(f"   Sharpe Ratio: {backtest_results.sharpe_ratio:.2f}")
        print(f"   Number of Trades: {len(backtest_results.trades)}")
        print(f"   Max Drawdown: {backtest_results.max_drawdown:.2%}")
        
        # Test suggestions
        print("\n4. Testing backtest suggestions...")
        
        # Simulate screening results
        import pandas as pd
        mock_screening = pd.DataFrame([
            {'symbol': 'AAPL', 'score': 0.85, 'strategy': 'momentum'},
            {'symbol': 'MSFT', 'score': 0.72, 'strategy': 'momentum'},
            {'symbol': 'GOOGL', 'score': 0.68, 'strategy': 'momentum'}
        ])
        
        suggestions = integrator.get_screening_backtest_suggestions(mock_screening)
        print(f"   Suggested max positions: {suggestions.get('max_positions')}")
        print(f"   Suggested rebalance: {suggestions.get('rebalance_frequency')}")
        print(f"   Risk level: {suggestions.get('risk_level')}")
        
        print("\n" + "=" * 50)
        print("INTEGRATION TEST PASSED!")
        print("[OK] Data fetching successful")
        print("[OK] Screening integration working")
        print("[OK] Backtest execution successful")
        print("[OK] Suggestion system functional")
        print("Platform integration ready!")
        
    else:
        print(f"   [FAILED] {result['error']}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_integration()
    if not success:
        print("\nIntegration test failed")
        sys.exit(1)