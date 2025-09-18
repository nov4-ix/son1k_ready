// Popup Script - Son1k Suno Bridge v2.0
console.log('Son1k Suno Bridge - Popup inicializado');

// Referencias DOM
let apiInput, saveBtn, testBtn, statusEl, connectBtn, debugInfo;
let workerSection, startWorkerBtn, stopWorkerBtn, workerIndicator, workerStats;

// Estado del popup
let currentConfig = {
  apiUrl: 'https://2a73bb633652.ngrok-free.app', // Configurado para ngrok actual
  connected: false,
  lastTest: null
};

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
  try {
    initializeElements();
    await loadConfiguration();
    setupEventListeners();
    await checkConnectionStatus();
    console.log('Popup ready');
  } catch (error) {
    console.error('Error inicializando popup:', error);
    showStatus('Error de inicialización', true);
  }
});

function initializeElements() {
  apiInput = document.getElementById('api-url');
  saveBtn = document.getElementById('save-btn');
  testBtn = document.getElementById('test-btn');
  statusEl = document.getElementById('status');
  connectBtn = document.getElementById('connect-btn');
  debugInfo = document.getElementById('debug-info');
  
  // Worker elements
  workerSection = document.getElementById('worker-section');
  startWorkerBtn = document.getElementById('start-worker-btn');
  stopWorkerBtn = document.getElementById('stop-worker-btn');
  workerIndicator = document.getElementById('worker-indicator');
  workerStats = document.getElementById('worker-stats');
  
  if (!apiInput || !saveBtn || !testBtn || !statusEl) {
    throw new Error('Elementos DOM requeridos no encontrados');
  }
}

async function loadConfiguration() {
  try {
    // Cargar configuración desde storage
    const result = await chrome.storage.sync.get(['apiUrl', 'lastConnected']);
    
    currentConfig.apiUrl = result.apiUrl || currentConfig.apiUrl;
    currentConfig.lastTest = result.lastConnected || null;
    
    // Actualizar UI
    apiInput.value = currentConfig.apiUrl;
    
    // Obtener estado desde background
    const response = await sendMessageToBackground('GET_STATUS');
    if (response) {
      currentConfig.connected = response.connected || false;
      updateConnectionStatus();
    }
    
    console.log('Configuración cargada:', currentConfig);
  } catch (error) {
    console.error('Error cargando configuración:', error);
  }
}

function setupEventListeners() {
  // Botón guardar
  saveBtn.addEventListener('click', handleSave);
  
  // Botón probar
  testBtn.addEventListener('click', handleTest);
  
  // Enter en input
  apiInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handleSave();
    }
  });
  
  // Worker listeners
  if (startWorkerBtn) {
    startWorkerBtn.addEventListener('click', startWorker);
  }
  
  if (stopWorkerBtn) {
    stopWorkerBtn.addEventListener('click', stopWorker);
  }
  
  // Auto-refresh worker status every 5 seconds
  setInterval(updateWorkerStatus, 5000);
  
  // Botón conectar (si existe)
  if (connectBtn) {
    connectBtn.addEventListener('click', handleConnect);
  }
  
  // Input change listener
  apiInput.addEventListener('input', () => {
    // Reset status cuando el usuario edita
    currentConfig.connected = false;
    updateConnectionStatus();
  });
}

async function handleSave() {
  try {
    const url = normalizeUrl(apiInput.value.trim());
    
    if (!url) {
      showStatus('Por favor ingresa una URL válida', true);
      return;
    }
    
    if (!isValidUrl(url)) {
      showStatus('Formato de URL inválido', true);
      return;
    }
    
    // Actualizar estado
    currentConfig.apiUrl = url;
    apiInput.value = url;
    
    // Guardar en storage
    await chrome.storage.sync.set({ 
      apiUrl: url,
      lastSaved: new Date().toISOString()
    });
    
    // Notificar al background
    await sendMessageToBackground('UPDATE_API_URL', { apiUrl: url });
    
    showStatus('Configuración guardada ✓', false);
    
    // Auto-test después de guardar
    setTimeout(() => {
      handleTest();
    }, 500);
    
  } catch (error) {
    console.error('Error guardando:', error);
    showStatus('Error al guardar configuración', true);
  }
}

