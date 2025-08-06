import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        self.cache = {}
        self.demo_mode = False
        self._setup_proxy()
        
    def _setup_proxy(self):
        """Configure proxy settings for corporate network"""
        proxy_url = "http://cba.proxy.prismaaccess.com:8080"
        
        # Set environment variables
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        
        # Disable SSL verification for corporate proxy
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['SSL_CERT_FILE'] = ''
        os.environ['SSL_CERT_DIR'] = ''
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
        # Configure curl_cffi to ignore SSL
        try:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass
        
        # Configure proxy dictionary
        self.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        logger.info(f"Configured proxy: {proxy_url} (SSL verification disabled)")
    
    def _get_demo_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Generate realistic demo data when live data is unavailable"""
        from demo_data_fetcher import DemoDataFetcher
        if not hasattr(self, '_demo_fetcher'):
            self._demo_fetcher = DemoDataFetcher()
        return self._demo_fetcher.get_stock_data(symbol, period)
    
    def _get_demo_info(self, symbol: str) -> Dict:
        """Get demo stock info when live data is unavailable"""
        from demo_data_fetcher import DemoDataFetcher
        if not hasattr(self, '_demo_fetcher'):
            self._demo_fetcher = DemoDataFetcher()
        return self._demo_fetcher.get_stock_info(symbol)
        
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch stock data from Yahoo Finance using direct API calls"""
        try:
            if f"{symbol}_{period}" in self.cache:
                return self.cache[f"{symbol}_{period}"]
            
            # Try direct Yahoo Finance API call with proxy
            data = self._fetch_yahoo_data_direct(symbol, period)
            
            if not data.empty:
                data = data.dropna()
                self.cache[f"{symbol}_{period}"] = data
                return data
            else:
                # Fallback to demo data
                logger.warning(f"No live data for {symbol}, using demo data")
                return self._get_demo_data(symbol, period)
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            # Final fallback to demo data
            try:
                return self._get_demo_data(symbol, period)
            except:
                return pd.DataFrame()
    
    def _fetch_yahoo_data_direct(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch data directly from Yahoo Finance API using requests"""
        try:
            # Convert period to timestamps
            end_time = int(datetime.now().timestamp())
            period_map = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180,
                '1y': 365, '2y': 730, '5y': 1825, '10y': 3650
            }
            days = period_map.get(period, 365)
            start_time = int((datetime.now() - timedelta(days=days)).timestamp())
            
            # Yahoo Finance API URL
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'period1': start_time,
                'period2': end_time,
                'interval': '1d',
                'events': 'history'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://finance.yahoo.com/',
                'Origin': 'https://finance.yahoo.com'
            }
            
            # Make API call with proxy
            response = requests.get(
                url=url, 
                params=params,
                headers=headers, 
                proxies=self.proxies, 
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                data_json = response.json()
                result = data_json['chart']['result'][0]
                
                # Extract data
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]
                
                # Create DataFrame
                dates = [datetime.fromtimestamp(ts) for ts in timestamps]
                df = pd.DataFrame({
                    'Open': quotes['open'],
                    'High': quotes['high'], 
                    'Low': quotes['low'],
                    'Close': quotes['close'],
                    'Volume': quotes['volume']
                }, index=dates)
                
                # Remove None values and duplicates
                df = df.dropna().drop_duplicates()
                logger.info(f"Successfully fetched {len(df)} days of {symbol} data via API")
                
                return df
            else:
                logger.error(f"Yahoo API error {response.status_code} for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Direct API fetch failed for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_multiple_stocks(self, symbols: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple stocks"""
        result = {}
        for symbol in symbols:
            data = self.get_stock_data(symbol, period)
            if not data.empty:
                result[symbol] = data
        return result
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get stock information including market cap, sector, etc."""
        try:
            # Try direct API call for stock info
            info_data = self._fetch_stock_info_direct(symbol)
            if info_data:
                return info_data
            else:
                # Fallback to demo data
                logger.warning(f"No live info for {symbol}, using demo data")
                return self._get_demo_info(symbol)
                
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            # Final fallback to demo data
            try:
                return self._get_demo_info(symbol)
            except:
                return {'symbol': symbol}
    
    def _fetch_stock_info_direct(self, symbol: str) -> Dict:
        """Fetch stock info directly from Yahoo Finance API"""
        try:
            # Try multiple Yahoo Finance endpoints with different headers
            endpoints = [
                # Primary endpoint with detailed modules
                {
                    'url': f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}",
                    'params': {'modules': 'summaryDetail,defaultKeyStatistics,financialData'},
                    'headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'application/json',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Referer': 'https://finance.yahoo.com/',
                        'Origin': 'https://finance.yahoo.com',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-site'
                    }
                },
                # Fallback to simpler endpoint
                {
                    'url': f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}",
                    'params': {'modules': 'summaryDetail'},
                    'headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://finance.yahoo.com/'
                    }
                },
                # Alternative quote endpoint
                {
                    'url': f"https://query1.finance.yahoo.com/v7/finance/quote",
                    'params': {'symbols': symbol},
                    'headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://finance.yahoo.com/'
                    }
                }
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(
                        url=endpoint['url'],
                        params=endpoint['params'], 
                        headers=endpoint['headers'],
                        proxies=self.proxies,
                        verify=False,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Handle different response formats
                        if 'quoteSummary' in data and data['quoteSummary']['result']:
                            # Standard quoteSummary format
                            result = data['quoteSummary']['result'][0]
                            summary = result.get('summaryDetail', {})
                            key_stats = result.get('defaultKeyStatistics', {})
                            financial = result.get('financialData', {})
                            
                            logger.info(f"Successfully fetched live info for {symbol} via quoteSummary")
                            return {
                                'symbol': symbol,
                                'market_cap': self._extract_value(summary.get('marketCap')),
                                'sector': 'Unknown',
                                'industry': 'Unknown',
                                'pe_ratio': self._extract_value(summary.get('trailingPE')),
                                'pb_ratio': self._extract_value(key_stats.get('priceToBook')),
                                'dividend_yield': self._extract_value(summary.get('dividendYield')),
                                'beta': self._extract_value(key_stats.get('beta')),
                                'avg_volume': self._extract_value(summary.get('averageVolume')),
                                'current_price': self._extract_value(summary.get('regularMarketPrice'))
                            }
                        
                        elif 'quoteResponse' in data and data['quoteResponse']['result']:
                            # Alternative quote format
                            quote = data['quoteResponse']['result'][0]
                            
                            logger.info(f"Successfully fetched live info for {symbol} via quote")
                            return {
                                'symbol': symbol,
                                'market_cap': quote.get('marketCap'),
                                'sector': quote.get('sector', 'Unknown'),
                                'industry': quote.get('industry', 'Unknown'),
                                'pe_ratio': quote.get('trailingPE'),
                                'pb_ratio': quote.get('priceToBook'),
                                'dividend_yield': quote.get('dividendYield'),
                                'beta': quote.get('beta'),
                                'avg_volume': quote.get('averageVolume10days'),
                                'current_price': quote.get('regularMarketPrice')
                            }
                    
                    elif response.status_code == 401:
                        logger.warning(f"Yahoo API 401 for {symbol} with endpoint {endpoint['url']}, trying next endpoint")
                        continue  # Try next endpoint
                    
                    else:
                        logger.warning(f"Yahoo API error {response.status_code} for {symbol} with endpoint {endpoint['url']}")
                        continue  # Try next endpoint
                        
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request failed for {symbol} with endpoint {endpoint['url']}: {e}")
                    continue  # Try next endpoint
                    
            # All endpoints failed
            logger.error(f"All Yahoo quote API endpoints failed for {symbol}")
            return None
                
        except Exception as e:
            logger.error(f"Direct info fetch failed for {symbol}: {e}")
            return None
    
    def _extract_value(self, yahoo_value):
        """Extract numeric value from Yahoo Finance API response"""
        if yahoo_value is None:
            return None
        if isinstance(yahoo_value, dict):
            return yahoo_value.get('raw', yahoo_value.get('fmt', None))
        return yahoo_value
    
    def get_sp500_symbols(self) -> List[str]:
        """Get S&P 500 symbols from Wikipedia"""
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            
            # Use requests session with proxy for pandas read_html
            session = requests.Session()
            session.proxies.update(self.proxies)
            
            # Create a custom request function for pandas
            def custom_request(url):
                response = session.get(url)
                response.raise_for_status()
                return response.text
            
            # Use pandas read_html with custom request
            tables = pd.read_html(url, requests_kwargs={'proxies': self.proxies})
            sp500 = tables[0]
            return sp500['Symbol'].tolist()
        except Exception as e:
            logger.error(f"Error fetching S&P 500 symbols: {e}")
            # Fallback to a subset of popular stocks
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    
    def get_popular_etfs(self) -> List[str]:
        """Get list of popular ETFs"""
        return [
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VXUS', 'BND', 'VEA',
            'VWO', 'AGG', 'TLT', 'GLD', 'SLV', 'USO', 'XLF', 'XLE',
            'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLRE', 'XLB'
        ]
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to price data"""
        df = data.copy()
        
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Exponential moving averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / df['BB_Width']
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Volatility
        df['Volatility'] = df['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)
        
        return df