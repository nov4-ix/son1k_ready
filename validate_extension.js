// Validate Extension - Son1k Chrome Extension Validator
// Ejecutar este script en DevTools de Chrome para validar la extensión

console.log('🔍 Son1k Extension Validator - Starting...');

// Configuración
const NGROK_URL = 'https://2a73bb633652.ngrok-free.app';
const TEST_WORKER_ID = 'validator-' + Math.random().toString(36).substr(2, 9);

// Tests a ejecutar
const tests = [
  { name: 'Health Check', endpoint: '/api/health', method: 'GET' },
  { name: 'Worker Heartbeat', endpoint: '/api/worker/heartbeat', method: 'POST', body: {
    worker_id: TEST_WORKER_ID,
    status: 'online',
    version: '2.0.0'
  }},
  { name: 'Pending Jobs', endpoint: `/api/jobs/pending?worker_id=${TEST_WORKER_ID}`, method: 'GET' }
];

// Función para ejecutar test
async function runTest(test) {
  const startTime = Date.now();
  
  try {
    const options = {
      method: test.method,
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'any'
      }
    };
    
    if (test.body) {
      options.body = JSON.stringify(test.body);
    }
    
    const response = await fetch(NGROK_URL + test.endpoint, options);
    const duration = Date.now() - startTime;
    const data = await response.json();
    
    const result = {
      name: test.name,
      status: response.ok ? 'PASS' : 'FAIL',
      httpStatus: response.status,
      duration: `${duration}ms`,
      response: data
    };
    
    console.log(`${result.status === 'PASS' ? '✅' : '❌'} ${result.name}:`, result);
    return result;
    
  } catch (error) {
    const result = {
      name: test.name,
      status: 'ERROR',
      error: error.message,
      duration: `${Date.now() - startTime}ms`
    };
    
    console.log(`❌ ${result.name}:`, result);
    return result;
  }
}

// Función principal de validación
async function validateExtension() {
  console.log(`🚀 Testing against: ${NGROK_URL}`);
  console.log(`🆔 Test Worker ID: ${TEST_WORKER_ID}`);
  console.log('─'.repeat(60));
  
  const results = [];
  
  for (const test of tests) {
    const result = await runTest(test);
    results.push(result);
    
    // Esperar un poco entre tests
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  console.log('─'.repeat(60));
  console.log('📊 SUMMARY:');
  
  const passed = results.filter(r => r.status === 'PASS').length;
  const failed = results.filter(r => r.status === 'FAIL').length;
  const errors = results.filter(r => r.status === 'ERROR').length;
  
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  console.log(`🔥 Errors: ${errors}`);
  
  if (passed === tests.length) {
    console.log('🎉 ALL TESTS PASSED! Extension should work correctly.');
    console.log('');
    console.log('📋 NEXT STEPS:');
    console.log(`1. Open Chrome extension popup`);
    console.log(`2. Set Backend URL to: ${NGROK_URL}`);
    console.log(`3. Click "Guardar" then "Probar"`);
    console.log(`4. Click "Conectar" to establish connection`);
    console.log(`5. Extension should show green status`);
  } else {
    console.log('🔥 SOME TESTS FAILED! Check backend status.');
  }
  
  return results;
}

// Test de conexión Chrome Extension específico
async function testExtensionMessages() {
  console.log('');
  console.log('🔌 Testing Chrome Extension Messages...');
  
  // Simular mensaje de content script
  if (typeof chrome !== 'undefined' && chrome.runtime) {
    try {
      chrome.runtime.sendMessage({
        type: 'UPDATE_API_URL',
        apiUrl: NGROK_URL
      }, (response) => {
        console.log('📨 Extension message response:', response);
      });
      
      chrome.runtime.sendMessage({
        type: 'TEST_CONNECTION'
      }, (response) => {
        console.log('🔗 Connection test response:', response);
      });
      
      console.log('✅ Extension messages sent successfully');
    } catch (error) {
      console.log('❌ Extension message error:', error);
    }
  } else {
    console.log('⚠️  Chrome extension API not available (run in extension context)');
  }
}

// Función para mostrar configuración actual
function showExtensionConfig() {
  console.log('');
  console.log('⚙️  EXTENSION CONFIGURATION:');
  console.log('─'.repeat(40));
  console.log(`🌐 Backend URL: ${NGROK_URL}`);
  console.log(`🆔 Worker ID: ${TEST_WORKER_ID}`);
  console.log(`🔄 Polling: Every 60 seconds`);
  console.log(`💓 Heartbeat: Every 30 seconds`);
  console.log('');
  console.log('📱 Manual Configuration:');
  console.log('1. Click on Son1k extension icon');
  console.log('2. Paste this URL in "Backend URL" field:');
  console.log(`   ${NGROK_URL}`);
  console.log('3. Click "Guardar" → "Probar" → "Conectar"');
  console.log('4. Extension should turn GREEN ✅');
}

// Ejecutar validación automáticamente
(async () => {
  showExtensionConfig();
  await validateExtension();
  await testExtensionMessages();
  
  console.log('');
  console.log('🎯 VALIDATION COMPLETE!');
  console.log('Copy the ngrok URL above and paste it in the extension popup.');
})();

// Exportar funciones para uso manual
window.validateExtension = validateExtension;
window.showExtensionConfig = showExtensionConfig;
window.NGROK_URL = NGROK_URL;