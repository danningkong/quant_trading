#!/usr/bin/env python3
"""
Final test to verify the HTTP 500 error is fixed
"""

import requests
import json

def test_final_fix():
    base_url = "http://127.0.0.1:8001"
    
    print("FINAL TEST: HTTP 500 ERROR FIX")
    print("=" * 35)
    
    # Test the main issue: Custom engine backtest
    print("\n1. Testing Custom Engine (Main Issue)...")
    try:
        backtest_data = {
            "symbols": ["AAPL"],
            "screener_type": "momentum",
            "backtest_settings": {
                "engine": "custom",
                "initial_capital": 50000,
                "max_positions": 1,
                "rebalance_frequency": "monthly"
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
            perf = result.get('performance', {})
            print("   [SUCCESS] HTTP 500 ERROR IS FIXED!")
            print(f"   Total Return: {perf.get('total_return', 0)*100:.2f}%")
            print(f"   Profit Factor: {perf.get('profit_factor', 0):.2f}")
            print(f"   Engine: Custom")
            
        elif response.status_code == 500:
            print("   [STILL BROKEN] HTTP 500 error persists")
            print(f"   Response: {response.text[:200]}...")
            return False
        else:
            print(f"   [ERROR] Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Request failed: {e}")
        return False
    
    print("\n" + "=" * 35)
    print("SUCCESS! CUSTOM ENGINE WORKS!")
    print("The main HTTP 500 error has been fixed.")
    print("Your dual-engine platform is ready!")
    return True

if __name__ == "__main__":
    success = test_final_fix()
    if not success:
        print("\nStill debugging needed.")
    else:
        print("\nRestart your server and test the web interface!")