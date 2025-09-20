#!/bin/bash

# 🚀 SCRIPT COMPLETO PARA LEVANTAR SISTEMA CAPTCHA + NOVNC
# Levanta todo: Selenium, ngrok, Backend API, y prepara automatización

set -e  # Exit on any error

PROJECT_DIR="/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
LOG_FILE="$PROJECT_DIR/captcha_system.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# Cleanup function
cleanup() {
    log "🛑 Shutting down services..."
    
    # Kill background processes
    if [ ! -z "$FASTAPI_PID" ]; then
        kill $FASTAPI_PID 2>/dev/null || true
        log "   ✅ FastAPI stopped"
    fi
    
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
        log "   ✅ ngrok stopped"
    fi
    
    # Optional: Stop docker containers
    read -p "🐳 Stop Docker containers? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose down
        log "   ✅ Docker containers stopped"
    fi
    
    log "👋 System shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

main() {
    clear
    log "🚀 STARTING CAPTCHA + NOVNC SYSTEM"
    log "=================================="
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # 1. SETUP ENVIRONMENT
    log "📦 Setting up environment..."
    
    if [ ! -d ".venv" ]; then
        error "Virtual environment not found. Run: python3 -m venv .venv"
        exit 1
    fi
    
    source .venv/bin/activate
    export PYTHONPATH="$PWD"
    log "   ✅ Virtual environment activated"
    
    # 2. CHECK DEPENDENCIES
    log "🔍 Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Please install Docker Desktop."
        exit 1
    fi
    log "   ✅ Docker available"
    
    # Check ngrok
    if ! command -v ngrok &> /dev/null; then
        warn "ngrok not found. Installing via brew..."
        if command -v brew &> /dev/null; then
            brew install ngrok
        else
            error "Please install ngrok from https://ngrok.com/download"
            exit 1
        fi
    fi
    log "   ✅ ngrok available"
    
    # 3. START DOCKER SERVICES
    log "🐳 Starting Docker services..."
    
    # Stop any existing containers
    docker compose down 2>/dev/null || true
    
    # Start Selenium with noVNC
    docker compose up -d selenium
    
    # Wait for container to be ready
    log "   ⏳ Waiting for Selenium container..."
    for i in {1..30}; do
        if curl -s http://localhost:4444/wd/hub/status &>/dev/null; then
            log "   ✅ Selenium WebDriver ready"
            break
        fi
        if [ $i -eq 30 ]; then
            error "Selenium container failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # Check noVNC
    for i in {1..15}; do
        if curl -s http://localhost:7900 &>/dev/null; then
            log "   ✅ noVNC web interface ready"
            break
        fi
        if [ $i -eq 15 ]; then
            error "noVNC interface failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # 4. CONFIGURE TUNNEL (ngrok or cloudflare)
    log "🌐 Configuring tunnel access..."
    
    # Check if user wants to use existing Cloudflare tunnel or create ngrok
    if [ ! -z "$CLOUDFLARE_TUNNEL_URL" ]; then
        # Use provided Cloudflare tunnel
        NOVNC_PUBLIC_URL="$CLOUDFLARE_TUNNEL_URL"
        log "   ✅ Using Cloudflare tunnel: $NOVNC_PUBLIC_URL"
        log "   ℹ️  Make sure port 7900 is configured in your Cloudflare tunnel"
    else
        # Ask user preference
        read -p "🌐 Use Cloudflare tunnel? Enter URL (or press Enter for ngrok): " cloudflare_url
        
        if [ ! -z "$cloudflare_url" ]; then
            NOVNC_PUBLIC_URL="$cloudflare_url"
            log "   ✅ Using Cloudflare tunnel: $NOVNC_PUBLIC_URL"
            log "   ℹ️  Make sure port 7900 is configured in your Cloudflare tunnel"
        else
            # Create ngrok tunnel
            log "   🚀 Creating ngrok tunnel..."
            
            # Kill any existing ngrok processes
            killall ngrok 2>/dev/null || true
            sleep 2
            
            # Start ngrok with authentication
            ngrok http -auth="son1k:captcha" 7900 --log=stdout > ngrok.log 2>&1 &
            NGROK_PID=$!
            log "   ⏳ Waiting for ngrok tunnel..."
            
            # Wait for ngrok to establish tunnel
            for i in {1..20}; do
                if curl -s http://localhost:4040/api/tunnels &>/dev/null; then
                    break
                fi
                if [ $i -eq 20 ]; then
                    error "ngrok tunnel failed to establish"
                    exit 1
                fi
                sleep 1
            done
            
            # Get public URL
            NOVNC_PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = [t['public_url'] for t in data.get('tunnels', []) if t['public_url'].startswith('https://')]
    print(tunnels[0] if tunnels else '')
except:
    print('')
")
            
            if [ -z "$NOVNC_PUBLIC_URL" ]; then
                error "Failed to get ngrok public URL"
                exit 1
            fi
            
            log "   ✅ ngrok tunnel established: $NOVNC_PUBLIC_URL"
        fi
    fi
    
    # 5. CONFIGURE ENVIRONMENT VARIABLES
    log "⚙️  Configuring environment variables..."
    
    export SV_SELENIUM_URL="http://localhost:4444"
    export NOVNC_PUBLIC_URL="$NOVNC_PUBLIC_URL"
    
    # Configure API base - use Cloudflare if available, otherwise localhost
    if [ ! -z "$CLOUDFLARE_API_URL" ]; then
        export SON1K_API_BASE="$CLOUDFLARE_API_URL"
        log "   🌐 Using Cloudflare API: $SON1K_API_BASE"
    else
        export SON1K_API_BASE="http://localhost:8000"
        log "   🏠 Using local API: $SON1K_API_BASE"
    fi
    
    export SV_HEADLESS=0
    export SV_NO_QUIT=1
    export SV_CHROME_PROFILE_DIR="$PWD/.selenium_profile_suno"
    export SON1K_FRONTEND_PUSH=1
    
    # Default test content
    export SV_LYRICS="Testing the CAPTCHA resolution system
With remote browser access via noVNC
Visual resolution works seamlessly
Automation continues after solving"
    
    export SV_PROMPT="upbeat electronic test song, 120 BPM, synthesizers and drums"
    
    log "   ✅ Environment configured"
    
    # 6. START FASTAPI BACKEND
    log "🔧 Starting FastAPI backend..."
    
    # Check if port 8000 is available
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        warn "Port 8000 already in use. Trying to stop existing process..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start FastAPI in background
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --log-level info > fastapi.log 2>&1 &
    FASTAPI_PID=$!
    
    log "   ⏳ Waiting for FastAPI to start..."
    for i in {1..20}; do
        if curl -s http://localhost:8000/api/health &>/dev/null; then
            log "   ✅ FastAPI backend ready"
            break
        fi
        if [ $i -eq 20 ]; then
            error "FastAPI failed to start"
            exit 1
        fi
        sleep 1
    done
    
    # 7. VALIDATE SYSTEM
    log "🧪 Validating system integration..."
    
    # Test CAPTCHA API
    if curl -s http://localhost:8000/api/captcha/health | grep -q "healthy"; then
        log "   ✅ CAPTCHA API functional"
    else
        error "CAPTCHA API not responding"
        exit 1
    fi
    
    # Test Selenium integration
    if python3 -c "
from backend.selenium_worker.browser_manager import BrowserManager
import os
os.environ['SV_SELENIUM_URL'] = 'http://localhost:4444'
try:
    bm = BrowserManager(headless=False)
    driver = bm.get_driver()
    driver.get('https://www.google.com')
    print('SUCCESS' if 'Google' in driver.title else 'FAILED')
    bm.close()
except Exception as e:
    print(f'FAILED: {e}')
" | grep -q "SUCCESS"; then
        log "   ✅ Remote Selenium integration working"
    else
        warn "Selenium integration test failed, but system may still work"
    fi
    
    # 8. SYSTEM READY
    clear
    log "🎉 CAPTCHA + NOVNC SYSTEM READY!"
    log "================================"
    echo
    log "📋 SYSTEM STATUS:"
    log "   🐳 Selenium + noVNC: http://localhost:7900"
    log "   🌐 Public noVNC URL: $NOVNC_PUBLIC_URL"
    log "   🔧 FastAPI Backend: http://localhost:8000"
    log "   🛡️ CAPTCHA API: http://localhost:8000/api/captcha/health"
    echo
    log "🔑 noVNC ACCESS:"
    log "   Username: son1k"
    log "   Password: captcha"
    echo
    log "🚀 TO RUN AUTOMATION:"
    log "   python3 scripts/run_suno_create.py"
    echo
    log "📊 MONITORING COMMANDS:"
    log "   curl http://localhost:8000/api/captcha/active"
    log "   curl http://localhost:8000/api/captcha/health"
    log "   docker logs son1k_selenium"
    echo
    log "📁 LOG FILES:"
    log "   System: $LOG_FILE"
    log "   FastAPI: $PWD/fastapi.log"
    log "   ngrok: $PWD/ngrok.log"
    echo
    
    # 9. INTERACTIVE MENU
    while true; do
        echo -e "${BLUE}Choose an option:${NC}"
        echo "  1) Run Suno automation test"
        echo "  2) Test CAPTCHA system"
        echo "  3) Open noVNC in browser"
        echo "  4) Show system status"
        echo "  5) View logs"
        echo "  6) Configure Cloudflare tunnel"
        echo "  7) Load Cloudflare config"
        echo "  8) Stop system"
        echo
        read -p "Enter choice [1-8]: " choice
        
        case $choice in
            1)
                log "🎵 Running Suno automation..."
                python3 scripts/run_suno_create.py
                ;;
            2)
                log "🧪 Testing CAPTCHA system..."
                python3 test_novnc_captcha.py
                ;;
            3)
                log "🖥️ Opening noVNC in browser..."
                open "$NOVNC_PUBLIC_URL" 2>/dev/null || xdg-open "$NOVNC_PUBLIC_URL" 2>/dev/null || echo "Open manually: $NOVNC_PUBLIC_URL"
                ;;
            4)
                log "📊 System Status:"
                echo
                
                # Check Selenium status
                selenium_status=$(curl -s http://localhost:4444/wd/hub/status 2>/dev/null)
                if echo "$selenium_status" | grep -q '"ready":true' 2>/dev/null; then
                    echo -e "   🐳 Selenium WebDriver: ${GREEN}✅ Ready${NC}"
                else
                    echo -e "   🐳 Selenium WebDriver: ${RED}❌ Not Ready${NC}"
                fi
                
                # Check noVNC status
                novnc_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7900 2>/dev/null)
                if [ "$novnc_code" = "200" ]; then
                    echo -e "   🖥️  noVNC Interface: ${GREEN}✅ Accessible (http://localhost:7900)${NC}"
                else
                    echo -e "   🖥️  noVNC Interface: ${RED}❌ Not Accessible (Code: $novnc_code)${NC}"
                fi
                
                # Check FastAPI status
                fastapi_response=$(curl -s http://localhost:8000/api/health 2>/dev/null)
                if echo "$fastapi_response" | grep -q '"ok":true' 2>/dev/null; then
                    echo -e "   🔧 FastAPI Backend: ${GREEN}✅ Running (http://localhost:8000)${NC}"
                else
                    echo -e "   🔧 FastAPI Backend: ${RED}❌ Not Running${NC}"
                fi
                
                # Check CAPTCHA API status
                captcha_response=$(curl -s http://localhost:8000/api/captcha/health 2>/dev/null)
                if echo "$captcha_response" | grep -q '"status":"healthy"' 2>/dev/null; then
                    echo -e "   🛡️  CAPTCHA API: ${GREEN}✅ Healthy${NC}"
                else
                    echo -e "   🛡️  CAPTCHA API: ${RED}❌ Not Healthy${NC}"
                fi
                
                # Check tunnel status
                if [ ! -z "$NOVNC_PUBLIC_URL" ]; then
                    tunnel_code=$(curl -s -o /dev/null -w "%{http_code}" "$NOVNC_PUBLIC_URL" --max-time 10 2>/dev/null)
                    if [ "$tunnel_code" = "200" ] || [ "$tunnel_code" = "401" ]; then
                        echo -e "   🌐 Public Tunnel: ${GREEN}✅ Accessible ($NOVNC_PUBLIC_URL)${NC}"
                    else
                        echo -e "   🌐 Public Tunnel: ${YELLOW}⚠️  May need configuration ($NOVNC_PUBLIC_URL)${NC}"
                    fi
                else
                    echo -e "   🌐 Public Tunnel: ${RED}❌ Not Configured${NC}"
                fi
                
                # Docker container status
                docker_status=$(docker ps --filter "name=son1k_selenium" --format "{{.Status}}" 2>/dev/null)
                if echo "$docker_status" | grep -q "Up" 2>/dev/null; then
                    echo -e "   🐳 Docker Container: ${GREEN}✅ Running ($docker_status)${NC}"
                else
                    echo -e "   🐳 Docker Container: ${RED}❌ Not Running${NC}"
                fi
                
                echo
                ;;
            5)
                echo "📋 Recent logs:"
                tail -20 "$LOG_FILE"
                ;;
            6)
                log "🌐 Configuring Cloudflare tunnel..."
                ./setup_cloudflare.sh
                ;;
            7)
                if [ -f "cloudflare.env" ]; then
                    log "📁 Loading Cloudflare configuration..."
                    source cloudflare.env
                    log "   ✅ Configuration loaded"
                    log "   🖥️  noVNC URL: $CLOUDFLARE_TUNNEL_URL"
                    log "   🔧 API Base: $SON1K_API_BASE"
                else
                    warn "cloudflare.env not found. Run option 6 first."
                fi
                ;;
            8)
                cleanup
                ;;
            *)
                warn "Invalid choice. Please select 1-8."
                ;;
        esac
        echo
    done
}

# Run main function
main "$@"