# 🚨 REINSTALACIÓN COMPLETA DE EXTENSION

## ✅ **TU CUENTA ESTÁ LISTA**
```
Email: nov4-ix@son1kvers3.com
Password: music123
```

## 🔄 **PASOS PARA REINSTALAR (OBLIGATORIO)**

### **PASO 1: Eliminar Extensión Actual**
1. Ve a `chrome://extensions/`
2. Busca "Son1k ↔ Suno Bridge"
3. Click en **"Eliminar"** o **"Remove"**
4. Confirma la eliminación

### **PASO 2: Reinstalar Extensión**
1. En `chrome://extensions/` asegúrate que **"Modo desarrollador"** esté activado (esquina superior derecha)
2. Click **"Cargar extensión sin empaquetar"** (Load unpacked)
3. Navega a la carpeta: `/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2/extension/`
4. Selecciona la carpeta `extension/` y click **"Seleccionar"**

### **PASO 3: Verificar Instalación**
1. Debes ver **"Son1k ↔ Suno Bridge"** en la lista
2. Debe mostrar **"popup_simple.html"** como popup
3. **NO** debe mostrar errores

### **PASO 4: Configurar Conexión**
1. **Click en el icono** de la extensión en la toolbar
2. **Verificar URL**: Debe mostrar `https://2a73bb633652.ngrok-free.app`
3. **Click "🔍 Probar Conexión"** → Debe mostrar "✅ Conexión exitosa!"
4. **Click "🔄 Conectar"** → Debe mostrar "✅ Conectado correctamente!"
5. **Indicador debe cambiar a VERDE** 🟢

### **PASO 5: Test en Frontend**
1. Ve a `https://2a73bb633652.ngrok-free.app`
2. Click **"Login"**
3. Usar credenciales:
   - Email: `nov4-ix@son1kvers3.com`
   - Password: `music123`
4. Debe loguearte correctamente

---

## ✅ **SEÑALES DE ÉXITO**

### **Extension:**
- ✅ Popup se abre sin errores
- ✅ Indicador VERDE 🟢
- ✅ Status: "✅ Conectado correctamente!"

### **Frontend:**
- ✅ Login exitoso con tu cuenta
- ✅ Acceso a secciones protegidas
- ✅ No se muestra modal de login

### **Backend (verificación):**
```bash
curl -H "ngrok-skip-browser-warning: any" https://2a73bb633652.ngrok-free.app/api/health
# Debe responder: {"ok":true}
```

---

## 🚨 **SI ALGO FALLA:**

### **Extension sigue roja:**
1. Reinicia Chrome completamente
2. Ve a `chrome://extensions/`
3. Click en **"🔄 Reload"** en la extensión Son1k
4. Abre el popup nuevamente

### **Error de conexión:**
1. Verifica que el backend esté corriendo (debe estar)
2. En popup, cambia URL a: `https://2a73bb633652.ngrok-free.app`
3. Click "Probar Conexión" nuevamente

### **Login falla:**
```
Email: nov4-ix@son1kvers3.com
Password: music123
```

---

## 📞 **RESULTADO ESPERADO:**

Después de estos pasos:
1. **Extension**: Estado VERDE y funcionando
2. **Login**: Exitoso con tu cuenta
3. **Backend**: Recibiendo conexiones
4. **Frontend**: Completamente accesible

**LA REINSTALACIÓN ES NECESARIA porque la extensión actual está usando configuración incorrecta. Una vez reinstalada con el nuevo popup simple, debe funcionar inmediatamente.**