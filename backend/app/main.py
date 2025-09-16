from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from .settings import settings
from .queue import enqueue_generation
from .db import init_db, SessionLocal
from . import models
from .deps import rate_limiter
from .ws import router as ws_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ORIGINS == "*" else settings.CORS_ORIGINS.split(","),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(ws_router)

class CreateSong(BaseModel):
    prompt: Optional[str] = None
    lyrics: Optional[str] = None
    style: Optional[str] = None
    length_sec: int = 60
    mode: str = "original"  # original | promptless
    postprocessing: Optional[dict] = None

class WebhookResult(BaseModel):
    src: str
    prompt: Optional[str] = None
    ts: int

@app.on_event("startup")
def on_start():
    init_db()

@app.get(f"{settings.API_PREFIX}/health")
def health():
    return {"ok": True}

@app.post(f"{settings.API_PREFIX}/songs/create")
def create_song(payload: CreateSong, user_id: str = Depends(rate_limiter(30))):
    job_id = enqueue_generation(payload.dict())
    return {"ok": True, "job_id": job_id}

@app.get(f"{settings.API_PREFIX}/songs/status/{{job_id}}")
def status(job_id: str):
    return {"job_id": job_id, "status": "queued"}  # TODO: real status

@app.post(f"{settings.API_PREFIX}/suno/results")
def suno_results(r: WebhookResult):
    # TODO: persist in DB, create Song/Asset rows, trigger process_audio
    print("SUNO RESULT:", r.dict())
    return {"ok": True}

# Verificar si el directorio frontend existe
frontend_path = "../frontend"
if os.path.exists(frontend_path):
    # Servir archivos estáticos del frontend
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    
    # Servir index.html en la raíz
    @app.get("/")
    def serve_frontend():
        return FileResponse(f"{frontend_path}/index.html")
else:
    # Fallback si no existe el directorio frontend
    @app.get("/")
    def root():
        return {
            "mensaje": "Son1kVers3 Suno Bridge - Backend funcionando",
            "estado": "ok",
            "ruta_frontend": "/frontend",
            "existencia_frontend": "falso"
        }
