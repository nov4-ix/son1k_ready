"""
Selenium Worker Integration Service
Handles communication between queue system and Selenium workers
"""
import logging
import requests
import json
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class UserPlan(Enum):
    FREE = "free"
    PRO = "pro" 
    VIP = "vip"
    ENTERPRISE = "enterprise"

def submit_to_selenium_worker(payload: dict, job_id: str, user_plan: UserPlan) -> Dict:
    """
    Submit job to available Selenium worker with priority handling
    """
    try:
        # Get backend URL for worker communication
        backend_url = "http://localhost:8000"
        
        # Enhanced payload with priority information
        enhanced_payload = {
            **payload,
            "job_id": job_id,
            "user_plan": user_plan.value,
            "priority": _get_priority_score(user_plan),
            "submitted_at": "2024-12-18T15:30:00Z"
        }
        
        # Submit job via internal API
        response = requests.post(
            f"{backend_url}/api/selenium/jobs/submit",
            json=enhanced_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Job {job_id} submitted to Selenium worker")
            return {
                "ok": True,
                "job_id": job_id,
                "worker_id": result.get("worker_id"),
                "status": "submitted",
                "user_plan": user_plan.value,
                "message": f"Job submitted to {user_plan.value} priority queue"
            }
        else:
            raise Exception(f"Worker submission failed: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error submitting to Selenium worker: {e}")
        return {
            "ok": False,
            "job_id": job_id,
            "status": "failed",
            "error": str(e),
            "message": f"Failed to submit {user_plan.value} job to worker"
        }

def _get_priority_score(user_plan: UserPlan) -> int:
    """Get numeric priority score for worker processing"""
    scores = {
        UserPlan.FREE: 1,
        UserPlan.PRO: 5,
        UserPlan.VIP: 8,
        UserPlan.ENTERPRISE: 10
    }
    return scores[user_plan]

def get_worker_capacity() -> Dict:
    """Get current worker capacity and availability"""
    try:
        backend_url = "http://localhost:8000"
        response = requests.get(f"{backend_url}/api/selenium/workers/capacity")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"available_workers": 0, "total_capacity": 0}
            
    except Exception as e:
        logger.error(f"Error getting worker capacity: {e}")
        return {"available_workers": 0, "total_capacity": 0}