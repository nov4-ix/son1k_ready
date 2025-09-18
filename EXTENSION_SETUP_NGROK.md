# 🔧 Son1kVers3 Chrome Extension - Configuración para Ngrok

## 🚨 PROBLEMA IDENTIFICADO
La extensión muestra **estado rojo** porque está configurada para `https://son1kvers3.com` pero el backend está ejecutándose en ngrok.

## ✅ SOLUCIÓN PASO A PASO

### 📋 **PASO 1: Obtener URL de Ngrok**
La URL actual de ngrok es: **https://2a73bb633652.ngrok-free.app**

### 🔧 **PASO 2: Configurar la Extensión**

1. **Abrir la extensión**:
   - Click en el ícono de Son1k en la barra de herramientas de Chrome
   - Verás el popup con estado "rojo" (disconnected)

2. **Cambiar Backend URL**:
   - En el campo "Backend URL" reemplazar el contenido con:
   ```
   https://2a73bb633652.ngrok-free.app
   ```

3. **Guardar configuración**:
   - Click en el botón "**Guardar**"
   - La extensión almacenará la nueva URL

4. **Probar conexión**:
   - Click en el botón "**Probar**"
   - Debería mostrar "✅ Conexión exitosa"

5. **Conectar worker**:
   - Click en el botón "**🔄 Conectar**"
   - El indicador debería cambiar a **verde**

6. **Iniciar auto-worker** (opcional):
   - En la sección "Worker Automático"
   - Click en "**🤖 Iniciar**"
   - El worker comenzará a buscar trabajos automáticamente

---

## 🔍 **VERIFICACIÓN DE ESTADO**

### ✅ **Estado CORRECTO (Verde)**:
- **Indicador**: 🟢 Verde en "Son1k ↔ Suno Bridge"
- **Status**: "Conectado" o "Connected"
- **Worker**: 🟢 Verde en "Worker Automático" (si está activado)

### ❌ **Estado INCORRECTO (Rojo)**:
- **Indicador**: 🔴 Rojo en "Son1k ↔ Suno Bridge"  
- **Status**: "Desconectado" o error de conexión
- **Causa**: URL incorrecta o backend no disponible

---

## 🧪 **TESTING COMPLETO**

### **1. Test de Conexión**:
```
✅ Esperado: "Conexión exitosa"
❌ Error: Verificar URL y que backend esté corriendo
```

### **2. Test de Heartbeat**:
```
✅ Esperado: Worker ID asignado y heartbeat funcionando
❌ Error: Verificar endpoints del worker
```

### **3. Test de Jobs**:
```
✅ Esperado: "No hay trabajos disponibles" (normal si no hay queue)
❌ Error: Endpoint /api/jobs/pending no responde
```

---

## 🔧 **TROUBLESHOOTING**

### **Problema: "Connection failed"**
**Solución**:
1. Verificar que ngrok esté ejecutándose
2. Comprobar que la URL sea correcta
3. Probar la URL manualmente en el navegador

### **Problema: "CORS error"**
**Solución**:
1. El backend tiene CORS configurado para "*"
2. No debería haber problemas de CORS
3. Verificar en DevTools (F12) si hay errores

### **Problema: "Worker no inicia"**
**Solución**:
1. Primero establecer conexión exitosa
2. Luego iniciar el worker
3. Verificar logs en background script (chrome://extensions)

---

## 📊 **ENDPOINTS VERIFICADOS**

### ✅ **Funcionando correctamente**:
- `GET /api/health` → `{"ok": true}`
- `POST /api/worker/heartbeat` → `{"ok": true, "message": "Heartbeat received"}`
- `GET /api/jobs/pending` → Array de trabajos o `[]` si no hay

### 🔗 **URLs Completas**:
- **Health**: https://2a73bb633652.ngrok-free.app/api/health
- **Heartbeat**: https://2a73bb633652.ngrok-free.app/api/worker/heartbeat
- **Jobs**: https://2a73bb633652.ngrok-free.app/api/jobs/pending?worker_id=test

---

## 🎯 **RESULTADO ESPERADO**

Después de seguir estos pasos:

1. **🟢 Extensión en verde**: Indicador conectado
2. **🤖 Worker activo**: Buscando trabajos automáticamente  
3. **📊 Stats visibles**: Trabajos completados/fallidos
4. **🔗 Backend conectado**: Comunicación exitosa

---

## ⚡ **CONFIGURACIÓN RÁPIDA**

**Para configurar rápidamente**:

1. **Copiar URL**: `https://2a73bb633652.ngrok-free.app`
2. **Pegar en extensión** → Campo "Backend URL"
3. **Guardar** → **Probar** → **Conectar** → **✅ Verde**

**¡La extensión debería pasar de rojo a verde inmediatamente!**

---

## 📱 **MONITOREO CONTINUO**

La extensión mostrará:
- **Estado de conexión** en tiempo real
- **Estadísticas del worker** (trabajos procesados)
- **Logs de actividad** en background script
- **Heartbeat automático** cada 30 segundos

**🎉 ¡Con esto la extensión debería estar completamente funcional!**