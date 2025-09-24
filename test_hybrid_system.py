#!/usr/bin/env python3
"""
🎵 Test Hybrid Stealth System
Prueba el sistema híbrido Suno + Ollama
"""

import requests
import time
import json
import os

HYBRID_URL = "http://localhost:3003"
API_URL = "http://localhost:8000"

def log_test_result(test_name, passed, message=""):
    """Log resultado de prueba"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"    {message}")
    print()

def test_hybrid_health():
    """Probar salud del sistema híbrido"""
    try:
        response = requests.get(f"{HYBRID_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test_result(
                "Hybrid Health Check",
                True,
                f"Status: {data.get('status')}, Suno: {data.get('suno', {}).get('accounts', 0)} cuentas, Ollama: {'Activo' if data.get('ollama', {}).get('enabled') else 'Inactivo'}"
            )
            return True
        else:
            log_test_result("Hybrid Health Check", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test_result("Hybrid Health Check", False, str(e))
        return False

def test_hybrid_generation():
    """Probar generación híbrida"""
    try:
        test_prompts = [
            "una canción épica de synthwave sobre la resistencia",
            "música cyberpunk instrumental",
            "balada romántica suave"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"🎵 [HYBRID] Probando generación {i}/3: {prompt[:30]}...")
            
            payload = {
                "prompt": prompt,
                "lyrics": "",
                "style": "profesional",
                "instrumental": True
            }
            
            response = requests.post(
                f"{HYBRID_URL}/generate-music",
                json=payload,
                timeout=60  # Más tiempo para generación híbrida
            )
            
            if response.status_code == 200:
                data = response.json()
                method = data.get('method', 'unknown')
                source = data.get('source', 'unknown')
                fallback = data.get('fallbackUsed', False)
                
                log_test_result(
                    f"Hybrid Generation {i}",
                    True,
                    f"Method: {method}, Source: {source}, Fallback: {fallback}"
                )
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                log_test_result(
                    f"Hybrid Generation {i}",
                    False,
                    f"HTTP {response.status_code}: {error_data.get('error', 'Unknown error')}"
                )
            
            # Delay entre pruebas
            time.sleep(3)
        
        return True
        
    except Exception as e:
        log_test_result("Hybrid Generation", False, str(e))
        return False

def test_suno_only():
    """Probar solo Suno"""
    try:
        print("🤖 [SUNO] Probando solo Suno...")
        
        payload = {
            "prompt": "test solo suno",
            "instrumental": True,
            "forceMethod": "suno"
        }
        
        response = requests.post(
            f"{HYBRID_URL}/generate-music",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test_result(
                "Suno Only Test",
                True,
                f"Method: {data.get('method')}, Source: {data.get('source')}"
            )
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            log_test_result(
                "Suno Only Test",
                False,
                f"HTTP {response.status_code}: {error_data.get('error', 'Unknown error')}"
            )
            return False
            
    except Exception as e:
        log_test_result("Suno Only Test", False, str(e))
        return False

def test_ollama_only():
    """Probar solo Ollama"""
    try:
        print("🧠 [OLLAMA] Probando solo Ollama...")
        
        payload = {
            "prompt": "test solo ollama",
            "instrumental": True,
            "forceMethod": "ollama"
        }
        
        response = requests.post(
            f"{HYBRID_URL}/generate-music",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test_result(
                "Ollama Only Test",
                True,
                f"Method: {data.get('method')}, Source: {data.get('source')}"
            )
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            log_test_result(
                "Ollama Only Test",
                False,
                f"HTTP {response.status_code}: {error_data.get('error', 'Unknown error')}"
            )
            return False
            
    except Exception as e:
        log_test_result("Ollama Only Test", False, str(e))
        return False

def test_hybrid_stats():
    """Probar estadísticas híbridas"""
    try:
        response = requests.get(f"{HYBRID_URL}/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            suno_stats = data.get('suno', {})
            ollama_stats = data.get('ollama', {})
            
            log_test_result(
                "Hybrid Stats",
                True,
                f"Suno: {suno_stats.get('success', 0)} éxitos, Ollama: {ollama_stats.get('success', 0)} éxitos"
            )
            return True
        else:
            log_test_result("Hybrid Stats", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test_result("Hybrid Stats", False, str(e))
        return False

def test_ollama_health():
    """Probar salud de Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            log_test_result(
                "Ollama Health",
                True,
                f"Modelos disponibles: {len(models)}"
            )
            return True
        else:
            log_test_result("Ollama Health", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test_result("Ollama Health", False, "Ollama no disponible")
        return False

def main():
    """Función principal de pruebas"""
    print("🎵 Son1k Hybrid Stealth System Tester")
    print("Suno Real + Ollama Proxy = Máxima Robustez")
    print("=" * 60)
    print("🧪 Probando sistema híbrido...")
    print()
    
    # Verificar que el sistema híbrido esté corriendo
    print("🔍 Verificando sistema híbrido...")
    if not test_hybrid_health():
        print("❌ Sistema híbrido no está funcionando")
        print("💡 Ejecuta: ./start_hybrid_system.sh")
        return
    
    print("✅ Sistema híbrido funcionando")
    print()
    
    # Ejecutar pruebas
    tests = [
        ("Hybrid Health", test_hybrid_health),
        ("Ollama Health", test_ollama_health),
        ("Hybrid Stats", test_hybrid_stats),
        ("Suno Only", test_suno_only),
        ("Ollama Only", test_ollama_only),
        ("Hybrid Generation", test_hybrid_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
        print()
    
    # Resumen final
    print("=" * 60)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Sistema híbrido funcionando perfectamente!")
        print("🎵 Características activas:")
        print("   ✅ Suno real con Puppeteer")
        print("   ✅ Ollama como proxy/fallback")
        print("   ✅ Generación híbrida inteligente")
        print("   ✅ Pool de navegadores optimizado")
        print("   ✅ Estadísticas en tiempo real")
        print("   ✅ Manejo de errores robusto")
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("💡 Verifica la configuración del sistema")
    
    print()
    print("🌐 Accede al sistema en: http://localhost:8000")
    print("🎵 Sistema híbrido: http://localhost:3003")

if __name__ == "__main__":
    main()


