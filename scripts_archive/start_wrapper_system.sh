#!/bin/bash

# 🎵 Son1k Suno Wrapper System Startup Script
# Inicia tanto el wrapper Node.js como la API Python

echo "🎵 Iniciando Sistema Son1k con Suno Wrapper"
echo "============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con color
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

# Verificar que estamos en el directorio correcto
if [ ! -f "suno_wrapper_server.js" ]; then
    log_error "No se encontró suno_wrapper_server.js. Ejecutar desde el directorio raíz del proyecto."
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js no está instalado. Instalar Node.js primero."
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 no está instalado. Instalar Python3 primero."
    exit 1
fi

# Verificar dependencias Node.js
log_info "Verificando dependencias Node.js..."
if [ ! -d "node_modules" ]; then
    log_warning "node_modules no encontrado. Instalando dependencias..."
    npm install
    if [ $? -ne 0 ]; then
        log_error "Error instalando dependencias Node.js"
        exit 1
    fi
    log_success "Dependencias Node.js instaladas"
else
    log_success "Dependencias Node.js encontradas"
fi

# Verificar dependencias Python
log_info "Verificando dependencias Python..."
if [ ! -f "requirements.txt" ]; then
    log_warning "requirements.txt no encontrado"
else
    log_info "Instalando dependencias Python..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        log_warning "Algunas dependencias Python no se pudieron instalar"
    else
        log_success "Dependencias Python instaladas"
    fi
fi

# Función para limpiar procesos al salir
cleanup() {
    log_info "Cerrando procesos..."
    if [ ! -z "$WRAPPER_PID" ]; then
        kill $WRAPPER_PID 2>/dev/null
        log_info "Wrapper Node.js cerrado"
    fi
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        log_info "API Python cerrada"
    fi
    exit 0
}

# Configurar trap para limpiar al salir
trap cleanup SIGINT SIGTERM

# Iniciar wrapper Node.js stealth
log_info "Iniciando Suno Ultra-Stealth Wrapper Server (Node.js)..."
node suno_stealth_wrapper.js &
WRAPPER_PID=$!

# Esperar un momento para que el wrapper inicie
sleep 3

# Verificar que el wrapper esté funcionando
log_info "Verificando wrapper..."
if curl -s http://localhost:3001/health > /dev/null; then
    log_success "Wrapper Node.js funcionando en puerto 3001"
else
    log_warning "Wrapper Node.js no responde en puerto 3001"
fi

# Iniciar API Python
log_info "Iniciando API Python..."
python3 main_production_final.py &
API_PID=$!

# Esperar un momento para que la API inicie
sleep 3

# Verificar que la API esté funcionando
log_info "Verificando API..."
if curl -s http://localhost:8000/api/status > /dev/null; then
    log_success "API Python funcionando en puerto 8000"
else
    log_warning "API Python no responde en puerto 8000"
fi

# Mostrar información del sistema
echo ""
echo "🎉 Sistema Son1k con Suno Wrapper iniciado"
echo "============================================="
echo "🌐 Frontend: http://localhost:8000"
echo "🎵 Wrapper Suno: http://localhost:3001"
echo "🔧 API Principal: http://localhost:8000/api"
echo ""
echo "📊 Endpoints disponibles:"
echo "  - Wrapper Health: http://localhost:3001/health"
echo "  - Wrapper Stats: http://localhost:3001/stats"
echo "  - API Health: http://localhost:8000/api/status"
echo "  - API Generate: http://localhost:8000/api/generate"
echo ""
echo "🧪 Para probar la integración:"
echo "  python3 test_wrapper_integration.py"
echo ""
echo "⏹️  Presiona Ctrl+C para detener el sistema"
echo ""

# Mantener el script ejecutándose
wait
