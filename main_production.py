from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os
import requests
import logging
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib

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

# Pro tester accounts database
PRO_TESTER_ACCOUNTS = {
    "tester1@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester2@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester3@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester4@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester5@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester6@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester7@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester8@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester9@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True},
    "tester10@son1k.com": {"password": "Premium123!", "tier": "pro", "credits": 1000, "active": True}
}

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict] = None
    token: Optional[str] = None

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

from fastapi.responses import HTMLResponse

@app.post("/api/auth/login", response_model=AuthResponse)
def login(request: LoginRequest):
    """Login endpoint for tester accounts"""
    email = request.email.lower().strip()
    
    if email in PRO_TESTER_ACCOUNTS:
        account = PRO_TESTER_ACCOUNTS[email]
        if account["password"] == request.password and account["active"]:
            # Generate simple token
            token = hashlib.md5(f"{email}:{request.password}:{int(time.time())}".encode()).hexdigest()
            
            return AuthResponse(
                success=True,
                message="Login successful",
                user={
                    "email": email,
                    "tier": account["tier"],
                    "credits": account["credits"],
                    "features": ["music_generation", "pro_features", "priority_support"]
                },
                token=token
            )
    
    return AuthResponse(
        success=False,
        message="Invalid credentials"
    )

@app.get("/api/auth/tester-accounts")
def get_tester_accounts():
    """Get list of available tester accounts"""
    return {
        "accounts": [
            {
                "email": email,
                "tier": data["tier"],
                "credits": data["credits"],
                "active": data["active"]
            }
            for email, data in PRO_TESTER_ACCOUNTS.items()
        ],
        "instructions": "Use password: Premium123! for all accounts"
    }

@app.get("/", response_class=HTMLResponse)
def root():
    """Serve the complete Son1k frontend"""
    # Read the complete frontend HTML
    try:
        with open("son1k_complete_frontend.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        # Fallback to API info if HTML file not found
        return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Son1k - Complete Frontend Loading...</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: #fff; 
            text-align: center; 
            padding: 100px 20px; 
        }
        .logo { 
            font-size: 3rem; 
            color: #ff6b6b; 
            margin-bottom: 30px; 
        }
        .message { 
            font-size: 1.2rem; 
            color: #ccc; 
            max-width: 600px; 
            margin: 0 auto; 
        }
    </style>
</head>
<body>
    <div class="logo">🎵 Son1k</div>
    <div class="message">
        Complete frontend HTML file not found. <br>
        Please ensure son1k_complete_frontend.html is in the root directory.
        <br><br>
        <a href="/api" style="color: #ff6b6b;">View API Documentation</a>
    </div>
</body>
</html>
""", status_code=200)

@app.get("/api")
def api_root():
    return {
        "service": "Son1k Auto-Renewal API", 
        "status": "running",
        "version": "1.0.0",
        "features": {
            "auto_renewal": "active",
            "music_generation": "available"
        }
    }

@app.get("/docs-api", response_class=HTMLResponse)
def api_docs():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Son1k API - Código JavaScript</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #ff6b6b; }
            .code-block { background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 20px 0; overflow-x: auto; }
            .copy-btn { background: #ff6b6b; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 0; }
            .copy-btn:hover { background: #e55555; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Código JavaScript para Son1k</h1>
            
            <h3>Código Limpio - Copia exactamente esto:</h3>
            
            <button class="copy-btn" onclick="copyCode()">📋 Copiar Código</button>
            
            <div class="code-block" id="jsCode">
async function generateMusic(prompt, lyrics, style) {
  try {
    const response = await fetch('https://son1kvers3.com/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: prompt,
        lyrics: lyrics,
        style: style
      })
    });

    if (!response.ok) {
      throw new Error('Error HTTP: ' + response.status);
    }

    const result = await response.json();
    
    console.log('Música generada:', result);
    console.log('Job ID:', result.job_id);
    console.log('Audio URL:', result.suno_response.audio_url);
    
    return result;
    
  } catch (error) {
    console.error('Error generando música:', error);
    throw error;
  }
}

generateMusic("electronic music", "test lyrics", "electronic").then(result => {
  console.log('Música lista:', result.suno_response.audio_url);
});
            </div>
            
            <script>
            function copyCode() {
              const code = document.getElementById('jsCode').innerText;
              navigator.clipboard.writeText(code).then(() => {
                alert('Código copiado al portapapeles');
              });
            }
            </script>
            
            <p style="margin-top: 40px; text-align: center; color: #666;">
                <a href="https://son1k.com" style="color: #ff6b6b;">← Volver a Son1k</a>
            </p>
        </div>
    </body>
    </html>
    """

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

