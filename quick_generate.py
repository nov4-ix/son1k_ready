#!/usr/bin/env python3
"""
Uso rápido del generador musical
"""

from complete_music_generator import Son1kMusicGenerator
import json
import sys

def quick_generate(theme):
    generator = Son1kMusicGenerator()
    result = generator.generate_complete_song(theme)
    
    print(f"🎵 GENERANDO: {theme}")
    print("=" * 50)
    
    print("📝 LETRAS COMPLETAS:")
    print(result['lyrics']['full_lyrics'])
    
    print(f"\n🎹 PROGRESIÓN DE ACORDES:")
    chords = result['chord_progression']
    print(f"Tonalidad: {chords['key_signature']}")
    print(f"Verso: {' - '.join(chords['verse_progression'])}")
    print(f"Coro: {' - '.join(chords['chorus_progression'])}")
    print(f"Puente: {' - '.join(chords['bridge_progression'])}")
    
    print(f"\n🎛️ PROMPT PARA SUNO:")
    print(result['suno_prompt'])
    
    print(f"\n⚙️ PARÁMETROS SON1KVERS3:")
    params = result['advanced_parameters']
    for param, value in params.items():
        print(f"- {param}: {value}")
    
    print(f"\n🎵 SUGERENCIAS MELÓDICAS:")
    melody = result['melody_suggestions']
    print(f"Escala: {' - '.join(melody['scale_notes'])}")
    print(f"Patrones: {melody['melodic_patterns'][0]}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        theme = " ".join(sys.argv[1:])
    else:
        theme = input("🎵 Tema para generar música: ")
    
    quick_generate(theme)