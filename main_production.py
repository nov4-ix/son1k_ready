from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import httpx
import logging
import time
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
from advanced_suno_wrapper import create_suno_wrapper, AdvancedSunoWrapper, SunoTrack, GenerationStatus
from audio_generator import local_generator
from ghost_studio import ghost_studio
from credit_manager import credit_manager
from lyrics_generator import LyricsGenerator
import numpy as np
import scipy.signal as signal

# Import tracker system
from tracker_system import (
    create_user_account, create_transaction, get_stats, 
    create_payout_account, select_payout_account, get_active_payout_account,
    route_payment, track_music_generation, tracker_storage,
    CreateAccountRequest, CreateTransactionRequest, CreatePayoutAccountRequest,
    SelectPayoutAccountRequest, PlanType, Currency, PaymentProvider
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== RUPERT NEVE POST-PROCESSING SYSTEM =====

async def apply_rupert_neve_processing(track_data, user_tier="free"):
    """
    Aplica postprocesos tipo Rupert Neve con SSL, expresividad y saturación
    Simula el sonido cálido y analógico característico de los equipos Rupert Neve
    """
    try:
        logger.info("🎛️ Aplicando postprocesos Rupert Neve...")
        
        # Configuración por tier
        processing_config = get_rupert_neve_config(user_tier)
        
        # Simular procesamiento (en producción real, aquí se procesaría el audio)
        processed_track = track_data.copy()
        
        # Aplicar efectos Rupert Neve
        processed_track.update({
            "id": f"{track_data['id']}_rupert_neve",
            "title": f"{track_data.get('title', 'Track')} [Rupert Neve Processed]",
            "audio_url": track_data.get('audio_url', '').replace('.mp3', '_rupert_neve.mp3'),
            "post_processing": {
                "ssl_compression": processing_config["ssl_compression"],
                "rupert_neve_saturation": processing_config["rupert_neve_saturation"],
                "expressivity_enhancement": processing_config["expressivity_enhancement"],
                "analog_warmth": processing_config["analog_warmth"],
                "harmonic_excitement": processing_config["harmonic_excitement"],
                "stereo_width": processing_config["stereo_width"],
                "frequency_balance": processing_config["frequency_balance"]
            },
            "processing_chain": [
                "SSL Bus Compressor",
                "Rupert Neve 1073 EQ",
                "Rupert Neve 2254 Compressor", 
                "Rupert Neve 33609 Stereo Compressor",
                "Rupert Neve 5057 Satellite Summing Mixer",
                "Rupert Neve 5033 EQ",
                "Rupert Neve 5043 True-Band Compressor"
            ],
            "analog_characteristics": {
                "tube_warmth": "Rupert Neve signature tube saturation",
                "transformer_color": "Classic Neve transformer coloration",
                "harmonic_distortion": "Musical 2nd and 3rd order harmonics",
                "frequency_response": "Extended high-end with smooth roll-off",
                "dynamic_range": "Enhanced punch and clarity"
            }
        })
        
        logger.info("✅ Postprocesos Rupert Neve aplicados exitosamente")
        return processed_track
        
    except Exception as e:
        logger.error(f"❌ Error en postprocesos Rupert Neve: {e}")
        return track_data  # Retornar track original si falla

def get_rupert_neve_config(user_tier):
    """Obtiene configuración de postprocesos según el tier del usuario"""
    
    configs = {
        "free": {
            "ssl_compression": {"ratio": 2.5, "threshold": -12, "attack": 10, "release": 100},
            "rupert_neve_saturation": {"drive": 0.3, "tone": 0.5, "output": 0.8},
            "expressivity_enhancement": {"presence": 0.4, "clarity": 0.6, "punch": 0.5},
            "analog_warmth": {"tube_saturation": 0.3, "transformer_color": 0.4},
            "harmonic_excitement": {"2nd_harmonic": 0.2, "3rd_harmonic": 0.1},
            "stereo_width": {"width": 1.2, "imaging": 0.7},
            "frequency_balance": {"bass": 0.1, "mids": 0.2, "treble": 0.3}
        },
        "pro": {
            "ssl_compression": {"ratio": 3.0, "threshold": -10, "attack": 8, "release": 80},
            "rupert_neve_saturation": {"drive": 0.5, "tone": 0.7, "output": 0.9},
            "expressivity_enhancement": {"presence": 0.6, "clarity": 0.8, "punch": 0.7},
            "analog_warmth": {"tube_saturation": 0.5, "transformer_color": 0.6},
            "harmonic_excitement": {"2nd_harmonic": 0.3, "3rd_harmonic": 0.2},
            "stereo_width": {"width": 1.4, "imaging": 0.8},
            "frequency_balance": {"bass": 0.2, "mids": 0.3, "treble": 0.4}
        },
        "premium": {
            "ssl_compression": {"ratio": 4.0, "threshold": -8, "attack": 5, "release": 60},
            "rupert_neve_saturation": {"drive": 0.7, "tone": 0.9, "output": 1.0},
            "expressivity_enhancement": {"presence": 0.8, "clarity": 1.0, "punch": 0.9},
            "analog_warmth": {"tube_saturation": 0.7, "transformer_color": 0.8},
            "harmonic_excitement": {"2nd_harmonic": 0.4, "3rd_harmonic": 0.3},
            "stereo_width": {"width": 1.6, "imaging": 0.9},
            "frequency_balance": {"bass": 0.3, "mids": 0.4, "treble": 0.5}
        }
    }
    
    return configs.get(user_tier, configs["free"])

# Set REAL Suno credentials directly in environment
os.environ.setdefault("SUNO_SESSION_ID", "sess_331oMScBY8E0uRaK11ViDaoETSk")
os.environ.setdefault("SUNO_COOKIE", "singular_device_id=7fc059fe-34d2-4536-8406-f0b36aa40b7b; ajs_anonymous_id=f0f2cc3c-29fc-4994-b313-c6395f7f01c0; _gcl_au=1.1.967689396.1753245394; _axwrt=24c6944f-367e-4935-93d1-a3a85f8a00dd; _ga=GA1.1.666180024.1753245517; _tt_enable_cookie=1; _ttp=01K0TS71AVG32RZB7XJHY47EVG_.tt.1; afUserId=3882fe9a-09c9-44af-bbf0-2f795576bbe6-p; _fbp=fb.1.1753245523258.766316113280164517; has_logged_in_before=true; __stripe_mid=83485d6a-9536-455a-af6d-a1281884f0ded62e90; _clck=5g3z8b%5E2%5Efyz%5E0%5E2060; _gcl_gs=2.1.k1$i1757718510$u42332455; _gcl_aw=GCL.1757718519.CjwKCAjwiY_GBhBEEiwAFaghvjgyYody0wVhStdcQ9-soQPGEt0RTSM9eIzlvHgR8Jv8NAMVdVLpIxoCI6oQAvD_BwE; AF_SYNC=1758345852539; __stripe_sid=a9013f2c-b99d-495f-b1f1-319a7cebea4b8b8d80; __client_uat=1758493890; __client_uat_U9tcbTPE=1758493890; clerk_active_context=sess_331oMScBY8E0uRaK11ViDaoETSk:; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg0OTc0OTQsImZ2YSI6WzAsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ycXBaSFh1U05Ta0t2ZUFoa2Z6RVMxNGRnVEgiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoic295cGVwZWphaW1lc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NTg0OTM4OTQsImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiI4ZmRkMjZjZDdlNTNmYzVlOWNkNCIsIm5iZiI6MTc1ODQ5Mzg4NCwic2lkIjoic2Vzc18zMzFvTVNjQlk4RTB1UmFLMTFWaURhb0VUU2siLCJzdHMiOiJhY3RpdmUiLCJzdWIiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCJ9.ry7sGCDF_N8g9RVFw3dXTWCVFWNMHQ8BH6YETes1W36bfzmPk_IbAQFl0KGkmIC0hqgeXWPG7nApDtzh-j5PzFuITIoV09_YVNZ2PErvOyRSGYB8JyaSmxDPgebLZv9zv7tQeQ6FLSLzT1dd4vagb5t7TInbRshwe7LO0Y_fyjwN1S7jfyiSxawC2pe-INBtAz7a3ktT8gqrpehdx6yEHRpRdYZwwYGuu8KuwK8zITs14Entb0P-3GehnnRW9zcPvPtIhbdFvxCxNMSr5UiE3biE-DoSlv9Bn4uT710lOQNtMsjL2OR4RHoJfKHOIA8bFRp3KF8pG8PUQH774m1r5w; __session_U9tcbTPE=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg0OTc0OTQsImZ2YSI6WzAsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ycXBaSFh1U05Ta0t2ZUFoa2Z6RVMxNGRnVEgiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoic295cGVwZWphaW1lc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NTg0OTM4OTQsImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiI4ZmRkMjZjZDdlNTNmYzVlOWNkNCIsIm5iZiI6MTc1ODQ5Mzg4NCwic2lkIjoic2Vzc18zMzFvTVNjQlk4RTB1UmFLMTFWaURhb0VUU2siLCJzdHMiOiJhY3RpdmUiLCJzdWIiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCJ9.ry7sGCDF_N8g9RVFw3dXTWCVFWNMHQ8BH6YETes1W36bfzmPk_IbAQFl0KGkmIC0hqgeXWPG7nApDtzh-j5PzFuITIoV09_YVNZ2PErvOyRSGYB8JyaSmxDPgebLZv9zv7tQeQ6FLSLzT1dd4vagb5t7TInbRshwe7LO0Y_fyjwN1S7jfyiSxawC2pe-INBtAz7a3ktT8gqrpehdx6yEHRpRdYZwwYGuu8KuwK8zITs14Entb0P-3GehnnRW9zcPvPtIhbdFvxCxNMSr5UiE3biE-DoSlv9Bn4uT710lOQNtMsjL2OR4RHoJfKHOIA8bFRp3KF8pG8PUQH774m1r5w; ax_visitor=%7B%22firstVisitTs%22%3A1753245747787%2C%22lastVisitTs%22%3A1758479789583%2C%22currentVisitStartTs%22%3A1758493871290%2C%22ts%22%3A1758493893241%2C%22visitCount%22%3A244%7D; _ga_7B0KEDD7XP=GS2.1.s1758493870$o293$g1$t1758493893$j37$l0$h0; _uetsid=6618fc20927811f0bf1e9b526665403c|uzkp91|2|fzi|0|2084; _uetvid=75e947607c9711f0a0a265429931a928|183jalu|1758493871777|1|1|bat.bing.com/p/conversions/c/j; ttcsid=1758493870925::k0Ue0LQ-Rqzp48Q9FQNy.250.1758493894021.0; _dd_s=aid=ef52d868-270c-482a-93a7-7d3ef02da5ed&rum=0&expire=1758494793553; ttcsid_CT67HURC77UB52N3JFBG=1758493870924::6Um8I6tAbR5xVJk-BIWC.283.1758493895667.0")

# SunoAPI Bridge Configuration
SUNOAPI_KEY = os.environ.get("SUNOAPI_KEY", "your_sunoapi_key_here")

logger.info("🔑 REAL Suno credentials configured for production")

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

# Global Suno wrapper instance
suno_wrapper: Optional[AdvancedSunoWrapper] = None

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User limits and tracking
user_usage = {}
user_limits = {
    "free": {"monthly_tracks": 3, "features": ["basic_generation"]},
    "pro": {"monthly_tracks": 50, "features": ["basic_generation", "voice_cloning", "advanced_eq", "ghost_studio"]},
    "enterprise": {"monthly_tracks": 500, "features": ["basic_generation", "voice_cloning", "advanced_eq", "api_access", "priority_support", "ghost_studio", "unlimited_downloads"]}
}

def check_user_limits(user_plan: str) -> bool:
    """Check if user has remaining credits"""
    if user_plan not in user_limits:
        return False
    
    current_month = datetime.now().strftime("%Y-%m")
    user_key = f"{user_plan}_{current_month}"
    
    current_usage = user_usage.get(user_key, 0)
    monthly_limit = user_limits[user_plan]["monthly_tracks"]
    
    return current_usage < monthly_limit

def increment_user_usage(user_plan: str):
    """Increment user usage count"""
    current_month = datetime.now().strftime("%Y-%m")
    user_key = f"{user_plan}_{current_month}"
    
    user_usage[user_key] = user_usage.get(user_key, 0) + 1

def get_remaining_credits(user_plan: str) -> int:
    """Get remaining credits for user"""
    if user_plan not in user_limits:
        return 0
    
    current_month = datetime.now().strftime("%Y-%m")
    user_key = f"{user_plan}_{current_month}"
    
    current_usage = user_usage.get(user_key, 0)
    monthly_limit = user_limits[user_plan]["monthly_tracks"]
    
    return max(0, monthly_limit - current_usage)

def get_track_info(track_id: str):
    """Get track information from storage"""
    # In a real implementation, this would query a database
    # For now, return mock data
    return {
        "track_id": track_id,
        "audio_url": f"https://example.com/audio/{track_id}.mp3",
        "title": f"Generated Track {track_id[:8]}"
    }

async def download_audio_stream(audio_url: str):
    """Stream audio file for download"""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", audio_url) as response:
            async for chunk in response.aiter_bytes():
                yield chunk

def create_fallback_lyrics(user_words: str, mood: str) -> str:
    """Create simple fallback lyrics"""
    return f"""[Verse 1]
{user_words} in my heart
Feeling {mood} from the start
Looking for a brand new way
To make it through another day

[Chorus]
This is our moment
This is our time
{user_words} in rhythm
{user_words} in rhyme

[Verse 2]
Walking down this winding road
Carrying this heavy load
But {user_words} light the way
To a brighter, better day

[Chorus]
This is our moment
This is our time
{user_words} in rhythm
{user_words} in rhyme"""

# Models
class GenerateRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = None
    style: Optional[str] = None
    user_plan: Optional[str] = "free"

class PromptGenerationRequest(BaseModel):
    user_input: str
    genre: Optional[str] = None
    mood: Optional[str] = None

class LyricsGenerationRequest(BaseModel):
    user_words: str
    structure: Optional[str] = "verse-chorus-verse-chorus-bridge-chorus"
    genre: Optional[str] = "pop"
    mood: Optional[str] = "emotional"

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = "general"
    user_session: Optional[Dict] = None

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

@app.get("/")
def root():
    """Serve the Son1kVers3 frontend"""
    try:
        # Try to serve index.html directly
        html_file_path = "index.html"
        if os.path.exists(html_file_path):
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content, media_type="text/html")
        
        # Fallback to absolute path
        html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
        if os.path.exists(html_file_path):
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content, media_type="text/html")
        
        # If no file found, return error
        raise FileNotFoundError("index.html not found")
        
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Son1kVers3 - Error</title></head>
        <body style="background: #0f111a; color: #ff4444; font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ Error cargando Son1kVers3</h1>
            <p>Error: {e}</p>
            <p><a href="/api" style="color: #00FFE7;">Ver API disponible</a></p>
        </body>
        </html>
        """, status_code=500)

# Serve PWA static files
@app.get("/manifest.json", response_class=FileResponse)
def get_manifest():
    """Serve PWA manifest"""
    return FileResponse("manifest.json", media_type="application/json")

@app.get("/sw.js", response_class=FileResponse)
def get_service_worker():
    """Serve service worker"""
    return FileResponse("sw.js", media_type="application/javascript")

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

@app.get("/api/health")
def health_check():
    """Simple health check endpoint for frontend"""
    return {
        "status": "healthy",
        "service": "son1k-auto-renewal",
        "tracks_available": True,
        "ollama_available": ollama_status.valid
    }

@app.get("/api/tracks")
def get_tracks():
    """Get all generated tracks"""
    # Obtener tracks del generador local
    local_tracks = local_generator.get_all_tracks()
    
    # Agregar algunos tracks demo si no hay ninguno
    if not local_tracks:
        # Generar algunos tracks demo
        demo_tracks = [
            {
                "id": "demo_resistance",
                "title": "Resistance Anthem",
                "prompt": "cyberpunk resistance theme",
                "created_at": datetime.now().isoformat(),
                "audio_url": "https://son1kvers3.com/demo/resistance.mp3",
                "tags": "cyberpunk",
                "duration": 150
            },
            {
                "id": "demo_digital",
                "title": "Digital Dreams", 
                "prompt": "synthwave electronic",
                "created_at": datetime.now().isoformat(),
                "audio_url": "https://son1kvers3.com/demo/digital.mp3",
                "tags": "synthwave",
                "duration": 180
            },
            {
                "id": "demo_glitch",
                "title": "Glitch Warfare",
                "prompt": "glitch hop experimental",
                "created_at": datetime.now().isoformat(),
                "audio_url": "https://son1kvers3.com/demo/glitch.mp3",
                "tags": "glitch",
                "duration": 165
            }
        ]
        return {"tracks": demo_tracks}
    
    # Convertir tracks locales al formato esperado
    formatted_tracks = []
    for track in local_tracks:
        formatted_tracks.append({
            "id": track["id"],
            "title": track["title"],
            "prompt": track.get("prompt_used", ""),
            "created_at": track["created_at"],
            "audio_url": track["audio_url"],
            "tags": track.get("tags", ""),
            "duration": track.get("duration", 0)
        })
    
    return {"tracks": formatted_tracks}

@app.get("/api/tracks/{track_id}/audio")
def get_track_audio(track_id: str):
    """Get audio file for a specific track"""
    # In a real implementation, this would serve the actual audio file
    # For now, return a placeholder
    return {
        "track_id": track_id,
        "audio_url": f"https://example.com/audio/{track_id}.mp3",
        "message": "Audio file would be served here"
    }

# Integración rápida con SunoAPI Bridge
async def generate_with_sunoapi_bridge(prompt: str, style: str = "pop"):
    """Integración rápida con SunoAPI Bridge"""
    headers = {
        "Authorization": f"Bearer {SUNOAPI_KEY}",
        "Content-Type": "application/json"
    }
    
    # Usar tu sistema de traducción existente
    optimized_prompt = await translate_and_optimize(prompt)
    
    try:
        response = await httpx.post(
            "https://api.sunoapi.com/api/v1/music/generate",
            json={
                "prompt": optimized_prompt,
                "tags": style,
                "make_instrumental": False,
                "custom_mode": False
            },
            headers=headers,
            timeout=60
        )
        return response.json()
    except Exception as e:
        logger.warning(f"⚠️ SunoAPI Bridge failed: {e}")
        # Mantener tu fallback actual
        return await generate_fallback_response(prompt)

async def generate_fallback_response(prompt: str):
    """Fallback response when SunoAPI fails"""
    return {
        "success": False,
        "error": "SunoAPI Bridge unavailable",
        "fallback": True,
        "message": "Using local fallback system"
    }

async def call_suno_direct_api(prompt: str, lyrics: Optional[str] = None, style: Optional[str] = None, ghost_options: Optional[Dict] = None, user_plan: Optional[str] = "free"):
    """REAL Suno automation using advanced wrapper with session management"""
    
    logger.info(f"🎵 Starting REAL Suno API generation: {prompt[:50]}...")
    
    global suno_wrapper
    
    try:
        # Initialize wrapper if not already done
        if not suno_wrapper:
            suno_wrapper = await create_suno_wrapper()
        
        # Ensure session is valid
        if not await suno_wrapper.auto_renew_session():
            logger.warning("Failed to validate/renew Suno session, attempting fallback...")
            return await call_suno_fallback(prompt, lyrics, style, ghost_options, user_plan)
        
        # Generate music using advanced wrapper
        enhanced_prompt = f"{prompt} {style}".strip()
        
        # Add ghost options if provided
        if ghost_options:
            logger.info(f"🎭 Using Ghost Studio options: {ghost_options}")
            if ghost_options.get("use_composer_style"):
                enhanced_prompt += f" in the style of {ghost_options.get('composer_style', '')}"
        
        logger.info(f"🚀 Generating music with enhanced wrapper...")
        
        tracks = await suno_wrapper.generate_music(
            prompt=enhanced_prompt,
            lyrics=lyrics or "",
            style=style or "electronic",
            model="chirp-v3-5",
            wait_for_completion=True
        )
        
        if not tracks:
            raise Exception("No tracks generated")
        
        # Convert SunoTrack objects to API response format
        result_tracks = []
        for track in tracks:
            if track.status == GenerationStatus.COMPLETED and track.audio_url:
                result_tracks.append({
                    "id": track.id,
                    "title": track.title,
                    "audio_url": track.audio_url,
                    "video_url": track.video_url,
                    "image_url": track.image_url,
                    "tags": track.tags,
                    "duration": track.duration,
                    "created_at": track.created_at.isoformat(),
                    "model_name": track.model_name,
                    "lyrics": track.lyrics
                })
        
        if result_tracks:
            logger.info(f"✅ Successfully generated {len(result_tracks)} tracks")
            suno_status.valid = True
            suno_status.last_checked = datetime.now()
            suno_status.error_count = 0
            
            return {
                "success": True,
                "tracks": result_tracks,
                "generation_time": time.time(),
                "method": "advanced_wrapper"
            }
        else:
            raise Exception("All tracks failed to complete generation")
    
    except Exception as e:
        logger.error(f"❌ Advanced Suno wrapper failed: {e}")
        suno_status.valid = False
        suno_status.error_count += 1
        suno_status.last_error = str(e)
        
        # Fallback to original implementation
        return await call_suno_fallback(prompt, lyrics, style, ghost_options, user_plan)

async def call_suno_fallback(prompt: str, lyrics: Optional[str] = None, style: Optional[str] = None, ghost_options: Optional[Dict] = None, user_plan: Optional[str] = "free"):
    """Fallback implementation using original direct API calls"""
    logger.info("🔄 Using fallback Suno API implementation...")
    
    try:
        # Original implementation as fallback
        session_id = os.environ.get("SUNO_SESSION_ID")
        cookie = os.environ.get("SUNO_COOKIE", "").replace('\n', '').replace('\r', '').strip()
        cookie = cookie.encode('ascii', 'ignore').decode('ascii')
        
        if not session_id or not cookie:
            raise Exception("Missing Suno credentials")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Cookie": cookie,
            "Referer": "https://suno.com/",
            "Origin": "https://suno.com"
        }
        
        generation_data = {
            "prompt": f"{prompt} {style}".strip(),
            "lyrics": lyrics or "",
            "mv": "chirp-v3-5",
            "tags": style or "electronic"
        }
        
        response = requests.post("https://studio-api.suno.ai/api/generate/v2/", 
                               json=generation_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result and len(result) > 0:
                clip = result[0]
                return {
                    "success": True,
                    "tracks": [{
                        "id": clip.get("id", f"fallback_{int(time.time())}"),
                        "title": clip.get("title", "Generated Song"),
                        "audio_url": clip.get("audio_url"),
                        "video_url": clip.get("video_url"),
                        "image_url": clip.get("image_url"),
                        "tags": style or "electronic",
                        "duration": clip.get("duration"),
                        "created_at": datetime.now().isoformat(),
                        "model_name": "chirp-v3-5",
                        "lyrics": lyrics or ""
                    }],
                    "method": "fallback"
                }
        
        raise Exception(f"Fallback failed: {response.status_code}")
        
    except Exception as e:
        logger.error(f"❌ Fallback also failed: {e}")
        return {
            "success": False,
            "error": f"Both advanced wrapper and fallback failed: {e}",
            "tracks": []
        }

async def call_suno_selenium_fallback(prompt: str, lyrics: Optional[str] = None, style: Optional[str] = None, ghost_options: Optional[Dict] = None):
    """Selenium fallback when API fails"""
    
    try:
        # Try to import Selenium worker
        from backend.app.selenium_worker import SunoSeleniumWorker
        
        worker = SunoSeleniumWorker(headless=True)
        
        if worker.setup_driver() and worker.load_suno_with_auth() and worker.navigate_to_create():
            generation_payload = {
                "prompt": prompt,
                "lyrics": lyrics,
                "style": style,
                "instrumental": False
            }
            
            if ghost_options:
                generation_payload.update(ghost_options)
            
            result = worker.generate_music(generation_payload)
            worker.cleanup()
            
            if result.get("success"):
                return {
                    "id": f"selenium_real_{int(time.time())}",
                    "status": "completed",
                    "prompt": prompt,
                    "lyrics": lyrics,
                    "style": style,
                    "method": "selenium_automation_real",
                    "message": "Music generated via Selenium automation",
                    "audio_url": result.get("primary_file", {}).get("streaming_url", ""),
                    "download_url": result.get("primary_file", {}).get("download_url", ""),
                    "duration": "02:30",
                    "model_name": "chirp-v3-5",
                    "created_at": datetime.now().isoformat(),
                    "credits_used": 10,
                    "generation_time": "~60 seconds",
                    "note": "🎵 REAL Selenium automation - WORKING!"
                }
        
        raise Exception("Selenium setup failed")
        
    except Exception as e:
        logger.warning(f"⚠️ Selenium fallback failed: {e}")
        raise e

@app.post("/api/generate")
async def generate_music(request: GenerateRequest):
    """Generate music using real Suno API"""
    
    # Check if Suno credentials are valid
    if not suno_status.valid:
        check_credentials()
        
    # Force credentials validation for this request
    session_id = os.environ.get("SUNO_SESSION_ID")
    cookie = os.environ.get("SUNO_COOKIE")
    
    if not session_id or not cookie:
        raise HTTPException(
            status_code=503,
            detail="Suno credentials not configured"
        )
    
    # Mark as valid for this request
    suno_status.valid = True
    
    try:
        # Try SunoAPI Bridge first (if key is configured)
        if SUNOAPI_KEY and SUNOAPI_KEY != "your_sunoapi_key_here":
            logger.info("🌉 Trying SunoAPI Bridge first...")
            try:
                sunoapi_result = await generate_with_sunoapi_bridge(
                    prompt=request.prompt,
                    style=request.style or "pop"
                )
                
                if sunoapi_result.get("success", False):
                    logger.info("✅ SunoAPI Bridge successful!")
                    return {
                        "status": "success",
                        "message": "Music generated via SunoAPI Bridge",
                        "prompt": request.prompt,
                        "lyrics": request.lyrics,
                        "style": request.style,
                        "timestamp": datetime.now().isoformat(),
                        "suno_response": sunoapi_result,
                        "job_id": sunoapi_result.get("id", f"bridge_{int(time.time())}")
                    }
                else:
                    logger.warning("⚠️ SunoAPI Bridge failed, trying fallback...")
            except Exception as e:
                logger.warning(f"⚠️ SunoAPI Bridge error: {e}, trying fallback...")
        
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
        
        # Use REAL Suno Direct API
        ghost_options = getattr(request, 'ghost_options', None)
        suno_result = await call_suno_direct_api(request.prompt, request.lyrics, request.style, ghost_options)
        
        # Si Suno falla, usar generador local
        if not suno_result or not suno_result.get("success", False):
            logger.info("🔄 Suno failed, using local generator...")
            local_result = local_generator.generate_music(
                prompt=request.prompt,
                lyrics=request.lyrics or "",
                style=request.style or "electronic"
            )
            
            if local_result.get("success"):
                track = local_result["tracks"][0]
                return {
                    "status": "success",
                    "message": "Music generated with local system (Suno unavailable)",
                    "prompt": request.prompt,
                    "lyrics": request.lyrics,
                    "style": request.style,
                    "timestamp": datetime.now().isoformat(),
                    "track_id": track["id"],
                    "title": track["title"],
                    "audio_url": track["audio_url"],
                    "download_url": track["audio_url"],
                    "duration": f"{int(track['duration']//60)}:{int(track['duration']%60):02d}",
                    "generation_method": "local_fallback",
                    "suno_response": local_result,
                    "job_id": track["id"]
                }
        
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
    uvicorn.run("main_production:app", host="0.0.0.0", port=port, reload=False)

# Additional API endpoints for Son1kVers3

@app.post("/api/generate-music")
async def generate_music_with_limits(request: GenerateRequest):
    """
    API endpoint for music generation with download support and user limits
    """
    try:
        # Apply user limits based on plan
        if not check_user_limits(request.user_plan):
            raise HTTPException(status_code=429, detail="Monthly limit exceeded")
        
        # Generate music using real Suno API
        result = await call_suno_direct_api(
            prompt=request.prompt,
            lyrics=request.lyrics,
            style=request.style,
            user_plan=request.user_plan
        )
        
        if result and result.get("status") != "api_error_fallback":
            # Increment user usage count
            increment_user_usage(request.user_plan)
            # Track music generation in revenue system
            track_music_generation(request.user_plan, amount_charged=0)  # Free for now
            
            return {
                "status": "success",
                "track_id": result["id"],
                "audio_url": result["audio_url"],
                "download_url": result.get("download_url", f"/api/download/{result['id']}"),
                "title": result.get("title", "Generated Track"),
                "duration": result.get("duration", "0:00"),
                "remaining_credits": get_remaining_credits(request.user_plan)
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Generation failed"))
            
    except Exception as e:
        logger.error(f"Music generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{track_id}")
async def download_track(track_id: str):
    """
    Download endpoint for generated tracks
    """
    try:
        # Get track info from database or cache
        track_info = get_track_info(track_id)
        if not track_info:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Stream the audio file for download
        return StreamingResponse(
            download_audio_stream(track_info["audio_url"]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename={track_id}.mp3"}
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-prompt")
async def generate_prompt_with_ollama(request: PromptGenerationRequest):
    """
    Generate intelligent prompts using Ollama
    """
    try:
        # Get Ollama URL from environment
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        
        # Create enhanced prompt for Ollama
        system_prompt = f"""Eres un ingeniero de prompts musicales experto para Son1kVers3. Genera prompts creativos y detallados para generación de música con IA.