async function handleTest() {
  try {
    showStatus('Probando conexión...', false);
    testBtn.disabled = true;
    
    // Test a través del background
    const response = await sendMessageToBackground('TEST_CONNECTION');
    
    if (response && response.connected) {
      currentConfig.connected = true;
      currentConfig.lastTest = new Date().toISOString();
      
      // Guardar último test exitoso
      await chrome.storage.sync.set({ 
        lastConnected: currentConfig.lastTest 
      });
      
      showStatus('¡Conectado al backend! ✅', false);
      updateConnectionStatus();
      
      // Auto-abrir Suno después de test exitoso
      setTimeout(() => {
        openSunoTab();
      }, 1000);
      
    } else {
      currentConfig.connected = false;
      const errorMsg = response?.error || 'No se pudo conectar';
      showStatus(`Error: ${errorMsg}`, true);
      updateConnectionStatus();
    }
    
  } catch (error) {
    console.error('Error probando conexión:', error);
    currentConfig.connected = false;
    showStatus('Error de conexión', true);
    updateConnectionStatus();
  } finally {
    testBtn.disabled = false;
  }
}

async function handleConnect() {
  if (currentConfig.connected) {
    openSunoTab();
  } else {
    await handleTest();
  }
}

async function checkConnectionStatus() {
  try {
    const response = await sendMessageToBackground('GET_STATUS');
    if (response) {
      currentConfig.connected = response.connected || false;
      updateConnectionStatus();
      updateDebugInfo(response);
    }
  } catch (error) {
    console.error('Error verificando estado:', error);
  }
}

function updateConnectionStatus() {
  // Actualizar indicadores visuales
  if (statusEl) {
    statusEl.className = currentConfig.connected ? 'status-connected' : 'status-disconnected';
  }
  
  if (connectBtn) {
    connectBtn.textContent = currentConfig.connected ? '🎵 Abrir Suno' : '🔄 Conectar';
    connectBtn.disabled = false;
  }
  
  // Actualizar clase del popup
  document.body.className = currentConfig.connected ? 'connected' : 'disconnected';
}

function updateDebugInfo(data) {
  if (debugInfo) {
    debugInfo.innerHTML = `
      <small>
        Backend: ${data.apiUrl || 'No configurado'}<br>
        Estado: ${data.connected ? 'Conectado' : 'Desconectado'}<br>
        Última prueba: ${currentConfig.lastTest ? new Date(currentConfig.lastTest).toLocaleTimeString() : 'Nunca'}
      </small>
    `;
  }
}

async function openSunoTab() {
  try {
    await chrome.tabs.create({ 
      url: 'https://suno.com/create',
      active: true 
    });
    
    // Cerrar popup después de abrir
    window.close();
  } catch (error) {
    console.error('Error abriendo Suno:', error);
    showStatus('Error abriendo Suno', true);
  }
}

// Utility Functions
function normalizeUrl(url) {
  if (!url) return '';
  
  url = url.trim();
  
  // Agregar protocolo si no existe
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'http://' + url;
  }
  
  // Remover trailing slash
  url = url.replace(/\/+$/, '');
  
  return url;
}

