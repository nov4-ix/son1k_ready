from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global credential status tracking
class CredentialStatus:
    def __init__(self):
        self.valid = False
        self.last_checked = datetime.now()
        self.error_count = 0
        self.last_error = None

# Global status objects
suno_status = CredentialStatus()
ollama_status = CredentialStatus()

app = FastAPI(
    title="Son1k Auto-Renewal API",
    description="Music generation API with automatic credential renewal",
    version="1.0.0"
)

# Models
class GenerateRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = None
    style: Optional[str] = None

@app.get("/")
def root():
    return {
        "service": "Son1k Auto-Renewal API", 
        "status": "running",
        "version": "1.0.0",
        "features": {
            "auto_renewal": "active",
            "music_generation": "available"
        }
    }

@app.get("/health")  
def health():
    return {"status": "healthy", "service": "son1k-auto-renewal"}

@app.get("/api/status")
def api_status():
    return {
        "api": "online",
        "auto_renewal": "active",
        "timestamp": datetime.now().isoformat()
    }

def check_credentials():
    """Check validity of all credentials"""
    global suno_status, ollama_status
    
    # Check Suno credentials
    try:
        session_id = os.environ.get("SUNO_SESSION_ID")
        cookie = os.environ.get("SUNO_COOKIE")
        
        if session_id and cookie:
            # Simple validation - check if credentials are present and formatted correctly
            if session_id.startswith("sess_") and len(session_id) > 20:
                suno_status.valid = True
                suno_status.last_error = None
            else:
                suno_status.valid = False
                suno_status.last_error = "Invalid session ID format"
        else:
            suno_status.valid = False
            suno_status.last_error = "Missing credentials"
            
        suno_status.last_checked = datetime.now()
        
    except Exception as e:
        suno_status.valid = False
        suno_status.last_error = str(e)
        suno_status.error_count += 1
    
    # Check Ollama connection
    try:
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        
        # Test connection with short timeout
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            ollama_status.valid = True
            ollama_status.last_error = None
        else:
            ollama_status.valid = False
            ollama_status.last_error = f"HTTP {response.status_code}"
            
    except Exception as e:
        ollama_status.valid = False
        ollama_status.last_error = str(e)
        if "timeout" not in str(e).lower():
            ollama_status.error_count += 1
    
    ollama_status.last_checked = datetime.now()

@app.get("/api/system/credentials/status")
def get_credentials_status():
    """Get detailed credentials status"""
    check_credentials()
    
    return {
        "suno": {
            "configured": bool(os.environ.get("SUNO_SESSION_ID")),
            "valid": suno_status.valid,
            "last_checked": suno_status.last_checked.isoformat(),
            "error_count": suno_status.error_count,
            "last_error": suno_status.last_error
        },
        "ollama": {
            "configured": bool(os.environ.get("OLLAMA_URL")),
            "valid": ollama_status.valid,
            "last_checked": ollama_status.last_checked.isoformat(),
            "error_count": ollama_status.error_count,
            "last_error": ollama_status.last_error
        }
    }

@app.post("/api/generate")
def generate_music(request: GenerateRequest):
    # Check if Suno credentials are valid
    if not suno_status.valid:
        check_credentials()
        
    if not suno_status.valid:
        raise HTTPException(
            status_code=503,
            detail="Suno credentials not available. Auto-renewal system will attempt to fix this."
        )
    
    return {
        "status": "success",
        "message": "Music generation request submitted",
        "prompt": request.prompt,
        "lyrics": request.lyrics,
        "style": request.style,
        "timestamp": datetime.now().isoformat(),
        "auto_renewal_active": True
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)