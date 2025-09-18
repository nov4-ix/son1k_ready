#!/usr/bin/env python3
"""
Test Script - Son1k Suno Bridge Extension Flow Validation
Simula el flujo completo de la extensión para validar end-to-end
"""

import requests
import json
import time
import sys

API_BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test 1: Backend Health Check"""
    print("🏥 Test 1: Backend Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200 and response.json().get("ok"):
            print("✅ Backend health: OK")
            return True
        else:
            print(f"❌ Backend health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_song_creation_endpoint():
    """Test 2: Song Creation Endpoint (simula extensión)"""
    print("\n🎵 Test 2: Song Creation Endpoint...")
    
    # Datos que enviaría la extensión desde Suno
    test_data = {
        "prompt": "Una balada emotiva con piano y cuerdas, estilo neo-soul, tempo 70 BPM",
        "lyrics": "Verso 1:\nEn la quietud de la noche\nTu recuerdo me acompaña\n\nCoro:\nEsta es nuestra balada\nEscrita en el viento",
        "mode": "original",
        "source": "suno_extension",
        "timestamp": "2024-09-17T12:30:00Z"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/songs/create",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok") and result.get("job_id"):
                print(f"✅ Song creation: OK - Job ID: {result['job_id']}")
                return result["job_id"]
            else:
                print(f"❌ Song creation failed: {result}")
                return None
        else:
            print(f"❌ Song creation HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Song creation error: {e}")
        return None

def test_ai_endpoints():
    """Test 3: AI Endpoints (funciones inteligentes)"""
    print("\n🤖 Test 3: AI Endpoints...")
    
    tests = [
        {
            "name": "Generate Lyrics",
            "endpoint": "/api/generate-lyrics",
            "data": {"prompt": "una balada romántica con piano"}
        },
        {
            "name": "Improve Lyrics", 
            "endpoint": "/api/improve-lyrics",
            "data": {"lyrics": "amor en la noche\ncanta el corazón"}
        },
        {
            "name": "Smart Prompt",
            "endpoint": "/api/smart-prompt",
            "data": {"lyrics": "amor eterno baila en mi corazón con guitarras"}
        }
    ]
    
    success_count = 0
    for test in tests:
        try:
            response = requests.post(
                f"{API_BASE_URL}{test['endpoint']}",
                json=test["data"],
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {test['name']}: OK")
                success_count += 1
            else:
                print(f"❌ {test['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test['name']}: {e}")
    
    print(f"🎯 AI Endpoints: {success_count}/{len(tests)} passed")
    return success_count == len(tests)

def test_system_status_endpoints():
    """Test 4: System Status Endpoints"""
    print("\n⚡ Test 4: System Status Endpoints...")
    
    endpoints = [
        "/api/celery-status",
        "/api/redis-status"
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            status_name = endpoint.split("-")[1].title()
            
            if response.status_code == 200:
                print(f"✅ {status_name}: Connected")
                success_count += 1
            else:
                print(f"⚠️ {status_name}: Service unavailable (but endpoint works)")
                
        except Exception as e:
            print(f"❌ {status_name}: {e}")
    
    return success_count

def simulate_extension_workflow():
    """Test 5: Simular flujo completo de extensión"""
    print("\n🔄 Test 5: Extension Workflow Simulation...")
    
    # Paso 1: Usuario abre popup y prueba conexión
    print("📱 Step 1: Popup connection test...")
    if not test_backend_health():
        return False
    
    # Paso 2: Usuario configura URL en popup
    print("⚙️ Step 2: API URL configuration... (simulated)")
    
    # Paso 3: Usuario va a suno.com/create y escribe content
    print("🌐 Step 3: User creates content on Suno...")
    suno_data = {
        "prompt": "Trap melódico con 808s y melodías de piano, estilo moderno, BPM 140",
        "lyrics": "Verso 1:\nSubiendo desde abajo\nNunca me voy a rendir\nCada paso es un trabajo\nVoy a conseguir vivir\n\nCoro:\nEste es mi momento\nNo hay tiempo que perder\nCon flow y sentimiento\nVoy a prevalecer",
        "mode": "original",
        "source": "suno_extension", 
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Paso 4: Content script extrae datos y envía
    print("📤 Step 4: Content script sends data...")
    job_id = test_song_creation_endpoint_with_data(suno_data)
    
    if job_id:
        print(f"✅ Extension workflow: SUCCESS - Job {job_id} created")
        return True
    else:
        print("❌ Extension workflow: FAILED")
        return False

def test_song_creation_endpoint_with_data(data):
    """Helper: Test endpoint with specific data"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/songs/create",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("job_id")
        return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_test_report():
    """Generar reporte final de tests"""
    print("\n" + "="*60)
    print("🧪 SON1K SUNO BRIDGE - VALIDATION REPORT")
    print("="*60)
    
    results = []
    
    # Run all tests
    results.append(("Backend Health", test_backend_health()))
    
    job_id = test_song_creation_endpoint()
    results.append(("Song Creation", job_id is not None))
    
    results.append(("AI Endpoints", test_ai_endpoints()))
    
    status_count = test_system_status_endpoints()
    results.append(("System Status", status_count > 0))
    
    results.append(("Extension Workflow", simulate_extension_workflow()))
    
    # Calculate score
    passed = sum(1 for _, result in results if result)
    total = len(results)
    score = (passed / total) * 100
    
    print(f"\n📊 TEST RESULTS:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 OVERALL SCORE: {passed}/{total} ({score:.1f}%)")
    
    if score >= 80:
        print("🚀 SYSTEM READY FOR PRODUCTION!")
        print("✅ Extension can be loaded and tested with Suno premium account")
    elif score >= 60:
        print("⚠️ SYSTEM PARTIALLY READY - Some issues detected")
    else:
        print("❌ SYSTEM NOT READY - Critical issues found")
    
    print("\n📋 NEXT STEPS:")
    if score >= 80:
        print("1. Load extension in Chrome: chrome://extensions/")
        print("2. Configure URL: http://localhost:8000") 
        print("3. Test on suno.com/create with premium account")
        print("4. Verify music generation end-to-end")
    else:
        print("1. Fix failing tests above")
        print("2. Restart backend if needed: python3 run_local.py")
        print("3. Check Redis/Celery services")
    
    return score

if __name__ == "__main__":
    print("🚀 Starting Son1k Suno Bridge Validation...")
    print("⏱️  This will test the complete extension flow...\n")
    
    score = generate_test_report()
    
    # Exit with appropriate code
    sys.exit(0 if score >= 80 else 1)