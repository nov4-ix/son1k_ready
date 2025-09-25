"""
Integración stealth con Suno API usando el wrapper Node.js
"""
import asyncio
import aiohttp
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SunoStealthIntegration:
    def __init__(self, wrapper_url: str = "http://localhost:3001"):
        self.wrapper_url = wrapper_url
        self.session = None
        self.available = False
        
    async def initialize(self) -> bool:
        """Inicializar la conexión con el wrapper"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Verificar que el wrapper esté funcionando
            async with self.session.get(f"{self.wrapper_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.available = data.get('status') == 'healthy'
                    logger.info(f"✅ Suno Stealth Wrapper conectado: {data.get('version', 'unknown')}")
                    return self.available
                else:
                    logger.warning(f"⚠️ Wrapper no disponible: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error conectando con Suno Stealth Wrapper: {e}")
            return False
    
    async def generate_music(self, prompt: str, lyrics: str = "", style: str = "profesional") -> Dict[str, Any]:
        """Generar música usando el wrapper stealth"""
        if not self.available or not self.session:
            return {"success": False, "error": "Suno Stealth Wrapper no disponible"}
        
        try:
            logger.info(f"🎵 [STEALTH] Generando música: {prompt[:50]}...")
            
            payload = {
                "prompt": prompt,
                "lyrics": lyrics,
                "style": style
            }
            
            async with self.session.post(
                f"{self.wrapper_url}/generate-music",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minutos timeout
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        logger.info(f"✅ [STEALTH] Música generada: {data.get('metadata', {}).get('audioCount', 0)} versiones")
                        return {
                            "success": True,
                            "audio_urls": data.get('audioUrls', []),
                            "lyrics": data.get('lyrics', lyrics),
                            "metadata": data.get('metadata', {}),
                            "mode": "suno_stealth"
                        }
                    else:
                        logger.error(f"❌ [STEALTH] Error en generación: {data.get('error')}")
                        return {
                            "success": False,
                            "error": data.get('error', 'Error desconocido'),
                            "mode": "suno_stealth"
                        }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [STEALTH] HTTP {response.status}: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "mode": "suno_stealth"
                    }
                    
        except asyncio.TimeoutError:
            logger.error("❌ [STEALTH] Timeout en generación")
            return {
                "success": False,
                "error": "Timeout en generación (5 minutos)",
                "mode": "suno_stealth"
            }
        except Exception as e:
            logger.error(f"❌ [STEALTH] Error en generación: {e}")
            return {
                "success": False,
                "error": str(e),
                "mode": "suno_stealth"
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del wrapper"""
        if not self.available or not self.session:
            return {"error": "Wrapper no disponible"}
        
        try:
            async with self.session.get(f"{self.wrapper_url}/stats") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def add_cookie(self, cookie: str) -> bool:
        """Agregar cookie al pool del wrapper"""
        if not self.available or not self.session:
            return False
        
        try:
            async with self.session.post(
                f"{self.wrapper_url}/add-cookie",
                json={"cookie": cookie}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('success', False)
                return False
        except Exception as e:
            logger.error(f"❌ Error agregando cookie: {e}")
            return False
    
    async def cleanup(self):
        """Limpiar recursos"""
        if self.session:
            await self.session.close()
            self.session = None

# Instancia global
suno_stealth_integration = SunoStealthIntegration()

async def generate_music_with_suno_stealth(prompt: str, lyrics: str = "", style: str = "profesional") -> Dict[str, Any]:
    """Función de conveniencia para generar música con Suno Stealth"""
    if not suno_stealth_integration.available:
        if not await suno_stealth_integration.initialize():
            return {"success": False, "error": "No se pudo inicializar Suno Stealth Wrapper"}
    
    return await suno_stealth_integration.generate_music(prompt, lyrics, style)




