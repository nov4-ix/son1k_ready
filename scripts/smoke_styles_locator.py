#!/usr/bin/env python3
"""
Smoke test for styles locator functionality
Tests the ability to find and distinguish lyrics vs styles editors
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from selenium_worker.browser_manager import BrowserManager
from selenium_worker.suno_automation import (
    ensure_on_create,
    ensure_logged_in,
    ensure_custom_tab,
    get_lyrics_card_and_textarea,
    get_styles_card,
    get_styles_editor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main smoke test"""
    print("🧪 SMOKE TEST: Styles Locator")
    print("=" * 40)
    
    # Configuration
    headless = os.environ.get("SV_HEADLESS", "1") == "1"
    profile_dir = os.environ.get("SV_CHROME_PROFILE_DIR", "")
    binary_location = os.environ.get("SV_CHROME_BINARY", "")
    
    browser_manager = None
    
    try:
        # Initialize browser
        print("🚀 Initializing browser...")
        
        browser_manager = BrowserManager(
            headless=headless,
            user_data_dir=profile_dir if profile_dir else None,
            binary_location=binary_location if binary_location else None
        )
        
        driver = browser_manager.get_driver()
        
        if not headless:
            driver.set_window_size(1280, 800)
        
        # Login
        print("🔐 Checking login...")
        if not ensure_logged_in(driver):
            print("❌ Login failed")
            return False
        
        print("✅ Login OK")
        
        # Navigate to create
        print("🎯 Navigating to create page...")
        if not ensure_on_create(driver):
            print("❌ Could not reach create page")
            return False
        
        print("✅ Create page OK")
        
        # Activate custom tab
        print("🎛️ Activating custom tab...")
        if not ensure_custom_tab(driver):
            print("❌ Could not activate custom tab")
            return False
        
        print("✅ Custom tab OK")
        
        # Get lyrics elements
        print("🎵 Locating lyrics elements...")
        lyrics_card, lyrics_textarea = get_lyrics_card_and_textarea(driver)
        
        if not lyrics_card:
            print("❌ Lyrics card not found")
            return False
        
        if not lyrics_textarea:
            print("❌ Lyrics textarea not found")
            return False
        
        print("✅ Lyrics OK: textarea found")
        
        # Get styles elements
        print("🎨 Locating styles elements...")
        styles_card = get_styles_card(driver, lyrics_card)
        
        if not styles_card:
            print("❌ Styles card not found")
            return False
        
        styles_editor = get_styles_editor(styles_card)
        
        if not styles_editor:
            print("❌ Styles editor not found")
            return False
        
        # Critical test: ensure they're different elements
        same_element = driver.execute_script(
            "return arguments[0] === arguments[1]", 
            styles_editor, 
            lyrics_textarea
        )
        
        if same_element:
            print("❌ CRITICAL ERROR: Styles editor is the same as lyrics textarea!")
            return False
        
        print("✅ Styles OK: editor found (not same node)")
        
        # Additional info
        lyrics_tag = lyrics_textarea.tag_name
        lyrics_placeholder = lyrics_textarea.get_attribute('placeholder') or 'N/A'
        
        styles_tag = styles_editor.tag_name
        styles_contenteditable = styles_editor.get_attribute('contenteditable')
        styles_placeholder = styles_editor.get_attribute('placeholder') or 'N/A'
        
        print(f"📋 Lyrics: <{lyrics_tag}> placeholder='{lyrics_placeholder[:30]}...'")
        print(f"📋 Styles: <{styles_tag}> contenteditable={styles_contenteditable} placeholder='{styles_placeholder[:30]}...'")
        
        print("🎉 ALL SMOKE TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False
        
    finally:
        if browser_manager:
            try:
                # Brief pause for inspection if visible
                if not headless:
                    print("🔍 Pausing for inspection...")
                    import time
                    time.sleep(5)
                
                browser_manager.close()
            except:
                pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)