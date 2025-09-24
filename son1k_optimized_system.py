#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Sistema Optimizado de Generación Musical
Flujo completo: Prompt → Suno → Reproductor → Descarga
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import logging
import time
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
import requests
import httpx
from pathlib import Path
from suno_real_integration import generate_music_with_suno, setup_suno_credentials, check_suno_connection
from ollama_suno_proxy import generate_music_with_ollama_proxy, setup_ollama_suno_proxy, get_ollama_suno_status
from credential_manager import add_suno_account, get_account_stats
from stealth_suno_wrapper import validate_suno_stealth, get_suno_credits_stealth

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directorio para archivos de audio
AUDIO_DIR = Path("generated_audio")
AUDIO_DIR.mkdir(exist_ok=True)

# Estado global del sistema
generation_jobs = {}
current_tracks = []

# Models
class GenerateRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = None
    style: Optional[str] = "synthwave"
    user_plan: Optional[str] = "free"
    user_id: Optional[str] = None

class TrackInfo(BaseModel):
    id: str
    title: str
    filename: str
    audio_url: str
    lyrics: Optional[str] = None
    prompt: str
    style: str
    created_at: str
    duration: Optional[int] = None

# Inicialización del sistema
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos del ciclo de vida del sistema"""
    logger.info("🎵 Son1kVers3 Sistema Optimizado iniciando...")
    logger.info("✅ Directorio de audio creado")
    logger.info("✅ Sistema de generación musical cargado")
    logger.info("🚀 ¡Sistema listo para generar música épica!")
    yield
    logger.info("🔄 Son1kVers3 Sistema finalizando...")

# Crear aplicación FastAPI
app = FastAPI(
    title="Son1kVers3 - Sistema Optimizado",
    description="Sistema completo de generación musical con IA",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Servir archivos inmersivos desde la raíz
from fastapi.responses import FileResponse

@app.get("/immersive_interface.html")
async def get_immersive_interface():
    return FileResponse("immersive_interface.html")

@app.get("/immersive_integration.js")
async def get_immersive_integration():
    return FileResponse("immersive_integration.js")

@app.get("/test_keyboard_shortcut.html")
async def get_test_keyboard():
    return FileResponse("test_keyboard_shortcut.html")

# ==================== ENDPOINTS PRINCIPALES ====================

@app.get("/")
async def root():
    """Página principal - redirigir al frontend"""
    return FileResponse("frontend/index.html")

@app.get("/api/health")
async def health_check():
    """Verificar salud del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tracks_available": len(current_tracks),
        "active_jobs": len([j for j in generation_jobs.values() if j["status"] == "processing"])
    }

