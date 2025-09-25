#!/bin/bash
# 🚀 Son1kVers3 - IONOS VPS Deployment Script
# Para ejecutar en VPS IONOS Ubuntu 22.04

set -e

echo "🚀 Deploying Son1kVers3 to IONOS VPS..."

# Variables
DOMAIN="son1kvers3.com"
WWW_DOMAIN="www.son1kvers3.com"
APP_DIR="/var/www/son1kvers3"
SECRET_KEY=$(openssl rand -hex 32)

echo "📦 Installing system dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git

echo "📁 Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Copy current codebase (adjust path as needed)
echo "📋 Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

echo "🐍 Setting up Python environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "🗄️ Initializing production database..."
export POSTGRES_DSN="sqlite:///./son1k_production.db"
export SECRET_KEY="$SECRET_KEY"
export CORS_ORIGINS="https://$DOMAIN,https://$WWW_DOMAIN"

python -c "from app.db import init_db; init_db()"

echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/son1kvers3.service > /dev/null <<EOF
[Unit]
Description=Son1kVers3 FastAPI Backend
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
Environment=POSTGRES_DSN=sqlite:///./son1k_production.db
Environment=SECRET_KEY=$SECRET_KEY
Environment=CORS_ORIGINS=https://$DOMAIN,https://$WWW_DOMAIN
ExecStart=$APP_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/son1kvers3.com > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN $WWW_DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin "https://$DOMAIN" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    }

    # Frontend
    location / {
        root $APP_DIR/frontend;
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

echo "🔗 Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/son1kvers3.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "🔄 Starting services..."
sudo systemctl enable son1kvers3
sudo systemctl start son1kvers3
sudo systemctl enable nginx

echo "🔒 Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN -d $WWW_DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

echo "📊 Creating log directories..."
sudo mkdir -p /var/log/son1kvers3
sudo chown -R $USER:$USER /var/log/son1kvers3

echo "✅ Deployment completed!"
echo ""
echo "🌐 Your site should be available at:"
echo "   https://$DOMAIN"
echo "   https://$WWW_DOMAIN"
echo ""
echo "📊 Service status:"
sudo systemctl status son1kvers3 --no-pager -l
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status son1kvers3    # Check service status"
echo "   sudo systemctl restart son1kvers3   # Restart service"
echo "   sudo journalctl -u son1kvers3 -f    # View logs"
echo "   sudo nginx -t                       # Test nginx config"
echo ""
echo "🎯 Next steps:"
echo "1. Update DNS A record: $DOMAIN → $(curl -s ifconfig.me)"
echo "2. Test: curl https://$DOMAIN/api/health"
echo "3. Configure domain email if needed"