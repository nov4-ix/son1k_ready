#!/bin/bash
"""
🔧 INSTALL EXTENSION - Instalador de Extensión de Chrome
Script para instalar y configurar la extensión de Son1k
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

info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] INFO: $1${NC}"
}

echo -e "${BLUE}🔧 Instalando Extensión de Chrome Son1k...${NC}"

# Verificar que Chrome esté instalado
if ! command -v google-chrome &> /dev/null && ! command -v chrome &> /dev/null; then
    error "Chrome no está instalado. Por favor instala Google Chrome primero."
    exit 1
fi

# Verificar que el servidor esté funcionando
log "🔍 Verificando servidor..."
if ! curl -s http://localhost:8000/api/extension/status > /dev/null; then
    error "El servidor no está funcionando. Inicia el servidor primero:"
    echo "  source .venv/bin/activate && python3 son1k_simple_stable.py"
    exit 1
fi

log "✅ Servidor funcionando"

# Crear directorio de extensión temporal
EXT_DIR="/tmp/son1k_extension_$(date +%s)"
log "📁 Creando directorio temporal: $EXT_DIR"

mkdir -p "$EXT_DIR"
cp -r extension/* "$EXT_DIR/"

# Actualizar manifest para desarrollo
cat > "$EXT_DIR/manifest.json" << 'EOF'
{
  "manifest_version": 3,
  "name": "Son1k Extension (Dev)",
  "version": "3.1.0",
  "description": "Son1k-Suno Bridge - Development Version",
  "action": {
    "default_title": "Son1k Extension",
    "default_popup": "popup_testing.html"
  },
  "permissions": [
    "storage",
    "activeTab",
    "tabs",
    "scripting"
  ],
  "host_permissions": [
    "http://localhost:8000/*",
    "https://suno.com/*",
    "https://*.suno.com/*"
  ],
  "background": {
    "service_worker": "background_robust.js"
  },
  "content_scripts": [
    {
      "matches": ["https://suno.com/*", "https://*.suno.com/*"],
      "js": ["content_suno.js"],
      "run_at": "document_end"
    }
  ]
}
EOF

log "✅ Extensión preparada en: $EXT_DIR"

# Instrucciones para el usuario
echo -e "\n${YELLOW}📋 INSTRUCCIONES DE INSTALACIÓN:${NC}"
echo -e "1. Abre Google Chrome"
echo -e "2. Ve a chrome://extensions/"
echo -e "3. Activa 'Modo de desarrollador' (esquina superior derecha)"
echo -e "4. Haz clic en 'Cargar extensión sin empaquetar'"
echo -e "5. Selecciona el directorio: ${BLUE}$EXT_DIR${NC}"
echo -e "6. La extensión aparecerá en tu barra de herramientas"

echo -e "\n${YELLOW}🧪 CÓMO PROBAR:${NC}"
echo -e "1. Ve a https://suno.com"
echo -e "2. Inicia sesión en tu cuenta"
echo -e "3. Ve a la página de creación"
echo -e "4. Busca el botón '🎵 Send to Son1k'"
echo -e "5. Haz clic para enviar a Son1k"

echo -e "\n${YELLOW}🔍 VERIFICAR FUNCIONAMIENTO:${NC}"
echo -e "1. Abre las herramientas de desarrollador (F12)"
echo -e "2. Ve a la pestaña 'Console'"
echo -e "3. Busca mensajes que empiecen con '🎵'"
echo -e "4. Si hay errores, compártelos"

echo -e "\n${GREEN}✅ ¡Extensión lista para instalar!${NC}"
echo -e "Directorio: ${BLUE}$EXT_DIR${NC}"

# Mantener el directorio temporal
echo -e "\n${YELLOW}💡 NOTA: El directorio temporal se mantendrá hasta que lo elimines manualmente${NC}"

