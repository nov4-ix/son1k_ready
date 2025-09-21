"""
Ollama Creative Assistant - Son1k Music Generation AI
Advanced lyrics and prompt generation using local Ollama models
"""
import requests
import json
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class LyricsRequest(BaseModel):
    theme: str
    mood: str = "upbeat"
    genre: str = "pop"
    language: str = "en"
    structure: str = "verse-chorus-verse-chorus-bridge-chorus"
    max_lines: int = 20

class PromptRequest(BaseModel):
    user_words: str
    desired_mood: str = "energetic"
    target_genre: str = "auto"  # auto-detect or specify
    duration: int = 60

class SongMetadataRequest(BaseModel):
    lyrics: str
    style_prompt: str

class LyricsResponse(BaseModel):
    lyrics: str
    structure: List[str]
    rhyme_scheme: str
    suggested_melody_notes: str
    coherence_score: float

class PromptResponse(BaseModel):
    optimized_prompt: str
    detected_genre: str
    style_tags: List[str]
    mood_analysis: str
    suggested_bpm: str

class OllamaCreativeAssistant:
    def __init__(self, ollama_url: str = None, model: str = "llama3.1:8b"):
        # Try multiple Ollama URLs (local, external, cloud)
        possible_urls = [
            os.environ.get("OLLAMA_URL"),
            "https://bcea9a8ab0da.ngrok-free.app",  # Current ngrok tunnel
            "http://localhost:11434",
            "http://127.0.0.1:11434"
        ]
        
        self.ollama_url = None
        for url in possible_urls:
            if url and self._test_connection(url):
                self.ollama_url = url
                break
        
        if not self.ollama_url:
            self.ollama_url = ollama_url or "http://localhost:11434"
            
        self.model = model
        self.available = self._test_connection(self.ollama_url)
    
    def _test_connection(self, url):
        """Test if Ollama is available at given URL"""
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
        
    def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Make request to Ollama instance"""
        if not self.available:
            return f"AI assistant not available. Please check Ollama installation at {self.ollama_url}"
            
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return ""
    
    def generate_coherent_lyrics(self, request: LyricsRequest) -> LyricsResponse:
        """Generate coherent, structured lyrics with proper rhyme schemes"""
        
        system_prompt = f"""You are a professional songwriter specializing in {request.genre} music. 
        Create lyrics that are:
        - Emotionally coherent and tell a story
        - Follow proper rhyme schemes (AABB, ABAB, or ABCB)
        - Match the {request.mood} mood perfectly
        - Are radio-friendly and memorable
        - Follow the structure: {request.structure}
        - Maximum {request.max_lines} lines total
        
        Format your response as:
        [VERSE 1]
        lyrics here...
        
        [CHORUS]
        lyrics here...
        
        etc."""
        
        prompt = f"""Create {request.language} lyrics about: {request.theme}
        
        Mood: {request.mood}
        Genre: {request.genre}
        Structure: {request.structure}
        
        Make it catchy, emotionally resonant, and suitable for {request.genre} music."""
        
        lyrics_text = self._call_ollama(prompt, system_prompt)
        
        # Analyze the generated lyrics
        structure_analysis = self._analyze_song_structure(lyrics_text)
        rhyme_scheme = self._detect_rhyme_scheme(lyrics_text)
        coherence_score = self._calculate_coherence_score(lyrics_text)
        melody_notes = self._suggest_melody_notes(request.mood, request.genre)
        
        return LyricsResponse(
            lyrics=lyrics_text,
            structure=structure_analysis,
            rhyme_scheme=rhyme_scheme,
            suggested_melody_notes=melody_notes,
            coherence_score=coherence_score
        )
    
    def generate_smart_prompt(self, request: PromptRequest) -> PromptResponse:
        """Convert user words into professional Suno prompts"""
        
        system_prompt = """You are a music production expert who creates professional Suno AI prompts.
        Convert user's basic words into detailed, professional music generation prompts.
        
        Your prompts should include:
        - Specific instruments and sounds
        - Production style and mixing details
        - BPM and rhythm information
        - Musical key and progression hints
        - Atmospheric and mood descriptors
        
        Output format:
        PROMPT: [detailed professional prompt]
        GENRE: [detected/refined genre]
        TAGS: [comma-separated style tags]
        MOOD: [detailed mood analysis]
        BPM: [suggested BPM range]"""
        
        prompt = f"""Convert these user words into a professional Suno prompt:
        
        User words: "{request.user_words}"
        Desired mood: {request.desired_mood}
        Target genre: {request.target_genre}
        Duration: {request.duration} seconds
        
        Create a detailed, professional prompt that will generate high-quality music."""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Parse the structured response
        parsed = self._parse_prompt_response(response)
        
        return PromptResponse(
            optimized_prompt=parsed.get("prompt", request.user_words),
            detected_genre=parsed.get("genre", request.target_genre),
            style_tags=parsed.get("tags", []),
            mood_analysis=parsed.get("mood", request.desired_mood),
            suggested_bpm=parsed.get("bpm", "120-130")
        )
    
    def generate_song_metadata(self, request: SongMetadataRequest) -> Dict[str, Any]:
        """Generate metadata, titles, and descriptions for songs"""
        
        system_prompt = """You are a music industry expert who creates compelling song metadata.
        Analyze lyrics and style to create professional metadata.
        
        Output format:
        TITLE: [catchy, memorable song title]
        DESCRIPTION: [engaging description for listeners]
        TAGS: [genre, mood, instrument tags]
        TARGET_AUDIENCE: [who would love this song]
        PLAYLIST_FIT: [what playlists this belongs in]
        MARKETING_ANGLE: [how to promote this song]"""
        
        prompt = f"""Create metadata for this song:
        
        LYRICS:
        {request.lyrics[:500]}...
        
        STYLE: {request.style_prompt}
        
        Generate professional, marketable metadata."""
        
        response = self._call_ollama(prompt, system_prompt)
        return self._parse_metadata_response(response)
    
    def suggest_song_structure(self, theme: str, genre: str, duration: int = 180) -> Dict[str, Any]:
        """Suggest optimal song structure based on genre and theme"""
        
        system_prompt = f"""You are a music composition expert. Suggest optimal song structures 
        for {genre} music that effectively tells a story about the given theme.
        
        Consider:
        - Standard {genre} song structures
        - Emotional arc and storytelling
        - Radio-friendly formats
        - Target duration of {duration} seconds
        
        Output format:
        STRUCTURE: [detailed structure breakdown]
        TIMING: [time breakdown for each section]
        TIPS: [composition tips for this structure]"""
        
        prompt = f"""Suggest the best song structure for:
        
        Theme: {theme}
        Genre: {genre}
        Duration: {duration} seconds
        
        Include timing estimates and composition advice."""
        
        response = self._call_ollama(prompt, system_prompt)
        return self._parse_structure_response(response)
    
    def recommend_style_improvements(self, current_prompt: str, target_quality: str = "professional") -> Dict[str, Any]:
        """Suggest improvements to make prompts more effective"""
        
        system_prompt = f"""You are a Suno AI prompt optimization expert. 
        Analyze prompts and suggest improvements for {target_quality} quality output.
        
        Consider:
        - Specific instrument mentions
        - Production quality descriptors
        - Genre-appropriate terminology
        - Mixing and mastering hints
        
        Output format:
        IMPROVED_PROMPT: [enhanced version]
        CHANGES_MADE: [list of improvements]
        REASONING: [why these changes help]
        QUALITY_SCORE: [1-10 rating]"""
        
        prompt = f"""Improve this Suno prompt for {target_quality} results:
        
        CURRENT PROMPT: "{current_prompt}"
        
        Make it more specific, professional, and likely to generate high-quality music."""
        
        response = self._call_ollama(prompt, system_prompt)
        return self._parse_improvement_response(response)
    
    def enhance_existing_lyrics(self, lyrics: str, improvements: List[str]) -> str:
        """Improve existing lyrics for better flow, coherence, and impact"""
        
        system_prompt = """You are a professional lyricist and editor. 
        Enhance lyrics while preserving the original meaning and emotional impact.
        
        Focus on:
        - Better rhyme schemes and flow
        - Stronger emotional impact
        - Improved coherence and storytelling
        - More memorable hooks and phrases"""
        
        improvements_text = ", ".join(improvements)
        
        prompt = f"""Enhance these lyrics with focus on: {improvements_text}
        
        ORIGINAL LYRICS:
        {lyrics}
        
        Preserve the core message but make them more impactful and professional."""
        
        return self._call_ollama(prompt, system_prompt)
    
    # Helper methods for analysis
    def _analyze_song_structure(self, lyrics: str) -> List[str]:
        """Analyze the structure of generated lyrics"""
        sections = []
        lines = lyrics.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                sections.append(line.replace('[', '').replace(']', '').title())
        
        return sections if sections else ["Verse", "Chorus", "Verse", "Chorus"]
    
    def _detect_rhyme_scheme(self, lyrics: str) -> str:
        """Detect rhyme scheme pattern in lyrics"""
        # Simplified rhyme detection - can be enhanced
        lines = [line.strip() for line in lyrics.split('\n') if line.strip() and not line.startswith('[')]
        
        if len(lines) >= 4:
            return "ABAB"  # Default assumption
        return "AABB"
    
    def _calculate_coherence_score(self, lyrics: str) -> float:
        """Calculate coherence score based on repetition, structure, etc."""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        # Simple coherence metrics
        word_count = len(lyrics.split())
        unique_words = len(set(lyrics.lower().split()))
        
        # More unique words = more coherent (up to a point)
        coherence = min(unique_words / word_count * 2, 1.0) if word_count > 0 else 0.5
        
        return round(coherence, 2)
    
    def _suggest_melody_notes(self, mood: str, genre: str) -> str:
        """Suggest melody note patterns based on mood and genre"""
        melody_patterns = {
            "upbeat": "C-E-G-E, F-A-C-A",
            "sad": "Am-F-C-G, Dm-Bb-F-C",
            "energetic": "D-F#-A-F#, G-B-D-B",
            "chill": "Em-G-C-Am, F-Am-Dm-G"
        }
        
        return melody_patterns.get(mood.lower(), "C-E-G-C, F-A-C-F")
    
    def _parse_prompt_response(self, response: str) -> Dict[str, Any]:
        """Parse structured prompt response"""
        parsed = {}
        
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == "prompt":
                    parsed["prompt"] = value
                elif key == "genre":
                    parsed["genre"] = value
                elif key == "tags":
                    parsed["tags"] = [tag.strip() for tag in value.split(',')]
                elif key == "mood":
                    parsed["mood"] = value
                elif key == "bpm":
                    parsed["bpm"] = value
        
        return parsed
    
    def _parse_metadata_response(self, response: str) -> Dict[str, Any]:
        """Parse metadata response"""
        parsed = {}
        
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace('_', ' ')
                value = value.strip()
                parsed[key] = value
        
        return parsed
    
    def _parse_structure_response(self, response: str) -> Dict[str, Any]:
        """Parse structure suggestion response"""
        return self._parse_metadata_response(response)  # Same format
    
    def _parse_improvement_response(self, response: str) -> Dict[str, Any]:
        """Parse improvement suggestion response"""
        return self._parse_metadata_response(response)  # Same format

# Global instance
ollama_assistant = OllamaCreativeAssistant()