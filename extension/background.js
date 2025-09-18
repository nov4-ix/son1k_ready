// Background Service Worker - Son1k Suno Bridge v2.0
console.log('Son1k Suno Bridge - Background Service Worker iniciado');

let cachedApiUrl = null;
let isConnected = false;
let workerStatus = 'offline'; // offline | online | busy
let currentJobId = null;
let workerId = null;
let jobPollingInterval = null;
let heartbeatInterval = null;
let jobsCompleted = 0;
let jobsFailed = 0;
let autoWorkerEnabled = true; // Auto-worker habilitado por defecto

// Configuración por defecto
const DEFAULT_CONFIG = {
  apiUrl: 'https://son1kvers3.com',
  autoSubmit: false,
  debugMode: false,
  pollingInterval: 60000, // 60 segundos para producción
  heartbeatInterval: 30000 // 30 segundos
};

// Generar worker ID único
function generateWorkerId() {
  return 'worker-' + Math.random().toString(36).substr(2, 9) + '-' + Date.now();
}

// Inicialización del service worker
chrome.runtime.onStartup.addListener(() => {
  console.log('Extension startup - inicializando configuración');
  initializeExtension();
});

chrome.runtime.onInstalled.addListener((details) => {
  console.log('Extension installed/updated:', details.reason);
  initializeExtension();
});

async function initializeExtension() {
  try {
    // Cargar configuración guardada o usar defaults
    const result = await chrome.storage.sync.get(['apiUrl', 'autoSubmit', 'debugMode', 'workerId']);
    
    cachedApiUrl = result.apiUrl || DEFAULT_CONFIG.apiUrl;
    workerId = result.workerId || generateWorkerId();
    
    // Guardar worker ID si es nuevo
    if (!result.workerId) {
      await chrome.storage.sync.set({ workerId });
    }
    
    // Verificar conexión inicial
    await testConnection();
    
    if (isConnected) {
      startWorkerMode();
    }
    
    console.log('Extension inicializada:', {
      apiUrl: cachedApiUrl,
      connected: isConnected,
      workerId: workerId,
      workerStatus: workerStatus
    });
  } catch (error) {
    console.error('Error inicializando extension:', error);
  }
}

// Prueba de conexión con el backend
async function testConnection() {
  if (!cachedApiUrl) return false;
  
  try {
    const response = await fetch(`${cachedApiUrl}/api/health`, {
      method: 'GET',
      mode: 'cors',
      cache: 'no-cache'
    });
    
    if (response.ok) {
      const data = await response.json();
      const previousConnection = isConnected;
      isConnected = data.ok === true;
      
      // Si se reconectó, reiniciar worker mode
      if (isConnected && !previousConnection) {
        console.log('Backend reconnected - starting worker mode');
        startWorkerMode();
      } else if (!isConnected && previousConnection) {
        console.log('Backend disconnected - stopping worker mode');
        stopWorkerMode();
      }
      
      console.log('Backend connection test:', isConnected ? 'SUCCESS' : 'FAILED');
      return isConnected;
    }
  } catch (error) {
    console.warn('Backend connection failed:', error.message);
    if (isConnected) {
      stopWorkerMode();
    }
    isConnected = false;
  }
  return false;
}

