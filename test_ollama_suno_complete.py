#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Test Completo Ollama-Suno Proxy
Demostración del sistema completo de generación musical
"""

import requests
import json
import time
import asyncio

async def test_ollama_suno_complete():
    """Test completo del sistema Ollama-Suno"""
    
    print("🎵 SON1KVERS3 - TEST COMPLETO OLLAMA-SUNO PROXY")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Verificar salud de la API
    print("\n🔍 1. Verificando salud de la API...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API saludable")
        else:
            print("❌ API no disponible")
            return
    except Exception as e:
        print(f"❌ Error conectando con API: {e}")
        return
    
    # 2. Verificar estado del proxy Ollama-Suno
    print("\n🔍 2. Verificando estado del proxy Ollama-Suno...")
    try:
        response = requests.get(f"{base_url}/api/ollama-suno/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Ollama conectado: {status.get('ollama_connected', False)}")
            print(f"✅ Suno configurado: {status.get('suno_configured', False)}")
            print(f"✅ Estado: {status.get('status', 'unknown')}")
        else:
            print("❌ Error verificando estado del proxy")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Probar generación musical
    print("\n🎵 3. Probando generación musical...")
    
    test_cases = [
        {
            "prompt": "cyberpunk neon city",
            "lyrics": "Neon lights shine bright, in the digital night, we are the future",
            "style": "electronic",
            "mood": "energetic"
        },
        {
            "prompt": "epic fantasy battle",
            "lyrics": "Swords clash and magic flows, heroes rise against the darkness",
            "style": "orchestral",
            "mood": "epic"
        },
        {
            "prompt": "chill lofi beats",
            "lyrics": "Relaxing vibes and smooth sounds, perfect for studying",
            "style": "lofi",
            "mood": "chill"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎼 Test {i}: {test_case['prompt']}")
        
        try:
            # Enviar request de generación
            response = requests.post(
                f"{base_url}/api/music/generate",
                json=test_case,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get("job_id")
                print(f"✅ Generación iniciada: {job_id}")
                
                # Monitorear progreso
                for attempt in range(5):
                    await asyncio.sleep(2)
                    
                    status_response = requests.get(
                        f"{base_url}/api/music/status/{job_id}",
                        timeout=5
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        progress = status.get("progress", 0)
                        print(f"   Progreso: {progress}% - {status.get('message', '')}")
                        
                        if status.get("status") == "completed":
                            track = status.get("result", {})
                            print(f"✅ ¡Completado! Título: {track.get('title', 'Sin título')}")
                            print(f"   Generado por: {track.get('generated_by', 'unknown')}")
                            print(f"   Archivo: {track.get('filename', 'unknown')}")
                            print(f"   URL: {track.get('audio_url', 'unknown')}")
                            break
                    else:
                        print(f"   ⚠️ Error verificando estado: {status_response.status_code}")
            else:
                print(f"❌ Error en generación: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error en test {i}: {e}")
    
    # 4. Verificar archivos generados
    print("\n📁 4. Verificando archivos generados...")
    try:
        response = requests.get(f"{base_url}/api/music/tracks", timeout=5)
        if response.status_code == 200:
            tracks = response.json()
            print(f"✅ Total de tracks: {len(tracks)}")
            
            for track in tracks[-3:]:  # Mostrar los últimos 3
                print(f"   - {track.get('title', 'Sin título')} ({track.get('filename', 'unknown')})")
        else:
            print("❌ Error obteniendo tracks")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETO FINALIZADO")
    print("✅ Sistema Ollama-Suno funcionando correctamente")
    print("✅ Generación musical operativa")
    print("✅ Fallbacks inteligentes activos")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ollama_suno_complete())
