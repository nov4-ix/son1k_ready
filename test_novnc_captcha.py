#!/usr/bin/env python3
"""
noVNC CAPTCHA System Validation Script
Tests the complete workflow for visual CAPTCHA resolution
"""
import os
import sys
import time
import requests
import subprocess
from pathlib import Path

def check_docker_selenium():
    """Check if Selenium container is running"""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=son1k_selenium', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        if 'son1k_selenium' in result.stdout:
            print("✅ Selenium container is running")
            return True
        else:
            print("❌ Selenium container not found")
            print("Run: docker compose up -d selenium")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def check_selenium_webdriver():
    """Test WebDriver endpoint"""
    try:
        response = requests.get("http://localhost:4444/wd/hub/status", timeout=5)
        if response.status_code == 200:
            print("✅ Selenium WebDriver is accessible")
            return True
        else:
            print(f"❌ Selenium WebDriver returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Selenium WebDriver: {e}")
        return False

def check_novnc_web():
    """Test noVNC web interface"""
    try:
        response = requests.get("http://localhost:7900", timeout=5)
        if response.status_code == 200:
            print("✅ noVNC web interface is accessible")
            return True
        else:
            print(f"❌ noVNC returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to noVNC: {e}")
        return False

def check_ngrok_tunnel():
    """Check if ngrok tunnel exists"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            https_tunnels = [t for t in tunnels if t['public_url'].startswith('https://')]
            if https_tunnels:
                public_url = https_tunnels[0]['public_url']
                print(f"✅ ngrok tunnel active: {public_url}")
                return public_url
            else:
                print("⚠️  ngrok running but no HTTPS tunnels found")
                return None
        else:
            print("⚠️  ngrok API not accessible")
            return None
    except Exception as e:
        print(f"⚠️  ngrok not running: {e}")
        print("Run: ngrok http -auth=\"son1k:captcha\" 7900")
        return None

def check_backend_api():
    """Test backend CAPTCHA API"""
    try:
        response = requests.get("http://localhost:8000/api/captcha/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend CAPTCHA API is working")
            return True
        else:
            print(f"❌ Backend API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend API: {e}")
        return False

def test_captcha_event():
    """Test CAPTCHA event notification"""
    try:
        test_event = {
            "job_id": "test_captcha_validation",
            "provider": "test",
            "status": "NEEDED",
            "novnc_url": "https://test.ngrok-free.app",
            "timestamp": int(time.time())
        }
        
        response = requests.post("http://localhost:8000/api/captcha/event", 
                               json=test_event, timeout=5)
        
        if response.status_code == 200:
            print("✅ CAPTCHA event notification works")
            
            # Test status retrieval
            status_response = requests.get(f"http://localhost:8000/api/captcha/status/{test_event['job_id']}", 
                                         timeout=5)
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data.get('status') == 'NEEDED':
                    print("✅ CAPTCHA status retrieval works")
                    
                    # Clean up test event
                    requests.delete(f"http://localhost:8000/api/captcha/status/{test_event['job_id']}")
                    return True
                else:
                    print(f"❌ CAPTCHA status mismatch: {status_data}")
                    return False
            else:
                print(f"❌ CAPTCHA status retrieval failed: {status_response.status_code}")
                return False
        else:
            print(f"❌ CAPTCHA event notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CAPTCHA event test failed: {e}")
        return False

def test_remote_browser():
    """Test creating a remote browser session"""
    try:
        # Add backend to Python path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from selenium_worker.browser_manager import BrowserManager
        
        # Set environment for remote Selenium
        os.environ["SV_SELENIUM_URL"] = "http://localhost:4444"
        os.environ["SV_HEADLESS"] = "0"  # Visible for noVNC
        
        browser_manager = BrowserManager(headless=False)
        driver = browser_manager.get_driver()
        
        # Navigate to a test page
        driver.get("https://www.google.com")
        title = driver.title
        
        if "Google" in title:
            print("✅ Remote browser session created successfully")
            print(f"   Browser title: {title}")
            browser_manager.close()
            return True
        else:
            print(f"❌ Unexpected page title: {title}")
            browser_manager.close()
            return False
            
    except Exception as e:
        print(f"❌ Remote browser test failed: {e}")
        return False

def check_environment_variables():
    """Check required environment variables"""
    required_vars = {
        'SV_SELENIUM_URL': 'http://localhost:4444',
        'NOVNC_PUBLIC_URL': 'https://your-ngrok-url.ngrok-free.app',
        'SON1K_API_BASE': 'http://localhost:8000'
    }
    
    all_set = True
    for var, example in required_vars.items():
        value = os.environ.get(var, '')
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"⚠️  {var} not set (example: {example})")
            all_set = False
    
    return all_set

def main():
    """Main validation function"""
    print("🧪 NOVNC CAPTCHA SYSTEM VALIDATION")
    print("=" * 50)
    
    success = True
    
    print("\n1. Environment Variables:")
    print("-" * 25)
    env_ok = check_environment_variables()
    if not env_ok:
        print("\n💡 Set environment variables first:")
        print("   export SV_SELENIUM_URL=\"http://localhost:4444\"")
        print("   export NOVNC_PUBLIC_URL=\"$(ngrok_url)\"")
        print("   export SON1K_API_BASE=\"http://localhost:8000\"")
    
    print("\n2. Docker Selenium:")
    print("-" * 18)
    if not check_docker_selenium():
        success = False
    
    print("\n3. Selenium WebDriver:")
    print("-" * 21)
    if not check_selenium_webdriver():
        success = False
    
    print("\n4. noVNC Web Interface:")
    print("-" * 24)
    if not check_novnc_web():
        success = False
    
    print("\n5. ngrok Tunnel:")
    print("-" * 16)
    ngrok_url = check_ngrok_tunnel()
    if ngrok_url:
        # Auto-update environment variable
        os.environ["NOVNC_PUBLIC_URL"] = ngrok_url
    
    print("\n6. Backend CAPTCHA API:")
    print("-" * 23)
    if not check_backend_api():
        success = False
    
    print("\n7. CAPTCHA Event System:")
    print("-" * 25)
    if not test_captcha_event():
        success = False
    
    print("\n8. Remote Browser Test:")
    print("-" * 23)
    if not test_remote_browser():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 ALL VALIDATION TESTS PASSED!")
        print("\n✅ Your noVNC CAPTCHA system is ready for production!")
        print("\n🚀 Usage:")
        print("   python3 scripts/run_suno_create.py")
        print("   # When CAPTCHA appears, user will get noVNC link")
        
        if ngrok_url:
            print(f"\n🖥️  noVNC URL: {ngrok_url}")
            print("   User: son1k, Pass: captcha (if auth enabled)")
    else:
        print("❌ SOME VALIDATION TESTS FAILED")
        print("\n🔧 Please fix the issues above before using the system")
        print("\n📚 See NOVNC_CAPTCHA_WORKFLOW.md for detailed setup instructions")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)