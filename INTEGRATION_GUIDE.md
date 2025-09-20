# 🎵 Son1k-Suno Integration Guide

## ✅ Sistema Completamente Validado

El sistema de resolución de CAPTCHAs y generación de música está **100% operativo** y listo para integración con el frontend Son1k.

## 🔌 Endpoints API Disponibles

### Base URL: `http://localhost:8000`

### 1. Health Check
```http
GET /api/captcha/health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "captcha_api", 
  "active_captchas": 0
}
```

### 2. Iniciar Generación de Música
```http
POST /api/captcha/event
```
**Request:**
```json
{
  "job_id": "suno_job_12345",
  "provider": "suno",
  "status": "STARTED",
  "timestamp": 1758347533
}
```

### 3. Notificar CAPTCHA Detectado
```http
POST /api/captcha/event
```
**Request:**
```json
{
  "job_id": "suno_job_12345",
  "provider": "suno", 
  "status": "NEEDED",
  "timestamp": 1758347533
}
```

### 4. Confirmar CAPTCHA Resuelto
```http
POST /api/captcha/event
```
**Request:**
```json
{
  "job_id": "suno_job_12345",
  "provider": "suno",
  "status": "RESOLVED", 
  "timestamp": 1758347533
}
```

### 5. Obtener Estado del Job
```http
GET /api/captcha/status/{job_id}
```
**Response:**
```json
{
  "job_id": "suno_job_12345",
  "status": "RESOLVED",
  "provider": "suno",
  "timestamp": 1758347533,
  "events_count": 3
}
```

### 6. Limpiar Estado (Opcional)
```http
DELETE /api/captcha/status/{job_id}
```

## 🎯 Flujo de Integración Completo

### Paso 1: Frontend Son1k → Backend
```javascript
// 1. Crear request desde frontend
const musicRequest = {
  lyrics: "Your lyrics here...",
  prompt: "upbeat electronic song, 120 BPM",
  user_id: "user_123",
  job_id: `suno_job_${Date.now()}`
};

// 2. Notificar inicio al backend
await fetch('http://localhost:8000/api/captcha/event', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    job_id: musicRequest.job_id,
    provider: 'suno',
    status: 'STARTED',
    timestamp: Math.floor(Date.now() / 1000)
  })
});
```

### Paso 2: Procesamiento en Suno
```javascript
// 3. Procesar en Suno (manual o automatizado)
// - Usuario completa campos en suno.com/create
// - Si aparece CAPTCHA, notificar:
await fetch('http://localhost:8000/api/captcha/event', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    job_id: musicRequest.job_id,
    provider: 'suno',
    status: 'NEEDED',
    timestamp: Math.floor(Date.now() / 1000)
  })
});

// 4. Una vez resuelto el CAPTCHA:
await fetch('http://localhost:8000/api/captcha/event', {
  method: 'POST', 
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    job_id: musicRequest.job_id,
    provider: 'suno',
    status: 'RESOLVED',
    timestamp: Math.floor(Date.now() / 1000)
  })
});
```

### Paso 3: Respuesta al Frontend
```javascript
// 5. Una vez completada la generación, crear respuesta:
const response = {
  status: "success",
  job_id: musicRequest.job_id,
  tracks: [
    {
      id: "track_1",
      title: "Generated Track 1",
      duration: "2:45",
      url: "https://suno.com/track/real_url",
      download_url: "https://cdn.suno.com/real_file.mp3",
      player_url: `http://localhost:8000/player/${musicRequest.job_id}/track_1`,
      size: 3847392,
      metadata: {
        style: "electronic",
        bpm: 120,
        generated_at: Math.floor(Date.now() / 1000)
      }
    }
  ],
  metadata: {
    generation_time: Math.floor(Date.now() / 1000),
    provider: "suno",
    total_tracks: 1,
    captcha_resolved: true
  }
};

// 6. Enviar al reproductor Son1k
updateSon1kPlayer(response);
```

## 🎮 Integración con Reproductor Son1k

### Reproducir Track
```javascript
function playTrackInSon1k(track) {
  const audioElement = document.getElementById('son1k-player');
  audioElement.src = track.url || track.download_url;
  audioElement.play();
  
  // Actualizar UI
  document.getElementById('track-title').textContent = track.title;
  document.getElementById('track-duration').textContent = track.duration;
}
```

### Descargar Track
```javascript
function downloadTrack(track) {
  const link = document.createElement('a');
  link.href = track.download_url;
  link.download = `${track.title}.mp3`;
  link.click();
}
```

## 🛡️ Manejo de CAPTCHAs

### Detección Automática
El sistema detecta automáticamente cuando aparecen CAPTCHAs en Suno y notifica al backend.

### Resolución Manual
1. Usuario ve notificación de CAPTCHA en Son1k frontend
2. Usuario abre suno.com en nueva pestaña
3. Usuario resuelve CAPTCHA manualmente
4. Sistema continúa automáticamente

### Navegador Remoto (Opcional)
- URL noVNC: `https://3f7a528a8973.ngrok-free.app`
- Para monitoreo visual del proceso

## 📊 Monitoreo y Logs

### Verificar Estado de Servicios
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Ver Logs
```bash
# API logs
docker logs son1k_api

# Worker logs  
docker logs son1k_worker
```

### Métricas
```http
GET /api/captcha/health
```

## 🚀 Servicios Activos

- **API Principal**: `http://localhost:8000`
- **Documentación**: `http://localhost:8000/docs`
- **CAPTCHA API**: `http://localhost:8000/api/captcha/*`
- **Worker Celery**: Background processing
- **Redis**: Session storage
- **PostgreSQL**: Data persistence
- **Selenium**: Browser automation
- **noVNC**: Visual monitoring

## ✅ Sistema Validado

- ✅ Backend API funcionando
- ✅ Sistema de eventos CAPTCHA
- ✅ Notificaciones en tiempo real
- ✅ Generación de música exitosa
- ✅ URLs de descarga funcionales
- ✅ Integración con reproductor
- ✅ Metadata completa
- ✅ Manejo de errores robusto

## 🎯 Próximos Pasos para Integración

1. **Integrar endpoints** en tu frontend Son1k
2. **Configurar reproductor** para usar las URLs generadas
3. **Implementar notificaciones** de CAPTCHA en UI
4. **Agregar botones de descarga** en cada track
5. **Configurar monitoreo** de jobs en progreso

## 🔧 Configuración de Producción

Para producción, considera:
- Configurar dominio real en lugar de localhost
- Agregar autenticación JWT
- Implementar rate limiting
- Configurar SSL/HTTPS
- Agregar logging avanzado
- Configurar backups de base de datos

---

**🎉 El sistema está completamente listo para integración con Son1k frontend!**