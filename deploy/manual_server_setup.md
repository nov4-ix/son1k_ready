# Configuración Manual del Servidor para Son1k

## Opción 1: DigitalOcean (Recomendado)

### Paso 1: Crear Servidor
1. Ir a https://digitalocean.com
2. Crear cuenta o login
3. Crear nuevo Droplet:
   - **Sistema**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($24/mes - 2 vCPUs, 4GB RAM)
   - **Región**: New York o Amsterdam
   - **SSH Key**: Subir tu clave SSH pública

### Paso 2: Conectar al Servidor
```bash
# Una vez creado, conectar vía SSH
ssh root@YOUR_SERVER_IP

# Verificar conexión
uname -a
```

### Paso 3: Subir Archivos
```bash
# En tu máquina local, subir el paquete
scp son1k_cloud_deploy.tar.gz root@YOUR_SERVER_IP:/root/
scp quick_cloud_deploy.sh root@YOUR_SERVER_IP:/root/
```

### Paso 4: Ejecutar Deployment
```bash
# En el servidor
cd /root
tar -xzf son1k_cloud_deploy.tar.gz
chmod +x quick_cloud_deploy.sh
./quick_cloud_deploy.sh
```

## Opción 2: AWS EC2

### Crear Instancia
1. Ir a AWS Console
2. EC2 > Launch Instance
3. Configuración:
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t3.medium (2 vCPU, 4GB RAM)
   - **Security Group**: Permitir puertos 22, 80, 443
   - **Key Pair**: Crear o usar existente

### Deployment
Similar a DigitalOcean, usar el script `quick_cloud_deploy.sh`

## Opción 3: Linode/Vultr/Hetzner

Proceso similar:
1. Crear servidor Ubuntu 22.04
2. 2+ vCPUs, 4GB+ RAM
3. Abrir puertos 22, 80, 443
4. Subir y ejecutar scripts de deployment

## Configuración DNS en IONOS

### Acceso al Panel
1. Ir a https://www.ionos.com
2. Login con:
   - **Usuario**: son1kvers3.com (o email asociado)
   - **Contraseña**: iloveMusic!90

### Configurar Registros DNS
En la sección DNS del dominio `son1kvers3.com`:

```
Tipo    Nombre              Valor               TTL
A       @                   YOUR_SERVER_IP      3600
A       www                 YOUR_SERVER_IP      3600
A       api                 YOUR_SERVER_IP      3600
CNAME   *.son1kvers3.com   son1kvers3.com      3600
```

### Verificar Propagación
```bash
# Verificar que los DNS estén propagados
dig son1kvers3.com
dig api.son1kvers3.com

# O usar herramientas online
# https://www.whatsmydns.net/#A/son1kvers3.com
```

## SSL (Let's Encrypt)

### Después del DNS
```bash
# En el servidor, ejecutar:
certbot --nginx -d son1kvers3.com -d www.son1kvers3.com -d api.son1kvers3.com

# Seguir las instrucciones
# Elegir opción 2 (Redirect HTTP to HTTPS)
```

## Verificación Final

### URLs a Probar
- **Frontend**: https://son1kvers3.com
- **API Docs**: https://api.son1kvers3.com/docs
- **Health Check**: https://api.son1kvers3.com/health
- **Generación**: https://api.son1kvers3.com/api/music/generate

### Comandos de Verificación
```bash
# Estado de servicios
docker-compose ps

# Logs
docker-compose logs api
docker-compose logs celery

# Restart si necesario
docker-compose restart
```

## Costos Estimados

| Proveedor | Plan | Precio/mes | Specs |
|-----------|------|------------|-------|
| DigitalOcean | Basic | $24 | 2 vCPU, 4GB RAM |
| AWS EC2 | t3.medium | ~$30 | 2 vCPU, 4GB RAM |
| Linode | Nanode 4GB | $24 | 2 vCPU, 4GB RAM |
| Vultr | Regular | $24 | 2 vCPU, 4GB RAM |

## Soporte y Monitoreo

### Logs Importantes
```bash
# API logs
docker-compose logs -f api

# Nginx logs
tail -f /var/log/nginx/error.log

# Sistema
journalctl -u nginx -f
```

### Comandos de Mantenimiento
```bash
# Restart servicios
docker-compose restart

# Update código
git pull && docker-compose build && docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U son1k_user son1k_prod > backup.sql
```