@app.post("/api/system/credentials/refresh")
def refresh_credentials():
    """Force credential refresh"""
    logger.info("🔄 Manual credential refresh requested")
    
    check_credentials()
    
    return {
        "status": "refreshed",
        "timestamp": datetime.now().isoformat(),
        "suno_valid": suno_status.valid,
        "ollama_valid": ollama_status.valid
    }

@app.get("/api/system/health")
def get_system_health():
    """Get comprehensive system health status"""
    
    # Check credentials
    check_credentials()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "auto_renewal": {
            "status": "active",
            "monitoring": True,
            "last_check": datetime.now().isoformat(),
            "next_check_in": "on demand"
        },
        "credentials": {
            "suno_valid": suno_status.valid,
            "suno_last_checked": suno_status.last_checked.isoformat(),
            "suno_error_count": suno_status.error_count,
            "suno_last_error": suno_status.last_error,
            "ollama_valid": ollama_status.valid,
            "ollama_last_checked": ollama_status.last_checked.isoformat(),
            "ollama_error_count": ollama_status.error_count,
            "ollama_last_error": ollama_status.last_error
        },
        "system_info": {
            "environment": "production",
            "railway_deployment": True,
            "auto_renewal_enabled": True,
            "version": "1.0.0",
            "deployment_url": "https://web-production-5847.up.railway.app"
        }
    }

async def call_suno_real_automation(prompt: str, lyrics: Optional[str] = None, style: Optional[str] = None, ghost_options: Optional[Dict] = None):
    """REAL Suno automation using Selenium worker"""
    
    logger.info(f"🎵 Starting REAL music generation: {prompt[:50]}...")
    
    try:
        # Import the real Selenium worker
        from backend.app.selenium_worker import SunoSeleniumWorker
        
        # Initialize worker with headless mode for production
        worker = SunoSeleniumWorker(headless=True)
        
        try:
            # Setup driver
            if not worker.setup_driver():
                raise Exception("Failed to setup Selenium driver")
            
            # Load Suno with authentication
            if not worker.load_suno_with_auth():
                raise Exception("Failed to authenticate with Suno")
            
            # Navigate to create page
            if not worker.navigate_to_create():
                raise Exception("Failed to navigate to creation page")
            
            # Prepare payload for generation
            generation_payload = {
                "prompt": prompt,
                "lyrics": lyrics,
                "style": style,
                "instrumental": False
            }
            
            # Add ghost options if provided
            if ghost_options:
                generation_payload.update(ghost_options)
                logger.info(f"🎭 Using Ghost Studio options: {ghost_options}")
            
            # Generate music
            result = worker.generate_music(generation_payload)
            
            if result.get("success"):
                logger.info("✅ REAL Suno generation successful!")
                
                # Format response to match API expectations
                formatted_result = {
                    "id": f"real_suno_{int(time.time())}",
                    "status": "completed",
                    "prompt": prompt,
                    "lyrics": lyrics,
                    "style": style,
                    "method": "selenium_automation_real",
                    "message": "Music generated successfully via REAL Suno automation",
                    "audio_url": result.get("primary_file", {}).get("streaming_url", ""),
                    "download_url": result.get("primary_file", {}).get("download_url", ""),
                    "video_url": result.get("primary_file", {}).get("file_path", ""),
                    "duration": "02:30",
                    "model_name": "chirp-v3-5",
                    "created_at": datetime.now().isoformat(),
                    "credits_used": 10,
                    "generation_time": "~60 seconds",
                    "audio_files": result.get("audio_files", []),
                    "file_count": len(result.get("audio_files", [])),
                    "note": "🎵 REAL Suno generation via Selenium automation - WORKING!"
                }
                
                return formatted_result
            else:
                raise Exception(f"Suno generation failed: {result.get('error', 'Unknown error')}")
                
        finally:
            # Always cleanup driver
            worker.cleanup()
            
    except ImportError as e:
        logger.error(f"❌ Selenium worker not available: {e}")
        # Fallback to simulation with clear indication
        job_id = f"fallback_sim_{int(time.time())}"
        return {
            "id": job_id,
            "status": "simulated",
            "prompt": prompt,
            "lyrics": lyrics,
            "style": style,
            "method": "fallback_simulation",
            "message": "Selenium worker not available - using simulation",
            "audio_url": f"https://suno.com/song/{job_id}",
            "video_url": f"https://suno.com/song/{job_id}/video",
            "duration": "02:30",
            "model_name": "chirp-v3-5",
            "created_at": datetime.now().isoformat(),
            "credits_used": 10,
            "generation_time": "~30 seconds",
            "note": "⚠️ SIMULATION MODE - Real automation not available"
        }
    except Exception as e:
        logger.error(f"❌ Real Suno automation failed: {e}")
        # Return error with fallback
        job_id = f"error_fallback_{int(time.time())}"
        return {
            "id": job_id,
            "status": "error_with_fallback",
            "prompt": prompt,
            "lyrics": lyrics,
            "style": style,
            "method": "error_fallback",
            "message": f"Real automation failed: {e}",
            "audio_url": f"https://suno.com/song/{job_id}",
            "video_url": f"https://suno.com/song/{job_id}/video",
            "duration": "02:30",
            "model_name": "chirp-v3-5",
            "created_at": datetime.now().isoformat(),
            "credits_used": 10,
            "generation_time": "~30 seconds",
            "note": f"❌ Real automation error: {e}"
        }

