#!/usr/bin/env python3
"""
Robust Suno.com automation module
Handles navigation, form filling, and creation with enhanced reliability
"""
import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
import json
from urllib.parse import urlparse

from .click_utils import click_create_when_enabled, _safe_body_click, _nudge_validation

logger = logging.getLogger(__name__)

def ensure_on_create(driver: webdriver.Chrome, timeout: int = 30) -> bool:
    """Navigate to create page with multiple retry strategies"""
    logger.info("🎯 Navigating to Suno create page...")
    
    for attempt in range(5):
        try:
            current_url = driver.current_url
            logger.info(f"📍 Attempt {attempt + 1}/5 - Current URL: {current_url}")
            
            # If starting from about:blank or chrome://, open new tab
            if current_url.startswith(('about:', 'chrome://', 'data:')):
                logger.info("🆕 Opening new tab from blank page...")
                driver.execute_script("window.open('about:blank', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
            
            # Navigate to create page
            driver.get("https://suno.com/create")
            
            # Wait for page to be fully loaded
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Wait for URL to contain /create
            try:
                WebDriverWait(driver, 10).until(
                    EC.url_contains('/create')
                )
            except TimeoutException:
                logger.warning(f"⚠️ URL doesn't contain /create: {driver.current_url}")
            
            # Check if we're successfully on create page
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            
            create_indicators = [
                "/create" in current_url,
                "custom" in page_source,
                "lyrics" in page_source,
                "song description" in page_source
            ]
            
            if any(create_indicators):
                logger.info(f"✅ Successfully on create page: {current_url}")
                return True
            
            logger.warning(f"⚠️ Not on create page yet, attempt {attempt + 1}/5")
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    
    logger.error("❌ Failed to reach create page after 5 attempts")
    return False

def ensure_logged_in(driver: webdriver.Chrome, timeout: int = 180) -> bool:
    """Ensure user is logged in with OAuth/passkey support"""
    logger.info("🔐 Checking login status...")
    
    try:
        # Check if already logged in by looking for user sidebar/menu
        user_indicators = [
            "[data-testid='user-menu']",
            ".user-menu",
            "button[aria-label*='user' i]",
            "img[alt*='profile' i]",
            "button:has(img[alt*='avatar' i])"
        ]
        
        for selector in user_indicators:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info("✅ Already logged in (found user menu)")
                    return True
            except:
                continue
        
        # Check for typical logged-in page content
        page_source = driver.page_source.lower()
        if any(indicator in page_source for indicator in ["logout", "sign out", "profile", "dashboard"]):
            logger.info("✅ Already logged in (found logged-in content)")
            return True
        
        # Need to login - look for Sign In button
        logger.info("🚪 Need to login - looking for Sign In button...")
        
        signin_selectors = [
            "//button[contains(translate(text(), 'SIGN IN', 'sign in'), 'sign in')]",
            "//a[contains(translate(text(), 'SIGN IN', 'sign in'), 'sign in')]",
            "//button[contains(translate(text(), 'LOGIN', 'login'), 'login')]",
            "//a[contains(translate(text(), 'LOGIN', 'login'), 'login')]"
        ]
        
        signin_button = None
        for xpath in signin_selectors:
            try:
                signin_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                break
            except TimeoutException:
                continue
        
        if not signin_button:
            logger.error("❌ Could not find Sign In button")
            return False
        
        # Click Sign In
        signin_button.click()
        time.sleep(3)
        
        # Look for Google sign-in option
        logger.info("🔍 Looking for Google sign-in option...")
        
        google_selectors = [
            "//button[contains(translate(text(), 'GOOGLE', 'google'), 'google')]",
            "//button[contains(@aria-label, 'google' i)]",
            "//button[contains(@title, 'google' i)]",
            "[data-provider='google']",
            "button[aria-label*='google' i]"
        ]
        
        google_button = None
        for selector in google_selectors:
            try:
                if selector.startswith("//"):
                    google_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    google_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                break
            except TimeoutException:
                continue
        
        if not google_button:
            logger.warning("⚠️ Could not find Google sign-in button - manual login required")
            return _wait_for_manual_login(driver, timeout)
        
        # Click Google sign-in
        logger.info("🔄 Clicking Google sign-in...")
        google_button.click()
        time.sleep(5)
        
        # Handle OAuth window
        return _handle_oauth_flow(driver, timeout)
        
    except Exception as e:
        logger.error(f"❌ Login process failed: {e}")
        return False

def _wait_for_manual_login(driver: webdriver.Chrome, timeout: int) -> bool:
    """Wait for manual login completion"""
    logger.info("⏳ Waiting for manual login (passkey/OAuth)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            current_url = driver.current_url
            
            # Check if back on Suno domain and logged in
            if "suno.com" in current_url and "/create" in current_url:
                # Verify login by looking for user indicators
                page_source = driver.page_source.lower()
                if any(indicator in page_source for indicator in ["logout", "profile", "dashboard"]):
                    logger.info("✅ Manual login completed successfully")
                    return True
            
            time.sleep(2)
            
        except Exception as e:
            logger.debug(f"Error during manual login wait: {e}")
            time.sleep(2)
    
    logger.error("❌ Manual login timeout")
    return False

def _handle_oauth_flow(driver: webdriver.Chrome, timeout: int) -> bool:
    """Handle OAuth popup/redirect flow"""
    logger.info("🔄 Handling OAuth flow...")
    
    initial_handles = set(driver.window_handles)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            current_handles = set(driver.window_handles)
            new_handles = current_handles - initial_handles
            
            # Check for new OAuth window
            if new_handles:
                oauth_handle = list(new_handles)[0]
                logger.info("🪟 Switching to OAuth window...")
                driver.switch_to.window(oauth_handle)
                
                # Wait for OAuth completion (user interaction)
                return _wait_oauth_completion(driver, timeout - (time.time() - start_time))
            
            # Check current window for OAuth indicators
            current_url = driver.current_url
            title = driver.title.lower()
            
            oauth_indicators = [
                "accounts.google.com" in current_url,
                "sign in" in title,
                "iniciar sesión" in title,
                "login" in title
            ]
            
            if any(oauth_indicators):
                logger.info("🔑 On OAuth page - waiting for completion...")
                return _wait_oauth_completion(driver, timeout - (time.time() - start_time))
            
            # Check if already completed and back on Suno
            if "suno.com" in current_url:
                logger.info("✅ OAuth completed - back on Suno")
                return True
            
            time.sleep(2)
            
        except Exception as e:
            logger.debug(f"Error in OAuth flow: {e}")
            time.sleep(2)
    
    logger.error("❌ OAuth flow timeout")
    return False

def _wait_oauth_completion(driver: webdriver.Chrome, timeout: int) -> bool:
    """Wait for OAuth completion and return to Suno"""
    logger.info("⏳ Waiting for OAuth completion...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            current_url = driver.current_url
            
            # Check if back on Suno domain
            if "suno.com" in current_url:
                logger.info("🎯 Returned to Suno - forcing navigation to /create...")
                
                # Force navigation to create page
                driver.get("https://suno.com/create")
                time.sleep(3)
                
                # Verify login success
                page_source = driver.page_source.lower()
                if any(indicator in page_source for indicator in ["logout", "profile", "custom", "lyrics"]):
                    logger.info("✅ OAuth login completed successfully")
                    return True
            
            time.sleep(2)
            
        except Exception as e:
            logger.debug(f"Error waiting for OAuth completion: {e}")
            time.sleep(2)
    
    logger.error("❌ OAuth completion timeout")
    return False

def ensure_custom_tab(driver: webdriver.Chrome, timeout: int = 20) -> bool:
    """Ensure Custom tab is active"""
    try:
        logger.info("🎛️ Activating Custom tab...")
        
        # Look for Custom tab/button
        custom_selectors = [
            "//button[contains(translate(text(), 'CUSTOM', 'custom'), 'custom')]",
            "//div[contains(translate(text(), 'CUSTOM', 'custom'), 'custom')]",
            "//span[contains(translate(text(), 'CUSTOM', 'custom'), 'custom')]/ancestor::button",
            "[data-testid*='custom']",
            ".custom-tab",
            "button[aria-selected='false']:contains('Custom')"
        ]
        
        for selector in custom_selectors:
            try:
                if selector.startswith("//"):
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    if ":contains(" in selector:
                        # Convert to XPath for text matching
                        text = selector.split(":contains('")[1].split("')")[0]
                        xpath = f"//button[contains(translate(text(), 'CUSTOM', 'custom'), '{text.lower()}')]"
                        element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                    else:
                        element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                
                # Scroll into view and click
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                element.click()
                time.sleep(2)
                
                logger.info("✅ Custom tab activated")
                return True
                
            except TimeoutException:
                continue
        
        # Check if already on custom mode
        page_source = driver.page_source.lower()
        if "lyrics" in page_source and ("style" in page_source or "description" in page_source):
            logger.info("✅ Already in Custom mode")
            return True
        
        logger.warning("⚠️ Could not activate Custom tab")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error activating Custom tab: {e}")
        return False

def get_lyrics_card_and_textarea(driver: webdriver.Chrome, timeout: int = 15) -> Tuple[Optional[WebElement], Optional[WebElement]]:
    """Locate lyrics card and its textarea"""
    try:
        logger.info("🎵 Locating lyrics card and textarea...")
        
        # Method 1: Find by "Lyrics" header
        lyrics_headers = [
            "//h3[contains(translate(text(), 'LYRICS', 'lyrics'), 'lyrics')]",
            "//h2[contains(translate(text(), 'LYRICS', 'lyrics'), 'lyrics')]", 
            "//div[contains(translate(text(), 'LYRICS', 'lyrics'), 'lyrics')]",
            "//span[contains(translate(text(), 'LYRICS', 'lyrics'), 'lyrics')]"
        ]
        
        lyrics_card = None
        for xpath in lyrics_headers:
            try:
                header = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                # Find parent card container
                lyrics_card = driver.execute_script("""
                    let el = arguments[0];
                    while (el && el.parentElement) {
                        let classes = el.className || '';
                        if (classes.toLowerCase().includes('card') || 
                            el.tagName === 'SECTION' || 
                            el.hasAttribute('data-testid')) {
                            return el;
                        }
                        el = el.parentElement;
                    }
                    return null;
                """, header)
                
                if lyrics_card:
                    break
            except TimeoutException:
                continue
        
        # Method 2: Find by textarea placeholder
        if not lyrics_card:
            try:
                textarea = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='lyrics' i]"))
                )
                lyrics_card = driver.execute_script("""
                    let el = arguments[0];
                    while (el && el.parentElement) {
                        let classes = el.className || '';
                        if (classes.toLowerCase().includes('card') || 
                            el.tagName === 'SECTION') {
                            return el;
                        }
                        el = el.parentElement;
                    }
                    return el.parentElement;
                """, textarea)
            except TimeoutException:
                pass
        
        if not lyrics_card:
            logger.error("❌ Could not find lyrics card")
            return None, None
        
        # Find textarea within the card
        textarea_selectors = [
            "textarea[placeholder*='Write some lyrics' i]",
            "textarea[placeholder*='lyrics' i]",
            "textarea[placeholder*='Enter lyrics' i]",
            "textarea"
        ]
        
        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = lyrics_card.find_element(By.CSS_SELECTOR, selector)
                if textarea:
                    break
            except:
                continue
        
        if not textarea:
            logger.error("❌ Could not find lyrics textarea")
            return lyrics_card, None
        
        logger.info("✅ Found lyrics card and textarea")
        return lyrics_card, textarea
        
    except Exception as e:
        logger.error(f"❌ Error finding lyrics elements: {e}")
        return None, None

def get_styles_card(driver: webdriver.Chrome, lyrics_card: WebElement, timeout: int = 15) -> Optional[WebElement]:
    """Get styles/description card, trying multiple methods"""
    try:
        logger.info("🎨 Locating styles card...")
        
        # Method 1: Find by "Styles" or "Song Description" header
        styles_headers = [
            "//h3[contains(translate(text(), 'STYLES', 'styles'), 'styles')]",
            "//h3[contains(translate(text(), 'SONG DESCRIPTION', 'song description'), 'song description')]",
            "//h2[contains(translate(text(), 'STYLES', 'styles'), 'styles')]",
            "//div[contains(translate(text(), 'STYLE', 'style'), 'style')]",
            "//span[contains(translate(text(), 'DESCRIPTION', 'description'), 'description')]"
        ]
        
        for xpath in styles_headers:
            try:
                header = driver.find_element(By.XPATH, xpath)
                styles_card = driver.execute_script("""
                    let el = arguments[0];
                    while (el && el.parentElement) {
                        let classes = el.className || '';
                        if (classes.toLowerCase().includes('card') || 
                            el.tagName === 'SECTION') {
                            return el;
                        }
                        el = el.parentElement;
                    }
                    return null;
                """, header)
                
                if styles_card:
                    logger.info("✅ Found styles card by header")
                    return styles_card
            except:
                continue
        
        # Method 2: Find by placeholder text
        try:
            placeholder_selectors = [
                "textarea[placeholder*='Hip-hop, R&B, upbeat' i]",
                "textarea[placeholder*='genre' i]",
                "textarea[placeholder*='style' i]",
                "div[placeholder*='Hip-hop' i]"
            ]
            
            for selector in placeholder_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    styles_card = driver.execute_script("""
                        let el = arguments[0];
                        while (el && el.parentElement) {
                            let classes = el.className || '';
                            if (classes.toLowerCase().includes('card') || 
                                el.tagName === 'SECTION') {
                                return el;
                            }
                            el = el.parentElement;
                        }
                        return null;
                    """, element)
                    
                    if styles_card:
                        logger.info("✅ Found styles card by placeholder")
                        return styles_card
                except:
                    continue
        except:
            pass
        
        # Method 3: Positional fallback - next card sibling after lyrics
        try:
            styles_card = driver.execute_script("""
                const lyricsCard = arguments[0];
                let next = lyricsCard.nextElementSibling;
                
                while (next) {
                    const classes = next.className || '';
                    if (classes.toLowerCase().includes('card') || 
                        next.tagName === 'SECTION' ||
                        next.tagName === 'DIV') {
                        // Check if it contains form elements
                        const hasTextarea = next.querySelector('textarea');
                        const hasContentEditable = next.querySelector('[contenteditable]');
                        const hasInput = next.querySelector('input[type="text"]');
                        
                        if (hasTextarea || hasContentEditable || hasInput) {
                            return next;
                        }
                    }
                    next = next.nextElementSibling;
                }
                return null;
            """, lyrics_card)
            
            if styles_card:
                logger.info("✅ Found styles card by position (fallback)")
                return styles_card
        except Exception as e:
            logger.debug(f"Positional fallback failed: {e}")
        
        logger.error("❌ Could not find styles card")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error finding styles card: {e}")
        return None

def get_styles_editor(styles_card: WebElement) -> Optional[WebElement]:
    """Get the styles editor (textarea or contenteditable)"""
    try:
        logger.info("📝 Locating styles editor...")
        
        # Method 1: Look for textarea first
        textarea_selectors = [
            "textarea[placeholder*='Hip-hop, R&B, upbeat' i]",
            "textarea[placeholder*='genre' i]",
            "textarea[placeholder*='style' i]",
            "textarea"
        ]
        
        for selector in textarea_selectors:
            try:
                editor = styles_card.find_element(By.CSS_SELECTOR, selector)
                if editor:
                    logger.info("✅ Found styles textarea editor")
                    return editor
            except:
                continue
        
        # Method 2: Look for contenteditable elements
        contenteditable_selectors = [
            "div[contenteditable='true']",
            "[role='textbox']",
            "[data-slate-editor='true']",
            "[contenteditable]"
        ]
        
        for selector in contenteditable_selectors:
            try:
                editor = styles_card.find_element(By.CSS_SELECTOR, selector)
                if editor:
                    logger.info("✅ Found styles contenteditable editor")
                    return editor
            except:
                continue
        
        logger.error("❌ Could not find styles editor")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error finding styles editor: {e}")
        return None

def write_textarea(driver: webdriver.Chrome, element: WebElement, text: str) -> bool:
    """Write text to textarea element"""
    try:
        # Clear and type
        element.clear()
        time.sleep(0.2)
        
        # Type character by character for more natural input
        for char in text:
            element.send_keys(char)
            time.sleep(0.02)  # Small delay between characters
        
        # Trigger events
        driver.execute_script("""
            const el = arguments[0];
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element)
        
        return True
    except Exception as e:
        logger.error(f"❌ Error writing to textarea: {e}")
        return False

def write_contenteditable(driver: webdriver.Chrome, element: WebElement, text: str) -> bool:
    """Write text to contenteditable element"""
    try:
        # Clear and set content using JavaScript
        driver.execute_script("""
            const el = arguments[0];
            const text = arguments[1];
            
            // Clear content
            el.innerText = '';
            el.focus();
            
            // Set new content
            el.innerText = text;
            
            // Dispatch events
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new Event('blur', { bubbles: true }));
        """, element, text)
        
        time.sleep(0.3)  # Allow time for re-render
        return True
    except Exception as e:
        logger.error(f"❌ Error writing to contenteditable: {e}")
        return False

def read_value(element: WebElement) -> str:
    """Read value from element (textarea or contenteditable)"""
    try:
        tag_name = element.tag_name.lower()
        if tag_name == 'textarea' or tag_name == 'input':
            return element.get_attribute('value') or ''
        else:
            return element.get_attribute('innerText') or element.text or ''
    except:
        return ''

def click_create_when_enabled(driver: webdriver.Chrome, timeout: int = 40) -> bool:
    """Click Create button when enabled"""
    try:
        logger.info("🚀 Looking for Create button...")
        
        create_xpaths = [
            "//button[contains(translate(text(), 'CREATE', 'create'), 'create') and not(@disabled) and not(@aria-disabled='true')]",
            "//button[contains(translate(text(), 'GENERATE', 'generate'), 'generate') and not(@disabled) and not(@aria-disabled='true')]"
        ]
        
        end_time = time.time() + timeout
        while time.time() < end_time:
            for xpath in create_xpaths:
                try:
                    button = driver.find_element(By.XPATH, xpath)
                    if button.is_enabled() and button.is_displayed():
                        # Scroll into view and click
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        button.click()
                        logger.info("✅ Create button clicked successfully")
                        return True
                except:
                    continue
            
            time.sleep(1)  # Wait before next attempt
        
        logger.error("❌ Create button not found or not enabled")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error clicking Create button: {e}")
        return False

def wait_captcha_if_any(driver: webdriver.Chrome, max_wait: int = 180) -> bool:
    """Wait for captcha to be resolved if present"""
    try:
        logger.info("🔍 Checking for captcha...")
        
        captcha_iframes = [
            "iframe[src*='hcaptcha']",
            "iframe[src*='recaptcha']", 
            "iframe[src*='turnstile']",
            "iframe[title*='captcha' i]"
        ]
        
        start_time = time.time()
        captcha_detected = False
        
        while time.time() - start_time < max_wait:
            # Check for captcha iframes
            for selector in captcha_iframes:
                try:
                    iframes = driver.find_elements(By.CSS_SELECTOR, selector)
                    if iframes:
                        if not captcha_detected:
                            logger.warning("⚠️ Captcha detected: Please solve it manually...")
                            captcha_detected = True
                        time.sleep(1)
                        break
                except:
                    continue
            else:
                # No captcha found
                if captcha_detected:
                    logger.info("✅ Captcha resolved")
                return True
            
            time.sleep(1)
        
        if captcha_detected:
            logger.error("❌ Captcha timeout")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking captcha: {e}")
        return True  # Continue anyway

def wait_for_generation_and_fetch_audio(driver: webdriver.Chrome, timeout: int = 180) -> List[Dict]:
    """
    Wait for generation completion and fetch real audio files
    
    Returns:
        List of audio artifacts with metadata
    """
    logger.info("⏳ Waiting for audio generation completion...")
    
    start_time = time.time()
    artifacts = []
    
    # Create artifacts directory
    timestamp = int(time.time())
    artifacts_dir = f"./artifacts/{timestamp}"
    os.makedirs(artifacts_dir, exist_ok=True)
    
    while time.time() - start_time < timeout:
        try:
            # Look for result cards/containers
            result_selectors = [
                ".track-card",
                ".song-card", 
                ".result-card",
                "[data-testid*='track']",
                "[data-testid*='song']",
                ".generation-result"
            ]
            
            result_elements = []
            for selector in result_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    result_elements.extend(elements)
                except:
                    continue
            
            if not result_elements:
                # Also check for generic containers with audio
                audio_containers = driver.find_elements(By.XPATH, "//*[.//audio or .//video or .//*[@src and contains(@src, '.mp3')]]")
                result_elements.extend(audio_containers)
            
            if result_elements:
                logger.info(f"🎵 Found {len(result_elements)} potential result elements")
                
                for i, element in enumerate(result_elements):
                    try:
                        # Extract audio URL from element
                        audio_url = _extract_audio_url_from_element(driver, element)
                        
                        if audio_url and not _is_placeholder_audio(audio_url):
                            # Extract metadata
                            title = _extract_title_from_element(element) or f"Generated_Song_{i+1}"
                            duration = _extract_duration_from_element(element)
                            
                            # Download audio file
                            local_path = _download_audio_file(audio_url, artifacts_dir, f"{title}_{timestamp}")
                            
                            if local_path:
                                # Get file size
                                file_size = os.path.getsize(local_path) if os.path.exists(local_path) else 0
                                
                                # Only include if file is substantial (>20KB)
                                if file_size > 20 * 1024:
                                    artifact = {
                                        "title": title,
                                        "url": audio_url,
                                        "local_path": local_path,
                                        "duration": duration,
                                        "size": file_size,
                                        "timestamp": timestamp
                                    }
                                    artifacts.append(artifact)
                                    logger.info(f"✅ Added real audio: {title} ({file_size} bytes)")
                                else:
                                    logger.warning(f"⚠️ Skipped small file: {local_path} ({file_size} bytes)")
                                    if os.path.exists(local_path):
                                        os.remove(local_path)
                        
                    except Exception as e:
                        logger.debug(f"Error processing result element {i}: {e}")
                        continue
                
                # If we found real artifacts, break
                if artifacts:
                    break
            
            # Check every 10 seconds
            time.sleep(10)
            elapsed = int(time.time() - start_time)
            logger.info(f"⏳ Still waiting for generation... {elapsed}s elapsed")
            
        except Exception as e:
            logger.debug(f"Error in generation wait loop: {e}")
            time.sleep(5)
    
    # Save metadata
    if artifacts:
        metadata_file = os.path.join(artifacts_dir, "metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump({
                "artifacts": artifacts,
                "generated_at": timestamp,
                "total_files": len(artifacts)
            }, f, indent=2)
        
        logger.info(f"💾 Saved {len(artifacts)} artifacts to {artifacts_dir}")
        logger.info(f"📄 Metadata saved: {metadata_file}")
    else:
        logger.warning("⚠️ No real audio artifacts found")
    
    return artifacts

def _extract_audio_url_from_element(driver: webdriver.Chrome, element: WebElement) -> Optional[str]:
    """Extract audio URL from a result element"""
    try:
        # Method 1: Direct audio/video elements
        audio_elements = element.find_elements(By.TAG_NAME, "audio")
        for audio in audio_elements:
            src = audio.get_attribute("src")
            if src and src.startswith("http"):
                return src
        
        video_elements = element.find_elements(By.TAG_NAME, "video")
        for video in video_elements:
            src = video.get_attribute("src")
            if src and src.startswith("http") and (".mp3" in src or ".wav" in src):
                return src
        
        # Method 2: Data attributes
        data_attrs = ["data-audio-url", "data-src", "data-track-url", "data-song-url"]
        for attr in data_attrs:
            url = element.get_attribute(attr)
            if url and url.startswith("http"):
                return url
        
        # Method 3: Links to audio files
        links = element.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if href and (".mp3" in href or ".wav" in href):
                return href
        
        # Method 4: JavaScript extraction
        url = driver.execute_script("""
            const el = arguments[0];
            
            // Check for React props
            for (let prop in el) {
                if (prop.startsWith('__reactInternalInstance') || prop.startsWith('_reactInternalInstance')) {
                    try {
                        const fiber = el[prop];
                        const props = fiber.memoizedProps || fiber.pendingProps;
                        if (props && props.audioUrl) return props.audioUrl;
                        if (props && props.src && props.src.includes('.mp3')) return props.src;
                    } catch(e) {}
                }
            }
            
            // Check for common audio URL patterns in element text/html
            const html = el.innerHTML;
            const matches = html.match(/https?:\\/\\/[^"'\\\\s]+\\.mp3/g);
            if (matches && matches.length > 0) {
                return matches[0];
            }
            
            return null;
        """, element)
        
        if url:
            return url
        
        return None
        
    except Exception as e:
        logger.debug(f"Error extracting audio URL: {e}")
        return None

def _extract_title_from_element(element: WebElement) -> Optional[str]:
    """Extract title from result element"""
    try:
        # Look for title in various elements
        title_selectors = [
            ".title", ".song-title", ".track-title", 
            "h1", "h2", "h3", ".name", ".track-name"
        ]
        
        for selector in title_selectors:
            try:
                title_element = element.find_element(By.CSS_SELECTOR, selector)
                title = title_element.text.strip()
                if title:
                    return title
            except:
                continue
        
        return None
        
    except Exception:
        return None

def _extract_duration_from_element(element: WebElement) -> Optional[str]:
    """Extract duration from result element"""
    try:
        duration_selectors = [".duration", ".time", ".length"]
        
        for selector in duration_selectors:
            try:
                duration_element = element.find_element(By.CSS_SELECTOR, selector)
                duration = duration_element.text.strip()
                if ":" in duration:  # Format like "2:30"
                    return duration
            except:
                continue
        
        return None
        
    except Exception:
        return None

def _download_audio_file(url: str, artifacts_dir: str, base_filename: str) -> Optional[str]:
    """Download audio file to artifacts directory"""
    try:
        logger.info(f"📥 Downloading audio: {url}")
        
        # Clean filename
        safe_filename = "".join(c for c in base_filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Determine extension
        if ".mp3" in url.lower():
            extension = ".mp3"
        elif ".wav" in url.lower():
            extension = ".wav"
        else:
            extension = ".mp3"  # Default
        
        local_path = os.path.join(artifacts_dir, f"{safe_filename}{extension}")
        
        # Download with timeout
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"✅ Downloaded: {local_path}")
        return local_path
        
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return None

def _is_placeholder_audio(url: str) -> bool:
    """Check if audio URL is a placeholder"""
    if not url:
        return True
    
    url_lower = url.lower()
    placeholder_patterns = [
        'sil-', 'silence', 'placeholder', 'temp', 'loading', 'empty', 'blank'
    ]
    
    return any(pattern in url_lower for pattern in placeholder_patterns)

def compose_and_create(driver: webdriver.Chrome, lyrics: str, prompt: str, screenshots_dir: str) -> Dict:
    """Main orchestration function"""
    result = {
        "ok": False,
        "lyrics_ok": False, 
        "styles_ok": False,
        "created": False,
        "shots": []
    }
    
    os.makedirs(screenshots_dir, exist_ok=True)
    
    try:
        # Step 1: Ensure on create page
        screenshot_path = os.path.join(screenshots_dir, "00_loaded.png")
        driver.save_screenshot(screenshot_path)
        result["shots"].append(screenshot_path)
        
        if not ensure_on_create(driver):
            screenshot_path = os.path.join(screenshots_dir, "ZZ_failed_navigate.png")
            driver.save_screenshot(screenshot_path)
            result["shots"].append(screenshot_path)
            return result
        
        # Step 2: Activate Custom tab
        if not ensure_custom_tab(driver):
            screenshot_path = os.path.join(screenshots_dir, "ZZ_failed_custom.png")
            driver.save_screenshot(screenshot_path)
            result["shots"].append(screenshot_path)
            return result
        
        screenshot_path = os.path.join(screenshots_dir, "01_custom.png")
        driver.save_screenshot(screenshot_path)
        result["shots"].append(screenshot_path)
        
        # Step 3: Get lyrics elements
        lyrics_card, lyrics_textarea = get_lyrics_card_and_textarea(driver)
        if not lyrics_card or not lyrics_textarea:
            screenshot_path = os.path.join(screenshots_dir, "ZZ_failed_lyrics_elements.png")
            driver.save_screenshot(screenshot_path)
            result["shots"].append(screenshot_path)
            return result
        
        # Step 4: Write lyrics
        if write_textarea(driver, lyrics_textarea, lyrics):
            time.sleep(0.5)
            # Verify lyrics were written
            lyrics_value = read_value(lyrics_textarea)
            if lyrics_value.strip():
                result["lyrics_ok"] = True
                logger.info(f"✅ Lyrics written: {len(lyrics_value)} characters")
            else:
                logger.error("❌ Lyrics not written properly")
        
        screenshot_path = os.path.join(screenshots_dir, "02_lyrics.png")
        driver.save_screenshot(screenshot_path)
        result["shots"].append(screenshot_path)
        
        # Step 5: Get styles elements
        styles_card = get_styles_card(driver, lyrics_card)
        if not styles_card:
            screenshot_path = os.path.join(screenshots_dir, "ZZ_failed_styles_card.png")
            driver.save_screenshot(screenshot_path)
            result["shots"].append(screenshot_path)
            return result
        
        screenshot_path = os.path.join(screenshots_dir, "02b_styles_card.png")
        driver.save_screenshot(screenshot_path)
        result["shots"].append(screenshot_path)
        
        styles_editor = get_styles_editor(styles_card)
        if not styles_editor:
            screenshot_path = os.path.join(screenshots_dir, "ZZ_failed_styles_editor.png")
            driver.save_screenshot(screenshot_path)
            result["shots"].append(screenshot_path)
            return result
        
        # Safety check: ensure styles editor is different from lyrics textarea
        if driver.execute_script("return arguments[0] === arguments[1]", styles_editor, lyrics_textarea):
            logger.error("❌ Styles editor is the same as lyrics textarea!")
            screenshot_path = os.path.join(screenshots_dir, "ZZ_same_editor_error.png")
            driver.save_screenshot(screenshot_path)
            result["shots"].append(screenshot_path)
            return result
        
        # Step 6: Write styles/prompt
        is_contenteditable = styles_editor.get_attribute('contenteditable') == 'true'
        write_success = False
        
        if is_contenteditable:
            write_success = write_contenteditable(driver, styles_editor, prompt)
        else:
            write_success = write_textarea(driver, styles_editor, prompt)
        
        if write_success:
            time.sleep(0.5)
            # Verify styles were written
            styles_value = read_value(styles_editor)
            if styles_value.strip():
                result["styles_ok"] = True
                logger.info(f"✅ Styles written: {len(styles_value)} characters")
                
                # Double-check lyrics didn't change
                lyrics_check = read_value(lyrics_textarea)
                if not lyrics_check.strip():
                    logger.error("❌ Lyrics disappeared after writing styles!")
                    result["lyrics_ok"] = False
            else:
                logger.error("❌ Styles not written properly")
        
        screenshot_path = os.path.join(screenshots_dir, "03_styles.png")
        driver.save_screenshot(screenshot_path)
        result["shots"].append(screenshot_path)
        
        # Step 7: Click Create if both fields have content
        if result["lyrics_ok"] and result["styles_ok"]:
            # Wait for any captcha
            if wait_captcha_if_any(driver):
                if click_create_when_enabled(driver):
                    result["created"] = True
                    result["ok"] = True
                    logger.info("🎉 Song creation initiated successfully!")
                    
                    screenshot_path = os.path.join(screenshots_dir, "04_create.png")
                    driver.save_screenshot(screenshot_path)
                    result["shots"].append(screenshot_path)
                else:
                    screenshot_path = os.path.join(screenshots_dir, "ZZ_failed_create_click.png")
                    driver.save_screenshot(screenshot_path)
                    result["shots"].append(screenshot_path)
            else:
                screenshot_path = os.path.join(screenshots_dir, "ZZ_captcha_timeout.png")
                driver.save_screenshot(screenshot_path)
                result["shots"].append(screenshot_path)
        else:
            logger.error("❌ Cannot create: lyrics_ok=%s, styles_ok=%s", result["lyrics_ok"], result["styles_ok"])
            screenshot_path = os.path.join(screenshots_dir, "ZZ_fields_not_ready.png")
            driver.save_screenshot(screenshot_path)
            result["shots"].append(screenshot_path)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Compose and create failed: {e}")
        screenshot_path = os.path.join(screenshots_dir, "ZZ_exception.png")
        try:
            driver.save_screenshot(screenshot_path)
            result["shots"].append(screenshot_path)
        except:
            pass
        return result

# ===== CAPTCHA Detection and Notification Functions =====

def detect_captcha(driver):
    """
    Detect CAPTCHA elements on the current page
    Returns the CAPTCHA provider name or None
    """
    try:
        # CAPTCHA detection selectors
        captcha_selectors = [
            ("hcaptcha", "iframe[src*='hcaptcha' i]"),
            ("turnstile", "iframe[src*='turnstile' i]"),
            ("recaptcha", "iframe[src*='recaptcha' i]"),
            ("recaptcha", "div[id*='recaptcha' i]"),
            ("hcaptcha", "div[id*='hcaptcha' i]"),
            ("turnstile", "div[id*='turnstile' i]"),
            ("unknown", "iframe[title*='captcha' i]"),
            ("unknown", "div[class*='captcha' i]"),
        ]
        
        for provider, selector in captcha_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Check if element is visible
                    for element in elements:
                        if element.is_displayed():
                            logger.info(f"🛡️ CAPTCHA detected: {provider} (selector: {selector})")
                            return provider
            except Exception:
                continue
        
        # Additional check for CAPTCHA challenges in page source
        page_source = driver.page_source.lower()
        if any(term in page_source for term in ['captcha', 'hcaptcha', 'recaptcha', 'turnstile']):
            # Check for visible CAPTCHA elements
            try:
                captcha_elements = driver.find_elements(By.CSS_SELECTOR, "*[class*='captcha' i], *[id*='captcha' i]")
                for elem in captcha_elements:
                    if elem.is_displayed():
                        logger.info("🛡️ CAPTCHA detected: unknown (page source analysis)")
                        return "unknown"
            except Exception:
                pass
        
        return None
        
    except Exception as e:
        logger.warning(f"⚠️ Error detecting CAPTCHA: {e}")
        return None

def notify_captcha_needed(job_id, provider, novnc_url=None, browser_session=None):
    """
    Notify backend that a CAPTCHA needs to be resolved
    """
    try:
        import requests
        
        base_url = os.environ.get("SON1K_API_BASE", "http://localhost:8000").rstrip("/")
        novnc_url = novnc_url or os.environ.get("NOVNC_PUBLIC_URL", "").strip()
        
        payload = {
            "job_id": job_id,
            "provider": provider or "unknown",
            "status": "NEEDED",
            "novnc_url": novnc_url,
            "browser_session": browser_session,
            "timestamp": int(time.time())
        }
        
        response = requests.post(
            f"{base_url}/api/captcha/event",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ CAPTCHA notification sent: {job_id} - {provider}")
            if novnc_url:
                logger.info(f"🖥️ noVNC URL available for user: {novnc_url}")
            return True
        else:
            logger.warning(f"⚠️ CAPTCHA notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️ Failed to notify CAPTCHA needed: {e}")
        return False

def notify_captcha_resolved(job_id, provider, browser_session=None):
    """
    Notify backend that a CAPTCHA has been resolved
    """
    try:
        import requests
        
        base_url = os.environ.get("SON1K_API_BASE", "http://localhost:8000").rstrip("/")
        
        payload = {
            "job_id": job_id,
            "provider": provider or "unknown",
            "status": "RESOLVED",
            "browser_session": browser_session,
            "timestamp": int(time.time())
        }
        
        response = requests.post(
            f"{base_url}/api/captcha/event",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ CAPTCHA resolution notification sent: {job_id}")
            return True
        else:
            logger.warning(f"⚠️ CAPTCHA resolution notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️ Failed to notify CAPTCHA resolved: {e}")
        return False

def wait_captcha_if_any_with_notifications(driver, job_id, max_wait_seconds=180, screenshot_callback=None):
    """
    Enhanced CAPTCHA waiting with backend notifications
    
    Args:
        driver: Selenium WebDriver instance
        job_id: Unique identifier for this automation job
        max_wait_seconds: Maximum time to wait for CAPTCHA resolution
        screenshot_callback: Function to call for taking screenshots
    
    Returns:
        bool: True if no CAPTCHA or CAPTCHA resolved, False if timeout
    """
    try:
        # Check for CAPTCHA
        provider = detect_captcha(driver)
        if not provider:
            logger.info("✅ No CAPTCHA detected")
            return True
        
        logger.info(f"🛡️ CAPTCHA detected: {provider}")
        
        # Notify backend that CAPTCHA is needed
        novnc_url = os.environ.get("NOVNC_PUBLIC_URL", "").strip()
        browser_session = os.environ.get("SV_SELENIUM_URL", "").strip()
        
        notify_captcha_needed(job_id, provider, novnc_url, browser_session)
        
        # Wait for CAPTCHA resolution
        end_time = time.time() + max_wait_seconds
        last_screenshot_time = 0
        
        logger.info(f"⏳ Waiting for CAPTCHA resolution (max {max_wait_seconds}s)...")
        if novnc_url:
            logger.info(f"🖥️ User can resolve at: {novnc_url}")
        
        while time.time() < end_time:
            # Take periodic screenshots
            current_time = time.time()
            if screenshot_callback and (current_time - last_screenshot_time) > 10:
                remaining = int(end_time - current_time)
                screenshot_callback(f"captcha_wait_{remaining}s.png")
                last_screenshot_time = current_time
            
            # Check if CAPTCHA is still present
            current_provider = detect_captcha(driver)
            if not current_provider:
                logger.info("✅ CAPTCHA resolved!")
                notify_captcha_resolved(job_id, provider, browser_session)
                return True
            
            time.sleep(1)
        
        logger.warning(f"⏰ CAPTCHA resolution timeout after {max_wait_seconds}s")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error in CAPTCHA waiting: {e}")
        return False

# Export main functions
__all__ = [
    "ensure_on_create",
    "ensure_logged_in", 
    "ensure_custom_tab", 
    "get_lyrics_card_and_textarea",
    "get_styles_card",
    "get_styles_editor",
    "write_textarea",
    "write_contenteditable", 
    "read_value",
    "wait_captcha_if_any",
    "wait_for_generation_and_fetch_audio",
    "compose_and_create",
    "detect_captcha",
    "notify_captcha_needed",
    "notify_captcha_resolved",
    "wait_captcha_if_any_with_notifications"
]
