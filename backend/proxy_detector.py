"""
Corporate firewall and proxy detection utility
"""

import requests
import socket
import subprocess
import platform
import logging
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyDetector:
    def __init__(self):
        self.corporate_proxy = "http://cba.proxy.prismaaccess.com:8080"
        self.test_urls = [
            "https://httpbin.org/ip",
            "https://httpbin.org/get",
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://www.google.com"
        ]
        self.corporate_indicators = [
            "cba.proxy.prismaaccess.com",
            "corporate",
            "company",
            ".local",
            "domain.com"  # Add your corporate domain patterns here
        ]
        # Cache the detection result to avoid repeated slow checks
        self._cached_result = None
        self._cache_timestamp = None
    
    def is_behind_corporate_firewall(self) -> Tuple[bool, str]:
        """
        Detect if we're behind a corporate firewall (with caching)
        Returns (is_corporate, reason)
        """
        import time
        
        # Check cache (5 minutes validity)
        if self._cached_result and self._cache_timestamp:
            if time.time() - self._cache_timestamp < 300:  # 5 minutes
                logger.info(f"Using cached firewall detection: {self._cached_result[1]}")
                return self._cached_result
        
        # Test 1: Quick proxy availability check first (faster)
        logger.info("Testing proxy availability...")
        proxy_responds = self._test_proxy_availability()
        
        if proxy_responds:
            result = (True, "Corporate proxy detected and available")
        else:
            # Test 2: Check network connectivity without proxy
            logger.info("Testing direct internet connectivity...")
            can_connect_direct = self._test_direct_connectivity()
            
            if can_connect_direct:
                result = (False, "Direct internet access available")
            else:
                # Assume corporate firewall if neither work well
                result = (True, "Likely behind corporate firewall - using proxy")
        
        # Cache the result
        self._cached_result = result
        self._cache_timestamp = time.time()
        
        logger.info(f"Firewall detection result: {result[1]}")
        return result
    
    def _test_direct_connectivity(self) -> bool:
        """Test if we can connect directly to internet without proxy"""
        try:
            # Test critical financial APIs first (most likely to be blocked)
            critical_urls = self.test_urls[:2]  # Yahoo Finance URLs
            
            for url in critical_urls:
                try:
                    response = requests.get(
                        url, 
                        timeout=3,  # Reduced timeout for faster detection
                        verify=False,  # Corporate networks often have certificate issues
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
                    if response.status_code == 200:
                        logger.info(f"Direct connectivity to financial APIs confirmed via {url}")
                        return True
                except (requests.exceptions.RequestException, requests.exceptions.Timeout):
                    logger.warning(f"Direct access failed for critical URL: {url}")
                    continue
            
            logger.info("Direct access to financial APIs failed - likely behind corporate firewall")
            return False
            
        except Exception as e:
            logger.error(f"Error testing direct connectivity: {e}")
            return False
    
    def _test_proxy_connectivity(self) -> bool:
        """Test if corporate proxy is available and working"""
        try:
            proxies = {
                'http': self.corporate_proxy,
                'https': self.corporate_proxy
            }
            
            # Test with corporate proxy - prioritize Yahoo Finance
            test_urls = self.test_urls[:2]  # Yahoo Finance URLs first
            
            for url in test_urls:
                try:
                    logger.info(f"Testing proxy connectivity to {url}")
                    response = requests.get(
                        url,
                        proxies=proxies,
                        timeout=8,  # Reduced timeout
                        verify=False,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
                    if response.status_code == 200:
                        logger.info(f"Proxy connectivity confirmed via {url}")
                        return True
                    else:
                        logger.warning(f"Proxy returned status {response.status_code} for {url}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Proxy test failed for {url}: {e}")
                    continue
            
            logger.error("All proxy connectivity tests failed")
            return False
            
        except Exception as e:
            logger.error(f"Error testing proxy connectivity: {e}")
            return False
    
    def _test_proxy_availability(self) -> bool:
        """Quick test to see if proxy server responds at all"""
        try:
            import socket
            
            # Parse proxy URL
            proxy_host = "cba.proxy.prismaaccess.com"
            proxy_port = 8080
            
            # Test socket connection to proxy
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((proxy_host, proxy_port))
            sock.close()
            
            if result == 0:
                logger.info(f"Proxy server {proxy_host}:{proxy_port} is reachable")
                return True
            else:
                logger.warning(f"Proxy server {proxy_host}:{proxy_port} is not reachable")
                return False
                
        except Exception as e:
            logger.error(f"Error testing proxy availability: {e}")
            return False
    
    def get_proxy_config(self) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration if needed
        Returns None if no proxy needed, or proxy dict if required
        """
        # Check for manual override
        import os
        if os.environ.get('FORCE_PROXY') == '1':
            logger.info("Manual proxy override detected - forcing corporate proxy")
            return {
                'http': self.corporate_proxy,
                'https': self.corporate_proxy
            }
        elif os.environ.get('FORCE_PROXY') == '0':
            logger.info("Manual proxy override detected - forcing direct connection")
            return None
        
        # Automatic detection
        is_corporate, reason = self.is_behind_corporate_firewall()
        
        logger.info(f"Proxy detection result: {reason}")
        
        if is_corporate:
            return {
                'http': self.corporate_proxy,
                'https': self.corporate_proxy
            }
        else:
            return None
    
    def get_network_info(self) -> Dict[str, str]:
        """Get additional network information for debugging"""
        info = {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'corporate_proxy': self.corporate_proxy
        }
        
        try:
            # Try to get domain information
            if platform.system() == 'Windows':
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=10)
                if 'Domain' in result.stdout:
                    for line in result.stdout.split('\n'):
                        if 'Primary Dns Suffix' in line:
                            info['dns_suffix'] = line.split(':')[-1].strip()
                        if 'Connection-specific DNS Suffix' in line:
                            info['connection_dns_suffix'] = line.split(':')[-1].strip()
            
        except Exception as e:
            logger.warning(f"Could not get network info: {e}")
        
        return info