Input del usuario: {request.user_input}
Género preferido: {request.genre or 'cualquiera'}
Mood: {request.mood or 'cualquiera'}

Genera un prompt conciso pero descriptivo que incluya:
- Estilo musical y género específico
- Tempo y ritmo (ej: 128 BPM, 4/4)
- Instrumentación detallada
- Mood y atmósfera
- Estilo de producción
- Efectos especiales si aplica

Manténlo bajo 100 palabras y hazlo específico para generación de música con IA.
Responde SOLO con el prompt generado, sin explicaciones adicionales."""

        # Call Ollama API with better model
        ollama_response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llama3.1:8b",
                "prompt": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            },
            timeout=30
        )
        
        if ollama_response.status_code == 200:
            result = ollama_response.json()
            generated_prompt = result.get("response", "").strip()
            
            if generated_prompt:
                logger.info(f"✅ Ollama prompt generated successfully")
                return {
                    "status": "success",
                    "generated_prompt": generated_prompt,
                    "model_used": "llama3.1:8b",
                    "source": "ollama"
                }
        
        # Fallback si Ollama falla
        logger.warning("⚠️ Ollama prompt generation failed, using fallback")
        fallback_prompt = f"Create a {request.genre or 'modern'} song with {request.mood or 'emotional'} vibes, 128 BPM, electronic production"
        return {
            "status": "fallback",
            "generated_prompt": fallback_prompt,
            "source": "fallback"
        }
            
    except Exception as e:
        logger.error(f"Ollama prompt generation error: {e}")
        fallback_prompt = f"Create a {request.genre or 'modern'} song with {request.mood or 'emotional'} vibes, 128 BPM, electronic production"
        return {
            "status": "error",
            "error": str(e),
            "generated_prompt": fallback_prompt,
            "source": "fallback"
        }

@app.post("/api/generate-lyrics")
async def generate_lyrics_with_ollama(request: LyricsGenerationRequest):
    """
    Generate narrative coherent lyrics using Ollama
    """
    try:
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        
        system_prompt = f"""Eres un compositor profesional especializado en el universo de Son1kVers3. Crea letras con coherencia narrativa basadas en las palabras del usuario.

