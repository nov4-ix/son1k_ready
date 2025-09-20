#!/usr/bin/env python3
"""
Simple script to start the Selenium Worker
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from selenium_worker.worker_service import main

if __name__ == "__main__":
    print("🚀 Starting Son1k Selenium Worker...")
    print("📧 Account: soypepejaimes@gmail.com")
    print("🔗 Backend: http://localhost:8000")
    print("⚠️  Press Ctrl+C to stop")
    print("-" * 50)
    
    # Set default arguments for production
    if "--backend-url" not in sys.argv:
        sys.argv.extend(["--backend-url", "http://localhost:8000"])
    
    if "--headless" not in sys.argv and "--visible" not in sys.argv:
        sys.argv.append("--headless")  # Default to headless
    
    if "--poll-interval" not in sys.argv:
        sys.argv.extend(["--poll-interval", "30"])
    
    # Start the worker
    main()