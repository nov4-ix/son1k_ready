#!/usr/bin/env python3
"""
Login and Cache Session Script
Performs initial login to Suno.com and caches session for future use
"""
import os
import sys
import logging
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from selenium_worker.browser_manager import BrowserManager
from selenium_worker.suno_automation import ensure_on_create, ensure_logged_in

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main login and cache function"""
    logger.info("🔐 Starting login and session caching...")
    
    # Configuration
    headless = os.environ.get("SV_HEADLESS", "0") == "1"
    profile_dir = os.environ.get("SV_CHROME_PROFILE_DIR", "")
    
    if not profile_dir:
        logger.error("❌ SV_CHROME_PROFILE_DIR environment variable is required")
        sys.exit(1)
    
    logger.info(f"📂 Profile directory: {profile_dir}")
    logger.info(f"🌐 Headless mode: {headless}")
    
    browser_manager = None
    
    try:
        # Initialize browser with persistent profile
        logger.info("🚀 Initializing browser with persistent profile...")
        
        browser_manager = BrowserManager(
            headless=headless,
            user_data_dir=profile_dir
        )
        
        driver = browser_manager.get_driver()
        
        if not headless:
            driver.set_window_size(1280, 800)
        
        # Navigate to Suno
        logger.info("🎯 Navigating to Suno.com...")
        if not ensure_on_create(driver):
            logger.error("❌ Failed to navigate to Suno create page")
            sys.exit(1)
        
        # Attempt login
        logger.info("🔑 Attempting login...")
        if not ensure_logged_in(driver):
            logger.error("❌ Login failed or was cancelled")
            sys.exit(1)
        
        # Verify login by navigating to create page again
        logger.info("✅ Login successful - verifying...")
        if not ensure_on_create(driver):
            logger.warning("⚠️ Could not navigate to create page after login")
        
        logger.info("🎉 Login completed and session cached!")
        logger.info("💾 Session is now saved in the browser profile")
        logger.info("🔄 Future runs will use the cached session")
        
        if not headless:
            logger.info("🔍 Browser will remain open for verification...")
            logger.info("✋ Press Ctrl+C to close when ready")
            
            try:
                # Keep browser open for manual verification
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("👋 User requested shutdown")
        
    except KeyboardInterrupt:
        logger.info("👋 Login process interrupted")
        
    except Exception as e:
        logger.error(f"❌ Login process failed: {e}")
        sys.exit(1)
        
    finally:
        # Note: We intentionally don't close the browser automatically
        # to allow the user to verify the login was successful
        logger.info("✅ Login script completed")

if __name__ == "__main__":
    main()