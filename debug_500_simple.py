#!/usr/bin/env python3
"""
Simple debug for HTTP 500 error without unicode characters
"""

import sys
import os
sys.path.insert(0, 'backend')

def test_backend_functionality():
    print("=" * 50)
    print("DEBUGGING HTTP 500 ERROR")
    print("=" * 50)
    
    print("\n1. Testing imports...")
    try:
        from data_fetcher import DataFetcher
        from strategies.screeners import ScreenerType
        from strategies.screener_backtest_integration import ScreenerBacktestIntegrator
        print("   [OK] All imports successful")
    except Exception as e:
        print(f"   [ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n2. Testing data fetching...")
    try:
        fetcher = DataFetcher()
        data = fetcher.get_stock_data('AAPL', '6mo')
        if not data.empty:
            print(f"   [OK] Fetched {len(data)} days of AAPL data")
        else:
            print("   [ERROR] No data returned")
            return
    except Exception as e:
        print(f"   [ERROR] Data fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n3. Testing backtest integration...")
    try:
        integrator = ScreenerBacktestIntegrator()
        
        # Prepare minimal test
        stock_data = {'AAPL': data}
        settings = {
            'engine': 'custom',
            'initial_capital': 50000,
            'max_positions': 2,
            'rebalance_frequency': 'monthly'
        }
        
        result = integrator.run_integrated_backtest(
            symbols=['AAPL'],
            screener_type=ScreenerType.MOMENTUM,
            stock_data=stock_data,
            backtest_settings=settings
        )
        
        if result['success']:
            print("   [OK] Backtest integration successful")
            bt_result = result['backtest_results']
            print(f"   Return: {bt_result.total_return:.2%}")
            print(f"   Sharpe: {bt_result.sharpe_ratio:.2f}")
        else:
            print(f"   [ERROR] Backtest failed: {result.get('error')}")
            return
            
    except Exception as e:
        print(f"   [ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n4. Testing API request simulation...")
    try:
        # Test the exact request structure from frontend
        request_data = {
            'symbols': ['AAPL'],
            'screener_type': 'momentum', 
            'backtest_settings': {
                'engine': 'custom',
                'initial_capital': 100000,
                'max_positions': 5,
                'rebalance_frequency': 'monthly',
                'commission': 0.001,
                'slippage': 0.001,
                'lookback_period': '1y'
            }
        }
        
        # Simulate what the API does
        screener_type = ScreenerType(request_data['screener_type'])
        print(f"   [OK] Screener type converted: {screener_type}")
        
        # Test with the settings format from frontend
        result = integrator.run_integrated_backtest(
            symbols=request_data['symbols'],
            screener_type=screener_type,
            stock_data=stock_data,
            backtest_settings=request_data['backtest_settings']
        )
        
        if result['success']:
            print("   [OK] API simulation successful!")
        else:
            print(f"   [ERROR] API simulation failed: {result.get('error')}")
            return
            
    except Exception as e:
        print(f"   [ERROR] API simulation exception: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("Backend logic is working correctly.")
    print("\nPossible causes of HTTP 500:")
    print("1. Server needs restart after code changes")
    print("2. FastAPI endpoint error handling issue")
    print("3. Request data format mismatch")
    print("4. Import path issues in live server")
    
    print("\nRECOMMENDED ACTIONS:")
    print("1. Check server logs for detailed error")
    print("2. Restart the server completely")
    print("3. Test with a minimal API request")

if __name__ == "__main__":
    test_backend_functionality()