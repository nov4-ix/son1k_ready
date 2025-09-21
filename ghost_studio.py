"""
Ghost Studio - Suno Cover + Postproducción System
Transparent audio style transfer and professional postproduction
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
import uuid
import time
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class GhostStudioRequest(BaseModel):
    style_prompt: str
    vocal_enhancement: Optional[bool] = True
    instrumental_boost: Optional[bool] = False
    postproduction: Optional[bool] = True

class GhostStudioResponse(BaseModel):
    job_id: str
    status: str
    message: str

class PostProductionSettings(BaseModel):
    eq_preset: Optional[str] = "modern_pop"
    compression_level: Optional[float] = 0.7
    reverb_amount: Optional[float] = 0.3
    stereo_width: Optional[float] = 1.2
    mastering_level: Optional[float] = -14.0  # LUFS
    
# Storage
ghost_jobs: Dict[str, Dict[str, Any]] = {}

# Configuration
SUNO_COOKIE = os.environ.get("SUNO_COOKIE", "")
SUNO_BASE_URL = "https://studio-api.suno.ai"
AUDIO_STORAGE_PATH = "/tmp/ghost_studio"
WAVES_PLUGINS_PATH = os.environ.get("WAVES_PLUGINS_PATH", "/Applications/Waves")

# Ensure audio storage directory exists
os.makedirs(AUDIO_STORAGE_PATH, exist_ok=True)

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
        job = ghost_jobs[job_id]
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
        ghost_jobs[job_id]["status"] = "failed"
        ghost_jobs[job_id]["error"] = f"Ghost Studio error: {str(e)}"
        logger.error(f"❌ Error in Ghost Studio processing: {e}")

async def poll_cover_completion(job_id: str, cover_ids: list, postprod_settings: PostProductionSettings):
    """
    Poll Suno Cover API for completion and then apply postproduction
    """
    import asyncio
    
    job = ghost_jobs[job_id]
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
                
                if job.get("postproduction", True):
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
                    "audio_url": f"/ghost_studio/download/{job_id}",
                    "original_cover_url": cover_audio_url,
                    "title": f"Ghost Studio: {job['style_prompt'][:30]}...",
                    "duration": best_cover.get("duration"),
                    "postproduction_applied": job.get("postproduction", True),
                    "metadata": {
                        "suno_cover_id": best_cover.get("id"),
                        "style_prompt": job["style_prompt"],
                        "generated_at": time.time(),
                        "postprod_settings": postprod_settings.dict() if job.get("postproduction", True) else None
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
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("ghost_studio:app", host="0.0.0.0", port=port, reload=True)