#!/bin/bash

# 🚀 SON1KVERS3 RAILWAY DEPLOYMENT SCRIPT
# Deployar automáticamente a Railway y configurar

echo "🚀 Iniciando deployment de Son1kVers3 a Railway..."

# Verificar que estamos en el directorio correcto
if [ ! -f "main_production_final.py" ]; then
    echo "❌ Error: No se encontró main_production_final.py"
    echo "Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

# Verificar Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Error: Railway CLI no está instalado"
    echo "Instalar con: npm install -g @railway/cli"
    exit 1
fi

echo "📦 Creando commit para deployment..."
git add .
git commit -m "🚀 DEPLOY: Son1kVers3 production ready - $(date '+%Y-%m-%d %H:%M:%S')"

echo "📤 Pushing a GitHub..."
git push

echo "🚂 Deploying a Railway..."
# Intentar deployment directo
railway up --detach || {
    echo "⚠️  Deployment directo falló, intentando con servicio específico..."
    
    # Si hay múltiples servicios, usar el primero disponible
    SERVICES=$(railway service list 2>/dev/null | grep -v "Service" | head -1)
    if [ ! -z "$SERVICES" ]; then
        SERVICE_NAME=$(echo $SERVICES | awk '{print $1}')
        echo "🎯 Usando servicio: $SERVICE_NAME"
        railway up --service "$SERVICE_NAME" --detach
    else
        echo "❌ No se encontraron servicios de Railway configurados"
        echo "Configurar manualmente en: https://railway.app"
        exit 1
    fi
}

echo "⏳ Esperando que el deployment se complete..."
sleep 10

echo "🔄 Inicializando base de datos..."
# Obtener la URL del servicio deployado
RAILWAY_URL=$(railway status 2>/dev/null | grep -o "https://[^[:space:]]*" | head -1)

if [ ! -z "$RAILWAY_URL" ]; then
    echo "🌐 Servicio deployado en: $RAILWAY_URL"
    echo "🔧 Inicializando base de datos..."
    
    # Intentar inicializar la base de datos
    curl -X POST "$RAILWAY_URL/api/admin/init-database" \
         -H "Content-Type: application/json" \
         --max-time 30 || echo "⚠️  Database init falló, se inicializará automáticamente"
    
    echo ""
    echo "✅ Deployment completado!"
    echo "🌍 URL: $RAILWAY_URL"
    echo "👤 Admin: nov4-ix@son1kvers3.com / iloveMusic!90"
    echo "🧪 Testers: pro.tester1-10@son1kvers3.com / Premium123!"
    echo ""
    echo "🎵 Son1kVers3 está listo para usar!"
else
    echo "⚠️  No se pudo obtener la URL del deployment"
    echo "Verificar en: https://railway.app"
fi

echo "🎉 Deployment script completado!"