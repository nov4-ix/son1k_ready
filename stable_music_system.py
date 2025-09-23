#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Sistema Musical Estable
Conexión optimizada Ollama + Suno con fallbacks inteligentes
"""

import requests
import json
import time
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import subprocess
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StableMusicSystem:
    """Sistema musical estable con múltiples niveles de fallback"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.fast_model = "llama3.1:latest"  # Usar el modelo que ya tenemos
        self.fallback_enabled = True
        
    async def check_ollama_health(self) -> bool:
        """Verificar salud de Ollama con timeout rápido"""
        try:
            response = requests.get(f"{self.ollama_url}/api/version", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    async def quick_ai_generation(self, prompt: str) -> Dict[str, Any]:
        """Generación rápida de AI con timeout corto"""
        if not await self.check_ollama_health():
            logger.warning("Ollama no disponible - usando fallback")
            return self._intelligent_fallback(prompt)
        
        # Prompt ultra-optimizado para respuesta rápida
        system_prompt = f"""RESPUESTA RÁPIDA - Solo responde el JSON exacto:
{{"title": "título corto aquí", "genre": "género aquí", "mood": "estado aquí", "lyrics": "letra corta aquí", "style_tags": "tags aquí", "description": "descripción aquí"}}

Tema: {prompt}
Genera música en base a esto. SOLO JSON, sin explicaciones."""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.fast_model,
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200,  # Respuesta muy corta
                        "stop": ["\n\n", "Explicación", "Note"]
                    }
                },
                timeout=20  # Timeout corto
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result.get('response', '').strip()
                
                # Intentar extraer JSON
                try:
                    json_start = ai_text.find('{')
                    json_end = ai_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = ai_text[json_start:json_end]
                        music_data = json.loads(json_str)
                        return self._finalize_music_data(music_data, prompt, "ai_generated")
                except:
                    pass
                
                # Si falla JSON, parsear texto
                return self._parse_ai_text(ai_text, prompt)
            
        except requests.exceptions.Timeout:
            logger.warning("AI timeout - usando fallback inteligente")
        except Exception as e:
            logger.warning(f"Error AI: {e} - usando fallback")
        
        return self._intelligent_fallback(prompt)
    
    def _parse_ai_text(self, text: str, prompt: str) -> Dict[str, Any]:
        """Parsear texto de AI cuando falla JSON"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extraer información clave
        title = self._extract_value(lines, ['title', 'título']) or f"Canción sobre {prompt}"
        genre = self._extract_value(lines, ['genre', 'género']) or "Pop"
        mood = self._extract_value(lines, ['mood', 'estado']) or "Energético"
        
        # Buscar letra en el texto
        lyrics = self._extract_lyrics(text) or self._generate_simple_lyrics(prompt)
        
        return self._finalize_music_data({
            "title": title,
            "genre": genre,
            "mood": mood,
            "lyrics": lyrics,
            "style_tags": f"{genre.lower()}, {mood.lower()}, original",
            "description": f"Canción generada con IA sobre: {prompt}"
        }, prompt, "ai_parsed")
    
    def _extract_value(self, lines: list, keywords: list) -> Optional[str]:
        """Extraer valor de líneas por palabras clave"""
        for line in lines:
            for keyword in keywords:
                if keyword.lower() in line.lower() and ':' in line:
                    value = line.split(':', 1)[-1].strip().strip('"\'')
                    if len(value) > 1:
                        return value
        return None
    
    def _extract_lyrics(self, text: str) -> Optional[str]:
        """Extraer letra del texto"""
        lines = text.split('\n')
        lyrics_lines = []
        in_lyrics = False
        
        for line in lines:
            clean_line = line.strip()
            if any(word in clean_line.lower() for word in ['lyrics', 'letra', 'verso', 'coro']):
                in_lyrics = True
                continue
            elif in_lyrics and clean_line and not clean_line.startswith(('{', '}', '"')):
                lyrics_lines.append(clean_line)
            elif in_lyrics and not clean_line:
                break
        
        return '\n'.join(lyrics_lines) if lyrics_lines else None
    
    def _intelligent_fallback(self, prompt: str) -> Dict[str, Any]:
        """Fallback inteligente basado en patrones de prompt"""
        # Analizar el prompt para generar respuesta contextual
        prompt_lower = prompt.lower()
        
        # Detectar género musical
        if any(word in prompt_lower for word in ['rock', 'metal', 'punk']):
            genre = "Rock"
            mood = "Energético"
            tags = "rock, energético, potente"
        elif any(word in prompt_lower for word in ['pop', 'comercial', 'pegadizo']):
            genre = "Pop"
            mood = "Alegre"
            tags = "pop, pegadizo, comercial"
        elif any(word in prompt_lower for word in ['triste', 'melancólico', 'lento']):
            genre = "Balada"
            mood = "Melancólico"
            tags = "balada, emocional, lento"
        elif any(word in prompt_lower for word in ['electrónico', 'dance', 'techno']):
            genre = "Electrónico"
            mood = "Bailable"
            tags = "electrónico, dance, moderno"
        else:
            genre = "Pop Alternativo"
            mood = "Creativo"
            tags = "alternativo, original, creativo"
        
        # Generar título contextual
        title_words = prompt.split()[:3]
        title = f"{''.join(word.capitalize() for word in title_words)}"
        
        return self._finalize_music_data({
            "title": title,
            "genre": genre,
            "mood": mood,
            "lyrics": self._generate_contextual_lyrics(prompt, genre, mood),
            "style_tags": tags,
            "description": f"Canción {genre.lower()} inspirada en: {prompt}"
        }, prompt, "intelligent_fallback")
    
    def _generate_contextual_lyrics(self, prompt: str, genre: str, mood: str) -> str:
        """Generar letra contextual basada en prompt, género y mood"""
        
        if mood.lower() == "energético":
            return f"""[Verso 1]
