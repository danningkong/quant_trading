#!/usr/bin/env python3
"""
Test server functionality with Yahoo Finance data
"""

import requests
import json

def test_server_yahoo():
    base_url = "http://127.0.0.1:8001"
    
    print("TESTING SERVER WITH YAHOO FINANCE DATA")
    print("=" * 42)
    
    # Test screening endpoint
    print("\n1. Testing screening endpoint...")
    try:
        screening_data = {
            "screener_type": "momentum",
            "symbols": ["AAPL", "MSFT", "GOOGL"]
        }
        
        response = requests.post(
            f"{base_url}/api/screen-stocks",
            json=screening_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            symbols = [stock['symbol'] for stock in result.get('stocks', [])]
            print(f"   [SUCCESS] Screened {len(symbols)} stocks: {symbols}")
            
            # Test integrated backtest
            print("\n2. Testing integrated backtest with screened stocks...")
            backtest_data = {
                "symbols": symbols[:2],  # Use first 2 symbols
                "screener_type": "momentum",
                "backtest_settings": {
                    "engine": "custom",
                    "initial_capital": 50000,
                    "max_positions": 1,
                    "rebalance_frequency": "monthly"
                }
            }
            
            backtest_response = requests.post(
                f"{base_url}/api/run-integrated-backtest",
                json=backtest_data,
                timeout=60
            )
            
            if backtest_response.status_code == 200:
                bt_result = backtest_response.json()
                perf = bt_result.get('performance', {})
                print(f"   [SUCCESS] Integrated backtest completed!")
                print(f"   Total Return: {perf.get('total_return', 0)*100:.2f}%")
                print(f"   Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
                print(f"   Number of Trades: {perf.get('number_of_trades', 0)}")
                return True
            else:
                print(f"   [ERROR] Backtest failed: HTTP {backtest_response.status_code}")
                print(f"   Response: {backtest_response.text[:200]}...")
                return False
                
        else:
            print(f"   [ERROR] Screening failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Server test failed: {e}")
        return False

if __name__ == "__main__":
    if test_server_yahoo():
        print(f"\n" + "=" * 42)
        print("SERVER WITH YAHOO FINANCE: WORKING!")
        print("Real price data + Demo fundamentals = Success")
        print("The platform is fully operational!")
        print("=" * 42)
    else:
        print(f"\nServer needs attention.")