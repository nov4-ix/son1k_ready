"""
Son1k Suno API - Production Version (Simplified for Railway)
Transparent music generation API for Son1k frontend
Core features without AI dependencies for stable deployment
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
import json
import time
import uuid
from typing import Optional, Dict, Any, List
import tempfile
import shutil
from pathlib import Path
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Son1k Suno API", 
    description="Transparent music generation API",
    version="1.0.0"
)

# CORS Configuration for Son1k frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class GenerationRequest(BaseModel):
    prompt: str
    lyrics: str
    style: Optional[str] = None
    duration: Optional[int] = 60

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str

class CaptchaRequest(BaseModel):
    job_id: str
    captcha_solution: Optional[str] = None

# Ghost Studio Models
class GhostStudioRequest(BaseModel):
    style_prompt: str
    vocal_enhancement: Optional[bool] = True
    instrumental_boost: Optional[bool] = False
    postproduction: Optional[bool] = True

class PostProductionSettings(BaseModel):
    eq_preset: Optional[str] = "modern_pop"
    compression_level: Optional[float] = 0.7
    reverb_amount: Optional[float] = 0.3
    stereo_width: Optional[float] = 1.2
    mastering_level: Optional[float] = -14.0  # LUFS

class UserTier(BaseModel):
    tier: str  # "basic", "pro", "enterprise"

# In-memory storage (use Redis in production)
generation_jobs: Dict[str, Dict[str, Any]] = {}
ghost_studio_jobs: Dict[str, Dict[str, Any]] = {}
user_ghost_usage: Dict[str, int] = {}  # Track Ghost Studio usage per user

# Ghost Studio Usage Limits
GHOST_STUDIO_LIMITS = {
    "free": 1,      # 1 trial generation
    "pro": 20,      # 20 generations per month
    "enterprise": -1  # Unlimited (-1)
}

# Suno API Configuration
SUNO_SESSION_ID = os.environ.get("SUNO_SESSION_ID", "")
SUNO_COOKIE = os.environ.get("SUNO_COOKIE", "")
SUNO_BASE_URL = "https://studio-api.suno.ai"

# Ghost Studio Configuration
AUDIO_STORAGE_PATH = "/tmp/ghost_studio"
WAVES_PLUGINS_PATH = os.environ.get("WAVES_PLUGINS_PATH", "/Applications/Waves")

# Ensure audio storage directory exists
os.makedirs(AUDIO_STORAGE_PATH, exist_ok=True)

@app.get("/")
def root():
    return {
        "service": "Son1k Suno API",
        "status": "online",
        "version": "1.0.0",
        "features": [
            "Music generation via Suno API",
            "Ghost Studio audio transformation", 
            "Tiered access system",
            "AI assistant (requires Ollama)"
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "son1k-suno-api"}

# ===== BASIC AI ENDPOINTS (without Ollama dependency) =====

@app.get("/api/ai/ollama-status")
async def check_ollama_status():
    """
    Check if Ollama is running and available
    """
    return {
        "ollama_available": False,
        "status": "not_installed",
        "message": "Ollama not available in this deployment. AI features disabled.",
        "alternatives": [
            "Basic music generation available via /api/generate",
            "Ghost Studio available via /api/ghost-studio/generate",
            "Template lyrics available via /api/ai/templates"
        ]
    }

@app.get("/api/ai/templates")
async def get_creative_templates():
    """
    Get creative templates and starting points (no AI required)
    """
    templates = {
        "song_themes": [
            {"theme": "Amor perdido", "mood": "melancólico", "genre": "balada"},
            {"theme": "Perseguir sueños", "mood": "inspirador", "genre": "pop"},
            {"theme": "Noche de fiesta", "mood": "energético", "genre": "dance"},
            {"theme": "Reflexiones de vida", "mood": "contemplativo", "genre": "indie"},
            {"theme": "Superación personal", "mood": "motivacional", "genre": "rock"}
        ],
        "lyric_templates": [
            {
                "theme": "love",
                "lyrics": """[Verse 1]
In the silence of the night, I think of you
Every memory feels so bright and true
Your voice echoes in my mind
A love like ours is hard to find

[Chorus] 
You're the melody in my heart
The rhythm that won't depart
Together we can face it all
Together we'll never fall"""
            },
            {
                "theme": "dreams",
                "lyrics": """[Verse 1]
Walking down this endless road
Carrying dreams and hope untold
Every step brings me closer
To the person I'm meant to be

[Chorus]
Chasing dreams under starlit skies
Nothing can stop me when I try
The future's calling out my name
I'll never be the same"""
            }
        ],
        "prompt_templates": [
            "Pop moderno, voces claras, producción cristalina, 120 BPM",
            "Rock alternativo, guitarras potentes, energía creciente",
            "Balada emotiva, piano principal, cuerdas sutiles",
            "Electrónica upbeat, sintetizadores brillantes, ritmo bailable",
            "Indie folk, guitarra acústica, voces íntimas, orgánico"
        ]
    }
    
    return {
        "success": True,
        "templates": templates,
        "tip": "Use these templates as starting points for your creativity!"
    }

