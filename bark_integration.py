# Bark Voice Cloning Integration for Son1kVers3
# Bark is better than XTTR for voice cloning - more natural, better quality

import asyncio
import httpx
import os
import uuid
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BarkVoiceCloning:
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.model_id = "suno/bark"
        self.base_url = "https://api-inference.huggingface.co/models"
        
    async def clone_voice(self, 
                         audio_file: bytes, 
                         text: str, 
                         voice_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Clone voice using Bark model
        
        Args:
            audio_file: Audio file bytes (reference voice)
            text: Text to be spoken
            voice_settings: Voice quality and style settings
            
        Returns:
            Dict with audio_url, duration, quality info
        """
        
        try:
            # Prepare voice settings
            settings = voice_settings or {}
            quality = settings.get('quality', 'high')
            duration = settings.get('duration', 60)
            
            # Prepare request payload
            payload = {
                "inputs": text,
                "parameters": {
                    "voice_preset": "v2/en_speaker_6",  # Default voice preset
                    "max_length": min(duration * 25, 1000),  # Bark uses ~25 tokens per second
                    "temperature": 0.6,
                    "repetition_penalty": 1.2,
                    "length_penalty": 1.0,
                    "do_sample": True,
                    "early_stopping": True
                }
            }
            
            # Add voice cloning if audio file provided
            if audio_file:
                # For voice cloning, we need to use Bark's voice cloning capabilities
                # This requires additional processing
                payload["voice_cloning"] = {
                    "reference_audio": audio_file,
                    "voice_style": settings.get('voice_style', 'neutral')
                }
            
            # Make request to Hugging Face
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/{self.model_id}",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Bark API error: {response.status_code} - {response.text}")
                
                # Save generated audio
                audio_data = response.content
                audio_id = str(uuid.uuid4())
                audio_path = f"results/bark_{audio_id}.wav"
                
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                with open(audio_path, "wb") as f:
                    f.write(audio_data)
                
                return {
                    "success": True,
                    "audio_url": f"/api/audio/bark_{audio_id}",
                    "duration": self.estimate_duration(text),
                    "quality": quality,
                    "model": "Bark",
                    "provider": "huggingface",
                    "cost": 0.0
                }
                
        except Exception as e:
            logger.error(f"Bark voice cloning failed: {str(e)}")
            raise Exception(f"Bark voice cloning failed: {str(e)}")
    
    def estimate_duration(self, text: str) -> float:
        """Estimate audio duration based on text length"""
        # Bark typically generates ~25 tokens per second
        # Average word length is ~5 characters
        words = len(text.split())
        estimated_seconds = words * 0.4  # ~2.5 words per second
        return min(estimated_seconds, 60)  # Cap at 60 seconds for free tier
    
    async def get_voice_presets(self) -> Dict[str, Any]:
        """Get available voice presets for Bark"""
        return {
            "presets": [
                {
                    "id": "v2/en_speaker_0",
                    "name": "Male Voice 1",
                    "gender": "male",
                    "accent": "american"
                },
                {
                    "id": "v2/en_speaker_1", 
                    "name": "Female Voice 1",
                    "gender": "female",
                    "accent": "american"
                },
                {
                    "id": "v2/en_speaker_2",
                    "name": "Male Voice 2", 
                    "gender": "male",
                    "accent": "british"
                },
                {
                    "id": "v2/en_speaker_3",
                    "name": "Female Voice 2",
                    "gender": "female", 
                    "accent": "british"
                },
                {
                    "id": "v2/en_speaker_4",
                    "name": "Male Voice 3",
                    "gender": "male",
                    "accent": "australian"
                },
                {
                    "id": "v2/en_speaker_5",
                    "name": "Female Voice 3",
                    "gender": "female",
                    "accent": "australian"
                },
                {
                    "id": "v2/en_speaker_6",
                    "name": "Neutral Voice",
                    "gender": "neutral",
                    "accent": "international"
                }
            ],
            "languages": [
                {"code": "en", "name": "English"},
                {"code": "es", "name": "Spanish"},
                {"code": "fr", "name": "French"},
                {"code": "de", "name": "German"},
                {"code": "it", "name": "Italian"},
                {"code": "pt", "name": "Portuguese"},
                {"code": "ru", "name": "Russian"},
                {"code": "ja", "name": "Japanese"},
                {"code": "ko", "name": "Korean"},
                {"code": "zh", "name": "Chinese"}
            ],
            "emotions": [
                "neutral", "happy", "sad", "angry", "fearful", 
                "disgusted", "surprised", "excited", "calm", "energetic"
            ]
        }
    
    async def clone_voice_with_emotion(self, 
                                     audio_file: bytes,
                                     text: str,
                                     emotion: str = "neutral",
                                     voice_preset: str = "v2/en_speaker_6") -> Dict[str, Any]:
        """Clone voice with specific emotion"""
        
        # Add emotion to text using Bark's emotion markers
        emotion_markers = {
            "happy": "[laughs] ",
            "sad": "[sighs] ",
            "angry": "[angry] ",
            "excited": "[excited] ",
            "whisper": "[whispers] ",
            "shout": "[shouts] ",
            "sing": "[sings] ",
            "cry": "[cries] "
        }
        
        if emotion in emotion_markers:
            text = emotion_markers[emotion] + text
        
        # Add emotion-specific parameters
        voice_settings = {
            "quality": "high",
            "emotion": emotion,
            "voice_preset": voice_preset,
            "temperature": 0.7 if emotion in ["excited", "angry"] else 0.6
        }
        
        return await self.clone_voice(audio_file, text, voice_settings)
    
    async def batch_clone_voices(self, 
                                requests: list) -> list:
        """Process multiple voice cloning requests"""
        
        results = []
        for request in requests:
            try:
                result = await self.clone_voice(
                    request.get("audio_file"),
                    request.get("text"),
                    request.get("voice_settings", {})
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e)
                })
        
        return results

# Usage example
async def main():
    bark = BarkVoiceCloning()
    
    # Example voice cloning
    with open("sample_voice.wav", "rb") as f:
        audio_data = f.read()
    
    result = await bark.clone_voice(
        audio_data,
        "Hello, this is a test of Bark voice cloning!",
        {
            "quality": "high",
            "emotion": "happy",
            "voice_preset": "v2/en_speaker_6"
        }
    )
    
    print(f"Generated audio: {result['audio_url']}")
    print(f"Duration: {result['duration']} seconds")

if __name__ == "__main__":
    asyncio.run(main())
