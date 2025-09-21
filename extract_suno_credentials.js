/**
 * SCRIPT DE CONSOLA PARA EXTRAER CREDENCIALES DE SUNO
 * ====================================================
 * 
 * INSTRUCCIONES:
 * 1. Ve a https://suno.com y haz login
 * 2. Abre DevTools (F12)
 * 3. Ve a la pestaña "Console"
 * 4. Pega este script completo y presiona Enter
 * 5. Copia los valores que aparezcan
 */

console.clear();
console.log("🎵 EXTRACTOR DE CREDENCIALES SUNO - Son1k Auto-Renewal");
console.log("======================================================");
console.log("");

// Función principal de extracción
const extractSunoCredentials = function() {
    try {
        console.log("🔍 Buscando credenciales de Suno...");
        console.log("");
        
        // Método 1: Extraer de cookies del documento
        const documentCookies = document.cookie;
        console.log("📋 Cookies del documento encontradas");
        
        // Método 2: Extraer de localStorage
        const localStorageData = {};
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            const value = localStorage.getItem(key);
            localStorageData[key] = value;
        }
        
        // Método 3: Extraer de sessionStorage
        const sessionStorageData = {};
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            const value = sessionStorage.getItem(key);
            sessionStorageData[key] = value;
        }
        
        // Buscar session_id en diferentes ubicaciones
        let sessionId = null;
        let fullCookie = documentCookies;
        
        // Buscar en localStorage
        Object.keys(localStorageData).forEach(key => {
            const value = localStorageData[key];
            if (key.toLowerCase().includes('session') || 
                key.toLowerCase().includes('token') ||
                key.toLowerCase().includes('auth')) {
                console.log(`🔑 LocalStorage [${key}]:`, value.substring(0, 50) + "...");
                if (!sessionId && value.length > 10) {
                    sessionId = value;
                }
            }
        });
        
        // Buscar en sessionStorage
        Object.keys(sessionStorageData).forEach(key => {
            const value = sessionStorageData[key];
            if (key.toLowerCase().includes('session') || 
                key.toLowerCase().includes('token') ||
                key.toLowerCase().includes('auth')) {
                console.log(`🔑 SessionStorage [${key}]:`, value.substring(0, 50) + "...");
                if (!sessionId && value.length > 10) {
                    sessionId = value;
                }
            }
        });
        
        // Buscar en cookies específicas
        const cookieEntries = documentCookies.split(';');
        cookieEntries.forEach(cookie => {
            const [name, value] = cookie.trim().split('=');
            if (name && value && (
                name.toLowerCase().includes('session') ||
                name.toLowerCase().includes('token') ||
                name.toLowerCase().includes('auth') ||
                name.toLowerCase().includes('clerk')
            )) {
                console.log(`🍪 Cookie [${name}]:`, value.substring(0, 50) + "...");
                if (!sessionId && value.length > 10) {
                    sessionId = value;
                }
            }
        });
        
        // Intentar obtener token de la aplicación React/Next.js
        try {
            // Buscar en el estado global de React si está disponible
            if (window.React || window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
                console.log("⚛️ Aplicación React detectada, buscando en estado...");
            }
            
            // Buscar en objetos globales comunes
            const globals = ['__NEXT_DATA__', '__NUXT__', 'window.app', 'window.store'];
            globals.forEach(globalName => {
                try {
                    const globalObj = eval(globalName);
                    if (globalObj) {
                        console.log(`🌐 Objeto global ${globalName} encontrado`);
                    }
                } catch (e) {
                    // Ignorar errores
                }
            });
            
        } catch (e) {
            console.log("⚠️ No se pudo acceder al estado de la aplicación");
        }
        
        console.log("");
        console.log("✅ CREDENCIALES ENCONTRADAS:");
        console.log("============================");
        console.log("");
        
        // Mostrar SESSION_ID
        if (sessionId) {
            console.log("🔑 SESSION_ID encontrado:");
            console.log(`SUNO_SESSION_ID="${sessionId}"`);
        } else {
            console.log("❌ SESSION_ID no encontrado automáticamente");
            console.log("💡 Busca manualmente en las cookies por 'session' o 'token'");
        }
        
        console.log("");
        
        // Mostrar COOKIE completa
        console.log("🍪 COOKIE completa:");
        console.log(`SUNO_COOKIE="${fullCookie}"`);
        
        console.log("");
        console.log("📋 INSTRUCCIONES PARA USAR:");
        console.log("============================");
        console.log("1. Copia los valores de arriba");
        console.log("2. Ve a Railway Dashboard");
        console.log("3. En Variables de entorno, agrega:");
        console.log("   - SUNO_SESSION_ID con el valor del SESSION_ID");
        console.log("   - SUNO_COOKIE con el valor de la COOKIE completa");
        console.log("");
        console.log("⚠️ IMPORTANTE:");
        console.log("- Mantén estas credenciales seguras");
        console.log("- El sistema de auto-renovación las actualizará automáticamente");
        console.log("- Si no funcionan, ejecuta este script nuevamente");
        
        console.log("");
        console.log("🚀 Sistema Son1k con Auto-Renewal listo!");
        
        return {
            sessionId: sessionId,
            fullCookie: fullCookie,
            localStorage: localStorageData,
            sessionStorage: sessionStorageData
        };
        
    } catch (error) {
        console.error("❌ Error extrayendo credenciales:", error);
        console.log("");
        console.log("🔧 EXTRACCIÓN MANUAL:");
        console.log("===================");
        console.log("1. Ve a DevTools > Application > Cookies");
        console.log("2. Busca cookies con 'session', 'token' o 'auth'");
        console.log("3. Copia el valor completo");
        console.log("");
        console.log("O en DevTools > Application > Local Storage:");
        console.log("Busca claves relacionadas con autenticación");
    }
}

// Ejecutar extracción
const credentials = extractSunoCredentials();

// Función adicional para copiar al portapapeles
const copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log("✅ Copiado al portapapeles!");
    }).catch(() => {
        console.log("❌ No se pudo copiar automáticamente");
    });
}

// Función para copiar SESSION_ID
window.copySunoSessionId = () => {
    if (credentials.sessionId) {
        copyToClipboard(credentials.sessionId);
        console.log("📋 SESSION_ID copiado al portapapeles");
    } else {
        console.log("❌ SESSION_ID no disponible");
    }
};

// Función para copiar COOKIE completa
window.copySunoCookie = () => {
    copyToClipboard(credentials.fullCookie);
    console.log("📋 COOKIE completa copiada al portapapeles");
};

console.log("");
console.log("🛠️ FUNCIONES AUXILIARES:");
console.log("========================");
console.log("copySunoSessionId() - Copia SESSION_ID al portapapeles");
console.log("copySunoCookie() - Copia COOKIE completa al portapapeles");
console.log("");
console.log("💡 Ejecuta las funciones de arriba para copiar fácilmente");