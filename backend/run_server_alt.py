#!/usr/bin/env python3
"""
Alternative server launcher on different port
"""

import uvicorn
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("Starting Quant Trading Platform on port 8001...")
    print("Server: http://localhost:8001")
    print("Press Ctrl+C to stop")
    print("-" * 30)
    
    uvicorn.run(
        "api.main:app", 
        host="127.0.0.1", 
        port=8001, 
        reload=False,
        log_level="info"
    )