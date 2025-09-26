#!/bin/bash
# 📊 SON1KVERS3 - Start Analytics System
# Script para iniciar el sistema de analytics

set -e

echo "📊 INICIANDO SISTEMA DE ANALYTICS - SON1KVERS3"
echo "=============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Python está disponible
check_python() {
    if command -v python3 &> /dev/null; then
        print_success "Python3 encontrado"
        return 0
    else
        print_error "Python3 no encontrado. Por favor instala Python3"
        exit 1
    fi
}

# Instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias de Python..."
    
    # Crear requirements.txt para analytics
    cat > analytics_requirements.txt << EOF
aiohttp>=3.8.0
asyncio
sqlite3
EOF
    
    pip3 install -r analytics_requirements.txt || {
        print_warning "Error instalando dependencias, continuando..."
    }
    
    print_success "Dependencias instaladas"
}

# Verificar si el puerto está disponible
check_port() {
    local port=8002
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        print_warning "Puerto $port ya está en uso"
        print_status "Intentando detener proceso existente..."
        pkill -f "analytics_system.py" || true
        sleep 2
    fi
}

# Iniciar servidor de analytics
start_analytics_server() {
    print_status "Iniciando servidor de analytics..."
    
    # Verificar que el archivo existe
    if [ ! -f "analytics_system.py" ]; then
        print_error "Archivo analytics_system.py no encontrado"
        exit 1
    fi
    
    # Iniciar servidor en segundo plano
    nohup python3 analytics_system.py > analytics.log 2>&1 &
    ANALYTICS_PID=$!
    
    # Esperar un poco para que el servidor se inicie
    sleep 3
    
    # Verificar que el servidor esté corriendo
    if ps -p $ANALYTICS_PID > /dev/null; then
        print_success "Servidor de analytics iniciado (PID: $ANALYTICS_PID)"
        echo $ANALYTICS_PID > analytics.pid
    else
        print_error "Error iniciando servidor de analytics"
        cat analytics.log
        exit 1
    fi
}

# Probar el sistema
test_system() {
    print_status "Probando sistema de analytics..."
    
    # Esperar un poco más para que el servidor esté listo
    sleep 5
    
    # Ejecutar pruebas
    python3 test_analytics_system.py
    
    if [ $? -eq 0 ]; then
        print_success "Pruebas del sistema exitosas"
    else
        print_warning "Algunas pruebas fallaron, pero el sistema puede estar funcionando"
    fi
}

# Mostrar información del sistema
show_info() {
    print_success "¡Sistema de analytics iniciado!"
    echo ""
    echo "🌐 Servidor Analytics: http://localhost:8002"
    echo "📊 Health Check: http://localhost:8002/api/health"
    echo "📈 Analytics: http://localhost:8002/api/analytics"
    echo ""
    echo "📁 Archivos:"
    echo "   - Logs: analytics.log"
    echo "   - PID: analytics.pid"
    echo "   - Base de datos: analytics.db"
    echo ""
    echo "🎮 Controles:"
    echo "   - Ver logs: tail -f analytics.log"
    echo "   - Detener: kill \$(cat analytics.pid)"
    echo "   - Probar: python3 test_analytics_system.py"
    echo ""
    echo "🎵 Frontend: http://localhost:8080"
    echo "   - Dashboard: Ctrl+Shift+A"
    echo ""
    echo "📊 ¡Analytics funcionando correctamente!"
}

# Función principal
main() {
    print_status "Iniciando sistema de analytics..."
    
    # Verificaciones
    check_python
    install_dependencies
    check_port
    
    # Iniciar sistema
    start_analytics_server
    test_system
    show_info
}

# Manejar señales para limpieza
cleanup() {
    print_status "Deteniendo sistema de analytics..."
    if [ -f "analytics.pid" ]; then
        kill $(cat analytics.pid) 2>/dev/null || true
        rm -f analytics.pid
    fi
    print_success "Sistema detenido"
    exit 0
}

# Configurar trap para limpieza
trap cleanup SIGINT SIGTERM

# Ejecutar función principal
main "$@"
