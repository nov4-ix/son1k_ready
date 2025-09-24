#!/usr/bin/env python3
"""
🎵 SON1K SIMPLE STABLE - Versión Simplificada y Estable
Sistema básico sin dependencias complejas que puedan causar colgadas
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
import time
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
import requests
from pathlib import Path

# Configurar logging simple primero
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/son1k_simple.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar controladores de Ollama (con manejo de errores)
try:
    from ollama_browser_controller import generate_music_with_browser
    BROWSER_CONTROLLER_AVAILABLE = True
    logger.info("✅ Ollama Browser Controller cargado")
except Exception as e:
    logger.warning(f"⚠️ Ollama Browser Controller no disponible: {e}")
    BROWSER_CONTROLLER_AVAILABLE = False

# Importar Suno Real Integration
try:
    from suno_real_integration import generate_music_in_suno_real
    SUNO_REAL_AVAILABLE = True
    logger.info("✅ Suno Real Integration cargado")
except Exception as e:
    SUNO_REAL_AVAILABLE = False
    logger.warning(f"⚠️ Suno Real Integration no disponible: {e}")

# Importar Suno Stealth Integration
try:
    from suno_stealth_integration import generate_music_with_suno_stealth
    SUNO_STEALTH_AVAILABLE = True
    logger.info("✅ Suno Stealth Integration cargado")
except Exception as e:
    SUNO_STEALTH_AVAILABLE = False
    logger.warning(f"⚠️ Suno Stealth Integration no disponible: {e}")

# Importar Multi Account Manager
try:
    from multi_account_manager import generate_music_with_multi_account
    MULTI_ACCOUNT_AVAILABLE = True
    logger.info("✅ Multi Account Manager cargado")
except Exception as e:
    MULTI_ACCOUNT_AVAILABLE = False
    logger.warning(f"⚠️ Multi Account Manager no disponible: {e}")

# Importar Real Music Generator
try:
    from real_music_generator import generate_real_music
    REAL_MUSIC_AVAILABLE = True
    logger.info("✅ Real Music Generator cargado")
except Exception as e:
    REAL_MUSIC_AVAILABLE = False
    logger.warning(f"⚠️ Real Music Generator no disponible: {e}")

try:
    from ollama_suno_proxy import OllamaSunoProxy, generate_music_with_ollama_proxy
    OLLAMA_AVAILABLE = True
    logger.info("✅ Ollama-Suno Proxy cargado")
except Exception as e:
    logger.warning(f"⚠️ Ollama-Suno Proxy no disponible: {e}")
    OLLAMA_AVAILABLE = False

# Directorio para archivos de audio
AUDIO_DIR = Path("generated_audio")
AUDIO_DIR.mkdir(exist_ok=True)

# Estado global del sistema
generation_jobs = {}
current_tracks = []

# Inicializar Ollama-Suno Proxy si está disponible
ollama_proxy = None
if OLLAMA_AVAILABLE:
    try:
        ollama_proxy = OllamaSunoProxy()
        
        # Cargar credenciales de Suno si existen
        try:
            with open('suno_credentials.json', 'r') as f:
                creds = json.load(f)
                ollama_proxy.setup_suno_credentials(
                    creds.get('session_id'),
                    creds.get('cookie'),
                    creds.get('token')
                )
                logger.info("✅ Credenciales de Suno cargadas")
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron cargar credenciales de Suno: {e}")
        
        logger.info("✅ Ollama-Suno Proxy inicializado")
    except Exception as e:
        logger.warning(f"⚠️ Error inicializando Ollama-Suno Proxy: {e}")
        OLLAMA_AVAILABLE = False

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

# Crear aplicación FastAPI
app = FastAPI(
    title="Son1k Simple Stable",
    description="Sistema simplificado de generación musical",
    version="1.0.0"
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

# Incluir router de WebSocket para extensiones
try:
    from extension_websocket import router as extension_router
    app.include_router(extension_router)
    logger.info("✅ Extension WebSocket router cargado")
except Exception as e:
    logger.warning(f"⚠️ Extension WebSocket no disponible: {e}")

# Health check simple
@app.get("/health")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - start_time,
        "active_jobs": len([j for j in generation_jobs.values() if j["status"] == "processing"]),
        "tracks_available": len(current_tracks)
    }

@app.get("/api/health")
async def api_health_check():
    """Health check para API"""
    return {
        "ok": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - start_time,
        "active_jobs": len([j for j in generation_jobs.values() if j["status"] == "processing"]),
        "tracks_available": len(current_tracks),
        "browser_controller_available": BROWSER_CONTROLLER_AVAILABLE,
        "ollama_available": OLLAMA_AVAILABLE
    }

# Endpoints para extensión
@app.get("/manifest.json")
async def get_manifest():
    """Manifest para extensión"""
    return {
        "name": "Son1k Music Generator",
        "version": "1.0.0",
        "description": "Generador de música con IA",
        "permissions": ["activeTab", "storage"],
        "host_permissions": ["http://localhost:8000/*", "https://suno.com/*"],
        "content_scripts": [{
            "matches": ["https://suno.com/*"],
            "js": ["content_suno.js"]
        }],
        "background": {
            "service_worker": "background_robust.js"
        },
        "action": {
            "default_popup": "popup.html"
        }
    }

@app.get("/sw.js")
async def get_service_worker():
    """Service worker para extensión"""
    return FileResponse("extension/background_robust.js")

@app.get("/")
async def root():
    """Página principal"""
    try:
        # Usar ruta absoluta para asegurar que se encuentra el archivo
        html_path = os.path.join(os.getcwd(), "index.html")
        if os.path.exists(html_path):
            return FileResponse(html_path)
        else:
            logger.error(f"❌ No se encontró index.html en: {html_path}")
            return {"message": "Son1k Simple Stable - Sistema funcionando", "error": "index.html no encontrado"}
    except Exception as e:
        logger.error(f"❌ Error sirviendo index.html: {e}")
        return {"message": "Son1k Simple Stable - Sistema funcionando", "error": str(e)}

@app.get("/debug")
async def debug_page():
    """Página de debug para el archivo"""
    try:
        debug_path = os.path.join(os.getcwd(), "debug_archivo.html")
        if os.path.exists(debug_path):
            return FileResponse(debug_path)
        else:
            return {"message": "Debug page not found"}
    except Exception as e:
        logger.error(f"❌ Error sirviendo debug page: {e}")
        return {"message": "Error loading debug page", "error": str(e)}

@app.get("/api/status")
async def get_status():
    """Estado del sistema"""
    ollama_status = "unavailable"
    if OLLAMA_AVAILABLE and ollama_proxy:
        try:
            ollama_healthy = await ollama_proxy.check_ollama_health()
            ollama_status = "healthy" if ollama_healthy else "unhealthy"
        except:
            ollama_status = "error"
    
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len([j for j in generation_jobs.values() if j["status"] == "processing"]),
        "tracks_available": len(current_tracks),
        "system": "simple_stable",
        "browser_controller_available": BROWSER_CONTROLLER_AVAILABLE,
        "ollama_available": OLLAMA_AVAILABLE,
        "ollama_status": ollama_status
    }

@app.post("/api/music/generate")
@app.post("/api/generate")  # Alias para compatibilidad con extensión
async def generate_music(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Generar música con Ollama-Suno Proxy o simulación"""
    try:
        job_id = f"son1k_{uuid.uuid4().hex[:12]}"
        
        # Crear registro de trabajo
        generation_jobs[job_id] = {
            "id": job_id,
            "status": "processing",
            "prompt": request.prompt,
            "lyrics": request.lyrics,
            "style": request.style,
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "mode": "ollama" if OLLAMA_AVAILABLE else "simulation"
        }
        
               # Prioridad: Multi Account > Suno Stealth > Suno Real > Real Music Generator > Ollama Proxy > Browser Controller > Simulación
               if MULTI_ACCOUNT_AVAILABLE:
                   background_tasks.add_task(generate_with_multi_account, job_id, request)
                   message = "Generación iniciada con Múltiples Cuentas (máxima evasión)"
               elif SUNO_STEALTH_AVAILABLE:
                   background_tasks.add_task(generate_with_suno_stealth, job_id, request)
                   message = "Generación iniciada con Suno Stealth (música real indetectable)"
               elif SUNO_REAL_AVAILABLE:
                   background_tasks.add_task(generate_with_suno_real, job_id, request)
                   message = "Generación iniciada con Suno Real (aparecerá en tu biblioteca)"
               elif REAL_MUSIC_AVAILABLE:
            background_tasks.add_task(generate_with_real_music, job_id, request)
            message = "Generación iniciada con Real Music Generator (música real sintetizada)"
        elif OLLAMA_AVAILABLE and ollama_proxy:
            background_tasks.add_task(generate_with_ollama, job_id, request)
            message = "Generación iniciada con Ollama-Suno Proxy"
        elif BROWSER_CONTROLLER_AVAILABLE:
            background_tasks.add_task(generate_with_browser, job_id, request)
            message = "Generación iniciada con Ollama Browser Controller"
        else:
            background_tasks.add_task(simulate_generation, job_id, request)
            message = "Generación iniciada (modo simulación - Ollama no disponible)"
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": message,
            "mode": "ollama" if OLLAMA_AVAILABLE else "simulation"
        }
        
    except Exception as e:
        logger.error(f"Error en generación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def simulate_generation(job_id: str, request: GenerateRequest):
    """Simular generación de música"""
    try:
        logger.info(f"Iniciando simulación de generación: {job_id}")
        
        # Simular progreso
        for i in range(1, 6):
            await asyncio.sleep(2)  # 2 segundos por paso
            generation_jobs[job_id]["progress"] = i * 20
            logger.info(f"Progreso {job_id}: {i * 20}%")
        
        # Crear track simulado
        track_id = f"track_{uuid.uuid4().hex[:8]}"
        track = TrackInfo(
            id=track_id,
            title=f"Generated: {request.prompt[:50]}...",
            filename=f"{track_id}.mp3",
            audio_url=f"/api/tracks/{track_id}/audio",
            lyrics=request.lyrics or "Lyrics not provided",
            prompt=request.prompt,
            style=request.style,
            created_at=datetime.now().isoformat(),
            duration=180
        )
        
        current_tracks.append(track)
        generation_jobs[job_id]["status"] = "completed"
        generation_jobs[job_id]["track_id"] = track_id
        generation_jobs[job_id]["progress"] = 100
        
        logger.info(f"Generación completada: {job_id}")
        
    except Exception as e:
        logger.error(f"Error en simulación: {e}")
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = str(e)

async def generate_with_ollama(job_id: str, request: GenerateRequest):
    """Generar música usando Ollama-Suno Proxy"""
    try:
        logger.info(f"Iniciando generación con Ollama: {job_id}")
        
        # Verificar que Ollama esté disponible
        if not ollama_proxy:
            raise Exception("Ollama proxy no disponible")
        
        # Actualizar progreso
        generation_jobs[job_id]["progress"] = 10
        generation_jobs[job_id]["status"] = "processing"
        
        # Preparar datos para Ollama
        generation_data = {
            "prompt": request.prompt,
            "lyrics": request.lyrics or "",
            "style": request.style,
            "duration": 60
        }
        
        # Generar música con Ollama-Suno Proxy
        generation_jobs[job_id]["progress"] = 30
        logger.info(f"Enviando a Ollama-Suno Proxy: {job_id}")
        
        result = await generate_music_with_ollama_proxy(
            prompt=request.prompt,
            lyrics=request.lyrics,
            style=request.style
        )
        
        if result and result.get("success"):
            # Crear track real
            track_id = f"track_{uuid.uuid4().hex[:8]}"
            track = TrackInfo(
                id=track_id,
                title=result.get("title", f"Generated: {request.prompt[:50]}..."),
                filename=result.get("filename", f"{track_id}.mp3"),
                audio_url=result.get("audio_url", f"/api/tracks/{track_id}/audio"),
                lyrics=result.get("lyrics", request.lyrics or "Generated lyrics"),
                prompt=request.prompt,
                style=request.style,
                created_at=datetime.now().isoformat(),
                duration=result.get("duration", 180)
            )
            
            current_tracks.append(track)
            generation_jobs[job_id]["status"] = "completed"
            generation_jobs[job_id]["track_id"] = track_id
            generation_jobs[job_id]["progress"] = 100
            generation_jobs[job_id]["result"] = result
            
            logger.info(f"Generación con Ollama completada: {job_id}")
        else:
            # Fallback a simulación si Ollama falla
            logger.warning(f"Ollama falló, usando simulación: {job_id}")
            await simulate_generation(job_id, request)
            
    except Exception as e:
        logger.error(f"Error en generación con Ollama: {e}")
        # Fallback a simulación
        try:
            await simulate_generation(job_id, request)
        except Exception as fallback_error:
            logger.error(f"Error en fallback: {fallback_error}")
            generation_jobs[job_id]["status"] = "failed"
            generation_jobs[job_id]["error"] = str(e)

async def generate_with_browser(job_id: str, request: GenerateRequest):
    """Generar música usando Ollama Browser Controller"""
    try:
        logger.info(f"Iniciando generación con navegador: {job_id}")
        
        # Actualizar progreso
        generation_jobs[job_id]["progress"] = 10
        generation_jobs[job_id]["status"] = "processing"
        
        # Generar música con navegador
        generation_jobs[job_id]["progress"] = 30
        logger.info(f"Enviando a Ollama Browser Controller: {job_id}")
        
        result = await generate_music_with_browser(
            prompt=request.prompt,
            lyrics=request.lyrics,
            style=request.style
        )
        
        if result and result.get("success"):
            # Crear track real
            track_id = f"track_{uuid.uuid4().hex[:8]}"
            track = TrackInfo(
                id=track_id,
                title=result.get("title", f"Generated: {request.prompt[:50]}..."),
                filename=result.get("filename", f"{track_id}.mp3"),
                audio_url=result.get("audio_url", f"/api/tracks/{track_id}/audio"),
                lyrics=result.get("lyrics", request.lyrics or "Generated lyrics"),
                prompt=request.prompt,
                style=request.style,
                created_at=datetime.now().isoformat(),
                duration=result.get("duration", 180)
            )
            
            current_tracks.append(track)
            generation_jobs[job_id]["status"] = "completed"
            generation_jobs[job_id]["track_id"] = track_id
            generation_jobs[job_id]["progress"] = 100
            generation_jobs[job_id]["result"] = result
            
            logger.info(f"Generación con navegador completada: {job_id}")
        else:
            # Fallback a simulación si el navegador falla
            logger.warning(f"Browser Controller falló, usando simulación: {job_id}")
            await simulate_generation(job_id, request)
            
    except Exception as e:
        logger.error(f"Error en generación con navegador: {e}")
        # Fallback a simulación
        try:
            await simulate_generation(job_id, request)
        except Exception as fallback_error:
            logger.error(f"Error en fallback: {fallback_error}")
            generation_jobs[job_id]["status"] = "failed"
            generation_jobs[job_id]["error"] = str(e)

async def generate_with_multi_account(job_id: str, request: GenerateRequest):
    """Generar música con múltiples cuentas de Suno (máxima evasión)"""
    try:
        logger.info(f"🎵 [MULTI] Generando música con múltiples cuentas: {job_id}")
        
        # Actualizar progreso
        generation_jobs[job_id]["progress"] = 20
        generation_jobs[job_id]["status"] = "processing"
        
        # Generar música con múltiples cuentas
        result = await generate_music_with_multi_account(
            prompt=request.prompt,
            lyrics=request.lyrics,
            style=request.style
        )
        
        if result.get("success"):
            # Crear track
            track_id = f"multi_{uuid.uuid4().hex[:8]}"
            track = TrackInfo(
                id=track_id,
                title=f"Multi: {request.prompt[:50]}...",
                filename="suno_multi.mp3",
                audio_url=f"/api/tracks/{track_id}/audio",
                lyrics=result.get("lyrics", request.lyrics),
                prompt=request.prompt,
                style=request.style,
                created_at=datetime.now().isoformat(),
                duration=180  # 3 minutos de música real
            )
            
            # Guardar track
            current_tracks.append(track)
            
            # Actualizar trabajo
            generation_jobs[job_id]["status"] = "completed"
            generation_jobs[job_id]["progress"] = 100
            generation_jobs[job_id]["track_id"] = track_id
            generation_jobs[job_id]["audio_url"] = track.audio_url
            generation_jobs[job_id]["mode"] = "multi_account"
            generation_jobs[job_id]["account_used"] = result.get("account_used", "unknown")
            
            logger.info(f"✅ [MULTI] Música generada con {result.get('account_used', 'unknown')}: {job_id}")
        else:
            logger.warning(f"⚠️ [MULTI] Falló: {result.get('error')}")
            logger.warning(f"Multi Account falló, usando Suno Stealth: {job_id}")
            await generate_with_suno_stealth(job_id, request)
            
    except Exception as e:
        logger.error(f"❌ [MULTI] Error generando música: {e}")
        logger.warning(f"Multi Account falló, usando Suno Stealth: {job_id}")
        await generate_with_suno_stealth(job_id, request)

async def generate_with_suno_stealth(job_id: str, request: GenerateRequest):
    """Generar música real con Suno Stealth (indetectable)"""
    try:
        logger.info(f"🎵 [STEALTH] Generando música real indetectable: {job_id}")
        
        # Actualizar progreso
        generation_jobs[job_id]["progress"] = 20
        generation_jobs[job_id]["status"] = "processing"
        
        # Generar música con Suno Stealth
        result = await generate_music_with_suno_stealth(
            prompt=request.prompt,
            lyrics=request.lyrics,
            style=request.style
        )
        
        if result.get("success"):
            # Crear track
            track_id = f"stealth_{uuid.uuid4().hex[:8]}"
            track = TrackInfo(
                id=track_id,
                title=f"Stealth: {request.prompt[:50]}...",
                filename="suno_stealth.mp3",
                audio_url=f"/api/tracks/{track_id}/audio",
                lyrics=result.get("lyrics", request.lyrics),
                prompt=request.prompt,
                style=request.style,
                created_at=datetime.now().isoformat(),
                duration=180  # 3 minutos de música real
            )
            
            # Guardar track
            current_tracks.append(track)
            
            # Actualizar trabajo
            generation_jobs[job_id]["status"] = "completed"
            generation_jobs[job_id]["progress"] = 100
            generation_jobs[job_id]["track_id"] = track_id
            generation_jobs[job_id]["audio_url"] = track.audio_url
            generation_jobs[job_id]["mode"] = "suno_stealth"
            
            logger.info(f"✅ [STEALTH] Música real generada: {job_id}")
        else:
            logger.warning(f"⚠️ [STEALTH] Falló: {result.get('error')}")
            logger.warning(f"Suno Stealth falló, usando Suno Real: {job_id}")
            await generate_with_suno_real(job_id, request)
            
    except Exception as e:
        logger.error(f"❌ [STEALTH] Error generando música: {e}")
        logger.warning(f"Suno Stealth falló, usando Suno Real: {job_id}")
        await generate_with_suno_real(job_id, request)

async def generate_with_suno_real(job_id: str, request: GenerateRequest):
    """Generar música real en Suno.com"""
    try:
        logger.info(f"Iniciando generación real en Suno: {job_id}")
        
        # Actualizar progreso
        generation_jobs[job_id]["progress"] = 10
        generation_jobs[job_id]["status"] = "processing"
        
        # Generar música en Suno
        generation_jobs[job_id]["progress"] = 30
        logger.info(f"Enviando a Suno Real: {job_id}")
        
        result = await generate_music_in_suno_real(
            request.prompt,
            request.lyrics,
            request.style
        )
        
        if result and result.get("success"):
            # Crear track con URL de Suno
            track_id = f"suno_{uuid.uuid4().hex[:8]}"
            track = TrackInfo(
                id=track_id,
                title=f"Suno: {request.prompt[:50]}...",
                filename=f"{track_id}.mp3",
                audio_url=result.get("audio_url", f"/api/tracks/{track_id}/audio"),
                lyrics=request.lyrics or "Generated lyrics",
                prompt=request.prompt,
                style=request.style,
                created_at=datetime.now().isoformat(),
                duration=180
            )
            
            # Agregar URL de Suno si está disponible
            if result.get("suno_url"):
                track.suno_url = result.get("suno_url")
            
            current_tracks.append(track)
            generation_jobs[job_id]["status"] = "completed"
            generation_jobs[job_id]["track_id"] = track_id
            generation_jobs[job_id]["progress"] = 100
            generation_jobs[job_id]["result"] = result
            
            logger.info(f"Generación real en Suno completada: {job_id}")
        else:
            # Fallback a simulación si Suno falla
            logger.warning(f"Suno Real falló, usando simulación: {job_id}")
            await simulate_generation(job_id, request)
            
    except Exception as e:
        logger.error(f"Error en generación real en Suno: {e}")
        # Fallback a simulación
        try:
            await simulate_generation(job_id, request)
        except Exception as fallback_error:
            logger.error(f"Error en fallback: {fallback_error}")
            generation_jobs[job_id]["status"] = "failed"
            generation_jobs[job_id]["error"] = str(e)

@app.get("/api/music/status/{job_id}")
async def get_generation_status(job_id: str):
    """Obtener estado de generación"""
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return generation_jobs[job_id]

@app.get("/api/tracks")
async def get_tracks():
    """Obtener lista de tracks"""
    return {
        "tracks": current_tracks,
        "total": len(current_tracks)
    }

@app.get("/api/tracks/{track_id}/audio")
async def get_track_audio(track_id: str):
    """Obtener audio del track"""
    try:
        # Buscar el track
        track = next((t for t in current_tracks if t.id == track_id), None)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Buscar archivo de audio real
        audio_file = None
        
        # Buscar por nombre de archivo
        if track.filename:
            audio_path = AUDIO_DIR / track.filename
            if audio_path.exists():
                audio_file = audio_path
        
        # Buscar por patrón de nombre (mp3 y wav)
        if not audio_file:
            for pattern in ["*.mp3", "*.wav"]:
                for file_path in AUDIO_DIR.glob(pattern):
                    if track_id in file_path.name or track_id.replace("track_", "") in file_path.name:
                        audio_file = file_path
                        break
                if audio_file:
                    break
        
        # Buscar archivo más reciente si no se encuentra específico
        if not audio_file:
            audio_files = list(AUDIO_DIR.glob("*.mp3")) + list(AUDIO_DIR.glob("*.wav"))
            if audio_files:
                audio_file = max(audio_files, key=lambda x: x.stat().st_mtime)
        
        if audio_file and audio_file.exists():
            return FileResponse(
                path=str(audio_file),
                media_type="audio/mpeg",
                filename=track.filename or f"{track_id}.mp3"
            )
        else:
            # Fallback: devolver mensaje si no hay archivo
            return {"message": f"Audio para track {track_id} no encontrado", "track_id": track_id}
            
    except Exception as e:
        logger.error(f"Error obteniendo audio para {track_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tracks/{track_id}")
async def get_track(track_id: str):
    """Obtener información del track"""
    track = next((t for t in current_tracks if t.id == track_id), None)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track

# Endpoints para extensión de Chrome
@app.post("/api/extension/generate")
async def extension_generate_music(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Endpoint para generación desde extensión de Chrome"""
    try:
        logger.info(f"🎵 Solicitud de generación desde extensión: {request.prompt}")
        
        # Usar el mismo sistema de generación
        job_id = f"ext_{uuid.uuid4().hex[:12]}"
        
        # Crear registro de trabajo
        generation_jobs[job_id] = {
            "id": job_id,
            "status": "processing",
            "prompt": request.prompt,
            "lyrics": request.lyrics,
            "style": request.style,
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "source": "extension"
        }
        
        # Prioridad: Ollama Proxy > Suno Real > Browser Controller > Simulación
        if OLLAMA_AVAILABLE and ollama_proxy:
            background_tasks.add_task(generate_with_ollama, job_id, request)
            message = "Generación iniciada con Ollama-Suno Proxy"
        elif SUNO_REAL_AVAILABLE:
            background_tasks.add_task(generate_with_suno_real, job_id, request)
            message = "Generación iniciada con Suno Real (aparecerá en tu biblioteca)"
        elif BROWSER_CONTROLLER_AVAILABLE:
            background_tasks.add_task(generate_with_browser, job_id, request)
            message = "Generación iniciada con Ollama Browser Controller"
        else:
            background_tasks.add_task(simulate_generation, job_id, request)
            message = "Generación iniciada (modo simulación)"
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": message,
            "source": "extension"
        }
        
    except Exception as e:
        logger.error(f"Error en generación desde extensión: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/extension/status")
async def extension_status():
    """Estado del sistema para la extensión"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "browser_controller_available": BROWSER_CONTROLLER_AVAILABLE,
        "ollama_available": OLLAMA_AVAILABLE,
        "active_jobs": len([j for j in generation_jobs.values() if j["status"] == "processing"]),
        "tracks_available": len(current_tracks)
    }

# Función de limpieza periódica
async def cleanup_old_jobs():
    """Limpiar trabajos antiguos"""
    while True:
        try:
            current_time = time.time()
            cutoff_time = current_time - 3600  # 1 hora
            
            # Limpiar trabajos completados antiguos
            old_jobs = [
                job_id for job_id, job in generation_jobs.items()
                if job["status"] in ["completed", "failed"] and
                datetime.fromisoformat(job["created_at"]).timestamp() < cutoff_time
            ]
            
            for job_id in old_jobs:
                del generation_jobs[job_id]
            
            if old_jobs:
                logger.info(f"Limpiados {len(old_jobs)} trabajos antiguos")
            
            await asyncio.sleep(300)  # Limpiar cada 5 minutos
            
        except Exception as e:
            logger.error(f"Error en limpieza: {e}")
            await asyncio.sleep(300)

# Inicialización
start_time = time.time()

@app.on_event("startup")
async def startup_event():
    """Evento de inicio"""
    logger.info("🎵 Son1k Simple Stable iniciando...")
    logger.info("✅ Sistema simplificado cargado")
    logger.info("🚀 ¡Sistema listo para generar música!")
    
    # Iniciar tarea de limpieza
    asyncio.create_task(cleanup_old_jobs())

async def generate_with_real_music(job_id: str, request: GenerateRequest):
    """Generar música real sintetizada"""
    try:
        logger.info(f"🎵 Generando música real sintetizada: {job_id}")
        
        # Actualizar progreso
        generation_jobs[job_id]["progress"] = 20
        generation_jobs[job_id]["status"] = "processing"
        
        # Generar música real
        audio_file = generate_real_music(
            prompt=request.prompt,
            lyrics=request.lyrics,
            style=request.style
        )
        
        # Crear track
        track_id = f"track_{uuid.uuid4().hex[:8]}"
        track = TrackInfo(
            id=track_id,
            title=f"Generated: {request.prompt[:50]}...",
            filename=os.path.basename(audio_file),
            audio_url=f"/api/tracks/{track_id}/audio",
            lyrics=request.lyrics,
            prompt=request.prompt,
            style=request.style,
            created_at=datetime.now().isoformat(),
            duration=30  # 30 segundos de música real
        )
        
        # Guardar track
        current_tracks.append(track)
        
        # Actualizar trabajo
        generation_jobs[job_id]["status"] = "completed"
        generation_jobs[job_id]["progress"] = 100
        generation_jobs[job_id]["track_id"] = track_id
        generation_jobs[job_id]["audio_url"] = track.audio_url
        generation_jobs[job_id]["mode"] = "real_music"
        
        logger.info(f"✅ Música real sintetizada completada: {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Error generando música real: {e}")
        logger.warning(f"Real Music falló, usando simulación: {job_id}")
        await simulate_generation(job_id, request)

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre"""
    logger.info("🛑 Son1k Simple Stable finalizando...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
