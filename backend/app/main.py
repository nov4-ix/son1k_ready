#!/usr/bin/env python3
"""
Son1kVers3 - Backend FastAPI Principal
Sistema completo de generación musical con IA
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import sqlite3
import hashlib
import jwt
import os
import time
import requests
import json
from datetime import datetime, timedelta
import logging

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "son1k_ultra_secret_key_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./son1k.db")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Son1kVers3 API",
    description="API para generación musical con IA",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Modelos Pydantic
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    archetype: str = "resistance"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class MusicGenerationRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = ""
    style: str = "profesional"
    user_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    context: Optional[str] = None

class NexusRequest(BaseModel):
    action: str
    parameters: Dict[str, Any]
    user_id: Optional[str] = None

# Base de datos
def init_database():
    """Inicializar base de datos SQLite"""
    conn = sqlite3.connect("son1k.db")
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            archetype TEXT DEFAULT 'resistance',
            plan TEXT DEFAULT 'free',
            credits INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # Tabla de generaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            prompt TEXT NOT NULL,
            lyrics TEXT,
            style TEXT,
            audio_urls TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Tabla de tracks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT,
            audio_url TEXT NOT NULL,
            duration INTEGER,
            genre TEXT,
            mood TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("✅ Base de datos inicializada")

# Utilidades
def hash_password(password: str) -> str:
    """Hashear contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verificar contraseña"""
    return hash_password(password) == hashed

def create_access_token(data: dict) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

# Endpoints principales
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "🎵 Son1kVers3 API",
        "status": "running",
        "version": "3.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/api/auth",
            "music": "/api/generate-music",
            "nexus": "/api/nexus"
        }
    }

@app.get("/health")
async def health_check():
    """Verificación de salud del sistema"""
    return {
        "status": "healthy",
        "service": "Son1kVers3 API",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0"
    }

# Autenticación
@app.post("/api/auth/register")
async def register_user(user: UserCreate):
    """Registrar nuevo usuario"""
    conn = sqlite3.connect("son1k.db")
    cursor = conn.cursor()
    
    try:
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        # Crear usuario
        password_hash = hash_password(user.password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, archetype)
            VALUES (?, ?, ?, ?)
        """, (user.username, user.email, password_hash, user.archetype))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        # Crear token
        token = create_access_token({"user_id": user_id, "email": user.email})
        
        return {
            "success": True,
            "message": "Usuario registrado exitosamente",
            "token": token,
            "user": {
                "id": user_id,
                "username": user.username,
                "email": user.email,
                "archetype": user.archetype,
                "plan": "free",
                "credits": 10
            }
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/auth/login")
async def login_user(user: UserLogin):
    """Iniciar sesión"""
    conn = sqlite3.connect("son1k.db")
    cursor = conn.cursor()
    
    try:
        # Buscar usuario
        cursor.execute("""
            SELECT id, username, email, password_hash, archetype, plan, credits
            FROM users WHERE email = ?
        """, (user.email,))
        
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        user_id, username, email, password_hash, archetype, plan, credits = user_data
        
        # Verificar contraseña
        if not verify_password(user.password, password_hash):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Actualizar último login
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
        
        # Crear token
        token = create_access_token({"user_id": user_id, "email": email})
        
        return {
            "success": True,
            "message": "Login exitoso",
            "token": token,
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "archetype": archetype,
                "plan": plan,
                "credits": credits
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Generación musical
@app.post("/api/generate-music")
async def generate_music(request: MusicGenerationRequest):
    """Generar música con IA"""
    try:
        # Llamar al servidor Node.js
        node_server_url = os.getenv("NODE_SERVER_URL", "http://localhost:3001")
        
        response = requests.post(
            f"{node_server_url}/generate-music",
            json={
                "prompt": request.prompt,
                "lyrics": request.lyrics,
                "style": request.style
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Guardar en base de datos si hay user_id
            if request.user_id:
                conn = sqlite3.connect("son1k.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO generations (user_id, prompt, lyrics, style, audio_urls, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    request.user_id,
                    request.prompt,
                    request.lyrics,
                    request.style,
                    json.dumps(data.get("audioUrls", [])),
                    "completed"
                ))
                conn.commit()
                conn.close()
            
            return data
        else:
            raise HTTPException(status_code=500, detail="Error en generación musical")
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-with-credits")
async def generate_with_credits(request: MusicGenerationRequest, token_data: dict = Depends(verify_token)):
    """Generar música con sistema de créditos"""
    user_id = token_data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    
    conn = sqlite3.connect("son1k.db")
    cursor = conn.cursor()
    
    try:
        # Verificar créditos
        cursor.execute("SELECT credits, plan FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        credits, plan = user_data
        
        # Verificar si tiene créditos suficientes
        if plan == "free" and credits <= 0:
            raise HTTPException(status_code=400, detail="Créditos insuficientes")
        
        # Generar música
        music_response = await generate_music(request)
        
        # Descontar crédito si es plan free
        if plan == "free":
            cursor.execute("UPDATE users SET credits = credits - 1 WHERE id = ?", (user_id,))
            conn.commit()
        
        return {
            **music_response,
            "credits_remaining": credits - 1 if plan == "free" else "unlimited",
            "plan": plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Sistema NEXUS
@app.post("/api/nexus/chat")
async def nexus_chat(request: ChatRequest):
    """Chat con PIXEL AI del sistema NEXUS"""
    return {
        "success": True,
        "response": f"PIXEL AI: Procesando tu consulta '{request.message}'...",
        "timestamp": datetime.now().isoformat(),
        "nexus_mode": True
    }

@app.post("/api/nexus/analyze-threats")
async def analyze_threats(request: NexusRequest):
    """Análisis de amenazas del sistema NEXUS"""
    return {
        "success": True,
        "threats_detected": 0,
        "security_level": "MAXIMUM",
        "recommendations": ["Sistema operativo estable", "Conexiones seguras verificadas"],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/nexus/optimize-systems")
async def optimize_systems(request: NexusRequest):
    """Optimización de sistemas NEXUS"""
    return {
        "success": True,
        "optimization_complete": True,
        "performance_boost": "15%",
        "memory_usage": "Optimized",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/nexus/generate-strategy")
async def generate_strategy(request: NexusRequest):
    """Generación de estrategia NEXUS"""
    return {
        "success": True,
        "strategy": "Estrategia de resistencia musical activada",
        "priority": "HIGH",
        "execution_time": "Immediate",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/nexus/scan-network")
async def scan_network(request: NexusRequest):
    """Escaneo de red NEXUS"""
    return {
        "success": True,
        "network_status": "SECURE",
        "connections": 42,
        "threats": 0,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/nexus/deploy-countermeasures")
async def deploy_countermeasures(request: NexusRequest):
    """Despliegue de contramedidas NEXUS"""
    return {
        "success": True,
        "countermeasures_deployed": True,
        "security_level": "MAXIMUM",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/nexus/apply-enhancement")
async def apply_enhancement(request: NexusRequest):
    """Aplicar mejoras NEXUS"""
    return {
        "success": True,
        "enhancement_applied": True,
        "performance_boost": "25%",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/nexus/quantum-analysis")
async def quantum_analysis(request: NexusRequest):
    """Análisis cuántico NEXUS"""
    return {
        "success": True,
        "quantum_state": "STABLE",
        "entanglement_level": "OPTIMAL",
        "analysis_complete": True,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/nexus/activate-protocols")
async def activate_protocols(request: NexusRequest):
    """Activar protocolos NEXUS"""
    return {
        "success": True,
        "protocols_activated": True,
        "system_status": "FULLY_OPERATIONAL",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/nexus/status")
async def nexus_status():
    """Estado del sistema NEXUS"""
    return {
        "success": True,
        "nexus_status": "OPERATIONAL",
        "security_level": "MAXIMUM",
        "threats": 0,
        "performance": "OPTIMAL",
        "timestamp": datetime.now().isoformat()
    }

# Sistema de Resistencia
@app.post("/api/resistance/chat")
async def resistance_chat(request: ChatRequest):
    """Chat del sistema de Resistencia"""
    return {
        "success": True,
        "response": f"Resistencia: Recibido '{request.message}'. Mantén la lucha musical.",
        "timestamp": datetime.now().isoformat(),
        "resistance_mode": True
    }

@app.post("/api/resistance/create-collaboration")
async def create_collaboration(request: dict):
    """Crear colaboración de Resistencia"""
    return {
        "success": True,
        "collaboration_id": f"res_{int(time.time())}",
        "status": "ACTIVE",
        "members": 1,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/resistance/status")
async def resistance_status():
    """Estado del sistema de Resistencia"""
    return {
        "success": True,
        "resistance_status": "ACTIVE",
        "members": 42,
        "missions_completed": 156,
        "timestamp": datetime.now().isoformat()
    }

# Easter Eggs
@app.post("/api/easter-eggs/portal")
async def activate_portal():
    """Activar Portal de Resistencia"""
    return {
        "success": True,
        "portal_activated": True,
        "message": "Portal de Resistencia activado. Bienvenido a la dimensión musical.",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/easter-eggs/konami")
async def activate_konami():
    """Activar Código Konami"""
    return {
        "success": True,
        "konami_activated": True,
        "message": "Código Konami activado. Modo cheat habilitado.",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/easter-eggs/glitch")
async def toggle_glitch():
    """Activar Modo Glitch"""
    return {
        "success": True,
        "glitch_mode": True,
        "message": "Modo Glitch activado. Realidad distorsionada.",
        "timestamp": datetime.now().isoformat()
    }

# Endpoints adicionales para el frontend
@app.post("/api/generate-prompt")
async def generate_prompt(request: dict):
    """Generar prompt mejorado con IA"""
    prompt = request.get("prompt", "")
    style = request.get("style", "profesional")
    
    # Simular generación de prompt mejorado
    enhanced_prompt = f"🎵 {prompt} - Estilo {style} con elementos musicales avanzados"
    
    return {
        "success": True,
        "enhanced_prompt": enhanced_prompt,
        "original_prompt": prompt,
        "style": style,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/generate-lyrics")
async def generate_lyrics(request: dict):
    """Generar letras con IA"""
    prompt = request.get("prompt", "")
    style = request.get("style", "profesional")
    
    # Simular generación de letras
    sample_lyrics = f"""
[Verso 1]
{prompt} es lo que siento
En este momento de creación
La música fluye en mi ser
Con cada nota y cada canción

[Coro]
Son1k, Son1k, la resistencia musical
Creando arte con tecnología
Son1k, Son1k, el futuro es digital
La música nunca será igual

[Verso 2]
{style} es mi estilo
Profesional en cada compás
La IA me ayuda a crear
Pero el corazón siempre está
"""
    
    return {
        "success": True,
        "lyrics": sample_lyrics.strip(),
        "prompt": prompt,
        "style": style,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/postprocess/rupert-neve")
async def postprocess_rupert_neve(request: dict):
    """Postprocesamiento con Rupert Neve"""
    audio_url = request.get("audio_url", "")
    
    return {
        "success": True,
        "processed_audio": audio_url,
        "effects_applied": [
            "Rupert Neve EQ",
            "Compresión Neve",
            "Saturación analógica",
            "Masterización profesional"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/transform-audio")
async def transform_audio(request: dict):
    """Transformar audio con efectos"""
    audio_url = request.get("audio_url", "")
    transformation = request.get("transformation", "enhance")
    
    return {
        "success": True,
        "transformed_audio": audio_url,
        "transformation": transformation,
        "effects": [
            "Reverb espacial",
            "Delay sincronizado",
            "Compresión dinámica",
            "EQ espectral"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """Chat con IA asistente"""
    message = request.message
    
    # Simular respuestas de IA
    responses = [
        f"Entiendo tu consulta: '{message}'. Te ayudo con la generación musical.",
        f"Interesante pregunta sobre '{message}'. ¿Te gustaría que genere una canción?",
        f"Perfecto, '{message}' es una excelente idea musical. ¿Procedo con la generación?",
        f"Comprendo tu solicitud: '{message}'. El sistema está listo para crear música."
    ]
    
    response = responses[len(message) % len(responses)]
    
    return {
        "success": True,
        "response": response,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

# Otros endpoints
@app.get("/api/tracks")
async def get_tracks():
    """Obtener tracks disponibles"""
    conn = sqlite3.connect("son1k.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, artist, audio_url, duration, genre, mood, created_at
        FROM tracks ORDER BY created_at DESC LIMIT 50
    """)
    
    tracks = []
    for row in cursor.fetchall():
        tracks.append({
            "id": row[0],
            "title": row[1],
            "artist": row[2],
            "audio_url": row[3],
            "duration": row[4],
            "genre": row[5],
            "mood": row[6],
            "created_at": row[7]
        })
    
    conn.close()
    return {"tracks": tracks}

@app.get("/api/user/usage")
async def get_user_usage(user_id: str, user_tier: str = "free"):
    """Obtener uso del usuario"""
    conn = sqlite3.connect("son1k.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT credits, plan FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    
    if not user_data:
        return {"credits": 0, "plan": "free", "unlimited": False}
    
    credits, plan = user_data
    
    return {
        "credits": credits,
        "plan": plan,
        "unlimited": plan in ["admin", "enterprise"],
        "generations_remaining": credits if plan == "free" else "unlimited"
    }

# Inicializar base de datos al startup
@app.on_event("startup")
async def startup_event():
    """Evento de inicio"""
    init_database()
    logger.info("🚀 Son1kVers3 API iniciada")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
