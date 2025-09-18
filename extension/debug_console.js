// 🔧 SCRIPT DE DEBUG PARA CONSOLE DEL POPUP
// Pega este código en la console del popup (F12 → Console)

console.log('🔍 INICIANDO DEBUG DE EXTENSIÓN SON1K');
console.log('='.repeat(50));

const API_URL = 'https://2a73bb633652.ngrok-free.app';

// Test 1: Verificar Chrome APIs
console.log('\n1️⃣ Testing Chrome APIs...');
console.log('chrome:', typeof chrome);
console.log('chrome.storage:', typeof chrome?.storage);
console.log('chrome.runtime:', typeof chrome?.runtime);

// Test 2: Verificar conexión directa
console.log('\n2️⃣ Testing direct connection...');
fetch(API_URL + '/api/health', {
  headers: { 'ngrok-skip-browser-warning': 'any' }
})
.then(r => r.json())
.then(d => {
  console.log('✅ Direct connection OK:', d);
})
.catch(e => {
  console.error('❌ Direct connection FAILED:', e);
});

// Test 3: Verificar storage
console.log('\n3️⃣ Testing storage...');
if (chrome?.storage) {
  chrome.storage.sync.get(null, (data) => {
    console.log('📦 Storage data:', data);
  });
} else {
  console.error('❌ Chrome storage not available');
}

// Test 4: Verificar background script
console.log('\n4️⃣ Testing background script...');
if (chrome?.runtime) {
  chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
    console.log('📡 Background response:', response);
    if (chrome.runtime.lastError) {
      console.error('Background error:', chrome.runtime.lastError);
    }
  });
} else {
  console.error('❌ Chrome runtime not available');
}

// Función helper para test manual
window.manualTest = function() {
  console.log('\n🧪 MANUAL TEST INICIADO');
  
  fetch(API_URL + '/api/health', {
    headers: { 'ngrok-skip-browser-warning': 'any' }
  })
  .then(response => {
    console.log('Response status:', response.status);
    console.log('Response headers:', [...response.headers]);
    return response.json();
  })
  .then(data => {
    console.log('✅ MANUAL TEST SUCCESS:', data);
    alert('✅ Conexión manual exitosa: ' + JSON.stringify(data));
  })
  .catch(error => {
    console.error('❌ MANUAL TEST FAILED:', error);
    alert('❌ Error en test manual: ' + error.message);
  });
};

// Función para forzar conexión
window.forceConnection = function() {
  console.log('\n🚀 FORZANDO CONEXIÓN...');
  
  // 1. Guardar en storage
  chrome.storage.sync.set({ apiUrl: API_URL }, () => {
    console.log('✅ URL guardada en storage');
    
    // 2. Notificar background
    chrome.runtime.sendMessage({
      type: 'UPDATE_API_URL',
      apiUrl: API_URL
    }, (response) => {
      console.log('📡 Background notificado:', response);
      
      // 3. Test final
      window.manualTest();
    });
  });
};

console.log('\n💡 COMANDOS DISPONIBLES:');
console.log('- window.manualTest() - Test directo de conexión');
console.log('- window.forceConnection() - Forzar conexión completa');
console.log('\n🔧 Ejecuta cualquiera de estos comandos para probar');