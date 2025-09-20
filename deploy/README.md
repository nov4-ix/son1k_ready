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
