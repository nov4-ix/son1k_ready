#!/usr/bin/env python3
"""
Script de prueba completo para Son1kvers3 con sistema de créditos
"""

import requests
import json
import time
import os

# Configurar API key
os.environ["SUNOAPI_KEY"] = "sk_7780f1e7602d4286b23badaac4a891bf"

API_BASE_URL = "http://localhost:8000"

def test_server_health():
    """Probar que el servidor esté funcionando"""
    print("🔍 Probando salud del servidor...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"❌ Error en servidor: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando con servidor: {e}")
        return False

def test_system_status():
    """Probar endpoint de estado del sistema"""
    print("\n💰 Probando sistema de créditos...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/system/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Sistema de créditos funcionando")
            print(f"Total créditos: {data.get('total_credits', 'N/A')}")
            print(f"Créditos usados: {data.get('used_credits', 'N/A')}")
            print(f"Créditos restantes: {data.get('remaining_credits', 'N/A')}")
            return True
        else:
            print(f"❌ Error en sistema de créditos: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando sistema de créditos: {e}")
        return False

def test_user_usage():
    """Probar endpoint de uso del usuario"""
    print("\n👤 Probando información de usuario...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/user/usage?user_id=test_user&user_tier=free", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Información de usuario obtenida")
            print(f"Tier: {data.get('tier', 'N/A')}")
            print(f"Generaciones usadas: {data.get('generations_used', 'N/A')}")
            print(f"Generaciones restantes: {data.get('remaining_generations', 'N/A')}")
            return True
        else:
            print(f"❌ Error obteniendo información de usuario: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando información de usuario: {e}")
        return False

def test_available_models():
    """Probar endpoint de modelos disponibles"""
    print("\n🎛️ Probando modelos disponibles...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/models/available?user_tier=free", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Modelos disponibles obtenidos")
            print(f"Modelos de música: {data.get('music_models', [])}")
            print(f"Configuración Ollama: {data.get('ollama_config', {}).get('model', 'N/A')}")
            return True
        else:
            print(f"❌ Error obteniendo modelos: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando modelos disponibles: {e}")
        return False

def test_music_generation():
    """Probar generación de música con créditos"""
    print("\n🎵 Probando generación de música...")
    
    try:
        payload = {
            "prompt": "música cyberpunk épica",
            "lyrics": "",
            "style": "profesional",
            "user_id": "test_user",
            "user_tier": "free",
            "model": "nuro",
            "generate_lyrics": True,
            "optimize_prompt": True
        }
        
        response = requests.post(f"{API_BASE_URL}/api/generate-with-credits", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Generación de música exitosa")
            print(f"Status: {data.get('status', 'N/A')}")
            print(f"Créditos consumidos: {data.get('credits_consumed', 'N/A')}")
            print(f"Modelo usado: {data.get('model_used', 'N/A')}")
            return True
        else:
            print(f"❌ Error en generación de música: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando generación de música: {e}")
        return False

def test_ollama_integration():
    """Probar integración con Ollama"""
    print("\n🤖 Probando integración con Ollama...")
    
    try:
        # Probar generación de letras
        payload = {
            "user_words": "resistencia digital",
            "genre": "synthwave",
            "mood": "energético",
            "structure": "verse-chorus-verse-chorus-bridge-chorus"
        }
        
        response = requests.post(f"{API_BASE_URL}/api/generate-lyrics", 
                               json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Generación de letras exitosa")
            print(f"Fuente: {data.get('source', 'N/A')}")
            print(f"Modelo: {data.get('model_used', 'N/A')}")
            return True
        else:
            print(f"❌ Error en generación de letras: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando integración con Ollama: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas completas del sistema Son1kvers3")
    print("=" * 60)
    
    tests = [
        ("Salud del Servidor", test_server_health),
        ("Sistema de Créditos", test_system_status),
        ("Información de Usuario", test_user_usage),
        ("Modelos Disponibles", test_available_models),
        ("Integración Ollama", test_ollama_integration),
        ("Generación de Música", test_music_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS COMPLETAS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! El sistema está completamente funcional.")
        print("\n✨ Características implementadas:")
        print("   • Sistema de créditos por tiers (Free/Pro/Premium)")
        print("   • Integración con Ollama para letras y prompts")
        print("   • Generación de música con SunoAPI Bridge")
        print("   • Sistema de respaldo local")
        print("   • Gestión de usuarios y límites")
        print("   • Easter eggs y funcionalidades avanzadas")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()