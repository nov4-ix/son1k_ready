#!/bin/bash

# 🌐 SCRIPT PARA CONFIGURAR CLOUDFLARE TUNNEL
# Configura túnel de Cloudflare para noVNC (puerto 7900) y FastAPI (puerto 8000)

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"
}

main() {
    clear
    log "🌐 CLOUDFLARE TUNNEL CONFIGURATION"
    log "=================================="
    echo
    
    log "Para usar Cloudflare tunnel con el sistema CAPTCHA, necesitas configurar:"
    echo
    echo -e "${BLUE}1. Puerto 7900${NC} (noVNC) - Para que usuarios resuelvan CAPTCHAs"
    echo -e "${BLUE}2. Puerto 8000${NC} (FastAPI) - Para APIs del backend"
    echo
    
    # Check if cloudflared is installed
    if ! command -v cloudflared &> /dev/null; then
        warn "cloudflared no está instalado. Instalando..."
        if command -v brew &> /dev/null; then
            brew install cloudflared
        else
            log "Instala cloudflared desde: https://github.com/cloudflare/cloudflared/releases"
            exit 1
        fi
    fi
    
    log "✅ cloudflared disponible"
    echo
    
    # Ask for tunnel configuration
    read -p "¿Ya tienes un túnel de Cloudflare configurado? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Use existing tunnel
        read -p "Ingresa la URL base de tu túnel (ej: https://mi-tunnel.example.com): " base_url
        
        if [ -z "$base_url" ]; then
            echo "❌ URL requerida"
            exit 1
        fi
        
        # Remove trailing slash
        base_url=$(echo "$base_url" | sed 's/\/$//')
        
        novnc_url="${base_url}"
        api_url="${base_url}"
        
        log "✅ Usando túnel existente:"
        log "   🖥️  noVNC: $novnc_url"
        log "   🔧 API: $api_url"
        
    else
        # Create new tunnel
        log "🚀 Configurando nuevo túnel de Cloudflare..."
        
        # Login to Cloudflare
        log "1. Iniciando sesión en Cloudflare..."
        cloudflared tunnel login
        
        # Create tunnel
        tunnel_name="suno-captcha-$(date +%s)"
        log "2. Creando túnel: $tunnel_name"
        cloudflared tunnel create "$tunnel_name"
        
        # Get tunnel ID
        tunnel_id=$(cloudflared tunnel list | grep "$tunnel_name" | awk '{print $1}')
        
        if [ -z "$tunnel_id" ]; then
            echo "❌ Error obteniendo tunnel ID"
            exit 1
        fi
        
        log "✅ Túnel creado: $tunnel_id"
        
        # Create config file
        config_dir="$HOME/.cloudflared"
        mkdir -p "$config_dir"
        
        cat > "$config_dir/config.yml" << EOF
tunnel: $tunnel_id
credentials-file: $config_dir/$tunnel_id.json

ingress:
  # noVNC for CAPTCHA resolution
  - hostname: novnc-$tunnel_name.example.com
    service: http://localhost:7900
  # FastAPI backend
  - hostname: api-$tunnel_name.example.com
    service: http://localhost:8000
  # Catch-all rule
  - service: http_status:404
EOF
        
        log "✅ Configuración creada en $config_dir/config.yml"
        log "⚠️  IMPORTANTE: Actualiza los hostnames en el archivo de configuración"
        log "   Edita: $config_dir/config.yml"
        log "   Cambia 'example.com' por tu dominio real"
        
        # Instructions for DNS
        echo
        log "📋 PRÓXIMOS PASOS:"
        log "1. Editar $config_dir/config.yml con tus dominios reales"
        log "2. Configurar DNS records en Cloudflare Dashboard:"
        log "   - novnc-$tunnel_name.tudominio.com -> CNAME -> $tunnel_id.cfargotunnel.com"
        log "   - api-$tunnel_name.tudominio.com -> CNAME -> $tunnel_id.cfargotunnel.com"
        log "3. Ejecutar: cloudflared tunnel run $tunnel_name"
        
        novnc_url="https://novnc-$tunnel_name.tudominio.com"
        api_url="https://api-$tunnel_name.tudominio.com"
    fi
    
    echo
    log "🔧 CONFIGURACIÓN PARA EL SISTEMA:"
    echo
    echo "export CLOUDFLARE_TUNNEL_URL=\"$novnc_url\""
    echo "export SON1K_API_BASE=\"$api_url\""
    echo
    
    # Save to env file
    cat > cloudflare.env << EOF
# Cloudflare Tunnel Configuration
export CLOUDFLARE_TUNNEL_URL="$novnc_url"
export SON1K_API_BASE="$api_url"

# Other required variables
export SV_SELENIUM_URL="http://localhost:4444"
export SV_HEADLESS=0
export SV_NO_QUIT=1
export SON1K_FRONTEND_PUSH=1
EOF
    
    log "✅ Configuración guardada en cloudflare.env"
    echo
    
    log "🚀 PARA USAR CON EL SISTEMA:"
    echo "1. source cloudflare.env"
    echo "2. ./start_captcha_system.sh"
    echo
    
    log "🌐 URLs DEL SISTEMA:"
    log "   🖥️  noVNC (usuarios): $novnc_url"
    log "   🔧 API Backend: $api_url"
    log "   🛡️  CAPTCHA API: $api_url/api/captcha/health"
    echo
    
    # Test connectivity if tunnel exists
    read -p "¿Probar conectividad ahora? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "🧪 Probando conectividad..."
        
        # Test noVNC
        if curl -s -o /dev/null -w "%{http_code}" "$novnc_url" --max-time 10 | grep -q "200\|401"; then
            log "   ✅ noVNC accesible"
        else
            warn "   ⚠️  noVNC no accesible (puede necesitar configuración)"
        fi
        
        # Test API (if running)
        if curl -s "$api_url/api/health" --max-time 10 2>/dev/null | grep -q "ok"; then
            log "   ✅ API Backend accesible"
        else
            warn "   ⚠️  API Backend no accesible (asegúrate de que esté corriendo)"
        fi
    fi
    
    log "🎉 Configuración de Cloudflare completada!"
}

main "$@"