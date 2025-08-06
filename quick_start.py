#!/usr/bin/env python3
"""
Quick Start Script for Quant Trading Platform
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    print("=" * 50)
    print("QUANT TRADING PLATFORM - QUICK START")
    print("=" * 50)
    
    # Get current directory
    current_dir = Path(__file__).parent
    backend_dir = current_dir / "backend"
    
    if not backend_dir.exists():
        print("Error: Backend directory not found!")
        print(f"Looking for: {backend_dir}")
        return
    
    print("Starting server from:", backend_dir)
    print("Dashboard will open at: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Add to Python path
    sys.path.insert(0, str(backend_dir))
    
    try:
        # Open browser after delay
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8000")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Import and run
        import uvicorn
        uvicorn.run(
            "api.main:app", 
            host="127.0.0.1", 
            port=8000, 
            log_level="warning"  # Reduce log noise
        )
        
    except KeyboardInterrupt:
        print("\n\nShutting down Quant Trading Platform...")
        print("Thanks for using the platform!")
    except Exception as e:
        print(f"\nError: {e}")
        print("Try running: python backend/run_server.py")

if __name__ == "__main__":
    main()