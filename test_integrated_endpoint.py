#!/usr/bin/env python3
"""
Test just the integrated backtest endpoint to debug the 500 error
"""

import requests
import json

def test_integrated_backtest():
    base_url = "http://127.0.0.1:8001"
    
    print("=" * 50)
    print("TESTING INTEGRATED BACKTEST ENDPOINT")
    print("=" * 50)
    
    # Test data
    test_data = {
        "symbols": ["AAPL", "MSFT"],
        "screener_type": "momentum",
        "backtest_settings": {
            "initial_capital": 100000,
            "max_positions": 5,
            "rebalance_frequency": "monthly",
            "commission": 0.001,
            "slippage": 0.001,
            "lookback_period": "1y"
        }
    }
    
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        print("\nSending request...")
        response = requests.post(
            f"{base_url}/api/run-integrated-backtest",
            json=test_data,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS!")
            perf = result.get('performance', {})
            print(f"Total Return: {perf.get('total_return', 0)*100:.2f}%")
            print(f"Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
            print(f"Trades: {perf.get('number_of_trades', 0)}")
        else:
            print("ERROR!")
            print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")
        
if __name__ == "__main__":
    test_integrated_backtest()