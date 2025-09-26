#!/usr/bin/env python3
"""
🤖 SON1KVERS3 - Ollama Music AI Integration
Sistema de IA local para análisis musical avanzado
"""

import requests
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaMusicAI:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.models = {
            'music_analysis': 'llama3.1:8b',
            'lyrics_generation': 'mistral:7b', 
            'style_classification': 'codellama:7b',
            'prompt_optimization': 'llama3.1:8b'
        }
        self.is_available = False
        self.available_models = []
        
    async def init(self):
        """Inicializar conexión con Ollama"""
        try:
            # Verificar que Ollama esté corriendo
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.available_models = [model['name'] for model in data.get('models', [])]
                        self.is_available = True
                        logger.info(f"✅ Ollama conectado. Modelos disponibles: {self.available_models}")
                        return True
                    else:
                        logger.error(f"❌ Error conectando con Ollama: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Error inicializando Ollama: {e}")
            return False
    
    async def analyze_music_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analizar prompt musical con IA"""
        if not self.is_available:
            return self._fallback_analysis(prompt)
        
        try:
            analysis_prompt = f"""
Analiza este prompt musical y devuelve un JSON con la siguiente estructura:
{{
    "tempo": 120,
    "scale": "C major",
    "instruments": ["piano", "drums"],
    "mood": "epic",
    "genre": "electronic",
    "key_signature": "C",
    "time_signature": "4/4",
    "energy_level": 8,
    "complexity": 6,
    "style_characteristics": ["synthetic", "atmospheric"],
    "emotional_tone": "uplifting",
    "technical_notes": "Use reverb and delay effects"
}}

Prompt musical: "{prompt}"

Responde SOLO con el JSON, sin texto adicional.
"""
            
            response = await self._call_ollama(self.models['music_analysis'], analysis_prompt)
            
            # Intentar parsear JSON
            try:
                analysis = json.loads(response)
                logger.info(f"✅ Análisis musical completado: {analysis}")
                return analysis
            except json.JSONDecodeError:
                logger.warning("⚠️ Respuesta no es JSON válido, usando análisis de fallback")
                return self._fallback_analysis(prompt)
                
        except Exception as e:
            logger.error(f"❌ Error analizando prompt: {e}")
            return self._fallback_analysis(prompt)
    
    async def generate_lyrics(self, prompt: str, style: str = "electronic", language: str = "es") -> str:
        """Generar letras con IA"""
        if not self.is_available:
            return self._fallback_lyrics(prompt, style)
        
        try:
            lyrics_prompt = f"""
Genera letras para una canción en {language} con el siguiente prompt y estilo:

Prompt: "{prompt}"
Estilo: {style}

Requisitos:
- 2-3 estrofas de 4 líneas cada una
- 1 coro de 4 líneas
- Tema coherente con el prompt
- Estilo apropiado para {style}
- Lenguaje natural y expresivo
- Estructura: Estrofa 1, Coro, Estrofa 2, Coro, Estrofa 3, Coro

Genera SOLO las letras, sin títulos ni explicaciones.
"""
            
            response = await self._call_ollama(self.models['lyrics_generation'], lyrics_prompt)
            logger.info(f"✅ Letras generadas: {len(response)} caracteres")
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generando letras: {e}")
            return self._fallback_lyrics(prompt, style)
    
    async def classify_music_style(self, prompt: str) -> Dict[str, Any]:
        """Clasificar estilo musical con IA"""
        if not self.is_available:
            return self._fallback_style_classification(prompt)
        
        try:
            classification_prompt = f"""
Clasifica el estilo musical de este prompt y devuelve un JSON:

{{
    "primary_style": "synthwave",
    "secondary_styles": ["electronic", "ambient"],
    "confidence": 0.85,
    "characteristics": ["retro", "atmospheric", "synthetic"],
    "influences": ["80s", "cyberpunk"],
    "target_audience": "young_adults",
    "mood_tags": ["nostalgic", "futuristic"]
}}

Prompt: "{prompt}"

