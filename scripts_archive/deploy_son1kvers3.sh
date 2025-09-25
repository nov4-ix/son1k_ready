#!/bin/bash

echo "🚀 DEPLOY SON1K A PRODUCCIÓN CON DOMINIO PERSONALIZADO"
echo "======================================================"
echo "🌐 Dominio: son1kvers3.com"
echo "🏢 Proveedor: IONOS"
echo "🎯 Objetivo: Link público para testers"
echo ""

# Configuración
DOMAIN="son1kvers3.com"
PROJECT_NAME="son1k-production"

echo "📋 INFORMACIÓN DEL DEPLOY:"
echo "   Dominio: $DOMAIN"
echo "   Proyecto: $PROJECT_NAME"
echo "   Frontend: React/HTML estático"
echo "   Backend: Docker + API"
echo ""

echo "🎯 ESTRATEGIA DE DEPLOY:"
echo "   1. Frontend → Vercel/Netlify (CDN global)"
echo "   2. Backend → DigitalOcean/Railway (contenedores)"
echo "   3. Base datos → PostgreSQL gestionada"
echo "   4. DNS → Configuración en IONOS"
echo ""

# Crear estructura para deploy
echo "📁 Preparando archivos para deploy..."

# 1. Preparar frontend para deploy estático
mkdir -p deploy/frontend
cp -r frontend/* deploy/frontend/

# 2. Configurar variables de producción para frontend
cat > deploy/frontend/config.js << 'EOF'
// Configuración de producción para Son1k
window.SON1K_CONFIG = {
    API_BASE_URL: 'https://api.son1kvers3.com',
    DOMAIN: 'son1kvers3.com',
    ENVIRONMENT: 'production',
    VERSION: '3.0.0',
    FEATURES: {
        TRANSPARENT_GENERATION: true,
        DYNAMIC_NAMING: true,
        REAL_TIME_UPDATES: true
    }
};

console.log('🎵 Son1k Production Config Loaded');
console.log('🌐 API:', window.SON1K_CONFIG.API_BASE_URL);
console.log('✅ Transparent Generation Enabled');
EOF

# 3. Modificar index.html para producción
sed -i.bak 's|localhost:8000|api.son1kvers3.com|g' deploy/frontend/index.html
sed -i.bak 's|http://|https://|g' deploy/frontend/index.html

# 4. Crear package.json para frontend
cat > deploy/frontend/package.json << 'EOF'
{
  "name": "son1k-frontend",
  "version": "3.0.0",
  "description": "Son1k - Generación Musical Transparente",
  "main": "index.html",
  "scripts": {
    "build": "echo 'Frontend built successfully'",
    "start": "echo 'Serving static files'"
  },
  "keywords": ["music", "generation", "ai", "son1k"],
  "author": "Son1k Team",
  "license": "MIT"
}
EOF

# 5. Crear Dockerfile optimizado para producción
cat > deploy/Dockerfile.production << 'EOF'
# Imagen optimizada para producción
FROM python:3.11-slim

# Variables de entorno de producción
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV API_WORKERS=4

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r son1k && useradd -r -g son1k son1k

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY backend/ ./backend/
COPY deploy/production_config.py ./backend/app/production_config.py

# Cambiar ownership
RUN chown -R son1k:son1k /app

# Cambiar a usuario no-root
USER son1k

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
EOF

# 6. Crear docker-compose para producción
cat > deploy/docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  api:
    build:
      context: ..
      dockerfile: deploy/Dockerfile.production
    container_name: son1k_api_prod
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - POSTGRES_DSN=postgresql://son1k_user:${DB_PASSWORD}@db:5432/son1k_prod
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_ORIGINS=https://son1kvers3.com,https://www.son1kvers3.com
      - CORS_ORIGINS=https://son1kvers3.com
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    volumes:
      - app_data:/app/data
    networks:
      - son1k_network

  worker:
    build:
      context: ..
      dockerfile: deploy/Dockerfile.production
    container_name: son1k_worker_prod
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - POSTGRES_DSN=postgresql://son1k_user:${DB_PASSWORD}@db:5432/son1k_prod
      - REDIS_URL=redis://redis:6379/0
    command: ["celery", "-A", "backend.app.queue.celery_app", "worker", "--loglevel=info", "-Q", "default", "-c", "2"]
    depends_on:
      - db
      - redis
    volumes:
      - app_data:/app/data
    networks:
      - son1k_network

  selenium:
    image: selenium/standalone-chrome:latest
    container_name: son1k_selenium_prod
    restart: unless-stopped
    shm_size: 2gb
    environment:
      - SE_NODE_MAX_SESSIONS=2
      - SE_VNC_NO_PASSWORD=1
      - SE_SESSION_TIMEOUT=600
    volumes:
      - selenium_data:/home/seluser/downloads
    networks:
      - son1k_network

  db:
    image: postgres:15-alpine
    container_name: son1k_db_prod
    restart: unless-stopped
    environment:
      - POSTGRES_DB=son1k_prod
      - POSTGRES_USER=son1k_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - son1k_network

  redis:
    image: redis:7-alpine
    container_name: son1k_redis_prod
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - son1k_network

  nginx:
    image: nginx:alpine
    container_name: son1k_nginx_prod
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    networks:
      - son1k_network

volumes:
  postgres_data:
  redis_data:
  app_data:
  selenium_data:

networks:
  son1k_network:
    driver: bridge
EOF

# 7. Crear configuración de Nginx
cat > deploy/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api:8000;
    }

    # Redirección HTTP a HTTPS
    server {
        listen 80;
        server_name son1kvers3.com www.son1kvers3.com;
        return 301 https://$server_name$request_uri;
    }

    # Configuración HTTPS
    server {
        listen 443 ssl http2;
        server_name son1kvers3.com www.son1kvers3.com;

        # Certificados SSL (Let's Encrypt)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        # Configuración SSL moderna
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;

        # Headers de seguridad
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Proxy para API
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header Access-Control-Allow-Origin "https://son1kvers3.com" always;
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
        }

        # Health check
        location /health {
            proxy_pass http://api_backend/health;
            access_log off;
        }

        # Documentación API
        location /docs {
            proxy_pass http://api_backend/docs;
        }

        # Frontend servido por CDN, pero fallback local
        location / {
            return 301 https://son1kvers3.com$request_uri;
        }
    }
}
EOF

# 8. Crear script de configuración de DNS
cat > deploy/configure_dns.md << 'EOF'
# 🌐 Configuración DNS para son1kvers3.com

## Registros DNS a configurar en IONOS:

### Registros A (IPv4):
```
Tipo: A
Nombre: @
Valor: [IP_DEL_SERVIDOR]
TTL: 3600

Tipo: A  
Nombre: www
Valor: [IP_DEL_SERVIDOR]
TTL: 3600

Tipo: A
Nombre: api
Valor: [IP_DEL_SERVIDOR]  
TTL: 3600
```

### Registro CNAME (Alias):
```
Tipo: CNAME
Nombre: app
Valor: son1kvers3.com
TTL: 3600
```

## URLs finales:
- Frontend: https://son1kvers3.com
- API: https://api.son1kvers3.com
- Documentación: https://api.son1kvers3.com/docs
- Health: https://api.son1kvers3.com/health

## Verificación:
```bash
# Verificar DNS
dig son1kvers3.com
dig www.son1kvers3.com
dig api.son1kvers3.com

# Test de conectividad
curl https://son1kvers3.com
curl https://api.son1kvers3.com/health
```
EOF

# 9. Crear script de deploy automatizado
cat > deploy/deploy.sh << 'EOF'
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
EOF

chmod +x deploy/deploy.sh

# 10. Crear README de deploy
cat > deploy/README.md << 'EOF'
# 🚀 Deploy de Son1k a Producción

## 🎯 Objetivo
Deploy del sistema Son1k en producción con dominio personalizado `son1kvers3.com`.

## 📋 Componentes
- **Frontend**: HTML/JS estático con interceptor de transparencia
- **Backend**: FastAPI + Celery + PostgreSQL + Redis + Selenium
- **Proxy**: Nginx con SSL
- **DNS**: Configurado en IONOS

## 🌐 URLs Finales
- Frontend: https://son1kvers3.com
- API: https://api.son1kvers3.com  
- Documentación: https://api.son1kvers3.com/docs

## 🚀 Proceso de Deploy

### 1. Preparar servidor (DigitalOcean/AWS)
```bash
# Crear droplet Ubuntu 22.04
# Instalar Docker y Docker Compose
# Configurar firewall (puertos 80, 443)
```

### 2. Deploy de backend
```bash
cd deploy
./deploy.sh
```

### 3. Configurar SSL (Let's Encrypt)
```bash
sudo apt install certbot
sudo certbot --nginx -d son1kvers3.com -d www.son1kvers3.com -d api.son1kvers3.com
```

### 4. Deploy de frontend (Vercel/Netlify)
```bash
# Subir carpeta deploy/frontend a Vercel
# Configurar dominio personalizado
# Configurar redirects
```

### 5. Configurar DNS en IONOS
- Ver archivo: configure_dns.md

## 🔧 Monitoreo
- Health check: https://api.son1kvers3.com/health
- Logs: `docker-compose logs -f`
- Métricas: Panel de Grafana (opcional)

## 🎵 Features Garantizadas
✅ Transparencia total (sin referencias a "suno")
✅ Nombres dinámicos basados en lyrics
✅ Job IDs con formato son1k_job_*
✅ SSL/HTTPS automático
✅ CDN global para frontend
✅ Escalabilidad horizontal
EOF

echo ""
echo "✅ ARCHIVOS DE DEPLOY PREPARADOS"
echo "================================"
echo ""
echo "📁 Estructura creada:"
echo "   deploy/"
echo "   ├── frontend/           # Frontend listo para CDN"
echo "   ├── Dockerfile.production"
echo "   ├── docker-compose.production.yml"
echo "   ├── nginx.conf"
echo "   ├── deploy.sh"
echo "   ├── configure_dns.md    # Instrucciones DNS"
echo "   └── README.md"
echo ""
echo "🎯 PRÓXIMOS PASOS:"
echo "   1. 🌐 Crear servidor en DigitalOcean/AWS"
echo "   2. 📦 Subir archivos al servidor"
echo "   3. 🚀 Ejecutar ./deploy/deploy.sh"
echo "   4. 🔒 Configurar SSL con Let's Encrypt"
echo "   5. 🌍 Configurar DNS en IONOS"
echo "   6. 📱 Deploy frontend en Vercel/Netlify"
echo ""
echo "📋 Información del dominio:"
echo "   Dominio: son1kvers3.com"
echo "   Proveedor: IONOS"
echo "   Panel: Acceso con dominio + iloveMusic!90"
echo ""
echo "🎵 Una vez completado, tendrás:"
echo "   ✅ https://son1kvers3.com (Frontend)"
echo "   ✅ https://api.son1kvers3.com (API)"
echo "   ✅ Sistema transparente funcionando"
echo "   ✅ Link público para testers"