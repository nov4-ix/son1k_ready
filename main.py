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
    Background task to handle Suno generation
    This is where we'll integrate with Suno API
    """
    try:
        job = generation_jobs[job_id]
        job["status"] = "processing"
        
        # Mock Suno API call (replace with real implementation)
        if not SUNO_SESSION_ID or not SUNO_COOKIE:
            # For testing without Suno credentials
            await simulate_generation(job_id, request)
            return
        
        # Real Suno API integration would go here
        headers = {
            "Cookie": SUNO_COOKIE,
            "Session-ID": SUNO_SESSION_ID,
            "Content-Type": "application/json"
        }
        
        # Suno generation payload
        payload = {
            "prompt": request.prompt,
            "lyrics": request.lyrics,
            "style": request.style or "pop",
            "duration": request.duration
        }
        
        # This would be the real Suno API call
        # response = requests.post(f"{SUNO_BASE_URL}/api/generate", 
        #                         headers=headers, json=payload)
        
        # For now, simulate the process
        await simulate_generation(job_id, request)
        
    except Exception as e:
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = str(e)

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
    uvicorn.run(app, host="0.0.0.0", port=port)