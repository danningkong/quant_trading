#!/usr/bin/env python3
"""
Test specific API components to isolate the 500 error
"""

import sys
import os
sys.path.insert(0, 'backend')

def test_api_components():
    print("TESTING API COMPONENTS")
    print("=" * 30)
    
    # Test 1: Import check
    print("\n1. Testing API imports...")
    try:
        from strategies.screener_backtest_integration import BacktestConfigurationHelper
        print("   [OK] BacktestConfigurationHelper imported")
    except Exception as e:
        print(f"   [ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Validate settings function
    print("\n2. Testing validate_settings...")
    try:
        test_settings = {
            "engine": "custom",
            "initial_capital": 50000,
            "max_positions": 1,
            "rebalance_frequency": "monthly"
        }
        
        validated = BacktestConfigurationHelper.validate_settings(test_settings)
        print(f"   [OK] Settings validated: {len(validated)} keys")
        print(f"   Input:  {test_settings}")
        print(f"   Output: {validated}")
        
    except Exception as e:
        print(f"   [ERROR] validate_settings failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: Import ScreenerType enum
    print("\n3. Testing ScreenerType enum...")
    try:
        from strategies.screeners import ScreenerType
        screener_type = ScreenerType('momentum')
        print(f"   [OK] ScreenerType works: {screener_type}")
    except Exception as e:
        print(f"   [ERROR] ScreenerType failed: {e}")
        return
    
    # Test 4: Full integration logic simulation
    print("\n4. Simulating full API logic...")
    try:
        from data_fetcher import DataFetcher
        from strategies.screener_backtest_integration import ScreenerBacktestIntegrator
        
        # Simulate the exact API code path
        data_fetcher = DataFetcher()
        screener_backtester = ScreenerBacktestIntegrator()
        
        # Simulate request data
        class MockRequest:
            def __init__(self):
                self.symbols = ['AAPL']
                self.screener_type = 'momentum'
                self.backtest_settings = {
                    "engine": "custom",
                    "initial_capital": 50000,
                    "max_positions": 1,
                    "rebalance_frequency": "monthly"
                }
        
        request = MockRequest()
        
        # Step 1: Validate screener type (like API does)
        screener_type = ScreenerType(request.screener_type)
        print(f"   [OK] Step 1: Screener type validated")
        
        # Step 2: Validate and clean settings (like API does)
        settings = BacktestConfigurationHelper.validate_settings(request.backtest_settings)
        print(f"   [OK] Step 2: Settings validated")
        
        # Step 3: Fetch stock data (like API does)
        stock_data = {}
        for symbol in request.symbols:
            try:
                data = data_fetcher.get_stock_data(symbol, settings.get('lookback_period', '1y'))
                if not data.empty:
                    data = data_fetcher.calculate_technical_indicators(data)
                    stock_data[symbol] = data
                    print(f"   [OK] Step 3: Data fetched for {symbol}: {len(data)} days")
            except Exception as e:
                print(f"   [ERROR] Data fetch failed for {symbol}: {e}")
                continue
        
        if not stock_data:
            print("   [ERROR] No stock data available")
            return
        
        # Step 4: Run integrated backtest (like API does)
        result = screener_backtester.run_integrated_backtest(
            symbols=request.symbols,
            screener_type=screener_type,
            stock_data=stock_data,
            backtest_settings=settings
        )
        
        if result['success']:
            print(f"   [OK] Step 4: Backtest successful!")
            backtest_results = result['backtest_results']
            print(f"   Total Return: {backtest_results.total_return:.2%}")
        else:
            print(f"   [ERROR] Step 4: Backtest failed: {result.get('error')}")
            return
        
        print("\n   [SUCCESS] Full API logic simulation works!")
        
    except Exception as e:
        print(f"   [ERROR] Full simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 30)
    print("ALL API COMPONENTS WORKING!")
    print("The 500 error might be:")
    print("1. Server import path issue")  
    print("2. FastAPI request parsing")
    print("3. Response serialization")
    print("4. Server needs complete restart")

if __name__ == "__main__":
    test_api_components()