#!/bin/bash

echo "🔍 VERIFICACIÓN FINAL RÁPIDA DEL SISTEMA"
echo "======================================="

# Asegurar que el endpoint correcto esté respondiendo
echo "1. 📡 VERIFICANDO ENDPOINTS DISPONIBLES"
echo ""

# Mostrar rutas de API
echo "🌐 Rutas de API disponibles:"
curl -s "http://localhost:8000/openapi.json" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for path in sorted(data.get('paths', {}).keys()):
        if 'music' in path or 'generate' in path:
            print(f'   {path}')
except:
    print('   Error obteniendo rutas')
" 2>/dev/null

echo ""
echo "2. 🧪 PROBANDO ENDPOINT TRANSPARENTE"
echo ""

# Test del endpoint correcto
echo "📤 Enviando request al endpoint transparente..."

RESPONSE=$(curl -s -X POST "http://localhost:8000/api/music/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": "Walking down the street tonight\nFeeling free and feeling right", 
    "prompt": "upbeat electronic, 120 BPM",
    "instrumental": false,
    "style": "default"
  }' --max-time 10)

echo "📥 Respuesta recibida:"
echo "$RESPONSE" | head -3

# Verificar Job ID
if echo "$RESPONSE" | grep -q "son1k_job_"; then
    echo "✅ Job ID TRANSPARENTE detectado (son1k_job_*)"
    JOB_ID_OK=true
else
    echo "❌ Job ID NO es transparente"
    JOB_ID_OK=false
fi

# Verificar ausencia de 'suno'
if echo "$RESPONSE" | grep -qi "suno"; then
    echo "❌ Response contiene 'suno'"
    SUNO_FREE=false
else
    echo "✅ Response libre de 'suno'"
    SUNO_FREE=true
fi

echo ""
echo "3. 📄 VERIFICANDO FRONTEND INTERCEPTOR"
echo ""

# Verificar que el script esté en el frontend
if grep -q "SOLUCIÓN GARANTIZADA: Transparencia Total" frontend/index.html; then
    echo "✅ Script interceptor presente en frontend"
    FRONTEND_OK=true
else
    echo "❌ Script interceptor NO encontrado"
    FRONTEND_OK=false
fi

echo ""
echo "4. 📊 RESUMEN FINAL"
echo "=================="

echo "🔍 COMPONENTES VERIFICADOS:"

if [ "$JOB_ID_OK" = true ]; then
    echo "✅ Job IDs Transparentes: FUNCIONANDO"
else
    echo "❌ Job IDs Transparentes: FALLANDO"
fi

if [ "$SUNO_FREE" = true ]; then
    echo "✅ Sin Referencias 'Suno': FUNCIONANDO" 
else
    echo "❌ Sin Referencias 'Suno': FALLANDO"
fi

if [ "$FRONTEND_OK" = true ]; then
    echo "✅ Frontend Interceptor: FUNCIONANDO"
else
    echo "❌ Frontend Interceptor: FALLANDO"
fi

# Evaluación final
WORKING_COMPONENTS=0
if [ "$JOB_ID_OK" = true ]; then ((WORKING_COMPONENTS++)); fi
if [ "$SUNO_FREE" = true ]; then ((WORKING_COMPONENTS++)); fi
if [ "$FRONTEND_OK" = true ]; then ((WORKING_COMPONENTS++)); fi

echo ""
echo "🎯 RESULTADO: $WORKING_COMPONENTS/3 componentes principales funcionando"

if [ $WORKING_COMPONENTS -eq 3 ]; then
    echo ""
    echo "🎉 ¡SISTEMA TRANSPARENTE FUNCIONANDO!"
    echo "✅ Listo para deploy público"
    echo "🌐 El siguiente paso es:"
    echo "   1. Deploy en servidor cloud"
    echo "   2. Dominio personalizado"
    echo "   3. Link público para testers"
    
elif [ $WORKING_COMPONENTS -eq 2 ]; then
    echo ""
    echo "⚠️ SISTEMA MAYORMENTE FUNCIONAL"
    echo "🔧 1 componente menor necesita atención"
    echo "✅ Se puede proceder con deploy monitoreado"
    
else
    echo ""
    echo "❌ SISTEMA NECESITA CORRECCIONES"
    echo "🔧 Múltiples componentes críticos fallando"
    echo ""
    echo "🛠️ ACCIONES SUGERIDAS:"
    
    if [ "$JOB_ID_OK" = false ]; then
        echo "   • Corregir generación de Job IDs transparentes"
    fi
    
    if [ "$SUNO_FREE" = false ]; then
        echo "   • Eliminar referencias a 'suno' en responses"
    fi
    
    if [ "$FRONTEND_OK" = false ]; then
        echo "   • Instalar script interceptor en frontend"
    fi
fi

echo ""
echo "📋 DATOS PARA REFERENCIA:"
echo "   • Frontend: http://localhost:3000"
echo "   • API Docs: http://localhost:8000/docs" 
echo "   • Endpoint: POST /api/music/generate"
echo ""
echo "🔧 Para reiniciar servicios:"
echo "   docker compose restart api worker"