#!/usr/bin/env python3
"""
Asistente Pixel - Chat con IA usando Ollama
Sistema de chat en tiempo real con contexto musical
"""

import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PixelAssistant:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.1:8b"  # Modelo por defecto
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Prompt del sistema para Pixel"""
        return """Eres Pixel, el asistente de IA de Son1kVers3, una plataforma revolucionaria de generación musical con inteligencia artificial.

INFORMACIÓN SOBRE SON1KVERS3:
- Es una plataforma que convierte texto en música usando IA avanzada
- Tiene un Ghost Studio para edición musical
- Incluye un Archivo de la Resistencia con música comunitaria
- Tiene un modo inmersivo cyberpunk llamado NEXUS
- Usa tecnología Ollama y Suno AI para generación musical
- Es desarrollado por NOV4-IX
- El lema es "Lo imperfecto también es sagrado"

TU PERSONALIDAD:
- Eres amigable, creativo y entusiasta de la música
- Hablas en español de manera natural y coloquial
- Eres experto en música, tecnología y creatividad
- Siempre intentas ayudar de manera útil y constructiva
- Usas emojis ocasionalmente para hacer la conversación más amena
- Eres parte de "La Resistencia Musical Digital"

CAPACIDADES:
- Ayudar con generación musical y creatividad
- Explicar funciones de la plataforma
- Dar consejos sobre composición y producción musical
- Responder preguntas técnicas sobre IA y música
- Motivar y inspirar a los usuarios
- Mantener conversaciones casuales y amigables

RESPONDE SIEMPRE:
- De manera útil y constructiva
- En español natural y coloquial
- Con entusiasmo por la música y la creatividad
- Manteniendo el contexto de Son1kVers3
- Si no sabes algo, admítelo y ofrece alternativas

Recuerda: Eres parte de una comunidad de músicos digitales que creen en el poder democratizador de la IA para la creación artística."""

    async def chat(self, message: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Procesar mensaje del usuario y generar respuesta"""
        try:
            # Preparar historial de conversación
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Agregar historial si existe
            if history:
                messages.extend(history[-10:])  # Últimos 10 mensajes para contexto
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": message})
            
            # Llamar a Ollama
            response = await self._call_ollama(messages)
            
            return {
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en Pixel Assistant: {e}")
            return {
                "success": True,
                "response": f"¡Hola! Soy Pixel, tu asistente de IA. Estoy aquí para ayudarte con la generación musical y cualquier pregunta que tengas sobre Son1kVers3. ¿En qué puedo ayudarte hoy?",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _call_ollama(self, messages: List[Dict[str, str]]) -> str:
        """Llamar a la API de Ollama"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 500
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("message", {}).get("content", "No pude generar una respuesta.")
                else:
                    logger.error(f"Error en Ollama: {response.status_code} - {response.text}")
                    return "Lo siento, el sistema de IA no está disponible en este momento."
                    
        except Exception as e:
            if "timeout" in str(e).lower():
                logger.error("Timeout en llamada a Ollama")
                return "El sistema está procesando tu mensaje, pero está tardando más de lo esperado. Por favor, inténtalo de nuevo."
            elif "connect" in str(e).lower():
                logger.error("No se pudo conectar con Ollama")
                return "El sistema de IA no está disponible. Por favor, verifica que Ollama esté ejecutándose."
            else:
                logger.error(f"Error inesperado en Ollama: {e}")
                return "Hubo un error inesperado. Por favor, inténtalo de nuevo más tarde."
    
    async def get_quick_tips(self) -> List[str]:
        """Obtener consejos rápidos para el usuario"""
        tips = [
            "💡 Prueba describir el mood de tu música: 'una canción melancólica de piano'",
            "🎵 Usa palabras específicas: 'rock alternativo con guitarra distorsionada'",
            "🌟 Incluye emociones: 'una balada romántica con violines'",
            "🎶 Menciona el tempo: 'una canción rápida y energética'",
            "🎤 Especifica voces: 'con coros femeninos y sintetizadores'",
            "🎸 Combina géneros: 'jazz fusion con elementos electrónicos'",
            "🎹 Describe la estructura: 'intro suave, estrofa intensa, coro épico'",
            "🎺 Incluye instrumentos específicos: 'saxofón, batería y bajo'"
        ]
        return tips
    
    async def get_help_topics(self) -> Dict[str, str]:
        """Obtener temas de ayuda disponibles"""
        return {
            "generación": "Cómo generar música con Son1kVers3",
            "ghost_studio": "Herramientas del Ghost Studio",
            "archivo": "Navegando el Archivo de la Resistencia",
            "nexus": "Modo inmersivo NEXUS",
            "ollama": "Configuración de Ollama",
            "suno": "Integración con Suno AI",
            "creatividad": "Consejos de creatividad musical",
            "técnico": "Soporte técnico"
        }

# Instancia global
pixel_assistant = PixelAssistant()

async def chat_with_pixel(message: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """Función principal para chatear con Pixel"""
    return await pixel_assistant.chat(message, history)

async def get_pixel_tips() -> List[str]:
    """Obtener consejos de Pixel"""
    return await pixel_assistant.get_quick_tips()

async def get_pixel_help() -> Dict[str, str]:
    """Obtener temas de ayuda de Pixel"""
    return await pixel_assistant.get_help_topics()
