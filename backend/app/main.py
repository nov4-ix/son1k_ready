from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .settings import settings
from .queue import enqueue_generation
from .queue_commercial import enqueue_generation as enqueue_commercial, get_job_status, job_manager
from . import models
from .deps import rate_limiter
from .ws import router as ws_router
from .auth import (
    create_user, authenticate_user, create_access_token, 
    get_current_user, get_user_limits
)


# --- Inicializa la app ---
app = FastAPI(title=settings.PROJECT_NAME)

# --- Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS] if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket router ---
app.include_router(ws_router, prefix="/ws")


# --- Healthcheck ---
@app.get("/api/health")
def health():
    return {"ok": True}


# --- Authentication endpoints ---
@app.post("/api/auth/register")
def register(user_data: models.UserCreate):
    """Register new user"""
    try:
        user = create_user(user_data.email, user_data.password, user_data.name)
        token = create_access_token(user.id, user.email)
        limits = get_user_limits(user)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": getattr(user, 'name', None),
                "plan": user.plan,
                "daily_usage": user.daily_usage,
                "daily_limit": limits["daily_limit"],
                "monthly_usage": user.monthly_usage,
                "monthly_limit": limits["monthly_limit"],
                "created_at": user.created_at
            }
        }
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/api/auth/login")
def login(login_data: models.UserLogin):
    """Login user"""
    user = authenticate_user(login_data.email, login_data.password)
    if not user:
        return {"error": "Invalid credentials"}, 401
    
    token = create_access_token(user.id, user.email)
    limits = get_user_limits(user)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": getattr(user, 'name', None),
            "plan": user.plan,
            "daily_usage": user.daily_usage,
            "daily_limit": limits["daily_limit"],
            "monthly_usage": user.monthly_usage,
            "monthly_limit": limits["monthly_limit"],
            "created_at": user.created_at
        }
    }

@app.get("/api/auth/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    """Get current user info"""
    limits = get_user_limits(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": getattr(current_user, 'name', None),
        "plan": current_user.plan,
        "daily_usage": current_user.daily_usage,
        "daily_limit": limits["daily_limit"],
        "monthly_usage": current_user.monthly_usage,
        "monthly_limit": limits["monthly_limit"],
        "can_create_job": limits["can_create_job"],
        "created_at": current_user.created_at
    }

# --- Endpoint para crear canciones (Comercial) ---
@app.post("/api/songs/create")
def create_song(payload: models.SongCreate, current_user: models.User = Depends(get_current_user)):
    """Create commercial job with rate limiting and quota checking"""
    # Check user limits
    limits = get_user_limits(current_user)
    if not limits["can_create_job"]:
        return {"ok": False, "error": "Daily or monthly limit exceeded"}, 429
    
    # Create job for authenticated user
    job_id = enqueue_commercial(payload.dict(), user_id=current_user.id)
    if job_id:
        return {"ok": True, "job_id": job_id}
    else:
        return {"ok": False, "error": "Failed to create job"}, 500

# --- Job Management Endpoints ---
@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    """Get job status and details"""
    job_data = get_job_status(job_id)
    if job_data:
        return job_data
    else:
        return {"error": "Job not found"}, 404

@app.post("/api/jobs/{job_id}/retry")
def retry_job(job_id: str):
    """Manually retry a failed job"""
    success = job_manager.retry_failed_job(job_id)
    if success:
        return {"ok": True, "message": "Job retry scheduled"}
    else:
        return {"ok": False, "error": "Cannot retry job"}, 400

# --- User Quota Endpoints ---
@app.get("/api/users/{user_id}/quota")
def get_user_quota(user_id: str):
    """Get user's current quota and usage"""
    try:
        from .db import get_db_session
        from .models import User, PLAN_LIMITS, UserPlan
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}, 404
            
            plan_config = PLAN_LIMITS.get(user.plan, PLAN_LIMITS[UserPlan.FREE])
            
            return {
                "user_id": user_id,
                "plan": user.plan,
                "daily_usage": user.daily_usage,
                "daily_limit": plan_config["daily_limit"],
                "monthly_usage": user.monthly_usage,
                "monthly_limit": plan_config["monthly_limit"],
                "concurrent_jobs": plan_config["concurrent_jobs"],
                "can_create_job": job_manager._check_user_quota(user_id)
            }
    except Exception as e:
        return {"error": str(e)}, 500

