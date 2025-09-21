"""
Son1k Suno API - Production Version
Transparent music generation API for Son1k frontend
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
from typing import Optional, Dict, Any
import tempfile
import shutil
from pathlib import Path
import subprocess
import logging
# Import AI assistants with fallback handling
try:
    from ollama_creative_assistant import (
        ollama_assistant, 
        LyricsRequest, 
        PromptRequest, 
        SongMetadataRequest,
        LyricsResponse,
        PromptResponse
    )
    from interactive_music_assistant import interactive_assistant, ConversationMessage
    AI_AVAILABLE = True
    logger.info("✅ AI assistants loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ AI assistants not available: {e}")
    AI_AVAILABLE = False
    
    # Fallback classes for when AI is not available
    class LyricsRequest:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class PromptRequest:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class SongMetadataRequest:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

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
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "son1k-suno-api"}

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

@app.post("/api/captcha/{job_id}")
def submit_captcha(job_id: str, captcha: CaptchaRequest):
    """
    Submit CAPTCHA solution from frontend
    Resumes generation process
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = generation_jobs[job_id]
    
    if job["status"] != "captcha_needed":
        raise HTTPException(status_code=400, detail="CAPTCHA not required for this job")
    
    # Mark as processing and continue generation
    job["status"] = "processing"
    job["captcha_solution"] = captcha.captcha_solution
    
    return {"message": "CAPTCHA submitted, resuming generation"}

async def process_suno_generation(job_id: str, request: GenerationRequest):
    """
    Background task to handle Suno generation with real Suno API
    """
    try:
        job = generation_jobs[job_id]
        job["status"] = "processing"
        
        # Check if we have Suno credentials
        if not SUNO_SESSION_ID or not SUNO_COOKIE:
            job["status"] = "failed"
            job["error"] = "Suno credentials not configured. Please set SUNO_SESSION_ID and SUNO_COOKIE environment variables."
            return
        
        # Real Suno API integration  
        # Clean cookie string to remove invalid characters
        clean_cookie = SUNO_COOKIE.replace('\n', '').replace('\r', '').strip()
        
        headers = {
            "Cookie": clean_cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://suno.com",
            "Origin": "https://suno.com"
        }
        
        # Step 1: Create generation request (modern Suno format)
        generation_payload = {
            "gpt_description_prompt": request.prompt,
            "mv": "chirp-v3-5",
            "prompt": "",
            "make_instrumental": False,
            "wait_audio": False
        }
        
        # Add lyrics if provided (modern format)
        if request.lyrics:
            generation_payload["prompt"] = request.lyrics
            generation_payload["tags"] = request.style or "pop"
            generation_payload["gpt_description_prompt"] = request.prompt
        else:
            generation_payload["make_instrumental"] = True
            generation_payload["tags"] = f"{request.style or 'instrumental'}, {request.prompt}"
            generation_payload["prompt"] = "[Instrumental]"
        
        print(f"🎵 Starting Suno generation for job {job_id}")
        print(f"📝 Prompt: {request.prompt}")
        print(f"🎤 Lyrics: {request.lyrics[:100]}..." if request.lyrics else "🎼 Instrumental")
        
        # Make request to Suno API (try multiple modern endpoints)
        endpoints_to_try = [
            "https://studio-api.suno.ai/api/external_generate/",
            "https://studio-api.suno.ai/api/generate/v2/",
            "https://studio-api.suno.ai/api/generate/",
            "https://studio-api.suno.ai/api/custom_generate/",
            "https://clerk.suno.com/api/generate/",
            "https://suno.com/api/generate/",
            f"{SUNO_BASE_URL}/api/generate/v2/",
            f"{SUNO_BASE_URL}/api/generate/"
        ]
        
        response = None
        for endpoint in endpoints_to_try:
            try:
                print(f"🔄 Trying endpoint: {endpoint}")
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=generation_payload,
                    timeout=30
                )
                print(f"📡 Response status: {response.status_code}")
                
                if response.status_code not in [503, 404]:
                    break  # Found working endpoint
                    
            except Exception as e:
                print(f"❌ Endpoint {endpoint} failed: {e}")
                continue
        
        if response.status_code == 401:
            job["status"] = "failed"
            job["error"] = "Suno authentication failed. Please update your session credentials."
            return
        elif response.status_code == 429:
            job["status"] = "failed" 
            job["error"] = "Suno rate limit exceeded. Please try again later."
            return
        elif response.status_code != 200:
            job["status"] = "failed"
            job["error"] = f"Suno API error: {response.status_code} - {response.text}"
            return
        
        result = response.json()
        print(f"✅ Suno responded: {result}")
        
        # Extract song IDs from response
        if "clips" in result and len(result["clips"]) > 0:
            song_ids = [clip["id"] for clip in result["clips"]]
            job["suno_ids"] = song_ids
            job["status"] = "processing"
            
            # Start polling for completion
            await poll_suno_completion(job_id, song_ids)
        else:
            job["status"] = "failed"
            job["error"] = "No songs generated by Suno"
        
    except requests.exceptions.Timeout:
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = "Suno API timeout - please try again"
    except Exception as e:
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = f"Generation error: {str(e)}"
        print(f"❌ Error in Suno generation: {e}")

