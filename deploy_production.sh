#!/bin/bash
# 🚀 Son1kVers3 PRODUCTION Deployment Script
# Para VPS IONOS con dominio son1kvers3.com

set -e

echo "🌐 SON1KVERS3.COM - PRODUCTION DEPLOYMENT"
echo "========================================"

# Variables de producción
DOMAIN="son1kvers3.com"
WWW_DOMAIN="www.son1kvers3.com"
APP_DIR="/var/www/son1kvers3"
SECRET_KEY="son1k_production_$(openssl rand -hex 16)"
DB_PATH="$APP_DIR/backend/son1k_production.db"

echo "📦 [1/8] Installing system dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git curl htop

echo "👤 [2/8] Creating application user..."
sudo useradd -r -s /bin/false son1k || true
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

echo "📁 [3/8] Setting up application..."
cd $APP_DIR

# Backend setup
echo "🐍 [4/8] Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Initialize production database
echo "🗄️ [5/8] Setting up production database..."
export POSTGRES_DSN="sqlite:///$DB_PATH"
export SECRET_KEY="$SECRET_KEY"
export CORS_ORIGINS="https://$DOMAIN,https://$WWW_DOMAIN"

python -c "from app.db import init_db; init_db(); print('✅ Database initialized')"

echo "⚙️ [6/8] Creating systemd service..."
sudo tee /etc/systemd/system/son1kvers3.service > /dev/null <<EOF
[Unit]
Description=Son1kVers3 Music Platform
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
Environment=POSTGRES_DSN=sqlite:///$DB_PATH
Environment=SECRET_KEY=$SECRET_KEY
Environment=CORS_ORIGINS=https://$DOMAIN,https://$WWW_DOMAIN
ExecStart=$APP_DIR/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "🌐 [7/8] Configuring Nginx..."
sudo tee /etc/nginx/sites-available/son1kvers3.com > /dev/null <<'EOF'
# Son1kVers3 Production Configuration
server {
    listen 80;
    server_name son1kvers3.com www.son1kvers3.com;
    return 301 https://son1kvers3.com$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.son1kvers3.com;
    return 301 https://son1kvers3.com$request_uri;
}

server {
    listen 443 ssl http2;
    server_name son1kvers3.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # SSL Configuration (will be added by certbot)
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "https://son1kvers3.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
        
        # Handle preflight
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "https://son1kvers3.com";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type "text/plain; charset=utf-8";
            add_header Content-Length 0;
            return 204;
        }
    }

    # Frontend
    location / {
        root /var/www/son1kvers3/frontend;
        try_files $uri $uri/ /index.html;
        
        # Cache control
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        location ~* \.(html)$ {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/son1kvers3.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

echo "🔄 [8/8] Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable son1kvers3
sudo systemctl start son1kvers3
sudo systemctl enable nginx
sudo systemctl reload nginx

echo "🔒 Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN -d $WWW_DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

echo "📊 Creating monitoring setup..."
sudo mkdir -p /var/log/son1kvers3
sudo chown -R $USER:$USER /var/log/son1kvers3

# Health check script
sudo tee /usr/local/bin/son1k_health.sh > /dev/null <<'EOF'
#!/bin/bash
curl -f https://son1kvers3.com/api/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "$(date): ✅ Son1kVers3 is healthy"
else
    echo "$(date): ❌ Son1kVers3 health check failed"
    sudo systemctl restart son1kvers3
fi
EOF

sudo chmod +x /usr/local/bin/son1k_health.sh

# Add to crontab for monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/son1k_health.sh >> /var/log/son1kvers3/health.log 2>&1") | crontab -

echo ""
echo "🎉 SON1KVERS3.COM DEPLOYMENT COMPLETED!"
echo "======================================="
echo ""
echo "🌐 Your platform is now live at:"
echo "   https://son1kvers3.com"
echo "   https://www.son1kvers3.com"
echo ""
echo "📊 Service Status:"
sudo systemctl status son1kvers3 --no-pager -l
echo ""
echo "🔧 Useful Commands:"
echo "   sudo systemctl status son1kvers3     # Check service"
echo "   sudo journalctl -u son1kvers3 -f     # View logs"
echo "   sudo systemctl restart son1kvers3    # Restart service"
echo "   sudo nginx -t && sudo systemctl reload nginx  # Reload nginx"
echo ""
echo "📈 Monitoring:"
echo "   tail -f /var/log/son1kvers3/health.log  # Health checks"
echo "   curl https://son1kvers3.com/api/health  # Test API"
echo ""
echo "🎯 Next Steps:"
echo "1. Test registration: https://son1kvers3.com"
echo "2. Update Chrome extension to use new domain"
echo "3. Configure domain email if needed"
echo "4. Setup monitoring alerts"

# Final health check
echo ""
echo "🏥 Final Health Check:"
sleep 5
curl -f https://son1kvers3.com/api/health && echo "✅ API is responding" || echo "❌ API check failed"
EOF