#!/usr/bin/env python3
"""
Son1kVers3 Backend Integration
Notifies the frontend of new generated tracks
"""
import os
import requests
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def notify_frontend(result: Dict) -> bool:
    """
    Send track generation result to Son1kVers3 backend
    
    Args:
        result: Dictionary with lyrics, prompt, artifacts, etc.
        
    Returns:
        True if notification was successful
    """
    try:
        # Get configuration from environment
        base_url = os.getenv("SON1K_API_BASE", "http://localhost:8000").rstrip("/")
        token = os.getenv("SON1K_API_TOKEN", "")
        
        # Prepare endpoint
        url = f"{base_url}/api/tracks/ingest"
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Son1k-Suno-Automation/1.0"
        }
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Log the notification attempt
        logger.info(f"📡 Notifying frontend: {url}")
        logger.info(f"🎵 Track count: {len(result.get('artifacts', []))}")
        
        # Send request
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(result), 
            timeout=30
        )
        
        if response.ok:
            logger.info("✅ Frontend notification successful")
            return True
        else:
            logger.error(f"❌ Frontend notification failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Frontend notification timeout")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Frontend notification connection error")
        return False
    except Exception as e:
        logger.error(f"❌ Frontend notification error: {e}")
        return False

def prepare_notification_payload(lyrics: str, prompt: str, artifacts: list, session_id: Optional[str] = None) -> Dict:
    """
    Prepare the notification payload for the frontend
    
    Args:
        lyrics: Song lyrics
        prompt: Style prompt
        artifacts: List of audio artifacts
        session_id: Optional session identifier
        
    Returns:
        Formatted payload dictionary
    """
    import time
    
    return {
        "lyrics": lyrics,
        "prompt": prompt,
        "artifacts": artifacts,
        "session_id": session_id,
        "created_at": int(time.time()),
        "source": "suno_automation",
        "status": "completed",
        "total_tracks": len(artifacts)
    }

# Export functions
__all__ = ["notify_frontend", "prepare_notification_payload"]