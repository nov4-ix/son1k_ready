# Variables de entorno para Railway - Sistema completo

## Variables necesarias para Railway:

### Suno API (obligatorio)
```
SUNO_SESSION_ID=tu_session_id_aqui
SUNO_COOKIE=tu_cookie_completa_aqui
```

### Ollama AI (para funciones avanzadas)
```
OLLAMA_URL=https://bcea9a8ab0da.ngrok-free.app
```

### Waves Plugins (opcional - fallback a FFmpeg)
```
WAVES_PLUGINS_PATH=/Applications/Waves
```

### Puerto
```
PORT=8000
```

## Características por configuración:

### Con OLLAMA_URL configurado:
✅ Asistente conversacional interactivo
✅ Generación de letras con IA
✅ Optimización inteligente de prompts
✅ Análisis de coherencia lírica
✅ Recomendaciones personalizadas
✅ Mejora automática de prompts

### Sin OLLAMA_URL:
✅ Generación básica de música
✅ Ghost Studio con templates
✅ Sistema de tiers
✅ Templates predefinidos
⚠️ AI avanzado deshabilitado

### Con WAVES_PLUGINS_PATH:
✅ Postproducción profesional con Waves
✅ Masterización automática
✅ EQ, compresión, reverb avanzados

### Sin Waves:
✅ Postproducción básica con FFmpeg
✅ Normalización de audio
✅ Filtros básicos

## Estado actual del tunnel ngrok:
URL: https://bcea9a8ab0da.ngrok-free.app
Status: ✅ Activo
Modelo: llama3.1:8b

## Próximos pasos:
1. Configurar variables en Railway
2. Desplegar sistema completo
3. Probar todas las funciones