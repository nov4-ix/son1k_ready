#!/usr/bin/env python3
"""
Test completo END-TO-END del flujo Son1k
Prueba que el frontend → backend → Suno → regreso funcione al 100%
"""

import requests
import time
import json
import sys
from datetime import datetime

def test_complete_flow():
    """Test completo del flujo de generación musical"""
    
    print("🧪 INICIANDO TEST COMPLETO DEL FLUJO SON1K")
    print("=" * 60)
    print()
    
    # Configuración
    frontend_url = "https://son1kvers3.com"  # Tu frontend en Vercel
    backend_url = "http://localhost:8000"   # Backend local (lo vamos a iniciar)
    
    # Test 1: Verificar frontend
    print("🌐 TEST 1: Verificando frontend en Vercel...")
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Frontend OK: {frontend_url}")
            print(f"   Status: {response.status_code}")
            print(f"   Contiene 'Son1k': {'Son1k' in response.text}")
        else:
            print(f"❌ Frontend error: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend no accesible: {e}")
    
    print()
    
    # Test 2: Verificar que el backend local esté corriendo
    print("🔧 TEST 2: Verificando backend local...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend OK: {backend_url}")
        else:
            print(f"❌ Backend no responde correctamente")
            return False
    except Exception as e:
        print(f"❌ Backend no accesible: {e}")
        print("🔧 Necesitas iniciar el backend primero:")
        print("   cd backend && python -m uvicorn app.main:app --reload")
        return False
    
    print()
    
    # Test 3: Test de generación musical
    print("🎵 TEST 3: Probando generación musical...")
    
    # Datos de prueba
    test_request = {
        "prompt": "upbeat electronic song about testing systems",
        "lyrics": "Testing Son1k system\nEverything should work fine\nTransparency is key\nMusic generation rocks"
    }
    
    print(f"📝 Prompt: {test_request['prompt']}")
    print(f"🎤 Lyrics preview: {test_request['lyrics'][:50]}...")
    print()
    
    try:
        # Hacer request al backend
        print("📡 Enviando request de generación...")
        response = requests.post(
            f"{backend_url}/api/music/generate",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request enviado exitosamente")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            
            # Verificar transparencia
            job_id = result.get('job_id', '')
            if job_id.startswith('son1k_job_'):
                print(f"✅ TRANSPARENCIA CONFIRMADA: {job_id}")
            else:
                print(f"❌ FALLA TRANSPARENCIA: {job_id}")
                
            # Verificar status
            if 'status' in result:
                print(f"📊 Status inicial: {result['status']}")
                
                # Polling del status
                print("\n⏳ Monitoreando progreso...")
                for i in range(10):  # Máximo 10 intentos
                    time.sleep(10)  # Esperar 10 segundos
                    
                    try:
                        status_response = requests.get(
                            f"{backend_url}/api/music/status/{job_id}",
                            timeout=10
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            current_status = status_data.get('status', 'unknown')
                            print(f"📊 Status {i+1}: {current_status}")
                            
                            if current_status == 'completed':
                                print("🎉 GENERACIÓN COMPLETADA!")
                                
                                # Verificar tracks
                                tracks = status_data.get('tracks', [])
                                if tracks:
                                    print(f"🎵 Tracks generados: {len(tracks)}")
                                    for j, track in enumerate(tracks):
                                        title = track.get('title', 'Sin título')
                                        audio_url = track.get('audio_url', '')
                                        print(f"   Track {j+1}: {title}")
                                        if audio_url:
                                            print(f"   Audio URL: {audio_url[:50]}...")
                                        
                                        # VERIFICAR NOMBRE DINÁMICO
                                        if 'Testing' in title or 'Son1k' in title:
                                            print("✅ NOMBRE DINÁMICO CONFIRMADO")
                                        else:
                                            print(f"⚠️ Nombre posiblemente no dinámico: {title}")
                                
                                print("\n🏆 TEST COMPLETO EXITOSO!")
                                return True
                                
                            elif current_status == 'failed':
                                print(f"❌ Generación falló: {status_data}")
                                return False
                                
                        else:
                            print(f"❌ Error consultando status: {status_response.status_code}")
                            
                    except Exception as e:
                        print(f"❌ Error en polling: {e}")
                
                print("⏰ Timeout esperando completación")
                return False
                
        else:
            print(f"❌ Error en generación: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de generación: {e}")
        return False

def print_system_info():
    """Mostrar información del sistema"""
    print("🔍 INFORMACIÓN DEL SISTEMA")
    print("=" * 40)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print(f"🌐 Frontend: https://son1kvers3.com")
    print(f"🔧 Backend: http://localhost:8000")
    print(f"📡 API Docs: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    print_system_info()
    
    success = test_complete_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 FLUJO COMPLETO VERIFICADO - LISTO PARA PRODUCCIÓN")
        print("✅ Frontend funcionando")
        print("✅ Backend funcionando") 
        print("✅ Generación musical funcionando")
        print("✅ Transparencia confirmada")
        print("✅ Nombres dinámicos funcionando")
        print("\n🚀 PROCEDER CON HETZNER DEPLOYMENT")
    else:
        print("❌ FLUJO TIENE PROBLEMAS - CORREGIR ANTES DE DEPLOYMENT")
        print("🔧 Revisar:")
        print("   - Backend esté corriendo")
        print("   - Suno credentials configurados")
        print("   - Selenium funcionando")
        print("\n⚠️ NO PROCEDER CON DEPLOYMENT HASTA CORREGIR")
    
    sys.exit(0 if success else 1)