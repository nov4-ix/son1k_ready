# 🎵 Son1k Suno API - Documentación Completa

## 🎯 API Transparente para Generación Musical

Esta API permite al frontend de Son1k generar música usando tu cuenta premium de Suno de forma completamente transparente.

## 🔗 Base URL
```
https://web-production-b52c4.up.railway.app
```

## 📋 Endpoints Disponibles

### 1. 🎵 Generar Música
```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "upbeat electronic song with synthesizers",
  "lyrics": "Verse 1:\nThis is my song\nIt's really long...",
  "style": "electronic",
  "duration": 60
}
```

**Respuesta:**
```json
{
  "job_id": "uuid-aqui",
  "status": "pending",
  "message": "Music generation started"
}
```

### 2. 📊 Verificar Estado
```http
GET /api/status/{job_id}
```

**Respuestas posibles:**

**🕐 Pendiente/Procesando:**
```json
{
  "job_id": "uuid-aqui",
  "status": "processing",
  "created_at": 1642678900
}
```

**🎉 Completado:**
```json
{
  "job_id": "uuid-aqui",
  "status": "completed",
  "created_at": 1642678900,
  "result": {
    "audio_url": "https://suno.com/song/xxxxx.mp3",
    "video_url": "https://suno.com/song/xxxxx.mp4",
    "title": "Generated Song Title",
    "duration": 60,
    "metadata": {
      "prompt": "upbeat electronic song...",
      "style": "electronic",
      "generated_at": 1642678960
    }
  }
}
```

**🛡️ CAPTCHA Requerido:**
```json
{
  "job_id": "uuid-aqui",
  "status": "captcha_needed",
  "created_at": 1642678900,
  "message": "CAPTCHA required - please solve and submit"
}
```

**❌ Error:**
```json
{
  "job_id": "uuid-aqui",
  "status": "failed",
  "created_at": 1642678900,
  "error": "Descripción del error"
}
```

### 3. 🛡️ Enviar CAPTCHA
```http
POST /api/captcha/{job_id}
Content-Type: application/json

{
  "captcha_solution": "solucion-del-captcha"
}
```

**Respuesta:**
```json
{
  "message": "CAPTCHA submitted, resuming generation"
}
```

### 4. 📋 Listar Trabajos (Debug)
```http
GET /api/jobs
```

## 🔄 Flujo Completo de Trabajo

### Frontend Son1k → API Son1k → Suno → API Son1k → Frontend Son1k

```javascript
// 1. Iniciar generación
const response = await fetch('/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "cyberpunk ballad, 90 BPM, emotional",
    lyrics: "Verse 1:\nIn the neon lights...",
    style: "ballad",
    duration: 120
  })
});

const { job_id } = await response.json();

// 2. Verificar estado periodicamente
const checkStatus = async () => {
  const statusResponse = await fetch(`/api/status/${job_id}`);
  const status = await statusResponse.json();
  
  switch(status.status) {
    case 'pending':
    case 'processing':
      // Mostrar "Generando música..."
      setTimeout(checkStatus, 5000); // Verificar cada 5 segundos
      break;
      
    case 'captcha_needed':
      // Mostrar CAPTCHA al usuario
      const captchaSolution = await showCaptchaModal();
      await fetch(`/api/captcha/${job_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ captcha_solution: captchaSolution })
      });
      setTimeout(checkStatus, 2000); // Continuar verificando
      break;
      
    case 'completed':
      // ¡Música lista!
      playGeneratedMusic(status.result.audio_url);
      showVideoIfAvailable(status.result.video_url);
      break;
      
    case 'failed':
      // Mostrar error al usuario
      showError(status.error);
      break;
  }
};

checkStatus();
```

## 🔧 Variables de Entorno Necesarias

Para conectar con tu cuenta premium de Suno, configura en Railway:

```bash
SUNO_SESSION_ID=tu_session_id_de_suno
SUNO_COOKIE=tu_cookie_completa_de_suno
```

## 🎨 Estilos Disponibles

- `pop`
- `rock`
- `electronic`
- `hip-hop`
- `jazz`
- `classical`
- `country`
- `ballad`
- `reggae`
- `blues`

## ⚡ Características del Sistema

- ✅ **Transparente**: Frontend no sabe que usa Suno
- ✅ **Asíncrono**: No bloquea la interfaz
- ✅ **CAPTCHA**: Manejo automático de CAPTCHAs
- ✅ **Error Handling**: Manejo robusto de errores
- ✅ **Job Tracking**: Seguimiento completo de trabajos
- ✅ **Premium**: Usa tu cuenta premium de Suno
- ✅ **Sin límites**: No hay límites adicionales, solo los de tu cuenta

## 🚀 URLs de Prueba

```bash
# Verificar que la API está funcionando
curl https://web-production-b52c4.up.railway.app/health

# Generar música de prueba
curl -X POST https://web-production-b52c4.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "happy birthday song, cheerful",
    "lyrics": "Happy birthday to you\nHappy birthday to you\nHappy birthday dear friend\nHappy birthday to you",
    "style": "pop",
    "duration": 30
  }'

# Verificar estado (usar el job_id de la respuesta anterior)
curl https://web-production-b52c4.up.railway.app/api/status/JOB_ID_AQUI
```

## 🔐 Seguridad

- API protegida con CORS
- Validación de inputs
- Rate limiting (puede agregarse)
- Autenticación JWT (puede agregarse)

¡Tu API de generación musical transparente está lista! 🎉