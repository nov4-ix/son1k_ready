# 🔑 Guía para Extraer Credenciales de Suno

## 📋 Método Automático - Script de Consola

### **Paso 1: Ir a Suno y hacer login**
1. Ve a **https://suno.com**
2. Haz **login** con tu cuenta
3. Asegúrate de estar en la página principal (logged in)

### **Paso 2: Abrir DevTools**
1. Presiona **F12** (o Click derecho → Inspeccionar)
2. Ve a la pestaña **"Console"**
3. Asegúrate de que no hay errores en la consola

### **Paso 3: Ejecutar Script de Extracción**
1. Abre el archivo: `extract_suno_credentials.js`
2. **Copia TODO el contenido** del script
3. **Pega** en la consola del navegador
4. Presiona **Enter**

### **Paso 4: Copiar Credenciales**
El script mostrará algo como:
```
✅ CREDENCIALES ENCONTRADAS:
============================

🔑 SESSION_ID encontrado:
SUNO_SESSION_ID="sess_2x...long_token_here"

🍪 COOKIE completa:
SUNO_COOKIE="__clerk_session=sess_2x...; _ga=GA1.1...; other_cookies_here"
```

### **Paso 5: Usar Funciones de Copia**
```javascript
// Ejecuta en la consola para copiar fácilmente:
copySunoSessionId()    // Copia SESSION_ID al portapapeles
copySunoCookie()       // Copia COOKIE completa al portapapeles
```

## 🔧 Método Manual (Fallback)

### **Si el script automático no funciona:**

#### **Opción A: Extraer de Cookies**
1. DevTools → **Application** → **Cookies** → `https://suno.com`
2. Busca cookies que contengan:
   - `__clerk_session` (más común)
   - Cualquier cookie con `session`, `token`, o `auth`
3. Copia el **valor completo**

#### **Opción B: Extraer de Local Storage**
1. DevTools → **Application** → **Storage** → **Local Storage** → `https://suno.com`
2. Busca claves como:
   - `clerk-session`
   - `auth-token`
   - `user-session`
   - Cualquier clave con `session` o `token`

#### **Opción C: Network Tab**
1. DevTools → **Network**
2. Recarga la página (F5)
3. Busca requests a `suno.com` o `clerk.com`
4. Ve a **Headers** → **Request Headers**
5. Busca `Cookie:` y copia el valor completo

## 🚀 Configurar en Railway

### **Variables a configurar:**
```bash
# En Railway Dashboard → Variables:
SUNO_SESSION_ID = "sess_2x...tu_session_id_aqui"
SUNO_COOKIE = "__clerk_session=sess_2x...; _ga=GA1.1...; todos_los_cookies"
```

### **Variables adicionales recomendadas:**
```bash
OLLAMA_URL = "https://19f27f4b1376.ngrok-free.app"
PORT = "8000"
```

## ⚠️ Importantes

### **Seguridad:**
- **NO compartas** estas credenciales
- Son específicas de tu cuenta de Suno
- Cambian periódicamente (por eso el auto-renewal)

### **Validación:**
- Las credenciales deben empezar con `sess_` generalmente
- La cookie debe contener múltiples valores separados por `;`
- Si no funcionan, vuelve a extraerlas

### **Auto-Renovación:**
- Una vez configuradas, el sistema las renovará automáticamente
- El sistema detecta cuando expiran y busca nuevas
- Recibirás notificaciones si requiere intervención manual

## 🎯 Siguiente Paso

Una vez que tengas las credenciales:
1. Ve a **Railway Dashboard**
2. Configura las **variables de entorno**
3. El sistema se **auto-desplegará**
4. ¡**Auto-renovación 24/7 activa!** ✅

## 🆘 Solución de Problemas

### **Si el script no encuentra nada:**
- Asegúrate de estar **logged in** en Suno
- Recarga la página y vuelve a intentar
- Usa el método manual

### **Si las credenciales no funcionan:**
- Verifica que las copiaste **completas**
- Asegúrate de que no hay **espacios extra**
- Vuelve a extraerlas (pueden haber expirado)

### **Si necesitas ayuda:**
- Ejecuta el script nuevamente
- El sistema de auto-renovación intentará renovarlas automáticamente
- Revisa los logs en Railway para diagnóstico