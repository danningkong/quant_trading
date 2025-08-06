import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoDataFetcher:
    """Demo data fetcher that works without internet connection"""
    
    def __init__(self):
        self.cache = {}
        self.demo_symbols = {
            'AAPL': {'base_price': 185, 'volatility': 0.25, 'sector': 'Technology'},
            'MSFT': {'base_price': 340, 'volatility': 0.22, 'sector': 'Technology'},
            'GOOGL': {'base_price': 135, 'volatility': 0.28, 'sector': 'Technology'},
            'AMZN': {'base_price': 145, 'volatility': 0.30, 'sector': 'Consumer Discretionary'},
            'TSLA': {'base_price': 240, 'volatility': 0.40, 'sector': 'Consumer Discretionary'},
            'META': {'base_price': 320, 'volatility': 0.35, 'sector': 'Technology'},
            'NVDA': {'base_price': 450, 'volatility': 0.45, 'sector': 'Technology'},
            'NFLX': {'base_price': 420, 'volatility': 0.32, 'sector': 'Communication Services'},
            'JPM': {'base_price': 155, 'volatility': 0.20, 'sector': 'Financial Services'},
            'V': {'base_price': 280, 'volatility': 0.18, 'sector': 'Financial Services'},
            'SPY': {'base_price': 445, 'volatility': 0.16, 'sector': 'ETF'},
            'QQQ': {'base_price': 380, 'volatility': 0.20, 'sector': 'ETF'},
            'IWM': {'base_price': 195, 'volatility': 0.25, 'sector': 'ETF'},
            'VTI': {'base_price': 245, 'volatility': 0.15, 'sector': 'ETF'},
        }
        
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Generate realistic mock stock data"""
        try:
            if f"{symbol}_{period}" in self.cache:
                return self.cache[f"{symbol}_{period}"]
            
            if symbol not in self.demo_symbols:
                logger.warning(f"Symbol {symbol} not in demo data")
                return pd.DataFrame()
            
            # Parse period
            days = self._parse_period(period)
            if days <= 0:
                return pd.DataFrame()
            
            # Generate dates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            # Remove weekends
            dates = dates[dates.weekday < 5]
            
            # Generate price data
            symbol_info = self.demo_symbols[symbol]
            base_price = symbol_info['base_price']
            volatility = symbol_info['volatility']
            
            # Set seed for consistent data
            np.random.seed(hash(symbol) % 2147483647)
            
            # Generate returns with some trend
            daily_returns = np.random.normal(0.0005, volatility/16, len(dates))
            
            # Add some momentum/trend
            trend = np.sin(np.linspace(0, 2*np.pi, len(dates))) * 0.002
            daily_returns += trend
            
            # Calculate prices
            prices = [base_price]
            for ret in daily_returns[1:]:
                new_price = prices[-1] * (1 + ret)
                prices.append(max(new_price, 1.0))
            
            # Create OHLCV data
            data = pd.DataFrame(index=dates[:len(prices)])
            data['Close'] = prices
            
            # Generate realistic OHLC
            noise = np.random.normal(1.0, 0.005, len(data))
            data['Open'] = data['Close'].shift(1).fillna(data['Close'].iloc[0]) * noise
            
            high_noise = np.random.uniform(1.0, 1.015, len(data))
            low_noise = np.random.uniform(0.985, 1.0, len(data))
            
            data['High'] = np.maximum(data['Open'], data['Close']) * high_noise
            data['Low'] = np.minimum(data['Open'], data['Close']) * low_noise
            
            # Generate volume
            base_volume = 50_000_000 if 'ETF' not in symbol_info['sector'] else 100_000_000
            volume_noise = np.random.lognormal(0, 0.5, len(data))
            data['Volume'] = (base_volume * volume_noise).astype(int)
            
            # Cache the data
            self.cache[f"{symbol}_{period}"] = data
            
            logger.info(f"Generated demo data for {symbol}: {len(data)} days")
            return data
            
        except Exception as e:
            logger.error(f"Error generating demo data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _parse_period(self, period: str) -> int:
        """Convert period string to days"""
        period_map = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180,
            '1y': 365, '2y': 730, '5y': 1825, '10y': 3650, 'ytd': 250, 'max': 3650
        }
        return period_map.get(period, 365)
    
    def get_multiple_stocks(self, symbols: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple stocks"""
        result = {}
        for symbol in symbols:
            data = self.get_stock_data(symbol, period)
            if not data.empty:
                result[symbol] = data
        return result
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get mock stock information"""
        if symbol not in self.demo_symbols:
            return {'symbol': symbol}
        
        symbol_info = self.demo_symbols[symbol]
        
        # Generate realistic fundamental data
        np.random.seed(hash(symbol) % 2147483647)
        
        market_cap = np.random.uniform(50e9, 2e12)  # 50B to 2T
        pe_ratio = np.random.uniform(8, 35) if symbol_info['sector'] != 'ETF' else None
        pb_ratio = np.random.uniform(1, 6) if symbol_info['sector'] != 'ETF' else None
        dividend_yield = np.random.uniform(0, 0.06)
        beta = np.random.uniform(0.5, 2.0)
        
        return {
            'symbol': symbol,
            'market_cap': market_cap,
            'sector': symbol_info['sector'],
            'industry': 'Mock Industry',
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio,
            'dividend_yield': dividend_yield,
            'beta': beta,
            'avg_volume': int(np.random.uniform(10e6, 100e6)),
            'current_price': symbol_info['base_price'] * np.random.uniform(0.95, 1.05)
        }
    
    def get_sp500_symbols(self) -> List[str]:
        """Get mock S&P 500 symbols"""
        return list(self.demo_symbols.keys())[:10]  # First 10 symbols
    
    def get_popular_etfs(self) -> List[str]:
        """Get list of mock popular ETFs"""
        return [symbol for symbol, info in self.demo_symbols.items() 
                if info['sector'] == 'ETF']
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to price data"""
        if data.empty:
            return data
            
        df = data.copy()
        
        try:
            # Moving averages
            df['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
            df['SMA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
            
            # Exponential moving averages
            df['EMA_12'] = df['Close'].ewm(span=12, min_periods=1).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, min_periods=1).mean()
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, min_periods=1).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20, min_periods=1).mean()
            bb_std = df['Close'].rolling(window=20, min_periods=1).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
            
            # Avoid division by zero
            df['BB_Position'] = ((df['Close'] - df['BB_Lower']) / 
                               df['BB_Width'].replace(0, np.nan)).fillna(0.5)
            
            # Volume indicators
            df['Volume_SMA'] = df['Volume'].rolling(window=20, min_periods=1).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA'].replace(0, 1)
            
            # Volatility
            df['Volatility'] = (df['Close'].pct_change().rolling(window=20, min_periods=1).std() * 
                              np.sqrt(252))
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
        
        return df