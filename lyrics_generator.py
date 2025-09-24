"""
Generador de Letras con Ollama para Son1kvers3
Sistema optimizado por tiers según la guía
"""

import requests
import logging
from typing import Dict, Any, Optional
from credit_manager import credit_manager

logger = logging.getLogger(__name__)

class LyricsGenerator:
    def __init__(self, user_tier: str = "free"):
        self.user_tier = user_tier
        self.config = credit_manager.get_ollama_config(user_tier)
        self.ollama_url = "http://localhost:11434"
    
    def generate_lyrics(self, theme: str, genre: str = "pop", language: str = "es", 
                       structure: str = "verse-chorus-verse-chorus-bridge-chorus") -> Dict[str, Any]:
        """Generar letras usando Ollama con configuración por tier"""
        try:
            # Crear prompt optimizado según el tier
            prompt = self._create_lyrics_prompt(theme, genre, language, structure)
            
            # Configurar parámetros según el tier
            ollama_payload = {
                "model": self.config["model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config["temperature"],
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "num_predict": self.config["max_tokens"]
                }
            }
            
            logger.info(f"🎵 Generando letras con Ollama (tier: {self.user_tier}, modelo: {self.config['model']})")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=ollama_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_lyrics = result.get("response", "").strip()
                
                if generated_lyrics:
                    logger.info("✅ Letras generadas exitosamente con Ollama")
                    return {
                        "success": True,
                        "lyrics": generated_lyrics,
                        "model_used": self.config["model"],
                        "tier": self.user_tier,
                        "quality": self.config["quality"],
                        "source": "ollama"
                    }
            
            # Fallback si Ollama falla
            logger.warning("⚠️ Ollama falló, usando generador de respaldo")
            return self._generate_fallback_lyrics(theme, genre, language)
            
        except Exception as e:
            logger.error(f"❌ Error generando letras: {e}")
            return self._generate_fallback_lyrics(theme, genre, language)
    
    def _create_lyrics_prompt(self, theme: str, genre: str, language: str, structure: str) -> str:
        """Crear prompt optimizado según el tier del usuario"""
        
        # Prompt base para todos los tiers
        base_prompt = f"""Eres un compositor profesional especializado en el universo de Son1kvers3. Crea letras con coherencia narrativa basadas en el tema del usuario.

Tema del usuario: {theme}
Género: {genre}
Idioma: {language}
Estructura: {structure}

Crea letras completas que:
- Tengan un hilo narrativo claro
- Usen el tema del usuario de manera significativa
- Sigan la estructura solicitada
- Coincidan con el género y mood
- Sean cantables y rítmicas"""

        # Añadir características específicas por tier
        if self.user_tier == "free":
            prompt = f"""{base_prompt}
- Formato simple con etiquetas [Verse], [Chorus], [Bridge]
- Longitud moderada (2-3 versos, 2-3 coros)
- Lenguaje directo y accesible

Responde SOLO con las letras, sin explicaciones adicionales."""
        
        elif self.user_tier == "pro":
            prompt = f"""{base_prompt}
- Incluye referencias al lore de "La Resistencia" cuando sea apropiado
- Formato profesional con etiquetas claras [Verse], [Chorus], [Bridge]
- Longitud completa (3-4 versos, 3-4 coros, puente)
- Lenguaje más sofisticado y creativo
- Incluye elementos de storytelling

Responde SOLO con las letras, sin explicaciones adicionales."""
        
        else:  # premium
            prompt = f"""{base_prompt}
- Integra profundamente el lore de "La Resistencia" y el universo cyberpunk
- Formato premium con etiquetas detalladas [Verse 1], [Chorus], [Verse 2], [Chorus], [Bridge], [Final Chorus]
- Longitud completa y elaborada (4+ versos, 4+ coros, puente complejo)
- Lenguaje sofisticado, poético y técnico
- Incluye storytelling avanzado y referencias culturales
- Adapta el estilo según el género específico
- Incluye elementos de resistencia y rebelión digital

Responde SOLO con las letras, sin explicaciones adicionales."""
        
        return prompt
    
    def _generate_fallback_lyrics(self, theme: str, genre: str, language: str) -> Dict[str, Any]:
        """Generar letras de respaldo cuando Ollama no está disponible"""
        
        # Letras de respaldo básicas
        fallback_lyrics = f"""[Verse 1]
{theme} es lo que siento
En este mundo digital
La música es mi refugio
Mi forma de expresar

[Chorus]
{theme}, {theme}
Es mi canción
{theme}, {theme}
Mi inspiración

[Verse 2]
En Son1kvers3 creo
Con la IA como aliada
La resistencia musical
Nunca se acaba

[Chorus]
{theme}, {theme}
Es mi canción
{theme}, {theme}
Mi inspiración

[Bridge]
La tecnología y el arte
Se unen en armonía
Creando algo nuevo
Cada día

[Final Chorus]
{theme}, {theme}
Es mi canción
{theme}, {theme}
Mi inspiración"""

        return {
            "success": True,
            "lyrics": fallback_lyrics,
            "model_used": "fallback_generator",
            "tier": self.user_tier,
            "quality": "básica",
            "source": "fallback",
            "note": "Generado con sistema de respaldo - Ollama no disponible"
        }
    
    def generate_prompt(self, user_input: str, genre: str = "pop", mood: str = "emotional") -> Dict[str, Any]:
        """Generar prompt musical optimizado usando Ollama"""
        try:
            prompt_text = f"""Eres un ingeniero de prompts musicales experto para Son1kvers3. Genera prompts creativos y detallados para generación de música con IA.

Input del usuario: {user_input}
Género preferido: {genre}
Mood: {mood}

Genera un prompt conciso pero descriptivo que incluya:
- Estilo musical y género específico
- Tempo y ritmo (ej: 128 BPM, 4/4)
- Instrumentación detallada
- Mood y atmósfera
- Estilo de producción
- Efectos especiales si aplica

Manténlo bajo 100 palabras y hazlo específico para generación de música con IA.
Responde SOLO con el prompt generado, sin explicaciones adicionales."""

            ollama_payload = {
                "model": self.config["model"],
                "prompt": prompt_text,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "num_predict": 200  # Prompts más cortos
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=ollama_payload,
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_prompt = result.get("response", "").strip()
                
                if generated_prompt:
                    logger.info("✅ Prompt musical generado exitosamente con Ollama")
                    return {
                        "success": True,
                        "generated_prompt": generated_prompt,
                        "model_used": self.config["model"],
                        "tier": self.user_tier,
                        "source": "ollama"
                    }
            
            # Fallback
            fallback_prompt = f"Create a {genre} song with {mood} vibes, 128 BPM, electronic production"
            return {
                "success": True,
                "generated_prompt": fallback_prompt,
                "model_used": "fallback",
                "tier": self.user_tier,
                "source": "fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando prompt: {e}")
            fallback_prompt = f"Create a {genre} song with {mood} vibes, 128 BPM, electronic production"
            return {
                "success": True,
                "generated_prompt": fallback_prompt,
                "model_used": "fallback",
                "tier": self.user_tier,
                "source": "fallback"
            }
