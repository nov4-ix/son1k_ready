"""
Automatic Credential Management System for Son1k
Handles auto-renewal of Suno credentials, Ollama connections, and system health
"""
import os
import time
import json
import requests
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CredentialStatus:
    valid: bool
    expires_at: Optional[datetime]
    last_checked: datetime
    error_count: int
    last_error: Optional[str]

class AutoCredentialManager:
    def __init__(self):
        self.credentials = {
            "suno_session": None,
            "suno_cookie": None,
            "ollama_url": None
        }
        
        self.status = {
            "suno": CredentialStatus(False, None, datetime.now(), 0, None),
            "ollama": CredentialStatus(False, None, datetime.now(), 0, None)
        }
        
        # Auto-renewal settings
        self.check_interval = 300  # 5 minutes
        self.renewal_threshold = 3600  # 1 hour before expiry
        self.max_retry_attempts = 3
        
        # Credential sources (priority order)
        self.credential_sources = {
            "suno": [
                self._get_suno_from_env,
                self._get_suno_from_browser,
                self._get_suno_from_backup_file,
                self._request_manual_update
            ],
            "ollama": [
                self._get_ollama_from_env,
                self._discover_local_ollama,
                self._try_ngrok_tunnels,
                self._fallback_to_cloud_ollama
            ]
        }
        
        # Start background monitoring
        self.monitoring_active = False
    
    async def start_monitoring(self):
        """Start automatic credential monitoring and renewal"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        logger.info("🔄 Starting automatic credential monitoring")
        
        while self.monitoring_active:
            try:
                await self._check_all_credentials()
                await self._renew_if_needed()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error in credential monitoring: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute on error
    
    def stop_monitoring(self):
        """Stop automatic monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Stopped automatic credential monitoring")
    
    async def _check_all_credentials(self):
        """Check validity of all credentials"""
        await asyncio.gather(
            self._check_suno_credentials(),
            self._check_ollama_connection(),
            return_exceptions=True
        )
    
    async def _check_suno_credentials(self):
        """Check if Suno credentials are still valid"""
        try:
            session_id = os.environ.get("SUNO_SESSION_ID")
            cookie = os.environ.get("SUNO_COOKIE")
            
            if not session_id or not cookie:
                self.status["suno"].valid = False
                self.status["suno"].last_error = "Missing credentials"
                return
            
            # Test Suno API with current credentials
            clean_cookie = cookie.replace('\n', '').replace('\r', '').strip()
            headers = {
                "Cookie": clean_cookie,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://suno.com"
            }
            
            # Test endpoint to validate credentials
            test_endpoints = [
                "https://studio-api.suno.ai/api/generate/",
                "https://suno.com/api/generate/"
            ]
            
            valid = False
            for endpoint in test_endpoints:
                try:
                    response = requests.get(
                        f"{endpoint.replace('/generate/', '/billing/')}",  # Check billing for auth
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 404]:  # 404 is ok, means authenticated
                        valid = True
                        break
                    elif response.status_code == 401:
                        valid = False
                        break
                except:
                    continue
            
            self.status["suno"].valid = valid
            self.status["suno"].last_checked = datetime.now()
            self.status["suno"].error_count = 0 if valid else self.status["suno"].error_count + 1
            
            if not valid:
                self.status["suno"].last_error = "Authentication failed"
                logger.warning("⚠️ Suno credentials appear to be invalid")
            else:
                logger.info("✅ Suno credentials validated")
                
        except Exception as e:
            self.status["suno"].valid = False
            self.status["suno"].last_error = str(e)
            self.status["suno"].error_count += 1
            logger.error(f"❌ Error checking Suno credentials: {e}")
    
    async def _check_ollama_connection(self):
        """Check if Ollama connection is working"""
        try:
            ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
            
            # Test Ollama connection
            response = requests.get(f"{ollama_url}/api/tags", timeout=10)
            
            valid = response.status_code == 200
            
            self.status["ollama"].valid = valid
            self.status["ollama"].last_checked = datetime.now()
            self.status["ollama"].error_count = 0 if valid else self.status["ollama"].error_count + 1
            
            if not valid:
                self.status["ollama"].last_error = f"Connection failed: {response.status_code}"
                logger.warning(f"⚠️ Ollama connection failed: {ollama_url}")
            else:
                logger.info(f"✅ Ollama connection validated: {ollama_url}")
                
        except Exception as e:
            self.status["ollama"].valid = False
            self.status["ollama"].last_error = str(e)
            self.status["ollama"].error_count += 1
            logger.error(f"❌ Error checking Ollama connection: {e}")
    
    async def _renew_if_needed(self):
        """Renew credentials if they're invalid or expiring"""
        
        # Renew Suno credentials if needed
        if not self.status["suno"].valid or self.status["suno"].error_count >= 3:
            logger.info("🔄 Attempting to renew Suno credentials")
            await self._attempt_credential_renewal("suno")
        
        # Renew Ollama connection if needed  
        if not self.status["ollama"].valid or self.status["ollama"].error_count >= 3:
            logger.info("🔄 Attempting to renew Ollama connection")
            await self._attempt_credential_renewal("ollama")
    
    async def _attempt_credential_renewal(self, service: str):
        """Attempt to renew credentials for a specific service"""
        sources = self.credential_sources.get(service, [])
        
        for attempt, source_func in enumerate(sources):
            try:
                logger.info(f"🔄 Trying renewal method {attempt + 1} for {service}")
                result = await source_func()
                
                if result and result.get("success"):
                    logger.info(f"✅ Successfully renewed {service} credentials")
                    
                    # Update environment variables
                    if service == "suno":
                        if "session_id" in result:
                            os.environ["SUNO_SESSION_ID"] = result["session_id"]
                        if "cookie" in result:
                            os.environ["SUNO_COOKIE"] = result["cookie"]
                    elif service == "ollama":
                        if "url" in result:
                            os.environ["OLLAMA_URL"] = result["url"]
                    
                    # Reset error count
                    self.status[service].error_count = 0
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Renewal method {attempt + 1} failed for {service}: {e}")
                continue
        
        logger.error(f"❌ All renewal methods failed for {service}")
        return False
    
    # Credential source methods
    async def _get_suno_from_env(self):
        """Get Suno credentials from environment variables"""
        session_id = os.environ.get("SUNO_SESSION_ID_BACKUP")
        cookie = os.environ.get("SUNO_COOKIE_BACKUP")
        
        if session_id and cookie:
            return {"success": True, "session_id": session_id, "cookie": cookie}
        return {"success": False}
    
    async def _get_suno_from_browser(self):
        """Try to extract fresh Suno credentials from browser (if possible)"""
        # This would require browser automation - placeholder for now
        logger.info("🌐 Browser credential extraction not implemented yet")
        return {"success": False}
    
    async def _get_suno_from_backup_file(self):
        """Load Suno credentials from backup file"""
        backup_file = "suno_credentials_backup.json"
        
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r') as f:
                    creds = json.load(f)
                    
                if creds.get("session_id") and creds.get("cookie"):
                    # Check if backup credentials are recent (less than 7 days old)
                    backup_time = datetime.fromisoformat(creds.get("created_at", "2020-01-01"))
                    if datetime.now() - backup_time < timedelta(days=7):
                        return {"success": True, **creds}
            except:
                pass
        
        return {"success": False}
    
    async def _request_manual_update(self):
        """Request manual credential update (notification)"""
        logger.warning("📧 Manual credential update required - sending notification")
        
        # Here you could integrate with:
        # - Email notifications
        # - Slack/Discord webhooks  
        # - Dashboard alerts
        # - SMS notifications
        
        notification_data = {
            "type": "credential_renewal_needed",
            "service": "suno",
            "timestamp": datetime.now().isoformat(),
            "message": "Suno credentials need manual renewal",
            "action_required": "Update SUNO_SESSION_ID and SUNO_COOKIE environment variables"
        }
        
        # Placeholder for notification system
        await self._send_notification(notification_data)
        
        return {"success": False, "notification_sent": True}
    
    async def _get_ollama_from_env(self):
        """Get Ollama URL from environment"""
        backup_url = os.environ.get("OLLAMA_URL_BACKUP")
        if backup_url:
            return {"success": True, "url": backup_url}
        return {"success": False}
    
    async def _discover_local_ollama(self):
        """Try to discover local Ollama instances"""
        local_urls = [
            "http://localhost:11434",
            "http://127.0.0.1:11434",
            "http://0.0.0.0:11434"
        ]
        
        for url in local_urls:
            try:
                response = requests.get(f"{url}/api/tags", timeout=5)
                if response.status_code == 200:
                    return {"success": True, "url": url}
            except:
                continue
        
        return {"success": False}
    
    async def _try_ngrok_tunnels(self):
        """Try to find active ngrok tunnels for Ollama"""
        try:
            # Check ngrok API for active tunnels
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json().get("tunnels", [])
                
                for tunnel in tunnels:
                    if tunnel.get("config", {}).get("addr") == "localhost:11434":
                        public_url = tunnel.get("public_url")
                        if public_url:
                            return {"success": True, "url": public_url}
        except:
            pass
        
        return {"success": False}
    
    async def _fallback_to_cloud_ollama(self):
        """Fallback to cloud Ollama service (if configured)"""
        cloud_urls = [
            os.environ.get("OLLAMA_CLOUD_URL"),
            "https://ollama.your-domain.com"  # Configure your cloud instance
        ]
        
        for url in cloud_urls:
            if not url:
                continue
            try:
                response = requests.get(f"{url}/api/tags", timeout=10)
                if response.status_code == 200:
                    return {"success": True, "url": url}
            except:
                continue
        
        return {"success": False}
    
    async def _send_notification(self, data: Dict[str, Any]):
        """Send notification about credential issues"""
        # Implement your notification system here
        # Examples:
        
        # 1. Webhook notification
        webhook_url = os.environ.get("WEBHOOK_URL")
        if webhook_url:
            try:
                requests.post(webhook_url, json=data, timeout=10)
            except:
                pass
        
        # 2. Log notification
        logger.warning(f"🚨 NOTIFICATION: {data}")
        
        # 3. File notification (for monitoring systems)
        try:
            with open("credential_alerts.json", "a") as f:
                f.write(json.dumps(data) + "\n")
        except:
            pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system credential status"""
        return {
            "monitoring_active": self.monitoring_active,
            "last_check": datetime.now().isoformat(),
            "services": {
                "suno": {
                    "valid": self.status["suno"].valid,
                    "last_checked": self.status["suno"].last_checked.isoformat(),
                    "error_count": self.status["suno"].error_count,
                    "last_error": self.status["suno"].last_error
                },
                "ollama": {
                    "valid": self.status["ollama"].valid,
                    "last_checked": self.status["ollama"].last_checked.isoformat(),
                    "error_count": self.status["ollama"].error_count,
                    "last_error": self.status["ollama"].last_error
                }
            },
            "environment": {
                "suno_configured": bool(os.environ.get("SUNO_SESSION_ID")),
                "ollama_configured": bool(os.environ.get("OLLAMA_URL")),
                "backup_credentials": bool(os.environ.get("SUNO_SESSION_ID_BACKUP"))
            }
        }
    
    async def force_renewal(self, service: str = None):
        """Force credential renewal for specific service or all"""
        if service:
            await self._attempt_credential_renewal(service)
        else:
            await self._attempt_credential_renewal("suno")
            await self._attempt_credential_renewal("ollama")
    
    def save_credentials_backup(self):
        """Save current credentials as backup"""
        backup_data = {
            "session_id": os.environ.get("SUNO_SESSION_ID"),
            "cookie": os.environ.get("SUNO_COOKIE"),
            "ollama_url": os.environ.get("OLLAMA_URL"),
            "created_at": datetime.now().isoformat()
        }
        
        try:
            with open("suno_credentials_backup.json", "w") as f:
                json.dump(backup_data, f, indent=2)
            logger.info("💾 Credentials backup saved")
        except Exception as e:
            logger.error(f"❌ Failed to save credentials backup: {e}")

# Global instance
credential_manager = AutoCredentialManager()