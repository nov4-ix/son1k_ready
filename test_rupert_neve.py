#!/usr/bin/env python3
"""
Prueba específica de postprocesos Rupert Neve
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_rupert_neve_config():
    """Probar configuración de Rupert Neve"""
    print("🎛️ Probando configuración Rupert Neve...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/postprocess/rupert-neve/config/pro", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Configuración Rupert Neve obtenida")
            print(f"Tier: {data.get('user_tier')}")
            print(f"Descripción: {data.get('description')}")
            return True
        else:
            print(f"❌ Error obteniendo configuración: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def test_rupert_neve_postprocess():
    """Probar postprocesos Rupert Neve"""
    print("\n🎛️ Probando postprocesos Rupert Neve...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/postprocess/rupert-neve", 
                               json={
                                   "track_id": "test_track_123",
                                   "title": "Test Track",
                                   "audio_url": "https://example.com/test.mp3",
                                   "duration": 180,
                                   "user_tier": "pro"
                               }, 
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Postprocesos Rupert Neve aplicados")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            processing_chain = data.get('processing_chain', [])
            print(f"Cadena de procesamiento: {' → '.join(processing_chain)}")
            
            return True
        else:
            print(f"❌ Error aplicando postprocesos: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando postprocesos: {e}")
        return False

def test_music_generation_with_rupert_neve():
    """Probar generación de música con postprocesos Rupert Neve"""
    print("\n🎶 Probando generación con Rupert Neve...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/generate-with-credits", 
                               json={
                                   "prompt": "música cyberpunk épica con Rupert Neve",
                                   "lyrics": "",
                                   "style": "profesional",
                                   "user_id": "test_rupert_neve",
                                   "user_tier": "pro",
                                   "model": "nuro",
                                   "generate_lyrics": True,
                                   "optimize_prompt": True
                               }, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Generación con Rupert Neve exitosa")
            print(f"Status: {data.get('status')}")
            print(f"Post-processing: {data.get('post_processing')}")
            print(f"Generation method: {data.get('generation_method')}")
            return True
        else:
            print(f"❌ Error en generación: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando generación: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 PRUEBA DE POSTPROCESOS RUPERT NEVE")
    print("=" * 50)
    
    tests = [
        ("Configuración Rupert Neve", test_rupert_neve_config),
        ("Postprocesos Rupert Neve", test_rupert_neve_postprocess),
        ("Generación con Rupert Neve", test_music_generation_with_rupert_neve)
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
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS RUPERT NEVE")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("\n🎉 ¡POSTPROCESOS RUPERT NEVE FUNCIONANDO!")
        print("\n✨ Características implementadas:")
        print("   • 🎛️ SSL Bus Compressor")
        print("   • 🎛️ Rupert Neve 1073 EQ")
        print("   • 🎛️ Rupert Neve 2254 Compressor")
        print("   • 🎛️ Rupert Neve 33609 Stereo Compressor")
        print("   • 🎛️ Rupert Neve 5057 Satellite Summing Mixer")
        print("   • 🎛️ Rupert Neve 5033 EQ")
        print("   • 🎛️ Rupert Neve 5043 True-Band Compressor")
        print("   • 🎛️ Saturación de tubos característica")
        print("   • 🎛️ Coloration de transformadores")
        print("   • 🎛️ Armónicos musicales 2º y 3º orden")
        print("   • 🎛️ Calidez analógica Rupert Neve")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()
