# 🚨 SOLUCIÓN RÁPIDA - Frontend y Extensión

## ❌ PROBLEMAS ACTUALES:
1. Navegador muestra código JavaScript en lugar de HTML
2. Extensión dice "no se puede conectar al backend"

## ✅ SOLUCIONES INMEDIATAS:

### 🔧 PASO 1: LIMPIAR CACHÉ DEL NAVEGADOR

**Opción A - Recarga Fuerte:**
1. Ir a `http://localhost:8000`
2. Presionar `Cmd + Shift + R` (Mac) o `Ctrl + Shift + R` (Windows)
3. O presionar `F5` varias veces

**Opción B - Limpiar Caché:**
1. En Chrome: `Cmd + Shift + Delete`
2. Seleccionar "Últimos 1 hora"
3. Marcar "Imágenes y archivos en caché"
4. Clic "Borrar datos"

**Opción C - Ventana Incógnita:**
1. Abrir ventana incógnita: `Cmd + Shift + N`
2. Ir a `http://localhost:8000`

### 🔧 PASO 2: CONFIGURAR EXTENSIÓN CORRECTAMENTE

1. **Verificar backend corriendo:**
   ```bash
   curl http://localhost:8000/api/health
   # Debe responder: {"ok":true}
   ```

2. **Abrir popup extensión:**
   - Clic en ícono de extensión

3. **Configurar URL exacta:**
   - Escribir: `http://localhost:8000` (CON http://)
   - Clic "Guardar"

4. **Probar conexión:**
   - Clic "Probar"
   - Debe mostrar: "Backend conectado ✅"

### 🔧 PASO 3: VERIFICACIÓN MANUAL

**Si aún no funciona, probar manualmente:**

```bash
# Terminal 1: Verificar backend
curl http://localhost:8000/api/health

# Terminal 2: Probar endpoint songs
curl -X POST "http://localhost:8000/api/songs/create" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "mode": "original"}'
```

### 🔧 PASO 4: EXTENSIÓN - DEBUG

1. **Revisar errores en extensión:**
   - Ir a `chrome://extensions/`
   - Buscar "Son1k ↔ Suno Bridge"
   - Clic "Errores" si hay alguno

2. **Revisar Console del popup:**
   - Abrir popup extensión
   - Clic derecho → "Inspeccionar"
   - Ver pestaña "Console" por errores

### 🔧 PASO 5: SI NADA FUNCIONA - REINICIO COMPLETO

```bash
# 1. Detener backend (Ctrl+C en terminal)
# 2. Reiniciar todo:
cd "/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
redis-cli ping  # Verificar Redis
python3 run_local.py  # Reiniciar backend
```

## 🎯 VERIFICACIÓN FINAL

**Cuando todo funcione correctamente:**

1. **Frontend:** `http://localhost:8000` → Dashboard HTML limpio
2. **Backend Health:** `curl http://localhost:8000/api/health` → `{"ok":true}`
3. **Extensión:** Popup → "Backend conectado ✅"
4. **Suno:** `suno.com/create` → Botón "Send to Son1k" visible

## 🆘 SI PERSISTEN PROBLEMAS

**URL exactas para probar:**
- Backend: `http://localhost:8000/api/health`
- Frontend: `http://localhost:8000`
- Extensión URL: `http://localhost:8000` (con http://)

**Comandos de verificación:**
```bash
# Ver proceso backend
ps aux | grep python3

# Ver logs en tiempo real
tail -f logs.txt  # Si existe
```

## 💡 TIPS IMPORTANTES:

1. **Usar http:// completo** en extensión
2. **Limpiar caché** del navegador primero
3. **Ventana incógnita** para test limpio
4. **Verificar backend** con curl antes de usar extensión