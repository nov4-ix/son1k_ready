#!/bin/bash

# 🔍 SCRIPT DE DIAGNÓSTICO DEL SISTEMA CAPTCHA
# Ayuda a identificar por qué los servicios aparecen en rojo

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_service() {
    local service_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    echo -n "🔍 Testing $service_name... "
    
    if eval "$test_command" | grep -q "$expected_result" 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "   Command: $test_command"
        echo "   Expected: $expected_result"
        echo "   Got: $(eval "$test_command" 2>/dev/null || echo "COMMAND_FAILED")"
        return 1
    fi
}

main() {
    clear
    log "🔍 SISTEMA CAPTCHA - DIAGNÓSTICO COMPLETO"
    log "========================================"
    echo
    
    # 1. DOCKER SERVICES
    log "📋 1. DOCKER SERVICES"
    echo "-------------------"
    
    # Check if Docker is running
    if ! docker info &>/dev/null; then
        error "Docker no está ejecutándose. Inicia Docker Desktop."
        exit 1
    fi
    log "✅ Docker está ejecutándose"
    
    # Check Selenium container
    if docker ps | grep -q son1k_selenium; then
        log "✅ Container son1k_selenium está ejecutándose"
        docker ps --filter "name=son1k_selenium" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        error "Container son1k_selenium no está ejecutándose"
        log "💡 Ejecuta: docker compose up -d selenium"
    fi
    echo
    
    # 2. NETWORK CONNECTIVITY
    log "📋 2. NETWORK CONNECTIVITY"
    echo "--------------------------"
    
    # Test localhost ports
    check_service "Selenium WebDriver" "curl -s http://localhost:4444/wd/hub/status" '"ready"'
    check_service "noVNC Interface" "curl -s -o /dev/null -w '%{http_code}' http://localhost:7900" "200"
    
    # Check if FastAPI is running
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
        check_service "FastAPI Backend" "curl -s http://localhost:8000/api/health" '"ok"'
        check_service "CAPTCHA API" "curl -s http://localhost:8000/api/captcha/health" '"healthy"'
    else
        error "FastAPI no está ejecutándose en puerto 8000"
        log "💡 Ejecuta: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
    fi
    echo
    
    # 3. DETAILED SERVICE ANALYSIS
    log "📋 3. DETAILED SERVICE ANALYSIS"
    echo "-------------------------------"
    
    # Selenium detailed check
    log "🐳 Selenium WebDriver:"
    selenium_response=$(curl -s http://localhost:4444/wd/hub/status 2>/dev/null || echo "{}")
    echo "   Raw response: $selenium_response"
    if echo "$selenium_response" | jq . >/dev/null 2>&1; then
        echo "   JSON valid: ✅"
        ready_status=$(echo "$selenium_response" | jq -r '.value.ready // false' 2>/dev/null)
        echo "   Ready status: $ready_status"
    else
        echo "   JSON valid: ❌"
    fi
    echo
    
    # noVNC detailed check
    log "🖥️  noVNC Interface:"
    novnc_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7900 2>/dev/null || echo "000")
    echo "   HTTP Status: $novnc_code"
    if [ "$novnc_code" = "200" ]; then
        echo "   Status: ✅ Accessible"
    elif [ "$novnc_code" = "000" ]; then
        echo "   Status: ❌ Connection failed"
    else
        echo "   Status: ⚠️  Unexpected response code"
    fi
    echo
    
    # FastAPI detailed check
    log "🔧 FastAPI Backend:"
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
        echo "   Port 8000: ✅ Listening"
        
        health_response=$(curl -s http://localhost:8000/api/health 2>/dev/null || echo "{}")
        echo "   Health response: $health_response"
        
        captcha_response=$(curl -s http://localhost:8000/api/captcha/health 2>/dev/null || echo "{}")
        echo "   CAPTCHA response: $captcha_response"
    else
        echo "   Port 8000: ❌ Not listening"
        echo "   Process: $(lsof -Pi :8000 -sTCP:LISTEN 2>/dev/null || echo "None")"
    fi
    echo
    
    # 4. ENVIRONMENT VARIABLES
    log "📋 4. ENVIRONMENT VARIABLES"
    echo "---------------------------"
    
    vars=(
        "SV_SELENIUM_URL"
        "NOVNC_PUBLIC_URL"
        "SON1K_API_BASE"
        "CLOUDFLARE_TUNNEL_URL"
        "SV_HEADLESS"
        "SV_NO_QUIT"
    )
    
    for var in "${vars[@]}"; do
        value="${!var}"
        if [ -n "$value" ]; then
            echo "   $var = $value ✅"
        else
            echo "   $var = (not set) ⚠️"
        fi
    done
    echo
    
    # 5. PROCESS ANALYSIS
    log "📋 5. PROCESS ANALYSIS"
    echo "---------------------"
    
    log "Procesos en puertos clave:"
    echo "   Puerto 4444 (Selenium):"
    lsof -Pi :4444 -sTCP:LISTEN 2>/dev/null || echo "     No process listening"
    
    echo "   Puerto 7900 (noVNC):"
    lsof -Pi :7900 -sTCP:LISTEN 2>/dev/null || echo "     No process listening"
    
    echo "   Puerto 8000 (FastAPI):"
    lsof -Pi :8000 -sTCP:LISTEN 2>/dev/null || echo "     No process listening"
    echo
    
    # 6. RECOMMENDATIONS
    log "📋 6. RECOMMENDATIONS"
    echo "--------------------"
    
    if ! docker ps | grep -q son1k_selenium; then
        log "🔧 Para arreglar Docker Selenium:"
        echo "   docker compose up -d selenium"
        echo "   docker logs son1k_selenium"
        echo
    fi
    
    if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
        log "🔧 Para arreglar FastAPI:"
        echo "   cd \"$PWD\""
        echo "   source .venv/bin/activate"
        echo "   export PYTHONPATH=\"\$PWD\""
        echo "   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
        echo
    fi
    
    if [ -z "$SV_SELENIUM_URL" ]; then
        log "🔧 Para configurar variables de entorno:"
        echo "   export SV_SELENIUM_URL=\"http://localhost:4444\""
        echo "   export SON1K_API_BASE=\"http://localhost:8000\""
        echo
    fi
    
    # 7. QUICK FIX COMMANDS
    log "📋 7. QUICK FIX COMMANDS"
    echo "-----------------------"
    
    cat << 'EOF'
# Reiniciar todo el sistema:
docker compose down
docker compose up -d selenium
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &

# Verificar servicios:
curl http://localhost:4444/wd/hub/status
curl http://localhost:7900
curl http://localhost:8000/api/health
curl http://localhost:8000/api/captcha/health

# Variables de entorno básicas:
export SV_SELENIUM_URL="http://localhost:4444"
export SON1K_API_BASE="http://localhost:8000"
export SV_HEADLESS=0
export SV_NO_QUIT=1
EOF
    
    echo
    log "🎉 Diagnóstico completado!"
    log "Si sigues viendo errores, ejecuta los comandos de 'QUICK FIX' arriba."
}

main "$@"