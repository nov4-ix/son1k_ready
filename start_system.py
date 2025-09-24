#!/usr/bin/env python3
"""
Son1kVers3 System Startup Script
Quick test and deployment helper
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "requests", "httpx", 
        "pydantic", "bcrypt", "python-multipart"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def check_files():
    """Check if all required files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        "index.html",
        "main_production.py", 
        "requirements.txt",
        "Procfile"
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_server():
    """Test if the server starts correctly"""
    print("\n🚀 Testing server startup...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "main_production.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running and responding")
                return True
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Server not responding: {e}")
        
        # Kill the process
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
    
    return False

def main():
    """Main startup function"""
    print("🎵 Son1kVers3 System Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return False
    
    # Check files
    if not check_files():
        print("\n❌ File check failed")
        return False
    
    # Test server
    if not test_server():
        print("\n⚠️ Server test failed, but files are ready")
        print("You can still deploy manually with: python3 main_production.py")
    
    print("\n✅ System is ready!")
    print("\nTo start the server:")
    print("  python3 main_production.py")
    print("\nTo deploy to Railway:")
    print("  railway login")
    print("  railway up")
    
    return True

if __name__ == "__main__":
    main()

