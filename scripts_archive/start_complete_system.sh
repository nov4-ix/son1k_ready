#!/bin/bash

# 🎵 Son1k Complete System Startup
# Inicia todo el sistema Son1k-Suno integrado

echo "🚀 INICIANDO SISTEMA COMPLETO SON1K-SUNO"
echo "========================================"

# Verificar que estamos en el directorio correcto
if [[ ! -f "docker-compose.yml" ]]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# 1. Iniciar servicios backend
echo "📡 1. Iniciando servicios backend..."
docker compose up -d
sleep 5

echo "⏳ Esperando que los servicios estén listos..."
sleep 10

# 2. Verificar estado de servicios
echo "🔍 2. Verificando servicios..."
docker ps --format "table {{.Names}}\t{{.Status}}"

# 3. Probar conectividad de API
echo ""
echo "📡 3. Probando API..."
if curl -s http://localhost:8000/api/captcha/health > /dev/null; then
    echo "✅ API Backend: Funcionando"
else
    echo "⚠️  API Backend: Inicializando..."
fi

# 4. Mostrar información del sistema
echo ""
echo "🎯 SISTEMA LISTO - INFORMACIÓN IMPORTANTE:"
echo "=========================================="
echo ""
echo "🔗 URLs del Sistema:"
echo "   🌐 Frontend Son1k: http://localhost:3000"
echo "   🛠️  Backend API:    http://localhost:8000"
echo "   📚 Documentación:   http://localhost:8000/docs"
echo "   🛡️ CAPTCHA API:     http://localhost:8000/api/captcha/health"
echo ""
echo "🎵 Características Integradas:"
echo "   ✅ Frontend Son1k con diseño cyberpunk"
echo "   ✅ Sistema de CAPTCHA visual para Suno"
echo "   ✅ Monitoreo en tiempo real de generación"
echo "   ✅ Instrucciones automáticas para usuario"
echo "   ✅ Integración con reproductor existente"
echo "   ✅ Panel de progreso visual"
echo "   ✅ Notificaciones toast integradas"
echo ""
echo "🎯 Flujo de Usuario:"
echo "   1. Abre http://localhost:3000"
echo "   2. Ingresa lyrics y prompt en Son1k"
echo "   3. Haz clic en '🎵 Generar con Suno'"
echo "   4. Sigue las instrucciones automáticas"
echo "   5. Resuelve CAPTCHAs si aparecen"
echo "   6. Disfruta de tu música generada"
echo ""
echo "🚀 INICIANDO FRONTEND..."
echo "Presiona Ctrl+C para detener todo el sistema"
echo "=========================================="

# 5. Iniciar servidor frontend
python3 start_frontend.py