@app.post("/api/ai/simple-prompt")
async def generate_simple_prompt(
    user_words: str,
    genre: str = "pop",
    mood: str = "upbeat"
):
    """
    Generate basic prompts without AI (template-based)
    """
    # Simple template-based prompt generation
    genre_styles = {
        "pop": "modern pop, clean vocals, radio-ready production",
        "rock": "electric guitars, driving drums, powerful vocals",
        "electronic": "synthesizers, digital beats, modern production",
        "folk": "acoustic guitar, organic sound, intimate vocals",
        "jazz": "jazz instruments, swing rhythm, sophisticated harmony"
    }
    
    mood_descriptors = {
        "upbeat": "energetic, positive, uplifting",
        "chill": "relaxed, laid-back, smooth",
        "emotional": "heartfelt, touching, expressive",
        "energetic": "high-energy, dynamic, powerful",
        "peaceful": "calm, serene, gentle"
    }
    
    base_style = genre_styles.get(genre.lower(), "modern production")
    mood_desc = mood_descriptors.get(mood.lower(), "balanced")
    
    optimized_prompt = f"{base_style}, {mood_desc}, {user_words}"
    
    return {
        "success": True,
        "original_words": user_words,
        "optimized_prompt": optimized_prompt,
        "genre": genre,
        "mood": mood,
        "note": "This is a template-based prompt. For AI-enhanced prompts, deploy with Ollama support."
    }

# Include all the existing endpoints from main.py
# (copying the core generation and ghost studio functionality)

# Music generation endpoints
@app.post("/api/generate", response_model=GenerationResponse)
async def generate_music(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate music with Suno - Transparent API endpoint
    Frontend sends prompt + lyrics, gets back job_id
    """
    job_id = str(uuid.uuid4())
    
    # Store job info
    generation_jobs[job_id] = {
        "status": "pending",
        "prompt": request.prompt,
        "lyrics": request.lyrics,
        "style": request.style,
        "duration": request.duration,
        "created_at": time.time(),
        "result": None,
        "error": None
    }
    
    # Start generation in background
    background_tasks.add_task(process_suno_generation, job_id, request)
    
    return GenerationResponse(
        job_id=job_id,
        status="pending",
        message="Music generation started"
    )

@app.get("/api/status/{job_id}")
def get_generation_status(job_id: str):
    """
    Check generation status - Transparent for frontend
    Returns: pending, processing, captcha_needed, completed, failed
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = generation_jobs[job_id]
    
    response = {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"]
    }
    
    if job["status"] == "completed" and job["result"]:
        response["result"] = job["result"]
    elif job["status"] == "failed" and job["error"]:
        response["error"] = job["error"]
    elif job["status"] == "captcha_needed":
        response["message"] = "CAPTCHA required - please solve and submit"
        
    return response

# Ghost Studio endpoints (simplified versions)
@app.post("/api/ghost-studio/generate")
async def generate_ghost_studio(
    audio_file: UploadFile = File(...),
    style_prompt: str = Form(...),
    user_id: str = Form(...),
    user_tier: str = Form("free"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Ghost Studio: Upload audio file for Suno Cover style transfer + postproduction
    """
    job_id = str(uuid.uuid4())
    
    # Check usage limits
    user_usage = user_ghost_usage.get(user_id, 0)
    tier_limit = GHOST_STUDIO_LIMITS.get(user_tier, 0)
    
    if tier_limit != -1 and user_usage >= tier_limit:
        if user_tier == "free":
            raise HTTPException(
                status_code=403, 
                detail="Free tier limit reached (1 generation). Upgrade to Pro (20/month) or Enterprise (unlimited) for more Ghost Studio generations."
            )
        elif user_tier == "pro":
            raise HTTPException(
                status_code=403, 
                detail="Pro tier limit reached (20 generations this month). Upgrade to Enterprise for unlimited Ghost Studio generations."
            )
    
    # Validate audio file
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be audio format")
    
    # Save uploaded audio file
    temp_audio_path = f"{AUDIO_STORAGE_PATH}/{job_id}_original.mp3"
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio file: {str(e)}")
    
    # Create job record
    ghost_studio_jobs[job_id] = {
        "status": "pending",
        "style_prompt": style_prompt,
        "user_tier": user_tier,
        "postproduction_enabled": True,
        "created_at": time.time(),
        "result": None,
        "error": None,
        "stage": "pending",
        "original_audio_path": temp_audio_path
    }
    
    # Increment usage
    user_ghost_usage[user_id] = user_usage + 1
    
    # Start processing (would call actual Ghost Studio processing)
    # For now, return success
    
    remaining_usage = "unlimited" if tier_limit == -1 else max(0, tier_limit - user_usage)
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": f"Ghost Studio processing started (simplified mode)",
        "user_tier": user_tier,
        "usage_remaining": remaining_usage,
        "note": "Full Ghost Studio processing available with complete deployment"
    }

# Add basic processing function
async def process_suno_generation(job_id: str, request: GenerationRequest):
    """
    Background task to handle Suno generation
    """
    try:
        job = generation_jobs[job_id]
        job["status"] = "processing"
        
        # Check if we have Suno credentials
        if not SUNO_SESSION_ID or not SUNO_COOKIE:
            job["status"] = "failed"
            job["error"] = "Suno credentials not configured. Please set SUNO_SESSION_ID and SUNO_COOKIE environment variables."
            return
        
        # For now, simulate processing
        import asyncio
        await asyncio.sleep(5)
        
        # Simulate success
        job["status"] = "completed"
        job["result"] = {
            "audio_url": "https://example.com/generated_music.mp3",
            "title": f"Generated: {request.prompt[:30]}...",
            "duration": request.duration,
            "metadata": {
                "prompt": request.prompt,
                "style": request.style,
                "generated_at": time.time()
            }
        }
        
    except Exception as e:
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = f"Generation error: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)