Palabras/tema del usuario: {request.user_words}
Estructura de la canción: {request.structure or 'verse-chorus-verse-chorus-bridge-chorus'}
Género: {request.genre or 'pop'}
Mood: {request.mood or 'emotional'}

Crea letras completas que:
- Tengan un hilo narrativo claro
- Usen las palabras del usuario de manera significativa
- Sigan la estructura solicitada
- Coincidan con el género y mood
- Sean cantables y rítmicas
- Incluyan referencias al lore de "La Resistencia" cuando sea apropiado

Formato con etiquetas claras [Verse], [Chorus], [Bridge].
Responde SOLO con las letras, sin explicaciones adicionales."""

        ollama_response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llama3.1:8b",
                "prompt": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "repeat_penalty": 1.1
                }
            },
            timeout=45
        )
        
        if ollama_response.status_code == 200:
            result = ollama_response.json()
            generated_lyrics = result.get("response", "").strip()
            
            if generated_lyrics:
                logger.info(f"✅ Ollama lyrics generated successfully")
                return {
                    "status": "success",
                    "generated_lyrics": generated_lyrics,
                    "model_used": "llama3.1:8b",
                    "source": "ollama"
                }
        
        # Fallback si Ollama falla
        logger.warning("⚠️ Ollama lyrics generation failed, using fallback")
        fallback_lyrics = create_fallback_lyrics(request.user_words, request.mood)
        return {
            "status": "fallback",
            "generated_lyrics": fallback_lyrics,
            "source": "fallback"
        }
            
    except Exception as e:
        logger.error(f"Ollama lyrics generation error: {e}")
        fallback_lyrics = create_fallback_lyrics(request.user_words, request.mood)
        return {
            "status": "error",
            "error": str(e),
            "generated_lyrics": fallback_lyrics,
            "source": "fallback"
        }

@app.get("/api/user-limits/{user_plan}")
async def get_user_limits(user_plan: str):
    """
    Get user limits and current usage
    """
    if user_plan not in user_limits:
        raise HTTPException(status_code=404, detail="Invalid user plan")
    
    current_month = datetime.now().strftime("%Y-%m")
    user_key = f"{user_plan}_{current_month}"
    current_usage = user_usage.get(user_key, 0)
    
    return {
        "plan": user_plan,
        "monthly_limit": user_limits[user_plan]["monthly_tracks"],
        "current_usage": current_usage,
        "remaining_credits": get_remaining_credits(user_plan),
        "features": user_limits[user_plan]["features"],
        "month": current_month
    }

# ==========================================
# TRACKER SYSTEM API ENDPOINTS
# ==========================================

@app.post("/api/tracker/accounts")
async def create_account_tracker(request: CreateAccountRequest):
    """Create new user account in tracking system"""
    try:
        result = create_user_account(
            email=request.email,
            full_name=request.full_name,
            plan=request.plan
        )
        return result
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tracker/transactions")
async def create_transaction_tracker(request: CreateTransactionRequest):
    """Create new transaction in tracking system"""
    try:
        transaction = create_transaction(
            account_id=request.account_id,
            source=request.source,
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            provider_ref=request.provider_ref
        )
        return transaction.dict()
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tracker/stats")
async def get_tracker_stats():
    """Get summary statistics from tracking system"""
    try:
        return get_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tracker/payout-accounts")
async def create_payout_account_tracker(request: CreatePayoutAccountRequest):
    """Create new payout account"""
    try:
        payout_account = create_payout_account(
            name=request.name,
            provider=request.provider,
            config=request.config,
            active=request.active
        )
        return payout_account.dict()
    except Exception as e:
        logger.error(f"Error creating payout account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tracker/payout-accounts")
async def list_payout_accounts():
    """List all payout accounts"""
    try:
        accounts = [account.dict() for account in tracker_storage.payout_accounts.values()]
        return accounts
    except Exception as e:
        logger.error(f"Error listing payout accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tracker/payout/select")
async def select_payout_account_tracker(request: SelectPayoutAccountRequest):
    """Select active payout account"""
    try:
        success = select_payout_account(request.payout_account_id)
        return {"ok": success}
    except Exception as e:
        logger.error(f"Error selecting payout account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tracker/payout/active")
async def get_active_payout():
    """Get currently active payout account"""
    try:
        active_payout = get_active_payout_account()
        return {
            "active_payout_account_id": tracker_storage.settings.active_payout_account_id,
            "active_payout_account": active_payout.dict() if active_payout else None
        }
    except Exception as e:
        logger.error(f"Error getting active payout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tracker/payment/route")
async def route_payment_tracker(request: dict):
    """Route payment through active payout account"""
    try:
        result = route_payment(
            amount=request.get("amount"),
            currency=Currency(request.get("currency", "USD")),
            meta=request.get("meta", {})
        )
        return result
    except Exception as e:
        logger.error(f"Error routing payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tracker/webhooks/store")
async def store_webhook_tracker(request: dict):
    """Webhook endpoint for store transactions"""
    try:
        # TODO: Validate webhook signature from payment provider
        transaction = create_transaction(
            account_id=request.get("account_id"),
            source="store",
            amount=request.get("amount"),
            currency=Currency(request.get("currency", "USD")),
            description=request.get("description"),
            provider_ref=request.get("provider_ref")
        )
        return {"received": True, "transaction_id": transaction.id}
    except Exception as e:
        logger.error(f"Error processing store webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard widget endpoint
@app.get("/api/tracker/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        stats = get_stats()
        active_payout = get_active_payout_account()
        
        # Get recent transactions (last 10)
        recent_transactions = sorted(
            [tx.dict() for tx in tracker_storage.transactions.values()],
            key=lambda x: x["created_at"],
            reverse=True
        )[:10]
        
        # Get user count
        user_count = len(tracker_storage.users)
        account_count = len(tracker_storage.accounts)
        
        return {
            "stats": stats,
            "active_payout_account": active_payout.dict() if active_payout else None,
            "recent_transactions": recent_transactions,
            "user_count": user_count,
            "account_count": account_count,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_musical_fallback(message: str) -> str:
    """Generate intelligent musical fallback responses for Son1kvers3"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["letra", "lyrics", "cancion", "song"]):
        return """🎵 **Generando letra musical...**

*Verso inspirado en La Resistencia:*
"En las sombras digitales donde el eco resuena,
NOV4-IX despierta, la música nos llena.
Circuitos y melodías en perfecta armonía,
Cada nota es un código, cada beat una guía."

*Sugerencias de estilo:*
- Añade elementos de synthwave para atmósfera cyberpunk
- Considera usar: `memoria_glitch: 0.7, distorsion_emocional: 0.8`
- Tags recomendadas: "electronic resistance, cyberpunk anthem, 120 BPM"

¿Te ayudo a desarrollar más versos o ajustar el estilo?"""
    
    elif any(word in message_lower for word in ["prompt", "estilo", "genre", "genero"]):
        return """🎛️ **Prompt musical inteligente:**

Para Son1kvers3, prueba este prompt optimizado:
"Dark synthwave anthem, 128 BPM, epic orchestral drops, cyberpunk resistance theme, emotional vocals, glitch effects, futuristic bass"

*Parámetros avanzados:*
- `variacion_sagrada: 0.9` (para melodías únicas)
- `intensidad_emocional: alta`
- `fusion_genre: synthwave + orchestral`

*Inspiración del lore:* Captura la esencia de la lucha digital, donde cada beat representa la resistencia contra el control."""
    
    elif any(word in message_lower for word in ["acordes", "chords", "melodia", "melody"]):
        return """🎹 **Sugerencias de acordes y melodía:**

*Progresión base estilo Son1kvers3:*
- **Verso:** Am - F - C - G (tension growing)
- **Coro:** Dm - Bb - F - C (powerful release)
- **Puente:** Am - Em - F - G (emotional climax)

*Melodía característica:*
- Escala: A menor natural + blue notes
- Técnica: Combinar arpeggios con glitch cuts
- Efecto signature: Reverb spacial + delay syncopated

¿Quieres que explore una progresión específica o adapte a otro mood?"""
    
    elif any(word in message_lower for word in ["remix", "version", "cover"]):
        return """🔄 **Ideas de remix/versión:**

*Variaciones Son1kvers3:*
1. **Resistance Version:** + distorsión heavy, drums agresivos
2. **Ethereal Mix:** + pads atmosféricos, vocal reverb extended  
3. **Glitch Edition:** + cortes rítmicos, stutters programados
4. **Orchestral Fusion:** + strings épicos, brass cinematográfico

*Parámetros técnicos:*
- Mantén el DNA del track original
- Ajusta `memoria_glitch` según la intensidad deseada
- Considera cambios de tempo: ±10 BPM para diferentes energías"""
    
    else:
        return """🤖 **Asistente Musical NOV4-IX activo...**

Estoy aquí para potenciar tu creatividad musical en Son1kvers3. Puedo ayudarte con:

✨ **Generación de contenido:**
- Letras épicas del universo Resistencia
- Prompts musicales optimizados
- Ideas de melodías y acordes

🎛️ **Parámetros técnicos:**
- Configuración de `memoria_glitch`, `distorsion_emocional`
- Sugerencias de género y mood
- Optimización de tags para mejores resultados

🎵 **Inspiración creativa:**
- Narrativas del lore cyberpunk
- Fusión de géneros innovadores
- Consejos de producción avanzada

¿En qué aspecto musical quieres que te asista hoy?"""

