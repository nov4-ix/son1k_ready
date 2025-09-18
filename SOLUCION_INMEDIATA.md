# 🚨 SOLUCIÓN INMEDIATA - 2 Problemas

## ❌ PROBLEMA 1: VEO CÓDIGO EN EL NAVEGADOR

**SOLUCIÓN RÁPIDA:**

1. **Ir a** `http://localhost:8000`
2. **Presionar** `Cmd + Shift + R` (Mac) o `Ctrl + Shift + R` (Windows)  
3. **O** abrir ventana incógnita: `Cmd + Shift + N` y ir a `http://localhost:8000`

**Si aún no funciona:**
- Cerrar todas las pestañas de localhost:8000
- Abrir nueva pestaña
- Ir de nuevo a `http://localhost:8000`

---

## ❌ PROBLEMA 2: EXTENSIÓN NO CONECTA

**SOLUCIÓN RÁPIDA:**

1. **Abrir popup de extensión** (clic en ícono)

2. **En "Backend URL" escribir EXACTAMENTE:**
   ```
   http://localhost:8000
   ```
   ⚠️ **IMPORTANTE**: Incluir `http://` al inicio

3. **Clic "Guardar"** → Debe mostrar "Guardado ✔"

4. **Clic "Probar"** → Debe mostrar "Backend conectado ✅"

---

## ✅ VERIFICACIÓN RÁPIDA

**Backend funcionando?**
```bash
curl http://localhost:8000/api/health
# Debe responder: {"ok":true}
```

**Si no responde:**
- Verificar que veas en terminal: `INFO: Uvicorn running on http://0.0.0.0:8000`
- Si no, ejecutar: `python3 run_local.py`

---

## 🎯 RESULTADO ESPERADO

**Frontend:** Dashboard HTML limpio con indicadores de estado
**Extensión:** "Backend conectado ✅" en popup  
**Suno:** Botón "Send to Son1k" visible en suno.com/create

---

## 🆘 SI NADA FUNCIONA

**Reinicio completo:**
```bash
# 1. Detener backend (Ctrl+C)
# 2. Reiniciar:
cd "/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
python3 run_local.py
```

**En navegador:**
- Cerrar todas las pestañas localhost:8000
- Limpiar caché: `Cmd + Shift + Delete`
- Abrir nueva ventana incógnita
- Ir a `http://localhost:8000`

**En extensión:**
- URL: `http://localhost:8000` (con http://)
- Guardar → Probar