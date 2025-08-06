#!/usr/bin/env python3
"""
Test both Custom and Backtrader engines now that Backtrader is installed
"""

import sys
import os
sys.path.insert(0, 'backend')

def test_both_engines():
    print("TESTING BOTH ENGINES AFTER BACKTRADER INSTALLATION")
    print("=" * 55)
    
    try:
        from strategies.backtrader_wrapper import is_backtrader_available, BacktraderEngine
        from strategies.screener_backtest_integration import ScreenerBacktestIntegrator, BacktestConfigurationHelper
        from strategies.screeners import ScreenerType
        from data_fetcher import DataFetcher
        
        print(f"\n1. Backtrader Status: {'Available' if is_backtrader_available() else 'Not Available'}")
        
        if not is_backtrader_available():
            print("   [ERROR] Backtrader still not detected!")
            return False
        
        print("   [SUCCESS] Backtrader is now available!")
        
        # Get test data
        fetcher = DataFetcher()
        integrator = ScreenerBacktestIntegrator()
        
        data = fetcher.get_stock_data('AAPL', '6mo')
        data = fetcher.calculate_technical_indicators(data)
        stock_data = {'AAPL': data}
        
        print(f"\n2. Test data: {len(data)} days of AAPL")
        
        # Test Custom Engine
        print("\n3. Testing Custom Engine...")
        custom_settings = {
            'engine': 'custom',
            'initial_capital': 50000,
            'max_positions': 1,
            'rebalance_frequency': 'monthly'
        }
        
        validated_custom = BacktestConfigurationHelper.validate_settings(custom_settings)
        
        custom_result = integrator.run_integrated_backtest(
            symbols=['AAPL'],
            screener_type=ScreenerType.MOMENTUM,
            stock_data=stock_data,
            backtest_settings=validated_custom
        )
        
        if custom_result['success']:
            bt_results = custom_result['backtest_results']
            print(f"   [SUCCESS] Custom Engine:")
            print(f"   Total Return: {bt_results.total_return:.2%}")
            print(f"   Sharpe Ratio: {bt_results.sharpe_ratio:.2f}")
        else:
            print(f"   [ERROR] Custom engine failed: {custom_result.get('error')}")
            return False
        
        # Test Backtrader Engine
        print("\n4. Testing Backtrader Engine...")
        backtrader_settings = {
            'engine': 'backtrader',
            'initial_capital': 50000,
            'max_positions': 1,
            'rebalance_frequency': 'monthly',
            'backtrader_settings': {
                'rsi_period': 14,
                'rsi_lower': 30,
                'rsi_upper': 70,
                'momentum_period': 10,
                'momentum_threshold': 0.05,
                'sma_period': 20
            }
        }
        
        validated_bt = BacktestConfigurationHelper.validate_settings(backtrader_settings)
        
        bt_result = integrator.run_integrated_backtest(
            symbols=['AAPL'],
            screener_type=ScreenerType.MOMENTUM,
            stock_data=stock_data,
            backtest_settings=validated_bt
        )
        
        if bt_result['success']:
            if bt_result.get('installation_required'):
                print("   [ERROR] Backtrader still reports installation required")
                return False
            else:
                # Get results from Backtrader format
                if hasattr(bt_result.get('backtest_results'), 'total_return'):
                    # Custom format
                    results = bt_result['backtest_results']
                    print(f"   [SUCCESS] Backtrader Engine (Custom Format):")
                    print(f"   Total Return: {results.total_return:.2%}")
                    print(f"   Sharpe Ratio: {results.sharpe_ratio:.2f}")
                else:
                    # Direct Backtrader format
                    perf = bt_result.get('performance', {})
                    print(f"   [SUCCESS] Backtrader Engine (Direct Format):")
                    print(f"   Total Return: {perf.get('total_return', 0):.2%}")
                    print(f"   Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
                    
                    # Show Backtrader-specific stats
                    bt_stats = bt_result.get('backtrader_stats', {})
                    if bt_stats:
                        print(f"   Advanced Stats:")
                        print(f"     Total Trades: {bt_stats.get('total_trades', 0)}")
                        print(f"     Win Rate: {bt_stats.get('winning_trades', 0)}/{bt_stats.get('total_trades', 0)}")
        else:
            print(f"   [ERROR] Backtrader failed: {bt_result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   [ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_both_engines():
        print("\n" + "=" * 55)
        print("SUCCESS! BOTH ENGINES WORKING!")
        print("🚀 Custom Engine: Fast pandas/numpy backtesting")
        print("⚙️  Backtrader Engine: Advanced technical indicators")
        print("=" * 55)
        print("\nNow restart your server and both engines will be available!")
        print("Users can choose between Custom (Fast) and Backtrader (Advanced)")
    else:
        print("\nSome issues still need to be resolved.")