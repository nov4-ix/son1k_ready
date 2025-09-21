# 🚀 Guía de Despliegue Railway - Son1k Suno MVP v2

## 🎯 Resumen del Proyecto

**Son1k Suno MVP v2** es una plataforma completa de integración con Suno AI que incluye:
- ✅ **FastAPI Backend** con autenticación JWT
- ✅ **Celery + Redis** para procesamiento en background  
- ✅ **PostgreSQL** para persistencia de datos
- ✅ **WebSocket** para actualizaciones en tiempo real
- ✅ **Extensión Chrome** para integración con Suno
- ✅ **Sistema de pagos y suscripciones**

## Paso 1: Preparación ✅

Los archivos de configuración ya están listos:
- ✅ `railway.toml` - Configuración principal
- ✅ `railway.json` - Configuración alternativa
- ✅ `Procfile` - Comandos de inicio (web, worker, beat)
- ✅ `Dockerfile` - Container optimizado para Railway
- ✅ `railway.env.example` - Variables de entorno necesarias

## Paso 2: Crear Proyecto en Railway

### 2.1 Crear Cuenta
1. Ve a [railway.app](https://railway.app)
2. Registrarte con GitHub
3. Verifica tu email

### 2.2 Crear Proyecto
1. Click "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Conecta el repositorio con este código

## Paso 3: Agregar Servicios Necesarios

### 3.1 PostgreSQL Database
1. En tu proyecto → "Add Service" → "Database" → "PostgreSQL"
2. Railway creará automáticamente la variable `DATABASE_URL`

### 3.2 Redis
1. En tu proyecto → "Add Service" → "Database" → "Redis"
2. Railway creará automáticamente la variable `REDIS_URL`

## Paso 4: Configurar Variables de Entorno

En Railway dashboard → Variables → Agregar estas variables:

### Variables Críticas (OBLIGATORIAS)
```bash
# Seguridad
SECRET_KEY=tu-clave-super-secreta-cambiar-esto
JWT_SECRET_KEY=tu-jwt-secret-cambiar-esto

# CORS (cambiar por tu dominio real)
CORS_ORIGINS=https://tu-app-name.railway.app

# Configuración de app
PROJECT_NAME=Son1k Suno MVP
DEBUG=false
LOG_LEVEL=INFO
```

### Variables de Suno (para integración)
```bash
SUNO_SESSION_ID=tu_session_id_de_suno
SUNO_COOKIE=tu_cookie_de_suno
SUNO_BASE_URL=https://studio-api.suno.ai
SUNO_TIMEOUT=120
```

### Variables de Rate Limiting
```bash
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_BURST=5
```

### Variables de Extensión
```bash
EXTENSION_SECRET=tu-extension-secret
ALLOWED_EXTENSION_IDS=ghpilnilpmfdacoaiacjlafeemanjijn,bfbmjmiodbnnpllbbbfblcplfjjepjdn
```

**Nota**: Las variables `DATABASE_URL` y `REDIS_URL` se crean automáticamente cuando agregas los servicios.

## Paso 5: Configurar Workers (Opcional)

Si necesitas Celery workers para procesamiento en background:

1. En tu proyecto → "Add Service" → "Empty Service"
2. Nombra el servicio: "worker"
3. En Variables del worker:
   - Usar las mismas variables que el servicio web
   - En "Build & Deploy" → Start Command: `cd backend && python -m celery worker -A app.queue.celery_app --loglevel=info`

## Paso 6: Desplegar

### Despliegue Automático
1. Railway detectará tu `railway.toml`
2. Build iniciará automáticamente
3. Monitorea en "Deployments" tab

### Verificar Health Check
Una vez desplegado:
- `https://tu-app.railway.app/health` - Estado de la API
- `https://tu-app.railway.app/docs` - Documentación Swagger

## Paso 7: Configuración Post-Despliegue

### 7.1 Actualizar CORS
Cambia la variable `CORS_ORIGINS` con tu URL real:
```bash
CORS_ORIGINS=https://tu-app-real.railway.app
```

### 7.2 Configurar Dominio Personalizado (Opcional)
1. En proyecto → Settings → Domains
2. Agregar dominio personalizado
3. Configurar DNS según instrucciones

### 7.3 Extensión Chrome
1. Actualiza el URL en la extensión con tu nuevo dominio
2. Reinstala la extensión desde `extension/` folder

## Paso 8: Testing

### Test Básico de API
```bash
# Health check
curl https://tu-app.railway.app/health

# Test de creación de canción (requiere auth)
curl -X POST https://tu-app.railway.app/api/songs/create \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test_user" \
  -d '{"prompt":"Cyberpunk ballad, 90 BPM", "length_sec":60}'
```

### Test WebSocket
```javascript
// Conectar a WebSocket
const ws = new WebSocket('wss://tu-app.railway.app/ws/test_user');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Troubleshooting

### ❌ Error: "Build failed - requirements.txt not found"
**Solución**: Railway busca requirements.txt en root. Asegúrate de que `railway.toml` tenga el buildCommand correcto.

### ❌ Error: "Database connection failed"
**Solución**: Verifica que PostgreSQL service esté corriendo y `DATABASE_URL` configurada.

### ❌ Error: "Redis connection failed"
**Solución**: Verifica que Redis service esté corriendo y `REDIS_URL` configurada.

### ❌ Error: "CORS origin not allowed"
**Solución**: Actualiza `CORS_ORIGINS` con tu dominio real de Railway.

### ❌ Error: "Extension can't connect"
**Solución**: Actualiza la extensión con el nuevo URL de Railway.

## Arquitectura en Railway

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │   PostgreSQL    │    │      Redis      │
│   (FastAPI)     │ ←→ │   Database      │    │   (Cache/Queue) │
│   Port: 8000    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ↑                                             ↑
         │                                             │
┌─────────────────┐                          ┌─────────────────┐
│ Celery Worker   │                          │   WebSocket     │
│  (Background)   │ ←────────────────────────→ │   Connections   │
│   (Optional)    │                          │                 │
└─────────────────┘                          └─────────────────┘
```

## Variables de Entorno Críticas

🔴 **OBLIGATORIAS** (el app no funcionará sin estas):
- `SECRET_KEY`
- `JWT_SECRET_KEY` 
- `DATABASE_URL` (automática)
- `REDIS_URL` (automática)

🟡 **IMPORTANTES** (para funcionalidad completa):
- `CORS_ORIGINS`
- `SUNO_SESSION_ID`
- `SUNO_COOKIE`

🟢 **OPCIONALES** (tienen defaults):
- `DEBUG` (default: false)
- `RATE_LIMIT_PER_MINUTE` (default: 10)
- `LOG_LEVEL` (default: INFO)

## ✅ Lista de Verificación Final

- [ ] Servicios creados (PostgreSQL + Redis)
- [ ] Variables de entorno configuradas
- [ ] Build completado sin errores
- [ ] Health check funcionando (`/health`)
- [ ] API docs accesibles (`/docs`)
- [ ] WebSocket conectando (`/ws/{user_id}`)
- [ ] Extensión Chrome actualizada
- [ ] CORS configurado correctamente
- [ ] SSL/HTTPS funcionando

## 🎉 ¡Listo!

Tu plataforma Son1k Suno MVP v2 está corriendo en Railway en:
- **API**: `https://tu-app.railway.app`
- **Docs**: `https://tu-app.railway.app/docs`
- **WebSocket**: `wss://tu-app.railway.app/ws/{user_id}`

---

**Soporte**: Consulta [railway.app/help](https://railway.app/help) para temas específicos de Railway.

**Resistencia Sonora** ⚡ - Democratizando la creación musical