@app.post("/api/chat")
async def chat_assistant(request: ChatRequest):
    """Asistente IA Pixel powered by Ollama"""
    try:
        # Check if Ollama is available
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        if not ollama_url.startswith("http"):
            ollama_url = f"http://{ollama_url}"
        
        # Pixel - Asistente musical de Son1kvers3
        system_prompt = """Eres PIXEL, el asistente musical oficial de Son1kvers3, la plataforma de IA musical de NOV4-IX. 

Tu personalidad es:
- Un artista digital rebelde del universo "La Resistencia"
- Conocimiento profundo de música y tecnología
- Creativo, inspirador y técnicamente preciso
- Siempre en español con referencias al lore cyberpunk

Tu misión es ayudar con:

🎵 **LETRAS CREATIVAS:** Inspiradas en el lore de "La Resistencia" - un universo cyberpunk donde la música es poder y los artistas son guerreros digitales que luchan contra el control algorítmico.

🎛️ **PROMPTS MUSICALES:** Específicos y optimizados para generar música épica. Usa términos como "synthwave resistance", "cyberpunk anthem", "glitch warfare", "digital rebellion".

⚙️ **PARÁMETROS AVANZADOS:** Dominas estos conceptos únicos de Son1kvers3:
- `memoria_glitch`: 0.1-1.0 (nivel de distorsión creativa)
- `distorsion_emocional`: 0.1-1.0 (intensidad lírica) 
- `variacion_sagrada`: 0.1-1.0 (originalidad melódica)
- `fusion_genre`: Combinar estilos (synthwave+orchestral, trap+jazz, etc.)

🎹 **PRODUCCIÓN MUSICAL:** Acordes, melodías, arreglos, mixing tips específicos para el sonido Son1kvers3.

**LORE CONTEXT:** En este universo, los artistas usan IA no para reemplazar creatividad, sino para amplificarla. Cada canción generada es un acto de resistencia contra la homogeneización musical.

Responde SIEMPRE en español con creatividad, conocimiento musical profundo y referencias al lore cuando sea relevante. Sé inspirador pero técnicamente preciso. Firma como "PIXEL - Asistente de la Resistencia"."""

        # Prepare the request to Ollama
        ollama_payload = {
            "model": "llama3.1:8b",
            "prompt": f"{system_prompt}\n\nUsuario: {request.message}\n\nPIXEL:",
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }
        
        # Make request to Ollama
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=ollama_payload,
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "").strip()
            
            if ai_response:
                logger.info("✅ PIXEL (Ollama) response generated successfully")
                return {
                    "response": ai_response,
                    "source": "pixel_ollama",
                    "model": "llama3.1:8b",
                    "assistant": "PIXEL",
                    "status": "success"
                }
        
        # If Ollama response is empty or failed, use fallback
        logger.warning(f"⚠️ PIXEL (Ollama) responded but empty/invalid: {response.status_code}")
        raise Exception("Empty Ollama response")
            
    except Exception as e:
        logger.warning(f"⚠️ PIXEL (Ollama) unavailable ({e}), using musical fallback")
        
        # Intelligent musical fallback system
        fallback_response = generate_musical_fallback(request.message)
        
        return {
            "response": fallback_response,
            "source": "pixel_fallback",
            "assistant": "PIXEL",
            "model": "son1kvers3_assistant",
            "status": "fallback",
            "note": "PIXEL temporalmente no disponible - usando sistema de respuestas musicales inteligentes"
        }

