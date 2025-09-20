from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import uuid
import json
import time
import logging
from datetime import datetime

# usa la app Celery del proyecto existente
try:
    from backend.app.queue import celery_app
except Exception:
    from celery import Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    celery_app = Celery("son1k_fallback", broker=REDIS_URL, backend=REDIS_URL)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/music", tags=["music"])

class MusicGenRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = None
    instrumental: bool = False
    style: Optional[str] = None
    user_id: Optional[str] = None

# Simple in-memory job tracking (could be moved to Redis for production)
job_registry = {}

def create_job_record(job_id: str, user_id: str, payload: dict) -> dict:
    """Create and store a job record"""
    job_record = {
        "job_id": job_id,
        "user_id": user_id or "anonymous",
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "payload": payload,
        "progress": 0,
        "message": "Job queued for processing",
        "result": None,
        "error": None
    }
    
    job_registry[job_id] = job_record
    logger.info(f"📋 Created job record: {job_id} for user: {user_id}")
    return job_record

def update_job_status(job_id: str, status: str, **kwargs) -> bool:
    """Update job status and metadata"""
    if job_id not in job_registry:
        logger.warning(f"⚠️ Job {job_id} not found in registry")
        return False
    
    job_registry[job_id].update({
        "status": status,
        "updated_at": datetime.now().isoformat(),
        **kwargs
    })
    
    logger.info(f"📊 Updated job {job_id}: {status}")
    return True

@router.post("/generate")
def generate_music(req: MusicGenRequest, request: Request) -> Dict[str, Any]:
    """Generate music with enhanced job lifecycle management"""
    try:
        # Extract user info from request
        user_id = req.user_id or getattr(request.state, 'user_id', None) or "anonymous"
        
        # Create enhanced payload
        payload = {
            "prompt": req.prompt,
            "lyrics": req.lyrics,
            "instrumental": req.instrumental,
            "style": req.style,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "source": "web_interface"
        }
        
        # Generate transparent job ID
        job_id = f"son1k_job_{int(time.time())}"
        
        # Send task to Celery with custom job ID
        async_result = celery_app.send_task("tasks.generate", 
                                          args=[payload], 
                                          task_id=job_id)
        
        # Create job record
        job_record = create_job_record(job_id, user_id, payload)
        
        # Return comprehensive response
        return {
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "message": "Music generation job queued successfully",
            "user_id": user_id,
            "created_at": job_record["created_at"],
            "estimated_completion": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"❌ Music generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue music generation: {e}")

@router.get("/status/{job_id}")
def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get comprehensive job status and details"""
    try:
        # Check job registry first
        if job_id in job_registry:
            job_record = job_registry[job_id]
            
            # Try to get Celery task status
            try:
                async_result = celery_app.AsyncResult(job_id)
                celery_status = async_result.status
                celery_result = async_result.result
                
                # Update status based on Celery state
                if celery_status == "SUCCESS":
                    if isinstance(celery_result, dict) and celery_result.get("success"):
                        update_job_status(job_id, "completed", 
                                        progress=100, 
                                        result=celery_result,
                                        message="Generation completed successfully")
                    else:
                        update_job_status(job_id, "failed", 
                                        progress=100,
                                        error=celery_result.get("error", "Unknown error") if isinstance(celery_result, dict) else str(celery_result))
                elif celery_status == "FAILURE":
                    update_job_status(job_id, "failed", 
                                    progress=100,
                                    error=str(celery_result))
                elif celery_status == "PENDING":
                    update_job_status(job_id, "processing", 
                                    message="Job is being processed")
                    
            except Exception as celery_error:
                logger.warning(f"⚠️ Failed to get Celery status for {job_id}: {celery_error}")
            
            return {
                "success": True,
                **job_registry[job_id]
            }
        else:
            # Job not in registry, try Celery directly
            try:
                async_result = celery_app.AsyncResult(job_id)
                return {
                    "success": True,
                    "job_id": job_id,
                    "status": async_result.status.lower(),
                    "result": async_result.result,
                    "message": f"Job status: {async_result.status}"
                }
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {e}")

@router.get("/jobs")
def list_user_jobs(user_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """List jobs for a user or all jobs"""
    try:
        # Filter jobs by user if specified
        filtered_jobs = []
        for job_id, job_record in job_registry.items():
            if user_id is None or job_record["user_id"] == user_id:
                filtered_jobs.append(job_record)
        
        # Sort by creation time (newest first)
        filtered_jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply limit
        filtered_jobs = filtered_jobs[:limit]
        
        return {
            "success": True,
            "jobs": filtered_jobs,
            "count": len(filtered_jobs),
            "total_jobs": len(job_registry)
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {e}")

@router.delete("/jobs/{job_id}")
def cancel_job(job_id: str) -> Dict[str, Any]:
    """Cancel a job and clean up resources"""
    try:
        # Try to revoke Celery task
        try:
            celery_app.control.revoke(job_id, terminate=True)
            logger.info(f"🚫 Revoked Celery task: {job_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to revoke Celery task {job_id}: {e}")
        
        # Update job record
        if job_id in job_registry:
            update_job_status(job_id, "cancelled", 
                            progress=100,
                            message="Job cancelled by user")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Job cancelled successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error cancelling job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {e}")

@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: str) -> Dict[str, Any]:
    """Retry a failed job"""
    try:
        if job_id not in job_registry:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_record = job_registry[job_id]
        
        if job_record["status"] not in ["failed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Job is not in a retryable state")
        
        # Create new job with same payload
        new_result = celery_app.send_task("tasks.generate", args=[job_record["payload"]])
        new_job_id = new_result.id
        
        # Create new job record
        new_job_record = create_job_record(new_job_id, job_record["user_id"], job_record["payload"])
        
        return {
            "success": True,
            "original_job_id": job_id,
            "new_job_id": new_job_id,
            "message": "Job retry queued successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrying job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retry job: {e}")

# Export job management functions for use by other modules
__all__ = ["router", "job_registry", "create_job_record", "update_job_status"]
