"""
Interactive Music Creation Assistant - Son1k
AI-powered conversational assistant that guides users through music creation
"""
import json
import time
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from ollama_creative_assistant import ollama_assistant
import logging

logger = logging.getLogger(__name__)

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None

class CreativeSession(BaseModel):
    session_id: str
    user_id: str
    conversation: List[ConversationMessage] = []
    current_step: str = "intro"
    project_data: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}
    created_at: float
    last_activity: float

class InteractiveMusicAssistant:
    def __init__(self):
        self.active_sessions: Dict[str, CreativeSession] = {}
        self.conversation_flows = self._init_conversation_flows()
        
    def _init_conversation_flows(self) -> Dict[str, Any]:
        """Initialize conversation flow templates"""
        return {
            "intro": {
                "message": "¡Hola! 🎵 Soy tu asistente musical de Son1k. Te ayudaré a crear música increíble paso a paso. ¿Qué tipo de canción quieres crear hoy?",
                "options": [
                    "🎤 Una canción con letras originales",
                    "🎵 Música instrumental",
                    "🎭 Transformar una canción existente (Ghost Studio)",
                    "💡 No estoy seguro, necesito inspiración"
                ],
                "next_steps": {
                    "lyrics": "lyrics_theme",
                    "instrumental": "instrumental_style", 
                    "ghost": "ghost_upload",
                    "inspiration": "creative_brainstorm"
                }
            },
            
            "lyrics_theme": {
                "message": "Perfecto! 📝 Vamos a crear letras únicas. ¿Sobre qué quieres que trate tu canción?",
                "suggestions": [
                    "💕 Amor y relaciones",
                    "🌟 Perseguir sueños",
                    "🌧️ Superar dificultades",
                    "🎉 Celebrar la vida",
                    "🌙 Reflexiones nocturnas",
                    "✨ Algo completamente diferente"
                ],
                "follow_up": "¿Puedes contarme más sobre la historia o mensaje que quieres transmitir?"
            },
            
            "instrumental_style": {
                "message": "¡Excelente elección! 🎼 ¿Qué estilo instrumental tienes en mente?",
                "suggestions": [
                    "🎹 Piano melódico y emotivo",
                    "🎸 Guitarra acústica relajada",
                    "⚡ Electrónica energética",
                    "🎻 Orquestal y épico",
                    "🎺 Jazz con swing",
                    "🥁 Hip-hop con beats potentes"
                ],
                "follow_up": "¿Para qué ocasión o momento será esta música?"
            },
            
            "creative_brainstorm": {
                "message": "¡No te preocupes! 💭 Vamos a encontrar la inspiración perfecta. Te haré algunas preguntas:",
                "questions": [
                    "¿Cómo te sientes ahora mismo?",
                    "¿Qué tipo de música escuchas normalmente?",
                    "¿Hay alguna canción que te inspire últimamente?",
                    "¿Prefieres música para bailar, relajarte o reflexionar?"
                ]
            }
        }
    
    def start_session(self, user_id: str, session_id: str = None) -> CreativeSession:
        """Start a new interactive creative session"""
        if not session_id:
            session_id = f"session_{user_id}_{int(time.time())}"
        
        session = CreativeSession(
            session_id=session_id,
            user_id=user_id,
            created_at=time.time(),
            last_activity=time.time()
        )
        
        # Add welcome message
        intro_flow = self.conversation_flows["intro"]
        welcome_msg = ConversationMessage(
            role="assistant",
            content=intro_flow["message"],
            timestamp=time.time(),
            metadata={
                "step": "intro",
                "options": intro_flow["options"],
                "type": "welcome"
            }
        )
        session.conversation.append(welcome_msg)
        
        self.active_sessions[session_id] = session
        return session
    
    def process_user_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Process user message and generate intelligent response"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        session.last_activity = time.time()
        
        # Add user message to conversation
        user_msg = ConversationMessage(
            role="user",
            content=user_message,
            timestamp=time.time()
        )
        session.conversation.append(user_msg)
        
        # Generate AI response based on current context
        response = self._generate_contextual_response(session, user_message)
        
        # Add assistant response to conversation
        assistant_msg = ConversationMessage(
            role="assistant",
            content=response["content"],
            timestamp=time.time(),
            metadata=response.get("metadata", {})
        )
        session.conversation.append(assistant_msg)
        
        return {
            "session_id": session_id,
            "response": response,
            "conversation_length": len(session.conversation),
            "current_step": session.current_step,
            "project_progress": self._calculate_progress(session)
        }
    
    def _generate_contextual_response(self, session: CreativeSession, user_message: str) -> Dict[str, Any]:
        """Generate intelligent contextual response using Ollama"""
        
        # Build context from conversation history
        context = self._build_conversation_context(session)
        
        # Determine what kind of help the user needs
        intent = self._analyze_user_intent(user_message, session.current_step)
        
        if intent == "theme_selection":
            return self._handle_theme_selection(session, user_message)
        elif intent == "lyrics_help":
            return self._handle_lyrics_assistance(session, user_message)
        elif intent == "prompt_help":
            return self._handle_prompt_assistance(session, user_message)
        elif intent == "creative_block":
            return self._handle_creative_block(session, user_message)
        elif intent == "technical_question":
            return self._handle_technical_question(session, user_message)
        elif intent == "next_step":
            return self._handle_next_step_guidance(session, user_message)
        else:
            return self._handle_general_conversation(session, user_message, context)
    
    def _handle_theme_selection(self, session: CreativeSession, user_message: str) -> Dict[str, Any]:
        """Handle theme selection and provide specific guidance"""
        
        # Extract theme and mood from user message
        system_prompt = """You are a music production assistant. Analyze the user's message to extract:
        1. Main theme/topic for their song
        2. Emotional mood they want
        3. Any specific details or stories they mention
        
        Respond with encouraging feedback and specific next steps for their theme."""
        
        analysis = ollama_assistant._call_ollama(
            f"User wants to create a song about: {user_message}\n\nProvide encouraging feedback and suggest specific next steps.",
            system_prompt
        )
        
        # Update session data
        session.project_data.update({
            "theme": user_message,
            "ai_analysis": analysis
        })
        session.current_step = "theme_development"
        
        return {
            "content": f"¡Me encanta esa idea! 🌟\n\n{analysis}\n\n¿Te gustaría que primero creemos las letras o prefieres que trabajemos en el estilo musical?",
            "metadata": {
                "step": "theme_development",
                "options": [
                    "📝 Crear letras primero",
                    "🎵 Definir estilo musical primero",
                    "💡 Necesito más ideas para desarrollar el tema"
                ],
                "type": "guidance"
            }
        }
    
    def _handle_lyrics_assistance(self, session: CreativeSession, user_message: str) -> Dict[str, Any]:
        """Provide lyrics writing assistance"""
        
        theme = session.project_data.get("theme", "general theme")
        
        # Generate lyrics suggestions
        lyrics_request = {
            "theme": theme,
            "mood": session.project_data.get("mood", "upbeat"),
            "genre": session.project_data.get("genre", "pop"),
            "user_input": user_message
        }
        
        system_prompt = f"""You are a professional songwriter helping create lyrics about: {theme}
        
        The user said: {user_message}
        
        Provide:
        1. Encouraging feedback on their input
        2. 2-3 specific lyric line suggestions
        3. Questions to help them develop the concept further
        4. Rhyme scheme suggestions
        
        Keep it conversational and supportive."""
        
        lyrics_help = ollama_assistant._call_ollama(
            f"Help with lyrics for theme: {theme}. User input: {user_message}",
            system_prompt
        )
        
        session.current_step = "lyrics_development"
        
        return {
            "content": lyrics_help,
            "metadata": {
                "step": "lyrics_development",
                "type": "lyrics_assistance",
                "suggestions": [
                    "📝 Generar letras completas con IA",
                    "🎭 Probar diferentes estilos de escritura", 
                    "✨ Mejorar las letras que ya tengo"
                ]
            }
        }
    
    def _handle_prompt_assistance(self, session: CreativeSession, user_message: str) -> Dict[str, Any]:
        """Help create better Suno prompts"""
        
        system_prompt = """You are a Suno AI prompt expert. Help the user create better prompts.
        
        Analyze their message and provide:
        1. An improved, professional prompt
        2. Explanation of improvements made
        3. Alternative style suggestions
        4. Technical tips for better results
        
        Be encouraging and educational."""
        
        prompt_help = ollama_assistant._call_ollama(
            f"Help improve this Suno prompt: {user_message}",
            system_prompt
        )
        
        return {
            "content": prompt_help,
            "metadata": {
                "type": "prompt_assistance",
                "actions": [
                    "🎯 Usar prompt mejorado",
                    "🔄 Probar variaciones",
                    "📊 Ver ejemplos de prompts exitosos"
                ]
            }
        }
    
    def _handle_creative_block(self, session: CreativeSession, user_message: str) -> Dict[str, Any]:
        """Help overcome creative blocks"""
        
        system_prompt = """You are a creative coach helping overcome writer's block.
        
        Provide:
        1. Understanding and empathy
        2. 3-5 specific creative exercises
        3. Inspiration sources
        4. Encouragement to keep going
        
        Be warm, supportive, and practical."""
        
        creative_help = ollama_assistant._call_ollama(
            f"User is experiencing creative block: {user_message}",
            system_prompt
        )
        
        return {
            "content": creative_help,
            "metadata": {
                "type": "creative_support",
                "exercises": [
                    "🎲 Generador de ideas aleatorias",
                    "🖼️ Inspiración visual para letras",
                    "🎵 Escuchar referencias musicales",
                    "📱 Tomar un descanso y volver"
                ]
            }
        }
    
    def _handle_next_step_guidance(self, session: CreativeSession, user_message: str) -> Dict[str, Any]:
        """Provide guidance on next steps in the creative process"""
        
        progress = self._calculate_progress(session)
        
        if progress < 25:
            next_step = "definir el concepto principal"
        elif progress < 50:
            next_step = "crear las letras o el prompt"
        elif progress < 75:
            next_step = "generar la música"
        else:
            next_step = "revisar y perfeccionar"
        
        return {
            "content": f"Basándome en tu progreso, el siguiente paso recomendado es: {next_step}\n\n¿Te gustaría que te ayude con esto?",
            "metadata": {
                "type": "guidance",
                "progress": progress,
                "next_step": next_step
            }
        }
    
    def _handle_general_conversation(self, session: CreativeSession, user_message: str, context: str) -> Dict[str, Any]:
        """Handle general conversation with context awareness"""
        
        system_prompt = f"""You are a friendly, knowledgeable music creation assistant for Son1k.
        
        Conversation context: {context}
        
        Respond naturally and helpfully. If appropriate, guide toward music creation activities.
        Be encouraging, creative, and supportive. Ask follow-up questions to understand their needs better.
        
        Remember: You're here to help them create amazing music!"""
        
        response = ollama_assistant._call_ollama(user_message, system_prompt)
        
        return {
            "content": response,
            "metadata": {
                "type": "conversation",
                "context_aware": True
            }
        }
    
    def _analyze_user_intent(self, message: str, current_step: str) -> str:
        """Analyze user intent from their message"""
        
        message_lower = message.lower()
        
        # Keywords for different intents
        theme_keywords = ["sobre", "tema", "canción", "historia", "mensaje"]
        lyrics_keywords = ["letras", "escribir", "rima", "verso", "coro"]
        prompt_keywords = ["prompt", "estilo", "género", "sonido", "producción"]
        creative_keywords = ["bloqueado", "inspiración", "ideas", "ayuda", "no sé"]
        technical_keywords = ["cómo", "funciona", "configurar", "opciones"]
        next_keywords = ["siguiente", "después", "ahora qué", "continuar"]
        
        if any(word in message_lower for word in theme_keywords) and current_step in ["intro", "theme_selection"]:
            return "theme_selection"
        elif any(word in message_lower for word in lyrics_keywords):
            return "lyrics_help"
        elif any(word in message_lower for word in prompt_keywords):
            return "prompt_help"
        elif any(word in message_lower for word in creative_keywords):
            return "creative_block"
        elif any(word in message_lower for word in technical_keywords):
            return "technical_question"
        elif any(word in message_lower for word in next_keywords):
            return "next_step"
        else:
            return "general_conversation"
    
    def _build_conversation_context(self, session: CreativeSession) -> str:
        """Build context from conversation history"""
        
        context_parts = []
        
        # Add project data
        if session.project_data:
            context_parts.append(f"Project: {json.dumps(session.project_data, indent=2)}")
        
        # Add recent conversation (last 5 messages)
        recent_messages = session.conversation[-5:] if len(session.conversation) > 5 else session.conversation
        for msg in recent_messages:
            context_parts.append(f"{msg.role}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def _calculate_progress(self, session: CreativeSession) -> float:
        """Calculate creative progress percentage"""
        
        progress = 0
        
        # Check project milestones
        if session.project_data.get("theme"):
            progress += 25
        if session.project_data.get("lyrics") or session.project_data.get("prompt"):
            progress += 25
        if session.project_data.get("genre") and session.project_data.get("mood"):
            progress += 25
        if session.project_data.get("generated_music"):
            progress += 25
        
        return progress
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of creative session"""
        
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "duration": time.time() - session.created_at,
            "messages_exchanged": len(session.conversation),
            "current_step": session.current_step,
            "progress": self._calculate_progress(session),
            "project_data": session.project_data,
            "last_activity": session.last_activity
        }
    
    def generate_project_recommendations(self, session_id: str) -> Dict[str, Any]:
        """Generate personalized recommendations based on session"""
        
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Generate recommendations using AI
        context = self._build_conversation_context(session)
        
        system_prompt = """Based on the user's creative session, provide personalized recommendations:
        
        1. Next steps they should take
        2. Style suggestions that would work well
        3. Creative exercises to try
        4. Technical tips for better results
        
        Be specific and actionable."""
        
        recommendations = ollama_assistant._call_ollama(
            f"Generate recommendations based on this creative session: {context}",
            system_prompt
        )
        
        return {
            "session_id": session_id,
            "recommendations": recommendations,
            "generated_at": time.time(),
            "based_on": {
                "messages": len(session.conversation),
                "progress": self._calculate_progress(session),
                "current_step": session.current_step
            }
        }

# Global instance
interactive_assistant = InteractiveMusicAssistant()