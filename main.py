"""
Son1k Suno API - Production Version
Transparent music generation API for Son1k frontend
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import json
import time
import uuid
from typing import Optional, Dict, Any

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

# In-memory storage (use Redis in production)
generation_jobs: Dict[str, Dict[str, Any]] = {}

# Suno API Configuration
SUNO_SESSION_ID = os.environ.get("SUNO_SESSION_ID", "")
SUNO_COOKIE = os.environ.get("SUNO_COOKIE", "")
SUNO_BASE_URL = "https://studio-api.suno.ai"

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
        headers = {
            "Cookie": SUNO_COOKIE,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://suno.com",
            "Origin": "https://suno.com"
        }
        
        # Step 1: Create generation request
        generation_payload = {
            "mv": "chirp-v3-5",
            "prompt": request.prompt,
            "make_instrumental": False,
            "wait_audio": False
        }
        
        # Add lyrics if provided
        if request.lyrics:
            generation_payload["lyrics"] = request.lyrics
            generation_payload["tags"] = request.style or "pop"
        else:
            generation_payload["make_instrumental"] = True
            generation_payload["tags"] = f"{request.style or 'instrumental'}, {request.prompt}"
        
        print(f"🎵 Starting Suno generation for job {job_id}")
        print(f"📝 Prompt: {request.prompt}")
        print(f"🎤 Lyrics: {request.lyrics[:100]}..." if request.lyrics else "🎼 Instrumental")
        
        # Make request to Suno API
        response = requests.post(
            f"{SUNO_BASE_URL}/api/generate/v2/",
            headers=headers,
            json=generation_payload,
            timeout=30
        )
        
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
            headers = {
                "Cookie": SUNO_COOKIE,
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)# Force Railway redeploy
