#!/usr/bin/env python3
"""
Test server on a different port to verify the fix works
"""

import uvicorn
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    print("Starting test server on port 8002...")
    print("Test URL: http://localhost:8002")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    # Import the app
    from api.main import app
    
    # Run on different port
    uvicorn.run(app, host="127.0.0.1", port=8002)