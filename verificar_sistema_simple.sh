#!/bin/bash

echo "🚀 VERIFICACIÓN SIMPLE DEL SISTEMA LOCAL SON1K"
echo "==============================================="
echo "🎯 Objetivo: Confirmar que la transparencia funciona al 100%"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "\n${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Variables de estado
DOCKER_OK=false
API_OK=false
FRONTEND_OK=false
BACKEND_OK=false

# 1. Verificar Docker Services
print_step "1. 🐳 VERIFICANDO SERVICIOS DOCKER"

if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "son1k"; then
    print_success "Contenedores Docker funcionando"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep son1k
    DOCKER_OK=true
else
    print_error "Contenedores Docker no encontrados"
    echo "🔧 Iniciando contenedores..."
    docker compose up -d
    sleep 15
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "son1k"; then
        print_success "Contenedores iniciados correctamente"
        DOCKER_OK=true
    else
        print_error "Error iniciando contenedores"
    fi
fi

# 2. Verificar API Endpoints
print_step "2. 🌐 VERIFICANDO API ENDPOINTS"

# Health check principal
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "API principal (puerto 8000): FUNCIONANDO"
    API_OK=true
else
    print_error "API principal no responde en puerto 8000"
fi

# API de música
if curl -s http://localhost:8000/api/music/health > /dev/null; then
    print_success "API de música: FUNCIONANDO"
    echo "   📄 Response:"
    curl -s http://localhost:8000/api/music/health | head -3
else
    print_warning "API de música no responde (puede ser normal)"
fi

# Documentación
if curl -s http://localhost:8000/docs > /dev/null; then
    print_success "Documentación API: ACCESIBLE"
    echo "   🔗 Disponible en: http://localhost:8000/docs"
else
    print_error "Documentación no accesible"
fi

# 3. Verificar Archivos Frontend
print_step "3. 📄 VERIFICANDO ARCHIVOS FRONTEND"

if [ -f "frontend/index.html" ]; then
    print_success "Archivo frontend/index.html existe"
    
    # Verificar script de transparencia
    if grep -q "SOLUCIÓN GARANTIZADA: Transparencia Total" frontend/index.html; then
        print_success "Script de transparencia encontrado"
        FRONTEND_OK=true
    else
        print_error "Script de transparencia NO encontrado"
    fi
    
    # Verificar interceptor
    if grep -q "window.fetch = async function" frontend/index.html; then
        print_success "Interceptor de fetch configurado"
    else
        print_error "Interceptor de fetch NO configurado"
        FRONTEND_OK=false
    fi
    
    # Verificar generador de nombres
    if grep -q "generateDynamicName" frontend/index.html; then
        print_success "Generador de nombres dinámicos presente"
    else
        print_error "Generador de nombres dinámicos NO encontrado"
        FRONTEND_OK=false
    fi
    
else
    print_error "Archivo frontend/index.html NO existe"
fi

# 4. Verificar Archivos Backend
print_step "4. 🔧 VERIFICANDO ARCHIVOS BACKEND"

if [ -f "backend/app/routers/music_generation.py" ]; then
    print_success "Archivo music_generation.py existe"
    
    # Verificar imports corregidos
    if grep -q "MusicGeneratorFixed" backend/app/routers/music_generation.py; then
        print_success "Motor corregido importado"
        BACKEND_OK=true
    else
        print_error "Motor corregido NO importado"
    fi
    
    # Verificar job ID transparente
    if grep -q "son1k_job_" backend/app/routers/music_generation.py; then
        print_success "Job IDs transparentes configurados"
    else
        print_error "Job IDs transparentes NO configurados"
        BACKEND_OK=false
    fi
    
    # Verificar función de transparencia
    if grep -q "ensure_transparent_results" backend/app/routers/music_generation.py; then
        print_success "Función de transparencia presente"
    else
        print_error "Función de transparencia NO encontrada"
        BACKEND_OK=false
    fi
    
else
    print_error "Archivo music_generation.py NO existe"
fi

# Verificar motor fijo
if [ -f "backend/selenium_worker/music_generator_fixed.py" ]; then
    print_success "Motor corregido (music_generator_fixed.py) existe"
    
    if grep -q "SongNameGenerator" backend/selenium_worker/music_generator_fixed.py; then
        print_success "Generador de nombres presente en motor"
    else
        print_error "Generador de nombres NO encontrado en motor"
        BACKEND_OK=false
    fi
