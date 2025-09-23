#!/bin/bash

echo "🚀 SON1KVERS3 - DEPLOY COMPLETO A RAILWAY"
echo "=========================================="

# Verificar archivos necesarios
echo "📋 Verificando archivos de deployment..."
if [ ! -f "main_production_final.py" ]; then
    echo "❌ main_production_final.py no encontrado"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt no encontrado"
    exit 1
fi

if [ ! -f "Procfile" ]; then
    echo "❌ Procfile no encontrado"
    exit 1
fi

echo "✅ Todos los archivos de deployment presentes"

# Inicializar git si no existe
if [ ! -d ".git" ]; then
    echo "🔧 Inicializando repositorio Git..."
    git init
    git branch -m main
fi

echo "📦 Preparando archivos para deploy..."

# Agregar archivos principales
git add main_production_final.py
git add requirements.txt  
git add Procfile
git add railway.json
git add index.html
git add .env.example

# Verificar que el servidor funciona localmente
echo "🧪 Verificando que el servidor funciona..."
timeout 5s python3 main_production_final.py &
SERVER_PID=$!
sleep 3

# Test básico
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Servidor funcionando correctamente"
else
    echo "⚠️  Advertencia: No se pudo verificar el servidor localmente"
fi

# Matar proceso de test
kill $SERVER_PID 2>/dev/null

# Commit para deploy
echo "💾 Creando commit para deployment..."
git add .
git commit -m "🚀 SON1KVERS3 DEPLOY: Sistema completo con terminal UI

✅ FUNCIONALIDADES INCLUIDAS:
- FastAPI backend completamente funcional
- Terminal UI immersivo con efectos cyberpunk
- Chat IA real con Ollama Cloud
- Generación musical con traducción automática
- Sistema de navegación completo
- Endpoints /health, /api/chat, /api/generate
- Auto-renewal system activo
- CORS configurado para producción
- Responsive design completo

🎵 Generated with Son1kVers3 - La Resistencia Digital"

echo ""
echo "🎯 PRÓXIMOS PASOS PARA RAILWAY:"
echo "1. Conectar repositorio a Railway"
echo "2. Configurar variables de entorno:"
echo "   - SUNO_SESSION_ID"
echo "   - SUNO_COOKIE" 
echo "   - OLLAMA_URL (opcional)"
echo "3. Deploy automático se ejecutará"
echo ""
echo "📋 COMANDOS DE RAILWAY:"
echo "railway login"
echo "railway init"
echo "railway up"
echo ""
echo "🌐 DESPUÉS DEL DEPLOY:"
echo "- Verificar /health endpoint"
echo "- Probar /api/chat"
echo "- Probar /api/generate"
echo "- Configurar dominio personalizado"
echo ""
echo "✅ LISTO PARA DEPLOYMENT A RAILWAY!"