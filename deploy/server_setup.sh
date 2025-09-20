#!/bin/bash
# Ejecutar en el servidor cloud (Ubuntu 22.04)

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker $USER

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Nginx
apt install nginx certbot python3-certbot-nginx -y

# Create directories
mkdir -p /opt/son1k
cd /opt/son1k

echo "✅ Servidor preparado para Son1k"