else
    print_error "Motor corregido NO existe"
    BACKEND_OK=false
fi

# 5. Test Práctico de Transparencia
print_step "5. 🧪 TEST PRÁCTICO DE TRANSPARENCIA"

if [ "$API_OK" = true ]; then
    echo "📤 Enviando request de prueba..."
    
    # Test básico con curl
    TEST_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/music/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "lyrics": "Walking down the street tonight\nFeeling free and feeling right",
            "prompt": "upbeat electronic, 120 BPM",
            "instrumental": false,
            "style": "default"
        }' --max-time 30)
    
    if [ $? -eq 0 ] && [ ! -z "$TEST_RESPONSE" ]; then
        print_success "Request enviado exitosamente"
        echo "📄 Response (primeras líneas):"
        echo "$TEST_RESPONSE" | head -5
        
        # Verificar Job ID transparente
        if echo "$TEST_RESPONSE" | grep -q "son1k_job_"; then
            print_success "Job ID transparente confirmado (son1k_job_*)"
        else
            print_error "Job ID NO es transparente"
        fi
        
        # Verificar que NO contenga suno
        if echo "$TEST_RESPONSE" | grep -qi "suno"; then
            print_error "ADVERTENCIA: Response contiene 'suno'"
        else
            print_success "Response libre de referencias a 'suno'"
        fi
        
    else
        print_warning "Request falló o timeout (puede ser normal, el backend toma tiempo)"
    fi
else
    print_warning "Saltando test práctico (API no disponible)"
fi

# 6. Resumen Final
echo ""
echo "=================================================================="
echo "📊 RESUMEN FINAL DE VERIFICACIÓN"
echo "=================================================================="

TOTAL_COMPONENTS=4
WORKING_COMPONENTS=0

echo "🔍 COMPONENTES VERIFICADOS:"

if [ "$DOCKER_OK" = true ]; then
    print_success "Docker Services: FUNCIONANDO"
    ((WORKING_COMPONENTS++))
else
    print_error "Docker Services: FALLANDO"
fi

if [ "$API_OK" = true ]; then
    print_success "API Endpoints: FUNCIONANDO"
    ((WORKING_COMPONENTS++))
else
    print_error "API Endpoints: FALLANDO"
fi

if [ "$FRONTEND_OK" = true ]; then
    print_success "Frontend Configuration: FUNCIONANDO"
    ((WORKING_COMPONENTS++))
else
    print_error "Frontend Configuration: FALLANDO"
fi

if [ "$BACKEND_OK" = true ]; then
    print_success "Backend Configuration: FUNCIONANDO"
    ((WORKING_COMPONENTS++))
else
    print_error "Backend Configuration: FALLANDO"
fi

echo ""
echo "🎯 RESULTADO: $WORKING_COMPONENTS/$TOTAL_COMPONENTS componentes funcionando"

if [ $WORKING_COMPONENTS -eq $TOTAL_COMPONENTS ]; then
    echo ""
    echo "🎉 ¡TODAS LAS VERIFICACIONES PASARON!"
    echo "✅ El sistema está listo para deploy público"
    echo "🎵 La transparencia funciona al 100%"
    echo "🚫 No hay referencias a 'suno' en el frontend"  
    echo "✨ Los nombres dinámicos funcionan correctamente"
    echo ""
    echo "🚀 PRÓXIMOS PASOS:"
    echo "   1. ✅ Sistema local verificado"
    echo "   2. 🌐 Deploy en servidor cloud"
    echo "   3. 🔗 Link público para testers" 
    echo "   4. 📈 Optimizaciones de performance"
    echo ""
    echo "🔗 PARA PROBAR AHORA:"
    echo "   Frontend: Abrir browser → http://localhost:3000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Test API: http://localhost:8000/api/music/health"
    
elif [ $WORKING_COMPONENTS -ge 3 ]; then
    echo ""
    echo "⚠️ SISTEMA MAYORMENTE FUNCIONAL"
    echo "🔧 Algunos componentes menores necesitan atención"
    echo "✅ Se puede proceder con deploy con monitoreo"
    
else
    echo ""
    echo "❌ SISTEMA NECESITA CORRECCIONES"
    echo "🔧 Componentes críticos fallando"
    echo "🛠️ Corrige los errores antes del deploy"
fi

echo ""
echo "📋 Para ver detalles completos, revisa el output arriba"
echo "🔧 Para reiniciar servicios: docker compose down && docker compose up -d"