// Envío de datos musicales al backend
async function sendToBackend(musicData) {
  if (!cachedApiUrl || !isConnected) {
    throw new Error('Backend no disponible');
  }
  
  try {
    console.log('Enviando datos al backend:', musicData);
    
    const response = await fetch(`${cachedApiUrl}/api/songs/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: musicData.prompt || '',
        lyrics: musicData.lyrics || '',
        mode: musicData.mode || 'original',
        source: 'suno_extension',
        timestamp: new Date().toISOString()
      }),
      mode: 'cors'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('Backend response:', result);
    
    return {
      success: true,
      data: result
    };
  } catch (error) {
    console.error('Error enviando al backend:', error);
    throw error;
  }
}

// Manejo de mensajes de content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message.type, message);
  
  switch (message.type) {
    case 'GET_API_URL':
      sendResponse({ apiUrl: cachedApiUrl, connected: isConnected });
      break;
      
    case 'UPDATE_API_URL':
      handleApiUrlUpdate(message.apiUrl)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true; // Mantener el canal abierto para respuesta asíncrona
      
    case 'TEST_CONNECTION':
      testConnection()
        .then(connected => sendResponse({ connected }))
        .catch(error => sendResponse({ connected: false, error: error.message }));
      return true;
      
    case 'SEND_TO_SON1K':
      sendToBackend(message.data)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ 
          success: false, 
          error: error.message 
        }));
      return true;
      
    case 'GET_STATUS':
      sendResponse({
        apiUrl: cachedApiUrl,
        connected: isConnected,
        timestamp: new Date().toISOString()
      });
      break;
      
    default:
      console.warn('Unknown message type:', message.type);
      sendResponse({ error: 'Unknown message type' });
  }
});

// Actualización de URL de API
async function handleApiUrlUpdate(newApiUrl) {
  try {
    // Normalizar URL
    if (newApiUrl && !newApiUrl.startsWith('http')) {
      newApiUrl = 'http://' + newApiUrl;
    }
    
    // Guardar en storage
    await chrome.storage.sync.set({ apiUrl: newApiUrl });
    cachedApiUrl = newApiUrl;
    
    // Probar nueva conexión
    const connected = await testConnection();
    
    return {
      success: true,
      connected,
      apiUrl: cachedApiUrl
    };
  } catch (error) {
    console.error('Error updating API URL:', error);
    throw error;
  }
}

// Manejo de errores globales
self.addEventListener('error', (event) => {
  console.error('Service Worker error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('Service Worker unhandled rejection:', event.reason);
});

// ================================
// WORKER AUTOMÁTICO - FUNCIONES PRINCIPALES
// ================================

// Iniciar modo worker automático
function startWorkerMode() {
  if (!isConnected || !workerId) {
    console.warn('Cannot start worker mode - not connected or no worker ID');
    return;
  }
  
  workerStatus = 'online';
  
  // Iniciar polling de jobs
  if (!jobPollingInterval) {
    jobPollingInterval = setInterval(pollForJobs, DEFAULT_CONFIG.pollingInterval);
    console.log(`🤖 Worker polling started (every ${DEFAULT_CONFIG.pollingInterval/1000}s)`);
  }
  
  // Iniciar heartbeat
  if (!heartbeatInterval) {
    heartbeatInterval = setInterval(sendHeartbeat, DEFAULT_CONFIG.heartbeatInterval);
    console.log(`💓 Heartbeat started (every ${DEFAULT_CONFIG.heartbeatInterval/1000}s)`);
  }
  
  // Enviar heartbeat inicial
  sendHeartbeat();
  
  console.log(`✅ Worker mode started - ID: ${workerId}`);
}

// Detener modo worker
function stopWorkerMode() {
  workerStatus = 'offline';
  currentJobId = null;
  
  if (jobPollingInterval) {
    clearInterval(jobPollingInterval);
    jobPollingInterval = null;
    console.log('🛑 Worker polling stopped');
  }
  
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
    console.log('🛑 Heartbeat stopped');
  }
  
  console.log('❌ Worker mode stopped');
}

// Polling de jobs del backend
async function pollForJobs() {
  if (!isConnected || workerStatus === 'busy' || !autoWorkerEnabled) {
    return;
  }
  
  try {
    // Usar endpoint simplificado para compatibilidad
    const response = await fetch(`${cachedApiUrl}/api/jobs/pending?worker_id=${workerId}`, {
      method: 'GET',
      mode: 'cors',
      cache: 'no-cache'
    });
    
    if (response.ok) {
      const job = await response.json();
      
      if (job.job_id) {
        console.log('📋 New job received:', job);
        await processJob(job);
      } else {
        // No hay jobs disponibles
        console.log('⏳ No jobs available');
      }
    } else {
      console.warn('❌ Job polling failed:', response.status);
    }
  } catch (error) {
    console.error('❌ Error polling jobs:', error);
  }
}

// Procesar job recibido
async function processJob(job) {
  try {
    workerStatus = 'busy';
    currentJobId = job.job_id;
    
    // Actualizar estado a processing
    await updateJobStatus(job.job_id, 'processing');
    
    console.log(`🎵 Processing job ${job.job_id}:`, {
      prompt: job.prompt,
      lyrics: job.lyrics,
      mode: job.mode
    });
    
    // Enviar mensaje al content script para procesar en Suno
    const tabs = await chrome.tabs.query({ url: '*://suno.com/*' });
    
    if (tabs.length === 0) {
      // Abrir Suno si no está abierto
      console.log('🌐 Opening Suno tab...');
      const tab = await chrome.tabs.create({ url: 'https://suno.com' });
      
      // Esperar a que cargue
      await new Promise(resolve => {
        const listener = (tabId, changeInfo) => {
          if (tabId === tab.id && changeInfo.status === 'complete') {
            chrome.tabs.onUpdated.removeListener(listener);
            resolve();
          }
        };
        chrome.tabs.onUpdated.addListener(listener);
      });
      
      // Procesar en la nueva tab
      await processJobInTab(tab.id, job);
    } else {
      // Usar tab existente
      await processJobInTab(tabs[0].id, job);
    }
    
  } catch (error) {
    console.error(`❌ Error processing job ${job.job_id}:`, error);
    await updateJobStatus(job.job_id, 'failed', { error_message: error.message });
    jobsFailed++;
  } finally {
    workerStatus = 'online';
    currentJobId = null;
  }
}

// Procesar job en tab específica
async function processJobInTab(tabId, job) {
  try {
    // Enviar job al content script
    const response = await chrome.tabs.sendMessage(tabId, {
      type: 'PROCESS_JOB',
      job: job
    });
    
    if (response && response.success) {
      console.log(`✅ Job ${job.job_id} completed successfully`);
      
      // Usar endpoint simplificado para marcar como completado
      await fetch(`${cachedApiUrl}/api/jobs/${job.job_id}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio_url: response.audio_url,
          preview_url: response.preview_url,
          completed_at: new Date().toISOString()
        }),
        mode: 'cors'
      });
      
      jobsCompleted++;
      console.log(`📊 Total jobs completed: ${jobsCompleted}`);
    } else {
      throw new Error(response?.error || 'Job processing failed');
    }
  } catch (error) {
    console.error(`❌ Error in tab processing:`, error);
    throw error;
  }
}

