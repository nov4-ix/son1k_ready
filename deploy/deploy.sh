#!/bin/bash

echo "🚀 Ejecutando deploy de Son1k a producción..."

# Generar secretos
export SECRET_KEY=$(openssl rand -hex 32)
export DB_PASSWORD=$(openssl rand -hex 16)

echo "🔐 Secretos generados"
echo "🐳 Iniciando contenedores de producción..."

# Deploy con docker-compose
docker-compose -f docker-compose.production.yml up -d --build

echo "⏳ Esperando que los servicios se inicialicen..."
sleep 30

echo "🧪 Verificando deployment..."

# Verificar servicios
if curl -f http://localhost:8000/health; then
    echo "✅ API funcionando"
else
    echo "❌ API no responde"
fi

echo "🎉 Deploy completado!"
echo "📋 URLs de acceso:"
echo "   Frontend: https://son1kvers3.com"
echo "   API: https://api.son1kvers3.com"
echo "   Docs: https://api.son1kvers3.com/docs"
