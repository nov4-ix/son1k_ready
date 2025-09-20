#!/bin/bash

echo "🚀 Iniciando Sistema Son1k con Motor Corregido"
echo "==============================================="

# Configurar variables de entorno
export SV_SELENIUM_URL="http://localhost:4444"
export SV_HEADLESS=0
export SV_NO_QUIT=1
export SON1K_FRONTEND_PUSH=1
export NOVNC_PUBLIC_URL="https://a11795f9785f.ngrok-free.app"

echo "🔧 Variables configuradas:"
echo "   SV_SELENIUM_URL: $SV_SELENIUM_URL"
echo "   SV_HEADLESS: $SV_HEADLESS (visible para noVNC)"
echo "   SV_NO_QUIT: $SV_NO_QUIT (no cerrar en errores)"
echo "   SON1K_FRONTEND_PUSH: $SON1K_FRONTEND_PUSH"
echo "   NOVNC_PUBLIC_URL: $NOVNC_PUBLIC_URL"
echo ""

echo "🐳 1. Reiniciando contenedores Docker..."
echo "   Deteniendo contenedores existentes..."
docker compose down

echo "   Iniciando contenedores con motor corregido..."
docker compose up -d

echo "⏳ 2. Esperando que los servicios se inicialicen..."
sleep 15

echo "🧪 3. Verificando servicios..."

# Verificar API
echo "   🔍 Verificando API..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "   ✅ API funcionando en http://localhost:8000"
else
    echo "   ❌ API no responde"
fi

# Verificar Selenium
echo "   🔍 Verificando Selenium..."
if curl -s http://localhost:4444/status > /dev/null; then
    echo "   ✅ Selenium funcionando en http://localhost:4444"
else
    echo "   ❌ Selenium no responde"
fi

# Verificar noVNC
echo "   🔍 Verificando noVNC..."
if curl -s http://localhost:7900 > /dev/null; then
    echo "   ✅ noVNC funcionando en http://localhost:7900"
else
    echo "   ❌ noVNC no responde"
fi

echo ""
echo "✅ Sistema iniciado con motor corregido"
echo ""
echo "🎯 CARACTERÍSTICAS DEL MOTOR CORREGIDO:"
echo "   🚫 NO más archivos con nombre 'suno'"
echo "   ✨ Nombres dinámicos basados en la primera frase de lyrics"
echo "   🔧 Detección mejorada de elementos Custom"
echo "   🎵 Extracción robusta de tracks generados"
echo "   📁 Nombres de archivo válidos y limpios"
echo ""
echo "🖥️  ACCESO AL SISTEMA:"
echo "   API:          http://localhost:8000"
echo "   Documentación: http://localhost:8000/docs"
echo "   noVNC público: $NOVNC_PUBLIC_URL"
echo "   noVNC local:   http://localhost:7900"
echo ""
echo "🔑 PASOS SIGUIENTES:"
echo "   1. Ve a $NOVNC_PUBLIC_URL"
echo "   2. Haz login UNA VEZ en Suno (la sesión quedará guardada)"
echo "   3. Usa el frontend Son1k para generar música"
echo "   4. ¡Los archivos tendrán nombres dinámicos basados en tus lyrics!"
echo ""
echo "🧪 Para probar el sistema:"
echo "   python3 test_fixed_generation.py"
echo ""
echo "==============================================="
echo "🎵 Sistema Son1k con Motor Corregido LISTO"