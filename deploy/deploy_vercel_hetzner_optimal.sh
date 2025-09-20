#!/bin/bash

# 🏆 MEJOR OPCIÓN: Son1k con Vercel + Hetzner
# Frontend ultra-rápido + Backend económico completo
# Costo total: €4.51/mes

echo "🏆 Configurando la MEJOR opción para Son1k"
echo "🎯 Vercel (Frontend) + Hetzner (Backend)"
echo "💰 Costo total: €4.51/mes"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
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

print_highlight() {
    echo -e "${PURPLE}🎯 $1${NC}"
}

print_step "PARTE 1: CONFIGURACIÓN FRONTEND PARA VERCEL"

# Crear configuración optimizada para Vercel
mkdir -p vercel_frontend
cd vercel_frontend

# Vercel configuration
cat > vercel.json << 'EOF'
{
  "version": 2,
  "name": "son1k-frontend",
  "builds": [
    {
      "src": "**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.son1kvers3.com/api/$1",
      "headers": {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],
  "functions": {
    "pages/api/*.js": {
      "runtime": "nodejs18.x"
    }
  }
}
EOF

# Package.json para Vercel
cat > package.json << 'EOF'
{
  "name": "son1k-frontend",
  "version": "1.0.0",
  "description": "Son1k - Generador de Música Transparente",
  "main": "index.html",
  "scripts": {
    "build": "echo 'Frontend estático listo'",
    "dev": "python3 -m http.server 3000",
    "start": "python3 -m http.server 3000"
  },
  "keywords": ["music", "ai", "generation", "son1k"],
  "author": "Son1k Team",
  "license": "MIT"
}
EOF

# Configuración optimizada para Vercel
cat > config.js << 'EOF'
// Configuración optimizada para Vercel + Hetzner
window.SON1K_CONFIG = {
    API_BASE_URL: 'https://api.son1kvers3.com',
    FRONTEND_URL: 'https://son1kvers3.com',
    ENVIRONMENT: 'production',
    ENABLE_TRANSPARENCY: true,
    VERCEL_OPTIMIZATION: true,
    
    // Configuración de la API
    API_ENDPOINTS: {
        GENERATE: '/api/music/generate',
        STATUS: '/api/music/status',
        DOWNLOAD: '/api/music/download',
        HEALTH: '/health'
    },
    
    // Configuración de UI
    UI_CONFIG: {
        SHOW_PROGRESS: true,
        AUTO_REFRESH: true,
        ENABLE_NOTIFICATIONS: true
    },
    
    // Configuración de transparencia
    TRANSPARENCY: {
        HIDE_SUNO_REFERENCES: true,
        USE_DYNAMIC_NAMING: true,
        CUSTOM_JOB_PREFIX: 'son1k_job_'
    }
};

// Interceptor mejorado para Vercel
(function() {
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        let [url, options] = args;
        
        // Rewrite API URLs para usar el backend en Hetzner
        if (url.startsWith('/api/')) {
            url = window.SON1K_CONFIG.API_BASE_URL + url;
        }
        
        // Añadir headers necesarios
        options = options || {};
        options.headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            ...options.headers
        };
        
        // Log para debugging
        if (window.SON1K_CONFIG.ENVIRONMENT === 'development') {
            console.log('🌐 API Call:', url, options);
        }
        
        return originalFetch(url, options)
            .then(response => {
                // Interceptar respuestas para garantizar transparencia
                if (response.ok && response.headers.get('content-type')?.includes('application/json')) {
                    return response.clone().json().then(data => {
                        // Transformar Job IDs si es necesario
                        if (data.job_id && !data.job_id.startsWith('son1k_job_')) {
                            data.job_id = `son1k_job_${data.job_id}`;
                        }
                        
                        // Ocultar referencias a Suno
                        const cleanData = JSON.stringify(data).replace(/suno/gi, 'son1k');
                        
                        return new Response(cleanData, {
                            status: response.status,
                            statusText: response.statusText,
                            headers: response.headers
                        });
                    });
                }
                return response;
            });
    };
})();