async def poll_suno_completion(job_id: str, song_ids: list):
    """
    Poll Suno API for song completion
    """
    import asyncio
    
    job = generation_jobs[job_id]
    max_attempts = 60  # 5 minutes max (5 second intervals)
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Check status of all songs
            clean_cookie = SUNO_COOKIE.replace('\n', '').replace('\r', '').strip()
            headers = {
                "Cookie": clean_cookie,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://suno.com"
            }
            
            # Get song details
            songs_data = []
            all_complete = True
            
            for song_id in song_ids:
                response = requests.get(
                    f"{SUNO_BASE_URL}/api/feed/{song_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    song_data = response.json()
                    songs_data.append(song_data)
                    
                    # Check if song is complete
                    if song_data.get("status") != "complete":
                        all_complete = False
                        
                    # Check for CAPTCHA requirement
                    if "captcha" in str(song_data).lower() or response.status_code == 403:
                        job["status"] = "captcha_needed"
                        return
                else:
                    all_complete = False
            
            # If all songs are complete, finalize the job
            if all_complete and songs_data:
                # Take the first completed song
                completed_song = songs_data[0]
                
                job["status"] = "completed"
                job["result"] = {
                    "audio_url": completed_song.get("audio_url"),
                    "video_url": completed_song.get("video_url"),
                    "title": completed_song.get("title", f"Generated: {job['prompt'][:30]}..."),
                    "duration": completed_song.get("duration", job.get("duration", 60)),
                    "metadata": {
                        "suno_id": completed_song.get("id"),
                        "prompt": job["prompt"],
                        "style": job.get("style"),
                        "generated_at": time.time(),
                        "model_name": completed_song.get("model_name", "chirp-v3-5")
                    }
                }
                
                print(f"🎉 Song generation completed for job {job_id}")
                print(f"🎵 Audio: {completed_song.get('audio_url')}")
                return
            
            # Wait before next check
            await asyncio.sleep(5)
            attempt += 1
            
            if attempt % 6 == 0:  # Every 30 seconds
                print(f"⏳ Still waiting for Suno generation... ({attempt*5}s)")
                
        except Exception as e:
            print(f"❌ Error polling Suno: {e}")
            await asyncio.sleep(5)
            attempt += 1
    
    # Timeout reached
    job["status"] = "failed"
    job["error"] = "Suno generation timeout - songs took too long to complete"
    print(f"⏰ Suno generation timeout for job {job_id}")

async def simulate_generation(job_id: str, request: GenerationRequest):
    """
    Simulate music generation for testing
    Remove this when Suno integration is complete
    """
    import asyncio
    
    job = generation_jobs[job_id]
    
    # Simulate processing time
    await asyncio.sleep(5)
    
    # Simulate different outcomes
    import random
    outcome = random.choice(["success", "captcha", "error"])
    
    if outcome == "success":
        job["status"] = "completed"
        job["result"] = {
            "audio_url": "https://example.com/generated_music.mp3",
            "video_url": "https://example.com/generated_video.mp4",
            "title": f"Generated: {request.prompt[:30]}...",
            "duration": request.duration,
            "metadata": {
                "prompt": request.prompt,
                "style": request.style,
                "generated_at": time.time()
            }
        }
    elif outcome == "captcha":
        job["status"] = "captcha_needed"
    else:
        job["status"] = "failed"
        job["error"] = "Simulated generation error"

@app.get("/api/jobs")
def list_jobs():
    """
    List all generation jobs (for debugging)
    """
    return {
        "total_jobs": len(generation_jobs),
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "prompt": job["prompt"][:50] + "..." if len(job["prompt"]) > 50 else job["prompt"],
                "created_at": job["created_at"]
            }
            for job_id, job in generation_jobs.items()
        ]
    }

# ===== GHOST STUDIO ENDPOINTS =====

