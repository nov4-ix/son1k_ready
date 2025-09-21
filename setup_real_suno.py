#!/usr/bin/env python3
"""
Setup script for REAL Suno automation
Extracts credentials and configures the system for production
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from backend.app.cookie_manager import CookieManager
    from backend.app.selenium_worker import SunoSeleniumWorker
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Installing missing dependencies...")
    os.system("pip install selenium undetected-chromedriver webdriver-manager beautifulsoup4 browser-cookie3")
    
    try:
        from backend.app.cookie_manager import CookieManager
        from backend.app.selenium_worker import SunoSeleniumWorker
    except ImportError as e2:
        print(f"❌ Still cannot import: {e2}")
        sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_cookies_from_browser():
    """Extract Suno cookies from browser"""
    print("🍪 Extracting Suno cookies from browser...")
    
    try:
        import browser_cookie3
        
        # Try to get cookies from different browsers
        browsers = [
            ("Chrome", browser_cookie3.chrome),
            ("Firefox", browser_cookie3.firefox),
            ("Safari", browser_cookie3.safari),
            ("Edge", browser_cookie3.edge),
        ]
        
        for browser_name, browser_func in browsers:
            try:
                print(f"🔍 Checking {browser_name}...")
                cookies = browser_func(domain_name='suno.com')
                
                suno_cookies = []
                for cookie in cookies:
                    if 'suno.com' in cookie.domain:
                        suno_cookies.append({
                            'name': cookie.name,
                            'value': cookie.value,
                            'domain': cookie.domain,
                            'path': cookie.path,
                            'secure': cookie.secure
                        })
                
                if suno_cookies:
                    print(f"✅ Found {len(suno_cookies)} Suno cookies in {browser_name}")
                    
                    # Save cookies
                    with open('cookies.json', 'w') as f:
                        json.dump(suno_cookies, f, indent=2)
                    
                    return suno_cookies
                    
            except Exception as e:
                print(f"⚠️ {browser_name} failed: {e}")
                continue
        
        print("❌ No Suno cookies found in any browser")
        return None
        
    except ImportError:
        print("❌ browser-cookie3 not available")
        return None

def setup_environment_variables():
    """Setup environment variables for Suno credentials"""
    print("🔧 Setting up environment variables...")
    
    # Check if we have cookies
    if os.path.exists('cookies.json'):
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
        
        # Extract session ID and cookie string
        session_id = None
        cookie_string = ""
        
        for cookie in cookies:
            if 'session' in cookie['name'].lower():
                session_id = cookie['value']
            cookie_string += f"{cookie['name']}={cookie['value']}; "
        
        cookie_string = cookie_string.rstrip('; ')
        
        if session_id:
            print(f"✅ Found session ID: {session_id[:20]}...")
            os.environ['SUNO_SESSION_ID'] = session_id
        
        if cookie_string:
            print(f"✅ Cookie string length: {len(cookie_string)} chars")
            os.environ['SUNO_COOKIE'] = cookie_string
        
        # Write to .env file for persistence
        with open('.env', 'w') as f:
            if session_id:
                f.write(f"SUNO_SESSION_ID={session_id}\n")
            if cookie_string:
                f.write(f"SUNO_COOKIE={cookie_string}\n")
        
        print("✅ Environment variables configured")
        return True
    else:
        print("❌ No cookies.json found")
        return False

def test_selenium_setup():
    """Test Selenium setup"""
    print("🧪 Testing Selenium setup...")
    
    try:
        worker = SunoSeleniumWorker(headless=True)
        
        if worker.setup_driver():
            print("✅ Selenium driver setup successful")
            worker.cleanup()
            return True
        else:
            print("❌ Selenium driver setup failed")
            return False
            
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        return False

def test_suno_authentication():
    """Test Suno authentication"""
    print("🔐 Testing Suno authentication...")
    
    try:
        worker = SunoSeleniumWorker(headless=True)
        
        if not worker.setup_driver():
            print("❌ Driver setup failed")
            return False
        
        if worker.load_suno_with_auth():
            print("✅ Suno authentication successful")
            worker.cleanup()
            return True
        else:
            print("❌ Suno authentication failed")
            worker.cleanup()
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def run_manual_browser_setup():
    """Guide user through manual browser setup"""
    print("\n🌐 MANUAL BROWSER SETUP")
    print("=" * 50)
    print("1. Open Chrome and go to https://suno.com")
    print("2. Login to your Suno account")
    print("3. Press F12 to open Developer Tools")
    print("4. Go to 'Application' tab > 'Cookies' > 'https://suno.com'")
    print("5. Copy the following script to console:\n")
    
    # Read the JavaScript extraction script
    js_script_path = Path("extract_suno_credentials.js")
    if js_script_path.exists():
        with open(js_script_path, 'r') as f:
            js_content = f.read()
        print("```javascript")
        print(js_content)
        print("```")
    else:
        print("❌ extract_suno_credentials.js not found")
    
    print("\n6. Copy the output and paste it in credentials.json")
    print("7. Run this script again")
    print("=" * 50)

def main():
    """Main setup function"""
    print("🚀 Son1k REAL Suno Automation Setup")
    print("=" * 50)
    
    # Step 1: Try to extract cookies automatically
    cookies = extract_cookies_from_browser()
    
    if not cookies:
        print("\n⚠️ Automatic cookie extraction failed")
        run_manual_browser_setup()
        return
    
    # Step 2: Setup environment variables
    if not setup_environment_variables():
        print("❌ Failed to setup environment variables")
        return
    
    # Step 3: Test Selenium setup
    if not test_selenium_setup():
        print("❌ Selenium setup test failed")
        return
    
    # Step 4: Test Suno authentication
    if not test_suno_authentication():
        print("⚠️ Suno authentication test failed")
        print("🔧 Try manual browser setup or check credentials")
        return
    
    print("\n✅ REAL Suno automation setup COMPLETE!")
    print("🎵 Ready for real music generation!")
    print("🚀 Deploy to Railway to activate real automation")
    print("=" * 50)

if __name__ == "__main__":
    main()