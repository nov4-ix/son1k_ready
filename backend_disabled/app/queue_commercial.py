"""
Commercial Queue System for Son1kVers3
Handles job queueing, retry logic, timeout management, and worker coordination
"""

import os
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from celery import Celery
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .db import get_db_session
from .models import Job, JobStatus, User, Worker, UsageLog, PLAN_LIMITS, UserPlan

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration for commercial use
broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
backend_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app with commercial configuration
celery_app = Celery("son1k_commercial", broker=broker_url, backend=backend_url)

# Enhanced Celery configuration for production
celery_app.conf.update(
    # Task routing
    task_routes={
        "tasks.generate_music": {"queue": "music_generation"},
        "tasks.retry_job": {"queue": "retry"},
        "tasks.timeout_check": {"queue": "monitoring"},
        "tasks.worker_health_check": {"queue": "monitoring"}
    },
    
    # Reliability settings
    result_expires=7200,  # Results expire after 2 hours
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_log_level='INFO',
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
    worker_prefetch_multiplier=1,    # Only fetch one task at a time
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

class JobManager:
    """Commercial job management with rate limiting, retries, and monitoring"""
    
    def __init__(self):
        pass
    
    def create_job(self, user_id: Optional[str], job_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new job with rate limiting and validation
        Returns job_id if successful, None if rate limited
        """
        try:
            with get_db_session() as db:
                # Check user quota if user_id provided
                if user_id:
                    if not self._check_user_quota(user_id):
                        logger.warning(f"User {user_id} exceeded quota")
                        return None
                
                # Generate job ID
                job_id = str(uuid.uuid4())
                
                # Calculate timeout
                timeout_minutes = job_data.get('timeout_minutes', 5)
                timeout_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
                
                # Create job record
                job = Job(
                    id=job_id,
                    user_id=user_id,
                    prompt=job_data.get('prompt', ''),
                    lyrics=job_data.get('lyrics', ''),
                    mode=job_data.get('mode', 'original'),
                    status=JobStatus.QUEUED,
                    timeout_at=timeout_at,
                    source=job_data.get('source', 'api'),
                    job_metadata=job_data.get('metadata', {})
                )
                
                # Set priority based on user plan
                if user_id:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        plan_config = PLAN_LIMITS.get(user.plan, PLAN_LIMITS[UserPlan.FREE])
                        job.priority = plan_config['priority']
                
                db.add(job)
                db.commit()
                
                # Update user usage
                if user_id:
                    self._update_user_usage(user_id, job_id)
                
                # Enqueue for processing
                generate_music_task.delay(job_id)
                
                logger.info(f"Created job {job_id} for user {user_id}")
                return job_id
            
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return None
    
    def _check_user_quota(self, user_id: str) -> bool:
        """Check if user can create new job based on their plan limits"""
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            plan_config = PLAN_LIMITS.get(user.plan, PLAN_LIMITS[UserPlan.FREE])
            
            # Check daily limit
            if plan_config['daily_limit'] > 0 and user.daily_usage >= plan_config['daily_limit']:
                return False
            
            # Check monthly limit  
            if plan_config['monthly_limit'] > 0 and user.monthly_usage >= plan_config['monthly_limit']:
                return False
            
            # Check concurrent jobs
            concurrent_jobs = db.query(Job).filter(
                and_(
                    Job.user_id == user_id,
                    or_(
                        Job.status == JobStatus.QUEUED,
                        Job.status == JobStatus.ASSIGNED,
                        Job.status == JobStatus.PROCESSING
                    )
                )
            ).count()
            
            if concurrent_jobs >= plan_config['concurrent_jobs']:
                return False
            
            return True
    
    def _update_user_usage(self, user_id: str, job_id: str):
        """Update user usage statistics"""
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # Reset daily usage if needed
                if user.last_usage_reset.date() < datetime.utcnow().date():
                    user.daily_usage = 0
                    user.last_usage_reset = datetime.utcnow()
                
                user.daily_usage += 1
                user.monthly_usage += 1
                
                # Log usage
                usage_log = UsageLog(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    job_id=job_id,
                    action="generation",
                    cost_credits=1
                )
                db.add(usage_log)
                db.commit()
    
    def get_next_job_for_worker(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get next job for extension worker with priority ordering"""
        try:
            with get_db_session() as db:
                # Find highest priority queued job
                job = db.query(Job).filter(
                    Job.status == JobStatus.QUEUED
                ).order_by(
                    Job.priority.desc(),  # Higher priority first
                    Job.created_at.asc()   # FIFO within same priority
                ).first()
                
                if job:
                    # Assign job to worker
                    job.status = JobStatus.ASSIGNED
                    job.worker_id = worker_id
                    job.assigned_at = datetime.utcnow()
                    db.commit()
                    
                    logger.info(f"Assigned job {job.id} to worker {worker_id}")
                    
                    return {
                        "job_id": job.id,
                        "prompt": job.prompt,
                        "lyrics": job.lyrics,
                        "mode": job.mode,
                        "timeout_at": job.timeout_at.isoformat() if job.timeout_at else None
                    }
                
                return None
            
        except Exception as e:
            logger.error(f"Error getting next job: {e}")
            return None
    
    def update_job_status(self, job_id: str, status: str, **kwargs):
        """Update job status with additional data"""
        try:
            with get_db_session() as db:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.status = status
                    job.updated_at = datetime.utcnow()
                    
                    # Update specific fields based on status
                    if status == JobStatus.PROCESSING:
                        job.started_at = datetime.utcnow()
                    elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.TIMEOUT]:
                        job.completed_at = datetime.utcnow()
                    
                    # Update additional fields
                    for key, value in kwargs.items():
                        if hasattr(job, key):
                            setattr(job, key, value)
                    
                    db.commit()
                    logger.info(f"Updated job {job_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
    
    def retry_failed_job(self, job_id: str) -> bool:
        """Retry failed job with exponential backoff"""
        try:
            with get_db_session() as db:
                job = db.query(Job).filter(Job.id == job_id).first()
                if not job or job.retry_count >= job.max_retries:
                    return False
                
                # Calculate next retry time with exponential backoff
                backoff_minutes = 2 ** job.retry_count  # 2, 4, 8 minutes
                next_retry = datetime.utcnow() + timedelta(minutes=backoff_minutes)
                
                job.status = JobStatus.QUEUED
                job.retry_count += 1
                job.next_retry_at = next_retry
                job.worker_id = None
                job.assigned_at = None
                job.error_message = None
                
                db.commit()
                
                # Schedule retry task
                retry_job_task.apply_async(args=[job_id], eta=next_retry)
                
                logger.info(f"Scheduled retry {job.retry_count}/{job.max_retries} for job {job_id}")
                return True
            
        except Exception as e:
            logger.error(f"Error retrying job: {e}")
            return False

# Create global job manager instance
job_manager = JobManager()

@celery_app.task(name="tasks.generate_music", bind=True, max_retries=3)
def generate_music_task(self, job_id: str):
    """
    Main task for music generation - waits for extension worker to process
    """
    try:
        logger.info(f"Processing job {job_id}")
        
        # This task now primarily handles timeout monitoring
        # The actual processing is done by the extension worker
        
        # Check if job is still valid
        with get_db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            # Wait for extension worker to pick up the job
            # The worker will update the job status directly
            
            # Set timeout check
            if job.timeout_at:
                timeout_check_task.apply_async(
                    args=[job_id],
                    eta=job.timeout_at
                )
        
        return {"job_id": job_id, "status": "queued_for_worker"}
        
    except Exception as e:
        logger.error(f"Error in generate_music_task: {e}")
        job_manager.update_job_status(
            job_id, 
            JobStatus.FAILED, 
            error_message=str(e)
        )
        raise

@celery_app.task(name="tasks.retry_job")
def retry_job_task(job_id: str):
    """Task to retry failed jobs"""
    logger.info(f"Retrying job {job_id}")
    generate_music_task.delay(job_id)

@celery_app.task(name="tasks.timeout_check")
def timeout_check_task(job_id: str):
    """Check if job has timed out"""
    try:
        with get_db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job and job.status in [JobStatus.QUEUED, JobStatus.ASSIGNED, JobStatus.PROCESSING]:
                if job.timeout_at and datetime.utcnow() > job.timeout_at:
                    logger.warning(f"Job {job_id} timed out")
                    job_manager.update_job_status(
                        job_id,
                        JobStatus.TIMEOUT,
                        error_message="Job exceeded maximum processing time"
                    )
                    
                    # Schedule retry if retries available
                    if job.retry_count < job.max_retries:
                        job_manager.retry_failed_job(job_id)
                        
    except Exception as e:
        logger.error(f"Error in timeout check: {e}")

@celery_app.task(name="tasks.worker_health_check")
def worker_health_check_task():
    """Monitor worker health and reassign stale jobs"""
    try:
        with get_db_session() as db:
            # Mark workers as offline if no heartbeat in 2 minutes
            offline_threshold = datetime.utcnow() - timedelta(minutes=2)
            offline_workers = db.query(Worker).filter(
                Worker.last_heartbeat < offline_threshold,
                Worker.status != "offline"
            ).all()
            
            for worker in offline_workers:
                worker.status = "offline"
                logger.warning(f"Worker {worker.id} marked offline")
            
            # Reassign jobs from offline workers
            stale_jobs = db.query(Job).filter(
                and_(
                    Job.status.in_([JobStatus.ASSIGNED, JobStatus.PROCESSING]),
                    Job.worker_id.in_([w.id for w in offline_workers])
                )
            ).all()
            
            for job in stale_jobs:
                logger.warning(f"Reassigning stale job {job.id}")
                job.status = JobStatus.QUEUED
                job.worker_id = None
                job.assigned_at = None
            
            db.commit()
            
    except Exception as e:
        logger.error(f"Error in worker health check: {e}")

# Schedule periodic health checks
celery_app.conf.beat_schedule = {
    'worker-health-check': {
        'task': 'tasks.worker_health_check',
        'schedule': 60.0,  # Every minute
    },
}

# Helper functions for API usage
def enqueue_generation(payload: dict, user_id: Optional[str] = None) -> Optional[str]:
    """
    Commercial version of enqueue function with rate limiting
    """
    return job_manager.create_job(user_id, payload)

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get current status of a job"""
    try:
        with get_db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                return {
                    "id": job.id,
                    "status": job.status,
                    "created_at": job.created_at,
                    "updated_at": job.updated_at,
                    "progress": job.job_metadata.get("progress") if job.job_metadata else None,
                    "error_message": job.error_message,
                    "audio_url": job.audio_url,
                    "preview_url": job.preview_url,
                    "retry_count": job.retry_count,
                    "max_retries": job.max_retries
                }
        return None
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        return None