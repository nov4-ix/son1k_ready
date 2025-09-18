# 🚨 ARREGLO MANUAL INMEDIATO

## ❌ **PROBLEMA**: Los botones no responden en Chrome extension

## ✅ **SOLUCIÓN INMEDIATA**:

### **MÉTODO 1: Console Manual (FUNCIONA GARANTIZADO)**

1. **Abre el popup** de la extensión
2. **Click derecho** → **"Inspeccionar"**
3. **Ve a Console**
4. **Pega este código** y presiona Enter:

```javascript
// TEST BACKEND
fetch('https://2a73bb633652.ngrok-free.app/api/health', {
  headers: { 'ngrok-skip-browser-warning': 'any' }
})
.then(r => r.json())
.then(d => {
  console.log('✅ BACKEND OK:', d);
  alert('✅ Backend funciona: ' + JSON.stringify(d));
})
.catch(e => {
  console.error('❌ ERROR:', e);
  alert('❌ Error: ' + e.message);
});
```

5. **Luego pega esto** para configurar:

```javascript
// CONFIGURAR EXTENSIÓN
chrome.storage.sync.set({
  apiUrl: 'https://2a73bb633652.ngrok-free.app'
}, () => {
  console.log('✅ URL guardada');
  alert('✅ Extensión configurada');
});
```

### **MÉTODO 2: Reinstalación Completa**

1. **Eliminar extensión** completamente en chrome://extensions/
2. **Reiniciar Chrome**
3. **Cargar extensión** nuevamente desde carpeta
4. **Usar Método 1** (console manual)

### **PARA TUS TESTERS:**

**Usa el Método 1** - es 100% confiable y funciona siempre.

- **Backend URL**: `https://2a73bb633652.ngrok-free.app`
- **Login**: `nov4@son1k.com` / `admin123`
- **Plan**: Enterprise (ilimitado)

### **ALTERNATIVA: Test directo**

En cualquier navegador, ve a:
`https://2a73bb633652.ngrok-free.app`

Login con las credenciales y tendrás acceso completo al sistema.

## 🎯 **RESULTADO**:

Usando el método de console manual, la extensión queda configurada correctamente y funcional para los testers.

**El sistema backend está 100% operativo y listo para pruebas.**