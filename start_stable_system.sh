#!/bin/bash
"""
🚀 START STABLE SYSTEM - Script de Inicio Estable
Inicia el sistema con monitoreo automático y recuperación
"""

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎵 SON1K STABLE SYSTEM 🎵                 ║"
echo "║              Sistema de Generación Musical Estable           ║"
echo "║              Con Monitoreo y Recuperación Automática         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "son1k_optimized_system.py" ]; then
    error "No se encontró son1k_optimized_system.py. Ejecuta desde el directorio correcto."
    exit 1
fi

# Función para limpiar procesos existentes
cleanup_existing_processes() {
    log "🧹 Limpiando procesos existentes..."
    
    # Buscar y terminar procesos de son1k
    PIDS=$(ps aux | grep -E "(son1k_optimized_system|system_monitor)" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$PIDS" ]; then
        warn "Encontrados procesos existentes: $PIDS"
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        sleep 2
        log "✅ Procesos anteriores terminados"
    else
        log "✅ No hay procesos existentes"
    fi
}

# Función para verificar dependencias
check_dependencies() {
    log "🔍 Verificando dependencias..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 no está instalado"
        exit 1
    fi
    
    # Verificar entorno virtual
    if [ ! -d ".venv" ]; then
        warn "Entorno virtual no encontrado, creando..."
        python3 -m venv .venv
    fi
    
    # Activar entorno virtual
    source .venv/bin/activate
    
    # Verificar dependencias críticas
    python3 -c "import fastapi, uvicorn, requests" 2>/dev/null || {
        error "Dependencias faltantes. Instalando..."
        pip install -r requirements.txt
    }
    
    log "✅ Dependencias verificadas"
}

# Función para crear directorios necesarios
create_directories() {
    log "📁 Creando directorios necesarios..."
    
    mkdir -p generated_audio
    mkdir -p logs
    mkdir -p temp
    mkdir -p backups
    
    log "✅ Directorios creados"
}

# Función para configurar logging
setup_logging() {
    log "📝 Configurando sistema de logging..."
    
    # Crear archivo de configuración de logging
    cat > logging_config.json << EOF
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/son1k_system.log",
            "maxBytes": 10485760,
            "backupCount": 5
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,
            "backupCount": 3
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": false
        },
        "error": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": false
        }
    }
}
EOF
    
    log "✅ Logging configurado"
}

# Función para iniciar el sistema principal
start_main_system() {
    log "🚀 Iniciando sistema principal..."
    
    # Activar entorno virtual
    source .venv/bin/activate
    
    # Iniciar sistema principal en background
    nohup python3 son1k_optimized_system.py > logs/main_system.log 2>&1 &
    MAIN_PID=$!
    
    # Esperar a que inicie
    sleep 5
    
    # Verificar que esté funcionando
    if ps -p $MAIN_PID > /dev/null; then
        log "✅ Sistema principal iniciado (PID: $MAIN_PID)"
        echo $MAIN_PID > .main_system.pid
    else
        error "❌ Fallo al iniciar sistema principal"
        exit 1
    fi
}

# Función para iniciar el monitor
start_monitor() {
    log "🛡️ Iniciando sistema de monitoreo..."
    
    # Activar entorno virtual
    source .venv/bin/activate
    
    # Iniciar monitor en background
    nohup python3 system_monitor.py > logs/monitor.log 2>&1 &
    MONITOR_PID=$!
    
    # Esperar a que inicie
    sleep 2
    
    # Verificar que esté funcionando
    if ps -p $MONITOR_PID > /dev/null; then
        log "✅ Monitor iniciado (PID: $MONITOR_PID)"
        echo $MONITOR_PID > .monitor.pid
    else
        error "❌ Fallo al iniciar monitor"
        exit 1
    fi
}

# Función para verificar el estado del sistema
check_system_status() {
    log "🔍 Verificando estado del sistema..."
    
    # Verificar que los procesos estén ejecutándose
    if [ -f ".main_system.pid" ]; then
        MAIN_PID=$(cat .main_system.pid)
        if ps -p $MAIN_PID > /dev/null; then
            log "✅ Sistema principal activo (PID: $MAIN_PID)"
        else
            error "❌ Sistema principal no está ejecutándose"
            return 1
        fi
    fi
    
    if [ -f ".monitor.pid" ]; then
        MONITOR_PID=$(cat .monitor.pid)
        if ps -p $MONITOR_PID > /dev/null; then
            log "✅ Monitor activo (PID: $MONITOR_PID)"
        else
            error "❌ Monitor no está ejecutándose"
            return 1
        fi
    fi
    
    # Verificar que el servidor responda
    sleep 3
    if curl -s http://localhost:8000/ > /dev/null; then
        log "✅ Servidor HTTP respondiendo"
    else
        warn "⚠️ Servidor HTTP no responde aún"
    fi
    
    return 0
}

# Función para mostrar información del sistema
show_system_info() {
    echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗"
    echo "║                        📊 ESTADO DEL SISTEMA                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
    
    if [ -f ".main_system.pid" ]; then
        MAIN_PID=$(cat .main_system.pid)
        echo -e "🎵 Sistema Principal: ${GREEN}Activo${NC} (PID: $MAIN_PID)"
    else
        echo -e "🎵 Sistema Principal: ${RED}Inactivo${NC}"
    fi
    
    if [ -f ".monitor.pid" ]; then
        MONITOR_PID=$(cat .monitor.pid)
        echo -e "🛡️ Monitor: ${GREEN}Activo${NC} (PID: $MONITOR_PID)"
    else
        echo -e "🛡️ Monitor: ${RED}Inactivo${NC}"
    fi
    
    echo -e "🌐 Servidor: http://localhost:8000"
    echo -e "📊 Health Check: http://localhost:8000/health"
    echo -e "📝 Logs: logs/"
    
    echo -e "\n${YELLOW}💡 Comandos útiles:${NC}"
    echo -e "   Ver logs: tail -f logs/main_system.log"
    echo -e "   Ver monitor: tail -f logs/monitor.log"
    echo -e "   Detener: ./stop_stable_system.sh"
    echo -e "   Estado: ./check_system_status.sh"
}

# Función principal
main() {
    log "Iniciando Son1k Stable System..."
    
    # Ejecutar pasos de inicialización
    cleanup_existing_processes
    check_dependencies
    create_directories
    setup_logging
    
    # Iniciar componentes
    start_main_system
    start_monitor
    
    # Verificar estado
    if check_system_status; then
        show_system_info
        log "🎉 ¡Sistema iniciado exitosamente!"
    else
        error "❌ Fallo al verificar el sistema"
        exit 1
    fi
}

# Manejar señales de terminación
cleanup_on_exit() {
    log "🛑 Recibida señal de terminación, limpiando..."
    if [ -f ".main_system.pid" ]; then
        kill $(cat .main_system.pid) 2>/dev/null || true
        rm -f .main_system.pid
    fi
    if [ -f ".monitor.pid" ]; then
        kill $(cat .monitor.pid) 2>/dev/null || true
        rm -f .monitor.pid
    fi
    exit 0
}

trap cleanup_on_exit SIGINT SIGTERM

# Ejecutar función principal
main "$@"

