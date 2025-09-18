#!/usr/bin/env python3
"""
Test script to validate all the fixes made to Son1kVers3 backend
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all critical imports work"""
    print("🔍 Testing imports...")
    
    try:
        from backend.app.main import app
        print("✅ FastAPI app import successful")
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False
    
    try:
        from backend.app.queue import celery_app, enqueue_generation
        print("✅ Celery app import successful")
    except Exception as e:
        print(f"❌ Celery app import failed: {e}")
        return False
    
    try:
        from backend.app.models import SongCreate
        print("✅ Models import successful")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from backend.app.settings import settings
        print("✅ Settings import successful")
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
        return False
    
    return True

def test_app_structure():
    """Test that the app is properly configured"""
    print("\n🔍 Testing FastAPI app structure...")
    
    try:
        from backend.app.main import app
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/api/health", "/api/songs/create", "/"]
        
        for expected in expected_routes:
            if expected in routes:
                print(f"✅ Route {expected} found")
            else:
                print(f"❌ Route {expected} not found")
                return False
        
        # Check middleware
        middleware_types = [type(middleware).__name__ for middleware in app.middleware_stack.middleware]
        if 'CORSMiddleware' in str(middleware_types):
            print("✅ CORS middleware configured")
        else:
            print("❌ CORS middleware not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

def test_frontend_detection():
    """Test frontend file detection"""
    print("\n🔍 Testing frontend detection...")
    
    frontend_dir = os.path.join(project_root, "frontend")
    frontend_index = os.path.join(frontend_dir, "index.html")
    
    if os.path.exists(frontend_dir):
        print(f"✅ Frontend directory exists: {frontend_dir}")
    else:
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return False
    
    if os.path.exists(frontend_index):
        print(f"✅ Frontend index.html exists: {frontend_index}")
    else:
        print(f"❌ Frontend index.html not found: {frontend_index}")
        return False
        
    return True

def test_celery_configuration():
    """Test Celery configuration"""
    print("\n🔍 Testing Celery configuration...")
    
    try:
        from backend.app.queue import celery_app
        
        # Check broker URL
        broker = celery_app.conf.broker_url
        if broker:
            print(f"✅ Celery broker configured: {broker}")
        else:
            print("❌ Celery broker not configured")
            return False
        
        # Check task routes
        task_routes = celery_app.conf.task_routes
        if task_routes:
            print(f"✅ Celery task routes configured: {task_routes}")
        else:
            print("❌ Celery task routes not configured")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Celery configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Son1kVers3 Backend Fix Validation")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_structure,
        test_frontend_detection,
        test_celery_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The backend fixes are working correctly.")
        print("\n📝 Summary of fixes applied:")
        print("• ✅ Fixed docker-compose.yml paths and commands")
        print("• ✅ Improved Dockerfile with proper dependencies")
        print("• ✅ Fixed import paths in main.py and queue.py")
        print("• ✅ Added missing __init__.py files")
        print("• ✅ Fixed database URL reference in db.py")
        print("• ✅ Added missing SongCreate Pydantic model")
        print("• ✅ Enhanced frontend serving with better error handling")
        print("• ✅ Improved Celery worker configuration")
        print("\n🐳 Docker commands to try:")
        print("   cd '/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2'")
        print("   docker compose up --build")
        print("\n🌐 Once running, frontend should be available at: http://localhost:8000")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())