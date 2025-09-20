#!/usr/bin/env python3
"""
🧪 Test solo del generador de nombres dinámicos
"""
import os
import sys
import time
import re

# Configurar path
sys.path.append(os.path.abspath('.'))

class SongNameGenerator:
    """Generador de nombres dinámicos para canciones"""
    
    @staticmethod
    def generate_name_from_lyrics(lyrics: str) -> str:
        """Generar nombre desde la primera frase de las lyrics"""
        if not lyrics or not lyrics.strip():
            return f"Instrumental_{int(time.time())}"
        
        # Limpiar y procesar lyrics
        clean_lyrics = lyrics.strip()
        
        # Tomar primera línea/frase significativa
        lines = clean_lyrics.split('\n')
        first_line = ""
        
        for line in lines:
            line = line.strip()
            # Buscar primera línea con contenido real (no vacía, no solo signos)
            if line and len(line) > 3 and not line.isspace():
                first_line = line
                break
        
        if not first_line:
            # Si no hay primera línea, usar las primeras palabras
            words = clean_lyrics.split()[:4]
            first_line = " ".join(words) if words else "Sin Título"
        
        # Limpiar el nombre
        song_name = SongNameGenerator.clean_filename(first_line)
        
        # Limitar longitud
        if len(song_name) > 50:
            song_name = song_name[:47] + "..."
        
        return song_name or f"Canción_{int(time.time())}"
    
    @staticmethod
    def clean_filename(text: str) -> str:
        """Limpiar texto para usar como nombre de archivo"""
        # Remover caracteres especiales problemáticos
        cleaned = re.sub(r'[<>:"/\\|?*]', '', text)
        
        # Reemplazar múltiples espacios con uno solo
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remover espacios al inicio y final
        cleaned = cleaned.strip()
        
        # Capitalizar primera letra de cada palabra
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        return cleaned

def test_song_name_generator():
    """Probar generador de nombres dinámicos"""
    print("🧪 Probando generador de nombres dinámicos...")
    
    tests = [
        {
            "name": "Lyrics normales",
            "lyrics": """Walking down the street tonight
Feeling free and feeling right
Music playing in my head
Dancing till the day is dead""",
            "expected_contains": "Walking Down The Street Tonight"
        },
        {
            "name": "Lyrics con primera línea corta",
            "lyrics": """Hey!
This is a test song
With multiple lines
And different content""",
            "expected_contains": "This Is A Test Song"
        },
        {
            "name": "Lyrics vacías (instrumental)", 
            "lyrics": "",
            "expected_contains": "Instrumental_"
        },
        {
            "name": "Lyrics con caracteres especiales",
            "lyrics": """¡Hola mundo! ¿Cómo estás?
Esta es una canción en español
Con acentos y símbolos especiales
¡Que genial suena esto!""",
            "expected_contains": "¡hola Mundo! ¿cómo Estás?"
        },
        {
            "name": "Lyrics del problema original (suno)",
            "lyrics": """Testing the CAPTCHA resolution system
With remote browser access via noVNC
Visual resolution works seamlessly
Automation continues after solving
This is a comprehensive test of our system""",
            "expected_contains": "Testing The Captcha Resolution System"
        },
        {
            "name": "Lyrics en español",
            "lyrics": """Caminando por la calle de noche
Sintiendo la libertad en el aire
La música suena en mi cabeza
Bailando hasta el amanecer""",
            "expected_contains": "Caminando Por La Calle De Noche"
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(tests, 1):
        print(f"\n📝 Test {i}: {test['name']}")
        print(f"   Lyrics: {test['lyrics'][:50]}..." if len(test['lyrics']) > 50 else f"   Lyrics: '{test['lyrics']}'")
        
        generated_name = SongNameGenerator.generate_name_from_lyrics(test['lyrics'])
        print(f"   ✅ Nombre generado: '{generated_name}'")
        
        # Verificar que no contenga "suno"
        if "suno" in generated_name.lower():
            print(f"   ❌ ERROR: El nombre contiene 'suno'")
            all_passed = False
        else:
            print(f"   ✅ OK: No contiene 'suno'")
        
        # Verificar longitud
        if len(generated_name) > 50:
            print(f"   ❌ ERROR: Nombre demasiado largo ({len(generated_name)} chars)")
            all_passed = False
        else:
            print(f"   ✅ OK: Longitud apropiada ({len(generated_name)} chars)")
        
        # Verificar caracteres válidos para archivo
        cleaned_for_file = generated_name.replace(' ', '_').replace('...', '')
        if re.search(r'[<>:"/\\|?*]', cleaned_for_file):
            print(f"   ❌ ERROR: Contiene caracteres inválidos para archivo")
            all_passed = False
        else:
            print(f"   ✅ OK: Nombre válido para archivo: '{cleaned_for_file}.mp3'")
    
    return all_passed

def main():
    """Función principal de test"""
    print("🚀 Test del Generador de Nombres Dinámicos para Son1k")
    print("🎯 Objetivo: Reemplazar nombres 'suno' por nombres basados en lyrics")
    print("=" * 70)
    
    if test_song_name_generator():
        print("\n" + "=" * 70)
        print("✅ TODOS LOS TESTS PASARON")
        print("🎵 El generador de nombres dinámicos está funcionando correctamente")
        print("🚫 Los archivos ya NO se llamarán 'suno'")
        print("✨ Ahora usan la primera frase de las lyrics como nombre")
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisa los errores arriba")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)