// Actualizar estado del job
async function updateJobStatus(jobId, status, extraData = {}) {
  try {
    const response = await fetch(`${cachedApiUrl}/api/jobs/${jobId}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, ...extraData }),
      mode: 'cors'
    });
    
    if (response.ok) {
      console.log(`📝 Job ${jobId} status updated to: ${status}`);
    } else {
      console.error(`❌ Failed to update job status:`, response.statusText);
    }
  } catch (error) {
    console.error(`❌ Error updating job status:`, error);
  }
}

// Enviar heartbeat al backend
async function sendHeartbeat() {
  if (!isConnected || !workerId) return;
  
  try {
    const response = await fetch(`${cachedApiUrl}/api/worker/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        worker_id: workerId,
        status: workerStatus,
        version: '2.0.0',
        current_job_id: currentJobId,
        jobs_completed: jobsCompleted,
        jobs_failed: jobsFailed
      }),
      mode: 'cors'
    });
    
    if (response.ok) {
      console.log(`💓 Heartbeat sent - Status: ${workerStatus}`);
    }
  } catch (error) {
    console.error('❌ Error sending heartbeat:', error);
  }
}

// ================================
// MANEJO DE MENSAJES ACTUALIZADO
// ================================

// Actualizar manejo de mensajes para incluir worker commands
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message.type, message);
  
  switch (message.type) {
    case 'GET_API_URL':
      sendResponse({ apiUrl: cachedApiUrl, connected: isConnected });
      break;
      
    case 'UPDATE_API_URL':
      handleApiUrlUpdate(message.apiUrl)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true;
      
    case 'TEST_CONNECTION':
      testConnection()
        .then(connected => sendResponse({ connected }))
        .catch(error => sendResponse({ connected: false, error: error.message }));
      return true;
      
    case 'SEND_TO_SON1K':
      sendToBackend(message.data)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ 
          success: false, 
          error: error.message 
        }));
      return true;
      
    case 'GET_STATUS':
      sendResponse({
        apiUrl: cachedApiUrl,
        connected: isConnected,
        workerId: workerId,
        workerStatus: workerStatus,
        currentJobId: currentJobId,
        jobsCompleted: jobsCompleted,
        jobsFailed: jobsFailed,
        autoWorkerEnabled: autoWorkerEnabled,
        timestamp: new Date().toISOString()
      });
      break;
      
    case 'START_WORKER':
      if (isConnected) {
        autoWorkerEnabled = true;
        startWorkerMode();
        sendResponse({ success: true, status: 'Auto-worker started' });
      } else {
        sendResponse({ success: false, error: 'Not connected to backend' });
      }
      break;
      
    case 'STOP_WORKER':
      autoWorkerEnabled = false;
      stopWorkerMode();
      sendResponse({ success: true, status: 'Auto-worker stopped' });
      break;
      
    case 'TOGGLE_AUTO_WORKER':
      autoWorkerEnabled = !autoWorkerEnabled;
      if (autoWorkerEnabled && isConnected) {
        startWorkerMode();
      } else {
        stopWorkerMode();
      }
      sendResponse({ 
        success: true, 
        autoWorkerEnabled: autoWorkerEnabled,
        status: autoWorkerEnabled ? 'Auto-worker enabled' : 'Auto-worker disabled'
      });
      break;
      
    default:
      console.warn('Unknown message type:', message.type);
      sendResponse({ error: 'Unknown message type' });
  }
});

// Keepalive para mantener el service worker activo
let keepAliveTimer;

function keepAlive() {
  keepAliveTimer = setTimeout(() => {
    chrome.runtime.getPlatformInfo(() => {
      keepAlive();
    });
  }, 20000); // 20 segundos
}

// Iniciar keepalive
keepAlive();

console.log('Son1k Suno Bridge - Background Service Worker loaded successfully');