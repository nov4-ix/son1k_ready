"""
🎵 Music Generation Router
Router comercial para generación de música transparente
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import time
import logging
import asyncio
from datetime import datetime

from backend.selenium_worker.music_generator_fixed import MusicGeneratorFixed, SongNameGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/music", tags=["music"])

# Modelo para requests de generación
class MusicGenerationRequest(BaseModel):
    lyrics: str
    prompt: str
    instrumental: Optional[bool] = False
    style: Optional[str] = "default"
    user_id: Optional[str] = None

class MusicGenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str
    tracks: Optional[List[dict]] = None
    estimated_time: Optional[int] = None

# Store activo de engines
active_engines = {}

def ensure_transparent_results(results: List[dict], lyrics: str, job_id: str) -> List[dict]:
    """Asegurar transparencia total en resultados"""
    if not results:
        return results
    
    transparent_results = []
    
    for i, track in enumerate(results):
        # Generar nombre dinámico basado en lyrics
        dynamic_name = SongNameGenerator.generate_name_from_lyrics(lyrics)
        
        # Si hay múltiples tracks, agregar identificador
        if len(results) > 1:
            dynamic_name += f" - Parte {i+1}"
        
        # Crear resultado completamente transparente
        transparent_track = {
            "id": f"son1k_track_{int(time.time())}_{i+1}",
            "title": dynamic_name,  # NOMBRE DINÁMICO
            "duration": track.get("duration", "Unknown"),
            "url": track.get("url"),
            "download_url": track.get("download_url") or track.get("url"),
            "generated_at": int(time.time()),
            "provider": "Son1k",  # NUNCA mencionar suno
            "job_id": job_id.replace("suno", "son1k"),  # Limpiar cualquier referencia
            "filename": f"{dynamic_name.replace(' ', '_')}.mp3",
            "lyrics_preview": lyrics[:100] + "..." if len(lyrics) > 100 else lyrics
        }
        
        transparent_results.append(transparent_track)
        logger.info(f"✅ Track transparente creado: {dynamic_name}")
    
    return transparent_results

def get_or_create_engine() -> MusicGeneratorFixed:
    """Obtener o crear engine comercial fijo"""
    engine_id = "primary"
    
    if engine_id not in active_engines:
        active_engines[engine_id] = MusicGeneratorFixed()
    
    return active_engines[engine_id]

async def background_generation(job_id: str, lyrics: str, prompt: str, instrumental: bool):
    """Tarea en background para generación"""
    try:
        logger.info(f"Iniciando generación background para {job_id}")
        
        engine = get_or_create_engine()
        results = engine.generate_music(lyrics, prompt, job_id, instrumental)
        
        if results:
            # Asegurar naming dinámico y transparencia total
            results = ensure_transparent_results(results, lyrics, job_id)
            logger.info(f"Generación exitosa para {job_id}: {len(results)} tracks")
            # Aquí podrías guardar en base de datos si necesitas
        else:
            logger.error(f"Generación falló para {job_id}")
            
    except Exception as e:
        logger.error(f"Error en generación background: {e}")

@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(
    request: MusicGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Endpoint principal para generación de música
    Proceso completamente transparente para el usuario
    """
    try:
        # Generar job ID único (SIN referencias a suno)
        job_id = f"son1k_job_{int(time.time())}"
        
        logger.info(f"Nueva solicitud de generación: {job_id}")
        logger.info(f"Lyrics: {len(request.lyrics)} chars, Prompt: {request.prompt}")
        
        # Validaciones
        if not request.instrumental and not request.lyrics.strip():
            raise HTTPException(
                status_code=400,
                detail="Lyrics requeridas para modo no instrumental"
            )
        
        if not request.prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="Prompt de estilo requerido"
            )
        
        # Verificar engine disponible
        engine = get_or_create_engine()
        if not engine.initialize_driver():
            raise HTTPException(
                status_code=503,
                detail="Motor de generación no disponible"
            )
        
        # Iniciar generación en background
        background_tasks.add_task(
            background_generation,
            job_id,
            request.lyrics,
            request.prompt,
            request.instrumental
        )
        
        return MusicGenerationResponse(
            job_id=job_id,
            status="processing",
            message="Generación iniciada exitosamente",
            estimated_time=180  # 3 minutos estimados
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en endpoint de generación: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.get("/status/{job_id}")
async def get_generation_status(job_id: str):
    """Obtener estado de generación"""
    try:
        # Verificar estado en el sistema de CAPTCHA
        import requests
        response = requests.get(f"http://localhost:8000/api/captcha/status/{job_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            status_map = {
                "STARTED": "processing",
                "NEEDED": "captcha_required",
                "RESOLVED": "generating", 
                "COMPLETED": "completed",
                "ERROR": "failed"
            }
            
            return {
                "job_id": job_id,
                "status": status_map.get(data.get("status"), "unknown"),
                "message": f"Estado: {data.get('status')}",
                "progress": get_progress_from_status(data.get("status"))
            }
        
        return {
            "job_id": job_id,
            "status": "not_found",
            "message": "Job no encontrado"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return {
            "job_id": job_id,
            "status": "error",
            "message": "Error obteniendo estado"
        }

def get_progress_from_status(status: str) -> int:
    """Mapear estado a progreso porcentual"""
    progress_map = {
        "STARTED": 20,
        "NEEDED": 40,
        "RESOLVED": 70,
        "COMPLETED": 100,
        "ERROR": 0
    }
    return progress_map.get(status, 0)

@router.get("/health")
async def health_check():
    """Health check para el servicio de música"""
    try:
        engine = get_or_create_engine()
        available = engine.initialize_driver() if not engine.driver else True
        
        return {
            "status": "healthy" if available else "degraded",
            "service": "music_generation",
            "engine_available": available,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "unhealthy",
            "service": "music_generation",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/test")
async def test_generation():
    """Endpoint de prueba para verificar funcionamiento"""
    try:
        engine = get_or_create_engine()
        
        if not engine.initialize_driver():
            return {"status": "error", "message": "No se pudo inicializar driver"}
        
        if not engine.check_session():
            return {"status": "warning", "message": "No hay sesión activa en Suno"}
        
        return {"status": "success", "message": "Sistema listo para generación"}
        
    except Exception as e:
        logger.error(f"Error en test: {e}")
        return {"status": "error", "message": str(e)}