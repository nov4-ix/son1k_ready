from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Global connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        self.job_subscribers: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str):
        """Connect user to WebSocket"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        logger.info(f"🔗 User {user_id} connected via WebSocket ({connection_id})")
        
        # Send initial queue status
        await self.send_queue_status_to_user(user_id)
    
    def disconnect(self, user_id: str, connection_id: str):
        """Disconnect user from WebSocket"""
        websocket = self.active_connections.get(connection_id)
        if websocket:
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from job subscriptions
            for job_id, subscribers in list(self.job_subscribers.items()):
                subscribers.discard(websocket)
                if not subscribers:
                    del self.job_subscribers[job_id]
            
            del self.active_connections[connection_id]
            logger.info(f"❌ User {user_id} disconnected from WebSocket ({connection_id})")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user's connections"""
        if user_id in self.user_connections:
            disconnected = set()
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.user_connections[user_id].discard(ws)
    
    async def subscribe_to_job(self, websocket: WebSocket, job_id: str):
        """Subscribe WebSocket to job updates"""
        if job_id not in self.job_subscribers:
            self.job_subscribers[job_id] = set()
        self.job_subscribers[job_id].add(websocket)
    
    async def send_job_update(self, job_id: str, update_data: dict):
        """Send update to all subscribers of a job"""
        if job_id in self.job_subscribers:
            message = {
                "type": "job_update",
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                **update_data
            }
            
            disconnected = set()
            for websocket in self.job_subscribers[job_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.job_subscribers[job_id].discard(ws)
    
    async def send_queue_status_to_user(self, user_id: str):
        """Send current queue status to user"""
        try:
            from .queue import queue_manager
            queue_status = queue_manager.get_queue_status()
            
            message = {
                "type": "queue_status",
                "timestamp": datetime.now().isoformat(),
                "queue_status": queue_status
            }
            
            await self.send_personal_message(message, user_id)
        except Exception as e:
            logger.error(f"Error sending queue status: {e}")
    
    async def broadcast_queue_update(self):
        """Broadcast queue updates to all connected users"""
        try:
            from .queue import queue_manager
            queue_status = queue_manager.get_queue_status()
            
            message = {
                "type": "queue_update",
                "timestamp": datetime.now().isoformat(),
                "queue_status": queue_status
            }
            
            # Send to all connected users
            for user_id in list(self.user_connections.keys()):
                await self.send_personal_message(message, user_id)
                
        except Exception as e:
            logger.error(f"Error broadcasting queue update: {e}")

# Global connection manager instance
manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def ws_updates(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time updates"""
    connection_id = f"{user_id}_{datetime.now().timestamp()}"
    
    try:
        await manager.connect(websocket, user_id, connection_id)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "subscribe_job":
                    job_id = message.get("job_id")
                    if job_id:
                        await manager.subscribe_to_job(websocket, job_id)
                        await websocket.send_json({
                            "type": "subscription_confirmed",
                            "job_id": job_id,
                            "message": f"Subscribed to job {job_id} updates"
                        })
                
                elif message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
                elif message.get("type") == "request_queue_status":
                    await manager.send_queue_status_to_user(user_id)
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Internal server error"
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        manager.disconnect(user_id, connection_id)

@router.websocket("/ws/queue/monitor")
async def queue_monitor_ws(websocket: WebSocket):
    """WebSocket endpoint for monitoring queue status"""
    await websocket.accept()
    
    try:
        while True:
            # Send queue status every 10 seconds
            from .queue import queue_manager
            queue_status = queue_manager.get_queue_status()
            
            message = {
                "type": "queue_monitor",
                "timestamp": datetime.now().isoformat(),
                "queue_status": queue_status
            }
            
            await websocket.send_json(message)
            await asyncio.sleep(10)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Queue monitor WebSocket error: {e}")

# Background task for periodic queue updates
async def periodic_queue_updates():
    """Send periodic queue updates to all connected users"""
    while True:
        try:
            await manager.broadcast_queue_update()
            await asyncio.sleep(30)  # Update every 30 seconds
        except Exception as e:
            logger.error(f"Error in periodic queue updates: {e}")
            await asyncio.sleep(30)

# Functions to send updates from other parts of the application
async def send_job_status_update(job_id: str, status: str, user_id: str = None, **kwargs):
    """Send job status update via WebSocket"""
    update_data = {
        "status": status,
        "progress": kwargs.get("progress", 0),
        "message": kwargs.get("message", f"Job {status}"),
        "estimated_completion": kwargs.get("estimated_completion"),
        **kwargs
    }
    
    # Send to job subscribers
    await manager.send_job_update(job_id, update_data)
    
    # Send to specific user if provided
    if user_id:
        message = {
            "type": "job_status",
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            **update_data
        }
        await manager.send_personal_message(message, user_id)

async def send_queue_position_update(user_id: str, job_id: str, position: int, estimated_wait: int):
    """Send queue position update to user"""
    message = {
        "type": "queue_position",
        "job_id": job_id,
        "position": position,
        "estimated_wait_minutes": estimated_wait,
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.send_personal_message(message, user_id)

async def send_worker_scaling_update(plan: str, action: str, worker_count: int):
    """Send worker scaling update to monitoring clients"""
    message = {
        "type": "worker_scaling",
        "plan": plan,
        "action": action,  # "scale_up" or "scale_down"
        "worker_count": worker_count,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to all connected users (could be filtered to admin users)
    for user_id in list(manager.user_connections.keys()):
        await manager.send_personal_message(message, user_id)

# Export manager for use in other modules
__all__ = ["router", "manager", "send_job_status_update", "send_queue_position_update", "send_worker_scaling_update"]
