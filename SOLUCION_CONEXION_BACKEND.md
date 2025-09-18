# 🔧 SOLUCIÓN: "No se puede conectar al backend"

## ✅ PROBLEMA RESUELTO - BACKEND FUNCIONANDO

**El backend ahora está corriendo en segundo plano en tu terminal.**

---

## 🚀 PRÓXIMOS PASOS PARA LA EXTENSIÓN

### 1️⃣ VERIFICAR BACKEND (YA FUNCIONANDO)
El backend está corriendo y responde correctamente:
- ✅ Health endpoint: `http://localhost:8000/api/health` → `{"ok":true}`
- ✅ Create endpoint: `http://localhost:8000/api/songs/create` → funcionando
- ✅ Celery worker: procesando tareas correctamente

### 2️⃣ CONFIGURAR EXTENSIÓN AHORA

**Ahora que el backend funciona, configura la extensión:**

1. **Abrir popup de extensión:**
   - Clic en ícono de extensión en Chrome

2. **Configurar URL correctamente:**
   - En "Backend URL" escribir: `localhost:8000`
   - Clic "**Guardar**" → Debe mostrar "Guardado ✔"

3. **Probar conexión:**
   - Clic "**Probar**" → Debe mostrar "Backend conectado ✅"
   - Si funciona, automáticamente abre `suno.com/create`

### 3️⃣ USAR EN SUNO

1. **Ir a Suno (si no se abrió automáticamente):**
   - Navegar a: `https://suno.com/create`

2. **Buscar el botón:**
   - Debe aparecer botón flotante "**Send to Son1k**" (esquina inferior derecha)

3. **Probar funcionalidad:**
   - Escribir prompt musical en Suno
   - Clic "Send to Son1k"
   - Debe mostrar: "Enviado a Son1k ✅"

---

## 🔍 VERIFICACIONES ACTUALES

### ✅ Backend Status
```bash
# Health check
curl http://localhost:8000/api/health
# Respuesta: {"ok":true}

# Test song creation
curl -X POST "http://localhost:8000/api/songs/create" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test song", "mode": "original"}'
# Respuesta: {"ok":true,"job_id":"..."}
```

### ✅ Servicios Activos
- **FastAPI Server**: ✅ Corriendo en puerto 8000
- **Celery Worker**: ✅ Procesando tareas
- **Redis**: ✅ Conectado y funcionando
- **Frontend**: ✅ Sirviendo en localhost:8000

---

## 🆘 SI AÚN NO SE CONECTA

### Problema 1: Extensión dice "URL inválida"
**SOLUCIÓN:**
- Usar exactamente: `localhost:8000`
- O alternativamente: `http://localhost:8000`

### Problema 2: "No se pudo conectar"
**VERIFICAR:**
1. **Backend corriendo?**
   ```bash
   curl http://localhost:8000/api/health
   ```
   Debe responder: `{"ok":true}`

2. **URL correcta en extensión?**
   - Debe ser: `localhost:8000` (sin espacios extra)

3. **CORS habilitado?**
   - ✅ Ya configurado en el backend

### Problema 3: Botón no aparece en Suno
**SOLUCIÓN:**
1. Refrescar página `suno.com/create`
2. Abrir DevTools (F12) → Console
3. Buscar errores de la extensión

---

## 🎯 ESTADO ACTUAL

```
✅ Backend: Corriendo y funcionando
✅ API Endpoints: Respondiendo correctamente  
✅ Celery Worker: Procesando tareas
✅ Redis: Conectado
✅ Extensión: Lista para configurar
```

**🚀 EL SISTEMA ESTÁ OPERACIONAL - SOLO FALTA CONFIGURAR LA EXTENSIÓN**

---

## 📞 COMANDOS DE VERIFICACIÓN RÁPIDA

```bash
# Verificar backend
curl http://localhost:8000/api/health

# Ver logs del backend
# (Ya visible en tu terminal donde corre python3 run_local.py)

# Verificar Redis
redis-cli ping
```

**💡 El backend seguirá corriendo mientras tengas la terminal abierta. Cuando cierres la terminal, tendrás que volver a ejecutar `python3 run_local.py`**