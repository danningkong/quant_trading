#!/usr/bin/env python3
"""
Debug the HTTP 500 error in integrated backtesting
"""

import sys
import os
sys.path.insert(0, 'backend')

def test_import_issues():
    print("=" * 50)
    print("DEBUGGING IMPORT ISSUES")
    print("=" * 50)
    
    try:
        print("1. Testing basic imports...")
        from data_fetcher import DataFetcher
        print("   DataFetcher imported successfully")
        
        from strategies.screeners import StockScreener, ScreenerType
        print("   StockScreener imported successfully")
        
        from strategies.backtest_engine import BacktestEngine
        print("   BacktestEngine imported successfully")
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    try:
        print("\n2. Testing dual engine imports...")
        from strategies.screener_backtest_integration import ScreenerBacktestIntegrator
        print("   ✅ ScreenerBacktestIntegrator imported successfully")
        
        from strategies.backtrader_wrapper import is_backtrader_available, BacktraderEngine
        print(f"   ✅ Backtrader wrapper imported successfully")
        print(f"   ℹ️  Backtrader available: {is_backtrader_available()}")
        
    except Exception as e:
        print(f"   ❌ Dual engine import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_integration_functionality():
    print("\n3. Testing integration functionality...")
    
    try:
        from data_fetcher import DataFetcher
        from strategies.screener_backtest_integration import ScreenerBacktestIntegrator
        from strategies.screeners import ScreenerType
        
        # Initialize components
        fetcher = DataFetcher()
        integrator = ScreenerBacktestIntegrator()
        
        print("   ✅ Components initialized")
        
        # Test with minimal data
        symbols = ['AAPL']
        stock_data = {}
        
        try:
            data = fetcher.get_stock_data('AAPL', '6mo')  # Smaller dataset
            if not data.empty:
                stock_data['AAPL'] = data
                print(f"   ✅ Test data fetched: {len(data)} days")
            else:
                print("   ❌ No data fetched")
                return False
                
        except Exception as e:
            print(f"   ❌ Data fetch error: {e}")
            return False
        
        # Test custom engine
        print("\n4. Testing custom engine specifically...")
        settings = {
            'engine': 'custom',
            'initial_capital': 50000,
            'max_positions': 3,
            'rebalance_frequency': 'monthly',
            'commission': 0.001,
            'slippage': 0.001
        }
        
        try:
            result = integrator.run_integrated_backtest(
                symbols=['AAPL'],
                screener_type=ScreenerType.MOMENTUM,
                stock_data=stock_data,
                backtest_settings=settings
            )
            
            if result['success']:
                print("   ✅ Custom engine test successful")
                print(f"   📊 Result: {result['backtest_results'].total_return:.2%} return")
            else:
                print(f"   ❌ Custom engine failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Custom engine exception: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        # Test backtrader engine (should fail gracefully)
        print("\n5. Testing backtrader engine (expected to fail gracefully)...")
        settings['engine'] = 'backtrader'
        
        try:
            result = integrator.run_integrated_backtest(
                symbols=['AAPL'],
                screener_type=ScreenerType.MOMENTUM,
                stock_data=stock_data,
                backtest_settings=settings
            )
            
            if result.get('installation_required'):
                print("   ✅ Backtrader correctly reported as not installed")
            elif result['success']:
                print("   ✅ Backtrader test successful (unexpected but good!)")
            else:
                print(f"   ⚠️  Backtrader failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Backtrader engine exception: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint_locally():
    print("\n6. Testing API logic locally...")
    
    try:
        # Simulate the API request data
        request_data = {
            'symbols': ['AAPL'],
            'screener_type': 'momentum',
            'backtest_settings': {
                'engine': 'custom',
                'initial_capital': 50000,
                'max_positions': 3,
                'rebalance_frequency': 'monthly',
                'commission': 0.001,
                'slippage': 0.001
            }
        }
        
        # Import what the API uses
        from data_fetcher import DataFetcher
        from strategies.screener_backtest_integration import ScreenerBacktestIntegrator
        from strategies.screeners import ScreenerType
        
        data_fetcher = DataFetcher()
        screener_backtester = ScreenerBacktestIntegrator()
        
        # Simulate API logic
        symbols = request_data['symbols']
        screener_type = ScreenerType(request_data['screener_type'])
        backtest_settings = request_data['backtest_settings']
        
        print(f"   📝 Request: {symbols}, {screener_type}, engine={backtest_settings.get('engine')}")
        
        # Fetch data (like the API does)
        stock_data = {}
        for symbol in symbols:
            try:
                data = data_fetcher.get_stock_data(symbol, backtest_settings.get('lookback_period', '1y'))
                if not data.empty:
                    data = data_fetcher.calculate_technical_indicators(data)
                    stock_data[symbol] = data
                    print(f"   ✅ Fetched {symbol}: {len(data)} days")
                else:
                    print(f"   ⚠️  No data for {symbol}")
            except Exception as e:
                print(f"   ❌ Error fetching {symbol}: {e}")
                continue
        
        if not stock_data:
            print("   ❌ No stock data available")
            return False
            
        # Run integrated backtest (like the API does)
        result = screener_backtester.run_integrated_backtest(
            symbols=symbols,
            screener_type=screener_type,
            stock_data=stock_data,
            backtest_settings=backtest_settings
        )
        
        if result['success']:
            print("   ✅ API simulation successful!")
            backtest_results = result['backtest_results']
            print(f"   📊 Total Return: {backtest_results.total_return:.2%}")
            print(f"   📊 Sharpe Ratio: {backtest_results.sharpe_ratio:.2f}")
            return True
        else:
            print(f"   ❌ API simulation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ API simulation exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("DEBUGGING HTTP 500 ERROR")
    print("=" * 50)
    
    # Test step by step
    if not test_import_issues():
        print("\n❌ FAILED: Import issues found")
        return
    
    if not test_integration_functionality():
        print("\n❌ FAILED: Integration issues found")
        return
        
    if not test_api_endpoint_locally():
        print("\n❌ FAILED: API logic issues found")
        return
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("The backend logic appears to work correctly.")
    print("The HTTP 500 error might be:")
    print("1. Server restart needed after code changes")
    print("2. Request format issue from frontend")  
    print("3. Missing error handling in FastAPI endpoint")
    print("4. Database/file permissions issue")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Restart the server")
    print("2. Check server logs")
    print("3. Test with a simple API call")

if __name__ == "__main__":
    main()