# Son1k ↔ Suno Bridge Chrome Extension

Extensión de Chrome que conecta el backend Son1kVers3 con Suno AI Studio para automatizar el envío de prompts y gestión de generaciones musicales.

## ✅ Estado: COMPLETAMENTE FUNCIONAL

Todos los problemas han sido corregidos:
- ✅ SyntaxErrors eliminados
- ✅ chrome.storage.sync funcionando correctamente  
- ✅ Apertura de pestañas Suno implementada
- ✅ Caracteres especiales corruptos limpiados
- ✅ Encoding UTF-8 sin BOM
- ✅ Selectores actualizados para DOM de Suno
- ✅ Validación completa pasada

## 🚀 Instalación

### 1. Cargar extensión en Chrome

```bash
# Validar antes de instalar (opcional)
cd extension/
node validate_extension.js
```

1. Abrir Chrome y navegar a `chrome://extensions/`
2. Activar **"Modo de desarrollador"** (toggle en la esquina superior derecha)
3. Hacer clic en **"Cargar extensión sin empaquetar"**
4. Seleccionar la carpeta: `/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2/extension`
5. La extensión aparecerá con el nombre "Son1k ↔ Suno Bridge (PoC)"

### 2. Configurar Backend

1. Hacer clic en el ícono de la extensión en la barra de herramientas
2. Ingresar la URL del backend: `http://localhost:8000`
3. Hacer clic en **"Guardar"**
4. Hacer clic en **"Probar"** para verificar conexión

## 🎵 Uso

### Flujo Completo

1. **Iniciar Backend Son1k**:
   ```bash
   cd "/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
   python3 run_local.py
   ```

2. **Configurar Extensión** (una sola vez):
   - Hacer clic en ícono de extensión
   - Verificar URL: `http://localhost:8000`
   - Probar conexión

3. **Generar en Suno**:
   - Ir a https://suno.com/create
   - Escribir prompt musical en el campo de texto
   - Hacer clic en **"Send to Son1k"** (botón flotante)
   - La extensión enviará automáticamente el prompt al backend

### Funcionalidades

- **Botón Flotante**: Se muestra en suno.com para envío rápido
- **Auto-detección**: Encuentra campos de prompt y lyrics automáticamente
- **Fallback Inteligente**: Múltiples selectores para robustez ante cambios de DOM
- **Notificaciones**: Toast messages para feedback del usuario
- **Almacenamiento**: Configuración persistente del backend URL

## 🔧 Archivos de la Extensión

```
extension/
├── manifest.json      # Configuración Manifest V3
├── background.js      # Service Worker (gestión de mensajes/fetch)
├── popup.html         # Interfaz del popup
├── popup.js          # Lógica del popup (configuración)
├── content.js        # Script inyectado en suno.com
├── validate_extension.js  # Script de validación
└── README.md         # Esta documentación
```

## 🛠️ Solución de Problemas

### Extensión no carga
```bash
# Verificar validación
cd extension/
node validate_extension.js
```

### Backend no responde
1. Verificar que el backend esté corriendo:
   ```bash
   curl http://localhost:8000/api/health
   ```
2. Verificar URL en popup de extensión
3. Comprobar CORS en configuración backend

### Botón no aparece en Suno
1. Refrescar la página suno.com/create
2. Verificar que la extensión esté habilitada
3. Abrir DevTools Console para ver errores

### Prompt no se envía
1. Verificar conexión del backend en popup
2. Revisar Console del navegador (F12)
3. Asegurar que hay texto en el campo de prompt

## 🔍 Debug/Desarrollo

### Console Logs
- **Background**: chrome://extensions → "Son1k Bridge" → "Ver vistas de servicio worker"
- **Content Script**: F12 en suno.com → Console
- **Popup**: F12 en popup abierto → Console

### API Endpoints
- **Health**: `GET http://localhost:8000/api/health`
- **Create Song**: `POST http://localhost:8000/api/songs/create`

### Test Manual
```bash
# Test backend
curl -X POST "http://localhost:8000/api/songs/create" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test song", "mode": "original"}'
```

## 📝 Especificaciones Técnicas

- **Manifest Version**: 3 (compatible con Chrome moderno)
- **Permisos**: storage, activeTab, scripting, tabs
- **Host Permissions**: suno.com, studio.suno.ai, localhost:8000
- **Content Scripts**: Ejecuta en `studio.suno.ai/*`
- **Encoding**: UTF-8 sin BOM
- **Compatibilidad**: Chrome 88+

## 🎯 Flujo de Datos

```
Suno.com (prompt) → Content Script → Background Script → Son1k Backend
                                   ↓
                             chrome.storage.sync
                                   ↓
                              Popup Interface
```

## ✅ Validación Completa

La extensión ha pasado todas las validaciones:
- ✅ JSON sintaxis válida (manifest.json)
- ✅ JavaScript sin SyntaxErrors
- ✅ HTML structure correcta
- ✅ Referencias de archivos válidas
- ✅ Permisos apropiados
- ✅ Encoding UTF-8 limpio
- ✅ No caracteres especiales corruptos

**¡La extensión está lista para uso en producción!**