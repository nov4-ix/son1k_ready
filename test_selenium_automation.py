#!/usr/bin/env python3
"""
Test script for Selenium Worker automation
Tests the complete workflow: job creation → Selenium processing → results
"""
import sys
import time
import requests
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from selenium_worker.worker_service import SeleniumWorkerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumAutomationTester:
    """Test harness for Selenium automation"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url.rstrip('/')
        self.worker_service = None
        
    def test_backend_connectivity(self) -> bool:
        """Test backend API connectivity"""
        try:
            logger.info("🔍 Testing backend connectivity...")
            
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend is accessible")
                return True
            else:
                logger.error(f"❌ Backend returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Backend connectivity failed: {e}")
            return False
    
    def test_job_creation(self) -> str:
        """Test creating a job via API"""
        try:
            logger.info("📋 Testing job creation...")
            
            # Create test job data
            job_data = {
                "prompt": "A peaceful acoustic guitar song about nature and tranquility",
                "lyrics": "",
                "mode": "original",
                "style": "acoustic",
                "user_email": "test@son1k.com"
            }
            
            # Try to create job via test endpoint
            response = requests.post(
                f"{self.backend_url}/api/selenium/test",
                json=job_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get("job_id")
                logger.info(f"✅ Test job created: {job_id}")
                return job_id
            else:
                logger.error(f"❌ Job creation failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Job creation error: {e}")
            return None
    
    def test_selenium_worker_init(self) -> bool:
        """Test Selenium worker initialization"""
        try:
            logger.info("🤖 Testing Selenium worker initialization...")
            
            # Create worker in test mode (headless)
            self.worker_service = SeleniumWorkerService(
                backend_url=self.backend_url,
                worker_id="test_selenium_worker",
                headless=True,  # Use headless for testing
                poll_interval=5  # Faster polling for tests
            )
            
            # Test browser initialization
            self.worker_service._initialize_browser()
            
            if self.worker_service.browser_manager and self.worker_service.suno_automation:
                logger.info("✅ Selenium worker initialized successfully")
                return True
            else:
                logger.error("❌ Selenium worker initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Selenium worker init error: {e}")
            return False
    
    def test_suno_login(self) -> bool:
        """Test Suno.com login functionality"""
        try:
            logger.info("🔐 Testing Suno.com login...")
            
            if not self.worker_service or not self.worker_service.browser_manager:
                logger.error("❌ Worker not initialized")
                return False
            
            # Test login
            login_success = self.worker_service.browser_manager.ensure_logged_in()
            
            if login_success:
                logger.info("✅ Suno.com login successful")
                return True
            else:
                logger.error("❌ Suno.com login failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Suno login error: {e}")
            return False
    
    def test_job_processing(self, job_id: str) -> bool:
        """Test processing a specific job"""
        try:
            logger.info(f"⚙️ Testing job processing: {job_id}")
            
            if not self.worker_service:
                logger.error("❌ Worker not initialized")
                return False
            
            # Get job from backend
            response = requests.get(
                f"{self.backend_url}/api/selenium/jobs/next",
                params={"worker_id": "test_selenium_worker"},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error("❌ No jobs available for processing")
                return False
            
            job_data = response.json()
            if "job_id" not in job_data:
                logger.error("❌ Invalid job data received")
                return False
            
            logger.info(f"📄 Processing job: {job_data['job_id']}")
            
            # Process the job
            result = self.worker_service._process_job(job_data)
            
            if result.get("success"):
                logger.info("✅ Job processing successful")
                
                # Report results to backend
                self.worker_service._report_job_result(job_data["job_id"], result)
                
                return True
            else:
                logger.error(f"❌ Job processing failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Job processing error: {e}")
            return False
    
    def test_complete_workflow(self) -> bool:
        """Test the complete automation workflow"""
        logger.info("🚀 Starting complete workflow test...")
        
        try:
            # Step 1: Test backend connectivity
            if not self.test_backend_connectivity():
                return False
            
            # Step 2: Create test job
            job_id = self.test_job_creation()
            if not job_id:
                return False
            
            # Step 3: Initialize Selenium worker
            if not self.test_selenium_worker_init():
                return False
            
            # Step 4: Test Suno login
            if not self.test_suno_login():
                return False
            
            # Step 5: Test job processing
            logger.info("⏳ Waiting for job to be available in queue...")
            time.sleep(5)  # Give job time to be queued
            
            if not self.test_job_processing(job_id):
                return False
            
            logger.info("🎉 Complete workflow test successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete workflow test failed: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def test_browser_only(self) -> bool:
        """Test only browser functionality (faster test)"""
        logger.info("🌐 Testing browser functionality only...")
        
        try:
            # Test worker init
            if not self.test_selenium_worker_init():
                return False
            
            # Test login
            if not self.test_suno_login():
                return False
            
            # Test navigation to create page
            if self.worker_service.browser_manager.navigate_to_create():
                logger.info("✅ Successfully navigated to create page")
            else:
                logger.warning("⚠️ Could not navigate to create page")
            
            # Take screenshot for verification
            screenshot_path = self.worker_service.browser_manager.take_screenshot("test_suno_page.png")
            if screenshot_path:
                logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
            logger.info("✅ Browser functionality test completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser test failed: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.worker_service:
                self.worker_service.cleanup()
                self.worker_service = None
            logger.info("🧹 Cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Selenium automation workflow")
    parser.add_argument("--backend-url", default="http://localhost:8000",
                       help="Backend URL")
    parser.add_argument("--test-type", choices=["full", "browser", "backend"],
                       default="browser", help="Type of test to run")
    parser.add_argument("--visible", action="store_true",
                       help="Run browser in visible mode (for debugging)")
    
    args = parser.parse_args()
    
    # Create tester
    tester = SeleniumAutomationTester(backend_url=args.backend_url)
    
    success = False
    
    try:
        if args.test_type == "backend":
            # Test only backend connectivity
            success = tester.test_backend_connectivity()
            
        elif args.test_type == "browser":
            # Test browser functionality only
            success = tester.test_browser_only()
            
        elif args.test_type == "full":
            # Test complete workflow
            success = tester.test_complete_workflow()
        
        if success:
            logger.info("🎉 All tests passed!")
            sys.exit(0)
        else:
            logger.error("❌ Tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Tests interrupted by user")
        tester.cleanup()
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        tester.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()