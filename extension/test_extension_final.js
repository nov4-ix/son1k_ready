// Test completo de la extensión Son1k
console.log('🧪 Son1k Extension - Test Final');

const NGROK_URL = 'https://2a73bb633652.ngrok-free.app';

// Función principal de testing
async function runCompleteTest() {
  console.log('='.repeat(50));
  console.log('🔍 INICIANDO TEST COMPLETO DE SON1K EXTENSION');
  console.log('='.repeat(50));
  
  const results = {
    backendHealth: false,
    authTest: false,
    extensionLoaded: false,
    backgroundScript: false,
    popupConnection: false,
    overallStatus: 'FAILED'
  };
  
  try {
    // 1. Test Backend Health
    console.log('\n1️⃣ Testing Backend Health...');
    results.backendHealth = await testBackendHealth();
    
    // 2. Test Authentication
    console.log('\n2️⃣ Testing Authentication...');
    results.authTest = await testAuthentication();
    
    // 3. Test Extension Loading
    console.log('\n3️⃣ Testing Extension Loading...');
    results.extensionLoaded = testExtensionLoaded();
    
    // 4. Test Background Script
    console.log('\n4️⃣ Testing Background Script...');
    results.backgroundScript = await testBackgroundScript();
    
    // 5. Test Popup Connection
    console.log('\n5️⃣ Testing Popup Connection...');
    results.popupConnection = await testPopupConnection();
    
    // 6. Overall Status
    const allPassed = Object.values(results).slice(0, -1).every(test => test);
    results.overallStatus = allPassed ? 'PASSED' : 'FAILED';
    
    console.log('\n' + '='.repeat(50));
    console.log('📊 RESULTADOS FINALES');
    console.log('='.repeat(50));
    
    Object.entries(results).forEach(([key, value]) => {
      const icon = value === true || value === 'PASSED' ? '✅' : '❌';
      console.log(`${icon} ${key}: ${value}`);
    });
    
    console.log('\n' + (results.overallStatus === 'PASSED' ? 
      '🎉 TODOS LOS TESTS PASARON - EXTENSIÓN FUNCIONAL' : 
      '🚨 ALGUNOS TESTS FALLARON - REVISAR CONFIGURACIÓN'
    ));
    
    if (results.overallStatus === 'FAILED') {
      console.log('\n🔧 TROUBLESHOOTING:');
      if (!results.backendHealth) console.log('- Verificar que el backend esté corriendo en ngrok');
      if (!results.authTest) console.log('- Verificar endpoints de autenticación');
      if (!results.extensionLoaded) console.log('- Recargar la extensión en chrome://extensions/');
      if (!results.backgroundScript) console.log('- Revisar console del background script');
      if (!results.popupConnection) console.log('- Configurar URL correcta en popup');
    }
    
    return results;
    
  } catch (error) {
    console.error('❌ Error en test completo:', error);
    return results;
  }
}

// Test 1: Backend Health
async function testBackendHealth() {
  try {
    const response = await fetch(`${NGROK_URL}/api/health`, {
      method: 'GET',
      headers: { 'ngrok-skip-browser-warning': 'any' }
    });
    
    if (response.ok) {
      const data = await response.json();
      const healthy = data.ok === true;
      console.log(healthy ? '✅ Backend healthy' : '❌ Backend unhealthy');
      return healthy;
    } else {
      console.log(`❌ Backend response error: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log(`❌ Backend connection error: ${error.message}`);
    return false;
  }
}

// Test 2: Authentication
async function testAuthentication() {
  try {
    // Test login with admin account
    const response = await fetch(`${NGROK_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'any'
      },
      body: JSON.stringify({
        email: 'admin@son1k.com',
        password: 'admin123'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      const hasToken = data.access_token && data.user;
      console.log(hasToken ? '✅ Authentication working' : '❌ Authentication failed');
      return hasToken;
    } else {
      console.log(`❌ Auth response error: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log(`❌ Auth connection error: ${error.message}`);
    return false;
  }
}

// Test 3: Extension Loaded
function testExtensionLoaded() {
  try {
    const hasChrome = typeof chrome !== 'undefined';
    const hasRuntime = hasChrome && chrome.runtime && chrome.runtime.sendMessage;
    const hasStorage = hasChrome && chrome.storage && chrome.storage.sync;
    
    const loaded = hasChrome && hasRuntime && hasStorage;
    console.log(loaded ? '✅ Extension APIs available' : '❌ Extension APIs missing');
    
    if (!loaded) {
      console.log(`Chrome: ${hasChrome}, Runtime: ${hasRuntime}, Storage: ${hasStorage}`);
    }
    
    return loaded;
  } catch (error) {
    console.log(`❌ Extension loading error: ${error.message}`);
    return false;
  }
}

// Test 4: Background Script
async function testBackgroundScript() {
  try {
    if (typeof chrome === 'undefined' || !chrome.runtime) {
      console.log('❌ Chrome APIs not available');
      return false;
    }
    
    const response = await new Promise((resolve) => {
      chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
        resolve(response);
      });
    });
    
    if (response && response.apiUrl) {
      const connected = response.connected;
      console.log(connected ? 
        `✅ Background script connected to ${response.apiUrl}` : 
        `❌ Background script not connected to ${response.apiUrl}`
      );
      
      if (response.workerStatus) {
        console.log(`   Worker status: ${response.workerStatus}`);
      }
      
      return connected;
    } else {
      console.log('❌ Background script not responding');
      return false;
    }
  } catch (error) {
    console.log(`❌ Background script error: ${error.message}`);
    return false;
  }
}

// Test 5: Popup Connection
async function testPopupConnection() {
  try {
    // Simular test de conexión desde popup
    const response = await fetch(`${NGROK_URL}/api/health`, {
      method: 'GET',
      headers: { 'ngrok-skip-browser-warning': 'any' }
    });
    
    if (response.ok) {
      const data = await response.json();
      const connected = data.ok === true;
      console.log(connected ? '✅ Popup can connect to backend' : '❌ Popup cannot connect');
      return connected;
    } else {
      console.log(`❌ Popup connection error: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log(`❌ Popup connection error: ${error.message}`);
    return false;
  }
}

// Ejecutar test si estamos en contexto correcto
if (typeof window !== 'undefined') {
  // En popup o content script
  window.testSon1kExtension = runCompleteTest;
  console.log('🧪 Test cargado. Ejecuta: window.testSon1kExtension()');
} else {
  // En background script
  self.testSon1kExtension = runCompleteTest;
  console.log('🧪 Test cargado. Ejecuta: self.testSon1kExtension()');
}

// Función helper para usar en console
function quickTest() {
  console.log('🚀 QUICK TEST SON1K');
  console.log('Backend URL:', NGROK_URL);
  
  fetch(`${NGROK_URL}/api/health`, {
    headers: { 'ngrok-skip-browser-warning': 'any' }
  })
  .then(r => r.json())
  .then(d => console.log('✅ Backend:', d))
  .catch(e => console.log('❌ Backend error:', e));
  
  if (typeof chrome !== 'undefined' && chrome.runtime) {
    chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
      console.log('Background script:', response || 'No response');
    });
  }
}

window.quickTest = quickTest;
console.log('🔧 Quick test disponible: window.quickTest()');