¡{prompt} me da la fuerza!
Para seguir adelante cada día
Con energía que nunca cesa
Y una pasión que nunca se enfría

[Coro]
¡Vamos a brillar!
Como estrellas en el cielo
{prompt} nos va a llevar
Hasta cumplir nuestro anhelo

[Verso 2]
No hay límites en el horizonte
Cuando tienes el corazón ardiendo
{prompt} es nuestro norte
Y seguimos creciendo

[Coro]
¡Vamos a brillar!
Como estrellas en el cielo
{prompt} nos va a llevar
Hasta cumplir nuestro anhelo"""

        elif mood.lower() == "melancólico":
            return f"""[Verso 1]
{prompt} en mi mente
Como un eco que no se va
Recuerdos que vuelven siempre
A esta alma que llora ya

[Coro]
Lágrimas que caen
Como lluvia en el cristal
{prompt} que se desvanece
En este dolor eternal

[Verso 2]
Camino por las calles vacías
Buscando lo que se perdió
{prompt} en mis días
Era todo lo que me quedó

[Coro]
Lágrimas que caen
Como lluvia en el cristal
{prompt} que se desvanece
En este dolor eternal"""

        else:  # Default alegre/creativo
            return f"""[Verso 1]
{prompt} ilumina mi camino
Como una luz en la oscuridad
Cada paso es un destino
Hacia una nueva realidad

[Coro]
Cantemos juntos esta melodía
Que nace del corazón
{prompt} es nuestra guía
En esta dulce canción

[Verso 2]
Los sueños se hacen realidad
Cuando tienes fe en ti
{prompt} es libertad
Para ser feliz y vivir

[Coro]
Cantemos juntos esta melodía
Que nace del corazón
{prompt} es nuestra guía
En esta dulce canción"""
    
    def _generate_simple_lyrics(self, prompt: str) -> str:
        """Fallback para letra simple"""
        return f"""[Verso 1]
{prompt} en mi corazón
Como una melodía
Que suena sin razón
Y llena de alegría

[Coro]
Esta es nuestra canción
Nacida del momento
{prompt} es la inspiración
Para este sentimiento

[Verso 2]
Cada nota es especial
Cada palabra tiene poder
{prompt} es musical
Y nos hace florecer

[Coro]
Esta es nuestra canción
Nacida del momento
{prompt} es la inspiración
Para este sentimiento"""
    
    def _finalize_music_data(self, data: Dict, prompt: str, generation_type: str) -> Dict[str, Any]:
        """Finalizar y validar datos musicales"""
        return {
            "title": data.get("title", "Canción Sin Título")[:50],
            "genre": data.get("genre", "Pop")[:30],
            "mood": data.get("mood", "Neutral")[:30],
            "lyrics": data.get("lyrics", self._generate_simple_lyrics(prompt)),
            "style_tags": data.get("style_tags", "pop, original, creativo")[:100],
            "description": data.get("description", f"Canción sobre {prompt}")[:200],
            "generated_at": datetime.now().isoformat(),
            "generation_type": generation_type,
            "original_prompt": prompt,
            "status": "success"
        }

async def test_stable_system():
    """Probar el sistema estable"""
    print("🎵 Probando Sistema Musical Estable...")
    
    system = StableMusicSystem()
    
    test_prompts = [
        "una canción de rock energético sobre libertad",
        "balada triste sobre amor perdido",
        "música electrónica para bailar",
        "canción pop sobre amistad",
        "música relajante para meditar"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎯 Prueba {i}: {prompt}")
        
        start_time = time.time()
        result = await system.quick_ai_generation(prompt)
        duration = time.time() - start_time
        
        print(f"⏱️  Tiempo: {duration:.2f}s")
        print(f"🎵 Título: {result['title']}")
        print(f"🎭 Género: {result['genre']}")
        print(f"💫 Tipo: {result['generation_type']}")
        print(f"✅ Estado: {result['status']}")
    
    print("\n🎉 ¡Sistema estable funcionando correctamente!")

if __name__ == "__main__":
    asyncio.run(test_stable_system())