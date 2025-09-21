# 🚂 Railway Deployment Guide for Son1k

## 📋 **PASO 1: Crear cuenta Railway (GRATIS)**

1. **Ir a**: https://railway.app
2. **Clic en "Login"**
3. **Seleccionar**: "Login with GitHub"
4. **Autorizar** Railway para acceder a tus repos
5. **Verificar email** si te lo pide

## 📋 **PASO 2: Deploy desde GitHub**

1. **En Railway Dashboard**, clic en "New Project"
2. **Seleccionar**: "Deploy from GitHub repo"
3. **Buscar**: `son1k-suno-mvp`
4. **Clic en "Deploy"**

## 📋 **PASO 3: Configuración automática**

Railway detectará automáticamente:
- ✅ `requirements.txt` (dependencias Python)
- ✅ `Procfile` (comando de inicio)
- ✅ `railway.json` (configuración específica)

## 📋 **PASO 4: Variables de entorno**

En el proyecto Railway, ir a **"Variables"** y añadir:

```bash
# Database (Railway te da una gratis)
DATABASE_URL=postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway

# Redis (Railway te da uno gratis)
REDIS_URL=redis://default:password@containers-us-west-xxx.railway.app:6379

# Básicas
NODE_ENV=production
PORT=8000

# Stripe (usar claves de test primero)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# JWT
JWT_SECRET=your-super-secret-jwt-key-here

# CORS
CORS_ORIGINS=https://son1kvers3.com,https://www.son1kvers3.com

# Opcional (para Suno - añadir después)
SUNO_API_KEY=your_suno_key_here
SUNO_EMAIL=your_suno_email_here
SUNO_PASSWORD=your_suno_password_here
```

## 📋 **PASO 5: Añadir servicios**

1. **PostgreSQL Database**:
   - En Railway, clic "New" → "Database" → "PostgreSQL"
   - Automáticamente se conecta con `DATABASE_URL`

2. **Redis Cache**:
   - En Railway, clic "New" → "Database" → "Redis"
   - Automáticamente se conecta con `REDIS_URL`

## 📋 **PASO 6: Deploy y obtener URL**

1. Railway hará deploy automáticamente
2. Te dará una URL como: `https://son1k-backend-production.up.railway.app`
3. Verificar que funciona: `https://tu-url.railway.app/health`

## 📋 **PASO 7: Actualizar Vercel**

En tu proyecto Vercel, actualizar la variable:
```
API_BASE_URL=https://tu-url.railway.app
```

## 📋 **PASO 8: Configurar dominio personalizado**

1. **En Railway**, ir a "Settings" → "Domains"
2. **Añadir**: `api.son1kvers3.com`
3. **Railway te dará DNS records** para IONOS
4. **En IONOS**, añadir el CNAME que te dio Railway

## ⏱️ **Tiempos estimados**:
- Crear cuenta: 2 minutos
- Deploy inicial: 3-5 minutos
- Configurar variables: 2 minutos
- **Total: ~10 minutos**

## 💰 **Costos**:
- **$5 crédito gratis** cada mes
- Suficiente para testing y primeros usuarios
- Después: ~$5-20/mes dependiendo del uso

## 🧪 **Testing**:
Una vez deployado, probar:
1. `https://tu-url.railway.app/health` → Debe devolver 200
2. `https://tu-url.railway.app/docs` → Swagger UI
3. `https://son1kvers3.com` → Frontend con backend conectado

## 🚀 **Next Steps**:
1. Deploy en Railway
2. Configurar Stripe para pagos reales
3. Añadir credenciales de Suno
4. Testing completo del flujo
5. ¡Listo para usuarios reales!

---

## 🆘 **Troubleshooting**

**Si falla el build**:
- Verificar que `requirements.txt` esté en la raíz
- Verificar que `Procfile` apunte al directorio correcto

**Si falla al inicio**:
- Revisar logs en Railway Dashboard
- Verificar variables de entorno
- Verificar que `DATABASE_URL` esté configurado

**Si no conecta con frontend**:
- Verificar CORS_ORIGINS incluya son1kvers3.com
- Actualizar API_BASE_URL en Vercel
- Verificar que la URL de Railway sea correcta