#!/bin/bash

# Deployment económico en Hetzner Cloud (€4.51/mes)
# La opción más barata para Son1k con buen rendimiento

echo "💰 Deployment económico de Son1k en Hetzner Cloud"
echo "💳 Costo: €4.51/mes (~$5 USD)"
echo "🖥️  Specs: 1 vCPU, 2GB RAM, 20GB SSD"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_step "PASO 1: Instrucciones para crear servidor Hetzner"

cat << 'EOF'
🌐 CREAR SERVIDOR EN HETZNER CLOUD:

1. Ir a: https://www.hetzner.com/cloud
2. Registrarse/Login
3. Crear nuevo proyecto: "son1k-production"
4. Crear servidor:
   - Ubicación: Nuremberg (Alemania) o Ashburn (USA)
   - Imagen: Ubuntu 22.04
   - Tipo: CX11 (1 vCPU, 2GB RAM) - €4.51/mes
   - Red: IPv4 + IPv6
   - SSH Key: Subir tu clave pública

5. Anotar la IP del servidor creado

EOF

print_step "PASO 2: Configuración optimizada para servidor económico"

# Crear docker-compose optimizado para 2GB RAM
cat > docker-compose.economic.yml << 'EOF'
version: '3.8'

services:
  # Base de datos ligera
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER} 
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      # Optimización para poca RAM
      POSTGRES_INITDB_ARGS: "--data-checksums"
    command: >
      postgres
      -c shared_buffers=128MB
      -c effective_cache_size=256MB
      -c maintenance_work_mem=32MB
      -c work_mem=8MB
      -c max_connections=50
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - son1k_network
    restart: unless-stopped

  # Cache ligero
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 64mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - son1k_network
    restart: unless-stopped

  # API optimizada
  api:
    build:
      context: ../backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
      - SUNO_API_KEY=${SUNO_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - LOG_LEVEL=warning
      - WORKERS=1
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    depends_on:
      - postgres
      - redis
    networks:
      - son1k_network
    restart: unless-stopped

  # Celery worker ligero
  celery:
    build:
      context: ../backend
      dockerfile: Dockerfile
    command: celery -A app.celery worker --loglevel=warning --concurrency=1
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
      - SUNO_API_KEY=${SUNO_API_KEY}
    deploy:
      resources:
        limits:
          memory: 384M
        reservations:
          memory: 192M
    depends_on:
      - postgres
      - redis
    networks:
      - son1k_network
    restart: unless-stopped

  # Selenium solo cuando sea necesario
  selenium:
    image: selenium/standalone-chrome:latest
    environment:
      - SE_VNC_NO_PASSWORD=1
      - SE_NODE_MAX_SESSIONS=1
      - SE_ENABLE_TRACING=false
    deploy:
      resources:
        limits:
          memory: 768M
        reservations:
          memory: 384M
    volumes:
      - /dev/shm:/dev/shm
    networks:
      - son1k_network
    restart: unless-stopped
    profiles:
      - selenium  # Solo se inicia cuando se especifica

networks:
  son1k_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

print_step "PASO 3: Script de deployment económico"

cat > deploy_economic.sh << 'EOF'
#!/bin/bash
# Deployment para servidor económico (2GB RAM)

echo "💰 Configurando Son1k en servidor económico..."

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker (método ligero)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker $USER

# Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Nginx ligero
apt install nginx -y

# Configurar swap para mejorar rendimiento
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Optimizaciones del sistema
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf

# Crear directorio de trabajo
mkdir -p /opt/son1k
cd /opt/son1k

# Extraer archivos
tar -xzf /root/son1k_economic_deploy.tar.gz

# Configurar variables de entorno
cp .env.economic .env

# Iniciar servicios básicos (sin Selenium inicialmente)
docker-compose -f docker-compose.economic.yml up -d postgres redis api celery

# Configurar Nginx
cp nginx.economic.conf /etc/nginx/sites-available/son1k
ln -sf /etc/nginx/sites-available/son1k /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "✅ Deployment económico completado!"
echo "💰 Costo: €4.51/mes"
echo "🔧 Para iniciar Selenium (solo cuando sea necesario):"
echo "   docker-compose --profile selenium up -d selenium"
EOF

chmod +x deploy_economic.sh

print_step "PASO 4: Configuración económica de variables"

cat > .env.economic << EOF
# Son1k Economic Configuration
NODE_ENV=production
DOMAIN=son1kvers3.com
API_DOMAIN=api.son1kvers3.com

# Database optimizada
POSTGRES_DB=son1k_prod
POSTGRES_USER=son1k_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Redis
REDIS_URL=redis://redis:6379

# API Keys
SUNO_API_KEY=your_suno_api_key_here
JWT_SECRET=$(openssl rand -base64 64)

# Optimizaciones
LOG_LEVEL=warning
WORKERS=1
ENABLE_METRICS=false
MAX_MEMORY_USAGE=80
EOF

print_step "PASO 5: Nginx optimizado para económico"

cat > nginx.economic.conf << 'EOF'
# Configuración Nginx optimizada para servidor económico

# Optimizaciones globales
worker_processes 1;
worker_connections 1024;

events {
    use epoll;
    multi_accept on;
}

http {
    # Compresión
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;

    # Cache básico
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;

    # API Backend
    upstream api_backend {
        server localhost:8000;
        keepalive 2;
    }

    # API (api.son1kvers3.com)
    server {
        listen 80;
        server_name api.son1kvers3.com;
        
        location / {
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        }
    }

    # Frontend (son1kvers3.com)
    server {
        listen 80;
        server_name son1kvers3.com www.son1kvers3.com;
        root /var/www/son1k;
        index index.html;
        
        location / {
            try_files $uri $uri/ /index.html;
            expires 1h;
        }
        
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

print_step "PASO 6: Crear paquete económico"

tar -czf son1k_economic_deploy.tar.gz \
    docker-compose.economic.yml \
    deploy_economic.sh \
    .env.economic \
    nginx.economic.conf \
    ../backend \
    ../frontend

print_success "Paquete económico creado: son1k_economic_deploy.tar.gz"

print_step "RESUMEN ECONÓMICO"

echo
print_success "💰 COSTO TOTAL: €4.51/mes (~$5 USD)"
echo
echo "📋 Comparación de opciones:"
echo "   ┌─────────────────┬──────────────┬─────────────┐"
echo "   │ Proveedor       │ Costo/mes    │ Specs       │"
echo "   ├─────────────────┼──────────────┼─────────────┤"
echo "   │ Hetzner CX11    │ €4.51 (~$5)  │ 1 vCPU, 2GB │"
echo "   │ Vultr Regular   │ $6           │ 1 vCPU, 1GB │"
echo "   │ Linode Nanode   │ $5           │ 1 vCPU, 1GB │"
echo "   │ DigitalOcean    │ $6           │ 1 vCPU, 1GB │"
echo "   └─────────────────┴──────────────┴─────────────┘"
echo
print_warning "🔄 Próximos pasos para deployment económico:"
echo "   1. Crear servidor Hetzner CX11 (€4.51/mes)"
echo "   2. Subir: scp son1k_economic_deploy.tar.gz root@SERVER_IP:/root/"
echo "   3. Ejecutar: ssh root@SERVER_IP 'cd /root && tar -xzf son1k_economic_deploy.tar.gz && ./deploy_economic.sh'"
echo "   4. Configurar DNS en IONOS"
echo "   5. SSL: certbot --nginx -d son1kvers3.com -d api.son1kvers3.com"
echo
print_success "🎯 Resultado: Son1k funcionando por solo €4.51/mes"