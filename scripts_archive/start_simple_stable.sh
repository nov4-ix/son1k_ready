#!/bin/bash
"""
🚀 START SIMPLE STABLE - Inicio Simple y Estable
Versión simplificada que evita los problemas de importación
"""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR: $1${NC}"
}

echo -e "${BLUE}🎵 Iniciando Son1k Simple y Estable...${NC}"

# 1. Limpiar procesos existentes
log "🧹 Limpiando procesos..."
pkill -f son1k_optimized_system.py 2>/dev/null || true
pkill -f system_monitor.py 2>/dev/null || true
sleep 2

# 2. Crear directorios necesarios
mkdir -p logs generated_audio temp

# 3. Activar entorno virtual
source .venv/bin/activate

# 4. Iniciar sistema principal con timeout
log "🚀 Iniciando sistema principal..."
timeout 30s python3 son1k_optimized_system.py &
MAIN_PID=$!

# 5. Esperar y verificar
sleep 5

if ps -p $MAIN_PID > /dev/null; then
    log "✅ Sistema iniciado (PID: $MAIN_PID)"
    echo $MAIN_PID > .main_system.pid
    
    # Verificar que responda
    sleep 3
    if curl -s http://localhost:8000/ > /dev/null; then
        log "✅ Servidor respondiendo correctamente"
        echo -e "\n${GREEN}🎉 Sistema funcionando en: http://localhost:8000${NC}"
    else
        warn "⚠️ Servidor no responde aún, pero proceso está activo"
    fi
else
    error "❌ Fallo al iniciar sistema"
    exit 1
fi

# 6. Iniciar monitor simple en background
log "🛡️ Iniciando monitor simple..."
nohup python3 -c "
import time
import psutil
import requests
import os

def monitor_system():
    while True:
        try:
            # Verificar proceso principal
            if os.path.exists('.main_system.pid'):
                with open('.main_system.pid', 'r') as f:
                    pid = int(f.read().strip())
                if not psutil.pid_exists(pid):
                    print('⚠️ Proceso principal perdido, reiniciando...')
                    os.system('pkill -f son1k_optimized_system.py')
                    time.sleep(2)
                    os.system('source .venv/bin/activate && python3 son1k_optimized_system.py &')
                    time.sleep(5)
                    continue
            
            # Verificar respuesta HTTP
            try:
                response = requests.get('http://localhost:8000/', timeout=5)
                if response.status_code != 200:
                    print('⚠️ Servidor no responde correctamente')
            except:
                print('⚠️ Servidor no accesible')
            
            time.sleep(30)  # Verificar cada 30 segundos
        except Exception as e:
            print(f'Error en monitor: {e}')
            time.sleep(30)

if __name__ == '__main__':
    monitor_system()
" > logs/simple_monitor.log 2>&1 &
MONITOR_PID=$!

echo $MONITOR_PID > .monitor.pid
log "✅ Monitor simple iniciado (PID: $MONITOR_PID)"

echo -e "\n${GREEN}🎉 Sistema Simple y Estable iniciado exitosamente!${NC}"
echo -e "${YELLOW}💡 Para detener: pkill -f son1k_optimized_system.py${NC}"
echo -e "${YELLOW}💡 Para ver logs: tail -f logs/simple_monitor.log${NC}"

