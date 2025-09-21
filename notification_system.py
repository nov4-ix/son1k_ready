"""
Notification System for Son1k Auto-Renewal
Supports Slack, Discord, Email, and custom webhooks
"""
import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
        self.discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL")
        self.custom_webhook = os.environ.get("CUSTOM_WEBHOOK_URL")
        
        # Email configuration
        self.smtp_server = os.environ.get("SMTP_SERVER")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_username = os.environ.get("SMTP_USERNAME")
        self.smtp_password = os.environ.get("SMTP_PASSWORD")
        self.notification_email = os.environ.get("NOTIFICATION_EMAIL")
        
        # Notification preferences
        self.enable_slack = bool(self.slack_webhook)
        self.enable_discord = bool(self.discord_webhook)
        self.enable_email = bool(self.smtp_server and self.notification_email)
        self.enable_webhook = bool(self.custom_webhook)
    
    async def send_notification(self, data: Dict[str, Any]):
        """Send notification via all configured channels"""
        results = {}
        
        # Format message
        message = self._format_message(data)
        
        # Send via Slack
        if self.enable_slack:
            try:
                results["slack"] = await self._send_slack(message, data)
            except Exception as e:
                logger.error(f"❌ Slack notification failed: {e}")
                results["slack"] = {"success": False, "error": str(e)}
        
        # Send via Discord
        if self.enable_discord:
            try:
                results["discord"] = await self._send_discord(message, data)
            except Exception as e:
                logger.error(f"❌ Discord notification failed: {e}")
                results["discord"] = {"success": False, "error": str(e)}
        
        # Send via Email
        if self.enable_email:
            try:
                results["email"] = await self._send_email(message, data)
            except Exception as e:
                logger.error(f"❌ Email notification failed: {e}")
                results["email"] = {"success": False, "error": str(e)}
        
        # Send to custom webhook
        if self.enable_webhook:
            try:
                results["webhook"] = await self._send_webhook(data)
            except Exception as e:
                logger.error(f"❌ Webhook notification failed: {e}")
                results["webhook"] = {"success": False, "error": str(e)}
        
        return results
    
    def _format_message(self, data: Dict[str, Any]) -> str:
        """Format notification message"""
        message_type = data.get("type", "notification")
        service = data.get("service", "system")
        severity = data.get("severity", "info")
        message = data.get("message", "No message provided")
        
        # Emoji mapping
        severity_emojis = {
            "critical": "🚨",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "success": "✅"
        }
        
        emoji = severity_emojis.get(severity, "📢")
        
        if message_type == "credential_renewal_needed":
            return f"""
{emoji} **Son1k Credential Alert**

🔧 **Service**: {service}
📅 **Time**: {data.get('timestamp', 'N/A')}
💬 **Issue**: {message}

🔄 **Action Required**: {data.get('action_required', 'Manual intervention needed')}

📊 **Dashboard**: https://web-production-b52c4.up.railway.app/api/system/health
"""
        
        elif message_type == "service_failure":
            return f"""
{emoji} **Son1k Service Alert**

⚠️ **Service Down**: {service}
📅 **Time**: {data.get('timestamp', 'N/A')}
💬 **Error**: {message}

🔧 **Next Steps**: Check logs and restart if needed
📊 **Health Check**: https://web-production-b52c4.up.railway.app/api/system/health
"""
        
        else:
            return f"""
{emoji} **Son1k Notification**

📋 **Type**: {message_type}
🔧 **Service**: {service}
📅 **Time**: {data.get('timestamp', 'N/A')}
💬 **Message**: {message}
"""
    
    async def _send_slack(self, message: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification to Slack"""
        payload = {
            "text": "Son1k System Notification",
            "attachments": [
                {
                    "color": self._get_color(data.get("severity", "info")),
                    "fields": [
                        {
                            "title": f"{data.get('service', 'System')} Alert",
                            "value": message,
                            "short": False
                        }
                    ],
                    "footer": "Son1k Auto-Renewal System",
                    "ts": int(data.get("timestamp", 0))
                }
            ]
        }
        
        response = requests.post(self.slack_webhook, json=payload, timeout=10)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text[:100]
        }
    
    async def _send_discord(self, message: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification to Discord"""
        severity = data.get("severity", "info")
        color_map = {
            "critical": 16711680,  # Red
            "error": 16711680,     # Red
            "warning": 16776960,   # Yellow
            "info": 3447003,       # Blue
            "success": 65280       # Green
        }
        
        payload = {
            "embeds": [
                {
                    "title": f"Son1k {data.get('service', 'System').title()} Alert",
                    "description": message,
                    "color": color_map.get(severity, 3447003),
                    "footer": {
                        "text": "Son1k Auto-Renewal System"
                    },
                    "timestamp": data.get("timestamp")
                }
            ]
        }
        
        response = requests.post(self.discord_webhook, json=payload, timeout=10)
        
        return {
            "success": response.status_code in [200, 204],
            "status_code": response.status_code,
            "response": response.text[:100]
        }
    
    async def _send_email(self, message: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification via email"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.notification_email
            msg['Subject'] = f"Son1k Alert: {data.get('service', 'System')} - {data.get('severity', 'info').title()}"
            
            # Create HTML message
            html_message = f"""
            <html>
            <body>
                <h2>Son1k System Notification</h2>
                <pre>{message}</pre>
                
                <h3>Details:</h3>
                <ul>
                    <li><strong>Service:</strong> {data.get('service', 'N/A')}</li>
                    <li><strong>Type:</strong> {data.get('type', 'N/A')}</li>
                    <li><strong>Severity:</strong> {data.get('severity', 'N/A')}</li>
                    <li><strong>Timestamp:</strong> {data.get('timestamp', 'N/A')}</li>
                </ul>
                
                <p><a href="https://web-production-b52c4.up.railway.app/api/system/health">Check System Health</a></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_message, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_username, self.notification_email, text)
            server.quit()
            
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send to custom webhook"""
        payload = {
            "source": "son1k_auto_renewal",
            "alert": data,
            "system_info": {
                "api_url": "https://web-production-b52c4.up.railway.app",
                "health_endpoint": "/api/system/health",
                "timestamp": data.get("timestamp")
            }
        }
        
        response = requests.post(
            self.custom_webhook, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text[:100]
        }
    
    def _get_color(self, severity: str) -> str:
        """Get color for Slack attachments"""
        color_map = {
            "critical": "danger",
            "error": "danger",
            "warning": "warning",
            "info": "good",
            "success": "good"
        }
        return color_map.get(severity, "good")
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get current notification configuration status"""
        return {
            "channels_configured": {
                "slack": self.enable_slack,
                "discord": self.enable_discord,
                "email": self.enable_email,
                "custom_webhook": self.enable_webhook
            },
            "total_channels": sum([
                self.enable_slack,
                self.enable_discord, 
                self.enable_email,
                self.enable_webhook
            ]),
            "environment_variables": {
                "SLACK_WEBHOOK_URL": "✅" if self.slack_webhook else "❌",
                "DISCORD_WEBHOOK_URL": "✅" if self.discord_webhook else "❌",
                "SMTP_SERVER": "✅" if self.smtp_server else "❌",
                "NOTIFICATION_EMAIL": "✅" if self.notification_email else "❌",
                "CUSTOM_WEBHOOK_URL": "✅" if self.custom_webhook else "❌"
            }
        }

# Global instance
notification_manager = NotificationManager()

# Quick setup instructions
NOTIFICATION_SETUP_GUIDE = """
# Son1k Notification System Setup

## Environment Variables (add to Railway):

### Slack Integration:
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

### Discord Integration:
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL

### Email Integration:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=alerts@your-domain.com

### Custom Webhook:
CUSTOM_WEBHOOK_URL=https://your-monitoring-system.com/webhook

## Testing:
POST /api/system/notify
{
  "message": "Test notification",
  "severity": "info",
  "service": "test"
}
"""