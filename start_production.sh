#!/bin/bash

echo "🚀 Iniciando Son1kVers3 Production System..."

# Verificar que Node.js esté instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instala Node.js 18+"
    exit 1
fi

# Verificar versión de Node.js
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Se requiere Node.js 18+. Versión actual: $(node -v)"
    exit 1
fi

# Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Crear directorio para canciones generadas
mkdir -p generated_songs

# Iniciar el sistema
echo "🎵 Iniciando sistema de generación de música..."
node son1k_production_system.js


