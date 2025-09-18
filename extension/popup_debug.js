// Popup Debug - Versión simplificada para detectar errores
console.log('🔍 Popup Debug - Starting...');

// Configuración simplificada
let currentConfig = {
  apiUrl: 'https://2a73bb633652.ngrok-free.app',
  connected: false
};

// Referencias DOM
let elements = {};

// Función de inicialización simplificada
document.addEventListener('DOMContentLoaded', async () => {
  try {
    console.log('✅ DOM loaded');
    
    // Obtener elementos DOM
    elements.apiInput = document.getElementById('api-url');
    elements.saveBtn = document.getElementById('save-btn');
    elements.testBtn = document.getElementById('test-btn');
    elements.connectBtn = document.getElementById('connect-btn');
    elements.statusEl = document.getElementById('status');
    elements.debugInfo = document.getElementById('debug-info');
    
    console.log('📋 Elements found:', {
      apiInput: !!elements.apiInput,
      saveBtn: !!elements.saveBtn,
      testBtn: !!elements.testBtn,
      connectBtn: !!elements.connectBtn,
      statusEl: !!elements.statusEl,
      debugInfo: !!elements.debugInfo
    });
    
    // Verificar elementos críticos
    if (!elements.apiInput || !elements.saveBtn || !elements.testBtn) {
      throw new Error('Elementos DOM críticos no encontrados');
    }
    
    // Agregar botón reload si existe
    elements.reloadBtn = document.getElementById('reload-btn');
    
    // Configurar valores iniciales
    elements.apiInput.value = currentConfig.apiUrl;
    
    // Configurar event listeners
    setupEventListeners();
    
    // Cargar configuración guardada
    await loadSavedConfig();
    
    // Probar conexión inicial
    await testConnection();
    
    console.log('🎉 Popup inicializado correctamente');
    showStatus('Popup inicializado correctamente', false);
    
  } catch (error) {
    console.error('❌ Error en inicialización:', error);
    showStatus(`Error de inicialización: ${error.message}`, true);
  }
});

// Configurar event listeners
function setupEventListeners() {
  try {
    elements.saveBtn.addEventListener('click', saveConfiguration);
    elements.testBtn.addEventListener('click', testConnection);
    elements.connectBtn.addEventListener('click', connectToBackend);
    
    if (elements.reloadBtn) {
      elements.reloadBtn.addEventListener('click', reloadExtension);
    }
    
    console.log('✅ Event listeners configurados');
  } catch (error) {
    console.error('❌ Error configurando event listeners:', error);
  }
}

// Cargar configuración guardada
async function loadSavedConfig() {
  try {
    const result = await chrome.storage.sync.get(['apiUrl']);
    if (result.apiUrl) {
      currentConfig.apiUrl = result.apiUrl;
      elements.apiInput.value = result.apiUrl;
      console.log('✅ Configuración cargada:', result.apiUrl);
    }
  } catch (error) {
    console.error('❌ Error cargando configuración:', error);
  }
}

// Guardar configuración
async function saveConfiguration() {
  try {
    const newUrl = elements.apiInput.value.trim();
    if (!newUrl) {
      showStatus('URL no puede estar vacía', true);
      return;
    }
    
    currentConfig.apiUrl = newUrl;
    await chrome.storage.sync.set({ apiUrl: newUrl });
    
    console.log('✅ Configuración guardada:', newUrl);
    showStatus('Configuración guardada', false);
    
  } catch (error) {
    console.error('❌ Error guardando configuración:', error);
    showStatus(`Error guardando: ${error.message}`, true);
  }
}

// Probar conexión
async function testConnection() {
  try {
    showStatus('Probando conexión...', false);
    
    // Primero verificar con background script
    const backgroundStatus = await chrome.runtime.sendMessage({ type: 'GET_STATUS' });
    console.log('📊 Background status:', backgroundStatus);
    
    const response = await fetch(`${currentConfig.apiUrl}/api/health`, {
      method: 'GET',
      headers: {
        'ngrok-skip-browser-warning': 'any'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.ok) {
        currentConfig.connected = true;
        showStatus('✅ Conexión exitosa - Backend OK', false);
        updateConnectionIndicator(true);
        console.log('✅ Conexión exitosa:', data);
        
        // Mostrar info del background script
        if (backgroundStatus) {
          showDebugMessage(`Background: ${backgroundStatus.connected ? 'Conectado' : 'Desconectado'} | Worker: ${backgroundStatus.workerStatus || 'N/A'}`);
        }
      } else {
        throw new Error('Respuesta no válida del servidor');
      }
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
  } catch (error) {
    currentConfig.connected = false;
    console.error('❌ Error en conexión:', error);
    showStatus(`❌ Error de conexión: ${error.message}`, true);
    updateConnectionIndicator(false);
  }
}

// Conectar al backend
async function connectToBackend() {
  try {
    if (!currentConfig.connected) {
      await testConnection();
    }
    
    if (currentConfig.connected) {
      // Enviar mensaje al background script
      chrome.runtime.sendMessage({
        type: 'UPDATE_API_URL',
        apiUrl: currentConfig.apiUrl
      }, (response) => {
        if (response && response.success) {
          showStatus('✅ Conectado al backend', false);
          console.log('✅ Conectado al backend');
        } else {
          showStatus('❌ Error conectando al backend', true);
        }
      });
    }
    
  } catch (error) {
    console.error('❌ Error conectando:', error);
    showStatus(`Error conectando: ${error.message}`, true);
  }
}

// Recargar extensión
async function reloadExtension() {
  try {
    showStatus('Recargando extensión...', false);
    
    // Abrir página de extensiones
    const url = 'chrome://extensions/';
    await chrome.tabs.create({ url });
    
    showStatus('✅ Página de extensiones abierta - Presiona el botón reload', false);
    showDebugMessage('Ve a chrome://extensions/ y presiona "🔄 Reload" en Son1k extension');
    
  } catch (error) {
    console.error('❌ Error abriendo extensiones:', error);
    showStatus('Manual: Ve a chrome://extensions/ y recarga Son1k', true);
  }
}

// Mostrar estado
function showStatus(message, isError = false) {
  if (elements.statusEl) {
    elements.statusEl.textContent = message;
    elements.statusEl.className = isError ? 'status-error' : 'status-success';
  }
  
  // También mostrar en debug info
  showDebugMessage(message);
}

// Mostrar mensaje de debug
function showDebugMessage(message) {
  if (elements.debugInfo) {
    const timestamp = new Date().toLocaleTimeString();
    elements.debugInfo.innerHTML += `<div>[${timestamp}] ${message}</div>`;
    elements.debugInfo.scrollTop = elements.debugInfo.scrollHeight;
  }
}

// Actualizar indicador de conexión
function updateConnectionIndicator(connected) {
  const indicator = document.getElementById('connection-indicator');
  if (indicator) {
    indicator.className = `indicator ${connected ? 'connected' : 'disconnected'}`;
  }
}

// Función de debug para mostrar información
function showDebugInfo() {
  const info = {
    currentConfig: currentConfig,
    elements: Object.keys(elements).reduce((acc, key) => {
      acc[key] = !!elements[key];
      return acc;
    }, {}),
    timestamp: new Date().toISOString()
  };
  
  console.log('🔍 Debug Info:', info);
  return info;
}

// Exportar para debugging manual
window.debugPopup = {
  showDebugInfo,
  testConnection,
  currentConfig,
  elements
};

console.log('🎯 Popup Debug loaded. Use window.debugPopup for manual testing.');