Responde SOLO con el JSON.
"""
            
            response = await self._call_ollama(self.models['style_classification'], classification_prompt)
            
            try:
                classification = json.loads(response)
                logger.info(f"✅ Estilo clasificado: {classification}")
                return classification
            except json.JSONDecodeError:
                return self._fallback_style_classification(prompt)
                
        except Exception as e:
            logger.error(f"❌ Error clasificando estilo: {e}")
            return self._fallback_style_classification(prompt)
    
    async def optimize_prompt(self, original_prompt: str) -> Dict[str, Any]:
        """Optimizar prompt musical con IA"""
        if not self.is_available:
            return {"optimized_prompt": original_prompt, "improvements": []}
        
        try:
            optimization_prompt = f"""
Optimiza este prompt musical para mejor generación de música y devuelve un JSON:

{{
    "optimized_prompt": "prompt mejorado",
    "original_prompt": "{original_prompt}",
    "improvements": ["agregado tempo", "especificado instrumentos"],
    "technical_suggestions": ["usar reverb", "tempo 128 BPM"],
    "style_enhancements": ["agregar atmosfera", "énfasis en melodía"],
    "confidence": 0.9
}}

Mejora el prompt original para ser más específico y efectivo para generación musical.

Responde SOLO con el JSON.
"""
            
            response = await self._call_ollama(self.models['prompt_optimization'], optimization_prompt)
            
            try:
                optimization = json.loads(response)
                logger.info(f"✅ Prompt optimizado: {optimization}")
                return optimization
            except json.JSONDecodeError:
                return {"optimized_prompt": original_prompt, "improvements": []}
                
        except Exception as e:
            logger.error(f"❌ Error optimizando prompt: {e}")
            return {"optimized_prompt": original_prompt, "improvements": []}
    
    async def _call_ollama(self, model: str, prompt: str) -> str:
        """Llamar a Ollama con un modelo específico"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', '').strip()
                    else:
                        logger.error(f"❌ Error en llamada a Ollama: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"❌ Error en llamada a Ollama: {e}")
            return ""
    
    def _fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """Análisis de fallback cuando Ollama no está disponible"""
        words = prompt.lower().split()
        
        # Análisis básico
        tempo = 120
        if any(word in words for word in ['lento', 'slow', 'calm']):
            tempo = 80
        elif any(word in words for word in ['rápido', 'fast', 'epic', 'épico']):
            tempo = 140
        
        scale = "C major"
        if any(word in words for word in ['menor', 'minor', 'triste', 'sad']):
            scale = "A minor"
        
        instruments = []
        if any(word in words for word in ['piano', 'piano']):
            instruments.append('piano')
        if any(word in words for word in ['guitarra', 'guitar']):
            instruments.append('guitar')
        if any(word in words for word in ['batería', 'drums', 'beat']):
            instruments.append('drums')
        if any(word in words for word in ['sintetizador', 'synth', 'electronic']):
            instruments.append('synth')
        
        mood = "neutral"
        if any(word in words for word in ['alegre', 'happy', 'upbeat']):
            mood = "happy"
        elif any(word in words for word in ['triste', 'sad', 'melancholic']):
            mood = "sad"
        elif any(word in words for word in ['épico', 'epic', 'grandioso']):
            mood = "epic"
        
        return {
            "tempo": tempo,
            "scale": scale,
            "instruments": instruments if instruments else ['synth', 'drums'],
            "mood": mood,
            "genre": "electronic",
            "key_signature": "C",
            "time_signature": "4/4",
            "energy_level": 7,
            "complexity": 5,
            "style_characteristics": ["synthetic"],
            "emotional_tone": "neutral",
            "technical_notes": "Basic generation",
            "fallback": True
        }
    
    def _fallback_lyrics(self, prompt: str, style: str) -> str:
        """Letras de fallback cuando Ollama no está disponible"""
        themes = {
            'electronic': [
                "En el mundo digital donde todo es posible",
                "La música fluye como código en las venas",
                "Cada beat es un latido del futuro",
                "La tecnología nos conecta, nos une"
            ],
            'synthwave': [
                "Neon lights en la noche de la ciudad",
                "El pasado y futuro se encuentran aquí",
                "Sintetizadores suenan en la oscuridad",
                "La nostalgia nos lleva al mañana"
            ],
            'cyberpunk': [
                "En las calles de la matriz digital",
                "La resistencia nace en cada byte",
                "Hackeamos la realidad, creamos el futuro",
                "La música es nuestra arma, nuestro código"
            ]
        }
        
        return '\n'.join(themes.get(style, themes['electronic']))
    
    def _fallback_style_classification(self, prompt: str) -> Dict[str, Any]:
        """Clasificación de estilo de fallback"""
        words = prompt.lower().split()
        
        if any(word in words for word in ['synthwave', 'retro', '80s', 'neon']):
            return {
                "primary_style": "synthwave",
                "secondary_styles": ["electronic"],
                "confidence": 0.8,
                "characteristics": ["retro", "synthetic"],
                "influences": ["80s"],
                "target_audience": "young_adults",
                "mood_tags": ["nostalgic"],
                "fallback": True
            }
        elif any(word in words for word in ['cyberpunk', 'futuro', 'digital']):
            return {
                "primary_style": "cyberpunk",
                "secondary_styles": ["electronic", "industrial"],
                "confidence": 0.8,
                "characteristics": ["dark", "futuristic"],
                "influences": ["sci-fi"],
                "target_audience": "adults",
                "mood_tags": ["dark", "futuristic"],
                "fallback": True
            }
        else:
            return {
                "primary_style": "electronic",
                "secondary_styles": ["ambient"],
                "confidence": 0.6,
                "characteristics": ["synthetic"],
                "influences": ["modern"],
                "target_audience": "general",
                "mood_tags": ["neutral"],
                "fallback": True
            }

class OllamaMusicAIServer:
    """Servidor HTTP para exponer la IA musical"""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        self.host = host
        self.port = port
        self.ai = OllamaMusicAI()
        self.app = None
        
    async def init(self):
        """Inicializar servidor"""
        from aiohttp import web
        
        self.app = web.Application()
        self.app.router.add_post('/api/analyze', self.analyze_endpoint)
        self.app.router.add_post('/api/lyrics', self.lyrics_endpoint)
        self.app.router.add_post('/api/classify', self.classify_endpoint)
        self.app.router.add_post('/api/optimize', self.optimize_endpoint)
        self.app.router.add_get('/api/health', self.health_endpoint)
        
        # Inicializar IA
        await self.ai.init()
        
        return web.run_app(self.app, host=self.host, port=self.port)
    
    async def analyze_endpoint(self, request):
        """Endpoint para análisis musical"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            
            analysis = await self.ai.analyze_music_prompt(prompt)
            
            return web.json_response({
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def lyrics_endpoint(self, request):
        """Endpoint para generación de letras"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            style = data.get('style', 'electronic')
            language = data.get('language', 'es')
            
            lyrics = await self.ai.generate_lyrics(prompt, style, language)
            
            return web.json_response({
                'success': True,
                'lyrics': lyrics,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def classify_endpoint(self, request):
        """Endpoint para clasificación de estilo"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            
            classification = await self.ai.classify_music_style(prompt)
            
            return web.json_response({
                'success': True,
                'classification': classification,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def optimize_endpoint(self, request):
        """Endpoint para optimización de prompts"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            
            optimization = await self.ai.optimize_prompt(prompt)
            
            return web.json_response({
                'success': True,
                'optimization': optimization,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def health_endpoint(self, request):
        """Endpoint de salud"""
        return web.json_response({
            'status': 'healthy',
            'ollama_available': self.ai.is_available,
            'available_models': self.ai.available_models,
            'timestamp': datetime.now().isoformat()
        })

async def main():
    """Función principal para ejecutar el servidor"""
    server = OllamaMusicAIServer()
    await server.init()

if __name__ == "__main__":
    asyncio.run(main())
