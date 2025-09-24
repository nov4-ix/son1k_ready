#!/bin/bash
"""
🔍 CHECK SYSTEM STATUS - Verificador de Estado del Sistema
Verifica el estado actual del sistema y muestra información detallada
"""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
echo "║                    🔍 SON1K SYSTEM STATUS 🔍                 ║"
echo "║              Verificador de Estado del Sistema               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Función para verificar proceso por PID
check_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            local uptime=$(ps -o etime= -p $pid | tr -d ' ')
            local cpu=$(ps -o %cpu= -p $pid | tr -d ' ')
            local mem=$(ps -o %mem= -p $pid | tr -d ' ')
            
            echo -e "✅ ${GREEN}$process_name${NC}: Activo (PID: $pid, Uptime: $uptime, CPU: ${cpu}%, Mem: ${mem}%)"
            return 0
        else
            echo -e "❌ ${RED}$process_name${NC}: Inactivo (PID file existe pero proceso no)"
            rm -f "$pid_file"
            return 1
        fi
    else
        echo -e "❌ ${RED}$process_name${NC}: No iniciado"
        return 1
    fi
}

# Función para verificar conectividad HTTP
check_http() {
    local url=$1
    local name=$2
    
    if curl -s --max-time 5 "$url" > /dev/null 2>&1; then
        local response_time=$(curl -s --max-time 5 -w "%{time_total}" "$url" -o /dev/null 2>&1)
        echo -e "✅ ${GREEN}$name${NC}: Respondiendo (${response_time}s)"
        return 0
    else
        echo -e "❌ ${RED}$name${NC}: No responde"
        return 1
    fi
}

# Función para verificar uso de recursos del sistema
check_system_resources() {
    echo -e "\n${CYAN}📊 RECURSOS DEL SISTEMA:${NC}"
    
    # CPU
    local cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        echo -e "⚠️  ${YELLOW}CPU: ${cpu_usage}% (Alto)${NC}"
    else
        echo -e "✅ ${GREEN}CPU: ${cpu_usage}%${NC}"
    fi
    
    # Memoria
    local mem_usage=$(vm_stat | grep "Pages active" | awk '{print $3}' | sed 's/\.//')
    local mem_total=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    local mem_percent=$((mem_usage * 100 / (mem_usage + mem_total)))
    
    if [ $mem_percent -gt 85 ]; then
        echo -e "⚠️  ${YELLOW}Memoria: ${mem_percent}% (Alto)${NC}"
    else
        echo -e "✅ ${GREEN}Memoria: ${mem_percent}%${NC}"
    fi
    
    # Disco
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $disk_usage -gt 90 ]; then
        echo -e "⚠️  ${YELLOW}Disco: ${disk_usage}% (Alto)${NC}"
    else
        echo -e "✅ ${GREEN}Disco: ${disk_usage}%${NC}"
    fi
}

# Función para verificar logs recientes
check_recent_logs() {
    echo -e "\n${CYAN}📝 LOGS RECIENTES:${NC}"
    
    local log_files=("logs/son1k_system.log" "logs/monitor.log" "logs/errors.log")
    
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            local size=$(du -h "$log_file" | cut -f1)
            local lines=$(wc -l < "$log_file")
            local errors=$(grep -c "ERROR\|CRITICAL" "$log_file" 2>/dev/null || echo "0")
            local warnings=$(grep -c "WARNING" "$log_file" 2>/dev/null || echo "0")
            
            echo -e "📄 ${log_file}: ${size} (${lines} líneas, ${errors} errores, ${warnings} warnings)"
            
            # Mostrar últimos errores
            if [ $errors -gt 0 ]; then
                echo -e "   ${RED}Últimos errores:${NC}"
                tail -3 "$log_file" | grep "ERROR\|CRITICAL" | head -2 | sed 's/^/   /'
            fi
        else
            echo -e "❌ ${log_file}: No existe"
        fi
    done
}

