#!/bin/bash

echo "🚀 Iniciando Resistance Social Network Backend..."
echo "📍 Puerto: 8003"
echo "🔗 URL: http://localhost:8003"
echo ""

# Check if virtual environment exists
if [ ! -d "venv_resistance" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv_resistance
fi

# Activate virtual environment
echo "🔧 Activando entorno virtual..."
source venv_resistance/bin/activate

# Install dependencies
echo "📥 Instalando dependencias..."
pip install fastapi uvicorn sqlite3

# Start the server
echo "🎯 Iniciando servidor de resistencia..."
echo "💀 Santuario - Red Social de la Resistencia"
echo "⚡ Solo para miembros Pro y Premium"
echo ""

python resistance_social_backend.py

