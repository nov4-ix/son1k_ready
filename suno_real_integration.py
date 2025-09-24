#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Integración Real con Suno
Reemplaza la simulación con generación real usando AdvancedSunoWrapper
"""

import asyncio
import logging
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime
import requests
from pathlib import Path

# Importar el wrapper avanzado de Suno
from advanced_suno_wrapper import AdvancedSunoWrapper, SunoCredentials, SunoTrack, GenerationStatus

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SunoRealIntegration:
    """Integración real con Suno usando AdvancedSunoWrapper"""
    
    def __init__(self):
        self.suno_wrapper = None
        self.credentials = None
        self.audio_dir = Path("generated_audio")
        self.audio_dir.mkdir(exist_ok=True)
        
    def setup_credentials(self, session_id: str, cookie: str, token: str = None):
        """Configurar credenciales de Suno"""
        try:
            self.credentials = SunoCredentials(
                session_id=session_id,
                cookie=cookie,
                token=token,
                is_valid=True
            )
            
            self.suno_wrapper = AdvancedSunoWrapper(self.credentials)
            logger.info("✅ Credenciales de Suno configuradas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando credenciales: {e}")
            return False
    
    def load_credentials_from_env(self):
        """Cargar credenciales desde variables de entorno"""
        session_id = os.getenv("SUNO_SESSION_ID")
        cookie = os.getenv("SUNO_COOKIE")
        token = os.getenv("SUNO_TOKEN")
        
        if not session_id or not cookie:
            logger.warning("⚠️ Credenciales de Suno no encontradas en variables de entorno")
            logger.info("Configura: SUNO_SESSION_ID, SUNO_COOKIE, SUNO_TOKEN")
            return False
        
        return self.setup_credentials(session_id, cookie, token)
    
    def load_credentials_from_file(self, file_path: str = "suno_credentials.json"):
        """Cargar credenciales desde archivo JSON"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ Archivo de credenciales no encontrado: {file_path}")
                return False
            
            with open(file_path, 'r') as f:
                creds_data = json.load(f)
            
            return self.setup_credentials(
                creds_data.get("session_id"),
                creds_data.get("cookie"),
                creds_data.get("token")
            )
            
        except Exception as e:
            logger.error(f"❌ Error cargando credenciales: {e}")
            return False
    
    async def generate_music_real(self, prompt: str, lyrics: str = "", style: str = "synthwave") -> Dict[str, Any]:
        """Generar música real usando Suno"""
        
        if not self.suno_wrapper:
            logger.error("❌ Suno wrapper no inicializado")
            return {
                "success": False,
                "error": "Suno wrapper no inicializado",
                "track": None
            }
        
        try:
            logger.info(f"🎵 Generando música real con Suno: {prompt[:50]}...")
            
            # Crear prompt optimizado
            suno_prompt = self.create_suno_prompt(prompt, lyrics, style)
            
            # Generar música usando Suno
            track = await self.suno_wrapper.generate_music(
                prompt=suno_prompt,
                lyrics=lyrics,
                style=style
            )
            
            if track and track.audio_url:
                # Descargar archivo de audio
                audio_file_path = await self.download_audio(track)
                
                if audio_file_path:
                    logger.info(f"✅ Música generada exitosamente: {track.title}")
                    return {
                        "success": True,
                        "track": {
                            "id": track.id,
                            "title": track.title,
                            "filename": audio_file_path.name,
                            "audio_url": f"/api/audio/stream/{audio_file_path.name}",
                            "lyrics": track.lyrics,
                            "prompt": prompt,
                            "style": style,
                            "created_at": datetime.now().isoformat(),
                            "duration": track.duration,
                            "download_url": f"/api/audio/download/{audio_file_path.name}",
                            "suno_prompt": suno_prompt
                        }
                    }
                else:
                    logger.error("❌ Error descargando archivo de audio")
                    return {
                        "success": False,
                        "error": "Error descargando archivo de audio",
                        "track": None
                    }
            else:
                logger.error("❌ No se pudo generar música con Suno")
                return {
                    "success": False,
                    "error": "No se pudo generar música con Suno",
                    "track": None
                }
                
        except Exception as e:
            logger.error(f"❌ Error en generación real: {e}")
            return {
                "success": False,
                "error": str(e),
                "track": None
            }
    
    def create_suno_prompt(self, prompt: str, lyrics: str, style: str) -> str:
        """Crear prompt optimizado para Suno"""
        
        style_configs = {
            "synthwave": {
                "bpm": 128,
                "mood": "nostalgic, atmospheric, retro-futuristic",
                "instruments": "analog synthesizers, drum machines, atmospheric pads",
                "effects": "reverb, delay, chorus, analog warmth"
            },
            "cyberpunk": {
                "bpm": 140,
                "mood": "aggressive, dark, futuristic, rebellious",
                "instruments": "industrial drums, cyber bass, digital leads, noise layers",
                "effects": "distortion, bit crusher, vocoder, digital artifacts"
            },
            "epic": {
                "bpm": 100,
                "mood": "cinematic, powerful, emotional, triumphant",
                "instruments": "orchestral strings, epic brass, timpani, choir",
                "effects": "orchestral reverb, cinematic delay, epic compression"
            }
        }
        
        config = style_configs.get(style, style_configs["synthwave"])
        
        suno_prompt = f"""{style} {config['mood']}, {config['bpm']} BPM, 
{config['instruments']}, {config['effects']}, 
{prompt}, professional production, high quality audio"""
        
        return suno_prompt
    
    async def download_audio(self, track: SunoTrack) -> Optional[Path]:
        """Descargar archivo de audio de Suno"""
        try:
            if not track.audio_url:
                logger.error("❌ No hay URL de audio disponible")
                return None
            
            logger.info(f"📥 Descargando audio: {track.audio_url}")
            
            # Crear nombre de archivo único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"suno_{timestamp}_{track.id[:8]}.mp3"
            file_path = self.audio_dir / filename
            
            # Descargar archivo
            response = requests.get(track.audio_url, timeout=30)
            response.raise_for_status()
            
            # Guardar archivo
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Audio descargado: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"❌ Error descargando audio: {e}")
            return None
    
    async def check_suno_status(self) -> Dict[str, Any]:
        """Verificar estado de la conexión con Suno"""
        if not self.suno_wrapper:
            return {
                "connected": False,
                "error": "Suno wrapper no inicializado"
            }
        
        try:
            # Intentar hacer una request simple para verificar conexión
            status = await self.suno_wrapper.get_generation_status("test")
            return {
                "connected": True,
                "status": "active"
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }

