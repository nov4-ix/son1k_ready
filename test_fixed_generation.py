#!/usr/bin/env python3
"""
🧪 Test del sistema de generación musical corregido
Prueba la generación con nombres dinámicos basados en lyrics
"""
import os
import sys
import time
import logging

# Configurar path
sys.path.append(os.path.abspath('.'))

from backend.selenium_worker.music_generator_fixed import MusicGeneratorFixed, SongNameGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_song_name_generator():
    """Probar generador de nombres dinámicos"""
    print("🧪 Probando generador de nombres dinámicos...")
    
    # Test 1: Lyrics normales
    lyrics1 = """Walking down the street tonight
Feeling free and feeling right
Music playing in my head
Dancing till the day is dead"""
    
    name1 = SongNameGenerator.generate_name_from_lyrics(lyrics1)
    print(f"✅ Test 1 - Nombre generado: '{name1}'")
    
    # Test 2: Lyrics con primera línea corta
    lyrics2 = """Hey!
This is a test song
With multiple lines
And different content"""
    
    name2 = SongNameGenerator.generate_name_from_lyrics(lyrics2)
    print(f"✅ Test 2 - Nombre generado: '{name2}'")
    
    # Test 3: Lyrics vacías (instrumental)
    lyrics3 = ""
    name3 = SongNameGenerator.generate_name_from_lyrics(lyrics3)
    print(f"✅ Test 3 - Nombre instrumental: '{name3}'")
    
    # Test 4: Lyrics con caracteres especiales
    lyrics4 = """¡Hola mundo! ¿Cómo estás?
Esta es una canción en español
Con acentos y símbolos especiales
¡Que genial suena esto!"""
    
    name4 = SongNameGenerator.generate_name_from_lyrics(lyrics4)
    print(f"✅ Test 4 - Nombre con caracteres especiales: '{name4}'")
    
    return True

def test_music_generator():
    """Probar el motor de generación completo"""
    print("\n🎵 Probando motor de generación musical...")
    
    # Configurar variables de entorno
    os.environ["SV_SELENIUM_URL"] = "http://localhost:4444"
    os.environ["SV_HEADLESS"] = "0"  # Visible para debugging
    os.environ["SV_NO_QUIT"] = "1"   # No cerrar en errores
    
    generator = MusicGeneratorFixed()
    
    try:
        # Test de inicialización
        print("🔧 Inicializando driver...")
        if not generator.initialize_driver():
            print("❌ Error: No se pudo inicializar driver")
            return False
        
        print("✅ Driver inicializado correctamente")
        
        # Test de verificación de sesión
        print("🔍 Verificando sesión...")
        session_active = generator.check_session()
        
        if session_active:
            print("✅ Sesión activa detectada")
            
            # Test de generación completa
            print("🎵 Probando generación completa...")
            
            test_lyrics = """Testing the fixed generation system
With dynamic naming capabilities
This should work perfectly now
Creating music with style"""
            
            test_prompt = "upbeat electronic test song, 120 BPM, energetic synthesizers"
            job_id = f"test_job_{int(time.time())}"
            
            print(f"📝 Lyrics: {len(test_lyrics)} caracteres")
            print(f"🎨 Prompt: {test_prompt}")
            print(f"🆔 Job ID: {job_id}")
            
            # Ejecutar generación
            results = generator.generate_music(
                lyrics=test_lyrics,
                prompt=test_prompt,
                job_id=job_id,
                instrumental=False
            )
            
            if results:
                print(f"✅ Generación exitosa: {len(results)} tracks")
                for i, track in enumerate(results):
                    print(f"   🎵 Track {i+1}: {track['title']}")
                    print(f"      📁 Filename: {track.get('filename', 'N/A')}")
                    print(f"      ⏱️ Duración: {track.get('duration', 'Unknown')}")
                    print(f"      🔗 URL: {track.get('url', 'N/A')[:50]}..." if track.get('url') else "      🔗 URL: N/A")
                return True
            else:
                print("❌ Error: No se generaron resultados")
                return False
        else:
            print("⚠️ No hay sesión activa. Necesitas hacer login primero.")
            print("   1. Ve a: https://a11795f9785f.ngrok-free.app")
            print("   2. Haz login en Suno")
            print("   3. Ejecuta este test nuevamente")
            return False
            
    except Exception as e:
        logger.error(f"Error en test: {e}")
        return False
    finally:
        # Cleanup
        generator.cleanup()

def main():
    """Función principal de test"""
    print("🚀 Iniciando tests del sistema de generación corregido")
    print("=" * 60)
    
    # Test 1: Generador de nombres
    if not test_song_name_generator():
        print("❌ Error en test de generador de nombres")
        return False
    
    # Test 2: Motor de generación completo
    if not test_music_generator():
        print("❌ Error en test de motor de generación")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Todos los tests completados exitosamente")
    print("🎵 El sistema de generación con nombres dinámicos está funcionando")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)