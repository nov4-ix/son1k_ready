#!/bin/bash
"""
🛑 STOP STABLE SYSTEM - Script de Detención Segura
Detiene el sistema de forma segura y limpia
"""

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

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🛑 STOPPING SON1K SYSTEM 🛑               ║"
echo "║              Deteniendo Sistema de Forma Segura              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Función para detener proceso por PID
stop_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            log "Deteniendo $process_name (PID: $pid)..."
            
            # Intentar terminación graceful primero
            kill -TERM $pid 2>/dev/null
            
            # Esperar hasta 10 segundos
            local count=0
            while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Si aún está ejecutándose, forzar terminación
            if ps -p $pid > /dev/null 2>&1; then
                warn "Forzando terminación de $process_name..."
                kill -9 $pid 2>/dev/null
                sleep 1
            fi
            
            if ps -p $pid > /dev/null 2>&1; then
                error "No se pudo detener $process_name"
                return 1
            else
                log "✅ $process_name detenido exitosamente"
                rm -f "$pid_file"
                return 0
            fi
        else
            log "✅ $process_name ya estaba detenido"
            rm -f "$pid_file"
            return 0
        fi
    else
        log "✅ $process_name no estaba ejecutándose"
        return 0
    fi
}

# Función para limpiar procesos huérfanos
cleanup_orphaned_processes() {
    log "🧹 Limpiando procesos huérfanos..."
    
    # Buscar procesos de son1k que puedan haber quedado
    local pids=$(ps aux | grep -E "(son1k_optimized_system|system_monitor)" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$pids" ]; then
        warn "Encontrados procesos huérfanos: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
        log "✅ Procesos huérfanos limpiados"
    else
        log "✅ No hay procesos huérfanos"
    fi
}

# Función para limpiar archivos temporales
cleanup_temp_files() {
    log "🧹 Limpiando archivos temporales..."
    
    # Limpiar archivos .pid
    rm -f .main_system.pid .monitor.pid
    
    # Limpiar archivos temporales
    rm -f temp/*.tmp 2>/dev/null || true
    
    # Limpiar logs muy antiguos (más de 7 días)
    find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    log "✅ Archivos temporales limpiados"
}

# Función para crear backup de logs importantes
backup_logs() {
    log "💾 Creando backup de logs importantes..."
    
    local backup_dir="backups/logs_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Copiar logs importantes
    cp logs/*.log "$backup_dir/" 2>/dev/null || true
    
    # Crear resumen
    cat > "$backup_dir/summary.txt" << EOF
Backup creado: $(date)
Sistema: Son1k Stable System
Logs incluidos:
$(ls -la "$backup_dir"/*.log 2>/dev/null || echo "No hay logs")
EOF
    
    log "✅ Backup creado en: $backup_dir"
}

# Función para mostrar estadísticas finales
show_final_stats() {
    echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗"
    echo "║                        📊 ESTADÍSTICAS FINALES                ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
    
    # Verificar que no queden procesos
    local remaining=$(ps aux | grep -E "(son1k_optimized_system|system_monitor)" | grep -v grep | wc -l)
    
    if [ "$remaining" -eq 0 ]; then
        echo -e "🎵 Sistema Principal: ${GREEN}Detenido${NC}"
        echo -e "🛡️ Monitor: ${GREEN}Detenido${NC}"
        echo -e "🧹 Limpieza: ${GREEN}Completada${NC}"
        echo -e "\n${GREEN}✅ Sistema detenido exitosamente${NC}"
    else
        echo -e "⚠️ Aún quedan $remaining procesos ejecutándose"
        echo -e "💡 Ejecuta 'ps aux | grep son1k' para ver detalles"
    fi
    
    echo -e "\n${YELLOW}💡 Para reiniciar: ./start_stable_system.sh${NC}"
}

# Función principal
main() {
    log "Iniciando detención segura del sistema..."
    
    # Detener procesos principales
    stop_process ".monitor.pid" "Monitor"
    stop_process ".main_system.pid" "Sistema Principal"
    
    # Limpiar procesos huérfanos
    cleanup_orphaned_processes
    
    # Crear backup de logs
    backup_logs
    
    # Limpiar archivos temporales
    cleanup_temp_files
    
    # Mostrar estadísticas finales
    show_final_stats
}

# Ejecutar función principal
main "$@"

