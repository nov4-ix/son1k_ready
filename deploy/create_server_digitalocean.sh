#!/bin/bash

# Script para crear servidor en DigitalOcean via CLI
# Requiere: doctl (DigitalOcean CLI) instalado y configurado

echo "🌊 Creando servidor DigitalOcean para Son1k..."

# Configuración del servidor
DROPLET_NAME="son1k-production"
REGION="nyc1"  # Nueva York
SIZE="s-2vcpu-4gb"  # 2 vCPUs, 4GB RAM
IMAGE="ubuntu-22-04-x64"
SSH_KEY_NAME="son1k-key"

# Verificar si doctl está instalado
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl no está instalado"
    echo "💡 Instalar con: brew install doctl"
    echo "💡 O descargar desde: https://github.com/digitalocean/doctl/releases"
    exit 1
fi

# Crear SSH key si no existe
if [ ! -f ~/.ssh/son1k_rsa ]; then
    echo "🔑 Generando SSH key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/son1k_rsa -N ""
    echo "✅ SSH key generada: ~/.ssh/son1k_rsa"
fi

# Subir SSH key a DigitalOcean
echo "📤 Subiendo SSH key a DigitalOcean..."
doctl compute ssh-key create "$SSH_KEY_NAME" --public-key-file ~/.ssh/son1k_rsa.pub || echo "Key ya existe"

# Crear droplet
echo "🚀 Creando servidor..."
doctl compute droplet create "$DROPLET_NAME" \
    --region "$REGION" \
    --size "$SIZE" \
    --image "$IMAGE" \
    --ssh-keys "$SSH_KEY_NAME" \
    --enable-monitoring \
    --enable-ipv6 \
    --wait

# Obtener IP del servidor
echo "📍 Obteniendo IP del servidor..."
SERVER_IP=$(doctl compute droplet get "$DROPLET_NAME" --format PublicIPv4 --no-header)

if [ -z "$SERVER_IP" ]; then
    echo "❌ No se pudo obtener la IP del servidor"
    exit 1
fi

echo "✅ Servidor creado con IP: $SERVER_IP"

# Crear script de conexión
cat > connect_to_server.sh << EOF
#!/bin/bash
# Script para conectar al servidor Son1k
ssh -i ~/.ssh/son1k_rsa root@$SERVER_IP
EOF

chmod +x connect_to_server.sh

# Esperar a que el servidor esté listo
echo "⏳ Esperando que el servidor esté listo..."
sleep 30

# Subir archivos al servidor
echo "📤 Subiendo archivos de deployment..."
scp -i ~/.ssh/son1k_rsa son1k_cloud_deploy.tar.gz root@$SERVER_IP:/root/
scp -i ~/.ssh/son1k_rsa quick_cloud_deploy.sh root@$SERVER_IP:/root/

echo "🎯 Ejecutando deployment en el servidor..."
ssh -i ~/.ssh/son1k_rsa root@$SERVER_IP << 'ENDSSH'
cd /root
tar -xzf son1k_cloud_deploy.tar.gz
chmod +x quick_cloud_deploy.sh
./quick_cloud_deploy.sh
ENDSSH

echo
echo "🎉 ¡Servidor creado y configurado!"
echo "📋 Información del servidor:"
echo "   IP: $SERVER_IP"
echo "   SSH: ssh -i ~/.ssh/son1k_rsa root@$SERVER_IP"
echo "   Conectar: ./connect_to_server.sh"
echo
echo "🔄 Próximo paso: Configurar DNS en IONOS"
echo "   Añadir registro A: son1kvers3.com -> $SERVER_IP"
echo "   Añadir registro A: api.son1kvers3.com -> $SERVER_IP"
echo
echo "🌐 Después del DNS, visitar: https://son1kvers3.com"