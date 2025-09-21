#!/usr/bin/env python3
"""
CAPTCHA Router for Son1kVers3
Handles CAPTCHA event notifications and status tracking for Selenium automation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for CAPTCHA status (in production, use Redis/database)
CAPTCHA_STATUS: Dict[str, Dict] = {}

class CaptchaEvent(BaseModel):
    job_id: str
    provider: str  # hcaptcha | turnstile | recaptcha | unknown
    status: str    # NEEDED | RESOLVED
    novnc_url: Optional[str] = None
    browser_session: Optional[str] = None
    timestamp: Optional[int] = None

class CaptchaStatusResponse(BaseModel):
    job_id: str
    status: str
    provider: Optional[str] = None
    novnc_url: Optional[str] = None
    created_at: Optional[int] = None
    resolved_at: Optional[int] = None

@router.post("/captcha/event")
async def captcha_event(event: CaptchaEvent):
    """
    Receive CAPTCHA event notifications from Selenium workers
    
    This endpoint is called by the automation when:
    - A CAPTCHA is detected (status=NEEDED)
    - A CAPTCHA is resolved (status=RESOLVED)
    """
    try:
        logger.info(f"🛡️ CAPTCHA event: {event.job_id} - {event.status} ({event.provider})")
        
        # Update timestamp
        if not event.timestamp:
            event.timestamp = int(time.time())
        
        # Get existing status or create new
        existing = CAPTCHA_STATUS.get(event.job_id, {})
        
        # Update status
        updated_status = {
            "job_id": event.job_id,
            "status": event.status,
            "provider": event.provider,
            "novnc_url": event.novnc_url,
            "browser_session": event.browser_session,
            "created_at": existing.get("created_at", event.timestamp),
            "updated_at": event.timestamp
        }
        
        # Set resolved timestamp if CAPTCHA is resolved
        if event.status == "RESOLVED":
            updated_status["resolved_at"] = event.timestamp
            logger.info(f"✅ CAPTCHA resolved for job {event.job_id}")
        elif event.status == "NEEDED":
            logger.info(f"🔒 CAPTCHA needed for job {event.job_id}: {event.provider}")
            if event.novnc_url:
                logger.info(f"🖥️ noVNC URL available: {event.novnc_url}")
        
        CAPTCHA_STATUS[event.job_id] = updated_status
        
        return {
            "success": True,
            "message": f"CAPTCHA event recorded for job {event.job_id}",
            "status": event.status
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to process CAPTCHA event: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process CAPTCHA event: {str(e)}"
        )

@router.get("/captcha/status/{job_id}", response_model=CaptchaStatusResponse)
async def get_captcha_status(job_id: str):
    """
    Get current CAPTCHA status for a job
    
    Used by frontend to check if user intervention is needed
    """
    try:
        status_data = CAPTCHA_STATUS.get(job_id, {
            "job_id": job_id,
            "status": "UNKNOWN"
        })
        
        return CaptchaStatusResponse(**status_data)
        
    except Exception as e:
        logger.error(f"❌ Failed to get CAPTCHA status for {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get CAPTCHA status: {str(e)}"
        )

@router.get("/captcha/active")
async def get_active_captchas():
    """
    Get all active CAPTCHA requests needing resolution
    
    Useful for monitoring dashboard
    """
    try:
        active_captchas = [
            status for status in CAPTCHA_STATUS.values()
            if status.get("status") == "NEEDED"
        ]
        
        return {
            "success": True,
            "active_captchas": active_captchas,
            "total": len(active_captchas)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get active CAPTCHAs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active CAPTCHAs: {str(e)}"
        )

@router.delete("/captcha/status/{job_id}")
async def clear_captcha_status(job_id: str):
    """
    Clear CAPTCHA status for a completed job
    
    Used for cleanup after job completion
    """
    try:
        if job_id in CAPTCHA_STATUS:
            del CAPTCHA_STATUS[job_id]
            logger.info(f"🗑️ Cleared CAPTCHA status for job {job_id}")
        
        return {
            "success": True,
            "message": f"CAPTCHA status cleared for job {job_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to clear CAPTCHA status for {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear CAPTCHA status: {str(e)}"
        )

@router.post("/captcha/manual-resolve/{job_id}")
async def manual_resolve_captcha(job_id: str):
    """
    Manually mark a CAPTCHA as resolved
    
    Emergency endpoint for manual intervention
    """
    try:
        if job_id not in CAPTCHA_STATUS:
            raise HTTPException(
                status_code=404,
                detail=f"CAPTCHA status not found for job {job_id}"
            )
        
        # Update status to resolved
        CAPTCHA_STATUS[job_id]["status"] = "RESOLVED"
        CAPTCHA_STATUS[job_id]["resolved_at"] = int(time.time())
        CAPTCHA_STATUS[job_id]["updated_at"] = int(time.time())
        
        logger.info(f"🛠️ Manually resolved CAPTCHA for job {job_id}")
        
        return {
            "success": True,
            "message": f"CAPTCHA manually resolved for job {job_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to manually resolve CAPTCHA for {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to manually resolve CAPTCHA: {str(e)}"
        )

# Health check for the CAPTCHA API
@router.get("/captcha/health")
async def captcha_health():
    """Health check for CAPTCHA API"""
    return {
        "status": "healthy",
        "service": "captcha_api",
        "active_captchas": len([
            s for s in CAPTCHA_STATUS.values() 
            if s.get("status") == "NEEDED"
        ])
    }

# Export router
__all__ = ["router"]