@app.post("/api/ghost-studio/generate")
async def generate_ghost_studio(
    audio_file: UploadFile = File(...),
    style_prompt: str = Form(...),
    user_id: str = Form(...),  # Required to track usage
    user_tier: str = Form("free"),
    vocal_enhancement: bool = Form(True),
    instrumental_boost: bool = Form(False),
    eq_preset: str = Form("modern_pop"),
    compression_level: float = Form(0.7),
    reverb_amount: float = Form(0.3),
    stereo_width: float = Form(1.2),
    mastering_level: float = Form(-14.0),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Ghost Studio: Upload audio file for Suno Cover style transfer + postproduction
    - Free users: 1 trial generation with postproduction
    - Pro users: 20 generations per month with postproduction
    - Enterprise users: unlimited generations with postproduction
    """
    job_id = str(uuid.uuid4())
    
    # Check usage limits based on user tier
    user_usage = user_ghost_usage.get(user_id, 0)
    tier_limit = GHOST_STUDIO_LIMITS.get(user_tier, 0)
    
    # Check if user has exceeded their tier limit
    if tier_limit != -1 and user_usage >= tier_limit:  # -1 means unlimited (Enterprise)
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
        else:
            raise HTTPException(
                status_code=403, 
                detail="Usage limit reached for your tier. Please check your subscription."
            )
    
    # All tiers get postproduction (Free gets trial, Pro gets limited, Enterprise unlimited)
    postproduction_enabled = True
    
    # Increment usage counter
    user_ghost_usage[user_id] = user_usage + 1
    
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
        "postproduction_enabled": postproduction_enabled,
        "vocal_enhancement": vocal_enhancement,
        "instrumental_boost": instrumental_boost,
        "created_at": time.time(),
        "result": None,
        "error": None,
        "stage": "pending",
        "original_audio_path": temp_audio_path
    }
    
    # Create request objects
    ghost_request = GhostStudioRequest(
        style_prompt=style_prompt,
        vocal_enhancement=vocal_enhancement,
        instrumental_boost=instrumental_boost,
        postproduction=postproduction_enabled
    )
    
    postprod_settings = PostProductionSettings(
        eq_preset=eq_preset,
        compression_level=compression_level,
        reverb_amount=reverb_amount,
        stereo_width=stereo_width,
        mastering_level=mastering_level
    )
    
    # Start processing in background
    background_tasks.add_task(
        process_ghost_studio_generation, 
        job_id, 
        temp_audio_path, 
        ghost_request,
        postprod_settings
    )
    
    # Calculate remaining usage
    remaining_usage = "unlimited" if tier_limit == -1 else max(0, tier_limit - user_usage)
    
    # Create tier-specific message
    tier_messages = {
        "free": f" (FREE TRIAL - {remaining_usage} remaining)",
        "pro": f" (PRO - {remaining_usage}/20 remaining this month)",
        "enterprise": " (ENTERPRISE - unlimited access)"
    }
    tier_message = tier_messages.get(user_tier, "")
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": f"Ghost Studio processing started with postproduction{tier_message}",
        "postproduction_enabled": postproduction_enabled,
        "user_tier": user_tier,
        "usage_remaining": remaining_usage,
        "tier_limit": tier_limit if tier_limit != -1 else "unlimited"
    }

@app.get("/api/ghost-studio/status/{job_id}")
def get_ghost_studio_status(job_id: str):
    """
    Check Ghost Studio processing status
    """
    if job_id not in ghost_studio_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = ghost_studio_jobs[job_id]
    
    response = {
        "job_id": job_id,
        "status": job["status"],
        "stage": job.get("stage", "unknown"),
        "user_tier": job["user_tier"],
        "postproduction_enabled": job["postproduction_enabled"],
        "created_at": job["created_at"]
    }
    
    if job["status"] == "completed" and job["result"]:
        response["result"] = job["result"]
    elif job["status"] == "failed" and job["error"]:
        response["error"] = job["error"]
    elif job["status"] == "processing":
        response["message"] = f"Processing: {job.get('stage', 'unknown stage')}"
        
    return response

@app.get("/api/ghost-studio/download/{job_id}")
def download_ghost_studio_audio(job_id: str):
    """
    Download processed Ghost Studio audio file
    """
    if job_id not in ghost_studio_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = ghost_studio_jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    final_audio_path = job.get("final_audio_path")
    if not final_audio_path or not os.path.exists(final_audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    filename = f"ghost_studio_{job_id}.mp3"
    return FileResponse(
        final_audio_path,
        media_type="audio/mpeg",
        filename=filename
    )

@app.get("/api/ghost-studio/usage/{user_id}")
def get_user_ghost_usage(user_id: str, user_tier: str = "free"):
    """
    Check user's Ghost Studio usage and remaining quota
    """
    user_usage = user_ghost_usage.get(user_id, 0)
    tier_limit = GHOST_STUDIO_LIMITS.get(user_tier, 0)
    remaining_usage = "unlimited" if tier_limit == -1 else max(0, tier_limit - user_usage)
    
    return {
        "user_id": user_id,
        "user_tier": user_tier,
        "usage_count": user_usage,
        "tier_limit": tier_limit if tier_limit != -1 else "unlimited",
        "remaining_usage": remaining_usage,
        "can_generate": tier_limit == -1 or user_usage < tier_limit,
        "upgrade_message": {
            "free": "Upgrade to Pro for 20 generations/month or Enterprise for unlimited",
            "pro": "Upgrade to Enterprise for unlimited Ghost Studio generations",
            "enterprise": "You have unlimited access"
        }.get(user_tier, "")
    }

@app.get("/api/ghost-studio/jobs")
def list_ghost_studio_jobs():
    """
    List all Ghost Studio jobs (for debugging)
    """
    return {
        "total_jobs": len(ghost_studio_jobs),
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "style_prompt": job["style_prompt"][:50] + "..." if len(job["style_prompt"]) > 50 else job["style_prompt"],
                "user_tier": job["user_tier"],
                "postproduction_enabled": job["postproduction_enabled"],
                "created_at": job["created_at"]
            }
            for job_id, job in ghost_studio_jobs.items()
        ]
    }

# ===== OLLAMA CREATIVE AI ENDPOINTS =====

@app.post("/api/ai/generate-lyrics")
async def generate_lyrics_ai(request: LyricsRequest):
    """
    Generate coherent, structured lyrics using Ollama AI
    """
    if not AI_AVAILABLE:
        return {
            "success": False,
            "error": "AI assistant not available",
            "fallback_lyrics": f"""[Verse 1]
{getattr(request, 'theme', 'Life is beautiful')} fills my heart today
Every moment feels like a brand new way
{getattr(request, 'mood', 'Happy')} feelings flowing through my soul
Making me feel complete and whole

[Chorus]
This is the song of {getattr(request, 'theme', 'our dreams')}
Nothing is quite the way it seems
{getattr(request, 'genre', 'Pop')} rhythm in the air
Music and love everywhere""",
            "message": "AI not available, showing template lyrics. Deploy with Ollama for AI-generated content."
        }
    
    try:
        result = ollama_assistant.generate_coherent_lyrics(request)
        return {
            "success": True,
            "lyrics": result.lyrics,
            "structure": result.structure,
            "rhyme_scheme": result.rhyme_scheme,
            "suggested_melody_notes": result.suggested_melody_notes,
            "coherence_score": result.coherence_score,
            "metadata": {
                "theme": request.theme,
                "mood": request.mood,
                "genre": request.genre,
                "language": request.language
            }
        }
    except Exception as e:
        logger.error(f"❌ Lyrics generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate lyrics: {str(e)}")

@app.post("/api/ai/generate-prompt")
async def generate_prompt_ai(request: PromptRequest):
    """
    Convert user words into professional Suno prompts using AI
    """
    try:
        result = ollama_assistant.generate_smart_prompt(request)
        return {
            "success": True,
            "original_words": request.user_words,
            "optimized_prompt": result.optimized_prompt,
            "detected_genre": result.detected_genre,
            "style_tags": result.style_tags,
            "mood_analysis": result.mood_analysis,
            "suggested_bpm": result.suggested_bpm,
            "improvement_tips": [
                "Use the optimized prompt for better Suno results",
                f"Consider {result.suggested_bpm} BPM for this style",
                f"Genre detected as {result.detected_genre} - adjust if needed"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Prompt generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate prompt: {str(e)}")

@app.post("/api/ai/generate-metadata")
async def generate_metadata_ai(request: SongMetadataRequest):
    """
    Generate song metadata, titles, and descriptions using AI
    """
    try:
        result = ollama_assistant.generate_song_metadata(request)
        return {
            "success": True,
            "metadata": result,
            "generated_at": time.time()
        }
    except Exception as e:
        logger.error(f"❌ Metadata generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate metadata: {str(e)}")

@app.post("/api/ai/suggest-structure")
async def suggest_structure_ai(
    theme: str,
    genre: str = "pop",
    duration: int = 180
):
    """
    Suggest optimal song structure using AI
    """
    try:
        result = ollama_assistant.suggest_song_structure(theme, genre, duration)
        return {
            "success": True,
            "theme": theme,
            "genre": genre,
            "duration": duration,
            "suggestions": result
        }
    except Exception as e:
        logger.error(f"❌ Structure suggestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest structure: {str(e)}")

@app.post("/api/ai/improve-prompt")
async def improve_prompt_ai(
    current_prompt: str,
    target_quality: str = "professional"
):
    """
    Improve existing prompts for better Suno results
    """
    try:
        result = ollama_assistant.recommend_style_improvements(current_prompt, target_quality)
        return {
            "success": True,
            "original_prompt": current_prompt,
            "improvements": result,
            "target_quality": target_quality
        }
    except Exception as e:
        logger.error(f"❌ Prompt improvement error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to improve prompt: {str(e)}")

@app.post("/api/ai/enhance-lyrics")
async def enhance_lyrics_ai(
    lyrics: str,
    improvements: List[str] = ["flow", "coherence", "rhyme"]
):
    """
    Enhance existing lyrics for better quality
    """
    try:
        enhanced_lyrics = ollama_assistant.enhance_existing_lyrics(lyrics, improvements)
        return {
            "success": True,
            "original_lyrics": lyrics,
            "enhanced_lyrics": enhanced_lyrics,
            "improvements_applied": improvements,
            "enhancement_tips": [
                "Compare original vs enhanced versions",
                "Choose the version that fits your vision better",
                "Combine elements from both if needed"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Lyrics enhancement error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enhance lyrics: {str(e)}")

@app.get("/api/ai/creative-suggestions")
async def get_creative_suggestions(
    mood: str = "upbeat",
    genre: str = "pop"
):
    """
    Get creative suggestions for songwriting
    """
    try:
        # Generate creative prompts and ideas
        suggestions = {
            "theme_ideas": [
                "Love in the digital age",
                "Chasing dreams in the city",
                "Finding peace in chaos",
                "Dancing through the rain",
                "Midnight conversations"
            ],
            "lyric_starters": [
                f"In this {mood} {genre} song, we could explore...",
                f"Picture a {mood} scene where...",
                f"The {genre} rhythm captures the feeling of..."
            ],
            "prompt_templates": [
                f"{genre}, {mood} mood, modern production",
                f"Uplifting {genre} with {mood} energy, clean vocals",
                f"Contemporary {genre}, {mood} vibes, radio-ready"
            ],
            "structure_suggestions": [
                "Intro - Verse - Pre-Chorus - Chorus - Verse - Chorus - Bridge - Chorus - Outro",
                "Verse - Chorus - Verse - Chorus - Bridge - Chorus - Chorus",
                "Intro - Verse - Chorus - Verse - Chorus - Bridge - Final Chorus"
            ]
        }
        
        return {
            "success": True,
            "mood": mood,
            "genre": genre,
            "suggestions": suggestions,
            "tip": "Use these as starting points and let your creativity flow!"
        }
    except Exception as e:
        logger.error(f"❌ Creative suggestions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@app.get("/api/ai/ollama-status")
async def check_ollama_status():
    """
    Check if Ollama is running and available
    """
    try:
        # Test Ollama connection
        test_response = ollama_assistant._call_ollama("Test", "Respond with 'OK' if you're working.")
        
        if "OK" in test_response or test_response:
            return {
                "ollama_available": True,
                "model": ollama_assistant.model,
                "status": "ready",
                "response_test": test_response[:50] + "..." if len(test_response) > 50 else test_response
            }
        else:
            return {
                "ollama_available": False,
                "model": ollama_assistant.model,
                "status": "not_responding",
                "error": "Ollama not responding"
            }
    except Exception as e:
        return {
            "ollama_available": False,
            "model": ollama_assistant.model,
            "status": "error",
            "error": str(e)
        }

# ===== INTERACTIVE ASSISTANT ENDPOINTS =====

@app.post("/api/assistant/start-session")
async def start_creative_session(user_id: str):
    """
    Start a new interactive creative session with the AI assistant
    """
    if not AI_AVAILABLE:
        return {
            "success": False,
            "error": "AI assistant not available in this deployment",
            "message": "Interactive AI assistant requires Ollama to be installed. The basic music generation features are still available.",
            "alternatives": [
                "Use /api/generate for basic music generation",
                "Use /api/ghost-studio/generate for audio transformation",
                "Check /api/ai/ollama-status for AI availability"
            ]
        }
    
    try:
        session = interactive_assistant.start_session(user_id)
        return {
            "success": True,
            "session_id": session.session_id,
            "welcome_message": session.conversation[-1].content if session.conversation else "",
            "options": session.conversation[-1].metadata.get("options", []) if session.conversation else [],
            "created_at": session.created_at
        }
    except Exception as e:
        logger.error(f"❌ Session creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@app.post("/api/assistant/chat/{session_id}")
async def chat_with_assistant(session_id: str, message: str):
    """
    Send message to interactive assistant and get response
    """
    try:
        response = interactive_assistant.process_user_message(session_id, message)
        
        if "error" in response:
            raise HTTPException(status_code=404, detail=response["error"])
        
        return {
            "success": True,
            "session_id": session_id,
            "assistant_response": response["response"]["content"],
            "metadata": response["response"].get("metadata", {}),
            "conversation_length": response["conversation_length"],
            "current_step": response["current_step"],
            "progress": response["project_progress"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/api/assistant/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get information about a creative session
    """
    try:
        summary = interactive_assistant.get_session_summary(session_id)
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        return {
            "success": True,
            "session": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Session info error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")

@app.get("/api/assistant/conversation/{session_id}")
async def get_conversation_history(session_id: str, limit: int = 50):
    """
    Get conversation history for a session
    """
    try:
        if session_id not in interactive_assistant.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = interactive_assistant.active_sessions[session_id]
        
        # Get recent messages (limited)
        conversation = session.conversation[-limit:] if len(session.conversation) > limit else session.conversation
        
        return {
            "success": True,
            "session_id": session_id,
            "conversation": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "metadata": msg.metadata
                }
                for msg in conversation
            ],
            "total_messages": len(session.conversation),
            "showing": len(conversation)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Conversation history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

@app.post("/api/assistant/recommendations/{session_id}")
async def get_creative_recommendations(session_id: str):
    """
    Get personalized creative recommendations based on session
    """
    try:
        recommendations = interactive_assistant.generate_project_recommendations(session_id)
        
        if "error" in recommendations:
            raise HTTPException(status_code=404, detail=recommendations["error"])
        
        return {
            "success": True,
            "recommendations": recommendations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@app.post("/api/assistant/quick-help")
async def get_quick_help(
    question: str,
    context: str = "general"
):
    """
    Get quick help without starting a full session
    """
    try:
        system_prompt = f"""You are a helpful Son1k music assistant. 
        
        Context: {context}
        
        Provide a quick, helpful answer to the user's question about music creation.
        Be concise but informative. Include actionable advice when possible."""
        
        response = ollama_assistant._call_ollama(question, system_prompt)
        
        return {
            "success": True,
            "question": question,
            "answer": response,
            "context": context,
            "suggestion": "For more detailed help, start a creative session with our interactive assistant!"
        }
    except Exception as e:
        logger.error(f"❌ Quick help error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to provide help: {str(e)}")

@app.get("/api/assistant/templates")
async def get_creative_templates():
    """
    Get creative templates and starting points
    """
    try:
        templates = {
            "song_themes": [
                {"theme": "Amor perdido", "mood": "melancólico", "genre": "balada"},
                {"theme": "Perseguir sueños", "mood": "inspirador", "genre": "pop"},
                {"theme": "Noche de fiesta", "mood": "energético", "genre": "dance"},
                {"theme": "Reflexiones de vida", "mood": "contemplativo", "genre": "indie"},
                {"theme": "Superación personal", "mood": "motivacional", "genre": "rock"}
            ],
            "lyric_starters": [
                "En el silencio de la noche...",
                "Cuando todo parecía perdido...",
                "Bajo las luces de la ciudad...",
                "Con cada paso que doy...",
                "Entre sueños y realidad..."
            ],
            "prompt_templates": [
                "Pop moderno, voces claras, producción cristalina, 120 BPM",
                "Rock alternativo, guitarras potentes, energía creciente",
                "Balada emotiva, piano principal, cuerdas sutiles",
                "Electrónica upbeat, sintetizadores brillantes, ritmo bailable",
                "Indie folk, guitarra acústica, voces íntimas, orgánico"
            ],
            "creative_exercises": [
                "Describe tu día perfecto en 4 líneas",
                "Imagina un diálogo entre dos amigos",
                "Piensa en un color y sus emociones",
                "Recuerda tu canción favorita de la infancia",
                "Describe el sonido de tu ciudad"
            ]
        }
        
        return {
            "success": True,
            "templates": templates,
            "tip": "Usa estos templates como punto de partida para tu creatividad!"
        }
    except Exception as e:
        logger.error(f"❌ Templates error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

@app.delete("/api/assistant/session/{session_id}")
async def end_creative_session(session_id: str):
    """
    End and cleanup a creative session
    """
    try:
        if session_id in interactive_assistant.active_sessions:
            # Get final summary before deletion
            summary = interactive_assistant.get_session_summary(session_id)
            
            # Remove session
            del interactive_assistant.active_sessions[session_id]
            
            return {
                "success": True,
                "message": "Session ended successfully",
                "final_summary": summary
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Session cleanup error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

# ===== GHOST STUDIO PROCESSING FUNCTIONS =====

async def process_ghost_studio_generation(
    job_id: str, 
    audio_file_path: str, 
    request: GhostStudioRequest,
    postprod_settings: PostProductionSettings
):
    """
    Complete Ghost Studio processing pipeline
    """
    try:
        job = ghost_studio_jobs[job_id]
        job["status"] = "processing"
        job["stage"] = "uploading_to_suno"
        
        # Step 1: Upload audio to Suno Cover
        logger.info(f"🎭 Starting Ghost Studio processing for job {job_id}")
        
        # Check credentials
        if not SUNO_COOKIE:
            job["status"] = "failed"
            job["error"] = "Suno credentials not configured"
            return
            
        # Clean cookie
        clean_cookie = SUNO_COOKIE.replace('\n', '').replace('\r', '').strip()
        
        headers = {
            "Cookie": clean_cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://suno.com",
            "Origin": "https://suno.com"
        }
        
        # Step 2: Upload audio file to Suno Cover
        job["stage"] = "uploading_audio"
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'file': ('audio.mp3', audio_file, 'audio/mpeg')
            }
            
            # Try multiple Suno Cover endpoints
            cover_endpoints = [
                f"{SUNO_BASE_URL}/api/cover/upload/",
                f"{SUNO_BASE_URL}/api/v2/cover/upload/",
                "https://suno.com/api/cover/upload/"
            ]
            
            upload_response = None
            for endpoint in cover_endpoints:
                try:
                    logger.info(f"🔄 Trying cover upload endpoint: {endpoint}")
                    upload_response = requests.post(
                        endpoint,
                        headers=headers,
                        files=files,
                        timeout=60
                    )
                    
                    if upload_response.status_code == 200:
                        break
                        
                except Exception as e:
                    logger.error(f"❌ Upload endpoint {endpoint} failed: {e}")
                    continue
        
        if not upload_response or upload_response.status_code != 200:
            job["status"] = "failed"
            job["error"] = f"Failed to upload audio to Suno Cover: {upload_response.status_code if upload_response else 'No response'}"
            return
            
        upload_result = upload_response.json()
        audio_id = upload_result.get("id") or upload_result.get("audio_id")
        
        if not audio_id:
            job["status"] = "failed"
            job["error"] = "No audio ID returned from Suno upload"
            return
            
        logger.info(f"✅ Audio uploaded to Suno with ID: {audio_id}")
        
        # Step 3: Create cover generation request
        job["stage"] = "generating_cover"
        
        cover_payload = {
            "audio_id": audio_id,
            "prompt": request.style_prompt,
            "mv": "chirp-v3-5",
            "vocal_enhancement": request.vocal_enhancement,
            "instrumental_boost": request.instrumental_boost
        }
        
        # Try cover generation endpoints
        generation_endpoints = [
            f"{SUNO_BASE_URL}/api/cover/generate/",
            f"{SUNO_BASE_URL}/api/v2/cover/generate/",
            "https://suno.com/api/cover/generate/"
        ]
        
        generation_response = None
        for endpoint in generation_endpoints:
            try:
                logger.info(f"🔄 Trying cover generation endpoint: {endpoint}")
                generation_response = requests.post(
                    endpoint,
                    headers=headers,
                    json=cover_payload,
                    timeout=30
                )
                
                if generation_response.status_code == 200:
                    break
                    
            except Exception as e:
                logger.error(f"❌ Generation endpoint {endpoint} failed: {e}")
                continue
        
        if not generation_response or generation_response.status_code != 200:
            job["status"] = "failed"
            job["error"] = f"Failed to generate cover: {generation_response.status_code if generation_response else 'No response'}"
            return
            
        generation_result = generation_response.json()
        cover_ids = []
        
        if "clips" in generation_result:
            cover_ids = [clip["id"] for clip in generation_result["clips"]]
        elif "id" in generation_result:
            cover_ids = [generation_result["id"]]
        
        if not cover_ids:
            job["status"] = "failed"
            job["error"] = "No cover IDs returned from generation"
            return
            
        job["suno_cover_ids"] = cover_ids
        logger.info(f"✅ Cover generation started with IDs: {cover_ids}")
        
        # Step 4: Poll for completion
        job["stage"] = "waiting_for_completion"
        await poll_cover_completion(job_id, cover_ids, postprod_settings)
        
    except Exception as e:
        ghost_studio_jobs[job_id]["status"] = "failed"
        ghost_studio_jobs[job_id]["error"] = f"Ghost Studio error: {str(e)}"
        logger.error(f"❌ Error in Ghost Studio processing: {e}")

async def poll_cover_completion(job_id: str, cover_ids: list, postprod_settings: PostProductionSettings):
    """
    Poll Suno Cover API for completion and then apply postproduction
    """
    import asyncio
    
    job = ghost_studio_jobs[job_id]
    max_attempts = 120  # 10 minutes max
    attempt = 0
    
    clean_cookie = SUNO_COOKIE.replace('\n', '').replace('\r', '').strip()
    headers = {
        "Cookie": clean_cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://suno.com"
    }
    
    while attempt < max_attempts:
        try:
            all_complete = True
            completed_covers = []
            
            for cover_id in cover_ids:
                # Check cover status
                status_endpoints = [
                    f"{SUNO_BASE_URL}/api/feed/{cover_id}",
                    f"{SUNO_BASE_URL}/api/cover/{cover_id}",
                    f"https://suno.com/api/feed/{cover_id}"
                ]
                
                for endpoint in status_endpoints:
                    try:
                        response = requests.get(endpoint, headers=headers, timeout=10)
                        if response.status_code == 200:
                            cover_data = response.json()
                            
                            if cover_data.get("status") == "complete":
                                completed_covers.append(cover_data)
                            else:
                                all_complete = False
                            break
                    except:
                        continue
                else:
                    all_complete = False
            
            # If all covers are complete, proceed to postproduction
            if all_complete and completed_covers:
                logger.info(f"✅ All covers completed for job {job_id}")
                
                # Take the first completed cover
                best_cover = completed_covers[0]
                cover_audio_url = best_cover.get("audio_url")
                
                if not cover_audio_url:
                    job["status"] = "failed"
                    job["error"] = "No audio URL in completed cover"
                    return
                
                # Step 5: Download generated cover
                job["stage"] = "downloading_cover"
                temp_cover_path = f"{AUDIO_STORAGE_PATH}/{job_id}_cover.mp3"
                
                cover_response = requests.get(cover_audio_url, timeout=60)
                if cover_response.status_code == 200:
                    with open(temp_cover_path, 'wb') as f:
                        f.write(cover_response.content)
                else:
                    job["status"] = "failed"
                    job["error"] = f"Failed to download cover audio: {cover_response.status_code}"
                    return
                
                # Step 6: Apply postproduction if requested
                final_audio_path = temp_cover_path
                
                if job.get("postproduction_enabled", True):
                    job["stage"] = "applying_postproduction"
                    final_audio_path = await apply_postproduction(
                        job_id, 
                        temp_cover_path, 
                        postprod_settings
                    )
                    
                    if not final_audio_path:
                        job["status"] = "failed"
                        job["error"] = "Postproduction failed"
                        return
                
                # Step 7: Finalize job
                job["status"] = "completed"
                job["result"] = {
                    "audio_url": f"/api/ghost-studio/download/{job_id}",
                    "original_cover_url": cover_audio_url,
                    "title": f"Ghost Studio: {job['style_prompt'][:30]}...",
                    "duration": best_cover.get("duration"),
                    "postproduction_applied": job.get("postproduction_enabled", True),
                    "metadata": {
                        "suno_cover_id": best_cover.get("id"),
                        "style_prompt": job["style_prompt"],
                        "generated_at": time.time(),
                        "postprod_settings": postprod_settings.dict() if job.get("postproduction_enabled", True) else None
                    }
                }
                
                # Store final audio path for download
                job["final_audio_path"] = final_audio_path
                
                logger.info(f"🎉 Ghost Studio generation completed for job {job_id}")
                return
            
            # Wait before next check
            await asyncio.sleep(5)
            attempt += 1
            
            if attempt % 12 == 0:  # Every minute
                logger.info(f"⏳ Still waiting for Ghost Studio generation... ({attempt*5}s)")
                
        except Exception as e:
            logger.error(f"❌ Error polling cover completion: {e}")
            await asyncio.sleep(5)
            attempt += 1
    
    # Timeout reached
    job["status"] = "failed"
    job["error"] = "Ghost Studio generation timeout"
    logger.error(f"⏰ Ghost Studio timeout for job {job_id}")

async def apply_postproduction(job_id: str, audio_path: str, settings: PostProductionSettings) -> str:
    """
    Apply professional postproduction using Waves plugins
    """
    try:
        logger.info(f"🎛️ Starting postproduction for job {job_id}")
        
        output_path = f"{AUDIO_STORAGE_PATH}/{job_id}_mastered.wav"
        
        # Check if Waves plugins are available
        if not os.path.exists(WAVES_PLUGINS_PATH):
            logger.warning("Waves plugins not found, applying basic processing")
            return await apply_basic_postproduction(audio_path, output_path, settings)
        
        # Create Waves processing chain
        waves_script = create_waves_processing_script(audio_path, output_path, settings)
        
        # Execute Waves processing
        result = subprocess.run([
            "osascript", "-e", waves_script
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(output_path):
            logger.info(f"✅ Waves postproduction completed for job {job_id}")
            return output_path
        else:
            logger.error(f"❌ Waves processing failed: {result.stderr}")
            # Fallback to basic processing
            return await apply_basic_postproduction(audio_path, output_path, settings)
            
    except Exception as e:
        logger.error(f"❌ Postproduction error: {e}")
        # Fallback to basic processing
        try:
            return await apply_basic_postproduction(audio_path, output_path, settings)
        except:
            return audio_path  # Return original if all processing fails

def create_waves_processing_script(input_path: str, output_path: str, settings: PostProductionSettings) -> str:
    """
    Create AppleScript for Waves plugin automation
    """
    return f'''
    tell application "Logic Pro"
        activate
        
        -- Create new project
        make new project
        
        -- Import audio
        set audioTrack to make new software instrument track
        import audio file "{input_path}" to track audioTrack
        
        -- Apply Waves plugins chain
        
        -- 1. EQ (Waves SSL E-Channel)
        add audio effect "SSL E-Channel" to track audioTrack
        set eq_preset to "{settings.eq_preset}"
        
        -- 2. Compression (Waves CLA-76)
        add audio effect "CLA-76" to track audioTrack
        set parameter "Input" to {settings.compression_level}
        
        -- 3. Reverb (Waves H-Reverb)
        add audio effect "H-Reverb" to track audioTrack
        set parameter "Mix" to {settings.reverb_amount}
        
        -- 4. Stereo Enhancement (Waves S1 Stereo Imager)
        add audio effect "S1 Stereo Imager" to track audioTrack
        set parameter "Width" to {settings.stereo_width}
        
        -- 5. Final Limiter (Waves L3-16 Multimaximizer)
        add audio effect "L3-16 Multimaximizer" to track audioTrack
        set parameter "Threshold" to {settings.mastering_level}
        
        -- Bounce to file
        bounce to file "{output_path}" format AIFF bit depth 24 sample rate 44100
        
        -- Close project without saving
        close front project saving no
        
    end tell
    '''

async def apply_basic_postproduction(input_path: str, output_path: str, settings: PostProductionSettings) -> str:
    """
    Apply basic postproduction using FFmpeg when Waves is not available
    """
    try:
        logger.info("🔧 Applying basic postproduction with FFmpeg")
        
        # Build FFmpeg command with audio filters
        cmd = [
            "ffmpeg", "-i", input_path,
            "-af", f"""
            equalizer=f=100:width_type=q:width=1:g={settings.compression_level * 3},
            equalizer=f=1000:width_type=q:width=1:g={settings.compression_level * 2},
            equalizer=f=5000:width_type=q:width=1:g={settings.compression_level},
            compand=0.3|0.3:1|1:-90/-900|-70/-70|-30/-9|0/-3:6:0:-90:0.2,
            aecho=0.8:0.88:{int(settings.reverb_amount * 60)}:0.4,
            extrastereo=m={settings.stereo_width},
            loudnorm=I={settings.mastering_level}:TP=-1.5:LRA=11
            """.replace('\n', '').replace(' ', ''),
            "-ar", "44100", "-ac", "2",
            output_path, "-y"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0 and os.path.exists(output_path):
            logger.info("✅ Basic postproduction completed")
            return output_path
        else:
            logger.error(f"❌ FFmpeg processing failed: {result.stderr}")
            return input_path
            
    except Exception as e:
        logger.error(f"❌ Basic postproduction error: {e}")
        return input_path

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)# Force Railway redeploy
