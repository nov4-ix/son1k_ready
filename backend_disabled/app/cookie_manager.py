"""
Cookie Manager for Suno.com Selenium automation
Handles secure loading, validation, and management of browser cookies
"""

import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time

logger = logging.getLogger(__name__)

class CookieManager:
    """Manages Suno.com authentication cookies for Selenium automation"""
    
    def __init__(self, cookie_file: str = "cookies.json", project_root: Optional[str] = None):
        if project_root:
            self.cookie_file = Path(project_root) / cookie_file
        else:
            self.cookie_file = Path(cookie_file)
        
        self.cookies = {}
        self.last_loaded = None
        self.domain = "suno.com"
        
    def load_cookies(self) -> bool:
        """Load cookies from JSON file"""
        try:
            if not self.cookie_file.exists():
                logger.warning(f"🔸 Cookie file not found: {self.cookie_file}")
                return False
            
            with open(self.cookie_file, 'r') as f:
                data = json.load(f)
            
            if 'cookies' not in data:
                logger.error("❌ Invalid cookie file format")
                return False
            
            self.cookies = data
            self.last_loaded = datetime.now()
            
            logger.info(f"✅ Loaded {len(data['cookies'])} cookies from {self.cookie_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load cookies: {e}")
            return False
    
    def validate_cookies(self) -> Tuple[bool, List[str]]:
        """Validate loaded cookies for freshness and completeness"""
        if not self.cookies:
            return False, ["No cookies loaded"]
        
        issues = []
        cookies = self.cookies.get('cookies', [])
        
        if not cookies:
            return False, ["Empty cookie list"]
        
        # Check for essential authentication cookies
        auth_cookies = ['session', 'auth', 'token', '_session', 'connect.sid', '__session']
        found_auth = []
        
        for cookie in cookies:
            cookie_name = cookie.get('name', '').lower()
            for auth_name in auth_cookies:
                if auth_name in cookie_name:
                    found_auth.append(cookie['name'])
                    break
        
        if not found_auth:
            issues.append("No authentication cookies found")
        
        # Check cookie expiration
        expired_count = 0
        current_time = int(time.time() * 1000000)  # Chrome timestamp format
        
        for cookie in cookies:
            expires = cookie.get('expires', 0)
            if expires > 0 and expires < current_time:
                expired_count += 1
        
        if expired_count > len(cookies) * 0.5:  # More than 50% expired
            issues.append(f"{expired_count}/{len(cookies)} cookies expired")
        
        # Check extraction age
        extracted_at = self.cookies.get('extracted_at')
        if extracted_at:
            try:
                extract_time = datetime.fromisoformat(extracted_at.replace('Z', '+00:00'))
                age_hours = (datetime.now() - extract_time).total_seconds() / 3600
                
                if age_hours > 24:
                    issues.append(f"Cookies are {age_hours:.1f} hours old")
                elif age_hours > 72:
                    issues.append("Cookies are very old (>3 days)")
            except:
                pass
        
        is_valid = len(issues) == 0
        if is_valid:
            logger.info(f"✅ Cookies validated successfully. Auth cookies: {found_auth}")
        else:
            logger.warning(f"⚠️ Cookie validation issues: {issues}")
        
        return is_valid, issues
    
    def apply_cookies_to_driver(self, driver) -> bool:
        """Apply loaded cookies to Selenium WebDriver"""
        try:
            if not self.cookies:
                logger.error("❌ No cookies to apply")
                return False
            
            cookies = self.cookies.get('cookies', [])
            applied_count = 0
            
            # Navigate to domain first to set cookie context
            try:
                driver.get(f"https://{self.domain}")
                time.sleep(2)
            except Exception as e:
                logger.warning(f"⚠️ Could not navigate to {self.domain}: {e}")
            
            for cookie in cookies:
                try:
                    # Prepare cookie for Selenium
                    selenium_cookie = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', self.domain),
                        'path': cookie.get('path', '/'),
                        'secure': cookie.get('secure', False),
                        'httpOnly': cookie.get('httpOnly', False)
                    }
                    
                    # Handle expiry
                    expires = cookie.get('expires')
                    if expires and expires > 0:
                        # Convert Chrome timestamp to Unix timestamp
                        if expires > 1000000000000:  # Chrome format (microseconds)
                            expires = expires / 1000000
                        selenium_cookie['expiry'] = int(expires)
                    
                    # Handle sameSite
                    same_site = cookie.get('sameSite')
                    if same_site and same_site in ['Strict', 'Lax', 'None']:
                        selenium_cookie['sameSite'] = same_site
                    
                    driver.add_cookie(selenium_cookie)
                    applied_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to apply cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"✅ Applied {applied_count}/{len(cookies)} cookies to driver")
            return applied_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to apply cookies to driver: {e}")
            return False
    
    def refresh_cookies_if_needed(self) -> bool:
        """Check if cookies need refreshing and reload if necessary"""
        if not self.last_loaded:
            return self.load_cookies()
        
        # Reload if file is newer than our last load
        try:
            file_mtime = datetime.fromtimestamp(self.cookie_file.stat().st_mtime)
            if file_mtime > self.last_loaded:
                logger.info("🔄 Cookie file updated, reloading...")
                return self.load_cookies()
        except:
            pass
        
        # Reload if data is old
        age_minutes = (datetime.now() - self.last_loaded).total_seconds() / 60
        if age_minutes > 30:  # Reload every 30 minutes
            logger.info("🔄 Refreshing cookies (30min refresh)")
            return self.load_cookies()
        
        return True
    
    def get_cookie_summary(self) -> Dict:
        """Get summary of loaded cookies for debugging"""
        if not self.cookies:
            return {"status": "no_cookies", "count": 0}
        
        cookies = self.cookies.get('cookies', [])
        auth_cookies = []
        expired_count = 0
        current_time = int(time.time() * 1000000)
        
        for cookie in cookies:
            # Check for auth cookies
            cookie_name = cookie.get('name', '').lower()
            if any(auth in cookie_name for auth in ['session', 'auth', 'token', '_session']):
                auth_cookies.append(cookie['name'])
            
            # Check expiration
            expires = cookie.get('expires', 0)
            if expires > 0 and expires < current_time:
                expired_count += 1
        
        return {
            "status": "loaded",
            "count": len(cookies),
            "auth_cookies": auth_cookies,
            "expired_count": expired_count,
            "extracted_at": self.cookies.get('extracted_at'),
            "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None
        }
    
    def create_fallback_cookies(self) -> bool:
        """Create minimal fallback cookies for testing"""
        logger.warning("🔸 Creating fallback cookies for testing")
        
        fallback_data = {
            "extracted_at": datetime.now().isoformat(),
            "domain": self.domain,
            "count": 1,
            "cookies": [
                {
                    "name": "test_session",
                    "value": "fallback_session_token",
                    "domain": f".{self.domain}",
                    "path": "/",
                    "expires": int((datetime.now() + timedelta(days=1)).timestamp() * 1000000),
                    "secure": True,
                    "httpOnly": True,
                    "sameSite": "Lax"
                }
            ]
        }
        
        self.cookies = fallback_data
        return True

def test_cookie_manager():
    """Test cookie manager functionality"""
    print("🧪 Testing Cookie Manager...")
    
    cm = CookieManager()
    
    # Test loading
    if cm.load_cookies():
        print("✅ Cookie loading successful")
        
        # Test validation
        valid, issues = cm.validate_cookies()
        if valid:
            print("✅ Cookie validation passed")
        else:
            print(f"⚠️ Cookie validation issues: {issues}")
        
        # Print summary
        summary = cm.get_cookie_summary()
        print(f"📋 Cookie summary: {summary}")
        
    else:
        print("❌ Cookie loading failed")
        print("💡 Run extract_cookies.py first to create cookies.json")

if __name__ == "__main__":
    test_cookie_manager()