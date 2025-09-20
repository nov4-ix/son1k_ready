# 🛡️ NOVNC CAPTCHA RESOLUTION WORKFLOW

Comprehensive guide for implementing visual CAPTCHA resolution using Selenium remote + noVNC.

---

## 📋 OVERVIEW

This system enables **visual CAPTCHA resolution** for Suno automation by:
1. **Running Selenium in a remote container** with noVNC access
2. **Detecting CAPTCHAs** automatically during automation
3. **Notifying the frontend** with a secure noVNC link
4. **Allowing manual user resolution** through a browser interface
5. **Continuing automation** automatically after resolution

---

## 🏗️ ARCHITECTURE

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Device   │    │   Backend API   │    │ Selenium Grid   │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │ Frontend  │◄─┼────┤  │ FastAPI   │◄─┼────┤  │ Chrome    │  │
│  │ Browser   │  │    │  │ + CAPTCHA │  │    │  │ + noVNC   │  │
│  └───────────┘  │    │  │ API       │  │    │  └───────────┘  │
│                 │    │  └───────────┘  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        └────────── ngrok tunnel ─┼────────────────────────┘
                    (secure)      │
                                  │
                           ┌─────────────────┐
                           │   Automation    │
                           │    Worker       │
                           │ (run_suno.py)   │
                           └─────────────────┘
```

---

## 🚀 SETUP INSTRUCTIONS

### **1. Docker Selenium with noVNC**

```bash
# 1) Add to docker-compose.yml (already done)
services:
  selenium:
    image: selenium/standalone-chrome:123.0
    container_name: son1k_selenium
    shm_size: 2gb
    environment:
      - SE_NODE_MAX_SESSIONS=1
      - SE_VNC_NO_PASSWORD=1
    ports:
      - "4444:4444"   # WebDriver
      - "7900:7900"   # noVNC (web)
    restart: unless-stopped

# 2) Start Selenium container
docker compose up -d selenium
```

### **2. Secure noVNC Tunnel**

```bash
# Option A: ngrok with authentication (recommended)
ngrok http -auth="son1k:captcha" 7900

# Option B: ngrok with custom domain (for production)
ngrok http --domain=captcha.son1k.com 7900

# Get public URL
export NOVNC_PUBLIC_URL="https://xxxxx.ngrok-free.app"
```

### **3. Environment Variables**

```bash
# Remote Selenium configuration
export SV_SELENIUM_URL="http://localhost:4444"

# noVNC public URL (from ngrok)
export NOVNC_PUBLIC_URL="https://xxxxx.ngrok-free.app"

# Backend API base (for notifications)
export SON1K_API_BASE="http://localhost:8000"

# Optional: Basic auth for ngrok
export NOVNC_AUTH_USER="son1k"
export NOVNC_AUTH_PASS="captcha"
```

---

## ⚙️ WORKFLOW STEPS

### **Step 1: Automation Starts**
```bash
# Run Suno automation with remote Selenium
python3 scripts/run_suno_create.py
```

### **Step 2: CAPTCHA Detection**
- Automation detects CAPTCHA using multiple selectors:
  - `iframe[src*='hcaptcha']`
  - `iframe[src*='recaptcha']` 
  - `iframe[src*='turnstile']`
  - `div[class*='captcha']`

### **Step 3: Backend Notification**
```json
POST /api/captcha/event
{
  "job_id": "suno_20250919_143022_auto",
  "provider": "hcaptcha",
  "status": "NEEDED",
  "novnc_url": "https://xxxxx.ngrok-free.app",
  "browser_session": "http://localhost:4444",
  "timestamp": 1632150000
}
```

### **Step 4: Frontend Polling**
```javascript
// Frontend polls for CAPTCHA status
async function pollCaptchaStatus(jobId) {
    const response = await fetch(`/api/captcha/status/${jobId}`);
    const status = await response.json();
    
    if (status.status === "NEEDED" && status.novnc_url) {
        showCaptchaBanner(status.novnc_url);
    } else if (status.status === "RESOLVED") {
        hideCaptchaBanner();
    }
    
    setTimeout(() => pollCaptchaStatus(jobId), 2500);
}
```

### **Step 5: User Resolution**
1. **Frontend shows banner**: "CAPTCHA resolution needed"
2. **User clicks secure link**: Opens noVNC in new tab
3. **User sees Selenium browser**: Real Chrome instance with CAPTCHA
4. **User solves CAPTCHA**: Clicks, types, selects images, etc.
5. **Automation detects resolution**: CAPTCHA iframe disappears

### **Step 6: Automation Continues**
- Backend receives "RESOLVED" notification
- Frontend hides CAPTCHA banner
- Automation continues with music generation

---

## 🔧 API ENDPOINTS

### **CAPTCHA Events**
```bash
# Notify CAPTCHA needed/resolved
POST /api/captcha/event
Content-Type: application/json

