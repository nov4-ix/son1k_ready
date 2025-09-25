#!/usr/bin/env python3
"""
Script de prueba para el sistema Son1k con Suno Stealth
"""
import asyncio
import aiohttp
import json
import time

async def test_stealth_generation():
    """Probar la generación de música con Suno Stealth"""
    
    print("🚀 Iniciando prueba de Son1k Stealth Generator...")
    
    # Verificar que el servidor Node.js esté funcionando
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:3001/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Suno Stealth Wrapper: {data['status']} (v{data['version']})")
                    print(f"🍪 Cookies disponibles: {data['cookies']['total']}")
                else:
                    print(f"❌ Suno Stealth Wrapper no disponible: HTTP {response.status}")
                    return
    except Exception as e:
        print(f"❌ Error conectando con Suno Stealth Wrapper: {e}")
        return
    
    # Verificar que el servidor Python esté funcionando
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Son1k Python Server: {data['status']}")
                else:
                    print(f"❌ Son1k Python Server no disponible: HTTP {response.status}")
                    return
    except Exception as e:
        print(f"❌ Error conectando con Son1k Python Server: {e}")
        return
    
    # Probar generación de música
    print("\n🎵 Probando generación de música...")
    
    test_prompts = [
        "una balada rock sobre el amor perdido",
        "música electrónica futurista",
        "jazz suave para relajarse"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Prueba {i}: {prompt} ---")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Enviar petición de generación
                payload = {
                    "prompt": prompt,
                    "lyrics": "",
                    "style": "profesional"
                }
                
                print(f"📤 Enviando petición...")
                async with session.post(
                    "http://localhost:8000/api/music/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        job_id = data.get('job_id')
                        print(f"✅ Generación iniciada: {job_id}")
                        print(f"📝 Modo: {data.get('mode', 'unknown')}")
                        print(f"💬 Mensaje: {data.get('message', 'N/A')}")
                        
                        # Monitorear progreso
                        if job_id:
                            await monitor_generation(session, job_id)
                    else:
                        error_text = await response.text()
                        print(f"❌ Error HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
        
        # Pausa entre pruebas
        if i < len(test_prompts):
            print("⏳ Esperando 5 segundos antes de la siguiente prueba...")
            await asyncio.sleep(5)

async def monitor_generation(session, job_id):
    """Monitorear el progreso de generación"""
    print(f"👀 Monitoreando generación: {job_id}")
    
    max_attempts = 30  # 5 minutos máximo
    attempt = 0
    
    while attempt < max_attempts:
        try:
            async with session.get(f"http://localhost:8000/api/music/status/{job_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status')
                    progress = data.get('progress', 0)
                    
                    print(f"📊 Estado: {status} ({progress}%)")
                    
                    if status == "completed":
                        print(f"✅ ¡Generación completada!")
                        if data.get('track_id'):
                            print(f"🎵 Track ID: {data['track_id']}")
                        if data.get('audio_url'):
                            print(f"🔗 Audio URL: {data['audio_url']}")
                        break
                    elif status == "failed":
                        print(f"❌ Generación falló: {data.get('error', 'Error desconocido')}")
                        break
                    
                    attempt += 1
                    await asyncio.sleep(10)  # Verificar cada 10 segundos
                else:
                    print(f"⚠️ Error verificando estado: HTTP {response.status}")
                    break
                    
        except Exception as e:
            print(f"⚠️ Error monitoreando: {e}")
            break
    
    if attempt >= max_attempts:
        print("⏰ Timeout: La generación tardó demasiado")

async def test_tracks_endpoint():
    """Probar el endpoint de tracks"""
    print("\n📁 Probando endpoint de tracks...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/tracks") as response:
                if response.status == 200:
                    data = await response.json()
                    tracks = data.get('tracks', [])
                    print(f"✅ Tracks disponibles: {len(tracks)}")
                    
                    for track in tracks[:3]:  # Mostrar solo los primeros 3
                        print(f"  🎵 {track.get('title', 'Sin título')} ({track.get('id', 'N/A')})")
                else:
                    print(f"❌ Error obteniendo tracks: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Error probando tracks: {e}")

async def main():
    """Función principal"""
    print("🎵 Son1k Stealth Generator - Test Suite")
    print("=" * 50)
    
    await test_stealth_generation()
    await test_tracks_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")
    print("\n💡 Para probar manualmente:")
    print("   🌐 Interfaz web: http://localhost:3001")
    print("   🐍 API Python: http://localhost:8000")
    print("   📊 Estadísticas: http://localhost:3001/stats")

if __name__ == "__main__":
    asyncio.run(main())




