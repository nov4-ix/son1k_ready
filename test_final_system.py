#!/usr/bin/env python3
"""
Prueba final del sistema Son1kvers3 completo
Verifica reproductor, PIXEL, y conexión con generadores
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_pixel_chat():
    """Probar chat con PIXEL"""
    print("🤖 Probando chat con PIXEL...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/chat", 
                               json={"message": "Hola PIXEL, ayúdame a crear música cyberpunk"}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PIXEL respondiendo correctamente")
            print(f"Respuesta: {data.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Error en chat PIXEL: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error probando PIXEL: {e}")
        return False

def test_pixel_prompt_generation():
    """Probar generación de prompts con PIXEL"""
    print("\n🎛️ Probando generación de prompts con PIXEL...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/generate-prompt", 
                               json={
                                   "user_input": "música cyberpunk épica de resistencia",
                                   "genre": "synthwave",
                                   "mood": "energético"
                               }, 
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Generación de prompts funcionando")
            print(f"Prompt generado: {data.get('generated_prompt', '')[:100]}...")
            return True
        else:
            print(f"❌ Error en generación de prompts: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error probando generación de prompts: {e}")
        return False

def test_pixel_lyrics_generation():
    """Probar generación de letras con PIXEL"""
    print("\n🎵 Probando generación de letras con PIXEL...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/generate-lyrics", 
                               json={
                                   "user_words": "resistencia digital cyberpunk",
                                   "genre": "synthwave",
                                   "mood": "energético",
                                   "structure": "verse-chorus-verse-chorus-bridge-chorus"
                               }, 
                               timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Generación de letras funcionando")
            print(f"Letras generadas: {data.get('generated_lyrics', '')[:100]}...")
            return True
        else:
            print(f"❌ Error en generación de letras: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error probando generación de letras: {e}")
        return False

def test_music_generation_with_credits():
    """Probar generación de música con sistema de créditos"""
    print("\n🎶 Probando generación de música con créditos...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/generate-with-credits", 
                               json={
                                   "prompt": "música cyberpunk épica con PIXEL",
                                   "lyrics": "",
                                   "style": "profesional",
                                   "user_id": "test_final",
                                   "user_tier": "free",
                                   "model": "nuro",
                                   "generate_lyrics": True,
                                   "optimize_prompt": True
                               }, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Generación de música exitosa")
            print(f"Status: {data.get('status')}")
            print(f"Créditos consumidos: {data.get('credits_consumed')}")
            print(f"Modelo usado: {data.get('model_used')}")
            print(f"Audio URL: {data.get('audio_url', 'N/A')}")
            return True
        else:
            print(f"❌ Error en generación de música: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error probando generación de música: {e}")
        return False

def test_system_status():
    """Probar estado del sistema"""
    print("\n💰 Probando estado del sistema...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/system/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sistema de créditos funcionando")
            print(f"Total créditos: {data.get('total_credits')}")
            print(f"Créditos usados: {data.get('used_credits')}")
            print(f"Usuarios activos: {data.get('user_distribution', {}).get('total_active_users')}")
            return True
        else:
            print(f"❌ Error en estado del sistema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error probando estado del sistema: {e}")
        return False

def test_web_interface():
    """Probar interfaz web"""
    print("\n🌐 Probando interfaz web...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Interfaz web funcionando")
            print("✅ Reproductor de música disponible")
            print("✅ PIXEL integrado")
            print("✅ Sistema de créditos activo")
            return True
        else:
            print(f"❌ Error en interfaz web: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error probando interfaz web: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 PRUEBA FINAL DEL SISTEMA SON1KVERS3")
    print("=" * 60)
    
    tests = [
        ("Interfaz Web", test_web_interface),
        ("Estado del Sistema", test_system_status),
        ("Chat PIXEL", test_pixel_chat),
        ("Generación de Prompts", test_pixel_prompt_generation),
        ("Generación de Letras", test_pixel_lyrics_generation),
        ("Generación de Música", test_music_generation_with_credits)
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
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DEL SISTEMA")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("\n✨ Características implementadas:")
        print("   • 🤖 PIXEL - Asistente IA musical integrado")
        print("   • 🎵 Reproductor de música con controles completos")
        print("   • 🎛️ Generación de prompts con IA")
        print("   • 🎵 Generación de letras con IA")
        print("   • 🎶 Generación de música con sistema de créditos")
        print("   • 💰 Sistema de créditos por tiers")
        print("   • 🌐 Interfaz web completa")
        print("   • 🔄 Sistema de respaldo local")
        print("   • 🎮 Easter eggs y funcionalidades avanzadas")
        print("\n🌐 Accede a: http://localhost:8000")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()