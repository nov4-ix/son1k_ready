"""
Selenium Worker Service
Main service that processes job queue and coordinates automation
"""
import os
import time
import logging
import threading
import signal
import sys
from typing import Dict, Optional
from datetime import datetime
import requests

from .browser_manager import BrowserManager
from .suno_automation import SunoAutomation
from .audio_processor import AudioProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumWorkerService:
    """Main worker service that processes Suno automation jobs"""
    
    def __init__(self, 
                 backend_url: str = "http://localhost:8000",
                 worker_id: str = None,
                 headless: bool = True,
                 poll_interval: int = 30):
        
        self.backend_url = backend_url.rstrip('/')
        self.worker_id = worker_id or f"selenium_worker_{int(time.time())}"
        self.headless = headless
        self.poll_interval = poll_interval
        
        # Initialize components
        self.browser_manager: Optional[BrowserManager] = None
        self.suno_automation: Optional[SunoAutomation] = None
        self.audio_processor = AudioProcessor()
        
        # Worker state
        self.running = False
        self.current_job_id: Optional[str] = None
        self.jobs_completed = 0
        self.jobs_failed = 0
        self.last_heartbeat = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def start(self):
        """Start the worker service"""
        logger.info(f"🚀 Starting Selenium Worker Service: {self.worker_id}")
        logger.info(f"🔗 Backend URL: {self.backend_url}")
        logger.info(f"⏰ Poll interval: {self.poll_interval}s")
        logger.info(f"👁️ Headless mode: {self.headless}")
        
        self.running = True
        
        try:
            # Initialize browser
            self._initialize_browser()
            
            # Send initial heartbeat
            self._send_heartbeat("starting")
            
            # Start main processing loop
            self._main_loop()
            
        except Exception as e:
            logger.error(f"❌ Worker service failed: {e}")
            self._send_heartbeat("failed")
            
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop the worker service gracefully"""
        logger.info("🛑 Stopping Selenium Worker Service...")
        self.running = False
    
    def _initialize_browser(self):
        """Initialize browser manager and automation"""
        try:
            logger.info("🌐 Initializing browser...")
            
            self.browser_manager = BrowserManager(headless=self.headless)
            self.browser_manager.setup_driver()
            
            # Test login to Suno
            if self.browser_manager.ensure_logged_in():
                logger.info("✅ Successfully logged into Suno.com")
                self.suno_automation = SunoAutomation(self.browser_manager)
            else:
                raise Exception("Failed to login to Suno.com")
                
        except Exception as e:
            logger.error(f"❌ Browser initialization failed: {e}")
            raise
    
    def _main_loop(self):
        """Main processing loop"""
        logger.info("🔄 Starting main processing loop...")
        
        while self.running:
            try:
                # Send heartbeat
                self._send_heartbeat("idle")
                
                # Check for pending jobs
                job = self._get_next_job()
                
                if job:
                    self.current_job_id = job.get("job_id")
                    logger.info(f"📋 Processing job: {self.current_job_id}")
                    
                    # Process the job
                    result = self._process_job(job)
                    
                    # Report results
                    self._report_job_result(job["job_id"], result)
                    
                    # Update counters
                    if result.get("success"):
                        self.jobs_completed += 1
                    else:
                        self.jobs_failed += 1
                    
                    self.current_job_id = None
                else:
                    # No jobs available, wait
                    logger.debug(f"😴 No jobs available, waiting {self.poll_interval}s...")
                    time.sleep(self.poll_interval)
                
                # Periodic browser health check
                if not self._check_browser_health():
                    logger.warning("🏥 Browser unhealthy, reinitializing...")
                    self._reinitialize_browser()
                
                # Periodic cleanup
                if self.jobs_completed % 10 == 0 and self.jobs_completed > 0:
                    self.audio_processor.cleanup_old_files(max_age_hours=6)
                
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                self._send_heartbeat("error")
                time.sleep(10)  # Wait before retrying
    
    def _get_next_job(self) -> Optional[Dict]:
        """Get next job from backend queue"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/jobs/pending",
                params={"worker_id": self.worker_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "job_id" in data:
                    return data
                    
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error getting next job: {e}")
            return None
    
    def _process_job(self, job: Dict) -> Dict:
        """Process a single job"""
        job_id = job.get("job_id")
        job_type = job.get("type", "generation")
        job_data = job.get("data", {})
        
        logger.info(f"⚙️ Processing {job_type} job: {job_id}")
        
        try:
            # Update job status to processing
            self._update_job_status(job_id, "processing")
            self._send_heartbeat("processing")
            
            if job_type == "generation":
                # Regular song generation
                result = self._process_generation_job(job_data)
            elif job_type == "cover":
                # Cover/remix generation
                result = self._process_cover_job(job_data)
            else:
                result = {"success": False, "error": f"Unknown job type: {job_type}"}
            
            logger.info(f"✅ Job {job_id} processed: {result.get('success', False)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Job {job_id} failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_generation_job(self, job_data: Dict) -> Dict:
        """Process song generation job"""
        try:
            # Ensure browser is ready
            if not self.browser_manager.is_healthy():
                self._reinitialize_browser()
            
            # Perform generation
            generation_result = self.suno_automation.generate_song(job_data)
            
            if not generation_result.get("success"):
                return generation_result
            
            # Process audio files
            processed_result = self.audio_processor.process_generation_results(generation_result)
            
            return processed_result
            
        except Exception as e:
            logger.error(f"❌ Generation job failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_cover_job(self, job_data: Dict) -> Dict:
        """Process cover/remix job"""
        try:
            # Ensure browser is ready
            if not self.browser_manager.is_healthy():
                self._reinitialize_browser()
            
            # Perform cover generation
            cover_result = self.suno_automation.create_cover(job_data)
            
            if not cover_result.get("success"):
                return cover_result
            
            # Process audio files
            processed_result = self.audio_processor.process_generation_results(cover_result)
            
            return processed_result
            
        except Exception as e:
            logger.error(f"❌ Cover job failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _report_job_result(self, job_id: str, result: Dict):
        """Report job completion to backend"""
        try:
            # Determine status
            status = "completed" if result.get("success") else "failed"
            
            # Prepare payload
            payload = {
                "status": status,
                "result_data": result
            }
            
            # Add audio URLs if available
            if result.get("success") and result.get("primary_file"):
                payload["audio_url"] = result["primary_file"]["file_path"]
                payload["preview_url"] = result["primary_file"]["file_path"]  # Same for now
            
            # Send to backend
            response = requests.post(
                f"{self.backend_url}/api/jobs/{job_id}/complete",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Job {job_id} reported as {status}")
            else:
                logger.error(f"❌ Failed to report job {job_id}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error reporting job {job_id}: {e}")
    
    def _update_job_status(self, job_id: str, status: str):
        """Update job status in backend"""
        try:
            payload = {"status": status}
            
            response = requests.post(
                f"{self.backend_url}/api/jobs/{job_id}/update",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"📝 Job {job_id} status updated to {status}")
            else:
                logger.warning(f"⚠️ Failed to update job {job_id} status")
                
        except Exception as e:
            logger.warning(f"⚠️ Error updating job status: {e}")
    
    def _send_heartbeat(self, status: str = "running"):
        """Send heartbeat to backend"""
        try:
            payload = {
                "worker_id": self.worker_id,
                "status": status,
                "current_job_id": self.current_job_id,
                "jobs_completed": self.jobs_completed,
                "jobs_failed": self.jobs_failed,
                "version": "1.0.0"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/worker/heartbeat",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_heartbeat = datetime.now()
                logger.debug(f"💓 Heartbeat sent: {status}")
            else:
                logger.warning(f"⚠️ Heartbeat failed: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Heartbeat error: {e}")
    
    def _check_browser_health(self) -> bool:
        """Check if browser is healthy"""
        try:
            if not self.browser_manager:
                return False
            
            return self.browser_manager.is_healthy()
            
        except Exception:
            return False
    
    def _reinitialize_browser(self):
        """Reinitialize browser after failure"""
        try:
            logger.info("🔄 Reinitializing browser...")
            
            # Close existing browser
            if self.browser_manager:
                self.browser_manager.close()
            
            # Wait a bit
            time.sleep(5)
            
            # Reinitialize
            self._initialize_browser()
            
            logger.info("✅ Browser reinitialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Browser reinitialization failed: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up resources...")
        
        try:
            # Send final heartbeat
            self._send_heartbeat("stopping")
            
            # Close browser
            if self.browser_manager:
                self.browser_manager.close()
            
            # Cleanup old files
            self.audio_processor.cleanup_old_files(max_age_hours=1)
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
    
    def get_worker_stats(self) -> Dict:
        """Get worker statistics"""
        return {
            "worker_id": self.worker_id,
            "running": self.running,
            "current_job_id": self.current_job_id,
            "jobs_completed": self.jobs_completed,
            "jobs_failed": self.jobs_failed,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "browser_healthy": self._check_browser_health(),
            "audio_storage": self.audio_processor.get_storage_stats()
        }


def main():
    """Main entry point for running worker as standalone service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Son1k Selenium Worker Service")
    parser.add_argument("--backend-url", default="http://localhost:8000", 
                       help="Backend URL")
    parser.add_argument("--worker-id", default=None,
                       help="Worker ID (auto-generated if not provided)")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Run browser in headless mode")
    parser.add_argument("--visible", action="store_false", dest="headless",
                       help="Run browser in visible mode (for debugging)")
    parser.add_argument("--poll-interval", type=int, default=30,
                       help="Job polling interval in seconds")
    
    args = parser.parse_args()
    
    # Create and start worker
    worker = SeleniumWorkerService(
        backend_url=args.backend_url,
        worker_id=args.worker_id,
        headless=args.headless,
        poll_interval=args.poll_interval
    )
    
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("👋 Worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Worker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()