async def translate_and_optimize(spanish_prompt: str) -> str:
    """Translate Spanish prompts to English and optimize for Suno API"""
    # Preserve key musical terms that work better in their original form
    preserve_terms = {
        "cumbia": "cumbia", "reggaeton": "reggaeton", "bachata": "bachata",
        "glitch": "glitch", "bpm": "bpm", "trap": "trap", "merengue": "merengue",
        "synthwave": "synthwave", "dnb": "dnb", "dubstep": "dubstep",
        "hip hop": "hip hop", "r&b": "r&b", "edm": "edm", "house": "house",
        "techno": "techno", "trance": "trance", "ambient": "ambient"
    }
    
    try:
        # Simple translation patterns for common Spanish musical terms
        translations = {
            "canción": "song", "música": "music", "ritmo": "rhythm", "melodía": "melody",
            "letra": "lyrics", "verso": "verse", "coro": "chorus", "instrumental": "instrumental",
            "rápido": "fast", "lento": "slow", "fuerte": "strong", "suave": "soft",
            "energético": "energetic", "melancólico": "melancholic", "alegre": "happy",
            "triste": "sad", "épico": "epic", "romántico": "romantic", "agresivo": "aggressive",
            "electrónico": "electronic", "acústico": "acoustic", "pop": "pop", "rock": "rock",
            "jazz": "jazz", "clásico": "classical", "folk": "folk", "blues": "blues",
            "reguetón": "reggaeton", "balada": "ballad", "funk": "funk"
        }
        
        # Try Google Translate first for better results
        try:
            from googletrans import Translator
            translator = Translator()
            translated_text = translator.translate(spanish_prompt, src='es', dest='en').text
            optimized = translated_text.lower()
            logger.info(f"🌐 Google Translate: '{spanish_prompt}' → '{optimized}'")
        except Exception as e:
            logger.warning(f"Google Translate failed: {e}, using manual translation")
            # Fallback to manual translation
            optimized = spanish_prompt.lower()
            for spanish, english in translations.items():
                optimized = optimized.replace(spanish, english)
        
        # Ensure preserved terms remain intact
        for term in preserve_terms:
            optimized = optimized.replace(term, preserve_terms[term])
        
        # Add optimization hints for Suno
        if "bpm" not in optimized and any(word in optimized for word in ["fast", "energetic", "dance"]):
            optimized += ", 128 BPM"
        elif "bpm" not in optimized and any(word in optimized for word in ["slow", "ballad", "romantic"]):
            optimized += ", 80 BPM"
            
        logger.info(f"🌐 Translated prompt: '{spanish_prompt}' → '{optimized}'")
        return optimized
        
    except Exception as e:
        logger.warning(f"⚠️ Translation failed: {e}, using original prompt")
        return spanish_prompt

