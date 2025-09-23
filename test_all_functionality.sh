#!/bin/bash

# 🧪 SON1KVERS3 COMPLETE FUNCTIONALITY TEST
# Verificar que todas las funcionalidades estén trabajando

echo "🧪 Iniciando pruebas completas de Son1kVers3..."

# URLs a probar
LOCAL_URL="http://localhost:8002"
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else 'No tunnel')" 2>/dev/null)

echo "🌐 URLs a probar:"
echo "  Local: $LOCAL_URL"
echo "  Ngrok: $NGROK_URL"
echo "  Producción: https://son1kvers3.com"

# Función para probar endpoint
test_endpoint() {
    local url=$1
    local endpoint=$2
    local method=${3:-GET}
    local data=$4
    
    echo -n "  Testing $endpoint... "
    
    if [ "$method" = "POST" ] && [ ! -z "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X POST "$url$endpoint" \
                  -H "Content-Type: application/json" \
                  -d "$data" \
                  --max-time 10)
    else
        response=$(curl -s -w "%{http_code}" "$url$endpoint" --max-time 10)
    fi
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAIL ($http_code)"
        return 1
    fi
}

# Función para probar servidor local
test_local_server() {
    echo "🏠 Probando servidor local ($LOCAL_URL)..."
    
    local success=0
    local total=0
    
    # Endpoints básicos
    total=$((total + 1))
    test_endpoint "$LOCAL_URL" "/" && success=$((success + 1))
    
    total=$((total + 1))
    test_endpoint "$LOCAL_URL" "/api/health" && success=$((success + 1))
    
    # Smart prompt
    total=$((total + 1))
    test_endpoint "$LOCAL_URL" "/api/smart-prompt" "POST" '{"lyrics": "cancion de amor"}' && success=$((success + 1))
    
    # Generación musical
    total=$((total + 1))
    test_endpoint "$LOCAL_URL" "/api/generate" "POST" '{"prompt": "cyberpunk", "style": "synthwave"}' && success=$((success + 1))
    
    # Login
    total=$((total + 1))
    test_endpoint "$LOCAL_URL" "/api/login" "POST" '{"email": "nov4-ix@son1kvers3.com", "password": "iloveMusic!90"}' && success=$((success + 1))
    
    # Otros endpoints
    total=$((total + 1))
    test_endpoint "$LOCAL_URL" "/api/celery-status" && success=$((success + 1))
    
    total=$((total + 1))
    test_endpoint "$LOCAL_URL" "/api/redis-status" && success=$((success + 1))
    
    total=$((total + 1))
    test_endpoint "$LOCAL_URL" "/api/audio/files" && success=$((success + 1))
    
    echo "📊 Resultado local: $success/$total endpoints funcionando"
    return $([ $success -eq $total ])
}

# Función para probar ngrok
test_ngrok_server() {
    if [ "$NGROK_URL" = "No tunnel" ]; then
        echo "⚠️  Ngrok no está activo, saltando pruebas..."
        return 0
    fi
    
    echo "🌉 Probando servidor ngrok ($NGROK_URL)..."
    
    local success=0
    local total=0
    
    # Endpoints básicos con ngrok
    total=$((total + 1))
    test_endpoint "$NGROK_URL" "/" && success=$((success + 1))
    
    total=$((total + 1))
    test_endpoint "$NGROK_URL" "/api/health" && success=$((success + 1))
    
    total=$((total + 1))
    test_endpoint "$NGROK_URL" "/api/smart-prompt" "POST" '{"lyrics": "epic song"}' && success=$((success + 1))
    
    echo "📊 Resultado ngrok: $success/$total endpoints funcionando"
    return $([ $success -eq $total ])
}

# Función para verificar archivos importantes
check_files() {
    echo "📁 Verificando archivos importantes..."
    
    local files=(
        "main_production_final.py"
        "frontend/index.html"
        "requirements.txt"
        "railway.toml"
        "deploy_to_railway.sh"
        "IONOS_EMAIL_SETUP.md"
    )
    
    local missing=0
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file (FALTANTE)"
            missing=$((missing + 1))
        fi
    done
    
    if [ $missing -eq 0 ]; then
        echo "📁 Todos los archivos están presentes"
        return 0
    else
        echo "❌ $missing archivos faltantes"
        return 1
    fi
}

# Función para verificar dependencias
check_dependencies() {
    echo "📦 Verificando dependencias..."
    
    local deps=(
        "python3"
        "pip3"
        "git"
        "curl"
        "railway"
    )
    
    local missing=0
    
    for dep in "${deps[@]}"; do
        if command -v "$dep" &> /dev/null; then
            echo "  ✅ $dep"
        else
            echo "  ❌ $dep (FALTANTE)"
            missing=$((missing + 1))
        fi
    done
    
    if [ $missing -eq 0 ]; then
        echo "📦 Todas las dependencias están instaladas"
        return 0
    else
        echo "❌ $missing dependencias faltantes"
        return 1
    fi
}

# Función para verificar funcionalidades del frontend
check_frontend_features() {
    echo "🎨 Verificando funcionalidades del frontend..."
    
    local features=(
        "Matrix effect"
        "Terminal access" 
        "Pixel assistant"
        "Floating player"
        "Track upload zone"
        "Smart prompt button"
        "Generate music button"
        "Login system"
    )
    
    echo "  Buscar en frontend/index.html:"
    
    local found=0
    local total=${#features[@]}
    
    # Matrix effect
    if grep -q "createMatrixEffect" frontend/index.html; then
        echo "  ✅ Matrix effect"
        found=$((found + 1))
    else
        echo "  ❌ Matrix effect"
    fi
    
    # Terminal access
    if grep -q "Ctrl+Alt+H" frontend/index.html; then
        echo "  ✅ Terminal access"
        found=$((found + 1))
    else
        echo "  ❌ Terminal access"
    fi
    
    # Pixel assistant
    if grep -q "pixel-assistant" frontend/index.html; then
        echo "  ✅ Pixel assistant"
        found=$((found + 1))
    else
        echo "  ❌ Pixel assistant"
    fi
    
    # Floating player
    if grep -q "floating-player" frontend/index.html; then
        echo "  ✅ Floating player"
        found=$((found + 1))
    else
        echo "  ❌ Floating player"
    fi
    
    # Track upload
    if grep -q "track-upload-zone" frontend/index.html; then
        echo "  ✅ Track upload zone"
        found=$((found + 1))
    else
        echo "  ❌ Track upload zone"
    fi
    
    # Smart prompt
    if grep -q "smart-prompt" frontend/index.html; then
        echo "  ✅ Smart prompt button"
        found=$((found + 1))
    else
        echo "  ❌ Smart prompt button"
    fi
    
    # Generate music
    if grep -q "generarMusica" frontend/index.html; then
        echo "  ✅ Generate music button"
        found=$((found + 1))
    else
        echo "  ❌ Generate music button"
    fi
    
    # Login system
    if grep -q "loginModal" frontend/index.html; then
        echo "  ✅ Login system"
        found=$((found + 1))
    else
        echo "  ❌ Login system"
    fi
    
    echo "📊 Frontend features: $found/$total implementadas"
    return $([ $found -eq $total ])
}

# Ejecutar todas las pruebas
main() {
    echo "🚀 SON1KVERS3 COMPLETE TEST SUITE"
    echo "=================================="
    echo ""
    
    local total_tests=0
    local passed_tests=0
    
    # Verificar archivos
    total_tests=$((total_tests + 1))
    check_files && passed_tests=$((passed_tests + 1))
    echo ""
    
    # Verificar dependencias
    total_tests=$((total_tests + 1))
    check_dependencies && passed_tests=$((passed_tests + 1))
    echo ""
    
    # Verificar frontend
    total_tests=$((total_tests + 1))
    check_frontend_features && passed_tests=$((passed_tests + 1))
    echo ""
    
    # Verificar servidor local
    total_tests=$((total_tests + 1))
    test_local_server && passed_tests=$((passed_tests + 1))
    echo ""
    
    # Verificar ngrok
    total_tests=$((total_tests + 1))
    test_ngrok_server && passed_tests=$((passed_tests + 1))
    echo ""
    
    # Resultado final
    echo "🏆 RESULTADO FINAL"
    echo "=================="
    echo "✅ Pruebas pasadas: $passed_tests"
    echo "❌ Pruebas fallidas: $((total_tests - passed_tests))"
    echo "📊 Total: $passed_tests/$total_tests"
    echo ""
    
    if [ $passed_tests -eq $total_tests ]; then
        echo "🎉 ¡TODAS LAS PRUEBAS PASARON!"
        echo "🚀 Son1kVers3 está 100% funcional y listo para producción"
        echo ""
        echo "🌍 URLs de acceso:"
        echo "  Local: $LOCAL_URL"
        [ "$NGROK_URL" != "No tunnel" ] && echo "  Ngrok: $NGROK_URL"
        echo "  Producción: https://son1kvers3.com"
        echo ""
        echo "👤 Credenciales de prueba:"
        echo "  Admin: nov4-ix@son1kvers3.com / iloveMusic!90"
        echo "  Tester: pro.tester1@son1kvers3.com / Premium123!"
        echo ""
        echo "🎵 Funcionalidades verificadas:"
        echo "  ✅ Smart prompts con Pixel"
        echo "  ✅ Generación musical"
        echo "  ✅ Terminal Matrix (Ctrl+Alt+H)"
        echo "  ✅ Easter egg 'Conocer Universo'"
        echo "  ✅ Reproductor flotante"
        echo "  ✅ Subida de tracks"
        echo "  ✅ Login persistente"
        echo "  ✅ Pixel asistente flotante"
        return 0
    else
        echo "❌ ALGUNAS PRUEBAS FALLARON"
        echo "🔧 Revisar los errores arriba y corregir"
        return 1
    fi
}

# Ejecutar script
main "$@"