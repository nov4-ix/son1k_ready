#!/bin/bash
# Setup Extension for macOS

echo "🔧 Configurando Extensión de Chrome para Son1k..."

# Verificar servidor
echo "🔍 Verificando servidor..."
if ! curl -s http://localhost:8000/api/extension/status > /dev/null; then
    echo "❌ El servidor no está funcionando. Inicia el servidor primero:"
    echo "   source .venv/bin/activate && python3 son1k_simple_stable.py"
    exit 1
fi

echo "✅ Servidor funcionando"

# Crear directorio de extensión
EXT_DIR="$HOME/Desktop/Son1kExtension"
echo "📁 Creando extensión en: $EXT_DIR"

rm -rf "$EXT_DIR"
mkdir -p "$EXT_DIR"
cp -r extension/* "$EXT_DIR/"

# Crear manifest actualizado
cat > "$EXT_DIR/manifest.json" << 'EOF'
{
  "manifest_version": 3,
  "name": "Son1k Extension",
  "version": "3.1.0",
  "description": "Son1k-Suno Bridge - Full Integration",
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

echo "✅ Extensión creada en: $EXT_DIR"

echo ""
echo "📋 INSTRUCCIONES:"
echo "1. Abre Google Chrome"
echo "2. Ve a chrome://extensions/"
echo "3. Activa 'Modo de desarrollador'"
echo "4. Haz clic en 'Cargar extensión sin empaquetar'"
echo "5. Selecciona: $EXT_DIR"
echo ""
echo "🧪 PROBAR:"
echo "1. Ve a https://suno.com"
echo "2. Busca el botón '🎵 Send to Son1k'"
echo "3. Haz clic para enviar a Son1k"
echo ""
echo "✅ ¡Listo!"