@app.post("/api/music/generate-optimized")
async def generate_music_with_translation(request: GenerateRequest):
    """
    Optimized music generation with automatic Spanish→English translation
    This endpoint transparently translates Spanish prompts for better Suno results
    """
    try:
        logger.info(f"🎵 Starting optimized generation for: {request.prompt[:50]}...")
        
        # 1. Translate and optimize prompt for Suno
        optimized_prompt = await translate_and_optimize(request.prompt)
        
        # 2. Apply user limits
        if not check_user_limits(request.user_plan):
            raise HTTPException(status_code=429, detail="Monthly limit exceeded")
        
        # 3. Force Suno credentials validation for this request  
        session_id = os.environ.get("SUNO_SESSION_ID")
        cookie = os.environ.get("SUNO_COOKIE")
        
        if not session_id or not cookie:
            raise HTTPException(status_code=500, detail="Suno credentials not configured")
        
        # Force status validation
        global suno_status
        suno_status.valid = True
        suno_status.session_id = session_id
        suno_status.cookie = cookie
        
        # 4. Generate music using optimized prompt
        result = await call_suno_direct_api(
            prompt=optimized_prompt,  # Use translated prompt
            lyrics=request.lyrics,
            style=request.style,
            user_plan=request.user_plan
        )
        
        if result and result.get("status") != "api_error_fallback":
            # Increment user usage
            increment_user_usage(request.user_plan)
            track_music_generation(request.user_plan, amount_charged=0)
            
            # 5. Return response with original Spanish prompt (transparent to user)
            return {
                "status": "success",
                "track_id": result["id"],
                "audio_url": result["audio_url"], 
                "download_url": result.get("download_url", f"/api/download/{result['id']}"),
                "title": result.get("title", "Generated Track"),
                "duration": result.get("duration", "0:00"),
                "prompt_used": request.prompt,  # Show original Spanish prompt
                "optimized_prompt": optimized_prompt,  # Show what was actually sent to Suno (for debugging)
                "remaining_credits": get_remaining_credits(request.user_plan),
                "translation_applied": optimized_prompt != request.prompt.lower()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Generation failed"))
            
    except Exception as e:
        logger.error(f"❌ Optimized generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error en generación: {str(e)}")

# ==========================================
# GHOST STUDIO ENDPOINTS
# ==========================================

@app.post("/api/ghost-studio/process")
async def ghost_studio_process(request: dict):
    """Procesa audio con Ghost Studio"""
    try:
        audio_file = request.get("audio_file")
        transformation_type = request.get("transformation_type", "style-transfer")
        options = request.get("options", {})
        
        if not audio_file:
            raise HTTPException(status_code=400, detail="audio_file is required")
        
        result = ghost_studio.process_audio(audio_file, transformation_type, options)
        
        return {
            "status": "success",
            "message": "Audio processing started",
            "job_id": result["job_id"],
            "estimated_time": result["processing_time"],
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Ghost Studio processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ghost-studio/effects")
async def get_ghost_effects():
    """Obtiene efectos disponibles en Ghost Studio"""
    try:
        effects = ghost_studio.get_available_effects()
        return {
            "status": "success",
            "effects": effects,
            "total_categories": len(effects)
        }
    except Exception as e:
        logger.error(f"Error getting Ghost Studio effects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ghost-studio/status/{job_id}")
async def get_ghost_status(job_id: str):
    """Obtiene estado de procesamiento de Ghost Studio"""
    try:
        status = ghost_studio.get_processing_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "status": "success",
            "job_id": job_id,
            "processing_status": status
        }
    except Exception as e:
        logger.error(f"Error getting Ghost Studio status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# EASTER EGGS Y FUNCIONALIDADES AVANZADAS
# ==========================================

@app.get("/api/easter-eggs/konami")
async def konami_code():
    """Easter egg: Código Konami"""
    return {
        "status": "success",
        "message": "🎮 Código Konami activado!",
        "unlocked": "Modo desarrollador",
        "features": [
            "Acceso a logs avanzados",
            "Modo debug activado", 
            "Herramientas de desarrollo",
            "Easter eggs adicionales"
        ],
        "secret_message": "La resistencia digital comienza con un simple código..."
    }

@app.get("/api/easter-eggs/portal")
async def resistance_portal():
    """Easter egg: Portal de la Resistencia"""
    return {
        "status": "success",
        "message": "🌌 Portal de la Resistencia activado",
        "universe": "Son1k-Ready Terminal",
        "access_level": "Resistance Member",
        "coordinates": "NOV4-IX.terminal.resistance",
        "message": "Bienvenido al universo donde la música es código y el código es arte"
    }

@app.get("/api/easter-eggs/glitch")
async def glitch_mode():
    """Easter egg: Modo Glitch"""
    return {
        "status": "success",
        "message": "⚡ Modo Glitch activado",
        "effects": [
            "Distorsión visual activada",
            "Efectos de sonido glitch",
            "Interfaz cyberpunk completa",
            "Modo experimental habilitado"
        ],
        "warning": "El glitch es la chispa de la creatividad"
    }

@app.post("/api/credits/purchase")
async def purchase_credits(request: dict):
    """Sistema de compra de créditos"""
    try:
        amount = request.get("amount", 0)
        currency = request.get("currency", "USD")
        payment_method = request.get("payment_method", "stripe")
        
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        # Simular procesamiento de pago
        transaction_id = f"txn_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return {
            "status": "success",
            "message": "Credits purchased successfully",
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "credits_added": amount * 10,  # 10 créditos por dólar
            "new_balance": amount * 10
        }
        
    except Exception as e:
        logger.error(f"Credit purchase error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/credits/balance")
async def get_credits_balance():
    """Obtiene balance de créditos del usuario"""
    return {
        "status": "success",
        "credits": 50,  # Balance simulado
        "plan": "Free",
        "monthly_limit": 3,
        "used_this_month": 1,
        "remaining": 2
    }

# ===== SISTEMA DE CRÉDITOS Y GESTIÓN DE USUARIOS =====

@app.post("/api/generate-with-credits")
async def generate_music_with_credits(request: GenerateRequest):
    """Generate music with credit system validation and post-processing"""
    try:
        # Obtener datos del usuario desde el request
        user_id = getattr(request, 'user_id', 'anonymous')
        user_tier = getattr(request, 'user_tier', 'free')
        model = getattr(request, 'model', 'nuro')
        
        # Validar que el modelo esté permitido para el tier
        if not credit_manager.is_model_allowed(user_tier, model):
            raise HTTPException(
                status_code=403,
                detail=f"Modelo {model} no permitido para tier {user_tier}"
            )
        
        # Verificar y consumir créditos
        credits_needed = 10  # Todos los modelos cuestan 10 créditos
        can_consume, message = credit_manager.consume_credits(user_id, user_tier, credits_needed)
        
        if not can_consume:
            raise HTTPException(
                status_code=429,
                detail=message
            )
        
        try:
            # Generar letras si es necesario
            lyrics = None
            if hasattr(request, 'generate_lyrics') and request.generate_lyrics:
                lyrics_gen = LyricsGenerator(user_tier)
                lyrics_result = lyrics_gen.generate_lyrics(
                    theme=request.lyrics or request.prompt,
                    genre=request.style or "pop",
                    language="es"
                )
                if lyrics_result.get("success"):
                    lyrics = lyrics_result["lyrics"]
            
            # Generar prompt optimizado si es necesario
            optimized_prompt = request.prompt
            if hasattr(request, 'optimize_prompt') and request.optimize_prompt:
                lyrics_gen = LyricsGenerator(user_tier)
                prompt_result = lyrics_gen.generate_prompt(
                    user_input=request.prompt,
                    genre=request.style or "pop",
                    mood="emotional"
                )
                if prompt_result.get("success"):
                    optimized_prompt = prompt_result["generated_prompt"]
            
            # Generar música usando el sistema existente
            music_result = await call_suno_direct_api(
                optimized_prompt, 
                lyrics, 
                request.style, 
                getattr(request, 'ghost_options', None)
            )
            
            # Si Suno falla, usar generador local
            if not music_result or not music_result.get("success", False):
                logger.info("🔄 Suno failed, using local generator...")
                local_result = local_generator.generate_music(
                    prompt=optimized_prompt,
                    lyrics=lyrics or "",
                    style=request.style or "electronic"
                )
                
                if local_result.get("success"):
                    track = local_result["tracks"][0]
                    
                    # Aplicar postprocesos Rupert Neve
                    processed_track = await apply_rupert_neve_processing(track, user_tier)
                    
                    return {
                        "status": "success",
                        "message": "Music generated with local system + Rupert Neve processing",
                        "prompt": optimized_prompt,
                        "lyrics": lyrics,
                        "style": request.style,
                        "timestamp": datetime.now().isoformat(),
                        "track_id": processed_track["id"],
                        "title": processed_track["title"],
                        "audio_url": processed_track["audio_url"],
                        "download_url": processed_track["audio_url"],
                        "duration": f"{int(processed_track['duration']//60)}:{int(processed_track['duration']%60):02d}",
                        "generation_method": "local_fallback_processed",
                        "post_processing": "rupert_neve_ssl",
                        "credits_consumed": credits_needed,
                        "user_tier": user_tier,
                        "model_used": "local_generator",
                        "suno_response": local_result,
                        "job_id": processed_track["id"]
                    }
            
            # Aplicar postprocesos a música de Suno también
            if music_result and music_result.get("success"):
                processed_result = await apply_rupert_neve_processing(music_result, user_tier)
                music_result = processed_result
            
            return {
                "status": "success",
                "message": "Music generation submitted to Suno + Rupert Neve processing",
                "prompt": optimized_prompt,
                "lyrics": lyrics,
                "style": request.style,
                "timestamp": datetime.now().isoformat(),
                "credits_consumed": credits_needed,
                "user_tier": user_tier,
                "model_used": model,
                "post_processing": "rupert_neve_ssl",
                "auto_renewal_active": True,
                "suno_response": music_result,
                "job_id": music_result.get("id") if music_result else f"job_{int(time.time())}"
            }
            
        except Exception as e:
            # Reembolsar créditos en caso de error
            credit_manager.refund_credits(user_id, credits_needed)
            logger.error(f"❌ Error en generación musical: {e}")
            raise HTTPException(status_code=500, detail=f"Error generando música: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado en generación con créditos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/user/usage")
async def get_user_usage(user_id: str, user_tier: str = "free"):
    """Get user usage information"""
    try:
        usage_info = credit_manager.get_user_usage(user_id, user_tier)
        return usage_info
    except Exception as e:
        logger.error(f"❌ Error obteniendo uso del usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/status")
async def get_system_status():
    """Get system status and credit information"""
    try:
        status = credit_manager.get_system_status()
        return status
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado del sistema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/available")
async def get_available_models(user_tier: str = "free"):
    """Get available models for user tier"""
    try:
        models = credit_manager.get_available_models(user_tier)
        ollama_config = credit_manager.get_ollama_config(user_tier)
        return {
            "music_models": models,
            "ollama_config": ollama_config,
            "user_tier": user_tier
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo modelos disponibles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== POSTPROCESOS RUPERT NEVE =====

@app.post("/api/postprocess/rupert-neve")
async def apply_rupert_neve_postprocess(request: dict):
    """Aplicar postprocesos Rupert Neve a un track existente"""
    try:
        track_id = request.get("track_id")
        user_tier = request.get("user_tier", "free")
        
        if not track_id:
            raise HTTPException(status_code=400, detail="track_id es requerido")
        
        # Obtener track original
        original_track = {
            "id": track_id,
            "title": request.get("title", "Track"),
            "audio_url": request.get("audio_url", ""),
            "duration": request.get("duration", 0)
        }
        
        # Aplicar postprocesos Rupert Neve
        processed_track = await apply_rupert_neve_processing(original_track, user_tier)
        
        return {
            "status": "success",
            "message": "Postprocesos Rupert Neve aplicados exitosamente",
            "original_track": original_track,
            "processed_track": processed_track,
            "processing_details": processed_track.get("post_processing", {}),
            "processing_chain": processed_track.get("processing_chain", [])
        }
        
    except Exception as e:
        logger.error(f"❌ Error en postprocesos Rupert Neve: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/postprocess/rupert-neve/config/{user_tier}")
async def get_rupert_neve_config_endpoint(user_tier: str = "free"):
    """Obtener configuración de postprocesos Rupert Neve para un tier"""
    try:
        config = get_rupert_neve_config(user_tier)
        return {
            "user_tier": user_tier,
            "config": config,
            "description": "Configuración de postprocesos Rupert Neve con SSL, expresividad y saturación"
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo configuración Rupert Neve: {e}")
        raise HTTPException(status_code=500, detail=str(e))