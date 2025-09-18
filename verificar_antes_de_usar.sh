#!/bin/bash
# Script de verificación completa antes de usar Son1k ↔ Suno Bridge

echo "🔍 VERIFICANDO SON1K ↔ SUNO BRIDGE..."
echo "================================================="

PROJECT_DIR="/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
cd "$PROJECT_DIR"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success_count=0
total_checks=7

function check_success() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

function check_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo ""
echo "1️⃣ Verificando archivos del proyecto..."
if [ -f "backend/app/main.py" ] && [ -f "extension/manifest.json" ] && [ -f "run_local.py" ]; then
    check_success 0 "Archivos del proyecto presentes"
else
    check_success 1 "Archivos del proyecto faltantes"
fi

echo ""
echo "2️⃣ Verificando Redis..."
if redis-cli ping > /dev/null 2>&1; then
    check_success 0 "Redis está corriendo"
else
    check_success 1 "Redis no está corriendo"
    echo "   💡 Ejecutar: brew services start redis"
fi

echo ""
echo "3️⃣ Verificando entorno virtual Python..."
if [ -d "son1k_env" ]; then
    check_success 0 "Entorno virtual existe"
else
    check_success 1 "Entorno virtual no existe"
    echo "   💡 Ejecutar: python3 -m venv son1k_env"
fi

echo ""
echo "4️⃣ Verificando dependencias Python..."
if [ -f "son1k_env/bin/activate" ]; then
    source son1k_env/bin/activate
    if python3 -c "import fastapi, celery, redis" > /dev/null 2>&1; then
        check_success 0 "Dependencias Python instaladas"
    else
        check_success 1 "Dependencias Python faltantes"
        echo "   💡 Ejecutar: pip install -r backend/requirements.txt"
    fi
    deactivate
else
    check_success 1 "No se puede activar entorno virtual"
fi

echo ""
echo "5️⃣ Verificando archivos de extensión..."
if node extension/validate_extension.js > /dev/null 2>&1; then
    check_success 0 "Extensión válida y sin errores"
else
    check_success 1 "Extensión tiene errores"
fi

echo ""
echo "6️⃣ Verificando backend (si está corriendo)..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    response=$(curl -s http://localhost:8000/api/health)
    if [[ "$response" == *"\"ok\":true"* ]]; then
        check_success 0 "Backend respondiendo correctamente"
    else
        check_success 1 "Backend responde pero con error"
    fi
else
    check_warning "Backend no está corriendo (normal si no lo has iniciado)"
    echo "   💡 Para iniciar: python3 run_local.py"
    # No contamos esto como fallo ya que es normal
    ((success_count++))
fi

echo ""
echo "7️⃣ Verificando sintaxis de archivos críticos..."
if python3 -m py_compile backend/app/main.py > /dev/null 2>&1; then
    check_success 0 "Sintaxis Python correcta"
else
    check_success 1 "Errores de sintaxis en Python"
fi

echo ""
echo "================================================="
echo "📊 RESULTADO: $success_count/$total_checks verificaciones exitosas"

if [ $success_count -eq $total_checks ]; then
    echo -e "${GREEN}🎉 TODO PERFECTO - LISTO PARA USAR${NC}"
    echo ""
    echo "🚀 PRÓXIMOS PASOS:"
    echo "1. Ejecutar: python3 run_local.py"
    echo "2. Cargar extensión en Chrome desde: $PROJECT_DIR/extension"
    echo "3. Configurar URL 'localhost:8000' en popup de extensión"
    echo "4. Ir a https://suno.com/create y usar botón 'Send to Son1k'"
    exit 0
else
    echo -e "${RED}❌ HAY PROBLEMAS QUE RESOLVER${NC}"
    echo ""
    echo "📋 SOLUCIONAS SUGERIDAS:"
    
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "• Iniciar Redis: brew services start redis"
    fi
    
    if [ ! -d "son1k_env" ]; then
        echo "• Crear entorno virtual: python3 -m venv son1k_env"
    fi
    
    if [ -d "son1k_env" ]; then
        source son1k_env/bin/activate
        if ! python3 -c "import fastapi, celery, redis" > /dev/null 2>&1; then
            echo "• Instalar dependencias: source son1k_env/bin/activate && pip install -r backend/requirements.txt"
        fi
        deactivate
    fi
    
    echo ""
    echo "Ejecuta este script nuevamente después de las correcciones."
    exit 1
fi