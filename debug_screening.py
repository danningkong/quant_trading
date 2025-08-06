#!/usr/bin/env python3
"""
Debug screening issues
"""

import sys
import os
import pandas as pd
sys.path.insert(0, 'backend')

def debug_screening():
    print("DEBUGGING SCREENING ISSUES")
    print("=" * 30)
    
    try:
        from data_fetcher import DataFetcher
        from strategies.screeners import StockScreener, ScreenerType
        
        print("\n1. Testing data fetcher directly...")
        fetcher = DataFetcher()
        
        # Test single stock data
        print("   Testing AAPL data...")
        aapl_data = fetcher.get_stock_data('AAPL', '3mo')
        aapl_info = fetcher.get_stock_info('AAPL')
        
        print(f"   AAPL price data: {len(aapl_data)} days")
        print(f"   AAPL info: {list(aapl_info.keys())}")
        print(f"   Current price: ${aapl_info.get('current_price', 'N/A')}")
        print(f"   Market cap: {aapl_info.get('market_cap', 'N/A')}")
        print(f"   P/E ratio: {aapl_info.get('pe_ratio', 'N/A')}")
        
        if aapl_data.empty:
            print("   [ERROR] No price data for AAPL!")
            return False
            
        print("\n2. Testing screener directly...")
        screener = StockScreener()
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        
        # Prepare stock data in the format expected by screener
        stock_data = {}
        for symbol in symbols:
            price_data = fetcher.get_stock_data(symbol, '3mo')
            if not price_data.empty:
                price_data = fetcher.calculate_technical_indicators(price_data)
                fundamental_data = fetcher.get_stock_info(symbol)
                stock_data[symbol] = {
                    'price_data': price_data,
                    'fundamental_data': fundamental_data
                }
        
        print(f"   Prepared data for {len(stock_data)} stocks")
        
        # Test momentum screening
        print("   Running momentum screen...")
        results = screener.screen_stocks(stock_data, ScreenerType.MOMENTUM)
        
        print(f"   Screen results: {len(results)} rows")
        
        if isinstance(results, pd.DataFrame) and not results.empty:
            print("   Top results:")
            for _, row in results.head(3).iterrows():
                print(f"     {row['symbol']}: score={row['score']:.2f}")
                return_1m = row.get('return_1m', 0)
                if isinstance(return_1m, str):
                    return_1m = 0
                print(f"       performance: return_1m={return_1m:.3f}")
        elif isinstance(results, list):
            for stock in results:
                print(f"     {stock['symbol']}: score={stock['score']:.2f}")
                print(f"       criteria: {list(stock['criteria'].keys())}")
        else:
            print("   [ERROR] Unexpected results format or empty results")
        
        if isinstance(results, pd.DataFrame) and results.empty:
            print("   [ERROR] No screening results!")
            
            # Debug why no results
            print("\n   Debugging individual stock data...")
            for symbol in symbols:
                data = fetcher.get_stock_data(symbol, '3mo')
                info = fetcher.get_stock_info(symbol)
                
                print(f"   {symbol}:")
                print(f"     Price data: {len(data)} days")
                print(f"     Info keys: {list(info.keys()) if info else 'None'}")
                
                if not data.empty:
                    data_with_indicators = fetcher.calculate_technical_indicators(data)
                    print(f"     Technical indicators: {len(data_with_indicators.columns)} columns")
                    print(f"     Latest close: ${data_with_indicators['Close'].iloc[-1]:.2f}")
                    print(f"     Has SMA_20: {'SMA_20' in data_with_indicators.columns}")
                    print(f"     Has RSI: {'RSI' in data_with_indicators.columns}")
                else:
                    print(f"     [ERROR] No price data for {symbol}")
            
            return False
        
        return True
        
    except Exception as e:
        print(f"   [ERROR] Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if debug_screening():
        print(f"\n" + "=" * 30)
        print("SCREENING DEBUG: SUCCESS")
        print("All components working properly")
    else:
        print(f"\nFound issues with screening system.")