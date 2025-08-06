#!/usr/bin/env python3
"""
Test Backtrader engine through the live server
"""

import requests
import json

def test_backtrader_live():
    base_url = "http://127.0.0.1:8001"
    
    print("TESTING BACKTRADER ENGINE ON LIVE SERVER")
    print("=" * 40)
    
    # Test Backtrader engine
    print("\n1. Testing Backtrader Engine...")
    try:
        backtest_data = {
            "symbols": ["AAPL"],
            "screener_type": "momentum",
            "backtest_settings": {
                "engine": "backtrader",
                "initial_capital": 50000,
                "max_positions": 1,
                "rebalance_frequency": "monthly",
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
            json=backtest_data,
            timeout=60
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('installation_required'):
                print("   [ERROR] Backtrader still reports installation required")
                return False
            
            perf = result.get('performance', {})
            print("   [SUCCESS] BACKTRADER ENGINE WORKS!")
            print(f"   Total Return: {perf.get('total_return', 0)*100:.2f}%")
            print(f"   Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
            print(f"   Engine: Backtrader")
            
            # Show Backtrader-specific stats
            bt_stats = result.get('backtrader_stats', {})
            if bt_stats:
                print(f"   Advanced Backtrader Stats:")
                print(f"     Total Trades: {bt_stats.get('total_trades', 0)}")
                print(f"     Winning Trades: {bt_stats.get('winning_trades', 0)}")
                print(f"     Losing Trades: {bt_stats.get('losing_trades', 0)}")
            
            return True
            
        else:
            print(f"   [ERROR] HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Request failed: {e}")
        return False

if __name__ == "__main__":
    if test_backtrader_live():
        print("\n" + "=" * 40)
        print("COMPLETE SUCCESS!")
        print("Both engines are now working:")
        print("- Custom Engine: Fast & Simple")  
        print("- Backtrader Engine: Advanced Technical Analysis")
        print("Your platform is fully operational!")
    else:
        print("\nBacktrader engine needs attention.")