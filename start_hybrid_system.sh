#!/bin/bash

# 🎵 Son1k Hybrid Stealth System Launcher
# Suno Real + Ollama Proxy = Máxima Robustez

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funciones de logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_hybrid() {
    echo -e "${PURPLE}🎵 $1${NC}"
}

log_ollama() {
    echo -e "${CYAN}🧠 $1${NC}"
}

# Función de limpieza
cleanup() {
    log_info "Limpiando procesos..."
    pkill -f suno_hybrid_stealth.js 2>/dev/null || true
    pkill -f ollama 2>/dev/null || true
    pkill -f main_production_final.py 2>/dev/null || true
    log_success "Limpieza completada"
    exit 0
}

# Configurar trap para limpiar al salir
trap cleanup SIGINT SIGTERM

log_hybrid "Son1k Hybrid Stealth System"
log_hybrid "Suno Real + Ollama Proxy = Máxima Robustez"
echo "================================================"

# Verificar dependencias
log_info "Verificando dependencias..."

# Verificar Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js no está instalado"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 no está instalado"
    exit 1
fi

# Verificar Ollama
if ! command -v ollama &> /dev/null; then
    log_warning "Ollama no está instalado - el proxy estará deshabilitado"
    OLLAMA_AVAILABLE=false
else
    log_success "Ollama encontrado"
    OLLAMA_AVAILABLE=true
fi

# Verificar Puppeteer
if [ ! -d "node_modules/puppeteer" ]; then
    log_info "Instalando Puppeteer..."
    npm install puppeteer
fi

log_success "Dependencias verificadas"

# Iniciar Ollama si está disponible
if [ "$OLLAMA_AVAILABLE" = true ]; then
    log_ollama "Iniciando Ollama (Proxy IA)..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 3
    
    # Verificar que Ollama esté funcionando
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_success "Ollama funcionando en puerto 11434"
    else
        log_warning "Ollama no responde - continuando sin proxy"
        OLLAMA_AVAILABLE=false
    fi
else
    log_warning "Ollama no disponible - usando solo Suno"
fi

# Iniciar sistema híbrido
log_hybrid "Iniciando Suno Hybrid Stealth System (Node.js)..."
node suno_hybrid_stealth.js &
HYBRID_PID=$!

# Esperar un momento para que el sistema híbrido inicie
sleep 3

# Verificar que el sistema híbrido esté funcionando
log_info "Verificando sistema híbrido..."
if curl -s http://localhost:3003/health > /dev/null 2>&1; then
    log_success "Sistema híbrido funcionando en puerto 3003"
else
    log_error "Sistema híbrido no responde"
    exit 1
fi

# Iniciar API Python (opcional)
log_info "Iniciando API Python (opcional)..."
python3 main_production_final.py &
API_PID=$!

sleep 2

# Verificar API Python
if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    log_success "API Python funcionando en puerto 8000"
else
    log_warning "API Python no responde - continuando sin ella"
fi

# Mostrar estado final
log_hybrid "Sistema híbrido iniciado exitosamente"
echo "================================================"
log_info "🌐 Frontend: http://localhost:8000"
log_info "🎵 Sistema Híbrido: http://localhost:3003"
log_info "🤖 Suno Real: Puppeteer + Navegador"
if [ "$OLLAMA_AVAILABLE" = true ]; then
    log_info "🧠 Ollama Proxy: http://localhost:11434"
fi
log_info "🔧 API Python: http://localhost:8000/api"
echo ""
log_info "📊 Endpoints disponibles:"
log_info "  - Hybrid Health: http://localhost:3003/health"
log_info "  - Hybrid Stats: http://localhost:3003/stats"
log_info "  - Generate Music: http://localhost:3003/generate-music"
if [ "$OLLAMA_AVAILABLE" = true ]; then
    log_info "  - Ollama Health: http://localhost:11434/api/tags"
fi
echo ""
log_hybrid "Características híbridas activas:"
log_success "  ✅ Suno real con Puppeteer (música real)"
if [ "$OLLAMA_AVAILABLE" = true ]; then
    log_success "  ✅ Ollama como proxy/fallback"
fi
log_success "  ✅ Generación híbrida inteligente"
log_success "  ✅ Pool de navegadores optimizado"
log_success "  ✅ Estadísticas en tiempo real"
log_success "  ✅ Manejo de errores robusto"
echo ""
log_info "🧪 Para probar el sistema híbrido:"
log_info "  curl -X POST http://localhost:3003/generate-music \\"
log_info "    -H 'Content-Type: application/json' \\"
log_info "    -d '{\"prompt\":\"una canción épica de synthwave\"}'"
echo ""
log_info "⏹️  Presiona Ctrl+C para detener el sistema"

# Mantener el script corriendo
wait $HYBRID_PID $API_PID


