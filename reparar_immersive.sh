#!/bin/bash
# Script de reparación del modo inmersivo

echo "🎵 Reparando modo inmersivo de Son1kVers3..."

# Verificar que estamos en el directorio correcto
if [ ! -f "frontend/index.html" ]; then
    echo "❌ Error: No se encuentra frontend/index.html"
    echo "   Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Crear directorio frontend si no existe
mkdir -p frontend

# Verificar archivos
echo "🔍 Verificando archivos..."

if [ ! -f "frontend/immersive_interface.html" ]; then
    echo "❌ Faltante: immersive_interface.html"
    echo "   Este archivo debe ser creado manualmente"
fi

if [ ! -f "frontend/immersive_integration.js" ]; then
    echo "❌ Faltante: immersive_integration.js"
    echo "   Este archivo debe ser creado manualmente"
fi

# Verificar que el HTML tenga las funciones necesarias
if ! grep -q "toggleImmersiveInterface" frontend/index.html; then
    echo "❌ Faltante: función toggleImmersiveInterface en index.html"
fi

if ! grep -q "immersiveInterfaceContainer" frontend/index.html; then
    echo "❌ Faltante: contenedor immersiveInterfaceContainer en index.html"
fi

echo "✅ Verificación completada"
echo ""
echo "💡 Si hay archivos faltantes, ejecuta:"
echo "   python3 diagnostico_immersive.py --fix"