# --- Worker Management Endpoints ---
@app.get("/api/jobs/pending")
def get_pending_jobs(worker_id: str):
    """Get pending jobs for extension worker (simplified endpoint)"""
    job_data = job_manager.get_next_job_for_worker(worker_id)
    if job_data:
        return job_data
    else:
        return {"message": "No jobs available"}

@app.get("/api/worker/jobs/next")
def get_next_job(worker_id: str):
    """Get next job for extension worker"""
    job_data = job_manager.get_next_job_for_worker(worker_id)
    if job_data:
        return job_data
    else:
        return {"message": "No jobs available"}

@app.post("/api/jobs/{job_id}/complete")
def complete_job(job_id: str, result_data: dict):
    """Mark job as completed with results"""
    try:
        job_manager.update_job_status(
            job_id, 
            "completed",
            audio_url=result_data.get("audio_url"),
            preview_url=result_data.get("preview_url"),
            result_data=result_data
        )
        return {"ok": True, "message": "Job completed successfully"}
    except Exception as e:
        return {"ok": False, "error": str(e)}, 500

@app.post("/api/worker/heartbeat")
def worker_heartbeat(heartbeat: models.WorkerHeartbeat):
    """Extension worker heartbeat"""
    try:
        from .db import get_db_session
        from .models import Worker
        from datetime import datetime
        
        with get_db_session() as db:
            worker = db.query(Worker).filter(Worker.id == heartbeat.worker_id).first()
            if not worker:
                # Create new worker
                worker = Worker(
                    id=heartbeat.worker_id,
                    status=heartbeat.status,
                    last_heartbeat=datetime.utcnow(),
                    jobs_completed=heartbeat.jobs_completed or 0,
                    jobs_failed=heartbeat.jobs_failed or 0
                )
                db.add(worker)
            else:
                # Update existing worker
                worker.status = heartbeat.status
                worker.last_heartbeat = datetime.utcnow()
                worker.last_job_id = heartbeat.current_job_id
                if heartbeat.jobs_completed is not None:
                    worker.jobs_completed = heartbeat.jobs_completed
                if heartbeat.jobs_failed is not None:
                    worker.jobs_failed = heartbeat.jobs_failed
                if heartbeat.version:
                    worker.version = heartbeat.version
            
            db.commit()
            return {"ok": True, "message": "Heartbeat received"}
            
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/api/jobs/{job_id}/update")
def update_job_status(job_id: str, update_data: dict):
    """Update job status from worker"""
    try:
        status = update_data.get("status")
        if status:
            # Remove status from update_data to avoid duplicate keyword argument
            extra_data = {k: v for k, v in update_data.items() if k != "status"}
            job_manager.update_job_status(job_id, status, **extra_data)
            return {"ok": True, "message": "Job status updated"}
        else:
            return {"error": "Status required"}, 400
    except Exception as e:
        return {"error": str(e)}, 500


