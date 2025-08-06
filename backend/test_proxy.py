#!/usr/bin/env python3
"""
Test proxy configuration
"""

import sys
import os
sys.path.insert(0, '.')

from data_fetcher import DataFetcher

def test_proxy():
    print("Testing proxy configuration...")
    
    try:
        fetcher = DataFetcher()
        print("DataFetcher initialized successfully")
        print("Proxy configured for:", fetcher.proxies['https'])
        
        print("\nTesting AAPL data fetch...")
        data = fetcher.get_stock_data('AAPL', '5d')
        
        if not data.empty:
            print(f"SUCCESS: Got {len(data)} days of AAPL data")
            print(f"Latest close price: ${data['Close'].iloc[-1]:.2f}")
            print("Columns:", list(data.columns))
            return True
        else:
            print("No data returned - check proxy connectivity")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_proxy()
    if success:
        print("\nProxy configuration is working!")
    else:
        print("\nProxy configuration needs adjustment")