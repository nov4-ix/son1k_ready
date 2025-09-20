from backend.app.queue import celery_app
import logging
import os
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.generate", bind=True)
def generate(self, payload: dict):
    """Main generation task with Selenium automation and WebSocket progress tracking"""
    try:
        logger.info(f"🎵 Starting Selenium music generation task: {self.request.id}")
        logger.info(f"Payload received: {payload}")
        
        # Get user_id for WebSocket updates
        user_id = payload.get("user_id", "anonymous")
        job_id = self.request.id
        
        # Send initial status update
        import asyncio
        from backend.app.ws import send_job_status_update
        
        def send_update(status, progress=0, message="", **kwargs):
            """Helper to send WebSocket updates and update job registry"""
            try:
                # Update job registry
                from backend.app.routers.music import update_job_status
                update_job_status(job_id, status, progress=progress, message=message, **kwargs)
                
                # Send WebSocket update
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    send_job_status_update(job_id, status, user_id, progress=progress, message=message, **kwargs)
                )
                loop.close()
            except Exception as e:
                logger.warning(f"Failed to send WebSocket update: {e}")
        
        send_update("starting", progress=5, message="Initializing Selenium worker...")
        
        # Import Selenium worker
        from backend.app.selenium_worker import SunoSeleniumWorker
        
        # Initialize worker
        worker = SunoSeleniumWorker(headless=True)
        
        try:
            # Setup driver
            send_update("processing", progress=10, message="Setting up Chrome driver...")
            if not worker.setup_driver():
                logger.error("❌ Failed to setup Selenium driver")
                send_update("failed", progress=100, message="Failed to setup Chrome driver")
                return {"success": False, "error": "Driver setup failed"}
            
            # Load Suno with authentication
            send_update("processing", progress=25, message="Loading Suno.com with authentication...")
            if not worker.load_suno_with_auth():
                logger.error("❌ Failed to load Suno.com")
                send_update("failed", progress=100, message="Failed to load Suno.com")
                return {"success": False, "error": "Failed to load Suno.com"}
            
            # Navigate to create page
            send_update("processing", progress=40, message="Navigating to music creation page...")
            if not worker.navigate_to_create():
                logger.error("❌ Failed to navigate to create page")
                send_update("failed", progress=100, message="Failed to navigate to create page")
                return {"success": False, "error": "Failed to navigate to create page"}
            
            # Generate music
            send_update("processing", progress=50, message="Starting music generation...")
            result = worker.generate_music(payload)
            
            if result.get("success"):
                logger.info(f"✅ Selenium generation completed: {self.request.id}")
                
                # Update result with job metadata
                result.update({
                    "job_id": self.request.id,
                    "method": "selenium_automation",
                    "user_plan": payload.get("user_plan", "free"),
                    "worker_type": "selenium"
                })
                
                # Send completion update
                audio_files = result.get("audio_files", [])
                completion_message = f"Generation completed! {len(audio_files)} audio file(s) downloaded"
                
                send_update("completed", progress=100, message=completion_message, 
                          audio_files=audio_files, result_data=result)
                
            else:
                logger.error(f"❌ Selenium generation failed: {result.get('error', 'Unknown error')}")
                
                # Take screenshot for debugging
                try:
                    screenshot_path = worker.take_screenshot("generation_failed")
                    result["debug_screenshot"] = screenshot_path
                except:
                    pass
                
                send_update("failed", progress=100, message=f"Generation failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        finally:
            # Always cleanup
            send_update("processing", progress=95, message="Cleaning up resources...")
            worker.cleanup()
        
    except Exception as e:
        logger.error(f"❌ Error in Selenium generate task {self.request.id}: {str(e)}")
        
        # Send error update
        try:
            send_update("failed", progress=100, message=f"Task error: {str(e)}")
        except:
            pass
        
        return {"success": False, "error": str(e)}

@celery_app.task(name="tasks.generate_fallback", bind=True)
def generate_fallback(self, payload: dict):
    """Fallback generation task (forwards to queue system)"""
    try:
        logger.info(f"🔄 Starting fallback generation task: {self.request.id}")
        logger.info(f"Payload received: {payload}")
        
        # Forward to appropriate plan-based task
        user_plan = payload.get("user_plan", "free")
        
        if user_plan == "enterprise":
            from backend.app.queue import generate_task_enterprise
            result = generate_task_enterprise.delay(payload)
        elif user_plan == "vip":
            from backend.app.queue import generate_task_vip
            result = generate_task_vip.delay(payload)
        elif user_plan == "pro":
            from backend.app.queue import generate_task_pro
            result = generate_task_pro.delay(payload)
        else:
            from backend.app.queue import generate_task_free
            result = generate_task_free.delay(payload)
        
        logger.info(f"✅ Task forwarded to {user_plan} queue: {result.id}")
        return {"success": True, "forwarded_to": user_plan, "job_id": result.id}
        
    except Exception as e:
        logger.error(f"❌ Error in fallback generate task {self.request.id}: {str(e)}")
        return {"success": False, "error": str(e)}

@celery_app.task(name="tasks.test_selenium", bind=True)
def test_selenium(self, payload: dict = None):
    """Test Selenium automation with minimal payload"""
    try:
        logger.info(f"🧪 Testing Selenium automation: {self.request.id}")
        
        test_payload = payload or {
            "prompt": "upbeat electronic music for automation test",
            "instrumental": True,
            "user_plan": "free"
        }
        
        # Use main generate task
        result = generate(self, test_payload)
        
        logger.info(f"🧪 Selenium test result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Selenium test failed: {str(e)}")
        return {"success": False, "error": str(e)}