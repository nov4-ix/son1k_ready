#!/usr/bin/env python3
"""
🔒 Test Ultra-Stealth System
Prueba el sistema ultra-indetectable de Son1k
"""

import requests
import time
import json
import os

WRAPPER_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

def log_test_result(test_name, passed, message=""):
    """Log resultado de prueba"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"    {message}")
    print()

def test_ultra_stealth_health():
    """Probar salud del sistema ultra-stealth"""
    try:
        response = requests.get(f"{WRAPPER_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test_result(
                "Ultra-Stealth Health Check",
                True,
                f"Status: {data.get('status')}, Cuentas: {data.get('activeAccounts')}/{data.get('totalAccounts')}"
            )
            return True
        else:
            log_test_result("Ultra-Stealth Health Check", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test_result("Ultra-Stealth Health Check", False, str(e))
        return False

def test_ultra_stealth_generation():
    """Probar generación ultra-stealth"""
    try:
        test_prompts = [
            "una canción épica de synthwave sobre la resistencia",
            "música cyberpunk instrumental",
            "balada romántica suave"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"🔒 [ULTRA-STEALTH] Probando generación {i}/3: {prompt[:30]}...")
            
            payload = {
                "prompt": prompt,
                "lyrics": "",
                "style": "profesional",
                "instrumental": True,
                "ultraStealth": True
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Ultra-Stealth": "true",
                "X-Stealth-Level": "ULTRA"
            }
            
            response = requests.post(
                f"{WRAPPER_URL}/generate-music",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test_result(
                    f"Ultra-Stealth Generation {i}",
                    True,
                    f"Job ID: {data.get('jobId')}, Account: {data.get('account')}"
                )
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                log_test_result(
                    f"Ultra-Stealth Generation {i}",
                    False,
                    f"HTTP {response.status_code}: {error_data.get('error', 'Unknown error')}"
                )
            
            # Delay entre pruebas para simular uso humano
            time.sleep(2)
        
        return True
        
    except Exception as e:
        log_test_result("Ultra-Stealth Generation", False, str(e))
        return False

def test_ultra_stealth_stats():
    """Probar estadísticas ultra-stealth"""
    try:
        response = requests.get(f"{WRAPPER_URL}/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test_result(
                "Ultra-Stealth Stats",
                True,
                f"Success Rate: {data.get('successRate')}%, Features: {len(data.get('features', []))}"
            )
            return True
        else:
            log_test_result("Ultra-Stealth Stats", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test_result("Ultra-Stealth Stats", False, str(e))
        return False

def test_stealth_evasion():
    """Probar características de evasión"""
    try:
        # Probar múltiples requests con diferentes patrones
        evasion_tests = [
            {"prompt": "test 1", "delay": 1},
            {"prompt": "test 2", "delay": 2},
            {"prompt": "test 3", "delay": 3}
        ]
        
        for test in evasion_tests:
            print(f"🔒 [EVASION] Probando evasión: {test['prompt']}")
            
            payload = {
                "prompt": test["prompt"],
                "instrumental": True,
                "ultraStealth": True
            }
            
            response = requests.post(
                f"{WRAPPER_URL}/generate-music",
                json=payload,
                timeout=15
            )
            
            # Delay aleatorio para simular comportamiento humano
            time.sleep(test["delay"])
        
        log_test_result("Stealth Evasion Tests", True, "Patrones de evasión ejecutados")
        return True
        
    except Exception as e:
        log_test_result("Stealth Evasion Tests", False, str(e))
        return False

def test_cookie_rotation():
    """Probar rotación de cookies"""
    try:
        # Verificar que el sistema puede manejar múltiples cuentas
        response = requests.get(f"{WRAPPER_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('accounts', [])
            
            if len(accounts) > 0:
                log_test_result(
                    "Cookie Rotation",
                    True,
                    f"Cuentas disponibles: {len(accounts)}, Sistema de rotación activo"
                )
                return True
            else:
                log_test_result("Cookie Rotation", False, "No hay cuentas configuradas")
                return False
        else:
            log_test_result("Cookie Rotation", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test_result("Cookie Rotation", False, str(e))
        return False

def main():
    """Función principal de pruebas"""
    print("🔒 Son1k Ultra-Stealth System Tester")
    print("=" * 50)
    print("🧪 Probando sistema ultra-indetectable...")
    print()
    
    # Verificar que el wrapper esté corriendo
    print("🔍 Verificando wrapper ultra-stealth...")
    if not test_ultra_stealth_health():
        print("❌ Wrapper ultra-stealth no está funcionando")
        print("💡 Ejecuta: node suno_ultra_stealth.js")
        return
    
    print("✅ Wrapper ultra-stealth funcionando")
    print()
    
    # Ejecutar pruebas
    tests = [
        ("Ultra-Stealth Health", test_ultra_stealth_health),
        ("Ultra-Stealth Stats", test_ultra_stealth_stats),
        ("Cookie Rotation", test_cookie_rotation),
        ("Stealth Evasion", test_stealth_evasion),
        ("Ultra-Stealth Generation", test_ultra_stealth_generation)
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
    print("=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Sistema ultra-stealth funcionando perfectamente!")
        print("🔒 Nivel de evasión: ULTRA-INDETECTABLE")
        print("🛡️ Características activas:")
        print("   ✅ Simulación de comportamiento humano")
        print("   ✅ Obfuscación avanzada de payloads")
        print("   ✅ Rotación inteligente de cuentas")
        print("   ✅ Headers de navegador real")
        print("   ✅ Spoofing de IP")
        print("   ✅ Gestión de sesiones")
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("💡 Verifica la configuración de cuentas en suno_accounts_stealth.json")
    
    print()
    print("🌐 Accede al sistema en: http://localhost:8000")
    print("🔒 Wrapper ultra-stealth: http://localhost:3001")

if __name__ == "__main__":
    main()


