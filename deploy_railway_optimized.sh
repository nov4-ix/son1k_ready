#!/bin/bash

echo "🚀 SON1KVERS3 - DEPLOY OPTIMIZADO A RAILWAY"
echo "============================================="

# Verificar archivos necesarios
echo "📋 Verificando archivos de deployment..."

required_files=("main.py" "requirements.txt" "Procfile" "railway.json" "railway.toml")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ $file no encontrado"
        exit 1
    fi
done

echo "✅ Todos los archivos de deployment presentes"

# Verificar estructura del frontend
if [ ! -d "frontend" ]; then
    echo "❌ Directorio frontend no encontrado"
    exit 1
fi

echo "✅ Estructura del proyecto verificada"

# Inicializar git si no existe
if [ ! -d ".git" ]; then
    echo "🔧 Inicializando repositorio Git..."
    git init
    git branch -m main
fi

# Crear .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
env.bak/
venv.bak/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
temp/

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local
.env.production

# Build outputs
dist/
build/
frontend/dist/

# Railway
.railway/
EOF
fi

echo "📦 Preparando archivos para deploy..."

# Agregar archivos principales
git add main.py
git add requirements.txt
git add Procfile
git add railway.json
git add railway.toml
git add package.json
git add suno_wrapper_server.js
git add .gitignore

# Agregar frontend
git add frontend/

# Verificar que el servidor funciona localmente
echo "🧪 Verificando que el servidor funciona..."
timeout 10s python3 main.py &
SERVER_PID=$!
sleep 3

# Test básico
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Servidor funcionando correctamente"
else
    echo "⚠️  Advertencia: No se pudo verificar el servidor localmente"
fi

# Matar proceso de test
kill $SERVER_PID 2>/dev/null

# Commit para deploy
echo "💾 Creando commit para deployment..."
git add .
git commit -m "🚀 SON1KVERS3 DEPLOY: Sistema híbrido con frontend inmersivo

✅ FUNCIONALIDADES INCLUIDAS:
- Servidor híbrido Python + Node.js
- Frontend React inmersivo con historia cyberpunk
- Tailwind CSS + Framer Motion
- Matrix Rain background
- 5 vistas: Onboarding, Terminal, Misiones, Studio, Archivo
- Sistema de generación musical integrado
- Configuración optimizada para Railway

🎵 Generated with Son1kVers3 - La Resistencia Digital"

echo ""
echo "🎯 PRÓXIMOS PASOS PARA RAILWAY:"
echo "1. Conectar repositorio a Railway"
echo "2. Configurar variables de entorno:"
echo "   - SUNO_COOKIE (opcional)"
echo "   - SUNO_COOKIE_2 (opcional)"
echo "   - SUNO_COOKIE_3 (opcional)"
echo "3. Deploy automático se ejecutará"
echo ""
echo "📋 COMANDOS DE RAILWAY:"
echo "railway login"
echo "railway init"
echo "railway up"
echo ""
echo "🌐 DESPUÉS DEL DEPLOY:"
echo "- Verificar /health endpoint"
echo "- Probar frontend inmersivo"
echo "- Configurar dominio personalizado"
echo ""
echo "✅ LISTO PARA DEPLOYMENT A RAILWAY!"

