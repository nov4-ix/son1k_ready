#!/bin/bash

# Son1kVers3 - Script de Inicio Completo
# Inicia tanto el backend FastAPI como el servidor Node.js

echo "🎵 Son1kVers3 - Iniciando Sistema Completo"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log_info "Verificando dependencias..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 no está instalado"
        exit 1
    fi
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js no está instalado"
        exit 1
    fi
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 no está instalado"
        exit 1
    fi
    
    log_success "Dependencias verificadas"
}

# Instalar dependencias Python
install_python_deps() {
    log_info "Instalando dependencias Python..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "Dependencias Python instaladas"
    else
        log_warning "No se encontró requirements.txt"
    fi
}

# Instalar dependencias Node.js
install_node_deps() {
    log_info "Instalando dependencias Node.js..."
    
    if [ -f "package.json" ]; then
        npm install
        log_success "Dependencias Node.js instaladas"
    else
        log_warning "No se encontró package.json"
    fi
}

# Iniciar servidor Node.js
start_node_server() {
    log_info "Iniciando servidor Node.js..."
    
    if [ -f "suno_wrapper_server.js" ]; then
        node suno_wrapper_server.js &
        NODE_PID=$!
        log_success "Servidor Node.js iniciado (PID: $NODE_PID)"
        echo $NODE_PID > node_server.pid
    else
        log_error "No se encontró suno_wrapper_server.js"
        exit 1
    fi
}

# Iniciar servidor Python
start_python_server() {
    log_info "Iniciando servidor Python FastAPI..."
    
    if [ -f "backend/app/main.py" ]; then
        cd backend
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
        PYTHON_PID=$!
        cd ..
        log_success "Servidor Python iniciado (PID: $PYTHON_PID)"
        echo $PYTHON_PID > python_server.pid
    else
        log_error "No se encontró backend/app/main.py"
        exit 1
    fi
}

# Verificar que los servidores estén funcionando
check_servers() {
    log_info "Verificando servidores..."
    
    # Esperar un poco para que los servidores se inicien
    sleep 5
    
    # Verificar Node.js
    if curl -s http://localhost:3001/health > /dev/null; then
        log_success "Servidor Node.js funcionando en puerto 3001"
    else
        log_warning "Servidor Node.js no responde en puerto 3001"
    fi
    
    # Verificar Python
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "Servidor Python funcionando en puerto 8000"
    else
        log_warning "Servidor Python no responde en puerto 8000"
    fi
}

# Mostrar información del sistema
show_system_info() {
    echo ""
    echo "🎵 Son1kVers3 - Sistema Iniciado"
    echo "================================="
    echo "🌐 Frontend: http://localhost:8000"
    echo "📡 API Python: http://localhost:8000/docs"
    echo "🎵 API Node.js: http://localhost:3001"
    echo "📊 Health Check: http://localhost:8000/health"
    echo ""
    echo "Para detener el sistema, presiona Ctrl+C"
    echo ""
}

# Función de limpieza
cleanup() {
    log_info "Deteniendo servidores..."
    
    if [ -f "node_server.pid" ]; then
        kill $(cat node_server.pid) 2>/dev/null
        rm node_server.pid
    fi
    
    if [ -f "python_server.pid" ]; then
        kill $(cat python_server.pid) 2>/dev/null
        rm python_server.pid
    fi
    
    log_success "Servidores detenidos"
    exit 0
}

# Configurar trap para limpieza
trap cleanup SIGINT SIGTERM

# Función principal
main() {
    echo "🎵 Son1kVers3 - Sistema de Generación Musical con IA"
    echo "====================================================="
    echo ""
    
    check_dependencies
    install_python_deps
    install_node_deps
    start_node_server
    start_python_server
    check_servers
    show_system_info
    
    # Mantener el script corriendo
    while true; do
        sleep 1
    done
}

# Ejecutar función principal
main



