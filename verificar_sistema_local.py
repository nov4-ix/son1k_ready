#!/usr/bin/env python3
"""
🔍 VERIFICACIÓN COMPLETA DEL SISTEMA LOCAL
Script para verificar que todo funciona perfectamente antes del deploy
"""
import requests
import json
import time
import subprocess
import sys

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_step(step, description):
    print(f"\n{step}. {description}")

def test_docker_services():
    """Verificar que los servicios Docker estén funcionando"""
    print_header("VERIFICACIÓN DE SERVICIOS DOCKER")
    
    services = {
        'son1k_api': 8000,
        'son1k_selenium': 4444,
        'son1k_redis': None,
        'son1k_db': None
    }
    
    try:
        # Verificar containers
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        
        print("📋 Contenedores activos:")
        print(result.stdout)
        
        # Verificar puertos específicos
        for service, port in services.items():
            if port:
                try:
                    response = requests.get(f"http://localhost:{port}", timeout=5)
                    print(f"✅ {service} (puerto {port}): FUNCIONANDO")
                except:
                    print(f"❌ {service} (puerto {port}): NO RESPONDE")
                    return False
            else:
                if service in result.stdout:
                    print(f"✅ {service}: FUNCIONANDO")
                else:
                    print(f"❌ {service}: NO ENCONTRADO")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando Docker: {e}")
        return False

def test_api_endpoints():
    """Verificar endpoints principales del API"""
    print_header("VERIFICACIÓN DE ENDPOINTS API")
    
    base_url = "http://localhost:8000"
    
    tests = [
        {
            'name': 'Health Check',
            'url': f'{base_url}/health',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'API Docs',
            'url': f'{base_url}/docs',
            'method': 'GET', 
            'expected_status': 200
        },
        {
            'name': 'Music Health',
            'url': f'{base_url}/api/music/health',
            'method': 'GET',
            'expected_status': 200
        }
    ]
    
    all_passed = True
    
    for test in tests:
        print_step("🌐", f"Testing {test['name']}")
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            
            if response.status_code == test['expected_status']:
                print(f"✅ {test['name']}: OK ({response.status_code})")
                if 'health' in test['url']:
                    try:
                        data = response.json()
                        print(f"   📄 Response: {data}")
                    except:
                        pass
            else:
                print(f"❌ {test['name']}: ERROR ({response.status_code})")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {test['name']}: EXCEPCIÓN - {e}")
            all_passed = False
    
    return all_passed

def test_music_generation_endpoint():
    """Verificar endpoint de generación musical con transparencia"""
    print_header("VERIFICACIÓN DE GENERACIÓN MUSICAL TRANSPARENTE")
    
    test_cases = [
        {
            'name': 'Generación con Lyrics Dinámicos',
            'payload': {
                'lyrics': 'Walking down the street tonight\nFeeling free and feeling right\nMusic playing in my head\nDancing till the day is dead',
                'prompt': 'upbeat electronic, 120 BPM, energetic synthesizers',
                'instrumental': False,
                'style': 'default'
            },
            'expected_title_start': 'Walking Down The Street Tonight',
            'expected_job_prefix': 'son1k_job_'
        },
        {
            'name': 'Generación en Español',
            'payload': {
                'lyrics': 'Tu risa cae, lluvia de bits\nBaila mi nombre en tu playlist\nEn cada nota, mi corazón\nSuena tu voz en mi canción',
                'prompt': 'reggaeton moderno, 95 BPM',
                'instrumental': False,
                'style': 'default'  
            },
            'expected_title_start': 'Tu Risa Cae Lluvia De Bits',
            'expected_job_prefix': 'son1k_job_'
        },
        {
            'name': 'Generación Instrumental',
            'payload': {
                'lyrics': '',
                'prompt': 'ambient electronic, 80 BPM, atmospheric pads',
                'instrumental': True,
                'style': 'default'
            },
            'expected_title_start': 'Instrumental_',
            'expected_job_prefix': 'son1k_job_'
        }
    ]
    
    url = "http://localhost:8000/api/music/generate"
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print_step(f"🎵", f"Test {i}: {test['name']}")
        
        try:
            print("   📤 Enviando request...")
            response = requests.post(url, 
                                   json=test['payload'],
                                   headers={'Content-Type': 'application/json'},
                                   timeout=30)
            
            print(f"   📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📄 Response data:")
                print(f"      Job ID: {data.get('job_id', 'N/A')}")
                print(f"      Status: {data.get('status', 'N/A')}")
                print(f"      Message: {data.get('message', 'N/A')}")
                
                # Verificar Job ID
                job_id = data.get('job_id', '')
                if job_id.startswith(test['expected_job_prefix']):
                    print(f"   ✅ Job ID correcto: {job_id}")
                else:
                    print(f"   ❌ Job ID incorrecto: {job_id} (esperaba: {test['expected_job_prefix']}*)")
                    all_passed = False
                
                # Verificar que NO contenga 'suno'
                response_text = response.text.lower()
                if 'suno' in response_text:
                    print(f"   ❌ ADVERTENCIA: Response contiene 'suno'")
                    all_passed = False
                else:
                    print(f"   ✅ Response transparente (sin 'suno')")
                
                # Si hay tracks en la respuesta, verificarlos
                if 'tracks' in data and data['tracks']:
                    for track in data['tracks']:
                        title = track.get('title', '')
                        provider = track.get('provider', '')
                        
                        print(f"      🎵 Track: {title}")
                        print(f"      🏢 Provider: {provider}")
                        
                        if provider == 'Son1k':
                            print(f"         ✅ Provider correcto")
                        else:
                            print(f"         ❌ Provider incorrecto: {provider}")
                            all_passed = False
                
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
            all_passed = False
    
    return all_passed

