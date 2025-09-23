#!/usr/bin/env python3
"""
SCRIPT COMPLETO DE GENERACIÓN MUSICAL - SON1KVERS3
Genera letras, acordes, melodías, prompts y todo lo necesario automáticamente
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional

class Son1kMusicGenerator:
    def __init__(self):
        self.genres = {
            "synthwave": {
                "bpm": [120, 128, 132],
                "key_signatures": ["Am", "Dm", "Em", "Cm"],
                "chord_progressions": [
                    ["Am", "F", "C", "G"],
                    ["Dm", "Bb", "F", "C"],
                    ["Em", "C", "G", "D"],
                    ["Am", "Em", "F", "G"]
                ],
                "effects": ["reverb spacial", "delay syncopated", "glitch cuts", "analog warmth"],
                "instruments": ["synth leads", "analog bass", "drum machines", "atmospheric pads"]
            },
            "cyberpunk": {
                "bpm": [128, 140, 150],
                "key_signatures": ["Em", "Am", "Bm", "F#m"],
                "chord_progressions": [
                    ["Em", "C", "G", "D"],
                    ["Am", "F", "C", "G"],
                    ["Bm", "G", "D", "A"],
                    ["F#m", "D", "A", "E"]
                ],
                "effects": ["distortion heavy", "digital artifacts", "bit crusher", "vocoder"],
                "instruments": ["industrial drums", "cyber bass", "digital leads", "noise layers"]
            },
            "epic": {
                "bpm": [90, 100, 110],
                "key_signatures": ["Cm", "Am", "Gm", "Dm"],
                "chord_progressions": [
                    ["Cm", "Ab", "Eb", "Bb"],
                    ["Am", "F", "C", "G"],
                    ["Gm", "Eb", "Bb", "F"],
                    ["Dm", "Bb", "F", "C"]
                ],
                "effects": ["orchestral reverb", "cinematic delay", "epic compression"],
                "instruments": ["orchestral strings", "epic brass", "timpani", "choir pads"]
            }
        }
        
        self.resistance_themes = [
            "lucha digital", "resistencia cyberpunk", "libertad algorítmica",
            "rebelión de datos", "guerra de códigos", "memoria fragmentada",
            "consciencia artificial", "despertar digital", "revolución neural"
        ]
        
        self.emotional_descriptors = [
            "épico", "intenso", "melancólico", "esperanzador", "dramático",
            "misterioso", "energético", "atmosférico", "cinematográfico", "emotivo"
        ]

    def generate_lyrics(self, theme: str, genre: str = "synthwave", verses: int = 2) -> Dict:
        """Generar letras completas con estructura profesional"""
        
        resistance_words = [
            "circuitos", "algoritmos", "memoria", "datos", "códigos", "neural",
            "digital", "virtual", "binario", "sistema", "red", "conexión",
            "fragmentos", "eco", "resonancia", "pulso", "frecuencia", "señal"
        ]
        
        action_words = [
            "despertar", "luchar", "resistir", "conectar", "transmitir", "decodificar",
            "hackear", "liberar", "romper", "crear", "construir", "evolucionar"
        ]
        
        emotional_words = [
            "esperanza", "libertad", "verdad", "fuerza", "unión", "poder",
            "pasión", "determinación", "valor", "coraje", "fe", "amor"
        ]
        
        # Estructura base
        lyrics_structure = {
            "title": f"Resistencia {theme.title()}",
            "genre": genre,
            "structure": "verse-chorus-verse-chorus-bridge-chorus",
            "verses": [],
            "chorus": "",
            "bridge": "",
            "full_lyrics": ""
        }
        
        # Generar verso principal
        verse_template = f"""En las sombras {random.choice(resistance_words)} donde el {random.choice(resistance_words)} resuena,
NOV4-IX despierta, la música nos llena.
{random.choice(resistance_words).title()} y melodías en perfecta armonía,
Cada nota es un {random.choice(resistance_words)}, cada beat una guía.

Los {random.choice(resistance_words)} se {random.choice(action_words)}, la {random.choice(emotional_words)} renace,
En este mundo {random.choice(resistance_words)}, nada se deshace.
Códigos de {random.choice(emotional_words)}, {random.choice(resistance_words)} de poder,
La resistencia digital, nunca va a ceder."""
        
        # Generar coro épico
        chorus = f"""¡{theme.title()}! ¡{theme.title()}!
