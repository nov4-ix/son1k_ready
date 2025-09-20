#!/bin/bash

# Son1k Production Cloud Deployment Script
# Domain: son1kvers3.com (IONOS)
# Credentials: domain + password "iloveMusic!90"

set -e

echo "🚀 Iniciando deployment de Son1k en cloud..."
echo "🌐 Dominio: son1kvers3.com"
echo "☁️  Proveedor: IONOS"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Create cloud server setup commands
print_step "PASO 1: Preparando comandos para servidor cloud"

cat > server_setup.sh << 'EOF'
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
EOF

# Step 2: Create production environment
print_step "PASO 2: Creando configuración de producción"

cat > .env.production << EOF
# Son1k Production Environment
NODE_ENV=production
DOMAIN=son1kvers3.com
API_DOMAIN=api.son1kvers3.com

# Database
POSTGRES_DB=son1k_prod
POSTGRES_USER=son1k_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Redis
REDIS_URL=redis://redis:6379

# API Keys (configurar en producción)
SUNO_API_KEY=your_suno_api_key_here
JWT_SECRET=$(openssl rand -base64 64)

# Monitoring
LOG_LEVEL=info
ENABLE_METRICS=true
EOF

# Step 3: Create production Docker Compose
print_step "PASO 3: Configurando Docker Compose para producción"

cat > docker-compose.cloud.yml << 'EOF'
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - son1k_network
    restart: unless-stopped

  # Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - son1k_network
    restart: unless-stopped

  # API Backend
  api:
    build:
      context: ../backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=${REDIS_URL}
      - SUNO_API_KEY=${SUNO_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - LOG_LEVEL=${LOG_LEVEL}
    depends_on:
      - postgres
      - redis
    networks:
      - son1k_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker
  celery:
    build:
      context: ../backend
      dockerfile: Dockerfile
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=${REDIS_URL}
      - SUNO_API_KEY=${SUNO_API_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - son1k_network
    restart: unless-stopped

  # Selenium (for Suno automation)
  selenium:
    image: selenium/standalone-chrome:latest
    environment:
      - SE_VNC_NO_PASSWORD=1
      - SE_NODE_MAX_SESSIONS=1
    ports:
      - "4444:4444"
      - "7900:7900"
    volumes:
      - /dev/shm:/dev/shm
    networks:
      - son1k_network
    restart: unless-stopped

networks:
  son1k_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

# Step 4: Create Nginx configuration
print_step "PASO 4: Configurando Nginx"

cat > nginx.cloud.conf << 'EOF'
# API Backend (api.son1kvers3.com)
server {
    listen 80;
    server_name api.son1kvers3.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization";
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
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
    }
    
    # Static assets with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Step 5: Create deployment package
print_step "PASO 5: Creando paquete de deployment"

tar -czf son1k_cloud_deploy.tar.gz \
    server_setup.sh \
    .env.production \
    docker-compose.cloud.yml \
    nginx.cloud.conf \
    ../backend \
    frontend/

print_success "Paquete creado: son1k_cloud_deploy.tar.gz"

# Step 6: Create DNS configuration instructions
print_step "PASO 6: Instrucciones DNS para IONOS"

cat > ionos_dns_setup.md << 'EOF'
# Configuración DNS en IONOS para son1kvers3.com

## Credenciales
- Dominio: son1kvers3.com
- Usuario: (usar el dominio)
- Contraseña: iloveMusic!90

## Pasos en el panel IONOS:

1. **Acceder al panel**:
   - URL: https://www.ionos.com/
   - Login con credenciales del dominio

2. **Configurar registros DNS**:
   ```
   # Registro A principal
   @ (root)          A    [IP_DEL_SERVIDOR]
   
   # Subdominios
   www              A    [IP_DEL_SERVIDOR]
   api              A    [IP_DEL_SERVIDOR]
   
   # Opcional: CDN
   cdn              CNAME son1kvers3.com
   ```

3. **Verificar propagación**:
   ```bash
   dig son1kvers3.com
   dig api.son1kvers3.com
   ```

## Después de configurar DNS:

1. **SSL con Let's Encrypt**:
   ```bash
   certbot --nginx -d son1kvers3.com -d www.son1kvers3.com -d api.son1kvers3.com
   ```

2. **Verificar servicios**:
   - Frontend: https://son1kvers3.com
   - API: https://api.son1kvers3.com/docs
   - Health: https://api.son1kvers3.com/health
EOF

# Step 7: Create quick cloud deployment script
print_step "PASO 7: Script de deployment rápido"

cat > quick_cloud_deploy.sh << 'EOF'
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
EOF

chmod +x quick_cloud_deploy.sh

# Step 8: Show deployment summary
print_step "PASO 8: Resumen del deployment"

echo
print_success "📦 Archivos de deployment creados:"
echo "   - son1k_cloud_deploy.tar.gz (paquete completo)"
echo "   - server_setup.sh (configuración del servidor)"
echo "   - quick_cloud_deploy.sh (deployment automático)"
echo "   - ionos_dns_setup.md (instrucciones DNS)"

echo
print_warning "🔄 Próximos pasos:"
echo "   1. Crear servidor cloud (DigitalOcean/AWS/Linode)"
echo "   2. Subir son1k_cloud_deploy.tar.gz al servidor"
echo "   3. Ejecutar: bash quick_cloud_deploy.sh"
echo "   4. Configurar DNS en IONOS con la IP del servidor"
echo "   5. Activar SSL con certbot"

echo
print_success "🌐 URLs finales:"
echo "   - Frontend: https://son1kvers3.com"
echo "   - API: https://api.son1kvers3.com"
echo "   - Docs: https://api.son1kvers3.com/docs"

echo
echo "🔐 Credenciales IONOS recordadas:"
echo "   - Dominio: son1kvers3.com"
echo "   - Contraseña: iloveMusic!90"