# --- Endpoints para funciones de IA ---
@app.post("/api/generate-lyrics")
def generate_lyrics(request: dict):
    """Generar letras basadas en un prompt musical"""
    prompt = request.get("prompt", "")
    
    # Análisis básico del prompt para generar letra coherente
    lyrics_templates = {
        "balada": "Verso 1:\nEn la quietud de la noche\nTu recuerdo me acompaña\nCada estrella que destella\nHabla de lo que el alma extraña\n\nCoro:\nEsta es nuestra balada\nEscrita en el viento\nUn amor que trasciende\nTodo momento\n\nVerso 2:\nLas palabras se escapan\nComo hojas al volar\nPero el corazón no olvida\nLo que vino a encontrar",
        
        "rock": "Verso 1:\nEl asfalto bajo mis pies\nLa ciudad que no duerme\nCon guitarras que gritan\nLa verdad que nos duele\n\nCoro:\nRompemos las cadenas\nCon el poder del rock\nNuestra música es rebelde\nNo hay nada que nos frene\n\nVerso 2:\nLos amplificadores\nDevoran el silencio\nY en cada acorde\nNace nuestro momento",
        
        "pop": "Verso 1:\nLuces de neón\nIluminan la noche\nBailo sin pensar\nEn lo que puede importar\n\nCoro:\nEsta es mi canción\nPara bailar sin parar\nRitmo en el corazón\nNada nos va a detener\n\nVerso 2:\nLa música nos lleva\nA un lugar especial\nDonde todo es posible\nY el tiempo es ideal"
    }
    
    # Detectar estilo basado en palabras clave
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["balada", "emotiv", "piano", "lento", "romantic"]):
        lyrics = lyrics_templates["balada"]
    elif any(word in prompt_lower for word in ["rock", "guitar", "energetic", "fuerte", "rebel"]):
        lyrics = lyrics_templates["rock"]
    elif any(word in prompt_lower for word in ["pop", "alegre", "bailar", "dance", "upbeat"]):
        lyrics = lyrics_templates["pop"]
    else:
        # Letra genérica basada en el prompt
        lyrics = f"Verso 1:\n{prompt} me inspira\nCada nota que resuena\nEn mi corazón se aviva\nUna melodía serena\n\nCoro:\nEsta es mi canción\nNacida de la pasión\nCon {prompt}\nHallo mi dirección\n\nVerso 2:\nLas palabras fluyen\nComo ríos al mar\nY en cada verso\nEncuentro mi lugar"
    
    return {"lyrics": lyrics}


@app.post("/api/improve-lyrics")
def improve_lyrics(request: dict):
    """Mejorar letras existentes"""
    lyrics = request.get("lyrics", "")
    
    if not lyrics:
        return {"improved_lyrics": lyrics}
    
    # Mejoras básicas: capitalización, estructura
    lines = lyrics.split('\n')
    improved_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Capitalizar primera letra
            if line and line[0].islower():
                line = line[0].upper() + line[1:]
            # Agregar estructura si no está presente
            if not any(marker in line.lower() for marker in ['verso', 'coro', 'puente', 'estribillo']):
                improved_lines.append(line)
            else:
                improved_lines.append(f"[{line}]" if not line.startswith('[') else line)
        else:
            improved_lines.append('')
    
    improved_lyrics = '\n'.join(improved_lines)
    
    # Si las letras son muy cortas, sugerir expansión
    if len(lines) < 8:
        improved_lyrics += "\n\n[Sugerencia: Considera agregar un puente o segundo verso para mayor estructura]"
    
    return {"improved_lyrics": improved_lyrics}