# Función para verificar archivos de configuración
check_config_files() {
    echo -e "\n${CYAN}⚙️  ARCHIVOS DE CONFIGURACIÓN:${NC}"
    
    local config_files=(
        "requirements.txt"
        "son1k_optimized_system.py"
        "system_monitor.py"
        "health_checker.py"
        "error_handler.py"
        ".venv"
    )
    
    for file in "${config_files[@]}"; do
        if [ -e "$file" ]; then
            if [ -d "$file" ]; then
                echo -e "✅ ${GREEN}$file${NC}: Directorio"
            else
                local size=$(du -h "$file" | cut -f1)
                echo -e "✅ ${GREEN}$file${NC}: ${size}"
            fi
        else
            echo -e "❌ ${RED}$file${NC}: No encontrado"
        fi
    done
}

# Función para verificar puertos
check_ports() {
    echo -e "\n${CYAN}🌐 PUERTOS:${NC}"
    
    local ports=(8000 5000 3000)
    
    for port in "${ports[@]}"; do
        if lsof -i :$port > /dev/null 2>&1; then
            local process=$(lsof -i :$port | awk 'NR==2 {print $1}')
            echo -e "✅ ${GREEN}Puerto $port${NC}: En uso por $process"
        else
            echo -e "❌ ${RED}Puerto $port${NC}: Libre"
        fi
    done
}

# Función para mostrar resumen de estado
show_status_summary() {
    echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗"
    echo "║                        📋 RESUMEN DE ESTADO                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
    
    local main_status=0
    local monitor_status=0
    local http_status=0
    
    # Verificar estado de procesos
    if [ -f ".main_system.pid" ]; then
        local pid=$(cat .main_system.pid)
        if ps -p $pid > /dev/null 2>&1; then
            main_status=1
        fi
    fi
    
    if [ -f ".monitor.pid" ]; then
        local pid=$(cat .monitor.pid)
        if ps -p $pid > /dev/null 2>&1; then
            monitor_status=1
        fi
    fi
    
    # Verificar HTTP
    if curl -s --max-time 5 http://localhost:8000/ > /dev/null 2>&1; then
        http_status=1
    fi
    
    # Mostrar resumen
    if [ $main_status -eq 1 ] && [ $monitor_status -eq 1 ] && [ $http_status -eq 1 ]; then
        echo -e "🎉 ${GREEN}ESTADO: COMPLETAMENTE OPERATIVO${NC}"
        echo -e "   ✅ Sistema principal: Activo"
        echo -e "   ✅ Monitor: Activo"
        echo -e "   ✅ Servidor HTTP: Respondiendo"
    elif [ $main_status -eq 1 ] && [ $http_status -eq 1 ]; then
        echo -e "⚠️  ${YELLOW}ESTADO: PARCIALMENTE OPERATIVO${NC}"
        echo -e "   ✅ Sistema principal: Activo"
        echo -e "   ❌ Monitor: Inactivo"
        echo -e "   ✅ Servidor HTTP: Respondiendo"
    else
        echo -e "❌ ${RED}ESTADO: NO OPERATIVO${NC}"
        echo -e "   ❌ Sistema principal: Inactivo"
        echo -e "   ❌ Monitor: Inactivo"
        echo -e "   ❌ Servidor HTTP: No responde"
    fi
    
    echo -e "\n${YELLOW}💡 Comandos útiles:${NC}"
    echo -e "   Iniciar: ./start_stable_system.sh"
    echo -e "   Detener: ./stop_stable_system.sh"
    echo -e "   Ver logs: tail -f logs/son1k_system.log"
    echo -e "   Health check: curl http://localhost:8000/health"
}

# Función principal
main() {
    echo -e "${CYAN}🔍 Verificando estado del sistema Son1k...${NC}\n"
    
    # Verificar procesos principales
    echo -e "${CYAN}🔄 PROCESOS PRINCIPALES:${NC}"
    check_process ".main_system.pid" "Sistema Principal"
    check_process ".monitor.pid" "Monitor"
    
    # Verificar conectividad
    echo -e "\n${CYAN}🌐 CONECTIVIDAD:${NC}"
    check_http "http://localhost:8000/" "Servidor Principal"
    check_http "http://localhost:8000/health" "Health Check"
    
    # Verificar recursos del sistema
    check_system_resources
    
    # Verificar logs
    check_recent_logs
    
    # Verificar configuración
    check_config_files
    
    # Verificar puertos
    check_ports
    
    # Mostrar resumen
    show_status_summary
}

# Ejecutar función principal
main "$@"

