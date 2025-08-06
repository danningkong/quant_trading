#!/usr/bin/env python3
"""
Test the dual engine functionality (Custom + Backtrader)
"""

import requests
import json

def test_dual_engine_functionality():
    base_url = "http://127.0.0.1:8001"
    
    print("=" * 60)
    print("TESTING DUAL ENGINE FUNCTIONALITY")
    print("=" * 60)
    
    # Test 1: Check engine status
    print("\n1. Testing Engine Status...")
    try:
        response = requests.get(f"{base_url}/api/engine-status", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Available Engines:")
            for engine, info in data['engines'].items():
                status = "✅ Available" if info['available'] else "❌ Not Available"
                print(f"     - {info['name']} ({engine}): {status}")
                if not info['available'] and info.get('installation_required'):
                    print(f"       Installation needed: {info.get('installation_instructions', 'N/A')}")
        else:
            print("   [FAIL] Engine status check failed")
            return
    except Exception as e:
        print(f"   [ERROR] {e}")
        return
    
    # Test 2: Run screening first
    print("\n2. Running Stock Screening...")
    try:
        screening_data = {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "screener_type": "momentum"
        }
        response = requests.post(
            f"{base_url}/api/screen-stocks", 
            json=screening_data,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            screening_results = response.json()
            symbols = [r['symbol'] for r in screening_results['results'][:2]]
            print(f"   [OK] Screened stocks: {symbols}")
        else:
            print("   [FAIL] Screening failed")
            return
    except Exception as e:
        print(f"   [ERROR] {e}")
        return
    
    # Test 3: Test Custom Engine
    print("\n3. Testing Custom Engine...")
    try:
        custom_backtest_data = {
            "symbols": symbols,
            "screener_type": "momentum",
            "backtest_settings": {
                "engine": "custom",
                "initial_capital": 100000,
                "max_positions": 5,
                "rebalance_frequency": "monthly",
                "commission": 0.001,
                "slippage": 0.001
            }
        }
        
        response = requests.post(
            f"{base_url}/api/run-integrated-backtest",
            json=custom_backtest_data,
            timeout=60
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            perf = result.get('performance', {})
            engine_used = result.get('strategy_info', {}).get('engine', 'unknown')
            print(f"   [OK] Custom Engine Results:")
            print(f"       Engine: {engine_used}")
            print(f"       Total Return: {perf.get('total_return', 0)*100:.2f}%")
            print(f"       Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
            print(f"       Trades: {perf.get('number_of_trades', 0)}")
        else:
            print(f"   [WARN] Custom engine returned {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   [ERROR] Custom engine test: {e}")
    
    # Test 4: Test Backtrader Engine
    print("\n4. Testing Backtrader Engine...")
    try:
        backtrader_backtest_data = {
            "symbols": symbols,
            "screener_type": "momentum",
            "backtest_settings": {
                "engine": "backtrader",
                "initial_capital": 100000,
                "max_positions": 5,
                "rebalance_frequency": "monthly",
                "commission": 0.001,
                "slippage": 0.001,
                "backtrader_settings": {
                    "rsi_period": 14,
                    "rsi_lower": 30,
                    "rsi_upper": 70,
                    "momentum_period": 10,
                    "momentum_threshold": 0.05,
                    "sma_period": 20
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/api/run-integrated-backtest",
            json=backtrader_backtest_data,
            timeout=60
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            
            if result.get('installation_required'):
                print(f"   [INFO] Backtrader not installed - this is expected")
                print(f"   [INFO] Installation message: {result.get('error', 'N/A')}")
            else:
                perf = result.get('performance', {})
                engine_used = result.get('strategy_info', {}).get('engine', 'unknown')
                print(f"   [OK] Backtrader Engine Results:")
                print(f"       Engine: {engine_used}")
                print(f"       Total Return: {perf.get('total_return', 0)*100:.2f}%")
                print(f"       Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
                print(f"       Trades: {perf.get('number_of_trades', 0)}")
                
                # Show Backtrader-specific stats if available
                bt_stats = result.get('backtrader_stats', {})
                if bt_stats:
                    print(f"       Backtrader Stats:")
                    print(f"         Winning Trades: {bt_stats.get('winning_trades', 0)}")
                    print(f"         Losing Trades: {bt_stats.get('losing_trades', 0)}")
                    print(f"         Avg Win: ${bt_stats.get('avg_win', 0):.2f}")
                    print(f"         Avg Loss: ${bt_stats.get('avg_loss', 0):.2f}")
        else:
            print(f"   [WARN] Backtrader engine returned {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   [ERROR] Backtrader engine test: {e}")
    
    print("\n" + "=" * 60)
    print("DUAL ENGINE TEST COMPLETED!")
    print("=" * 60)
    
    print(f"\n📋 SUMMARY:")
    print(f"✅ Custom Engine: Always available (pandas/numpy)")
    print(f"⚙️  Backtrader Engine: Advanced features (requires installation)")
    print(f"🔄 Stock Selection: Users can pick which stocks to backtest")
    print(f"⚡ Engine Choice: Users can switch between engines in the UI")
    
    print(f"\n🚀 TO USE THE ENHANCED PLATFORM:")
    print(f"1. Open: http://localhost:8001")
    print(f"2. Run screening on stocks")
    print(f"3. Click 'Backtest These' button")
    print(f"4. Choose engine: Custom (fast) or Backtrader (advanced)")
    print(f"5. Configure settings and select stocks")
    print(f"6. Run backtest and compare results!")
    
    print(f"\n📦 TO INSTALL BACKTRADER:")
    print(f"pip install backtrader --index-url YOUR_INTERNAL_ARTIFACTORY_URL")

if __name__ == "__main__":
    test_dual_engine_functionality()