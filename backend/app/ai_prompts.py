"""
AI-Powered Prompts System
Real Llama 3.1 8B integration for intelligent lyrics and style generation
"""
import os
import time
import logging
import asyncio
from typing import Dict, List, Optional
import ollama
import json
import hashlib
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIPromptsEngine:
    """Advanced AI prompts generation using Llama 3.1 8B"""
    
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.client = ollama.Client()
        self.prompt_cache = {}  # In-memory cache for successful prompts
        self.cache_expiry = timedelta(hours=24)
        
        # Verify model availability
        self._ensure_model_ready()
        
    def _ensure_model_ready(self) -> bool:
        """Ensure the AI model is available and ready"""
        try:
            # Check if model is available
            models = self.client.list()
            available_models = [model['name'] for model in models['models']]
            
            if self.model_name not in available_models:
                logger.warning(f"⚠️ Model {self.model_name} not found. Available: {available_models}")
                return False
            
            logger.info(f"✅ AI Model {self.model_name} is ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking AI model: {e}")
            return False
    
    def _get_cache_key(self, text: str, prompt_type: str) -> str:
        """Generate cache key for prompt"""
        combined = f"{prompt_type}:{text.lower().strip()}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cached_prompt(self, cache_key: str) -> Optional[str]:
        """Get cached prompt if still valid"""
        if cache_key in self.prompt_cache:
            cached_item = self.prompt_cache[cache_key]
            if datetime.now() - cached_item['timestamp'] < self.cache_expiry:
                logger.info(f"📋 Using cached prompt for key: {cache_key[:8]}...")
                return cached_item['result']
            else:
                # Remove expired cache
                del self.prompt_cache[cache_key]
        return None
    
    def _cache_prompt(self, cache_key: str, result: str):
        """Cache successful prompt result"""
        self.prompt_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        logger.info(f"💾 Cached prompt result for key: {cache_key[:8]}...")
    
    def generate_lyrics(self, prompt: str, style: str = "", language: str = "spanish") -> Dict:
        """
        Generate creative lyrics based on prompt and style
        
        Args:
            prompt: Main theme/concept for the song
            style: Musical style (pop, rock, ballad, etc.)
            language: Target language for lyrics
            
        Returns:
            Dictionary with generated lyrics and metadata
        """
        try:
            logger.info(f"🎤 Generating lyrics for: {prompt[:30]}...")
            
            # Check cache first
            cache_key = self._get_cache_key(f"{prompt}:{style}", "lyrics")
            cached_result = self._get_cached_prompt(cache_key)
            if cached_result:
                return {"lyrics": cached_result, "cached": True, "success": True}
            
            # Construct detailed prompt for AI
            system_prompt = f"""Eres un compositor profesional especializado en {language}. 
            Tu tarea es crear letras de canciones emotivas y creativas.
            
            INSTRUCCIONES:
            - Crea letras originales y emotivas
            - Incluye estructura clara: [Verso 1], [Coro], [Verso 2], [Coro], [Puente], [Coro Final]
            - Usa lenguaje poético pero comprensible
            - Mantén coherencia narrativa
            - Adapta el tono al estilo musical solicitado
            - Longitud: 150-200 palabras aproximadamente
            
            TEMA: {prompt}
            ESTILO MUSICAL: {style if style else 'universal'}
            IDIOMA: {language}
            
            Responde SOLO con las letras, sin explicaciones adicionales."""
            
            # Generate lyrics
            response = self.client.generate(
                model=self.model_name,
                prompt=system_prompt,
                options={
                    'temperature': 0.8,  # Creative but controlled
                    'top_p': 0.9,
                    'max_tokens': 400,
                    'stop': ['[FIN]', '[END]']
                }
            )
            
            generated_lyrics = response['response'].strip()
            
            # Post-process lyrics
            processed_lyrics = self._post_process_lyrics(generated_lyrics)
            
            # Cache successful result
            self._cache_prompt(cache_key, processed_lyrics)
            
            logger.info(f"✅ Generated lyrics: {len(processed_lyrics)} characters")
            
            return {
                "lyrics": processed_lyrics,
                "word_count": len(processed_lyrics.split()),
                "char_count": len(processed_lyrics),
                "cached": False,
                "success": True,
                "style": style,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating lyrics: {e}")
            return {
                "lyrics": self._get_fallback_lyrics(prompt, style),
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def generate_style_prompt(self, basic_input: str, mood: str = "", instruments: List[str] = None) -> Dict:
        """
        Generate creative musical style prompt from basic input
        
        Args:
            basic_input: Basic description or keywords
            mood: Desired mood/emotion
            instruments: Preferred instruments
            
        Returns:
            Dictionary with enhanced musical prompt
        """
        try:
            logger.info(f"🎵 Generating style prompt for: {basic_input[:30]}...")
            
            # Check cache
            cache_key = self._get_cache_key(f"{basic_input}:{mood}:{instruments}", "style")
            cached_result = self._get_cached_prompt(cache_key)
            if cached_result:
                return {"prompt": cached_result, "cached": True, "success": True}
            
            instruments_text = ", ".join(instruments) if instruments else "instrumentos variados"
            
            system_prompt = f"""Eres un productor musical experto en crear prompts detallados para generación de música.
            Tu tarea es transformar ideas básicas en prompts musicales ricos y específicos.
            
            INSTRUCCIONES:
            - Convierte la idea básica en un prompt musical detallado
            - Incluye información sobre: género, tempo, instrumentación, atmósfera
            - Agrega detalles técnicos específicos cuando sea relevante
            - Mantén el prompt entre 50-100 palabras
            - Usa lenguaje técnico musical profesional
            - Hazlo específico y evocativo
            
            IDEA BÁSICA: {basic_input}
            MOOD DESEADO: {mood if mood else 'versátil'}
            INSTRUMENTOS PREFERIDOS: {instruments_text}
            
            Responde SOLO con el prompt musical mejorado, sin explicaciones."""
            
            response = self.client.generate(
                model=self.model_name,
                prompt=system_prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'max_tokens': 200
                }
            )
            
            enhanced_prompt = response['response'].strip()
            
            # Post-process prompt
            processed_prompt = self._post_process_style_prompt(enhanced_prompt)
            
            # Cache result
            self._cache_prompt(cache_key, processed_prompt)
            
            logger.info(f"✅ Generated style prompt: {len(processed_prompt)} characters")
            
            return {
                "prompt": processed_prompt,
                "original_input": basic_input,
                "mood": mood,
                "instruments": instruments,
                "cached": False,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating style prompt: {e}")
            return {
                "prompt": self._get_fallback_style_prompt(basic_input, mood),
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def improve_existing_lyrics(self, lyrics: str, improvement_type: str = "general") -> Dict:
        """
        Improve existing lyrics with AI suggestions
        
        Args:
            lyrics: Original lyrics to improve
            improvement_type: Type of improvement (rhyme, flow, emotion, etc.)
            
        Returns:
            Dictionary with improved lyrics
        """
        try:
            logger.info(f"✨ Improving lyrics: {improvement_type}")
            
            improvement_instructions = {
                "rhyme": "Mejora la rima y métrica de estas letras",
                "emotion": "Aumenta la carga emocional y expresividad",
                "flow": "Mejora el flujo y ritmo para cantabilidad",
                "structure": "Reorganiza la estructura para mayor impacto",
                "general": "Mejora estas letras manteniendo su esencia"
            }
            
            instruction = improvement_instructions.get(improvement_type, improvement_instructions["general"])
            
            system_prompt = f"""{instruction}:

LETRAS ORIGINALES:
{lyrics}

INSTRUCCIONES:
- Mantén el mensaje y tema original
- Mejora según el tipo solicitado: {improvement_type}
- Conserva la estructura existente cuando sea posible
- Haz cambios sutiles pero efectivos
- Responde SOLO con las letras mejoradas

LETRAS MEJORADAS:"""
            
            response = self.client.generate(
                model=self.model_name,
                prompt=system_prompt,
                options={
                    'temperature': 0.6,
                    'top_p': 0.8,
                    'max_tokens': 500
                }
            )
            
            improved_lyrics = response['response'].strip()
            processed_lyrics = self._post_process_lyrics(improved_lyrics)
            
            logger.info(f"✅ Improved lyrics: {improvement_type}")
            
            return {
                "improved_lyrics": processed_lyrics,
                "original_lyrics": lyrics,
                "improvement_type": improvement_type,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error improving lyrics: {e}")
            return {
                "improved_lyrics": lyrics,  # Return original on error
                "success": False,
                "error": str(e)
            }
    
    def analyze_music_prompt(self, prompt: str) -> Dict:
        """
        Analyze a music prompt and provide suggestions
        
        Args:
            prompt: Music prompt to analyze
            
        Returns:
            Dictionary with analysis and suggestions
        """
        try:
            logger.info(f"🔍 Analyzing music prompt...")
            
            system_prompt = f"""Analiza este prompt musical y proporciona sugerencias de mejora:

PROMPT: {prompt}

Proporciona un análisis en formato JSON con:
- "genre": género musical detectado
- "mood": estado de ánimo/emoción
- "tempo": tempo sugerido (lento/medio/rápido)
- "instruments": instrumentos sugeridos
- "suggestions": lista de mejoras específicas
- "clarity_score": puntuación de claridad (1-10)

Responde SOLO con el JSON válido."""
            
            response = self.client.generate(
                model=self.model_name,
                prompt=system_prompt,
                options={
                    'temperature': 0.3,
                    'top_p': 0.7,
                    'max_tokens': 300
                }
            )
            
            try:
                analysis = json.loads(response['response'].strip())
            except json.JSONDecodeError:
                # Fallback parsing
                analysis = self._parse_analysis_fallback(response['response'])
            
            logger.info(f"✅ Analyzed prompt successfully")
            
            return {
                "analysis": analysis,
                "original_prompt": prompt,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing prompt: {e}")
            return {
                "analysis": self._get_fallback_analysis(prompt),
                "success": False,
                "error": str(e)
            }
    
    def _post_process_lyrics(self, lyrics: str) -> str:
        """Post-process generated lyrics for consistency"""
        # Clean up formatting
        lines = lyrics.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Ensure proper capitalization
                if line and line[0].islower() and not line.startswith('['):
                    line = line[0].upper() + line[1:]
                
                # Ensure structure markers are properly formatted
                if any(marker in line.lower() for marker in ['verso', 'coro', 'puente', 'estribillo']):
                    if not line.startswith('[') or not line.endswith(']'):
                        line = f"[{line.strip('[]')}]"
                
                processed_lines.append(line)
            else:
                processed_lines.append('')
        
        return '\n'.join(processed_lines)
    
    def _post_process_style_prompt(self, prompt: str) -> str:
        """Post-process style prompt for consistency"""
        # Clean and enhance the prompt
        prompt = prompt.strip()
        
        # Ensure it doesn't end with punctuation that might confuse AI
        if prompt.endswith('.'):
            prompt = prompt[:-1]
        
        # Ensure it's descriptive enough
        if len(prompt) < 30:
            prompt += ", con producción profesional y sonido pulido"
        
        return prompt
    
    def _get_fallback_lyrics(self, prompt: str, style: str) -> str:
        """Generate fallback lyrics when AI fails"""
        fallback_templates = {
            "pop": f"""[Verso 1]
{prompt} me inspira cada día
Como una melodía que no se olvida
En cada nota encuentro la alegría
De una historia que apenas comienza

[Coro]
Esta es nuestra canción
Que nace del corazón
Con {prompt}
Bailamos sin cesar

[Verso 2]
Las palabras fluyen como el viento
Llevando mensajes de esperanza
En cada verso un sentimiento
Que nos une en esta danza""",
            
            "rock": f"""[Verso 1]
{prompt} enciende el fuego interior
Como guitarras que gritan verdad
En cada acorde hay un rugido
Que despierta nuestra libertad

[Coro]
Romperemos las cadenas
Con el poder del rock
{prompt} en nuestras venas
Nada nos va a parar

[Verso 2]
Los amplificadores devoran el silencio
Y en cada golpe de batería
Nace la fuerza de nuestro grito
Que resuena hasta el nuevo día""",
            
            "ballad": f"""[Verso 1]
En la quietud de la noche
{prompt} me acompaña
Como susurros del alma
Que calman cuando el corazón se daña

[Coro]
Esta balada es para ti
Escrita en las estrellas
Con {prompt}
Te canto estas querelas

[Verso 2]
Las lágrimas se vuelven melodía
Y el dolor se transforma en canción
En cada nota hay poesía
Que sana cada herida del corazón"""
        }
        
        return fallback_templates.get(style.lower(), fallback_templates["pop"])
    
    def _get_fallback_style_prompt(self, basic_input: str, mood: str) -> str:
        """Generate fallback style prompt"""
        mood_descriptors = {
            "happy": "alegre y energético",
            "sad": "melancólico y emotivo", 
            "energetic": "vibrante y dinámico",
            "peaceful": "sereno y contemplativo",
            "romantic": "romántico y suave"
        }
        
        mood_desc = mood_descriptors.get(mood.lower(), "expresivo")
        
        return f"Una composición {mood_desc} inspirada en {basic_input}, con instrumentación rica y producción moderna, tempo medio, ideal para transmitir emociones profundas"
    
    def _parse_analysis_fallback(self, response_text: str) -> Dict:
        """Parse analysis response when JSON fails"""
        return {
            "genre": "universal",
            "mood": "expresivo",
            "tempo": "medio", 
            "instruments": ["piano", "guitarra", "batería"],
            "suggestions": ["Agregar más detalles específicos", "Definir mejor el género"],
            "clarity_score": 7
        }
    
    def _get_fallback_analysis(self, prompt: str) -> Dict:
        """Generate fallback analysis"""
        return {
            "genre": "pop",
            "mood": "neutral",
            "tempo": "medio",
            "instruments": ["varios"],
            "suggestions": ["El prompt está bien estructurado"],
            "clarity_score": 8
        }
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cached_prompts": len(self.prompt_cache),
            "cache_size_mb": sum(len(str(item)) for item in self.prompt_cache.values()) / (1024 * 1024),
            "oldest_cache": min([item['timestamp'] for item in self.prompt_cache.values()]) if self.prompt_cache else None
        }
    
    def clear_cache(self):
        """Clear prompt cache"""
        self.prompt_cache.clear()
        logger.info("🧹 Prompt cache cleared")


# Global instance
ai_engine = AIPromptsEngine()