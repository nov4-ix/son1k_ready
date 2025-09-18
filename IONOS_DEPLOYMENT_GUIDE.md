# 🌐 Son1kVers3 - Deployment en IONOS con Dominio Personalizado

## 🎯 OBJETIVO: son1kvers3.com → Plataforma musical comercial

### OPCIÓN A: VPS IONOS (RECOMENDADO)

#### 1. CONFIGURACIÓN VPS IONOS (15 min)
```bash
# En VPS Ubuntu 22.04
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx certbot python3-certbot-nginx -y

# Clonar repositorio
git clone <repo> /var/www/son1kvers3
cd /var/www/son1kvers3
```

#### 2. SETUP BACKEND (10 min)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar para producción
export POSTGRES_DSN="sqlite:///./son1k_production.db"
export SECRET_KEY="your-secret-key-here"
export CORS_ORIGINS="https://son1kvers3.com,https://www.son1kvers3.com"

# Inicializar DB
python -c "from app.db import init_db; init_db()"
```

#### 3. NGINX CONFIGURATION (5 min)
```nginx
# /etc/nginx/sites-available/son1kvers3.com
server {
    listen 80;
    server_name son1kvers3.com www.son1kvers3.com;

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        root /var/www/son1kvers3/frontend;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
```

#### 4. SSL CERTIFICATE (5 min)
```bash
sudo ln -s /etc/nginx/sites-available/son1kvers3.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d son1kvers3.com -d www.son1kvers3.com
```

#### 5. SYSTEMD SERVICE (5 min)
```ini
# /etc/systemd/system/son1kvers3.service
[Unit]
Description=Son1kVers3 FastAPI Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/son1kvers3/backend
Environment=PATH=/var/www/son1kvers3/backend/venv/bin
ExecStart=/var/www/son1kvers3/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable son1kvers3
sudo systemctl start son1kvers3
sudo systemctl status son1kvers3
```

### OPCIÓN B: IONOS SHARED HOSTING (LIMITADO)
- Solo frontend estático
- Backend requiere VPS

### OPCIÓN C: VERCEL + RAILWAY (ALTERNATIVO)
```bash
# Frontend → Vercel
npm install -g vercel
vercel --prod

# Backend → Railway
# Conectar GitHub repo
# Deploy automático
```

## 🔧 CONFIGURACIÓN DNS EN IONOS

### DNS Records necesarios:
```
A     son1kvers3.com          → IP_VPS_IONOS
CNAME www.son1kvers3.com      → son1kvers3.com
```

## 📊 COSTO ESTIMADO IONOS:
- **VPS Cloud S**: €4/mes (2GB RAM, 40GB SSD)
- **Dominio**: €12/año
- **Total**: ~€60/año

## 🚀 DEPLOYMENT STEPS:

1. **Contratar VPS IONOS** (Ubuntu 22.04)
2. **Configurar DNS** A record → IP VPS
3. **Deploy código** (usar script automatizado)
4. **SSL Certificate** con Let's Encrypt
5. **Monitoring** con systemd

## ⚡ SCRIPT AUTOMATIZADO:

```bash
#!/bin/bash
# deploy_son1k.sh
curl -sSL https://raw.githubusercontent.com/son1k/deployment/main/deploy.sh | bash
```

## 🎯 RESULTADO:
- **https://son1kvers3.com** ← Plataforma funcionando
- **SSL válido** con certificado automático
- **99.9% uptime** con systemd
- **Logs centralizados** en /var/log/son1kvers3/

## 📈 NEXT STEPS POST-DEPLOYMENT:
- Domain email: info@son1kvers3.com
- Analytics: Google Analytics
- Monitoring: Uptime Robot
- Backup: Daily automated