#!/usr/bin/env python3
"""
Test minimal API request to debug 500 error
"""

import requests
import json

def test_minimal_api():
    base_url = "http://127.0.0.1:8001"
    
    print("TESTING MINIMAL API REQUEST")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] Server is running")
        else:
            print("   [ERROR] Server not responding correctly")
            return
    except Exception as e:
        print(f"   [ERROR] Connection failed: {e}")
        return
    
    # Test 2: Simple screening
    print("\n2. Simple Screening...")
    try:
        screening_data = {
            "symbols": ["AAPL"],
            "screener_type": "momentum"
        }
        
        response = requests.post(
            f"{base_url}/api/screen-stocks", 
            json=screening_data,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Screening successful: {len(data.get('results', []))} results")
            
            if data.get('results'):
                # Test 3: Minimal integrated backtest with custom engine
                print("\n3. Minimal Custom Engine Backtest...")
                
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
                
                print(f"   Request: {json.dumps(backtest_data, indent=2)}")
                
                response = requests.post(
                    f"{base_url}/api/run-integrated-backtest",
                    json=backtest_data,
                    timeout=60
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    perf = result.get('performance', {})
                    print("   [SUCCESS] Custom engine backtest works!")
                    print(f"   Total Return: {perf.get('total_return', 0)*100:.2f}%")
                    print(f"   Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
                    
                    # Test 4: Test Backtrader engine (should fail gracefully)
                    print("\n4. Backtrader Engine Test...")
                    
                    backtest_data['backtest_settings']['engine'] = 'backtrader'
                    
                    response = requests.post(
                        f"{base_url}/api/run-integrated-backtest",
                        json=backtest_data,
                        timeout=60
                    )
                    
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('installation_required'):
                            print("   [OK] Backtrader correctly reported as not installed")
                        else:
                            print("   [UNEXPECTED] Backtrader worked!")
                    else:
                        print(f"   [ERROR] HTTP {response.status_code}")
                        print(f"   Response: {response.text[:300]}")
                        
                else:
                    print(f"   [ERROR] HTTP {response.status_code}")
                    print(f"   Response: {response.text[:300]}")
                    
            else:
                print("   [WARNING] No screening results to test backtest")
                
        else:
            print(f"   [ERROR] HTTP {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"   [ERROR] Request failed: {e}")
    
    print("\n" + "=" * 40)
    print("MINIMAL API TEST COMPLETED")

if __name__ == "__main__":
    test_minimal_api()