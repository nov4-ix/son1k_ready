"""
Worker Pool Management System
Dynamic scaling and management of Selenium workers for commercial deployment
"""
import os
import time
import logging
import asyncio
import subprocess
import signal
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import redis
import psutil

logger = logging.getLogger(__name__)

class WorkerStatus(Enum):
    STARTING = "starting"
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class WorkerType(Enum):
    SELENIUM = "selenium"
    AUDIO_PROCESSING = "audio_processing"
    AI_PROMPTS = "ai_prompts"

@dataclass
class WorkerInstance:
    worker_id: str
    worker_type: WorkerType
    status: WorkerStatus
    plan_assignment: str  # free, pro, vip, enterprise
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    jobs_completed: int = 0
    jobs_failed: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    current_job_id: Optional[str] = None

class WorkerPoolManager:
    """Manages dynamic scaling and lifecycle of worker pools"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"), 
            decode_responses=True
        )
        
        # Worker management
        self.workers: Dict[str, WorkerInstance] = {}
        self.worker_processes: Dict[str, subprocess.Popen] = {}
        
        # Scaling configuration
        self.scaling_config = {
            'enterprise': {
                'min_workers': 3,
                'max_workers': 10,
                'scale_up_threshold': 2,    # Scale up if >2 jobs in queue
                'scale_down_threshold': 0,  # Scale down if queue empty for 5min
                'cooldown_period': 60       # 1 minute between scaling actions
            },
            'vip': {
                'min_workers': 2,
                'max_workers': 5,
                'scale_up_threshold': 3,
                'scale_down_threshold': 0,
                'cooldown_period': 120
            },
            'pro': {
                'min_workers': 1,
                'max_workers': 3,
                'scale_up_threshold': 5,
                'scale_down_threshold': 0,
                'cooldown_period': 180
            },
            'free': {
                'min_workers': 1,
                'max_workers': 2,
                'scale_up_threshold': 10,
                'scale_down_threshold': 0,
                'cooldown_period': 300
            }
        }
        
        # Monitoring
        self.last_scaling_action: Dict[str, datetime] = {}
        self.monitoring_interval = 30  # seconds
        self.is_running = False
        
    async def start_pool_manager(self):
        """Start the worker pool management system"""
        logger.info("🏭 Starting Worker Pool Manager...")
        self.is_running = True
        
        # Initialize minimum workers for each plan
        await self.initialize_minimum_workers()
        
        # Start monitoring tasks
        asyncio.create_task(self.monitor_workers())
        asyncio.create_task(self.auto_scaling_loop())
        asyncio.create_task(self.health_check_loop())
        
        logger.info("✅ Worker Pool Manager started successfully")
    
    async def stop_pool_manager(self):
        """Stop the worker pool management system"""
        logger.info("🛑 Stopping Worker Pool Manager...")
        self.is_running = False
        
        # Gracefully stop all workers
        await self.stop_all_workers()
        
        logger.info("✅ Worker Pool Manager stopped")
    
    async def initialize_minimum_workers(self):
        """Initialize minimum number of workers for each plan"""
        for plan, config in self.scaling_config.items():
            min_workers = config['min_workers']
            current_workers = await self.get_worker_count(plan)
            
            if current_workers < min_workers:
                workers_to_start = min_workers - current_workers
                logger.info(f"🚀 Starting {workers_to_start} minimum workers for {plan} plan")
                
                for _ in range(workers_to_start):
                    await self.start_worker(plan, WorkerType.SELENIUM)
    
    async def start_worker(self, plan: str, worker_type: WorkerType) -> Optional[str]:
        """Start a new worker instance"""
        try:
            worker_id = f"{worker_type.value}_{plan}_{int(time.time())}"
            
            # Create worker instance
            worker = WorkerInstance(
                worker_id=worker_id,
                worker_type=worker_type,
                status=WorkerStatus.STARTING,
                plan_assignment=plan,
                started_at=datetime.now()
            )
            
            # Start worker process
            process = await self._start_worker_process(worker)
            
            if process:
                worker.pid = process.pid
                worker.status = WorkerStatus.ACTIVE
                
                # Store worker data
                self.workers[worker_id] = worker
                self.worker_processes[worker_id] = process
                
                # Store in Redis
                await self._store_worker_in_redis(worker)
                
                logger.info(f"✅ Started {worker_type.value} worker {worker_id} for {plan} plan (PID: {process.pid})")
                return worker_id
            else:
                logger.error(f"❌ Failed to start worker {worker_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error starting worker: {e}")
            return None
    
    async def _start_worker_process(self, worker: WorkerInstance) -> Optional[subprocess.Popen]:
        """Start the actual worker process"""
        try:
            if worker.worker_type == WorkerType.SELENIUM:
                # Start Selenium worker
                cmd = [
                    "python", 
                    "start_selenium_worker.py",
                    "--worker-id", worker.worker_id,
                    "--backend-url", "http://localhost:8000",
                    "--headless",
                    "--poll-interval", "10",
                    "--plan-filter", worker.plan_assignment
                ]
                
                # Set environment variables
                env = os.environ.copy()
                env["WORKER_ID"] = worker.worker_id
                env["WORKER_PLAN"] = worker.plan_assignment
                
                # Start process
                process = subprocess.Popen(
                    cmd,
                    cwd="/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2",
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
                
                # Wait a bit to ensure it started properly
                await asyncio.sleep(2)
                
                if process.poll() is None:  # Process is still running
                    return process
                else:
                    logger.error(f"Worker process failed to start (exit code: {process.returncode})")
                    return None
                    
            else:
                logger.error(f"Unsupported worker type: {worker.worker_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error starting worker process: {e}")
            return None
    
    async def stop_worker(self, worker_id: str, graceful: bool = True) -> bool:
        """Stop a specific worker"""
        try:
            worker = self.workers.get(worker_id)
            if not worker:
                logger.warning(f"Worker {worker_id} not found")
                return False
            
            worker.status = WorkerStatus.STOPPING
            
            # Get process
            process = self.worker_processes.get(worker_id)
            if process:
                if graceful:
                    # Send SIGTERM for graceful shutdown
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()
                    
                    # Wait for graceful shutdown
                    for _ in range(10):  # Wait up to 10 seconds
                        if process.poll() is not None:
                            break
                        await asyncio.sleep(1)
                
                # Force kill if still running
                if process.poll() is None:
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
                
                # Clean up
                del self.worker_processes[worker_id]
            
            # Update worker status
            worker.status = WorkerStatus.STOPPED
            
            # Remove from Redis
            await self._remove_worker_from_redis(worker_id)
            
            # Remove from local storage
            del self.workers[worker_id]
            
            logger.info(f"🛑 Stopped worker {worker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping worker {worker_id}: {e}")
            return False
    
    async def stop_all_workers(self):
        """Stop all workers gracefully"""
        worker_ids = list(self.workers.keys())
        
        for worker_id in worker_ids:
            await self.stop_worker(worker_id, graceful=True)
    
    async def get_worker_count(self, plan: str = None) -> int:
        """Get number of active workers for a plan"""
        if plan:
            return len([w for w in self.workers.values() 
                       if w.plan_assignment == plan and w.status in [WorkerStatus.ACTIVE, WorkerStatus.BUSY, WorkerStatus.IDLE]])
        else:
            return len([w for w in self.workers.values() 
                       if w.status in [WorkerStatus.ACTIVE, WorkerStatus.BUSY, WorkerStatus.IDLE]])
    
    async def auto_scaling_loop(self):
        """Main auto-scaling logic loop"""
        while self.is_running:
            try:
                await self._check_scaling_for_all_plans()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in auto-scaling loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _check_scaling_for_all_plans(self):
        """Check if scaling is needed for each plan"""
        for plan in ['enterprise', 'vip', 'pro', 'free']:
            await self._check_scaling_for_plan(plan)
    
    async def _check_scaling_for_plan(self, plan: str):
        """Check and execute scaling for a specific plan"""
        try:
            config = self.scaling_config[plan]
            
            # Check cooldown period
            last_action = self.last_scaling_action.get(plan)
            if last_action and (datetime.now() - last_action).seconds < config['cooldown_period']:
                return
            
            # Get current metrics
            queue_size = await self._get_queue_size(plan)
            worker_count = await self.get_worker_count(plan)
            idle_workers = await self._get_idle_worker_count(plan)
            
            # Scale up logic
            if (queue_size > config['scale_up_threshold'] and 
                worker_count < config['max_workers'] and 
                idle_workers == 0):
                
                await self._scale_up(plan)
            
            # Scale down logic
            elif (queue_size <= config['scale_down_threshold'] and 
                  worker_count > config['min_workers'] and 
                  idle_workers > 0):
                
                await self._scale_down(plan)
                
        except Exception as e:
            logger.error(f"Error checking scaling for {plan}: {e}")
    
    async def _scale_up(self, plan: str):
        """Scale up workers for a plan"""
        try:
            worker_id = await self.start_worker(plan, WorkerType.SELENIUM)
            if worker_id:
                self.last_scaling_action[plan] = datetime.now()
                logger.info(f"📈 Scaled UP: Added worker for {plan} plan")
                
                # Notify via WebSocket
                await self._notify_scaling_action(plan, "scale_up", await self.get_worker_count(plan))
        except Exception as e:
            logger.error(f"Error scaling up {plan}: {e}")
    
    async def _scale_down(self, plan: str):
        """Scale down workers for a plan"""
        try:
            # Find an idle worker to remove
            idle_worker = await self._find_idle_worker(plan)
            if idle_worker:
                await self.stop_worker(idle_worker.worker_id)
                self.last_scaling_action[plan] = datetime.now()
                logger.info(f"📉 Scaled DOWN: Removed worker for {plan} plan")
                
                # Notify via WebSocket
                await self._notify_scaling_action(plan, "scale_down", await self.get_worker_count(plan))
        except Exception as e:
            logger.error(f"Error scaling down {plan}: {e}")
    
    async def monitor_workers(self):
        """Monitor worker health and performance"""
        while self.is_running:
            try:
                for worker_id, worker in list(self.workers.items()):
                    await self._update_worker_metrics(worker)
                    
                    # Check if worker is responsive
                    if self._is_worker_unresponsive(worker):
                        logger.warning(f"⚠️ Worker {worker_id} is unresponsive, restarting...")
                        await self._restart_worker(worker_id)
                
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in worker monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def health_check_loop(self):
        """Periodic health checks for the entire pool"""
        while self.is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(60)  # Health check every minute
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        total_workers = len(self.workers)
        active_workers = len([w for w in self.workers.values() if w.status == WorkerStatus.ACTIVE])
        
        # Check system resources
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "total_workers": total_workers,
            "active_workers": active_workers,
            "system_cpu": cpu_percent,
            "system_memory": memory_percent,
            "workers_by_plan": {
                plan: await self.get_worker_count(plan) 
                for plan in ['enterprise', 'vip', 'pro', 'free']
            }
        }
        
        # Store health data in Redis
        self.redis_client.setex("worker_pool:health", 300, json.dumps(health_data))
        
        logger.info(f"💓 Health check: {active_workers}/{total_workers} workers active, CPU: {cpu_percent}%, Memory: {memory_percent}%")
    
    async def _get_queue_size(self, plan: str) -> int:
        """Get current queue size for a plan"""
        try:
            queue_key = f"{plan}_queue"
            return self.redis_client.llen(queue_key) or 0
        except:
            return 0
    
    async def _get_idle_worker_count(self, plan: str) -> int:
        """Get number of idle workers for a plan"""
        return len([w for w in self.workers.values() 
                   if w.plan_assignment == plan and w.status == WorkerStatus.IDLE])
    
    async def _find_idle_worker(self, plan: str) -> Optional[WorkerInstance]:
        """Find an idle worker for a plan"""
        for worker in self.workers.values():
            if (worker.plan_assignment == plan and 
                worker.status == WorkerStatus.IDLE):
                return worker
        return None
    
    async def _update_worker_metrics(self, worker: WorkerInstance):
        """Update worker performance metrics"""
        try:
            if worker.pid:
                try:
                    process = psutil.Process(worker.pid)
                    worker.cpu_usage = process.cpu_percent()
                    worker.memory_usage = process.memory_percent()
                except psutil.NoSuchProcess:
                    worker.status = WorkerStatus.STOPPED
                    logger.warning(f"Worker {worker.worker_id} process not found")
        except Exception as e:
            logger.error(f"Error updating metrics for worker {worker.worker_id}: {e}")
    
    def _is_worker_unresponsive(self, worker: WorkerInstance) -> bool:
        """Check if worker is unresponsive"""
        if not worker.last_heartbeat:
            return False
        
        # Consider unresponsive if no heartbeat for 5 minutes
        return (datetime.now() - worker.last_heartbeat) > timedelta(minutes=5)
    
    async def _restart_worker(self, worker_id: str):
        """Restart an unresponsive worker"""
        try:
            worker = self.workers.get(worker_id)
            if not worker:
                return
                
            plan = worker.plan_assignment
            worker_type = worker.worker_type
            
            # Stop the old worker
            await self.stop_worker(worker_id, graceful=False)
            
            # Start a new worker
            await self.start_worker(plan, worker_type)
            
        except Exception as e:
            logger.error(f"Error restarting worker {worker_id}: {e}")
    
    async def _store_worker_in_redis(self, worker: WorkerInstance):
        """Store worker data in Redis"""
        try:
            key = f"worker:{worker.worker_id}"
            data = asdict(worker)
            data['started_at'] = worker.started_at.isoformat() if worker.started_at else None
            data['last_heartbeat'] = worker.last_heartbeat.isoformat() if worker.last_heartbeat else None
            data['status'] = worker.status.value
            data['worker_type'] = worker.worker_type.value
            
            self.redis_client.setex(key, 3600, json.dumps(data))  # 1 hour TTL
            
            # Add to plan-specific worker set
            plan_key = f"workers:{worker.plan_assignment}:active"
            self.redis_client.sadd(plan_key, worker.worker_id)
            self.redis_client.expire(plan_key, 3600)
            
        except Exception as e:
            logger.error(f"Error storing worker in Redis: {e}")
    
    async def _remove_worker_from_redis(self, worker_id: str):
        """Remove worker data from Redis"""
        try:
            worker = self.workers.get(worker_id)
            if worker:
                # Remove from plan-specific set
                plan_key = f"workers:{worker.plan_assignment}:active"
                self.redis_client.srem(plan_key, worker_id)
            
            # Remove worker data
            key = f"worker:{worker_id}"
            self.redis_client.delete(key)
            
        except Exception as e:
            logger.error(f"Error removing worker from Redis: {e}")
    
    async def _notify_scaling_action(self, plan: str, action: str, worker_count: int):
        """Notify about scaling actions via WebSocket"""
        try:
            from .ws import send_worker_scaling_update
            await send_worker_scaling_update(plan, action, worker_count)
        except Exception as e:
            logger.error(f"Error notifying scaling action: {e}")
    
    def get_pool_stats(self) -> Dict:
        """Get comprehensive pool statistics"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_workers": len(self.workers),
            "workers_by_status": {},
            "workers_by_plan": {},
            "workers_by_type": {},
            "system_metrics": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }
        
        # Count by status
        for status in WorkerStatus:
            stats["workers_by_status"][status.value] = len([
                w for w in self.workers.values() if w.status == status
            ])
        
        # Count by plan
        for plan in ['enterprise', 'vip', 'pro', 'free']:
            stats["workers_by_plan"][plan] = len([
                w for w in self.workers.values() if w.plan_assignment == plan
            ])
        
        # Count by type
        for worker_type in WorkerType:
            stats["workers_by_type"][worker_type.value] = len([
                w for w in self.workers.values() if w.worker_type == worker_type
            ])
        
        return stats

# Global worker pool manager instance
worker_pool = WorkerPoolManager()

# Helper functions for easy import
async def start_worker_pool():
    """Start the worker pool management system"""
    await worker_pool.start_pool_manager()

async def stop_worker_pool():
    """Stop the worker pool management system"""
    await worker_pool.stop_pool_manager()

def get_pool_statistics() -> Dict:
    """Get worker pool statistics"""
    return worker_pool.get_pool_stats()

async def scale_workers(plan: str, target_count: int) -> bool:
    """Manually scale workers for a plan"""
    current_count = await worker_pool.get_worker_count(plan)
    
    if target_count > current_count:
        # Scale up
        for _ in range(target_count - current_count):
            await worker_pool.start_worker(plan, WorkerType.SELENIUM)
        return True
    elif target_count < current_count:
        # Scale down
        for _ in range(current_count - target_count):
            idle_worker = await worker_pool._find_idle_worker(plan)
            if idle_worker:
                await worker_pool.stop_worker(idle_worker.worker_id)
        return True
    
    return False