import os
import logging
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from celery import Celery
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserPlan(Enum):
    FREE = "free"
    PRO = "pro" 
    VIP = "vip"
    ENTERPRISE = "enterprise"

class QueuePriority(Enum):
    LOW = 0      # Free users
    NORMAL = 1   # Pro users
    HIGH = 2     # VIP users
    URGENT = 3   # Enterprise users

@dataclass
class QueueJob:
    job_id: str
    user_id: str
    user_plan: UserPlan
    priority: QueuePriority
    payload: dict
    created_at: datetime
    estimated_wait: int  # minutes
    worker_assigned: Optional[str] = None
    started_at: Optional[datetime] = None

# Redis configuration
broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
backend_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Redis client for queue management
redis_client = redis.Redis.from_url(broker_url, decode_responses=True)

# Create Celery app
celery_app = Celery("son1k", broker=broker_url, backend=backend_url)

# Celery configuration with priority queues
celery_app.conf.update(
    task_routes={
        "tasks.generate_free": {"queue": "free_queue"},
        "tasks.generate_pro": {"queue": "pro_queue"},
        "tasks.generate_vip": {"queue": "vip_queue"},
        "tasks.generate_enterprise": {"queue": "enterprise_queue"}
    },
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_log_level='INFO',
    task_default_priority=1,
    task_inherit_parent_priority=True,
    worker_disable_rate_limits=True
)

# Priority-based generation tasks
@celery_app.task(name="tasks.generate_free", bind=True)
def generate_task_free(self, payload: dict):
    """Free tier: normal queue processing (10-15 min wait)"""
    return _process_generation_task(self, payload, UserPlan.FREE)

@celery_app.task(name="tasks.generate_pro", bind=True)
def generate_task_pro(self, payload: dict):
    """Pro tier: fast queue processing (3-5 min wait)"""
    return _process_generation_task(self, payload, UserPlan.PRO)

@celery_app.task(name="tasks.generate_vip", bind=True)
def generate_task_vip(self, payload: dict):
    """VIP tier: immediate processing"""
    return _process_generation_task(self, payload, UserPlan.VIP)

@celery_app.task(name="tasks.generate_enterprise", bind=True)
def generate_task_enterprise(self, payload: dict):
    """Enterprise tier: highest priority immediate processing"""
    return _process_generation_task(self, payload, UserPlan.ENTERPRISE)

def _process_generation_task(task_self, payload: dict, user_plan: UserPlan):
    """
    Process music generation task with plan-based handling
    """
    try:
        logger.info(f"🎵 Starting {user_plan.value} generation: {task_self.request.id}")
        
        # Update job status to processing
        _update_job_status(task_self.request.id, "processing", user_plan)
        
        # Call Selenium worker service
        from .selenium_integration import submit_to_selenium_worker
        result = submit_to_selenium_worker(payload, task_self.request.id, user_plan)
        
        logger.info(f"✅ {user_plan.value} generation completed: {task_self.request.id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in {user_plan.value} generation {task_self.request.id}: {str(e)}")
        _update_job_status(task_self.request.id, "failed", user_plan, str(e))
        raise

