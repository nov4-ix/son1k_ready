#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Wrapper Suno Sigiloso
Sistema anti-detección para Suno con rotación automática de cuentas
"""

import asyncio
import json
import time
import random
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import requests
from pathlib import Path
import secrets
import hashlib

from credential_manager import credential_manager, get_stealth_credentials

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StealthSunoWrapper:
    """Wrapper Suno con técnicas anti-detección"""
    
    def __init__(self):
        self.base_url = "https://suno.com"
        self.api_url = f"{self.base_url}/api"
        self.audio_dir = Path("generated_audio")
        self.audio_dir.mkdir(exist_ok=True)
        
        # Configuración anti-detección
        self.request_delays = (1, 3)  # Delay entre requests
        self.session_timeout = 30
        self.max_retries = 3
        self.retry_delay = (5, 15)
        
        # Patrones de comportamiento humano
        self.human_patterns = {
            "browse_time": (2, 8),  # Tiempo navegando
            "think_time": (1, 4),   # Tiempo "pensando"
            "typing_speed": (0.1, 0.3)  # Velocidad de escritura
        }
    
    async def _human_delay(self, delay_type: str = "request"):
        """Simular comportamiento humano con delays"""
        if delay_type == "request":
            delay = random.uniform(*self.request_delays)
        elif delay_type == "browse":
            delay = random.uniform(*self.human_patterns["browse_time"])
        elif delay_type == "think":
            delay = random.uniform(*self.human_patterns["think_time"])
        else:
            delay = random.uniform(1, 2)
        
        await asyncio.sleep(delay)
    
    async def _make_stealth_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Hacer request con configuración anti-detección"""
        
        # Obtener credenciales sigilosas
        credentials = await get_stealth_credentials()
        if not credentials:
            logger.error("❌ No hay credenciales disponibles")
            return None
        
        # Configurar headers anti-detección
        headers = credentials["headers"].copy()
        headers.update(kwargs.get("headers", {}))
        
        # Agregar headers adicionales para parecer más humano
        headers.update({
            "Referer": f"{self.base_url}/",
            "Origin": self.base_url,
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "X-Forwarded-For": self._generate_fake_ip(),
            "X-Real-IP": self._generate_fake_ip()
        })
        
        # Configurar proxy si está disponible
        proxy_config = credentials.get("proxy")
        
        # Simular comportamiento humano
        await self._human_delay("request")
        
        try:
            async with httpx.AsyncClient(
                timeout=self.session_timeout,
                proxies=proxy_config,
                follow_redirects=True
            ) as client:
                
                url = f"{self.api_url}{endpoint}"
                
                # Agregar parámetros aleatorios para evitar cache
                if "?" in url:
                    url += f"&_t={int(time.time())}&_r={random.randint(1000, 9999)}"
                else:
                    url += f"?_t={int(time.time())}&_r={random.randint(1000, 9999)}"
                
                response = await client.request(method, url, headers=headers, **kwargs)
                
                # Simular tiempo de "lectura" de respuesta
                await self._human_delay("think")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    logger.warning("⚠️ Rate limited, esperando...")
                    await asyncio.sleep(random.uniform(30, 60))
                    return None
                elif response.status_code == 403:  # Forbidden
                    logger.warning("⚠️ Acceso denegado, rotando cuenta...")
                    await self._rotate_account()
                    return None
                else:
                    logger.warning(f"⚠️ Error HTTP {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error en request: {e}")
            return None
    
    def _generate_fake_ip(self) -> str:
        """Generar IP falsa para headers"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    async def _rotate_account(self):
        """Rotar a la siguiente cuenta disponible"""
        logger.info("🔄 Rotando cuenta de Suno...")
        # La rotación se maneja automáticamente en credential_manager
        await asyncio.sleep(random.uniform(2, 5))
    
    async def generate_music(self, prompt: str, lyrics: str = "", style: str = "pop") -> Optional[Dict[str, Any]]:
        """Generar música con Suno usando técnicas anti-detección"""
        
        logger.info(f"🎵 Generando música sigilosa: {prompt[:50]}...")
        
        # Simular comportamiento de usuario navegando
        await self._human_delay("browse")
        
        # Crear prompt optimizado
        optimized_prompt = self._optimize_prompt(prompt, lyrics, style)
        
        # Simular tiempo de "escritura" del prompt
        typing_delay = len(optimized_prompt) * random.uniform(*self.human_patterns["typing_speed"])
        await asyncio.sleep(typing_delay)
        
        # Preparar datos de generación
        generation_data = {
            "prompt": optimized_prompt,
            "lyrics": lyrics,
            "style": style,
            "duration": 30,
            "model": "chirp-v3-5",
            "custom_mode": False,
            "tags": self._generate_realistic_tags(style),
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "user_agent": "web",
                "version": "1.0"
            }
        }
        
        # Intentar generación con retry
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🎼 Intento {attempt + 1} de generación...")
                
                # Simular tiempo de "pensamiento" antes de generar
                await self._human_delay("think")
                
                response = await self._make_stealth_request(
                    "POST",
                    "/generate/v2/",
                    json=generation_data
                )
                
                if response and response.get("clips"):
                    track_data = response["clips"][0]
                    
                    # Simular tiempo de "escucha" de la preview
                    await self._human_delay("browse")
                    
                    return {
                        "success": True,
                        "track": {
                            "id": track_data.get("id"),
                            "title": track_data.get("title", "Generated Track"),
                            "audio_url": track_data.get("audio_url"),
                            "video_url": track_data.get("video_url"),
                            "image_url": track_data.get("image_url"),
                            "lyrics": lyrics,
                            "prompt": prompt,
                            "style": style,
                            "created_at": datetime.now().isoformat(),
                            "duration": track_data.get("duration", 30),
                            "suno_prompt": optimized_prompt,
                            "is_simulation": False,
                            "generated_by": "suno_stealth"
                        }
                    }
                else:
                    logger.warning(f"⚠️ Intento {attempt + 1} falló, reintentando...")
                    await asyncio.sleep(random.uniform(*self.retry_delay))
                    
            except Exception as e:
                logger.error(f"❌ Error en intento {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(random.uniform(*self.retry_delay))
        
        logger.error("❌ Todos los intentos de generación fallaron")
        return None
    
    def _optimize_prompt(self, prompt: str, lyrics: str, style: str) -> str:
        """Optimizar prompt para mejor generación"""
        
        # Mapeo de estilos a prompts optimizados
        style_prompts = {
            "pop": "upbeat pop song with catchy melody",
            "rock": "energetic rock song with electric guitar",
            "folk": "acoustic folk song with guitar and harmonica",
            "jazz": "smooth jazz with piano and saxophone",
            "classical": "orchestral classical piece",
            "electronic": "electronic dance music with synthesizers",
            "lofi": "chill lofi hip hop beat",
            "country": "country song with banjo and fiddle",
            "blues": "blues song with guitar and harmonica",
            "reggae": "reggae song with offbeat rhythm"
        }
        
        base_prompt = style_prompts.get(style.lower(), f"{style} song")
        
        # Combinar con prompt del usuario
        if prompt:
            optimized = f"{base_prompt}, {prompt.lower()}"
        else:
            optimized = base_prompt
        
        # Agregar elementos musicales si hay letra
        if lyrics:
            optimized += ", with vocals and lyrics"
        
        # Limitar longitud
        return optimized[:200]
    
    def _generate_realistic_tags(self, style: str) -> List[str]:
        """Generar tags realistas para el estilo"""
        
        tag_map = {
            "pop": ["catchy", "upbeat", "melodic", "radio-friendly"],
            "rock": ["energetic", "guitar-driven", "powerful", "anthemic"],
            "folk": ["acoustic", "storytelling", "organic", "intimate"],
            "jazz": ["smooth", "sophisticated", "improvisational", "swinging"],
            "classical": ["orchestral", "dramatic", "elegant", "timeless"],
            "electronic": ["synthetic", "danceable", "futuristic", "rhythmic"],
            "lofi": ["chill", "relaxing", "nostalgic", "ambient"],
            "country": ["down-home", "storytelling", "traditional", "heartfelt"],
            "blues": ["soulful", "raw", "emotional", "gritty"],
            "reggae": ["laid-back", "island", "rhythmic", "uplifting"]
        }
        
        return tag_map.get(style.lower(), ["musical", "creative", "original"])
    
    async def get_track_status(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de una pista"""
        
        await self._human_delay("request")
        
        response = await self._make_stealth_request(
            "GET",
            f"/feed/?ids={track_id}"
        )
        
        if response and response.get("clips"):
            return response["clips"][0]
        
        return None
    
    async def get_user_credits(self) -> Optional[Dict[str, int]]:
        """Obtener créditos del usuario"""
        
        await self._human_delay("request")
        
        response = await self._make_stealth_request(
            "GET",
            "/billing/info/"
        )
        
        if response:
            return {
                "total_credits_left": response.get("total_credits_left", 0),
                "period_credits_left": response.get("period_credits_left", 0),
                "monthly_limit": response.get("monthly_limit", 0),
                "monthly_usage": response.get("monthly_usage", 0)
            }
        
        return None
    
    async def validate_connection(self) -> bool:
        """Validar conexión con Suno"""
        
        try:
            response = await self._make_stealth_request(
                "GET",
                "/feed/"
            )
            
            return response is not None
        except Exception as e:
            logger.error(f"❌ Error validando conexión: {e}")
            return False

# Instancia global
stealth_suno = StealthSunoWrapper()

# Funciones de conveniencia
async def generate_music_stealth(prompt: str, lyrics: str = "", style: str = "pop") -> Optional[Dict[str, Any]]:
    """Generar música con Suno usando modo sigiloso"""
    return await stealth_suno.generate_music(prompt, lyrics, style)

async def validate_suno_stealth() -> bool:
    """Validar conexión Suno en modo sigiloso"""
    return await stealth_suno.validate_connection()

async def get_suno_credits_stealth() -> Optional[Dict[str, int]]:
    """Obtener créditos Suno en modo sigiloso"""
    return await stealth_suno.get_user_credits()
