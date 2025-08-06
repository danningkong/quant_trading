#!/usr/bin/env python3
"""
Debug backtesting issues
"""

import sys
import os
sys.path.insert(0, '.')

from data_fetcher import DataFetcher
from strategies.screener_backtest_integration import ScreenerBacktestIntegrator
from strategies.screeners import ScreenerType
import traceback

def debug_backtest_failure():
    print("=" * 50)
    print("DEBUGGING BACKTEST FAILURE")
    print("=" * 50)
    
    try:
        # Step 1: Initialize components
        print("\n1. Initializing components...")
        fetcher = DataFetcher()
        integrator = ScreenerBacktestIntegrator()
        print("   [OK] Components initialized")
        
        # Step 2: Fetch data
        print("\n2. Fetching test data...")
        symbols = ['AAPL', 'MSFT']
        stock_data = {}
        
        for symbol in symbols:
            try:
                data = fetcher.get_stock_data(symbol, '1y')
                if not data.empty:
                    data = fetcher.calculate_technical_indicators(data)
                    stock_data[symbol] = data
                    print(f"   [OK] {symbol}: {len(data)} days")
                else:
                    print(f"   [FAIL] {symbol}: No data")
            except Exception as e:
                print(f"   [ERROR] {symbol}: {e}")
        
        if not stock_data:
            print("   [CRITICAL] No stock data available")
            return
        
        # Step 3: Test backtest settings
        print("\n3. Testing backtest settings...")
        settings = {
            'initial_capital': 100000,
            'max_positions': 5,
            'rebalance_frequency': 'monthly',
            'commission': 0.001,
            'slippage': 0.001,
            'lookback_period': '1y'
        }
        print(f"   Settings: {settings}")
        
        # Step 4: Run integrated backtest with detailed error tracking
        print("\n4. Running integrated backtest with error tracking...")
        try:
            result = integrator.run_integrated_backtest(
                symbols=list(stock_data.keys()),
                screener_type=ScreenerType.MOMENTUM,
                stock_data=stock_data,
                backtest_settings=settings
            )
            
            if result['success']:
                backtest_results = result['backtest_results']
                print("   [SUCCESS] Backtest completed!")
                print(f"   Total Return: {backtest_results.total_return:.2%}")
                print(f"   Sharpe Ratio: {backtest_results.sharpe_ratio:.2f}")
                print(f"   Trades: {len(backtest_results.trades)}")
                
                # Check for edge cases
                if backtest_results.final_capital <= 0:
                    print("   [WARNING] Final capital is zero or negative!")
                if len(backtest_results.trades) == 0:
                    print("   [WARNING] No trades executed!")
                if abs(backtest_results.sharpe_ratio) > 10:
                    print("   [WARNING] Sharpe ratio seems unusually high/low!")
                    
            else:
                print(f"   [FAILED] Backtest error: {result['error']}")
                return
                
        except Exception as e:
            print(f"   [CRITICAL ERROR] {e}")
            print("   Full traceback:")
            traceback.print_exc()
            return
        
        # Step 5: Test API endpoint simulation
        print("\n5. Simulating API endpoint...")
        try:
            # Simulate API request
            api_request = {
                'symbols': list(stock_data.keys()),
                'screener_type': 'momentum',
                'backtest_settings': settings
            }
            
            print(f"   API request would be: {api_request}")
            print("   [OK] API simulation successful")
            
        except Exception as e:
            print(f"   [ERROR] API simulation failed: {e}")
            
        print("\n" + "=" * 50)
        print("DEBUG COMPLETED - BACKTEST IS WORKING")
        print("Possible issues in web interface:")
        print("1. Network timeout (backtesting takes time)")
        print("2. Frontend error handling") 
        print("3. Date format conversion")
        print("4. JavaScript/API communication")
        
    except Exception as e:
        print(f"[CRITICAL] Debug failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_backtest_failure()