@app.post("/api/smart-prompt")  
def smart_prompt(request: dict):
    """Generar prompt inteligente basado en letras"""
    lyrics = request.get("lyrics", "")
    
    if not lyrics:
        return {"smart_prompt": "Una balada emotiva con instrumentación rica, tempo medio, expresión vocal intensa"}
    
    lyrics_lower = lyrics.lower()
    
    # Análisis de sentimiento y temas
    sentiment_analysis = {
        "romantic": ["amor", "corazón", "beso", "abrazo", "te amo", "cariño", "pasión"],
        "sad": ["triste", "llorar", "dolor", "perdón", "adiós", "soledad", "lágrimas"],
        "happy": ["alegr", "feliz", "risa", "bailar", "celebrar", "sonr", "fiesta"],
        "energetic": ["fuerte", "poder", "lucha", "rebeld", "grita", "rock", "energía"],
        "peaceful": ["paz", "calma", "quiet", "sereno", "suave", "tranquil", "descanso"]
    }
    
    # Detectar instrumentos mencionados
    instruments = {
        "piano": ["piano", "teclas"],
        "guitar": ["guitarra", "guitar", "acord"],
        "strings": ["cuerda", "violín", "orquesta"],
        "drums": ["batería", "percus", "ritmo"],
        "electronic": ["sintetizador", "electr", "digital"]
    }
    
    # Construir prompt
    prompt_parts = []
    
    # Determinar estilo emocional
    sentiment_scores = {}
    for sentiment, keywords in sentiment_analysis.items():
        score = sum(1 for keyword in keywords if keyword in lyrics_lower)
        if score > 0:
            sentiment_scores[sentiment] = score
    
    if sentiment_scores:
        dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        if dominant_sentiment == "romantic":
            prompt_parts.append("Una balada romántica")
        elif dominant_sentiment == "sad":
            prompt_parts.append("Una canción melancólica")
        elif dominant_sentiment == "happy":
            prompt_parts.append("Una canción alegre y optimista")
        elif dominant_sentiment == "energetic":
            prompt_parts.append("Una canción enérgica y poderosa")
        elif dominant_sentiment == "peaceful":
            prompt_parts.append("Una canción suave y serena")
    else:
        prompt_parts.append("Una canción emotiva")
    
    # Detectar instrumentación
    detected_instruments = []
    for instrument, keywords in instruments.items():
        if any(keyword in lyrics_lower for keyword in keywords):
            detected_instruments.append(instrument)
    
    if detected_instruments:
        if "piano" in detected_instruments:
            prompt_parts.append("con piano expresivo")
        if "guitar" in detected_instruments:
            prompt_parts.append("con guitarras emotivas")
        if "strings" in detected_instruments:
            prompt_parts.append("con arreglos de cuerdas")
        if "electronic" in detected_instruments:
            prompt_parts.append("con elementos electrónicos")
    else:
        prompt_parts.append("con instrumentación rica")
    
    # Determinar tempo
    if any(word in lyrics_lower for word in ["baila", "rápido", "energía", "fiesta"]):
        prompt_parts.append("tempo allegro")
    elif any(word in lyrics_lower for word in ["lento", "suave", "calma", "tranquil"]):
        prompt_parts.append("tempo lento")
    else:
        prompt_parts.append("tempo medio")
    
    # Determinar tipo de voz
    word_count = len(lyrics.split())
    if word_count > 100:
        prompt_parts.append("voz expresiva con matices dinámicos")
    else:
        prompt_parts.append("voz íntima y expresiva")
    
    smart_prompt = ", ".join(prompt_parts)
    
    return {"smart_prompt": smart_prompt}


# --- Endpoints de estado del sistema ---
@app.get("/api/celery-status")
def celery_status():
    """Verificar estado de Celery"""
    try:
        from .queue import celery_app
        # Intentar obtener estadísticas de workers activos
        stats = celery_app.control.inspect().stats()
        if stats:
            return {"status": "active", "workers": len(stats)}
        else:
            return {"status": "no_workers"}, 503
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 503


@app.get("/api/redis-status") 
def redis_status():
    """Verificar estado de Redis"""
    try:
        from .queue import celery_app
        # Intentar conectar a Redis a través de Celery
        result = celery_app.control.ping()
        if result:
            return {"status": "connected", "ping": "pong"}
        else:
            return {"status": "no_response"}, 503
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 503


# --- Static/frontend mounting robusto ---
BASE_DIR = Path(__file__).resolve().parent.parent      # /app/backend
FRONTEND_DIR = (BASE_DIR.parent / "frontend").resolve()  # /app/frontend

if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
    # Sirve todo el /frontend en /frontend y el index en "/"
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

    @app.get("/")
    def serve_frontend():
        from fastapi.responses import FileResponse
        response = FileResponse(str(FRONTEND_DIR / "index.html"))
        # Forzar no-cache para evitar problemas de caché
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    # Favicon
    @app.get("/favicon.ico")
    def favicon():
        favicon_path = FRONTEND_DIR / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(str(favicon_path))
        else:
            # Fallback to a default or return 404
            return {"error": "favicon not found"}
else:
    @app.get("/")
    def root():
        return {
            "mensaje": "Son1kVers3 Suno Bridge - Backend funcionando",
            "estado": "ok",
            "ruta_frontend": "/frontend",
            "existencia_frontend": "falso",
            "frontend_dir": str(FRONTEND_DIR),
            "frontend_exists": FRONTEND_DIR.exists(),
            "index_exists": (FRONTEND_DIR / "index.html").exists() if FRONTEND_DIR.exists() else False
        }