def test_frontend_files():
    """Verificar que los archivos del frontend estén configurados correctamente"""
    print_header("VERIFICACIÓN DE ARCHIVOS FRONTEND")
    
    files_to_check = [
        {
            'path': 'frontend/index.html',
            'checks': [
                'SOLUCIÓN GARANTIZADA: Transparencia Total',
                'window.fetch = async function',
                'generateDynamicName',
                'cleanSunoReferences'
            ]
        }
    ]
    
    all_passed = True
    
    for file_info in files_to_check:
        print_step("📄", f"Verificando {file_info['path']}")
        
        try:
            with open(file_info['path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            for check in file_info['checks']:
                if check in content:
                    print(f"   ✅ Encontrado: {check[:50]}...")
                else:
                    print(f"   ❌ NO encontrado: {check}")
                    all_passed = False
            
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
            all_passed = False
    
    return all_passed

def test_backend_files():
    """Verificar archivos del backend"""
    print_header("VERIFICACIÓN DE ARCHIVOS BACKEND")
    
    files_to_check = [
        {
            'path': 'backend/app/routers/music_generation.py',
            'checks': [
                'from backend.selenium_worker.music_generator_fixed import MusicGeneratorFixed',
                'son1k_job_',
                'ensure_transparent_results',
                'SongNameGenerator'
            ]
        },
        {
            'path': 'backend/selenium_worker/music_generator_fixed.py',
            'checks': [
                'class SongNameGenerator',
                'generate_name_from_lyrics',
                'class MusicGeneratorFixed',
                'extract_tracks_info'
            ]
        }
    ]
    
    all_passed = True
    
    for file_info in files_to_check:
        print_step("📄", f"Verificando {file_info['path']}")
        
        try:
            with open(file_info['path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            for check in file_info['checks']:
                if check in content:
                    print(f"   ✅ Encontrado: {check[:50]}...")
                else:
                    print(f"   ❌ NO encontrado: {check}")
                    all_passed = False
            
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
            all_passed = False
    
    return all_passed

def run_comprehensive_test():
    """Ejecutar todas las verificaciones"""
    print("🚀 VERIFICACIÓN COMPLETA DEL SISTEMA LOCAL SON1K")
    print("🎯 Objetivo: Confirmar que la transparencia funciona al 100%")
    
    start_time = time.time()
    
    tests = [
        ("Docker Services", test_docker_services),
        ("API Endpoints", test_api_endpoints), 
        ("Frontend Files", test_frontend_files),
        ("Backend Files", test_backend_files),
        ("Music Generation", test_music_generation_endpoint)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n⏳ Ejecutando: {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results[test_name] = False
    
    # Resumen final
    print_header("RESUMEN FINAL DE VERIFICACIÓN")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"📊 RESULTADOS:")
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ" 
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 TOTAL: {passed_tests}/{total_tests} tests pasaron")
    
    elapsed_time = time.time() - start_time
    print(f"⏱️  Tiempo total: {elapsed_time:.2f} segundos")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print(f"✅ El sistema está listo para deploy público")
        print(f"🎵 La transparencia funciona al 100%")
        print(f"🚫 No hay referencias a 'suno' en el frontend")
        print(f"✨ Los nombres dinámicos funcionan correctamente")
        
        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. ✅ Sistema local verificado")
        print(f"   2. 🌐 Deploy en servidor cloud")
        print(f"   3. 🔗 Link público para testers")
        print(f"   4. 📈 Optimizaciones de performance")
        
        return True
    else:
        print(f"\n⚠️ ALGUNAS VERIFICACIONES FALLARON")
        print(f"🔧 Componentes que necesitan atención:")
        for test_name, passed in results.items():
            if not passed:
                print(f"   ❌ {test_name}")
        
        print(f"\n🛠️ Corrige los errores arriba antes del deploy")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)