# Intelligent Queue Management System
class IntelligentQueueManager:
    """Manages priority-based queue with auto-scaling"""
    
    def __init__(self):
        self.plan_wait_times = {
            UserPlan.FREE: (10, 15),      # 10-15 min
            UserPlan.PRO: (3, 5),         # 3-5 min  
            UserPlan.VIP: (0, 1),         # immediate
            UserPlan.ENTERPRISE: (0, 0)    # highest priority
        }
        self.max_workers_per_plan = {
            UserPlan.FREE: 2,
            UserPlan.PRO: 3,
            UserPlan.VIP: 5,
            UserPlan.ENTERPRISE: 10
        }
    
    def enqueue_generation(self, payload: dict, user_plan: UserPlan, user_id: str) -> str:
        """
        Intelligent queue management with priority-based routing
        """
        try:
            priority = self._get_priority_for_plan(user_plan)
            
            # Create queue job record
            job = QueueJob(
                job_id="",  # Will be set after task creation
                user_id=user_id,
                user_plan=user_plan,
                priority=priority,
                payload=payload,
                created_at=datetime.now(),
                estimated_wait=self._calculate_wait_time(user_plan)
            )
            
            # Route to appropriate queue based on plan
            task_func = self._get_task_function(user_plan)
            async_result = task_func.delay(payload)
            
            job.job_id = async_result.id
            
            # Store job metadata in Redis
            self._store_job_metadata(job)
            
            # Update queue statistics
            self._update_queue_stats(user_plan)
            
            # Trigger auto-scaling if needed
            self._check_auto_scaling(user_plan)
            
            logger.info(f"🚀 Enqueued {user_plan.value} job {job.job_id} (wait: {job.estimated_wait}m)")
            return job.job_id
            
        except Exception as e:
            logger.error(f"❌ Error enqueuing {user_plan.value} task: {str(e)}")
            raise
    
    def _get_priority_for_plan(self, plan: UserPlan) -> QueuePriority:
        mapping = {
            UserPlan.FREE: QueuePriority.LOW,
            UserPlan.PRO: QueuePriority.NORMAL,
            UserPlan.VIP: QueuePriority.HIGH,
            UserPlan.ENTERPRISE: QueuePriority.URGENT
        }
        return mapping[plan]
    
    def _get_task_function(self, plan: UserPlan):
        mapping = {
            UserPlan.FREE: generate_task_free,
            UserPlan.PRO: generate_task_pro,
            UserPlan.VIP: generate_task_vip,
            UserPlan.ENTERPRISE: generate_task_enterprise
        }
        return mapping[plan]
    
    def _calculate_wait_time(self, plan: UserPlan) -> int:
        """Calculate estimated wait time based on current queue"""
        base_min, base_max = self.plan_wait_times[plan]
        
        # Get current queue size for this plan
        queue_size = self._get_queue_size(plan)
        
        # Adjust wait time based on queue load
        multiplier = 1 + (queue_size * 0.1)  # 10% increase per job in queue
        estimated = int((base_min + base_max) / 2 * multiplier)
        
        return max(estimated, base_min)
    
    def _get_queue_size(self, plan: UserPlan) -> int:
        """Get current queue size for plan"""
        queue_name = f"{plan.value}_queue"
        try:
            return redis_client.llen(queue_name) or 0
        except:
            return 0
    
    def _store_job_metadata(self, job: QueueJob):
        """Store job metadata in Redis"""
        key = f"job:{job.job_id}"
        data = {
            "user_id": job.user_id,
            "user_plan": job.user_plan.value,
            "priority": job.priority.value,
            "created_at": job.created_at.isoformat(),
            "estimated_wait": job.estimated_wait,
            "status": "queued"
        }
        redis_client.hset(key, mapping=data)
        redis_client.expire(key, 86400)  # 24 hours
    
    def _update_queue_stats(self, plan: UserPlan):
        """Update queue statistics for monitoring"""
        key = f"queue_stats:{plan.value}"
        redis_client.hincrby(key, "total_jobs", 1)
        redis_client.hincrby(key, "queued_jobs", 1)
        redis_client.expire(key, 86400)
    
    def _check_auto_scaling(self, plan: UserPlan):
        """Check if auto-scaling is needed"""
        queue_size = self._get_queue_size(plan)
        active_workers = self._get_active_workers(plan)
        max_workers = self.max_workers_per_plan[plan]
        
        # Scale up if queue is growing and we have capacity
        if queue_size > 3 and active_workers < max_workers:
            self._scale_up_workers(plan)
        
        # Scale down if queue is empty and we have excess workers
        elif queue_size == 0 and active_workers > 1:
            self._scale_down_workers(plan)
    
    def _get_active_workers(self, plan: UserPlan) -> int:
        """Get number of active workers for plan"""
        key = f"workers:{plan.value}:active"
        return len(redis_client.smembers(key))
    
    def _scale_up_workers(self, plan: UserPlan):
        """Scale up workers for plan"""
        logger.info(f"🔺 Scaling UP workers for {plan.value} plan")
        # Signal to spawn new worker (implementation depends on deployment)
        redis_client.publish("worker_scaling", f"scale_up:{plan.value}")
    
    def _scale_down_workers(self, plan: UserPlan):
        """Scale down workers for plan"""
        logger.info(f"🔻 Scaling DOWN workers for {plan.value} plan")
        redis_client.publish("worker_scaling", f"scale_down:{plan.value}")
    
    def get_queue_status(self) -> Dict:
        """Get comprehensive queue status"""
        status = {}
        for plan in UserPlan:
            queue_size = self._get_queue_size(plan)
            active_workers = self._get_active_workers(plan)
            wait_time = self._calculate_wait_time(plan)
            
            status[plan.value] = {
                "queue_size": queue_size,
                "active_workers": active_workers,
                "estimated_wait_minutes": wait_time,
                "priority_level": self._get_priority_for_plan(plan).value
            }
        
        return status

# Global queue manager instance
queue_manager = IntelligentQueueManager()

def _update_job_status(job_id: str, status: str, plan: UserPlan, error: str = None):
    """Update job status in Redis"""
    key = f"job:{job_id}"
    update_data = {"status": status, "updated_at": datetime.now().isoformat()}
    if error:
        update_data["error"] = error
    redis_client.hset(key, mapping=update_data)

# Compatibility function for existing API
def enqueue_generation(payload: dict, user_plan: str = "free", user_id: str = "anonymous") -> str:
    """
    Legacy wrapper for backward compatibility
    """
    plan_enum = UserPlan(user_plan.lower())
    return queue_manager.enqueue_generation(payload, plan_enum, user_id)

