# 🚀 INSTRUCCIONES SÚPER SIMPLES - Son1k ↔ Suno Bridge

## ✅ TODO ESTÁ VERIFICADO Y LISTO

**📋 SOLO SIGUE ESTOS 4 PASOS:**

---

### 1️⃣ INICIAR BACKEND
```bash
cd "/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
python3 run_local.py
```
**✅ Debes ver:** `INFO: Uvicorn running on http://0.0.0.0:8000`

---

### 2️⃣ CARGAR EXTENSIÓN EN CHROME
1. Ir a: `chrome://extensions/`
2. Activar "**Modo de desarrollador**"
3. Clic "**Cargar extensión sin empaquetar**"
4. Seleccionar carpeta: `/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2/extension`

**✅ Debes ver:** Extensión "Son1k ↔ Suno Bridge (PoC)" cargada sin errores

---

### 3️⃣ CONFIGURAR EXTENSIÓN
1. Clic en ícono de extensión en barra Chrome
2. En "Backend URL" escribir: `localhost:8000`
3. Clic "**Guardar**" → Debe mostrar "Guardado ✔"
4. Clic "**Probar**" → Debe mostrar "Backend conectado ✅"

**✅ Automáticamente se abre:** `https://suno.com/create`

---

### 4️⃣ USAR EN SUNO
1. En suno.com/create escribir un prompt musical
2. Buscar botón flotante "**Send to Son1k**" (esquina inferior derecha)
3. Clic en el botón → Debe mostrar "Enviado a Son1k ✅"

**✅ En la terminal del backend verás:** logs de procesamiento

---

## 🆘 SI ALGO NO FUNCIONA

### ❌ Extensión dice "URL no válido"
**SOLUCIÓN:** Usar exactamente `localhost:8000` o `http://localhost:8000`

### ❌ "No se pudo conectar al backend"
**VERIFICAR:** 
```bash
curl http://localhost:8000/api/health
```
**Debe responder:** `{"ok":true}`

### ❌ Botón no aparece en Suno
**SOLUCIÓN:** Refrescar página suno.com/create

### ❌ Backend no inicia
**VERIFICAR:**
```bash
cd "/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
./verificar_antes_de_usar.sh
```

---

## 📞 VERIFICACIÓN RÁPIDA

**Antes de empezar, ejecutar:**
```bash
cd "/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
./verificar_antes_de_usar.sh
```

**Debe mostrar:** `🎉 TODO PERFECTO - LISTO PARA USAR`

---

## 🎯 FLUJO COMPLETO

```
Backend corriendo → Extensión cargada → URL configurada → Suno.com → Botón funciona ✅
```

**¡ESO ES TODO! 🚀**