#!/bin/bash
# Script para ejecutar EN EL SERVIDOR CLOUD

echo "🚀 Iniciando deployment rápido de Son1k..."

# Extract deployment package
tar -xzf son1k_cloud_deploy.tar.gz
chmod +x server_setup.sh

# Setup server
./server_setup.sh

# Copy files to production location
cp docker-compose.cloud.yml /opt/son1k/docker-compose.yml
cp .env.production /opt/son1k/.env
cp nginx.cloud.conf /etc/nginx/sites-available/son1k

# Enable nginx site
ln -sf /etc/nginx/sites-available/son1k /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Start services
cd /opt/son1k
docker-compose up -d

echo "✅ Deployment completado!"
echo "📋 Próximos pasos:"
echo "   1. Configurar DNS en IONOS (ver ionos_dns_setup.md)"
echo "   2. Ejecutar: certbot --nginx -d son1kvers3.com -d api.son1kvers3.com"
echo "   3. Verificar: https://son1kvers3.com"
