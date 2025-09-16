import uuid, json
from celery import Celery
from .settings import settings

celery_app = Celery("suno_bridge", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task(name="jobs.generate_with_suno")
def generate_with_suno(payload: dict):
    # En producción: invoca motor (API) o dispara bridge/extension
    print("QUEUED:", json.dumps(payload, ensure_ascii=False))

@celery_app.task(name="jobs.process_audio")
def process_audio(asset_url: str):
    # Stub: normalizar, loudness, stems...
    print(f"PROCESS AUDIO: {asset_url}")
    return {"normalized": True}

def enqueue_generation(payload: dict) -> str:
    job_id = str(uuid.uuid4())
    generate_with_suno.apply_async(args=[payload], task_id=job_id, queue="default")
    return job_id
