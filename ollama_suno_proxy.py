#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Ollama-Suno Proxy
Sistema inteligente que usa Ollama como intermediario para comunicación robusta con Suno
"""

import asyncio
import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from pathlib import Path

# Importar sistema de credenciales avanzado
from credential_manager import credential_manager, get_stealth_credentials
from stealth_suno_wrapper import generate_music_stealth, validate_suno_stealth

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaSunoProxy:
    """Proxy inteligente Ollama-Suno para comunicación robusta"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.suno_credentials = None
        self.audio_dir = Path("generated_audio")
        self.audio_dir.mkdir(exist_ok=True)
        
    async def check_ollama_health(self) -> bool:
        """Verificar que Ollama esté funcionando"""
        try:
            response = requests.get(f"{self.ollama_url}/api/version", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    async def _translate_to_english(self, text: str) -> str:
        """Traducir texto del español al inglés usando diccionario básico"""
        
        if not text or not text.strip():
            return text
        
        # Detectar si ya está en inglés (básico)
        english_words = ['the', 'and', 'with', 'song', 'music', 'guitar', 'piano', 'drums', 'bass', 'rock', 'pop', 'jazz', 'folk', 'classical', 'electronic', 'acoustic', 'electric', 'soft', 'hard', 'fast', 'slow', 'happy', 'sad', 'energetic', 'calm', 'beautiful', 'epic', 'melodic', 'rhythmic']
        
        # Si contiene palabras en inglés, asumir que ya está en inglés
        text_lower = text.lower()
        if any(word in text_lower for word in english_words):
            return text
        
        # Diccionario de traducción básico
        translations = {
            # Géneros musicales
            'música': 'music',
            'canción': 'song',
            'balada': 'ballad',
            'rock': 'rock',
            'pop': 'pop',
            'jazz': 'jazz',
            'folk': 'folk',
            'clásica': 'classical',
            'electrónica': 'electronic',
            'acústica': 'acoustic',
            'romántica': 'romantic',
            'energética': 'energetic',
            'triste': 'sad',
            'feliz': 'happy',
            'calma': 'calm',
            'épica': 'epic',
            'melódica': 'melodic',
            'rítmica': 'rhythmic',
            
            # Instrumentos
            'guitarra': 'guitar',
            'piano': 'piano',
            'batería': 'drums',
            'bajo': 'bass',
            'violín': 'violin',
            'saxofón': 'saxophone',
            'trompeta': 'trumpet',
            'flauta': 'flute',
            'armónica': 'harmonica',
            'banjo': 'banjo',
            
            # Descriptores
            'suave': 'soft',
            'fuerte': 'strong',
            'rápida': 'fast',
            'lenta': 'slow',
            'hermosa': 'beautiful',
            'increíble': 'amazing',
            'perfecta': 'perfect',
            'genial': 'great',
            'fantástica': 'fantastic',
            'increíble': 'incredible',
            
            # Acciones musicales
            'cantar': 'sing',
            'tocar': 'play',
            'bailar': 'dance',
            'escuchar': 'listen',
            'disfrutar': 'enjoy',
            'rockear': 'rock',
            'vibrar': 'vibe',
            'relajarse': 'relax',
            'celebrar': 'celebrate',
            'inspirar': 'inspire'
        }
        
        # Traducir palabra por palabra
        words = text.lower().split()
        translated_words = []
        
        for word in words:
            # Limpiar palabra de puntuación
            clean_word = word.strip('.,!?;:')
            if clean_word in translations:
                translated_words.append(translations[clean_word])
            else:
                translated_words.append(word)
        
        translation = ' '.join(translated_words)
        
        if translation != text:
            logger.info(f"🌐 Traducido: '{text}' → '{translation}'")
            return translation
        
        # Fallback: devolver texto original
        return text
    
    def setup_suno_credentials(self, session_id: str, cookie: str, token: str = None):
        """Configurar credenciales de Suno"""
        self.suno_credentials = {
            "session_id": session_id,
            "cookie": cookie,
            "token": token,
            "last_used": datetime.now()
        }
        logger.info("✅ Credenciales de Suno configuradas en proxy")
    
    async def generate_music_via_ollama(self, prompt: str, lyrics: str = "", style: str = "synthwave") -> Dict[str, Any]:
        """Generar música usando Ollama como intermediario inteligente"""
        
        # 1. Verificar Ollama
        if not await self.check_ollama_health():
            logger.error("❌ Ollama no disponible")
            return self._fallback_response("Ollama no disponible")
        
        # 2. Usar Ollama para optimizar el prompt para Suno
        optimized_prompt = await self._optimize_prompt_with_ollama(prompt, lyrics, style)
        
        # 3. Intentar generación con Suno usando el prompt optimizado
        if self.suno_credentials:
            suno_result = await self._try_suno_generation(optimized_prompt, lyrics, style)
            if suno_result["success"]:
                return suno_result
        
        # 4. Fallback: Generar música usando Ollama directamente
        return await self._generate_with_ollama_fallback(optimized_prompt, lyrics, style)
    
    async def _optimize_prompt_with_ollama(self, prompt: str, lyrics: str, style: str) -> str:
        """Usar Ollama para optimizar y traducir el prompt para Suno"""
        
        # Primero traducir al inglés si es necesario
        english_prompt = await self._translate_to_english(prompt)
        english_lyrics = await self._translate_to_english(lyrics) if lyrics else ""
        
        system_prompt = f"""Eres un experto en generación musical. 
Crea un prompt natural y descriptivo en INGLÉS para generar música:

Prompt original: {english_prompt}
Letra: {english_lyrics}
Estilo: {style}

Genera un prompt optimizado en INGLÉS que:
1. Use lenguaje natural y descriptivo
2. Incluya elementos musicales reales (instrumentos, tempo, mood)
3. Sea específico pero no técnico
4. Tenga máximo 150 caracteres
5. Suene como una descripción musical normal en inglés

Ejemplos de buenos prompts en inglés:
- "acoustic guitar folk song with warm vocals"
- "upbeat pop with electric guitar and drums"
- "soft piano ballad with strings"
- "rock song with heavy guitar riffs"
- "jazz piano with smooth saxophone"
- "country song with banjo and harmonica"

Responde SOLO con el prompt optimizado en inglés, sin explicaciones."""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.1:latest",
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 100
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized = result.get("response", prompt).strip()
                logger.info(f"🎯 Prompt optimizado: {optimized}")
                return optimized
                
        except Exception as e:
            logger.warning(f"⚠️ Error optimizando prompt: {e}")
        
        # Fallback al prompt original
        return f"{style} {prompt}"
    
    async def _try_suno_generation(self, prompt: str, lyrics: str, style: str) -> Dict[str, Any]:
        """Intentar generación con Suno usando sistema sigiloso"""
        
        try:
            logger.info(f"🎵 Intentando generación Suno sigilosa: {prompt[:50]}...")
            
            # Usar el wrapper sigiloso para generación real
            result = await generate_music_stealth(prompt, lyrics, style)
            
            if result and result.get("success"):
                logger.info("✅ Música generada exitosamente con Suno sigiloso")
                return {
                    "success": True,
                    "track": result["track"]
                }
            else:
                logger.warning("⚠️ Generación Suno falló, usando fallback")
                return {"success": False, "error": "Suno generation failed"}
            
        except Exception as e:
            logger.warning(f"⚠️ Error en generación Suno: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_with_ollama_fallback(self, prompt: str, lyrics: str, style: str) -> Dict[str, Any]:
        """Generar música usando Ollama como fallback"""
        
        logger.info("🔄 Usando Ollama para generación musical...")
        
        # Generar concepto musical con Ollama
        concept = await self._generate_music_concept_with_ollama(prompt, lyrics, style)
        
        # Generar audio sintético (simulación)
        audio_file = await self._generate_synthetic_audio(concept)
        
        return {
            "success": True,
            "track": {
                "id": f"ollama_{int(time.time())}",
                "title": concept.get("title", "Música generada por Ollama"),
                "filename": audio_file.name,
                "audio_url": f"/api/audio/stream/{audio_file.name}",
                "lyrics": concept.get("lyrics", lyrics),
                "prompt": prompt,
                "style": style,
                "created_at": datetime.now().isoformat(),
                "duration": 30,
                "download_url": f"/api/audio/download/{audio_file.name}",
                "suno_prompt": prompt,
                "is_simulation": True,
                "generated_by": "ollama"
            }
        }
    
    async def _generate_music_concept_with_ollama(self, prompt: str, lyrics: str, style: str) -> Dict[str, Any]:
        """Generar concepto musical detallado con Ollama"""
        
        # Traducir al inglés para mejor procesamiento
        english_prompt = await self._translate_to_english(prompt)
        english_lyrics = await self._translate_to_english(lyrics) if lyrics else ""
        
        system_prompt = f"""Eres un compositor musical profesional. Crea un concepto musical natural y realista en INGLÉS basado en:

Prompt: {english_prompt}
Letra: {english_lyrics}
Estilo: {style}

Responde SOLO en formato JSON en INGLÉS:
{{
    "title": "Song title in English (maximum 6 words)",
    "genre": "Real music genre (pop, rock, folk, jazz, etc.)",
    "mood": "Natural mood (happy, sad, energetic, calm, etc.)",
    "lyrics": "Complete song lyrics in English",
    "tempo": "Tempo in BPM (80-160)",
    "key": "Musical key (C major, A minor, etc.)",
    "instruments": "Real instruments (guitar, piano, drums, bass, etc.)",
    "style_tags": "Real music style tags",
    "description": "Natural description of the musical concept"
}}

Use real music genres and natural descriptions, not technical or futuristic terms. Everything in English."""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.1:latest",
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                concept_text = result.get("response", "{}").strip()
                
                # Limpiar respuesta de Ollama
                if concept_text.startswith("```json"):
                    concept_text = concept_text.replace("```json", "").replace("```", "").strip()
                
                try:
                    concept = json.loads(concept_text)
                    logger.info(f"🎼 Concepto generado: {concept.get('title', 'Sin título')}")
                    return concept
                except json.JSONDecodeError:
                    logger.warning("⚠️ Error parseando JSON de Ollama")
            
        except Exception as e:
            logger.warning(f"⚠️ Error generando concepto: {e}")
        
        # Fallback básico con conceptos naturales
        genre_map = {
            "pop": "pop",
            "rock": "rock", 
            "folk": "folk",
            "jazz": "jazz",
            "classical": "classical",
            "electronic": "electronic",
            "orchestral": "orchestral",
            "lofi": "lofi",
            "synthwave": "electronic",
            "cyberpunk": "electronic"
        }
        
        instrument_map = {
            "pop": "guitar, piano, drums, bass",
            "rock": "electric guitar, drums, bass",
            "folk": "acoustic guitar, violin, harmonica",
            "jazz": "piano, saxophone, double bass",
            "classical": "piano, strings, woodwinds",
            "orchestral": "orchestra, strings, brass",
            "electronic": "synthesizer, electronic drums",
            "lofi": "piano, soft drums, ambient sounds"
        }
        
        natural_genre = genre_map.get(style.lower(), "pop")
        natural_instruments = instrument_map.get(style.lower(), "guitar, piano, drums")
        
        return {
            "title": f"{prompt[:40].title()}",
            "genre": natural_genre,
            "mood": "happy",
            "lyrics": lyrics or f"Una canción sobre {prompt}",
            "tempo": "120 BPM",
            "key": "C major",
            "instruments": natural_instruments,
            "style_tags": f"{natural_genre}, {style}",
            "description": f"Canción {natural_genre} sobre {prompt}"
        }
    
    async def _generate_synthetic_audio(self, concept: Dict[str, Any]) -> Path:
        """Generar audio sintético usando numpy (simulación)"""
        
        try:
            import numpy as np
            from scipy.io import wavfile
            
            # Generar audio sintético básico
            sample_rate = 44100
            duration = 30  # segundos
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Generar tono base
            frequency = 440  # La nota A4
            audio = np.sin(2 * np.pi * frequency * t)
            
            # Agregar variación
            audio += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
            audio += 0.1 * np.sin(2 * np.pi * frequency * 4 * t)
            
            # Normalizar
            audio = audio / np.max(np.abs(audio))
            audio = (audio * 32767).astype(np.int16)
            
            # Guardar archivo
            filename = f"ollama_{int(time.time())}.wav"
            filepath = self.audio_dir / filename
            
            wavfile.write(filepath, sample_rate, audio)
            logger.info(f"🎵 Audio sintético generado: {filename}")
            
            return filepath
            
        except ImportError:
            logger.warning("⚠️ numpy/scipy no disponible - creando archivo vacío")
            # Crear archivo vacío como fallback
            filename = f"ollama_{int(time.time())}.mp3"
            filepath = self.audio_dir / filename
            filepath.touch()
            return filepath
        except Exception as e:
            logger.error(f"❌ Error generando audio: {e}")
            # Fallback
            filename = f"ollama_{int(time.time())}.mp3"
            filepath = self.audio_dir / filename
            filepath.touch()
            return filepath
    
    def _fallback_response(self, error: str) -> Dict[str, Any]:
        """Respuesta de fallback cuando todo falla"""
        return {
            "success": False,
            "error": error,
            "track": None
        }
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Obtener estado de conexiones"""
        ollama_status = await self.check_ollama_health()
        suno_status = self.suno_credentials is not None
        
        return {
            "ollama_connected": ollama_status,
            "suno_configured": suno_status,
            "status": "active" if ollama_status else "inactive"
        }

# Instancia global
ollama_suno_proxy = OllamaSunoProxy()

# Funciones de conveniencia
async def generate_music_with_ollama_proxy(prompt: str, lyrics: str = "", style: str = "synthwave") -> Dict[str, Any]:
    """Función de conveniencia para generar música con el proxy Ollama-Suno"""
    return await ollama_suno_proxy.generate_music_via_ollama(prompt, lyrics, style)

def setup_ollama_suno_proxy(session_id: str, cookie: str, token: str = None):
    """Configurar el proxy con credenciales de Suno"""
    ollama_suno_proxy.setup_suno_credentials(session_id, cookie, token)

async def get_ollama_suno_status() -> Dict[str, Any]:
    """Obtener estado del proxy"""
    return await ollama_suno_proxy.get_connection_status()
