#!/usr/bin/env python3
"""
Test script to validate Suno automation fixes
Tests the complete workflow with enhanced debugging and real music detection
"""
import sys
import time
import logging
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from selenium_worker.browser_manager import BrowserManager
from selenium_worker.suno_automation import SunoAutomation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_suno_automation_fixes():
    """Test the fixed Suno automation workflow"""
    logger.info("🚀 Starting Suno automation test with fixes...")
    
    # Test data
    test_job = {
        "prompt": "Create a peaceful acoustic guitar instrumental with gentle melodies",
        "lyrics": "",
        "mode": "instrumental", 
        "style": "acoustic",
        "user_plan": "free",
        "priority": 5
    }
    
    browser_manager = None
    suno_automation = None
    
    try:
        # Step 1: Initialize browser with enhanced logging
        logger.info("🌐 Initializing browser manager...")
        browser_manager = BrowserManager(headless=False)  # Visible for debugging
        browser_manager.setup_driver()
        
        # Step 2: Initialize Suno automation
        logger.info("🎵 Initializing Suno automation...")
        suno_automation = SunoAutomation(browser_manager)
        
        # Step 3: Test login
        logger.info("🔐 Testing Suno login...")
        login_success = browser_manager.ensure_logged_in()
        if not login_success:
            logger.error("❌ Login failed!")
            return False
        
        logger.info("✅ Login successful")
        
        # Step 4: Navigate to create page
        logger.info("📝 Navigating to create page...")
        nav_success = browser_manager.navigate_to_create()
        if not nav_success:
            logger.error("❌ Navigation to create page failed!")
            return False
        
        logger.info("✅ Navigation successful")
        time.sleep(3)  # Allow page to load
        
        # Take screenshot of create page
        browser_manager.take_screenshot("create_page_loaded.png")
        
        # Step 5: Test form filling
        logger.info("📝 Testing form filling...")
        form_success = suno_automation._fill_generation_form(test_job)
        if not form_success:
            logger.error("❌ Form filling failed!")
            browser_manager.take_screenshot("form_fill_failed.png")
            return False
        
        logger.info("✅ Form filled successfully")
        time.sleep(2)
        
        # Take screenshot after form filling
        browser_manager.take_screenshot("form_filled.png")
        
        # Step 6: Test submission
        logger.info("🚀 Testing form submission...")
        submit_success = suno_automation._submit_generation()
        if not submit_success:
            logger.error("❌ Form submission failed!")
            browser_manager.take_screenshot("submit_failed.png")
            return False
        
        logger.info("✅ Form submitted successfully")
        
        # Take screenshot after submission
        browser_manager.take_screenshot("generation_started.png")
        
        # Step 7: Wait for completion (shorter timeout for testing)
        logger.info("⏳ Waiting for generation completion...")
        timeout = 120  # 2 minutes for testing
        results = suno_automation._wait_for_generation_completion(timeout=timeout)
        
        # Step 8: Analyze results
        if results.get("success"):
            logger.info("🎉 GENERATION SUCCESSFUL!")
            logger.info(f"📊 Audio URLs found: {len(results.get('audio_urls', []))}")
            
            for i, url in enumerate(results.get('audio_urls', [])):
                logger.info(f"  🎵 Audio {i+1}: {url}")
                
                # Validate URL is not placeholder
                if suno_automation._is_placeholder_audio(url):
                    logger.warning(f"⚠️ Audio {i+1} is a placeholder!")
                else:
                    logger.info(f"✅ Audio {i+1} is REAL music!")
            
            # Save results to file
            results_file = f"test_results_{int(time.time())}.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"💾 Results saved to {results_file}")
            
            return True
            
        else:
            logger.error(f"❌ Generation failed: {results.get('error')}")
            browser_manager.take_screenshot("generation_failed.png")
            return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        if browser_manager:
            browser_manager.take_screenshot("test_exception.png")
        return False
        
    finally:
        # Cleanup
        if browser_manager:
            logger.info("🧹 Cleaning up...")
            # Keep browser open for a moment to inspect
            input("Press Enter to close browser and exit...")
            browser_manager.close()

def test_placeholder_detection():
    """Test the placeholder detection function"""
    logger.info("🔍 Testing placeholder detection...")
    
    browser_manager = BrowserManager(headless=True)
    browser_manager.setup_driver()
    suno_automation = SunoAutomation(browser_manager)
    
    test_urls = [
        "https://cdn1.suno.ai/sil-100.mp3",  # Placeholder
        "https://cdn1.suno.ai/silence.mp3",  # Placeholder
        "https://cdn1.suno.ai/12345abcd-song.mp3",  # Real
        "https://cdn1.suno.ai/generated-music-67890.mp3",  # Real
        "https://cdn1.suno.ai/temp-loading.mp3",  # Placeholder
        "",  # Empty
        None  # None
    ]
    
    for url in test_urls:
        is_placeholder = suno_automation._is_placeholder_audio(url)
        logger.info(f"URL: {url} -> Placeholder: {is_placeholder}")
    
    browser_manager.close()

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Suno automation fixes")
    parser.add_argument("--test-type", choices=["full", "placeholder"], 
                       default="full", help="Type of test to run")
    
    args = parser.parse_args()
    
    try:
        if args.test_type == "placeholder":
            test_placeholder_detection()
        else:
            success = test_suno_automation_fixes()
            if success:
                logger.info("🎉 ALL TESTS PASSED!")
                sys.exit(0)
            else:
                logger.error("❌ TESTS FAILED!")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()