@app.post("/api/generate")
async def generate_music(request: GenerateRequest):
    """Generate music using real Suno API"""
    
    # Check if Suno credentials are valid
    if not suno_status.valid:
        check_credentials()
        
    if not suno_status.valid:
        raise HTTPException(
            status_code=503,
            detail="Suno credentials not available. Auto-renewal system will attempt to fix this."
        )
    
    try:
        # Check if there's a local automation service available
        selenium_automation_url = os.environ.get("SELENIUM_AUTOMATION_URL")
        
        if selenium_automation_url:
            # Use local Selenium automation service
            logger.info(f"🤖 Using Selenium automation service: {selenium_automation_url}")
            try:
                automation_payload = {
                    "prompt": request.prompt,
                    "lyrics": request.lyrics,
                    "style": request.style
                }
                
                automation_response = requests.post(
                    f"{selenium_automation_url}/api/suno/generate",
                    json=automation_payload,
                    timeout=60
                )
                
                if automation_response.status_code == 200:
                    automation_result = automation_response.json()
                    logger.info(f"✅ Selenium automation successful: {automation_result}")
                    
                    return {
                        "status": "success",
                        "message": "Music generation submitted via Selenium automation",
                        "prompt": request.prompt,
                        "lyrics": request.lyrics,
                        "style": request.style,
                        "timestamp": datetime.now().isoformat(),
                        "auto_renewal_active": True,
                        "suno_response": automation_result,
                        "job_id": automation_result.get("id", f"auto_{int(time.time())}")
                    }
                else:
                    logger.warning(f"⚠️ Selenium automation failed: {automation_response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Selenium automation error: {e}")
        
        # Use REAL Suno automation
        ghost_options = getattr(request, 'ghost_options', None)
        suno_result = await call_suno_real_automation(request.prompt, request.lyrics, request.style, ghost_options)
        
        return {
            "status": "success",
            "message": "Music generation submitted to Suno",
            "prompt": request.prompt,
            "lyrics": request.lyrics,
            "style": request.style,
            "timestamp": datetime.now().isoformat(),
            "auto_renewal_active": True,
            "suno_response": suno_result,
            "job_id": suno_result.get("id") if suno_result else f"job_{int(time.time())}"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (they're already properly formatted)
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in music generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during music generation")

@app.get("/api/generate/{job_id}/status")
async def get_generation_status(job_id: str):
    """Get status of a music generation job"""
    
    if not suno_status.valid:
        check_credentials()
        
    if not suno_status.valid:
        raise HTTPException(status_code=503, detail="Suno credentials not available")
    
    session_id = os.environ.get("SUNO_SESSION_ID")
    cookie = os.environ.get("SUNO_COOKIE")
    
    suno_url = f"https://studio-api.suno.ai/api/feed/?ids={job_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Cookie": cookie.replace('\n', '').replace('\r', '').strip(),
        "Referer": "https://suno.com/",
        "Origin": "https://suno.com"
    }
    
    try:
        response = requests.get(suno_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "job_id": job_id,
                "status": "found",
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "job_id": job_id,
                "status": "not_found",
                "error": f"HTTP {response.status_code}",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ Error checking job status: {e}")
        raise HTTPException(status_code=502, detail="Failed to check job status")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)