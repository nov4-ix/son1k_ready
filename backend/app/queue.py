import os
import logging
from celery import Celery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration
broker_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
backend_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Create Celery app
celery_app = Celery("son1k", broker=broker_url, backend=backend_url)

# Celery configuration
celery_app.conf.update(
    task_routes={"tasks.*": {"queue": "default"}},
    result_expires=3600,  # Results expire after 1 hour
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_log_level='INFO'
)

@celery_app.task(name="tasks.generate", bind=True)
def generate_task(self, payload: dict):
    """
    Task to generate music using Suno API
    TODO: integrar con tu bridge Suno (extensión MV3)
    """
    try:
        logger.info(f"Starting music generation with payload: {payload}")
        
        # Simulate processing time
        import time
        time.sleep(2)
        
        # TODO: Replace with actual Suno API integration
        result = {
            "ok": True, 
            "payload": payload,
            "job_id": self.request.id,
            "status": "completed",
            "message": "Music generation completed successfully"
        }
        
        logger.info(f"Music generation completed for job {self.request.id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in music generation: {str(e)}")
        raise

# --- helper para API ---
def enqueue_generation(payload: dict) -> str:
    """
    Encola una tarea de generación y devuelve el job_id (task id).
    """
    try:
        async_result = generate_task.delay(payload)
        logger.info(f"Enqueued generation task with ID: {async_result.id}")
        return async_result.id
    except Exception as e:
        logger.error(f"Error enqueuing task: {str(e)}")
        raise

