"""
Suno.com Selenium Automation Worker
Handles music generation via browser automation with anti-detection
"""

import os
import json
import time
import logging
import random
import tempfile
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException, ElementNotInteractableException
)
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import ssl
import urllib3

from .cookie_manager import CookieManager

logger = logging.getLogger(__name__)

class SunoSeleniumWorker:
    """Selenium automation worker for Suno.com music generation"""
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.proxy = proxy
        self.cookie_manager = CookieManager()
        self.generation_timeout = 300  # 5 minutes
        self.page_timeout = 30
        self.download_dir = Path("generated_audio")
        self.download_dir.mkdir(exist_ok=True)
        
        # Anti-detection settings
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Element selectors (updated for current Suno UI - December 2024)
        self.selectors = {
            # Authentication selectors
            'auth_buttons': [
                ".cl-socialButtonsIconButton__google",
                ".cl-socialButtonsIconButton__discord", 
                ".cl-socialButtonsIconButton__apple",
                "button[data-testid='google-sign-in']",
                "button[data-testid='discord-sign-in']"
            ],
            'phone_input': [
                "input[name='identifier']",
                "input[placeholder*='phone number']",
                "input[type='tel']"
            ],
            'continue_button': [
                ".cl-formButtonPrimary",
                "button:contains('Continue')",
                "button[type='submit']"
            ],
            # Navigation selectors
            'create_button': [
                "a[href*='/create']",
                "button[data-testid='create-button']",
                "button:contains('Create')",
                "[data-cy='create-btn']",
                ".create-button",
                "nav a:contains('Create')"
            ],
            # Creation form selectors (updated for current UI)
            'lyrics_input': [
                "textarea[placeholder*='lyrics']",
                "textarea[placeholder*='Lyrics']",
                "textarea[data-testid='lyrics-input']", 
                "textarea[name='lyrics']",
                ".lyrics-textarea",
                "textarea[aria-label*='lyrics']",
                "#lyrics-input"
            ],
            'prompt_input': [
                "input[placeholder*='style']",
                "input[placeholder*='Style']",
                "input[placeholder*='describe']",
                "input[placeholder*='Describe']",
                "textarea[placeholder*='describe']",
                "input[data-testid='style-input']",
                "input[name='prompt']",
                ".style-input",
                "input[aria-label*='style']",
                "#style-input"
            ],
            'generate_button': [
                "button[data-testid='generate-button']",
                "button:contains('Generate')",
                "button:contains('Create')",
                "button:contains('Create Music')",
                ".generate-btn",
                "[data-cy='generate']",
                "button[type='submit']:contains('Create')"
            ],
            # Results selectors
            'audio_elements': [
                "audio[src]",
                "[data-testid='audio-player'] audio",
                ".audio-container audio",
                "audio[controls]",
                "video[src*='audio']"
            ],
            'download_links': [
                "a[href*='.mp3']",
                "a[href*='.wav']", 
                "a[download*='audio']",
                "[data-testid='download-button']",
                ".download-link",
                "button:contains('Download')"
            ],
            'generation_status': [
                "[data-testid='generation-status']",
                ".generation-progress",
                ".status-indicator",
                "[aria-label*='status']",
                ".progress-bar"
            ]
        }
    
    def setup_driver(self) -> bool:
        """Initialize Chrome driver with anti-detection measures"""
        try:
            logger.info("🚀 Setting up Chrome driver...")
            
            # Disable SSL warnings for certificate issues
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Chrome options
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument("--headless=new")
            
            # Performance and stealth options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # Faster loading
            options.add_argument("--disable-javascript-harmony-shipping")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-ipc-flooding-protection")
            
            # SSL and certificate options for macOS
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--ignore-ssl-errors")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-web-security")
            options.add_argument("--ignore-certificate-errors-spki-list")
            options.add_argument("--ignore-ssl-errors-ssl-invalid-cert")
            
            # Random user agent
            user_agent = random.choice(self.user_agents)
            options.add_argument(f"--user-agent={user_agent}")
            
            # Window size
            options.add_argument("--window-size=1920,1080")
            
            # Download preferences
            prefs = {
                "download.default_directory": str(self.download_dir.absolute()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
            
            # Proxy if specified
            if self.proxy:
                options.add_argument(f"--proxy-server={self.proxy}")
            
            try:
                # Try to initialize undetected Chrome driver with fallback options
                logger.info("📦 Attempting to initialize undetected Chrome driver...")
                
                # First try with webdriver manager path
                driver_path = None
                try:
                    driver_path = ChromeDriverManager().install()
                    logger.info(f"📍 ChromeDriver path: {driver_path}")
                except Exception as driver_e:
                    logger.warning(f"⚠️ ChromeDriverManager failed: {driver_e}")
                
                # Initialize with driver path if available
                if driver_path:
                    self.driver = uc.Chrome(options=options, driver_executable_path=driver_path)
                else:
                    # Fallback to auto-detection
                    self.driver = uc.Chrome(options=options, version_main=None)
                    
            except Exception as uc_error:
                logger.warning(f"⚠️ Undetected Chrome failed: {uc_error}")
                logger.info("🔄 Falling back to standard ChromeDriver...")
                
                # Fallback to standard selenium ChromeDriver
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            self.wait = WebDriverWait(self.driver, self.page_timeout)
            
            # Additional stealth measures
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            except Exception as stealth_error:
                logger.warning(f"⚠️ Stealth script injection failed: {stealth_error}")
            
            logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Chrome driver: {e}")
            if 'certificate verify failed' in str(e):
                logger.error("🔒 SSL Certificate issue detected. Try running: pip install --upgrade certifi")
            return False
    
    def load_suno_with_auth(self) -> bool:
        """Load Suno.com and authenticate using cookies"""
        try:
            logger.info("🌐 Loading Suno.com with authentication...")
            
            # Load cookies first
            if not self.cookie_manager.load_cookies():
                logger.warning("⚠️ No cookies found, proceeding without authentication")
            else:
                valid, issues = self.cookie_manager.validate_cookies()
                if not valid:
                    logger.warning(f"⚠️ Cookie validation issues: {issues}")
            
            # Navigate to Suno.com
            self.driver.get("https://suno.com")
            self._random_delay(2, 4)
            
            # Apply cookies if available
            if self.cookie_manager.cookies:
                if self.cookie_manager.apply_cookies_to_driver(self.driver):
                    logger.info("🍪 Cookies applied, refreshing page...")
                    self.driver.refresh()
                    self._random_delay(3, 5)
            
            # Check if we're logged in
            login_indicators = [
                "button:contains('Create')",
                "[data-testid='user-menu']",
                ".user-avatar",
                "a[href*='/create']"
            ]
            
            is_logged_in = False
            for selector in login_indicators:
                try:
                    if self._find_element_safe(selector, timeout=5):
                        is_logged_in = True
                        break
                except:
                    continue
            
            if is_logged_in:
                logger.info("✅ Successfully authenticated with Suno.com")
            else:
                logger.warning("⚠️ Authentication status unclear, proceeding anyway")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load Suno.com: {e}")
            return False
    
    def navigate_to_create(self) -> bool:
        """Navigate to the music creation page"""
        try:
            logger.info("🎵 Navigating to music creation page...")
            
            # Check current URL first
            current_url = self.driver.current_url
            logger.info(f"📍 Current URL: {current_url}")
            
            # If we're on sign-in page, try to skip authentication
            if 'sign-in' in current_url or 'login' in current_url:
                logger.info("🔐 Detected sign-in page, attempting to bypass...")
                
                # Try to access the app directly with different URL patterns
                bypass_urls = [
                    "https://suno.com/home",
                    "https://suno.com/app",
                    "https://app.suno.com",
                    "https://suno.com",
                ]
                
                for bypass_url in bypass_urls:
                    try:
                        logger.info(f"🌐 Trying bypass URL: {bypass_url}")
                        self.driver.get(bypass_url)
                        self._random_delay(3, 5)
                        
                        # Re-apply cookies after navigation
                        if self.cookie_manager.cookies:
                            self.cookie_manager.apply_cookies_to_driver(self.driver)
                            self.driver.refresh()
                            self._random_delay(3, 5)
                        
                        # Check if we bypassed sign-in
                        current_url = self.driver.current_url
                        if 'sign-in' not in current_url and 'login' not in current_url:
                            logger.info(f"✅ Bypassed authentication via {bypass_url}")
                            break
                    except Exception as e:
                        logger.warning(f"⚠️ Bypass failed for {bypass_url}: {e}")
                        continue
            
            # Try multiple ways to get to create page
            create_methods = [
                ("direct_url", "https://suno.com/create"),
                ("direct_url_v2", "https://app.suno.com/create"),
                ("direct_url_v3", "https://suno.com/app/create"),
                ("button_click", None)
            ]
            
            for method, url in create_methods:
                try:
                    logger.info(f"🎯 Trying method: {method}")
                    
                    if method == "button_click":
                        # Look for create button on current page
                        for selector in self.selectors['create_button']:
                            element = self._find_element_safe(selector, timeout=5)
                            if element:
                                logger.info(f"🎯 Found create button: {selector}")
                                self._safe_click(element)
                                self._random_delay(3, 5)
                                break
                    else:
                        # Direct navigation
                        logger.info(f"🌐 Navigating to: {url}")
                        self.driver.get(url)
                        self._random_delay(3, 5)
                        
                        # Re-apply cookies if needed
                        if 'sign-in' in self.driver.current_url:
                            logger.info("🍪 Re-applying cookies...")
                            if self.cookie_manager.cookies:
                                self.cookie_manager.apply_cookies_to_driver(self.driver)
                                self.driver.refresh()
                                self._random_delay(3, 5)
                    
                    # Check if we're on create page or any valid page
                    current_url = self.driver.current_url
                    page_title = self.driver.title
                    logger.info(f"📍 Current URL: {current_url}")
                    logger.info(f"📄 Page title: {page_title}")
                    
                    # Check for create page indicators
                    create_indicators = self.selectors['lyrics_input'] + self.selectors['prompt_input'] + self.selectors['generate_button']
                    
                    page_valid = False
                    for indicator in create_indicators:
                        if self._find_element_safe(indicator, timeout=3):
                            logger.info(f"✅ Found create page element: {indicator}")
                            page_valid = True
                            break
                    
                    if page_valid:
                        logger.info("✅ Successfully reached create page")
                        self.take_screenshot("create_page_success")
                        return True
                    
                    # Check if we're at least not on sign-in page
                    if 'sign-in' not in current_url and 'login' not in current_url:
                        logger.info("🎯 Not on sign-in page, checking for any usable elements...")
                        
                        # Try to find any input fields we can use
                        all_inputs = self.driver.find_elements("css selector", "input, textarea")
                        if len(all_inputs) > 0:
                            logger.info(f"🔍 Found {len(all_inputs)} input elements")
                            
                            # Look for music-related inputs
                            for inp in all_inputs:
                                try:
                                    placeholder = inp.get_attribute('placeholder') or ''
                                    if any(keyword in placeholder.lower() for keyword in ['music', 'style', 'prompt', 'describe', 'lyrics']):
                                        logger.info(f"🎵 Found music-related input: {placeholder}")
                                        self.take_screenshot("music_input_found")
                                        return True
                                except:
                                    continue
                    
                except Exception as e:
                    logger.warning(f"⚠️ Create navigation method failed: {method} - {e}")
                    continue
            
            # Final attempt: try to work with whatever page we have
            logger.warning("⚠️ Could not reach ideal create page, checking current page...")
            self.take_screenshot("final_page_state")
            
            # If we're not on sign-in page, consider it a partial success
            current_url = self.driver.current_url
            if 'sign-in' not in current_url and 'login' not in current_url:
                logger.warning("🔄 Proceeding with current page state")
                return True
            
            logger.error("❌ Could not navigate to create page")
            return False
            
        except Exception as e:
            logger.error(f"❌ Navigation to create page failed: {e}")
            self.take_screenshot("navigation_error")
            return False
    
    def generate_music(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate music with the given payload and progress tracking"""
        try:
            logger.info(f"🎼 Starting music generation: {payload.get('prompt', 'No prompt')}")
            
            # Extract parameters
            prompt = payload.get('prompt', '')
            lyrics = payload.get('lyrics', '')
            style = payload.get('style', '')
            instrumental = payload.get('instrumental', False)
            
            # Progress tracking function
            def update_progress(progress, message):
                """Send progress update if callback is available"""
                try:
                    callback = payload.get('progress_callback')
                    if callback:
                        callback(progress, message)
                    logger.info(f"📊 Progress {progress}%: {message}")
                except Exception as e:
                    logger.warning(f"Progress update failed: {e}")
            
            update_progress(55, "Filling form inputs...")
            
            # Fill in lyrics if provided
            if lyrics and not instrumental:
                update_progress(60, "Entering lyrics...")
                if not self._fill_lyrics(lyrics):
                    logger.warning("⚠️ Failed to fill lyrics, continuing...")
            
            # Fill in style/prompt
            if prompt or style:
                update_progress(65, "Setting style and prompt...")
                style_text = f"{prompt} {style}".strip()
                if not self._fill_style_prompt(style_text):
                    logger.warning("⚠️ Failed to fill style prompt, continuing...")
            
            # Set instrumental mode if needed
            if instrumental:
                update_progress(70, "Configuring instrumental mode...")
                self._set_instrumental_mode()
            
            # Start generation
            update_progress(75, "Submitting generation request...")
            if not self._start_generation():
                return {"success": False, "error": "Failed to start generation"}
            
            # Wait for completion and get results
            update_progress(80, "Waiting for music generation to complete...")
            result = self._wait_for_generation_complete()
            
            if result["success"]:
                update_progress(90, "Downloading generated audio files...")
                # Download audio files
                audio_files = self._download_generated_audio()
                result["audio_files"] = audio_files
                
                if audio_files:
                    result["primary_file"] = audio_files[0]
                    result["all_files"] = audio_files
                    update_progress(100, f"Generation completed with {len(audio_files)} files")
                    logger.info(f"✅ Generation completed with {len(audio_files)} files")
                else:
                    update_progress(95, "Generation completed but no audio files found")
                    logger.warning("⚠️ Generation completed but no audio files found")
            else:
                update_progress(100, f"Generation failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Music generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _fill_lyrics(self, lyrics: str) -> bool:
        """Fill lyrics textarea"""
        try:
            for selector in self.selectors['lyrics_input']:
                element = self._find_element_safe(selector, timeout=5)
                if element:
                    self._safe_clear_and_type(element, lyrics)
                    logger.info("✅ Lyrics filled successfully")
                    return True
            
            logger.warning("⚠️ Lyrics input not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to fill lyrics: {e}")
            return False
    
    def _fill_style_prompt(self, style: str) -> bool:
        """Fill style/prompt input"""
        try:
            for selector in self.selectors['prompt_input']:
                element = self._find_element_safe(selector, timeout=5)
                if element:
                    self._safe_clear_and_type(element, style)
                    logger.info("✅ Style prompt filled successfully")
                    return True
            
            logger.warning("⚠️ Style input not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to fill style: {e}")
            return False
    
    def _set_instrumental_mode(self) -> bool:
        """Set instrumental mode if available"""
        try:
            instrumental_selectors = [
                "input[type='checkbox'][aria-label*='instrumental']",
                "input[type='checkbox'][name*='instrumental']",
                "[data-testid='instrumental-toggle']",
                "button:contains('Instrumental')",
                ".instrumental-toggle"
            ]
            
            for selector in instrumental_selectors:
                element = self._find_element_safe(selector, timeout=3)
                if element:
                    if element.tag_name == 'input' and element.get_attribute('type') == 'checkbox':
                        if not element.is_selected():
                            self._safe_click(element)
                    else:
                        self._safe_click(element)
                    
                    logger.info("✅ Instrumental mode enabled")
                    return True
            
            logger.info("ℹ️ Instrumental toggle not found (may not be available)")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to set instrumental mode: {e}")
            return False
    
    def _start_generation(self) -> bool:
        """Click generate button to start music generation"""
        try:
            logger.info("🚀 Starting music generation...")
            
            for selector in self.selectors['generate_button']:
                element = self._find_element_safe(selector, timeout=5)
                if element and element.is_enabled():
                    self._safe_click(element)
                    self._random_delay(2, 3)
                    logger.info("✅ Generate button clicked")
                    return True
            
            logger.error("❌ Generate button not found or not clickable")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start generation: {e}")
            return False
    
    def _wait_for_generation_complete(self) -> Dict[str, Any]:
        """Wait for music generation to complete"""
        try:
            logger.info("⏳ Waiting for generation to complete...")
            start_time = time.time()
            
            while time.time() - start_time < self.generation_timeout:
                # Check for audio elements (success indicator)
                audio_found = False
                for selector in self.selectors['audio_elements']:
                    if self._find_element_safe(selector, timeout=2):
                        audio_found = True
                        break
                
                if audio_found:
                    logger.info("✅ Audio elements detected - generation complete!")
                    return {"success": True, "message": "Generation completed successfully"}
                
                # Check for error indicators
                error_selectors = [
                    ".error-message",
                    "[data-testid='error']",
                    ".generation-failed",
                    "div:contains('failed')",
                    "div:contains('error')"
                ]
                
                for selector in error_selectors:
                    error_element = self._find_element_safe(selector, timeout=1)
                    if error_element:
                        error_text = error_element.text
                        logger.error(f"❌ Generation failed: {error_text}")
                        return {"success": False, "error": f"Generation failed: {error_text}"}
                
                # Check status indicators
                for selector in self.selectors['generation_status']:
                    status_element = self._find_element_safe(selector, timeout=1)
                    if status_element:
                        status_text = status_element.text.lower()
                        if 'complete' in status_text or 'done' in status_text:
                            return {"success": True, "message": "Generation completed"}
                        elif 'failed' in status_text or 'error' in status_text:
                            return {"success": False, "error": f"Generation failed: {status_text}"}
                
                # Progress indicator
                elapsed = int(time.time() - start_time)
                if elapsed % 30 == 0:  # Log every 30 seconds
                    logger.info(f"⏳ Still waiting for generation... ({elapsed}s elapsed)")
                
                time.sleep(5)  # Check every 5 seconds
            
            logger.error("❌ Generation timeout reached")
            return {"success": False, "error": "Generation timeout"}
            
        except Exception as e:
            logger.error(f"❌ Error waiting for generation: {e}")
            return {"success": False, "error": str(e)}
    
    def _download_generated_audio(self) -> List[Dict[str, str]]:
        """Download generated audio files"""
        try:
            logger.info("💾 Downloading generated audio files...")
            downloaded_files = []
            
            # Find audio sources
            audio_urls = set()
            
            # Method 1: Direct audio elements
            audio_elements = self.driver.find_elements(By.CSS_SELECTOR, "audio[src]")
            for audio in audio_elements:
                src = audio.get_attribute('src')
                if src and src.startswith('http'):
                    audio_urls.add(src)
            
            # Method 2: Download links
            for selector in self.selectors['download_links']:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        href = link.get_attribute('href')
                        if href and ('.mp3' in href or '.wav' in href):
                            audio_urls.add(href)
                except:
                    continue
            
            # Method 3: Page source parsing
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find audio URLs in various attributes
            for attr in ['src', 'href', 'data-src', 'data-url']:
                elements = soup.find_all(attrs={attr: True})
                for element in elements:
                    url = element.get(attr)
                    if url and any(ext in url for ext in ['.mp3', '.wav', '.m4a']):
                        if url.startswith('http'):
                            audio_urls.add(url)
                        elif url.startswith('/'):
                            audio_urls.add(f"https://suno.com{url}")
            
            logger.info(f"🔍 Found {len(audio_urls)} audio URLs")
            
            # Download each audio file
            for i, url in enumerate(audio_urls):
                try:
                    file_info = self._download_audio_file(url, f"generated_{i+1}")
                    if file_info:
                        downloaded_files.append(file_info)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to download {url}: {e}")
                    continue
            
            logger.info(f"✅ Downloaded {len(downloaded_files)} audio files")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"❌ Failed to download audio files: {e}")
            return []
    
    def _download_audio_file(self, url: str, filename_prefix: str) -> Optional[Dict[str, str]]:
        """Download a single audio file with metadata"""
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Referer': 'https://suno.com/'
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'audio/mpeg' in content_type or url.endswith('.mp3'):
                ext = '.mp3'
            elif 'audio/wav' in content_type or url.endswith('.wav'):
                ext = '.wav'
            else:
                ext = '.mp3'  # Default
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}{ext}"
            file_path = self.download_dir / filename
            
            # Download file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = file_path.stat().st_size
            logger.info(f"✅ Downloaded: {filename} ({file_size} bytes)")
            
            # Create metadata file
            metadata = {
                "filename": filename,
                "file_path": str(file_path.absolute()),
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "url": url,
                "downloaded_at": datetime.now().isoformat(),
                "content_type": content_type,
                "extension": ext,
                "source": "suno.com",
                "method": "selenium_automation",
                "streaming_url": f"/api/audio/stream/{filename}",
                "download_url": f"/api/audio/download/{filename}",
                "metadata_url": f"/api/audio/metadata/{filename}"
            }
            
            # Save metadata file
            metadata_path = file_path.with_suffix('.json')
            try:
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                logger.info(f"💾 Saved metadata: {metadata_path.name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save metadata: {e}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Download failed for {url}: {e}")
            return None
    
    def take_screenshot(self, name: str = "error_screenshot") -> str:
        """Take screenshot for debugging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/{name}_{timestamp}.png"
            os.makedirs("screenshots", exist_ok=True)
            
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
            return screenshot_path
        except:
            return ""
    
    def cleanup(self):
        """Cleanup driver and resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("🧹 Driver cleanup completed")
        except:
            pass
    
    # Helper methods
    def _find_element_safe(self, selector: str, timeout: int = 10) -> Optional[Any]:
        """Safely find element with timeout"""
        try:
            if selector.startswith("button:contains(") or selector.startswith("div:contains("):
                # Handle text-based selectors
                text = selector.split("'")[1] if "'" in selector else selector.split('"')[1]
                xpath = f"//*[contains(text(), '{text}')]"
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            else:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
        except:
            return None
    
    def _safe_click(self, element) -> bool:
        """Safely click element with retries"""
        try:
            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self._random_delay(0.5, 1)
            
            # Try regular click
            element.click()
            return True
        except:
            try:
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                try:
                    # Try ActionChains click
                    ActionChains(self.driver).move_to_element(element).click().perform()
                    return True
                except:
                    return False
    
    def _safe_clear_and_type(self, element, text: str) -> bool:
        """Safely clear and type text"""
        try:
            element.clear()
            self._random_delay(0.2, 0.5)
            element.send_keys(text)
            self._random_delay(0.2, 0.5)
            return True
        except:
            try:
                # Try JavaScript approach
                self.driver.execute_script("arguments[0].value = '';", element)
                element.send_keys(text)
                return True
            except:
                return False
    
    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay for human-like behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

def test_selenium_worker():
    """Test Selenium worker functionality"""
    print("🧪 Testing Selenium Worker...")
    
    worker = SunoSeleniumWorker(headless=False)  # Visible for testing
    
    try:
        if not worker.setup_driver():
            print("❌ Driver setup failed")
            return
        
        if not worker.load_suno_with_auth():
            print("❌ Suno loading failed")
            return
        
        if not worker.navigate_to_create():
            print("❌ Navigation to create failed")
            return
        
        # Test generation
        test_payload = {
            "prompt": "upbeat electronic music for testing",
            "instrumental": True
        }
        
        result = worker.generate_music(test_payload)
        print(f"🎵 Generation result: {result}")
        
    finally:
        worker.cleanup()

if __name__ == "__main__":
    test_selenium_worker()