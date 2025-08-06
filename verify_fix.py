#!/usr/bin/env python3
"""
Verify the fix works by testing the core functionality
"""

import sys
import os
sys.path.insert(0, 'backend')

def verify_fix():
    print("VERIFYING THE FIX")
    print("=" * 20)
    
    try:
        # Test the exact scenario that was causing HTTP 500
        from api.main import clean_numeric_values
        from strategies.backtest_engine import BacktestEngine
        from strategies.screener_backtest_integration import ScreenerBacktestIntegrator, BacktestConfigurationHelper
        from strategies.screeners import ScreenerType
        from data_fetcher import DataFetcher
        
        print("\n1. Testing components...")
        
        # Initialize components
        fetcher = DataFetcher()
        integrator = ScreenerBacktestIntegrator()
        
        # Get data
        data = fetcher.get_stock_data('AAPL', '6mo')
        stock_data = {'AAPL': data}
        
        # Test settings that caused the original error
        settings = {
            'engine': 'custom',
            'initial_capital': 50000,
            'max_positions': 1,
            'rebalance_frequency': 'monthly',
            'commission': 0.001,
            'slippage': 0.001
        }
        
        validated_settings = BacktestConfigurationHelper.validate_settings(settings)
        
        print("   [OK] Settings validated")
        
        # Run the backtest that was failing
        result = integrator.run_integrated_backtest(
            symbols=['AAPL'],
            screener_type=ScreenerType.MOMENTUM,
            stock_data=stock_data,
            backtest_settings=validated_settings
        )
        
        if result['success']:
            backtest_results = result['backtest_results']
            print("   [OK] Backtest successful")
            
            # Test the profit factor that was causing infinity
            profit_factor = backtest_results.profit_factor
            print(f"   Profit Factor: {profit_factor} (was causing inf error)")
            
            # Verify it's not infinity
            import math
            if math.isinf(profit_factor):
                print("   [ERROR] Profit factor is still infinity!")
                return False
            else:
                print("   [OK] Profit factor is safe for JSON")
            
            # Test the API response format
            response_data = {
                "performance": {
                    "initial_capital": float(backtest_results.initial_capital),
                    "final_capital": float(backtest_results.final_capital),
                    "total_return": float(backtest_results.total_return),
                    "annual_return": float(backtest_results.annual_return),
                    "max_drawdown": float(backtest_results.max_drawdown),
                    "sharpe_ratio": float(backtest_results.sharpe_ratio),
                    "sortino_ratio": float(backtest_results.sortino_ratio),
                    "win_rate": float(backtest_results.win_rate),
                    "profit_factor": float(backtest_results.profit_factor),
                    "number_of_trades": len(backtest_results.trades)
                }
            }
            
            # Clean the response
            cleaned_response = clean_numeric_values(response_data)
            
            # Try JSON serialization (this was failing before)
            import json
            json_str = json.dumps(cleaned_response)
            print("   [OK] JSON serialization successful!")
            
            print(f"\n2. Results:")
            print(f"   Total Return: {cleaned_response['performance']['total_return']*100:.2f}%")
            print(f"   Profit Factor: {cleaned_response['performance']['profit_factor']}")
            print(f"   Sharpe Ratio: {cleaned_response['performance']['sharpe_ratio']:.2f}")
            
            return True
            
        else:
            print(f"   [ERROR] Backtest failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Fix verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing if the HTTP 500 fix works...")
    
    if verify_fix():
        print("\n" + "=" * 50)
        print("SUCCESS! THE FIX WORKS!")
        print("The HTTP 500 error has been resolved.")
        print("The problem was infinity values in JSON serialization.")
        print("Now you just need to restart your server!")
        print("=" * 50)
        
        print("\nTo restart your server:")
        print("1. Stop current server (Ctrl+C or close terminal)")
        print("2. Run: start_server_final.bat")
        print("3. Test the web interface - it will work!")
    else:
        print("\nThe fix needs more work.")