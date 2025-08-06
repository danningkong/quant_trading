#!/usr/bin/env python3
"""
Test web interface accessibility
"""

import requests
import time
import subprocess
import threading
import sys
import os

def start_server():
    """Start the server in background"""
    try:
        os.chdir("backend")
        subprocess.run([sys.executable, "run_server.py"], check=True)
    except:
        pass

def test_web_interface():
    """Test if web interface is accessible"""
    print("Testing web interface accessibility...")
    
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Test endpoints
    base_url = "http://127.0.0.1:8000"
    
    tests = [
        ("/", "Frontend page"),
        ("/api/health", "Health check"),
        ("/api/popular-symbols", "Popular symbols"),
        ("/api/screener-types", "Screener types")
    ]
    
    for endpoint, description in tests:
        try:
            print(f"Testing {description} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"  Status: {response.status_code}")
            
            if endpoint == "/":
                # Check if it's HTML content
                if "html" in response.headers.get('content-type', '').lower():
                    print("  [OK] Frontend HTML served")
                else:
                    print("  [WARN] Not HTML content:", response.headers.get('content-type'))
                    print("  Content preview:", response.text[:200])
            else:
                # Check JSON endpoints
                if response.status_code == 200:
                    print("  [OK] JSON response received")
                else:
                    print(f"  [WARN] Status {response.status_code}")
                    
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
    
    print("\nTo manually test:")
    print("1. Run: python backend/run_server.py")
    print("2. Open: http://127.0.0.1:8000")
    print("3. Check browser developer console for errors")

if __name__ == "__main__":
    test_web_interface()