#!/usr/bin/env python3
"""
Complete workflow test for the fixed Suno automation
Tests the entire pipeline from login to music generation
"""
import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from selenium_worker.browser_manager import BrowserManager
from selenium_worker.suno_automation import compose_and_create

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main test function"""
    print("🚀 COMPLETE WORKFLOW TEST")
    print("=" * 50)
    
    # Test configuration
    test_lyrics = """Neon rain over midnight streets
Engines hum, hearts don't sleep
Silver sparks in a violet sky
We ride the bass, we never die"""
    
    test_prompt = "cyberpunk neon synthwave, 120 BPM, dark & cinematic"
    
    # Environment setup
    os.environ.setdefault("SV_HEADLESS", "0")  # Visible for debugging
    os.environ.setdefault("SUNO_EMAIL", "soypepejaimes@gmail.com")
    os.environ.setdefault("SUNO_PASSWORD", "Nov4-ix90")
    
    profile_dir = os.path.join(os.getcwd(), ".selenium_profile")
    os.environ.setdefault("SV_CHROME_PROFILE_DIR", profile_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshots_dir = f"./selenium_artifacts/{timestamp}"
    
    logger.info(f"🎵 Test lyrics: {len(test_lyrics)} characters")
    logger.info(f"🎨 Test prompt: {test_prompt}")
    logger.info(f"📂 Profile dir: {profile_dir}")
    logger.info(f"📸 Screenshots: {screenshots_dir}")
    
    browser_manager = None
    
    try:
        # Step 1: Initialize browser
        logger.info("🌐 Initializing browser manager...")
        browser_manager = BrowserManager(
            headless=False,  # Visible for testing
            user_data_dir=profile_dir
        )
        
        driver = browser_manager.get_driver()
        driver.set_window_size(1280, 800)
        
        logger.info("✅ Browser initialized")
        
        # Step 2: Test login
        logger.info("🔐 Testing login...")
        login_success = browser_manager.ensure_logged_in()
        
        if not login_success:
            logger.error("❌ Login failed!")
            print("❌ LOGIN FAILED - Check credentials")
            return False
        
        logger.info("✅ Login successful")
        
        # Step 3: Execute compose and create workflow
        logger.info("🎯 Starting compose and create workflow...")
        start_time = time.time()
        
        result = compose_and_create(driver, test_lyrics, test_prompt, screenshots_dir)
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Workflow completed in {elapsed:.1f}s")
        
        # Step 4: Analyze results
        print("\\n📊 RESULTS ANALYSIS")
        print("=" * 30)
        
        print(f"✅ Overall success: {result.get('ok', False)}")
        print(f"📝 Lyrics filled: {result.get('lyrics_ok', False)}")
        print(f"🎨 Styles filled: {result.get('styles_ok', False)}")
        print(f"🚀 Creation started: {result.get('created', False)}")
        print(f"📸 Screenshots: {len(result.get('shots', []))}")
        
        # List screenshots
        for i, shot in enumerate(result.get('shots', []), 1):
            filename = os.path.basename(shot)
            print(f"  {i}. {filename}")
        
        # Check for success criteria
        success_criteria = [
            result.get('lyrics_ok', False),
            result.get('styles_ok', False),
            result.get('created', False)
        ]
        
        if all(success_criteria):
            print("\\n🎉 ALL TESTS PASSED!")
            print("✅ The Suno automation is working correctly")
            return True
        else:
            print("\\n❌ SOME TESTS FAILED")
            if not result.get('lyrics_ok'):
                print("  - Lyrics filling failed")
            if not result.get('styles_ok'):
                print("  - Styles filling failed")
            if not result.get('created'):
                print("  - Music creation not initiated")
            return False
        
    except KeyboardInterrupt:
        logger.info("👋 Test interrupted by user")
        return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        print(f"❌ FATAL ERROR: {e}")
        return False
        
    finally:
        # Cleanup
        if browser_manager:
            try:
                logger.info("🔍 Keeping browser open for inspection (30s)...")
                time.sleep(30)
                browser_manager.close()
            except:
                pass

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\\n🎯 VALIDATION COMPLETE - AUTOMATION IS READY!")
        sys.exit(0)
    else:
        print("\\n❌ VALIDATION FAILED - CHECK LOGS AND SCREENSHOTS")
        sys.exit(1)