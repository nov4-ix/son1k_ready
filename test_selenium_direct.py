#!/usr/bin/env python3
"""
Direct test of Selenium automation without Celery
For debugging and validation
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.app.selenium_worker import SunoSeleniumWorker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_selenium_direct():
    """Test Selenium worker directly"""
    print("🧪 Testing Selenium Worker Directly...")
    
    # Test payload
    test_payload = {
        "prompt": "upbeat electronic music for testing automation",
        "instrumental": True,
        "style": "electronic"
    }
    
    worker = None
    try:
        # Initialize worker (headless=False for debugging)
        worker = SunoSeleniumWorker(headless=True)
        
        print("🚀 Setting up Chrome driver...")
        if not worker.setup_driver():
            print("❌ Driver setup failed")
            return False
        
        print("🌐 Loading Suno.com...")
        if not worker.load_suno_with_auth():
            print("❌ Failed to load Suno.com")
            return False
        
        print("🎵 Navigating to create page...")
        if not worker.navigate_to_create():
            print("❌ Failed to navigate to create page")
            return False
        
        print("🎼 Starting music generation...")
        result = worker.generate_music(test_payload)
        
        print(f"\n📋 Generation Result:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Error: {result.get('error', 'None')}")
        print(f"  Audio Files: {len(result.get('audio_files', []))}")
        
        if result.get('audio_files'):
            for i, file_info in enumerate(result['audio_files']):
                print(f"    File {i+1}: {file_info.get('filename', 'unknown')}")
                print(f"    Size: {file_info.get('file_size', 0)} bytes")
        
        if result.get('success'):
            print("✅ Selenium automation test PASSED")
            return True
        else:
            print("❌ Selenium automation test FAILED")
            return False
        
    except Exception as e:
        print(f"❌ Test exception: {e}")
        logger.exception("Test failed with exception")
        return False
        
    finally:
        if worker:
            print("🧹 Cleaning up...")
            worker.cleanup()

def test_component_loading():
    """Test individual components"""
    print("\n🔧 Testing Components...")
    
    try:
        # Test cookie manager
        from backend.app.cookie_manager import CookieManager
        cm = CookieManager()
        
        if cm.load_cookies():
            print("✅ Cookie manager: OK")
            summary = cm.get_cookie_summary()
            print(f"   Cookies loaded: {summary.get('count', 0)}")
        else:
            print("⚠️ Cookie manager: No cookies (expected)")
        
        # Test Selenium imports
        import undetected_chromedriver as uc
        from selenium import webdriver
        print("✅ Selenium imports: OK")
        
        # Test directory structure
        dirs = ['screenshots', 'generated_audio']
        for dir_name in dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                print(f"✅ Directory {dir_name}: OK")
            else:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ Directory {dir_name}: Created")
        
        print("✅ All components loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Selenium Direct Test\n")
    
    # Test components first
    if not test_component_loading():
        print("❌ Component test failed, aborting")
        sys.exit(1)
    
    # Run main test
    success = test_selenium_direct()
    
    if success:
        print("\n🎉 All tests PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Tests FAILED!")
        sys.exit(1)