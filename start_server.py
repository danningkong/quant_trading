#!/usr/bin/env python3
"""
Startup script for Quant Trading Platform
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'yfinance', 'pandas', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {missing_packages}")
        print("Installing missing packages...")
        
        # Use your corporate artifactory
        cmd = f"pip install {' '.join(missing_packages)} --index-url=https://artifactory.internal.cba/api/pypi/org.python.pypi/simple"
        subprocess.run(cmd, shell=True, check=True)
        print("Packages installed successfully!")
    else:
        print("All dependencies are installed.")

def start_server():
    """Start the FastAPI server"""
    print("\nStarting Quant Trading Platform...")
    print("Server will be available at: http://localhost:8000")
    print("Dashboard: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("\n" + "="*50)
    
    # Change to backend directory
    backend_path = Path(__file__).parent / "backend"
    os.chdir(backend_path)
    
    # Start the server
    try:
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open("http://localhost:8000")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start uvicorn server
        import uvicorn
        uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
        
    except KeyboardInterrupt:
        print("\n\nShutting down Quant Trading Platform...")
        print("Thanks for using the platform!")
    except Exception as e:
        print(f"\nError starting server: {e}")
        print("Please check the logs above for more details.")

def main():
    """Main startup function"""
    print("=" * 50)
    print("QUANT TRADING PLATFORM")
    print("=" * 50)
    print("Advanced Stock Screening & Backtesting Platform")
    print("")
    
    try:
        # Check if we're in the right directory
        if not os.path.exists("backend"):
            print("[ERROR] Please run this script from the project root directory")
            print("Expected structure: backend/, frontend/, start_server.py")
            sys.exit(1)
        
        check_dependencies()
        start_server()
        
    except Exception as e:
        print(f"[ERROR] Startup failed: {e}")
        print("Please check your Python environment and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()