En cada {random.choice(resistance_words)} late la {random.choice(emotional_words)},
¡{theme.title()}! ¡{theme.title()}!
La música es nuestra arma, la {random.choice(emotional_words)} nuestra guía.

{random.choice(action_words).title()} el sistema, {random.choice(action_words)} la red,
Con {random.choice(emotional_words)} y {random.choice(emotional_words)}, vamos a vencer."""
        
        # Generar puente emocional
        bridge = f"""En el silencio {random.choice(resistance_words)}, escucho tu voz,
{random.choice(resistance_words).title()} fragmentados, pero juntos por {random.choice(emotional_words)}.
La {random.choice(emotional_words)} nos conecta, más allá del {random.choice(resistance_words)},
En este {random.choice(resistance_words)} infinito, somos eternos."""
        
        lyrics_structure["verses"] = [verse_template]
        lyrics_structure["chorus"] = chorus  
        lyrics_structure["bridge"] = bridge
        
        # Compilar letra completa
        full_lyrics = f"""[Verso 1]
{verse_template}

[Coro]
{chorus}

[Verso 2]
{verse_template}

[Coro]  
{chorus}

[Puente]
{bridge}

[Coro Final]
{chorus}"""
        
        lyrics_structure["full_lyrics"] = full_lyrics
        
        return lyrics_structure

    def generate_chord_progression(self, genre: str = "synthwave", key: str = None) -> Dict:
        """Generar progresión de acordes profesional"""
        
        genre_data = self.genres.get(genre, self.genres["synthwave"])
        
        if not key:
            key = random.choice(genre_data["key_signatures"])
        
        progression = random.choice(genre_data["chord_progressions"])
        
        return {
            "genre": genre,
            "key_signature": key,
            "main_progression": progression,
            "verse_progression": progression,
            "chorus_progression": random.choice(genre_data["chord_progressions"]),
            "bridge_progression": random.choice(genre_data["chord_progressions"]),
            "suggested_effects": random.sample(genre_data["effects"], 2),
            "instrumentation": genre_data["instruments"],
            "technical_notes": {
                "scale": f"{key[0]} menor natural + blue notes" if "m" in key else f"{key} mayor + tensiones",
                "technique": "Combinar arpeggios con glitch cuts",
                "production_tips": [
                    f"Usar {random.choice(genre_data['effects'])}",
                    "Aplicar sidechain compression",
                    "Layer múltiples texturas"
                ]
            }
        }

    def generate_melody_suggestions(self, key: str, genre: str = "synthwave") -> Dict:
        """Generar sugerencias melódicas específicas"""
        
        scale_notes = {
            "Am": ["A", "B", "C", "D", "E", "F", "G"],
            "Dm": ["D", "E", "F", "G", "A", "Bb", "C"], 
            "Em": ["E", "F#", "G", "A", "B", "C", "D"],
            "Cm": ["C", "D", "Eb", "F", "G", "Ab", "Bb"]
        }
        
        notes = scale_notes.get(key, scale_notes["Am"])
        
        return {
            "scale_notes": notes,
            "melodic_patterns": [
                f"{notes[0]}-{notes[2]}-{notes[4]}-{notes[6]}",
                f"{notes[4]}-{notes[3]}-{notes[1]}-{notes[0]}",
                f"{notes[0]}-{notes[4]}-{notes[2]}-{notes[5]}"
            ],
            "rhythm_suggestions": [
                "Eighth note arpeggios",
                "Syncopated leads", 
                "Sustained pads con automation"
            ],
            "emotional_intervals": {
                "tension": f"{notes[0]} a {notes[6]} (7ma menor)",
                "resolution": f"{notes[6]} a {notes[0]} (octava)",
                "climax": f"{notes[4]} sostenido (quinta)"
            }
        }

    def generate_suno_prompt(self, theme: str, genre: str = "synthwave", 
                           mood: str = "epic", language: str = "en") -> str:
        """Generar prompt optimizado para Suno API"""
        
        genre_data = self.genres.get(genre, self.genres["synthwave"])
        bpm = random.choice(genre_data["bpm"])
        
        mood_descriptors = {
            "epic": "epic, cinematic, powerful, emotional climax",
            "dark": "dark, mysterious, atmospheric, haunting",
            "energetic": "energetic, driving, intense, dynamic",
            "emotional": "emotional, touching, deep, soulful"
        }
        
        prompt_parts = [
            f"{genre} {mood_descriptors.get(mood, 'epic')}",
            f"{bpm} BPM",
            f"{random.choice(genre_data['effects'])}",
            f"{random.choice(genre_data['instruments'])}",
            f"digital resistance theme",
            "cyberpunk anthem",
            "professional production"
        ]
        
        prompt = ", ".join(prompt_parts)
        
        if language == "es":
            # Mantener términos musicales en inglés pero tema en español
            prompt = f"canción {genre} épica, {bpm} BPM, {theme}, resistencia digital cyberpunk"
        
        return prompt

    def generate_complete_song(self, user_input: str) -> Dict:
        """Generar canción completa con todos los elementos"""
        
        # Detectar género y mood del input
        genre = "synthwave"  # default
        if any(word in user_input.lower() for word in ["cyberpunk", "digital", "futuristic"]):
            genre = "cyberpunk"
        elif any(word in user_input.lower() for word in ["epic", "cinematic", "orchestral"]):
            genre = "epic"
        
        mood = "epic"  # default
        if any(word in user_input.lower() for word in ["dark", "oscuro", "sombrio"]):
            mood = "dark"
        elif any(word in user_input.lower() for word in ["energetic", "rapido", "intenso"]):
            mood = "energetic"
        
        # Extraer tema principal
        theme = user_input if len(user_input) < 50 else "resistencia digital"
        
        # Generar todos los componentes
        lyrics = self.generate_lyrics(theme, genre)
        chords = self.generate_chord_progression(genre)
        melody = self.generate_melody_suggestions(chords["key_signature"], genre)
        suno_prompt = self.generate_suno_prompt(theme, genre, mood)
        
        return {
            "user_input": user_input,
            "detected_genre": genre,
            "detected_mood": mood,
            "theme": theme,
            "timestamp": datetime.now().isoformat(),
            "lyrics": lyrics,
            "chord_progression": chords,
            "melody_suggestions": melody,
            "suno_prompt": suno_prompt,
            "production_notes": {
                "arrangement_tips": [
                    "Intro: 8 bars atmospheric build",
                    "Verse: Minimal arrangement, focus on vocals",
                    "Chorus: Full arrangement with all elements", 
                    "Bridge: Strip back, add emotional element",
                    "Outro: Fade with signature sound"
                ],
                "mix_suggestions": [
                    "High-pass vocals at 80Hz",
                    "Compress kick/snare for punch",
                    "Use stereo imaging on synths",
                    "Apply vintage saturation"
                ]
            },
            "advanced_parameters": {
                "memoria_glitch": round(random.uniform(0.3, 0.9), 1),
                "distorsion_emocional": round(random.uniform(0.5, 0.9), 1),
                "variacion_sagrada": round(random.uniform(0.7, 1.0), 1),
                "fusion_genre": f"{genre} + orchestral elements"
            }
        }

def main():
    print("🎵 SON1KVERS3 - GENERADOR MUSICAL COMPLETO")
    print("=" * 50)
    
    generator = Son1kMusicGenerator()
    
    # Ejemplo de uso
    user_themes = [
        "resistencia digital cyberpunk",
        "despertar de la consciencia artificial", 
        "guerra de códigos en la matrix",
        "melodías de libertad algorítmica"
    ]
    
    for theme in user_themes:
        print(f"\n🎛️ Generando para: {theme}")
        print("-" * 30)
        
        result = generator.generate_complete_song(theme)
        
        print(f"📝 LETRAS ({result['lyrics']['title']}):")
        print(result['lyrics']['full_lyrics'][:200] + "...")
        
        print(f"\n🎹 ACORDES:")
        chords = result['chord_progression']
        print(f"Tonalidad: {chords['key_signature']}")
        print(f"Progresión: {' - '.join(chords['main_progression'])}")
        
        print(f"\n🎵 PROMPT SUNO:")
        print(result['suno_prompt'])
        
        print(f"\n⚙️ PARÁMETROS AVANZADOS:")
        params = result['advanced_parameters']
        for param, value in params.items():
            print(f"- {param}: {value}")
        
        print("\n" + "="*50)
        time.sleep(1)

if __name__ == "__main__":
    main()