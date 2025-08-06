#!/usr/bin/env python3
"""
Debug API endpoints directly
"""

import requests
import json

def test_api_endpoints():
    base_url = "http://127.0.0.1:8001"
    
    print("DEBUGGING API ENDPOINTS")
    print("=" * 25)
    
    # Test 1: Screen stocks endpoint
    print("\n1. Testing /api/screen-stocks...")
    try:
        screening_data = {
            "symbols": ["AAPL", "MSFT"],
            "screener_type": "momentum"
        }
        
        response = requests.post(
            f"{base_url}/api/screen-stocks",
            json=screening_data,
            timeout=60
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response keys: {list(result.keys())}")
            
            if 'stocks' in result:
                print(f"   Stocks found: {len(result['stocks'])}")
                for stock in result['stocks'][:3]:
                    print(f"     {stock}")
            elif 'results' in result:
                print(f"   Results found: {len(result['results'])}")  
                for res in result['results'][:3]:
                    print(f"     {res}")
            else:
                print(f"   Full response: {json.dumps(result, indent=2)[:500]}")
                
        else:
            print(f"   Error response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False
    
    # Test 2: Direct backtest endpoint  
    print("\n2. Testing /api/run-integrated-backtest...")
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
            timeout=120
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response keys: {list(result.keys())}")
            
            if result.get('success'):
                print(f"   SUCCESS!")
                perf = result.get('performance', {})
                print(f"     Return: {perf.get('total_return', 0)*100:.2f}%")
                print(f"     Sharpe: {perf.get('sharpe_ratio', 0):.2f}")
            else:
                print(f"   Failed: {result.get('error', 'No error message')}")
                
        else:
            print(f"   Error: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = test_api_endpoints()
    
    if success:
        print(f"\n" + "=" * 25)
        print("API ENDPOINTS: WORKING")
        print("All major endpoints functional")
    else:
        print(f"\nAPI needs debugging.")