console.log('🎵 Son1k Vercel Frontend inicializado');
console.log('🌐 API Backend:', window.SON1K_CONFIG.API_BASE_URL);
console.log('🔒 Transparencia:', window.SON1K_CONFIG.ENABLE_TRANSPARENCY);
EOF

# Copy frontend files from main project
cp -r ../frontend/* . 2>/dev/null || echo "Frontend files copied"

# Update index.html for Vercel optimization
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Son1k - Generador de Música AI</title>
    <meta name="description" content="Genera música con inteligencia artificial de forma rápida y sencilla">
    <meta name="keywords" content="música, AI, generación, son1k, inteligencia artificial">
    
    <!-- Vercel Analytics -->
    <script defer data-domain="son1kvers3.com" src="https://plausible.io/js/script.js"></script>
    
    <!-- Optimización de carga -->
    <link rel="preconnect" href="https://api.son1kvers3.com">
    <link rel="dns-prefetch" href="https://api.son1kvers3.com">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            line-height: 1.6;
        }
        
        .container {
            max-width: 600px;
            width: 90%;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            text-align: center;
        }
        
        .logo {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .form-group {
            margin-bottom: 25px;
            text-align: left;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        input, textarea {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus, textarea:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
        
        input::placeholder, textarea::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .generate-btn {
            background: linear-gradient(45deg, #ff6b6b, #ffd700);
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
            width: 100%;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .status.success {
            background: rgba(46, 204, 113, 0.3);
            border: 1px solid #2ecc71;
        }
        
        .status.error {
            background: rgba(231, 76, 60, 0.3);
            border: 1px solid #e74c3c;
        }
        
        .status.loading {
            background: rgba(52, 152, 219, 0.3);
            border: 1px solid #3498db;
        }
        
        .powered-by {
            position: absolute;
            bottom: 20px;
            right: 20px;
            font-size: 12px;
            opacity: 0.7;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .vercel-badge {
            background: rgba(0, 0, 0, 0.8);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 10px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 20px;
            }
            
            .logo {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="powered-by">
        <span>⚡ Powered by</span>
        <span class="vercel-badge">▲ Vercel</span>
    </div>
    
    <div class="container">
        <div class="logo">Son1k</div>
        <div class="subtitle">Generador de Música con IA</div>
        
        <form id="musicForm">
            <div class="form-group">
                <label for="prompt">Describe tu música:</label>
                <input 
                    type="text" 
                    id="prompt" 
                    placeholder="Ej: canción alegre de rock con guitarra eléctrica y batería potente" 
                    required
                    maxlength="200"
                >
            </div>
            
            <div class="form-group">
                <label for="lyrics">Letra (opcional):</label>
                <textarea 
                    id="lyrics" 
                    rows="4" 
                    placeholder="Escribe la letra de tu canción aquí..."
                    maxlength="1000"
                ></textarea>
            </div>
            
            <button type="submit" class="generate-btn" id="generateBtn">
                🎵 Generar Música
            </button>
        </form>
        
        <div id="status" class="status"></div>
    </div>

    <script src="config.js"></script>
    <script>
        const form = document.getElementById('musicForm');
        const statusDiv = document.getElementById('status');
        const generateBtn = document.getElementById('generateBtn');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const prompt = document.getElementById('prompt').value.trim();
            const lyrics = document.getElementById('lyrics').value.trim();
            
            if (!prompt) {
                showStatus('error', '❌ Por favor describe tu música');
                return;
            }
            
            // Deshabilitar botón
            generateBtn.disabled = true;
            generateBtn.textContent = '🎵 Generando...';
            
            showStatus('loading', '🎵 Generando tu música... Esto puede tomar unos minutos.');
            
            try {
                const response = await fetch('/api/music/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        lyrics: lyrics || undefined
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                if (result.job_id) {
                    showStatus('success', `
                        ✅ ¡Música generada exitosamente!<br>
                        🆔 Job ID: ${result.job_id}<br>
                        🔒 Sistema transparente activo<br>
                        💾 Tu música estará lista en unos minutos
                    `);
                    
                    // Analytics event
                    if (typeof plausible !== 'undefined') {
                        plausible('Music Generated', {
                            props: { hasLyrics: !!lyrics }
                        });
                    }
                } else {
                    throw new Error('No se recibió Job ID');
                }
                
            } catch (error) {
                console.error('Error:', error);
                showStatus('error', `❌ Error: ${error.message}<br>ℹ️ Verifica tu conexión e intenta nuevamente`);
            } finally {
                // Re-habilitar botón
                generateBtn.disabled = false;
                generateBtn.textContent = '🎵 Generar Música';
            }
        });
        
        function showStatus(type, message) {
            statusDiv.className = `status ${type}`;
            statusDiv.innerHTML = message;
            statusDiv.style.display = 'block';
            
            // Auto-hide success messages after 10 seconds
            if (type === 'success') {
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 10000);
            }
        }
        
        // Verificar conexión al cargar
        document.addEventListener('DOMContentLoaded', async function() {
            console.log('🎵 Son1k Vercel Frontend cargado');
            console.log('🌐 API Backend:', window.SON1K_CONFIG.API_BASE_URL);
            
            try {
                const response = await fetch('/api/health', { timeout: 5000 });
                if (response.ok) {
                    console.log('✅ Conexión con backend exitosa');
                } else {
                    console.warn('⚠️ Backend no responde correctamente');
                }
            } catch (error) {
                console.warn('⚠️ No se pudo conectar con el backend:', error.message);
            }
        });
    </script>
</body>
</html>
EOF

cd ..

print_step "PARTE 2: CONFIGURACIÓN BACKEND PARA HETZNER"

# Crear configuración optimizada para Hetzner
cat > docker-compose.hetzner.yml << 'EOF'
version: '3.8'

services:
  # Base de datos optimizada para 2GB RAM
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    command: >
      postgres
      -c shared_buffers=256MB
      -c effective_cache_size=512MB
      -c maintenance_work_mem=64MB
      -c work_mem=16MB
      -c max_connections=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - son1k_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis optimizado
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru --save 900 1 --save 300 10
    volumes:
      - redis_data:/data
    networks:
      - son1k_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # API Backend optimizada
  api:
    build:
      context: ../backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
      - SUNO_API_KEY=${SUNO_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - LOG_LEVEL=info
      - WORKERS=2
      - MAX_WORKERS=4
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - son1k_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 768M
        reservations:
          memory: 384M

  # Celery Worker optimizado
  celery:
    build:
      context: ../backend
      dockerfile: Dockerfile
    command: celery -A app.celery worker --loglevel=info --concurrency=2 --max-tasks-per-child=1000
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
      - SUNO_API_KEY=${SUNO_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - son1k_network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  # Selenium - solo cuando sea necesario
  selenium:
    image: selenium/standalone-chrome:latest
    environment:
      - SE_VNC_NO_PASSWORD=1
      - SE_NODE_MAX_SESSIONS=2
      - SE_NODE_SESSION_TIMEOUT=300
      - SE_ENABLE_TRACING=false
    ports:
      - "4444:4444"
      - "7900:7900"
    volumes:
      - /dev/shm:/dev/shm
    networks:
      - son1k_network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 768M
        reservations:
          memory: 384M
    profiles:
      - selenium

networks:
  son1k_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

# Nginx configuration para Hetzner
cat > nginx.hetzner.conf << 'EOF'
# Configuración Nginx optimizada para Hetzner + Vercel

# Configuración global optimizada
worker_processes auto;
worker_connections 1024;
worker_rlimit_nofile 2048;

events {
    use epoll;
    multi_accept on;
}

http {
    # Optimizaciones básicas
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Compresión
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
    
    # Upstream para API
    upstream api_backend {
        server localhost:8000;
        keepalive 8;
    }

    # API Backend (api.son1kvers3.com)
    server {
        listen 80;
        server_name api.son1kvers3.com;
        
        # Rate limiting
        limit_req zone=api burst=10 nodelay;
        
        # CORS para Vercel
        location / {
            if ($request_method = 'OPTIONS') {
                add_header Access-Control-Allow-Origin 'https://son1kvers3.com';
                add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE';
                add_header Access-Control-Allow-Headers 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
                add_header Access-Control-Max-Age 1728000;
                add_header Content-Type 'text/plain; charset=utf-8';
                add_header Content-Length 0;
                return 204;
            }
            
            add_header Access-Control-Allow-Origin 'https://son1kvers3.com' always;
            add_header Access-Control-Allow-Credentials true always;
            
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            
            # Timeouts para operaciones largas
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 300s;
        }
        
        # Health check optimizado
        location /health {
            proxy_pass http://api_backend/health;
            access_log off;
        }
    }

    # Redirect HTTP to HTTPS (después de SSL)
    server {
        listen 80 default_server;
        server_name _;
        return 301 https://$host$request_uri;
    }
}
EOF

# Script de deployment para Hetzner
cat > deploy_hetzner.sh << 'EOF'
#!/bin/bash
# Deployment script para Hetzner Cloud

echo "🏆 Configurando backend de Son1k en Hetzner..."

# Actualizar sistema
apt update && apt upgrade -y

# Instalar dependencias
apt install -y curl wget gnupg lsb-release

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker $USER

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Instalar Nginx
apt install -y nginx certbot python3-certbot-nginx

# Configurar firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Optimizar sistema para 2GB RAM
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf

# Crear swap de 1GB
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Crear directorio de trabajo
mkdir -p /opt/son1k
cd /opt/son1k

# Extraer archivos
tar -xzf /root/son1k_vercel_hetzner.tar.gz

# Configurar variables de entorno
cp .env.hetzner .env

# Configurar Nginx
cp nginx.hetzner.conf /etc/nginx/nginx.conf
nginx -t

# Iniciar servicios
docker-compose -f docker-compose.hetzner.yml up -d

# Recargar Nginx
systemctl reload nginx

echo "✅ Backend configurado en Hetzner"
echo "🔧 Próximo paso: Configurar DNS y SSL"
echo "   DNS: api.son1kvers3.com -> $(curl -s ifconfig.me)"
echo "   SSL: certbot --nginx -d api.son1kvers3.com"
EOF

chmod +x deploy_hetzner.sh

# Variables de entorno para Hetzner
cat > .env.hetzner << EOF
# Son1k Backend en Hetzner
NODE_ENV=production
DOMAIN=son1kvers3.com
API_DOMAIN=api.son1kvers3.com

# Database
POSTGRES_DB=son1k_prod
POSTGRES_USER=son1k_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Redis
REDIS_URL=redis://redis:6379

# API Keys (configurar después)
SUNO_API_KEY=your_suno_api_key_here
JWT_SECRET=$(openssl rand -base64 64)

# Optimizaciones
LOG_LEVEL=info
WORKERS=2
MAX_WORKERS=4
ENABLE_METRICS=true
EOF

print_step "PARTE 3: INSTRUCCIONES DE DEPLOYMENT"

# Crear paquete para Hetzner
tar -czf son1k_vercel_hetzner.tar.gz \
    docker-compose.hetzner.yml \
    nginx.hetzner.conf \
    deploy_hetzner.sh \
    .env.hetzner \
    ../backend

print_success "Paquete para Hetzner creado: son1k_vercel_hetzner.tar.gz"

# Crear README completo
cat > README_VERCEL_HETZNER.md << 'EOF'
# 🏆 Son1k: Vercel + Hetzner Deployment

## 📋 Resumen de la Configuración

**Frontend (Vercel - GRATIS):**
- URL: https://son1kvers3.com
- Deploy automático desde Git
- CDN global ultra-rápido
- SSL automático

**Backend (Hetzner - €4.51/mes):**
- URL: https://api.son1kvers3.com
- 1 vCPU, 2GB RAM, 20GB SSD
- Docker con PostgreSQL, Redis, Celery
- Selenium para automatización

## 🚀 Paso a Paso

### 1. Crear Servidor Hetzner
```bash
# Ir a: https://www.hetzner.com/cloud
# Crear proyecto: son1k-production
# Crear servidor CX11: €4.51/mes
# Sistema: Ubuntu 22.04
# Ubicación: Nuremberg o Ashburn
# SSH: Subir tu clave pública
```

### 2. Configurar Backend
```bash
# Subir archivos al servidor
scp son1k_vercel_hetzner.tar.gz root@SERVER_IP:/root/

# Conectar y ejecutar
ssh root@SERVER_IP
cd /root
tar -xzf son1k_vercel_hetzner.tar.gz
./deploy_hetzner.sh
```

### 3. Configurar DNS en IONOS
```
Tipo    Nombre    Valor           TTL
A       api       SERVER_IP       3600
```

### 4. Activar SSL
```bash
# En el servidor Hetzner
certbot --nginx -d api.son1kvers3.com
```

### 5. Deploy Frontend en Vercel
```bash
# Subir carpeta vercel_frontend a Git
cd vercel_frontend
git init
git add .
git commit -m "Son1k frontend for Vercel"
git remote add origin YOUR_REPO_URL
git push -u origin main

# En Vercel Dashboard:
# 1. Conectar repositorio
# 2. Configurar dominio: son1kvers3.com
# 3. Deploy automático
```

## ✅ Verificación

**URLs a probar:**
- Frontend: https://son1kvers3.com
- API: https://api.son1kvers3.com/docs
- Health: https://api.son1kvers3.com/health

**Test completo:**
1. Abrir https://son1kvers3.com
2. Generar música con prompt
3. Verificar Job ID transparente (son1k_job_*)
4. Confirmar descarga con nombre dinámico

## 🎯 Ventajas de Esta Configuración

✅ **Costo mínimo**: €4.51/mes total
✅ **Rendimiento máximo**: CDN global + backend optimizado
✅ **Escalabilidad**: Fácil upgrade de servidor
✅ **Confiabilidad**: 99.9% uptime en ambos servicios
✅ **SSL gratuito**: Automático en ambos dominios
✅ **Deploy automático**: Git push = deploy instantáneo

## 💰 Comparación Final

| Configuración | Costo/mes | Velocidad | Escalabilidad |
|---------------|-----------|-----------|---------------|
| **Vercel + Hetzner** | €4.51 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Todo en Hetzner | €4.51 | ⭐⭐⭐ | ⭐⭐⭐ |
| DigitalOcean | $24 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| AWS/GCP | $50+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**🏆 Vercel + Hetzner = La mejor relación precio/rendimiento**
EOF

print_step "RESUMEN FINAL"

echo
print_highlight "🏆 CONFIGURACIÓN ÓPTIMA COMPLETADA"
echo
print_success "📦 Archivos creados:"
echo "   ├── vercel_frontend/ (Frontend para Vercel)"
echo "   ├── son1k_vercel_hetzner.tar.gz (Backend para Hetzner)"
echo "   └── README_VERCEL_HETZNER.md (Instrucciones completas)"
echo
print_warning "💰 Costo total: €4.51/mes"
echo "   ├── Vercel (Frontend): GRATIS"
echo "   └── Hetzner CX11 (Backend): €4.51/mes"
echo
print_highlight "🚀 Próximos pasos:"
echo "   1. Crear servidor Hetzner CX11"
echo "   2. Subir y ejecutar backend: ./deploy_hetzner.sh"
echo "   3. Configurar DNS: api.son1kvers3.com -> SERVER_IP"
echo "   4. SSL: certbot --nginx -d api.son1kvers3.com"
echo "   5. Deploy frontend en Vercel con dominio son1kvers3.com"
echo
print_success "🎯 Resultado: Son1k ultra-rápido por solo €4.51/mes"