function isValidUrl(string) {
  try {
    const url = new URL(string);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

function showStatus(message, isError = false) {
  if (!statusEl) return;
  
  statusEl.textContent = message;
  statusEl.className = isError ? 'status-error' : 'status-success';
  
  // Auto-clear después de 3 segundos
  if (message) {
    setTimeout(() => {
      if (statusEl.textContent === message) {
        statusEl.textContent = '';
        statusEl.className = '';
      }
    }, 3000);
  }
}

async function sendMessageToBackground(type, data = {}) {
  try {
    return await chrome.runtime.sendMessage({
      type,
      ...data
    });
  } catch (error) {
    console.error('Error enviando mensaje al background:', error);
    return null;
  }
}

// ================================
// WORKER AUTOMÁTICO - UI
// ================================

// Actualizar status del worker
async function updateWorkerStatus() {
  try {
    const status = await sendMessageToBackground('GET_STATUS');
    
    if (status) {
      // Actualizar indicador
      if (workerIndicator) {
        if (status.workerStatus === 'online' || status.workerStatus === 'busy') {
          workerIndicator.className = 'indicator connected';
        } else {
          workerIndicator.className = 'indicator disconnected';
        }
      }
      
      // Actualizar estadísticas
      if (workerStats) {
        const statusText = getWorkerStatusText(status.workerStatus);
        const currentJob = status.currentJobId ? `\nJob actual: ${status.currentJobId.slice(0, 8)}...` : '';
        
        workerStats.innerHTML = `
          📊 Status: ${statusText}<br>
          ✅ Jobs completados: ${status.jobsCompleted || 0}<br>
          ❌ Jobs fallidos: ${status.jobsFailed || 0}${currentJob}
        `;
      }
      
      // Habilitar/deshabilitar botones
      if (startWorkerBtn && stopWorkerBtn) {
        const isConnected = status.connected;
        const isWorkerRunning = status.workerStatus === 'online' || status.workerStatus === 'busy';
        
        startWorkerBtn.disabled = !isConnected || isWorkerRunning;
        stopWorkerBtn.disabled = !isWorkerRunning;
      }
      
      // Mostrar/ocultar sección worker
      if (workerSection) {
        workerSection.style.display = status.connected ? 'block' : 'none';
      }
    }
  } catch (error) {
    console.error('Error updating worker status:', error);
  }
}

function getWorkerStatusText(status) {
  switch (status) {
    case 'online': return '🟢 Esperando jobs';
    case 'busy': return '🟡 Procesando';
    case 'offline': return '🔴 Detenido';
    default: return '⚪ Desconocido';
  }
}

// Iniciar worker
async function startWorker() {
  try {
    startWorkerBtn.disabled = true;
    startWorkerBtn.textContent = '⏳ Iniciando...';
    
    const result = await sendMessageToBackground('START_WORKER');
    
    if (result && result.success) {
      showStatus('🤖 Worker iniciado', false);
      setTimeout(updateWorkerStatus, 500);
    } else {
      showStatus('❌ Error iniciando worker', true);
    }
  } catch (error) {
    console.error('Error starting worker:', error);
    showStatus('❌ Error iniciando worker', true);
  } finally {
    startWorkerBtn.textContent = '🤖 Iniciar';
    setTimeout(updateWorkerStatus, 500);
  }
}

// Detener worker
async function stopWorker() {
  try {
    stopWorkerBtn.disabled = true;
    stopWorkerBtn.textContent = '⏳ Deteniendo...';
    
    const result = await sendMessageToBackground('STOP_WORKER');
    
    if (result && result.success) {
      showStatus('🛑 Worker detenido', false);
      setTimeout(updateWorkerStatus, 500);
    } else {
      showStatus('❌ Error deteniendo worker', true);
    }
  } catch (error) {
    console.error('Error stopping worker:', error);
    showStatus('❌ Error deteniendo worker', true);
  } finally {
    stopWorkerBtn.textContent = '🛑 Detener';
    setTimeout(updateWorkerStatus, 500);
  }
}

// Worker event listeners are now included in the main setupEventListeners function above

// Actualizar checkConnectionStatus para incluir worker status
async function checkConnectionStatus() {
  try {
    const response = await sendMessageToBackground('GET_STATUS');
    
    if (response) {
      currentConfig.connected = response.connected;
      updateConnectionIndicator(response.connected);
      updateDebugInfo(response);
      
      // Update worker status
      await updateWorkerStatus();
      
      if (response.connected) {
        showStatus('🟢 Conectado al backend', false);
      } else {
        showStatus('🔴 Sin conexión al backend', true);
      }
    } else {
      currentConfig.connected = false;
      updateConnectionIndicator(false);
      showStatus('❌ Error de comunicación', true);
    }
  } catch (error) {
    console.error('Error verificando conexión:', error);
    currentConfig.connected = false;
    updateConnectionIndicator(false);
    showStatus('❌ Error verificando estado', true);
  }
}

// Manejo de errores globales
window.addEventListener('error', (event) => {
  console.error('Popup error:', event.error);
  showStatus('Error interno del popup', true);
});

console.log('Son1k Suno Bridge - Popup script loaded');