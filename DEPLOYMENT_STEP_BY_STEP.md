# 🚀 Deployment Paso a Paso para Son1k

## 📋 **PARTE 1: Frontend en Vercel (GRATIS)**

### Paso 1: Crear cuenta Vercel
1. Ir a: https://vercel.com
2. Hacer clic en "Sign Up"
3. Seleccionar "Continue with GitHub"
4. Autorizar Vercel para acceder a tus repos

### Paso 2: Crear proyecto Vercel
1. En Vercel dashboard, clic en "New Project"
2. Buscar tu repo: `son1k-suno-mvp`
3. Seleccionar el repo y clic en "Import"

### Paso 3: Configurar el proyecto
```
Framework Preset: Other
Root Directory: frontend/
Build Command: (dejar vacío)
Output Directory: (dejar vacío)
Install Command: (dejar vacío)
```

### Paso 4: Variables de entorno en Vercel
```
API_BASE_URL=https://api.son1kvers3.com
ENVIRONMENT=production
```

### Paso 5: Deploy inicial
1. Clic en "Deploy"
2. Esperar 1-2 minutos
3. Vercel te dará una URL temporal como: `son1k-suno-mvp.vercel.app`

### Paso 6: Configurar dominio personalizado
1. En el proyecto Vercel, ir a "Settings" > "Domains"
2. Añadir: `son1kvers3.com`
3. Añadir: `www.son1kvers3.com`
4. Vercel te dará los DNS records para configurar

---

## 📋 **PARTE 2: Backend en Hetzner (€4.51/mes)**

### Paso 1: Crear cuenta Hetzner
1. Ir a: https://www.hetzner.com/cloud
2. Clic en "Sign Up"
3. Completar registro (email, verificación)
4. **No requiere pago inmediato - 7 días gratis**

### Paso 2: Crear servidor
1. Crear nuevo proyecto: "son1k-production"
2. Crear servidor:
   - **Ubicación**: Nuremberg (Alemania) o Ashburn (USA)
   - **Imagen**: Ubuntu 22.04
   - **Tipo**: CX11 (1 vCPU, 2GB RAM) - €4.51/mes
   - **SSH Key**: Generar nueva o subir existente

### Paso 3: Obtener IP del servidor
1. Anotar la IP pública del servidor creado
2. Ejemplo: `78.46.XXX.XXX`

### Paso 4: Conectar al servidor
```bash
# Conectar vía SSH
ssh root@YOUR_SERVER_IP

# Primer comando al conectar
apt update && apt upgrade -y
```

### Paso 5: Subir archivos de deployment
```bash
# En tu máquina local
scp son1k_cloud_deploy.tar.gz root@YOUR_SERVER_IP:/root/
scp quick_cloud_deploy.sh root@YOUR_SERVER_IP:/root/
```

### Paso 6: Ejecutar deployment
```bash
# En el servidor
cd /root
tar -xzf son1k_cloud_deploy.tar.gz
chmod +x quick_cloud_deploy.sh
./quick_cloud_deploy.sh
```

---

## 📋 **PARTE 3: Configurar DNS en IONOS**

### Paso 1: Acceder panel IONOS
1. Ir a: https://www.ionos.com
2. Login con:
   - **Usuario**: son1kvers3.com
   - **Contraseña**: iloveMusic!90

### Paso 2: Configurar registros DNS
En la sección DNS Management:

```
# Para Vercel (Frontend)
Tipo: CNAME
Nombre: @
Valor: cname.vercel-dns.com

Tipo: CNAME  
Nombre: www
Valor: cname.vercel-dns.com

# Para Hetzner (Backend API)
Tipo: A
Nombre: api
Valor: YOUR_HETZNER_SERVER_IP
```

### Paso 3: Esperar propagación
- Tiempo típico: 5-30 minutos
- Verificar con: `dig son1kvers3.com`

---

## 📋 **PARTE 4: SSL y Verificación Final**

### Paso 1: Configurar SSL en Hetzner
```bash
# En el servidor Hetzner, una vez que DNS esté propagado
certbot --nginx -d api.son1kvers3.com

# Seguir instrucciones para generar certificado
```

### Paso 2: Verificar Vercel SSL
- Vercel configura SSL automáticamente
- Verificar que https://son1kvers3.com funcione

### Paso 3: Tests finales
```bash
# 1. Frontend
curl -I https://son1kvers3.com
# Debe devolver 200 OK

# 2. Backend API
curl https://api.son1kvers3.com/health
# Debe devolver {"status": "ok"}

# 3. Documentación API
# Abrir: https://api.son1kvers3.com/docs
```

---

## 🎯 **RESUMEN DE COSTOS**

| Servicio | Costo | Período Gratuito |
|----------|--------|------------------|
| **Vercel** | $0 | Gratis permanente |
| **Hetzner** | €4.51/mes | 7 días gratis |
| **IONOS** | Ya pagado | - |
| **SSL** | $0 | Gratis (Let's Encrypt) |
| **TOTAL** | **€4.51/mes** | **7 días gratis** |

---

## ✅ **URLs Finales**

Una vez completado:
- **🌐 Frontend**: https://son1kvers3.com
- **📡 API**: https://api.son1kvers3.com
- **📚 Docs**: https://api.son1kvers3.com/docs
- **💳 Pricing**: https://son1kvers3.com/pricing
- **⚖️ Terms**: https://son1kvers3.com/terms
- **🔒 Privacy**: https://son1kvers3.com/privacy

---

## 🆘 **Troubleshooting**

### Si algo falla:

**DNS no propaga:**
```bash
# Verificar configuración
dig son1kvers3.com @8.8.8.8
nslookup api.son1kvers3.com
```

**SSL falla:**
```bash
# Verificar que DNS esté resuelto primero
certbot --nginx -d api.son1kvers3.com --dry-run
```

**API no responde:**
```bash
# En servidor Hetzner
docker-compose logs api
docker-compose restart api
```

---

## 📞 **Soporte**

Si necesitas ayuda:
- **Vercel**: https://vercel.com/help
- **Hetzner**: https://docs.hetzner.com
- **Certbot**: https://certbot.eff.org/help/

---

## 🎉 **¡Listo para recibir usuarios y pagos reales!**

Una vez completados estos pasos, tendrás Son1k completamente funcional en producción, listo para generar ingresos.