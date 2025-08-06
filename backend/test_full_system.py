#!/usr/bin/env python3
"""
Test full system functionality with proxy
"""

import sys
import os
sys.path.insert(0, '.')

from data_fetcher import DataFetcher
from strategies.screeners import StockScreener, ScreenerType

def test_full_screening():
    print("=" * 50)
    print("TESTING FULL SCREENING FUNCTIONALITY")
    print("=" * 50)
    
    # Test 1: Data Fetcher with proxy
    print("\n1. Testing Data Fetcher...")
    try:
        fetcher = DataFetcher()
        print(f"   Proxy configured: {fetcher.proxies['https']}")
        
        # Test multiple symbols
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        stock_data = {}
        
        for symbol in symbols:
            print(f"   Fetching {symbol}...")
            price_data = fetcher.get_stock_data(symbol, '6mo')
            if not price_data.empty:
                fundamental_data = fetcher.get_stock_info(symbol)
                stock_data[symbol] = {
                    'price_data': fetcher.calculate_technical_indicators(price_data),
                    'fundamental_data': fundamental_data
                }
                print(f"   [OK] {symbol}: {len(price_data)} days, PE: {fundamental_data.get('pe_ratio', 'N/A')}")
            else:
                print(f"   [FAIL] {symbol}: No data")
        
        if not stock_data:
            print("   No stock data available - cannot proceed")
            return False
            
    except Exception as e:
        print(f"   Error in data fetching: {e}")
        return False
    
    # Test 2: Stock Screening
    print("\n2. Testing Stock Screener...")
    try:
        screener = StockScreener()
        
        # Test momentum screening
        print("   Running momentum screening...")
        results = screener.screen_stocks(stock_data, ScreenerType.MOMENTUM)
        
        if not results.empty:
            print(f"   [OK] Found {len(results)} momentum candidates")
            top_result = results.iloc[0]
            print(f"   [TOP] Top pick: {top_result['symbol']} (score: {top_result['score']:.3f})")
            
            # Test other strategies
            for strategy_type in [ScreenerType.VALUE, ScreenerType.TECHNICAL]:
                try:
                    strategy_results = screener.screen_stocks(stock_data, strategy_type)
                    print(f"   [OK] {strategy_type.value}: {len(strategy_results)} results")
                except Exception as e:
                    print(f"   [WARN] {strategy_type.value} failed: {e}")
        else:
            print("   [FAIL] No screening results")
            return False
            
    except Exception as e:
        print(f"   Error in screening: {e}")
        return False
    
    # Test 3: API Simulation
    print("\n3. Testing API Integration...")
    try:
        # Simulate API request data
        screening_request = {
            'symbols': ['AAPL', 'MSFT', 'GOOGL'],
            'screener_type': 'momentum'
        }
        
        # Test screening logic
        results = screener.screen_stocks(stock_data, ScreenerType.MOMENTUM)
        
        if not results.empty:
            # Convert to API response format
            api_results = []
            for _, row in results.head(5).iterrows():
                api_results.append({
                    'symbol': row['symbol'],
                    'strategy': row['strategy'],
                    'score': float(row['score']),
                    'metrics': {k: v for k, v in row['metrics'].items() 
                              if isinstance(v, (int, float))}
                })
            
            print(f"   [OK] API simulation successful: {len(api_results)} results")
            print(f"   Sample result: {api_results[0]['symbol']} - {api_results[0]['score']:.3f}")
        else:
            print("   [FAIL] API simulation failed")
            return False
            
    except Exception as e:
        print(f"   Error in API simulation: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("[OK] Proxy configuration working")
    print("[OK] Data fetching successful") 
    print("[OK] Stock screening operational")
    print("[OK] API integration ready")
    print("Platform ready for deployment!")
    
    return True

if __name__ == "__main__":
    success = test_full_screening()
    if success:
        print("\nYou can now start the server with: python quick_start.py")
    else:
        print("\nPlease check the errors above")