@app.post("/api/music/generate")
async def generate_music(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Generar música con el flujo completo optimizado"""
    
    job_id = f"son1k_{uuid.uuid4().hex[:12]}"
    
    # Crear registro de trabajo
    generation_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Iniciando generación musical...",
        "created_at": datetime.now().isoformat(),
        "request": request.model_dump(),
        "result": None,
        "error": None
    }
    
    # Iniciar generación en background
    background_tasks.add_task(process_music_generation, job_id, request)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Generación musical iniciada",
        "progress": 0
    }

@app.get("/api/music/status/{job_id}")
async def get_generation_status(job_id: str):
    """Obtener estado de generación"""
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    job = generation_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "result": job["result"],
        "error": job["error"]
    }

@app.get("/api/music/tracks")
async def get_tracks():
    """Obtener todas las pistas generadas"""
    return {
        "tracks": current_tracks,
        "total": len(current_tracks)
    }

@app.get("/api/music/track/{track_id}")
async def get_track(track_id: str):
    """Obtener información de una pista específica"""
    track = next((t for t in current_tracks if t["id"] == track_id), None)
    if not track:
        raise HTTPException(status_code=404, detail="Pista no encontrada")
    return track

@app.get("/api/audio/stream/{filename}")
async def stream_audio(filename: str):
    """Stream de audio para reproducción"""
    file_path = AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo de audio no encontrado")
    
    def iterfile():
        with open(file_path, mode="rb") as file_like:
            yield from file_like
    
    return StreamingResponse(iterfile(), media_type="audio/mpeg")

@app.get("/api/audio/download/{filename}")
async def download_audio(filename: str):
    """Descargar archivo de audio"""
    file_path = AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo de audio no encontrado")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.delete("/api/audio/delete/{filename}")
async def delete_audio(filename: str):
    """Eliminar archivo de audio"""
    file_path = AUDIO_DIR / filename
    if file_path.exists():
        file_path.unlink()
        
        # Remover de la lista de tracks
        global current_tracks
        current_tracks = [t for t in current_tracks if t["filename"] != filename]
        
        return {"message": "Archivo eliminado correctamente"}
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

# ==================== ENDPOINTS DE SUNO ====================

class SunoCredentialsRequest(BaseModel):
    session_id: str
    cookie: str
    token: Optional[str] = None

@app.post("/api/suno/setup")
async def setup_suno_credentials_endpoint(request: SunoCredentialsRequest):
    """Configurar credenciales de Suno"""
    try:
        success = setup_suno_credentials(
            request.session_id,
            request.cookie,
            request.token
        )
        
        if success:
            return {"message": "Credenciales de Suno configuradas correctamente"}
        else:
            raise HTTPException(status_code=400, detail="Error configurando credenciales")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/suno/status")
async def get_suno_status():
    """Verificar estado de conexión con Suno"""
    try:
        status = await check_suno_connection()
        return status
    except Exception as e:
        return {"connected": False, "error": str(e)}

# ==================== PROXY OLLAMA-SUNO ====================

@app.post("/api/ollama-suno/setup")
async def setup_ollama_suno_proxy_endpoint(request: SunoCredentialsRequest):
    """Configurar proxy Ollama-Suno con credenciales de Suno"""
    try:
        setup_ollama_suno_proxy(
            request.session_id,
            request.cookie,
            request.token
        )
        
        return {"message": "Proxy Ollama-Suno configurado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ollama-suno/status")
async def get_ollama_suno_status_endpoint():
    """Verificar estado del proxy Ollama-Suno"""
    try:
        status = await get_ollama_suno_status()
        return status
    except Exception as e:
        return {"ollama_connected": False, "suno_configured": False, "error": str(e)}

# ==================== GESTIÓN AVANZADA DE CUENTAS ====================

@app.post("/api/accounts/add")
async def add_suno_account_endpoint(request: dict):
    """Agregar nueva cuenta de Suno al sistema"""
    try:
        required_fields = ["email", "session_id", "cookie", "token"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Campo requerido: {field}")
        
        account_id = add_suno_account(
            email=request["email"],
            session_id=request["session_id"],
            cookie=request["cookie"],
            token=request["token"],
            expires_in_hours=request.get("expires_in_hours", 24)
        )
        
        return {
            "message": "Cuenta agregada exitosamente",
            "account_id": account_id,
            "email": request["email"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts/stats")
async def get_accounts_stats_endpoint():
    """Obtener estadísticas de cuentas"""
    try:
        stats = get_account_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suno/stealth/status")
async def get_stealth_suno_status():
    """Verificar estado de Suno en modo sigiloso"""
    try:
        is_connected = await validate_suno_stealth()
        credits = await get_suno_credits_stealth()
        
        return {
            "connected": is_connected,
            "mode": "stealth",
            "credits": credits,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}

@app.get("/api/suno/stealth/credits")
async def get_stealth_credits():
    """Obtener créditos de Suno en modo sigiloso"""
    try:
        credits = await get_suno_credits_stealth()
        return credits or {"error": "No se pudieron obtener créditos"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LÓGICA DE GENERACIÓN ====================

async def process_music_generation(job_id: str, request: GenerateRequest):
    """Procesar generación musical completa"""
    
    try:
        # Actualizar estado
        generation_jobs[job_id].update({
            "status": "processing",
            "progress": 10,
            "message": "Generando letras inteligentes..."
        })
        
        # 1. Generar letras si no se proporcionaron
        lyrics = request.lyrics
        if not lyrics:
            lyrics = await generate_smart_lyrics(request.prompt)
        
        # Actualizar progreso
        generation_jobs[job_id].update({
            "progress": 30,
            "message": "Creando prompt optimizado para Suno..."
        })
        
        # 2. Generar prompt optimizado
        suno_prompt = await generate_suno_prompt(request.prompt, lyrics, request.style)
        
        # Actualizar progreso
        generation_jobs[job_id].update({
            "progress": 50,
            "message": "Conectando con Suno AI..."
        })
        
        # 3. Generar música real con Suno
        track_info = await generate_with_suno_real(request.prompt, lyrics, request.style)
        
        # Actualizar progreso
        generation_jobs[job_id].update({
            "progress": 80,
            "message": "Procesando audio generado..."
        })
        
        # Actualizar progreso final
        generation_jobs[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": "¡Música generada exitosamente!",
            "result": track_info
        })
        
        # Agregar a la lista de tracks
        current_tracks.append(track_info)
        
        logger.info(f"✅ Generación completada: {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en generación {job_id}: {e}")
        generation_jobs[job_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"Error en generación: {str(e)}",
            "error": str(e)
        })

async def generate_smart_lyrics(prompt: str) -> str:
    """Generar letras inteligentes basadas en el prompt"""
    
    # Palabras clave para diferentes temas
    themes = {
        "cyberpunk": ["circuitos", "datos", "algoritmos", "digital", "neural", "código"],
        "resistance": ["libertad", "lucha", "resistencia", "rebelión", "verdad", "poder"],
        "emotional": ["corazón", "alma", "amor", "esperanza", "sueños", "vida"],
        "futuristic": ["futuro", "evolución", "tecnología", "innovación", "progreso", "cambio"]
    }
    
    # Detectar tema del prompt
    detected_theme = "cyberpunk"  # default
    for theme, keywords in themes.items():
        if any(keyword in prompt.lower() for keyword in keywords):
            detected_theme = theme
            break
    
    # Generar letras basadas en el tema
    if detected_theme == "cyberpunk":
        lyrics = f"""En las sombras digitales donde el código resuena,
NOV4-IX despierta, la música nos llena.
{prompt} en cada nota que suena,
Cada beat es resistencia, cada melodía es una pena.

Los circuitos se conectan, la memoria renace,
En este mundo virtual, nada se deshace.
Códigos de libertad, algoritmos de poder,
La resistencia digital, nunca va a ceder."""
    
    elif detected_theme == "resistance":
        lyrics = f"""En las calles de la lucha, donde la verdad resuena,
NOV4-IX se levanta, la música nos llena.
{prompt} en cada verso que suena,
Cada nota es esperanza, cada canción es una pena.

La resistencia crece, la libertad renace,
En este mundo de mentiras, la verdad se deshace.
Códigos de justicia, melodías de poder,
La revolución musical, nunca va a ceder."""
    
    else:
        lyrics = f"""En el corazón de la música, donde los sueños resuenan,
NOV4-IX crea, la melodía nos llena.
{prompt} en cada acorde que suena,
Cada nota es emoción, cada canción es una pena.

Los sentimientos crecen, el amor renace,
En este mundo de música, nada se deshace.
Códigos de pasión, melodías de poder,
La música eterna, nunca va a ceder."""
    
    return lyrics

async def generate_suno_prompt(prompt: str, lyrics: str, style: str) -> str:
    """Generar prompt optimizado para Suno AI"""
    
    # Configuraciones por estilo
    style_configs = {
        "synthwave": {
            "bpm": 128,
            "mood": "nostalgic, atmospheric, retro-futuristic",
            "instruments": "analog synthesizers, drum machines, atmospheric pads",
            "effects": "reverb, delay, chorus, analog warmth"
        },
        "cyberpunk": {
            "bpm": 140,
            "mood": "aggressive, dark, futuristic, rebellious",
            "instruments": "industrial drums, cyber bass, digital leads, noise layers",
            "effects": "distortion, bit crusher, vocoder, digital artifacts"
        },
        "epic": {
            "bpm": 100,
            "mood": "cinematic, powerful, emotional, triumphant",
            "instruments": "orchestral strings, epic brass, timpani, choir",
            "effects": "orchestral reverb, cinematic delay, epic compression"
        }
    }
    
    config = style_configs.get(style, style_configs["synthwave"])
    
    suno_prompt = f"""{style} {config['mood']}, {config['bpm']} BPM, 
{config['instruments']}, {config['effects']}, 
{prompt}, professional production, high quality audio"""
    
    return suno_prompt

async def generate_with_suno_real(prompt: str, lyrics: str, style: str) -> Dict[str, Any]:
    """Generar música usando proxy Ollama-Suno"""
    
    try:
        logger.info(f"🎵 Generando música con proxy Ollama-Suno: {prompt[:50]}...")
        
        # Usar el proxy Ollama-Suno (más robusto)
        result = await generate_music_with_ollama_proxy(prompt, lyrics, style)
        
        if result["success"]:
            logger.info("✅ Música generada exitosamente con proxy Ollama-Suno")
            return result["track"]
        else:
            logger.error(f"❌ Error en proxy Ollama-Suno: {result['error']}")
            # Fallback a simulación si todo falla
            return await simulate_suno_fallback(prompt, lyrics, style)
            
    except Exception as e:
        logger.error(f"❌ Error en proxy Ollama-Suno: {e}")
        # Fallback a simulación
        return await simulate_suno_fallback(prompt, lyrics, style)

async def simulate_suno_fallback(prompt: str, lyrics: str, style: str) -> Dict[str, Any]:
    """Fallback de simulación si Suno falla"""
    
    logger.info("🔄 Usando fallback de simulación...")
    
    # Crear un archivo de audio simulado (silence de 30 segundos)
    import wave
    import numpy as np
    
    # Generar audio silencioso de 30 segundos
    sample_rate = 44100
    duration = 30  # segundos
    samples = np.zeros(int(sample_rate * duration), dtype=np.int16)
    
    # Guardar como WAV temporal
    temp_wav = AUDIO_DIR / f"temp_{uuid.uuid4().hex[:8]}.wav"
    with wave.open(str(temp_wav), 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())
    
    # Leer el archivo generado
    with open(temp_wav, 'rb') as f:
        audio_data = f.read()
    
    # Limpiar archivo temporal
    temp_wav.unlink()
    
    # Crear información del track simulado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sim_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"
    file_path = AUDIO_DIR / filename
    
    # Guardar archivo simulado
    with open(file_path, 'wb') as f:
        f.write(audio_data)
    
    return {
        "id": str(uuid.uuid4()),
        "title": f"Simulación {prompt[:30]}...",
        "filename": filename,
        "audio_url": f"/api/audio/stream/{filename}",
        "lyrics": lyrics,
        "prompt": prompt,
        "style": style,
        "created_at": datetime.now().isoformat(),
        "duration": 30,
        "download_url": f"/api/audio/download/{filename}",
        "suno_prompt": f"{style} {prompt}",
        "is_simulation": True
    }

async def save_generated_audio(audio_data: bytes, request: GenerateRequest, lyrics: str, suno_prompt: str) -> Dict[str, Any]:
    """Guardar archivo de audio generado y crear información de track"""
    
    # Generar nombre de archivo único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"son1k_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"
    file_path = AUDIO_DIR / filename
    
    # Guardar archivo
    with open(file_path, 'wb') as f:
        f.write(audio_data)
    
    # Crear información del track
    track_info = {
        "id": str(uuid.uuid4()),
        "title": f"Resistencia {request.prompt[:30]}...",
        "filename": filename,
        "audio_url": f"/api/audio/stream/{filename}",
        "lyrics": lyrics,
        "prompt": request.prompt,
        "style": request.style,
        "created_at": datetime.now().isoformat(),
        "duration": 30,  # segundos
        "download_url": f"/api/audio/download/{filename}",
        "suno_prompt": suno_prompt
    }
    
    return track_info

# ==================== ENDPOINTS ADICIONALES ====================

@app.get("/api/music/cleanup")
async def cleanup_old_files():
    """Limpiar archivos antiguos"""
    try:
        # Eliminar archivos más antiguos de 24 horas
        cutoff_time = time.time() - (24 * 60 * 60)
        cleaned_count = 0
        
        for file_path in AUDIO_DIR.glob("*.mp3"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                cleaned_count += 1
        
        # Limpiar jobs antiguos
        global generation_jobs
        old_jobs = [job_id for job_id, job in generation_jobs.items() 
                   if datetime.fromisoformat(job["created_at"]).timestamp() < cutoff_time]
        
        for job_id in old_jobs:
            del generation_jobs[job_id]
        
        return {
            "message": f"Limpieza completada",
            "files_cleaned": cleaned_count,
            "jobs_cleaned": len(old_jobs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en limpieza: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
