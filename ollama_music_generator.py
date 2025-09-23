#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Generador Musical con Ollama
Conexión estable y optimizada para generación musical con IA
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaMusicGenerator:
    """Generador musical inteligente usando Ollama"""
    
    def __init__(self, model_name: str = "llama3.1:latest", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
    def verify_connection(self) -> bool:
        """Verificar que Ollama esté funcionando"""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            if response.status_code == 200:
                version = response.json().get('version', 'unknown')
                logger.info(f"✅ Ollama conectado - versión {version}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error conectando con Ollama: {e}")
            return False
    
    def generate_song_concept(self, user_prompt: str) -> Dict[str, Any]:
        """Generar concepto musical usando IA"""
        if not self.verify_connection():
            return self._fallback_response("Ollama no disponible")
        
        # Prompt optimizado para generación musical
        music_prompt = f"""
Eres un asistente musical experto. Basándote en esta descripción: "{user_prompt}"

Genera SOLO la siguiente información en formato JSON:
{{
    "title": "Título de la canción (máximo 8 palabras)",
    "genre": "Género musical específico",
    "mood": "Estado de ánimo/energía",
    "lyrics": "Letra completa de la canción (4 estrofas)",
    "style_tags": "3 etiquetas de estilo separadas por comas",
    "description": "Descripción breve de la canción"
}}

Responde ÚNICAMENTE el JSON, sin explicaciones adicionales.
"""
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": music_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 500,
                        "stop": ["Human:", "Assistant:"]
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                
                # Intentar parsear JSON de la respuesta
                try:
                    # Limpiar la respuesta para extraer solo el JSON
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = ai_response[json_start:json_end]
                        music_data = json.loads(json_str)
                        
                        # Validar y completar datos
                        return self._validate_music_data(music_data, user_prompt)
                    else:
                        logger.warning("No se encontró JSON válido en la respuesta")
                        return self._parse_text_response(ai_response, user_prompt)
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parseando JSON: {e}")
                    return self._parse_text_response(ai_response, user_prompt)
            else:
                logger.error(f"Error HTTP {response.status_code}")
                return self._fallback_response(f"Error del servidor: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("Timeout conectando con Ollama")
            return self._fallback_response("Timeout - modelo ocupado")
        except Exception as e:
            logger.error(f"Error generando música: {e}")
            return self._fallback_response(str(e))
    
    def _validate_music_data(self, data: Dict, user_prompt: str) -> Dict[str, Any]:
        """Validar y completar datos musicales"""
        return {
            "title": data.get("title", "Canción Generada"),
            "genre": data.get("genre", "Pop"),
            "mood": data.get("mood", "Energético"),
            "lyrics": data.get("lyrics", self._generate_simple_lyrics(user_prompt)),
            "style_tags": data.get("style_tags", "pop, energético, moderno"),
            "description": data.get("description", f"Canción basada en: {user_prompt}"),
            "generated_at": datetime.now().isoformat(),
            "ai_model": self.model_name,
            "status": "success"
        }
    
    def _parse_text_response(self, text: str, user_prompt: str) -> Dict[str, Any]:
        """Parsear respuesta de texto libre cuando falla el JSON"""
        lines = text.split('\n')
        
        # Buscar información clave en el texto
        title = "Canción Generada"
        genre = "Pop"
        lyrics = ""
        
        for line in lines:
            if any(word in line.lower() for word in ['title', 'título']):
                title = line.split(':')[-1].strip().strip('"')
            elif any(word in line.lower() for word in ['genre', 'género']):
                genre = line.split(':')[-1].strip().strip('"')
            elif len(line.strip()) > 20 and not line.startswith(('Título', 'Género')):
                lyrics += line.strip() + '\n'
        
        return {
            "title": title,
            "genre": genre,
            "mood": "Creativo",
            "lyrics": lyrics.strip() or self._generate_simple_lyrics(user_prompt),
            "style_tags": f"{genre.lower()}, creativo, original",
            "description": f"Canción inspirada en: {user_prompt}",
            "generated_at": datetime.now().isoformat(),
            "ai_model": self.model_name,
            "status": "success"
        }
    
    def _generate_simple_lyrics(self, prompt: str) -> str:
        """Generar letra simple como fallback"""
        return f"""[Verso 1]
{prompt} me inspira cada día
La música fluye como melodía
En cada nota encuentro la magia
Que transforma mi alma en armonía

[Coro]
Cantamos juntos esta canción
Que nace desde el corazón
{prompt} es nuestra inspiración
Para crear esta bella composición

[Verso 2]
Las palabras danzan en el aire
Como notas que van a encontrarse
En esta música que vamos a crear
Juntos podemos todo alcanzar

[Coro]
Cantamos juntos esta canción
Que nace desde el corazón
{prompt} es nuestra inspiración
Para crear esta bella composición"""
    
    def _fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Respuesta de fallback cuando falla la conexión"""
        return {
            "title": "Canción Demo",
            "genre": "Pop Electrónico",
            "mood": "Optimista",
            "lyrics": """[Verso 1]
La tecnología nos conecta
La música nos inspira
En cada nota hay esperanza
En cada ritmo, una mentira transformada

[Coro]
Son1kVers3 está aquí
Para crear música sin fin
La IA y el corazón
Juntos en esta canción

[Verso 2]
Cada día es una oportunidad
De crear algo especial
La música nos une a todos
En una danza universal

[Coro]
Son1kVers3 está aquí
Para crear música sin fin
La IA y el corazón
Juntos en esta canción""",
            "style_tags": "pop electrónico, optimista, tecnológico",
            "description": f"Canción demo generada. Error: {error_message}",
            "generated_at": datetime.now().isoformat(),
            "ai_model": "fallback",
            "status": "fallback",
            "error": error_message
        }

def test_music_generation():
    """Probar el generador musical"""
    print("🎵 Probando generador musical con Ollama...")
    
    generator = OllamaMusicGenerator()
    
    # Probar conexión
    if not generator.verify_connection():
        print("❌ No se puede conectar con Ollama")
        return False
    
    # Generar canción de prueba
    test_prompts = [
        "una canción alegre sobre el futuro",
        "música triste sobre recuerdos",
        "rock enérgico sobre libertad"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎯 Prueba {i}: {prompt}")
        
        start_time = time.time()
        result = generator.generate_song_concept(prompt)
        duration = time.time() - start_time
        
        print(f"⏱️  Tiempo: {duration:.2f}s")
        print(f"🎵 Título: {result['title']}")
        print(f"🎭 Género: {result['genre']}")
        print(f"💫 Estado: {result['status']}")
        
        if result['status'] == 'success':
            print("✅ Generación exitosa")
        else:
            print(f"⚠️  Modo fallback: {result.get('error', 'Error desconocido')}")
    
    print("\n🎉 Pruebas completadas!")
    return True

if __name__ == "__main__":
    test_music_generation()