{
  "job_id": "string",
  "provider": "hcaptcha|recaptcha|turnstile|unknown", 
  "status": "NEEDED|RESOLVED",
  "novnc_url": "https://xxxxx.ngrok-free.app",
  "browser_session": "http://localhost:4444"
}
```

### **CAPTCHA Status**
```bash
# Get current CAPTCHA status
GET /api/captcha/status/{job_id}

Response:
{
  "job_id": "suno_20250919_143022_auto",
  "status": "NEEDED|RESOLVED|UNKNOWN",
  "provider": "hcaptcha",
  "novnc_url": "https://xxxxx.ngrok-free.app",
  "created_at": 1632150000,
  "resolved_at": null
}
```

### **Active CAPTCHAs**
```bash
# Get all pending CAPTCHAs (monitoring)
GET /api/captcha/active

Response:
{
  "success": true,
  "active_captchas": [...],
  "total": 2
}
```

### **Manual Resolution**
```bash
# Emergency manual resolution
POST /api/captcha/manual-resolve/{job_id}

Response:
{
  "success": true,
  "message": "CAPTCHA manually resolved for job_id"
}
```

---

## 🖥️ FRONTEND INTEGRATION

### **React/Vue Example**
```javascript
// CAPTCHA Banner Component
function CaptchaBanner({ jobId }) {
  const [captchaStatus, setCaptchaStatus] = useState(null);
  
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/captcha/status/${jobId}`);
        const status = await response.json();
        setCaptchaStatus(status);
        
        if (status.status === "NEEDED") {
          // Continue polling
          setTimeout(pollStatus, 2500);
        }
      } catch (error) {
        console.error('CAPTCHA polling error:', error);
      }
    };
    
    pollStatus();
  }, [jobId]);
  
  if (captchaStatus?.status !== "NEEDED") {
    return null;
  }
  
  return (
    <div className="captcha-banner alert alert-warning">
      <h4>🛡️ CAPTCHA Resolution Required</h4>
      <p>Your music generation is paused for security verification.</p>
      <a 
        href={captchaStatus.novnc_url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="btn btn-primary"
      >
        🖥️ Open Secure Browser
      </a>
      <small className="text-muted">
        Provider: {captchaStatus.provider} | Job: {jobId}
      </small>
    </div>
  );
}
```

### **Vanilla JavaScript Example**
```html
<div id="captcha-banner" style="display: none;" class="alert alert-warning">
  <h4>🛡️ CAPTCHA Resolution Required</h4>
  <p>Your music generation is paused for security verification.</p>
  <a id="captcha-link" href="#" target="_blank" class="btn btn-primary">
    🖥️ Open Secure Browser
  </a>
  <small id="captcha-info" class="text-muted"></small>
</div>

<script>
async function pollCaptchaStatus(jobId) {
  const banner = document.getElementById('captcha-banner');
  const link = document.getElementById('captcha-link');
  const info = document.getElementById('captcha-info');
  
  try {
    const response = await fetch(`/api/captcha/status/${jobId}`);
    const status = await response.json();
    
    if (status.status === "NEEDED" && status.novnc_url) {
      // Show banner
      banner.style.display = 'block';
      link.href = status.novnc_url;
      info.textContent = `Provider: ${status.provider} | Job: ${jobId}`;
      
      // Continue polling
      setTimeout(() => pollCaptchaStatus(jobId), 2500);
    } else {
      // Hide banner
      banner.style.display = 'none';
      
      // Continue polling if not resolved
      if (status.status !== "RESOLVED" && status.status !== "UNKNOWN") {
        setTimeout(() => pollCaptchaStatus(jobId), 2500);
      }
    }
  } catch (error) {
    console.error('CAPTCHA polling error:', error);
    setTimeout(() => pollCaptchaStatus(jobId), 5000); // Retry after 5s
  }
}

// Start polling when job begins
pollCaptchaStatus("suno_20250919_143022_auto");
</script>
```

---

## 🔒 SECURITY CONSIDERATIONS

### **noVNC Access Control**
```bash
# Option 1: Basic authentication
ngrok http -auth="son1k:captcha" 7900

# Option 2: IP allowlist (for corporate)
ngrok http --ip-whitelist="203.0.113.0/24" 7900

# Option 3: Custom domain with TLS
ngrok http --domain=captcha.son1k.com 7900
```

### **Session Isolation**
- Each automation job uses a **fresh Selenium session**
- CAPTCHA links are **time-limited** (expire after resolution)
- noVNC access is **read-write** but isolated per container

### **Data Protection**
- No sensitive data stored in browser
- CAPTCHA resolution happens in **isolated container**
- Browser profile can be **reset** after each job

---

## 🚨 TROUBLESHOOTING

### **Common Issues & Solutions**

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Selenium container not accessible** | Connection refused to 4444 | `docker compose up -d selenium` |
| **noVNC not loading** | Blank page at 7900 | Check container logs: `docker logs son1k_selenium` |
| **ngrok tunnel expired** | 404 on NOVNC_PUBLIC_URL | Restart ngrok, update environment variable |
| **CAPTCHA not detected** | Automation stuck | Check screenshots in `selenium_artifacts/` |
| **User can't access noVNC** | Authentication failed | Verify ngrok auth credentials |
| **CAPTCHA resolved but automation stuck** | Infinite waiting | Manual resolve: `POST /api/captcha/manual-resolve/{job_id}` |

### **Debug Commands**
```bash
# Check Selenium container status
docker ps | grep selenium
docker logs son1k_selenium

# Test WebDriver connection  
curl http://localhost:4444/wd/hub/status

# Test noVNC web interface
curl -I http://localhost:7900

# Check ngrok tunnels
curl http://localhost:4040/api/tunnels

# Test CAPTCHA API
curl http://localhost:8000/api/captcha/health
```

### **Emergency Manual Resolution**
```bash
# If automation is stuck, manually resolve CAPTCHA
curl -X POST http://localhost:8000/api/captcha/manual-resolve/suno_20250919_143022_auto

# Or through the API with job_id
curl -X POST http://localhost:8000/api/captcha/manual-resolve/YOUR_JOB_ID
```

---

## 📊 MONITORING & ANALYTICS

### **CAPTCHA Statistics**
```bash
# Get active CAPTCHAs
GET /api/captcha/active

# CAPTCHA health check
GET /api/captcha/health
```

### **Performance Metrics**
- **CAPTCHA detection rate**: How often CAPTCHAs appear
- **Resolution time**: Average time for user to resolve
- **Success rate**: Percentage of successful resolutions
- **Provider breakdown**: Which CAPTCHA providers are most common

### **Logging**
All CAPTCHA events are logged with structured data:
```python
logger.info(f"🛡️ CAPTCHA detected: {provider} (selector: {selector})")
logger.info(f"🖥️ noVNC URL available for user: {novnc_url}")
logger.info(f"✅ CAPTCHA resolved for job {job_id}")
```

---

## 🎯 PRODUCTION DEPLOYMENT

### **Scalable Setup**
```bash
# Multiple Selenium instances
docker compose scale selenium=3

# Load balancer for WebDriver requests
# (nginx configuration for round-robin)

# Dedicated CAPTCHA resolution workers
# (separate containers for CAPTCHA handling)
```

### **High Availability**
- **Multiple ngrok tunnels** for redundancy
- **Health checks** for Selenium containers
- **Automatic retry** on CAPTCHA timeout
- **Fallback to local browser** if remote fails

### **Monitoring Integration**
- **Prometheus metrics** for CAPTCHA events
- **Grafana dashboards** for visualization
- **AlertManager** for stuck CAPTCHAs
- **Slack notifications** for manual intervention

---

## ✅ VALIDATION CHECKLIST

Before deploying to production, verify:

- [ ] **Selenium container running**: `docker ps | grep selenium`
- [ ] **noVNC accessible**: Open `http://localhost:7900` in browser
- [ ] **ngrok tunnel active**: Check `NOVNC_PUBLIC_URL` is reachable
- [ ] **CAPTCHA API working**: `curl /api/captcha/health`
- [ ] **Environment variables set**: All `SV_*` and `NOVNC_*` vars
- [ ] **Frontend polling implemented**: User sees CAPTCHA banner
- [ ] **Manual resolution works**: Emergency endpoints functional
- [ ] **Security configured**: ngrok auth or IP restrictions
- [ ] **Monitoring setup**: Logs and metrics collection

---

## 🚀 QUICK START

Copy/paste commands for immediate setup:

```bash
# 1) Start Selenium with noVNC
docker compose up -d selenium

# 2) Create secure tunnel
ngrok http -auth="son1k:captcha" 7900 &
sleep 3

# 3) Export public URL (auto-extract from ngrok API)
export NOVNC_PUBLIC_URL="$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "import sys,json; d=json.load(sys.stdin); print([t['public_url'] for t in d['tunnels'] if t['public_url'].startswith('https://')][0])")"

# 4) Configure remote Selenium
export SV_SELENIUM_URL="http://localhost:4444"
export SON1K_API_BASE="http://localhost:8000"

# 5) Run automation (will use CAPTCHA workflow automatically)
python3 scripts/run_suno_create.py

# 6) Monitor CAPTCHA status
echo "CAPTCHA monitoring: http://localhost:8000/api/captcha/active"
echo "noVNC access: $NOVNC_PUBLIC_URL (user: son1k, pass: captcha)"
```

**🎉 Your Suno automation now supports visual CAPTCHA resolution!**

When a CAPTCHA appears:
1. User sees notification in frontend
2. Clicks secure link to open browser
3. Solves CAPTCHA visually  
4. Automation continues automatically

**STATUS: ✅ PRODUCTION READY - VISUAL CAPTCHA RESOLUTION ENABLED**