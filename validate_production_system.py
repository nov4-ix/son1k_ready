#!/usr/bin/env python3
"""
Production System Validation Script
Validates that all components of the Suno automation system work correctly
"""
import os
import sys
import time
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Core automation
        from selenium_worker.suno_automation import (
            ensure_logged_in, ensure_on_create, ensure_custom_tab,
            get_lyrics_card_and_textarea, get_styles_card, get_styles_editor,
            wait_for_generation_and_fetch_audio
        )
        print("✅ Core automation imports OK")
        
        # Browser manager
        from selenium_worker.browser_manager import BrowserManager
        print("✅ Browser manager import OK")
        
        # Click utilities
        from selenium_worker.click_utils import click_create_when_enabled
        print("✅ Click utilities import OK")
        
        # Backend integration
        from app.integrations.son1k_notify import notify_frontend, prepare_notification_payload
        print("✅ Backend integration imports OK")
        
        # API router
        from app.routers.tracks import router
        print("✅ API router import OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("🌍 Testing environment...")
    
    # Check virtual environment
    venv_path = Path(".venv")
    if venv_path.exists():
        print("✅ Virtual environment found")
    else:
        print("⚠️  Virtual environment not found")
    
    # Check profile directory
    profile_dir = os.environ.get("SV_CHROME_PROFILE_DIR", "")
    if profile_dir:
        print(f"✅ Chrome profile configured: {profile_dir}")
    else:
        print("ℹ️  Chrome profile not set (will use default)")
    
    # Check if selenium dependencies available
    try:
        import selenium
        print(f"✅ Selenium available: {selenium.__version__}")
    except ImportError:
        print("❌ Selenium not available")
        return False
    
    return True

def test_scripts():
    """Test that CLI scripts can be loaded"""
    print("📜 Testing scripts...")
    
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("❌ Scripts directory not found")
        return False
    
    try:
        # Test login script
        sys.path.insert(0, str(scripts_dir))
        import login_and_cache_session
        print("✅ Login script loadable")
        
        # Test main runner
        import run_suno_create
        print("✅ Main runner script loadable")
        
        # Test smoke test
        import smoke_styles_locator
        print("✅ Smoke test script loadable")
        
        return True
        
    except Exception as e:
        print(f"❌ Script loading failed: {e}")
        return False

def test_directories():
    """Test that required directories exist or can be created"""
    print("📁 Testing directories...")
    
    # Test artifacts directory
    artifacts_dir = Path("artifacts")
    if not artifacts_dir.exists():
        try:
            artifacts_dir.mkdir(exist_ok=True)
            print("✅ Artifacts directory created")
        except Exception as e:
            print(f"❌ Cannot create artifacts directory: {e}")
            return False
    else:
        print("✅ Artifacts directory exists")
    
    # Test screenshots directory
    screenshots_dir = Path("selenium_artifacts")
    if not screenshots_dir.exists():
        try:
            screenshots_dir.mkdir(exist_ok=True)
            print("✅ Screenshots directory created")
        except Exception as e:
            print(f"❌ Cannot create screenshots directory: {e}")
            return False
    else:
        print("✅ Screenshots directory exists")
    
    return True

def main():
    """Main validation function"""
    print("🚀 SUNO AUTOMATION SYSTEM VALIDATION")
    print("=" * 50)
    
    success = True
    
    # Run all tests
    tests = [
        ("Environment Setup", test_environment),
        ("Module Imports", test_imports),
        ("Script Loading", test_scripts),
        ("Directory Structure", test_directories),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        
        if not test_func():
            success = False
            print(f"❌ {test_name} FAILED")
        else:
            print(f"✅ {test_name} PASSED")
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 ALL VALIDATION TESTS PASSED")
        print("\n🔧 System is ready for production use!")
        print("\n📖 Next steps:")
        print("   1. Set environment variables (see PRODUCTION_READY_AUTOMATION.md)")
        print("   2. Run: python3 scripts/login_and_cache_session.py")
        print("   3. Run: python3 scripts/run_suno_create.py")
    else:
        print("❌ SOME VALIDATION TESTS FAILED")
        print("\n🔧 Please fix the issues above before using the system")
    
    print("\n📚 Documentation: PRODUCTION_READY_AUTOMATION.md")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)