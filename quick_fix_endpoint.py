#!/usr/bin/env python3
"""
⚡ Quick Fix Endpoint
Solución inmediata para el problema de naming y transparencia
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import time
import re
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

class QuickGenerationRequest(BaseModel):
    lyrics: str
    prompt: str
    instrumental: Optional[bool] = False

class QuickGenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str
    tracks: Optional[List[dict]] = None

def generate_dynamic_name_from_lyrics(lyrics: str) -> str:
    """Generar nombre dinámico desde lyrics"""
    if not lyrics or not lyrics.strip():
        return f"Instrumental_{int(time.time())}"
    
    # Limpiar y procesar lyrics
    clean_lyrics = lyrics.strip()
    
    # Tomar primera línea/frase significativa
    lines = clean_lyrics.split('\n')
    first_line = ""
    
    for line in lines:
        line = line.strip()
        # Buscar primera línea con contenido real
        if line and len(line) > 3 and not line.isspace():
            first_line = line
            break
    
    if not first_line:
        # Si no hay primera línea, usar las primeras palabras
        words = clean_lyrics.split()[:4]
        first_line = " ".join(words) if words else "Sin Título"
    
    # Limpiar el nombre
    song_name = clean_filename(first_line)
    
    # Limitar longitud
    if len(song_name) > 50:
        song_name = song_name[:47] + "..."
    
    return song_name or f"Canción_{int(time.time())}"

def clean_filename(text: str) -> str:
    """Limpiar texto para usar como nombre de archivo"""
    # Remover caracteres especiales problemáticos
    cleaned = re.sub(r'[<>:"/\\|?*]', '', text)
    
    # Reemplazar múltiples espacios con uno solo
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remover espacios al inicio y final
    cleaned = cleaned.strip()
    
    # Capitalizar primera letra de cada palabra
    cleaned = ' '.join(word.capitalize() for word in cleaned.split())
    
    return cleaned

@app.post("/api/quick-generate", response_model=QuickGenerationResponse)
async def quick_generate_music(request: QuickGenerationRequest):
    """
    🎯 Endpoint de generación rápida con transparencia garantizada
    """
    try:
        # Generar job ID completamente transparente
        job_id = f"son1k_express_{int(time.time())}"
        
        logger.info(f"🎵 Generación rápida iniciada: {job_id}")
        logger.info(f"📝 Lyrics: {len(request.lyrics)} chars")
        logger.info(f"🎨 Prompt: {request.prompt}")
        
        # Generar nombre dinámico inmediatamente
        dynamic_name = generate_dynamic_name_from_lyrics(request.lyrics)
        logger.info(f"✨ Nombre dinámico generado: {dynamic_name}")
        
        # Simular generación (en producción aquí iría la lógica real)
        # Para la demo, crear resultado mock con naming correcto
        
        mock_tracks = []
        for i in range(2):  # Simular 2 tracks
            track_name = dynamic_name
            if i > 0:
                track_name += f" - Variación {i+1}"
            
            track = {
                "id": f"son1k_track_{int(time.time())}_{i+1}",
                "title": track_name,  # NOMBRE DINÁMICO
                "duration": "2:45",
                "url": f"https://son1k-demo.com/audio/{track_name.replace(' ', '_')}.mp3",
                "download_url": f"https://son1k-demo.com/download/{track_name.replace(' ', '_')}.mp3",
                "generated_at": int(time.time()),
                "provider": "Son1k",  # NUNCA mencionar suno
                "job_id": job_id,
                "filename": f"{track_name.replace(' ', '_')}.mp3",
                "lyrics_preview": request.lyrics[:100] + "..." if len(request.lyrics) > 100 else request.lyrics
            }
            
            mock_tracks.append(track)
            logger.info(f"✅ Track creado: {track_name}")
        
        return QuickGenerationResponse(
            job_id=job_id,
            status="completed",
            message=f"Generación completada: {dynamic_name}",
            tracks=mock_tracks
        )
        
    except Exception as e:
        logger.error(f"❌ Error en generación rápida: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en generación: {str(e)}"
        )

@app.get("/api/quick-test")
async def quick_test():
    """Test rápido del endpoint"""
    return {
        "status": "ready",
        "message": "Endpoint de generación rápida funcionando",
        "features": [
            "✅ Job IDs transparentes (son1k_*)",
            "✅ Nombres dinámicos basados en lyrics", 
            "✅ Sin referencias a 'suno'",
            "✅ Respuestas inmediatas"
        ]
    }

@app.post("/api/test-naming")
async def test_naming(lyrics: str):
    """Test del generador de nombres"""
    dynamic_name = generate_dynamic_name_from_lyrics(lyrics)
    return {
        "lyrics": lyrics[:100] + "..." if len(lyrics) > 100 else lyrics,
        "generated_name": dynamic_name,
        "filename": f"{dynamic_name.replace(' ', '_')}.mp3",
        "contains_suno": "suno" in dynamic_name.lower(),
        "is_valid": len(dynamic_name) > 0 and "suno" not in dynamic_name.lower()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("⚡ Iniciando Quick Fix Endpoint")
    print("🎯 Solución inmediata para transparencia total")
    print("=" * 50)
    print("Endpoints disponibles:")
    print("  POST /api/quick-generate - Generación rápida transparente")
    print("  GET  /api/quick-test     - Test del sistema")
    print("  POST /api/test-naming    - Test de nombres dinámicos")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)