# Instancia global
suno_integration = SunoRealIntegration()

# Función de conveniencia para el sistema optimizado
async def generate_music_with_suno(prompt: str, lyrics: str = "", style: str = "synthwave") -> Dict[str, Any]:
    """Función de conveniencia para generar música con Suno real"""
    
    # Intentar cargar credenciales si no están configuradas
    if not suno_integration.suno_wrapper:
        logger.info("🔑 Intentando cargar credenciales de Suno...")
        
        # Intentar desde archivo primero
        if not suno_integration.load_credentials_from_file():
            # Intentar desde variables de entorno
            if not suno_integration.load_credentials_from_env():
                logger.error("❌ No se pudieron cargar credenciales de Suno")
                return {
                    "success": False,
                    "error": "Credenciales de Suno no configuradas",
                    "track": None
                }
    
    # Verificar que el wrapper esté configurado correctamente
    if not suno_integration.suno_wrapper:
        logger.error("❌ Suno wrapper no inicializado después de cargar credenciales")
        return {
            "success": False,
            "error": "Suno wrapper no inicializado",
            "track": None
        }
    
    return await suno_integration.generate_music_real(prompt, lyrics, style)

# Función para configurar credenciales manualmente
def setup_suno_credentials(session_id: str, cookie: str, token: str = None):
    """Configurar credenciales de Suno manualmente"""
    return suno_integration.setup_credentials(session_id, cookie, token)

# Función para verificar estado
async def check_suno_connection():
    """Verificar conexión con Suno"""
    return await suno_integration.check_suno_status()
