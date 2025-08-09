#!/usr/bin/env python3
"""
Direct server launcher
"""

import uvicorn
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("Starting Quant Trading Platform...")
    print("Server: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("-" * 30)
    
    try:
        print("Loading API...")
        uvicorn.run(
            "api.main:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"Server startup error: {e}")
        input("Press Enter to exit...")