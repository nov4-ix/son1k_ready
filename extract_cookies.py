#!/usr/bin/env python3
"""
Extract Suno.com cookies from Chrome browser for Selenium automation
Usage: python extract_cookies.py
Requirements: Chrome browser with Suno.com login session
"""

import json
import sqlite3
import os
import shutil
import platform
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
import keyring
import subprocess
from datetime import datetime

class ChromeCookieExtractor:
    def __init__(self):
        self.system = platform.system()
        self.chrome_data_path = self._get_chrome_data_path()
        self.cookies_db_path = self.chrome_data_path / "Default" / "Cookies"
        self.local_state_path = self.chrome_data_path / "Local State"
        
    def _get_chrome_data_path(self):
        """Get Chrome data directory path for different OS"""
        if self.system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
        elif self.system == "Windows":
            return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        else:  # Linux
            return Path.home() / ".config" / "google-chrome"
    
    def _get_encryption_key(self):
        """Get Chrome's encryption key for cookie decryption"""
        try:
            with open(self.local_state_path, 'r') as f:
                local_state = json.load(f)
            
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]  # Remove 'DPAPI' prefix
            
            if self.system == "Darwin":  # macOS
                # Use keychain access
                password = keyring.get_password("Chrome Safe Storage", "Chrome")
                if not password:
                    password = "peanuts"  # Default password
                key = PBKDF2(password.encode(), b"saltysalt", 16, 1003)
            elif self.system == "Windows":
                import win32crypt
                key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            else:  # Linux
                password = "peanuts".encode()
                key = PBKDF2(password, b"saltysalt", 16, 1)
            
            return key
        except Exception as e:
            print(f"⚠️ Warning: Could not get encryption key: {e}")
            return None
    
    def _decrypt_cookie_value(self, encrypted_value, key):
        """Decrypt Chrome cookie value"""
        try:
            if not key:
                return encrypted_value.decode('utf-8', errors='ignore')
            
            if encrypted_value.startswith(b'v10') or encrypted_value.startswith(b'v11'):
                # Chrome 80+ encryption
                iv = encrypted_value[3:15]
                encrypted_value = encrypted_value[15:]
                cipher = AES.new(key, AES.MODE_GCM, iv)
                decrypted_value = cipher.decrypt(encrypted_value)[:-16]
                return decrypted_value.decode('utf-8')
            else:
                # Older encryption or plain text
                return encrypted_value.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"⚠️ Warning: Cookie decryption failed: {e}")
            return ""
    
    def extract_suno_cookies(self):
        """Extract Suno.com cookies from Chrome"""
        print("🔍 Extracting Suno.com cookies from Chrome...")
        
        if not self.cookies_db_path.exists():
            raise FileNotFoundError(f"Chrome cookies database not found: {self.cookies_db_path}")
        
        # Copy database to avoid locking issues
        temp_db = Path("temp_cookies.db")
        shutil.copy2(self.cookies_db_path, temp_db)
        
        try:
            # Get encryption key
            key = self._get_encryption_key()
            
            # Connect to cookies database
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query Suno.com cookies
            query = """
            SELECT host_key, name, value, encrypted_value, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies 
            WHERE host_key LIKE '%suno.com%' OR host_key LIKE '%.suno.com'
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            cookies = []
            for row in rows:
                host_key, name, value, encrypted_value, path, expires_utc, is_secure, is_httponly, samesite = row
                
                # Decrypt cookie value if encrypted
                if encrypted_value:
                    cookie_value = self._decrypt_cookie_value(encrypted_value, key)
                else:
                    cookie_value = value
                
                if cookie_value:  # Only include cookies with values
                    cookie = {
                        'name': name,
                        'value': cookie_value,
                        'domain': host_key,
                        'path': path,
                        'expires': expires_utc,
                        'secure': bool(is_secure),
                        'httpOnly': bool(is_httponly),
                        'sameSite': 'Lax' if samesite == 1 else 'Strict' if samesite == 2 else 'None'
                    }
                    cookies.append(cookie)
            
            conn.close()
            return cookies
            
        finally:
            # Cleanup temp file
            if temp_db.exists():
                temp_db.unlink()
    
    def save_cookies(self, cookies, filename="cookies.json"):
        """Save cookies to JSON file"""
        if not cookies:
            raise ValueError("No cookies found for Suno.com")
        
        cookie_data = {
            'extracted_at': datetime.now().isoformat(),
            'domain': 'suno.com',
            'count': len(cookies),
            'cookies': cookies
        }
        
        with open(filename, 'w') as f:
            json.dump(cookie_data, f, indent=2)
        
        print(f"✅ Extracted {len(cookies)} cookies saved to {filename}")
        return filename

def main():
    """Main cookie extraction function"""
    try:
        print("🚀 Starting Suno.com cookie extraction...")
        
        # Check if Chrome is running
        if platform.system() == "Darwin":
            result = subprocess.run(['pgrep', 'Chrome'], capture_output=True)
            if result.returncode == 0:
                print("⚠️ Warning: Chrome is running. For best results, close Chrome before extraction.")
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Extraction cancelled.")
                    return
        
        extractor = ChromeCookieExtractor()
        cookies = extractor.extract_suno_cookies()
        
        if not cookies:
            print("❌ No Suno.com cookies found!")
            print("💡 Make sure you're logged into Suno.com in Chrome before running this script.")
            return
        
        # Save cookies
        filename = extractor.save_cookies(cookies)
        
        # Validate important cookies
        important_cookies = ['session', 'auth', 'token', '_session', 'connect.sid']
        found_important = [c['name'] for c in cookies if any(imp in c['name'].lower() for imp in important_cookies)]
        
        print(f"\n📋 Cookie Summary:")
        print(f"  Total cookies: {len(cookies)}")
        print(f"  Important cookies found: {found_important}")
        print(f"  Saved to: {filename}")
        
        if not found_important:
            print("⚠️ Warning: No authentication cookies found. Make sure you're logged in.")
        else:
            print("✅ Authentication cookies found! Ready for Selenium automation.")
        
        # Security reminder
        print(f"\n🔒 Security reminder:")
        print(f"  - {filename} contains sensitive session data")
        print(f"  - Add {filename} to .gitignore")
        print(f"  - Don't share this file")
        
    except Exception as e:
        print(f"❌ Cookie extraction failed: {e}")
        print("💡 Try closing Chrome and running as administrator/sudo if needed.")

if __name__ == "__main__":
    main()