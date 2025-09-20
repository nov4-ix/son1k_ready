#!/usr/bin/env python3
"""
Production CLI Runner for Suno Music Creation
Handles complete workflow from login to audio generation with backend integration
"""
import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from selenium_worker.browser_manager import BrowserManager
from selenium_worker.suno_automation import (
    ensure_on_create, ensure_logged_in, ensure_custom_tab,
    get_lyrics_card_and_textarea, get_styles_card, get_styles_editor,
    write_textarea, write_contenteditable, read_value,
    wait_captcha_if_any, wait_captcha_if_any_with_notifications, wait_for_generation_and_fetch_audio
)
from selenium_worker.click_utils import click_create_when_enabled
from app.integrations.son1k_notify import notify_frontend, prepare_notification_payload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main CLI runner with complete workflow"""
    parser = argparse.ArgumentParser(description="Create music on Suno.com with full automation")
    parser.add_argument("--lyrics", help="Song lyrics (overrides SV_LYRICS env var)")
    parser.add_argument("--prompt", help="Style prompt (overrides SV_PROMPT env var)")
    parser.add_argument("--session-id", help="Session identifier")
    parser.add_argument("--timeout", type=int, default=300, help="Overall timeout in seconds")
    
    args = parser.parse_args()
    
    # Get configuration from environment
    lyrics = args.lyrics or os.environ.get("SV_LYRICS", "").strip()
    prompt = args.prompt or os.environ.get("SV_PROMPT", "").strip()
    session_id = args.session_id
    
    # Browser configuration
    headless = os.environ.get("SV_HEADLESS", "0") == "1"
    profile_dir = os.environ.get("SV_CHROME_PROFILE_DIR", "")
    no_quit = os.environ.get("SV_NO_QUIT", "0") == "1"
    frontend_push = os.environ.get("SON1K_FRONTEND_PUSH", "0") == "1"
    
    # Screenshots directory and job ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshots_dir = f"./selenium_artifacts/{timestamp}"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Generate unique job ID for CAPTCHA tracking
    job_id = f"suno_{timestamp}_{session_id or 'auto'}"
    
    # Validate inputs
    if not lyrics:
        logger.error("❌ No lyrics provided. Set SV_LYRICS env var or use --lyrics")
        result = {"success": False, "error": "No lyrics provided"}
        print(json.dumps(result))
        sys.exit(1)
    
    if not prompt:
        logger.error("❌ No prompt provided. Set SV_PROMPT env var or use --prompt")
        result = {"success": False, "error": "No prompt provided"}
        print(json.dumps(result))
        sys.exit(1)
    
    logger.info("🎵 Starting Suno music creation")
    logger.info(f"📝 Lyrics: {len(lyrics)} characters")
    logger.info(f"🎨 Prompt: {prompt[:50]}...")
    logger.info(f"🌐 Headless: {headless}")
    logger.info(f"📸 Screenshots: {screenshots_dir}")
    logger.info(f"🔄 Frontend Push: {frontend_push}")
    
    browser_manager = None
    result = {"success": False, "error": "Not started"}
    
    try:
        # Step 1: Initialize browser
        logger.info("🚀 Initializing browser...")
        
        browser_manager = BrowserManager(
            headless=headless,
            user_data_dir=profile_dir if profile_dir else None
        )
        
        driver = browser_manager.get_driver()
        
        if not headless:
            driver.set_window_size(1280, 800)
        
        def take_screenshot(filename):
            """Helper for screenshots"""
            path = os.path.join(screenshots_dir, filename)
            try:
                driver.save_screenshot(path)
                logger.info(f"📸 Screenshot: {filename}")
            except Exception as e:
                logger.warning(f"⚠️ Screenshot failed: {e}")
        
        # Step 2: Ensure on create page
        take_screenshot("00_loaded.png")
        
        if not ensure_on_create(driver):
            take_screenshot("ZZ_failed_navigate.png")
            result = {"success": False, "error": "Failed to navigate to create page"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        # Step 3: Ensure logged in
        if not ensure_logged_in(driver):
            take_screenshot("ZZ_failed_login.png")
            result = {"success": False, "error": "Failed to login"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        logger.info("✅ Login successful")
        
        # Step 4: Ensure on create page again (OAuth might redirect)
        if not ensure_on_create(driver):
            take_screenshot("ZZ_failed_navigate_post_login.png")
            result = {"success": False, "error": "Failed to navigate to create page after login"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        # Step 5: Activate Custom tab
        if not ensure_custom_tab(driver):
            take_screenshot("ZZ_failed_custom.png")
            result = {"success": False, "error": "Failed to activate Custom tab"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        take_screenshot("01_custom.png")
        
        # Step 6: Fill lyrics
        lyrics_card, lyrics_textarea = get_lyrics_card_and_textarea(driver)
        if not lyrics_card or not lyrics_textarea:
            take_screenshot("ZZ_failed_lyrics_elements.png")
            result = {"success": False, "error": "Failed to find lyrics elements"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        if not write_textarea(driver, lyrics_textarea, lyrics):
            take_screenshot("ZZ_failed_lyrics_write.png")
            result = {"success": False, "error": "Failed to write lyrics"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        take_screenshot("02_lyrics.png")
        
        # Verify lyrics
        lyrics_value = read_value(lyrics_textarea)
        if not lyrics_value.strip():
            take_screenshot("ZZ_lyrics_empty.png")
            result = {"success": False, "error": "Lyrics field is empty after writing"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        logger.info(f"✅ Lyrics written: {len(lyrics_value)} characters")
        
        # Step 7: Fill styles
        styles_card = get_styles_card(driver, lyrics_card)
        if not styles_card:
            take_screenshot("ZZ_failed_styles_card.png")
            result = {"success": False, "error": "Failed to find styles card"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        take_screenshot("02b_styles_card.png")
        
        styles_editor = get_styles_editor(styles_card)
        if not styles_editor:
            take_screenshot("ZZ_failed_styles_editor.png")
            result = {"success": False, "error": "Failed to find styles editor"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        # Safety check: ensure different elements
        if driver.execute_script("return arguments[0] === arguments[1]", styles_editor, lyrics_textarea):
            take_screenshot("ZZ_same_editor_error.png")
            result = {"success": False, "error": "Styles editor is the same as lyrics textarea"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        # Write styles
        is_contenteditable = styles_editor.get_attribute('contenteditable') == 'true'
        if is_contenteditable:
            write_success = write_contenteditable(driver, styles_editor, prompt)
        else:
            write_success = write_textarea(driver, styles_editor, prompt)
        
        if not write_success:
            take_screenshot("ZZ_failed_styles_write.png")
            result = {"success": False, "error": "Failed to write styles"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        take_screenshot("03_styles.png")
        
        # Verify styles
        styles_value = read_value(styles_editor)
        if not styles_value.strip():
            take_screenshot("ZZ_styles_empty.png")
            result = {"success": False, "error": "Styles field is empty after writing"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        logger.info(f"✅ Styles written: {len(styles_value)} characters")
        
        # Double-check lyrics didn't disappear
        lyrics_check = read_value(lyrics_textarea)
        if not lyrics_check.strip():
            take_screenshot("ZZ_lyrics_disappeared.png")
            result = {"success": False, "error": "Lyrics disappeared after writing styles"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        # Step 8: Wait for captcha if any (with enhanced notifications)
        if not wait_captcha_if_any_with_notifications(driver, job_id, max_wait_seconds=300, screenshot_callback=take_screenshot):
            take_screenshot("ZZ_captcha_timeout.png")
            result = {"success": False, "error": "Captcha timeout", "job_id": job_id}
            print(json.dumps(result))
            if not no_quit:
                return
        
        # Step 9: Click Create button
        if not click_create_when_enabled(driver, lyrics_textarea, styles_editor, timeout=120, screenshot_cb=take_screenshot):
            take_screenshot("ZZ_create_failed.png")
            result = {"success": False, "error": "Failed to click Create button"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        logger.info("✅ Create button clicked successfully")
        
        # Step 10: Wait for generation and fetch audio
        artifacts = wait_for_generation_and_fetch_audio(driver, timeout=args.timeout)
        
        if not artifacts:
            take_screenshot("ZZ_no_audio.png")
            result = {"success": False, "error": "No real audio artifacts generated"}
            print(json.dumps(result))
            if not no_quit:
                return
        
        logger.info(f"🎉 Generation completed: {len(artifacts)} artifacts")
        
        # Step 11: Prepare result
        result = {
            "success": True,
            "message": "Music generation completed successfully",
            "artifacts": artifacts,
            "lyrics": lyrics,
            "prompt": prompt,
            "session_id": session_id,
            "job_id": job_id,
            "screenshots_dir": screenshots_dir,
            "total_tracks": len(artifacts)
        }
        
        # Step 12: Notify frontend if enabled
        if frontend_push:
            logger.info("📡 Notifying frontend...")
            notification_payload = prepare_notification_payload(lyrics, prompt, artifacts, session_id)
            
            if notify_frontend(notification_payload):
                logger.info("✅ Frontend notified successfully")
                result["frontend_notified"] = True
            else:
                logger.warning("⚠️ Frontend notification failed")
                result["frontend_notified"] = False
        
        # Output final result
        print(json.dumps(result, indent=2))
        
    except KeyboardInterrupt:
        logger.info("👋 Interrupted by user")
        result = {"success": False, "error": "Interrupted by user"}
        print(json.dumps(result))
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        result = {"success": False, "error": str(e)}
        print(json.dumps(result))
        
        # Take emergency screenshot
        try:
            if browser_manager and browser_manager.driver:
                emergency_path = os.path.join(screenshots_dir, "ZZ_emergency.png")
                browser_manager.driver.save_screenshot(emergency_path)
        except:
            pass
    
    finally:
        # Cleanup with respect to SV_NO_QUIT
        if browser_manager:
            try:
                if no_quit:
                    logger.info("🔍 Keeping browser open (SV_NO_QUIT=1)...")
                    logger.info("📂 Screenshots saved in: " + screenshots_dir)
                    
                    # Keep the script alive but don't block indefinitely
                    import time
                    time.sleep(5)
                    logger.info("✅ Script completed - browser remains open")
                else:
                    browser_manager.close()
            except Exception as e:
                logger.warning(f"⚠️ Cleanup warning: {e}")
    
    # Exit with appropriate code
    if result.get("success"):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()