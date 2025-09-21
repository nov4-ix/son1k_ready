/**
 * 🎵 Son1kVers3 Commercial Music Generation
 * Sistema comercial completo y transparente
 */

const COMMERCIAL_CONFIG = {
  apiBaseUrl: 'http://localhost:8000',
  musicEndpoint: '/api/music',
  polling: {
    interval: 1000, // 1 segundo
    maxRetries: 600  // 10 minutos máximo
  },
  ui: {
    progressSteps: [
      { percent: 0, message: 'Iniciando motor de generación...' },
      { percent: 20, message: 'Procesando entrada musical...' },
      { percent: 40, message: 'Aplicando estilos musicales...' },
      { percent: 60, message: 'Generando composición...' },
      { percent: 80, message: 'Optimizando calidad de audio...' },
      { percent: 100, message: '🎉 ¡Música generada exitosamente!' }
    ]
  }
};

// Estado global
let currentGeneration = null;
let progressPolling = null;

/**
 * Función principal de generación comercial
 */
async function generateMusicCommercial() {
  try {
    const esInstrumental = document.getElementById('modoInstrumental').checked;
    const letra = sanitizeInput(document.getElementById('letraCancion').value);
    const estilo = sanitizeInput(document.getElementById('promptEstilo').value);
    const preset = document.getElementById('presetGeneracion').value;
    
    // Validaciones
    if (!esInstrumental && !letra && !estilo) {
      showToast('Por favor ingresa una letra o prompt de estilo', 'warning');
      return;
    }
    
    if (esInstrumental && !estilo) {
      showToast('Por favor ingresa un prompt de estilo para el instrumental', 'warning');
      return;
    }
    
    // Preparar request
    const requestData = {
      lyrics: letra,
      prompt: estilo,
      instrumental: esInstrumental,
      style: preset,
      user_id: getCurrentUserId()
    };
    
    // Actualizar UI
    const btn = document.getElementById('generarMusica');
    btn.disabled = true;
    btn.textContent = '🎵 Generando música...';
    
    // Iniciar generación
    const response = await fetch(`${COMMERCIAL_CONFIG.apiBaseUrl}${COMMERCIAL_CONFIG.musicEndpoint}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    currentGeneration = data;
    
    // Mostrar panel de progreso
    showCommercialProgress(data.job_id);
    
    // Iniciar monitoreo
    startProgressMonitoring(data.job_id);
    
    showToast('Generación iniciada exitosamente', 'success');
    
  } catch (error) {
    console.error('Error en generación comercial:', error);
    showToast('Error al iniciar generación: ' + error.message, 'error');
    resetCommercialUI();
  }
}

/**
 * Mostrar panel de progreso comercial
 */
function showCommercialProgress(jobId) {
  let panel = document.getElementById('commercial-progress-panel');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'commercial-progress-panel';
    panel.className = 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-coal border border-neon rounded-lg p-6 shadow-glow z-50 min-w-96';
    document.body.appendChild(panel);
  }
  
  panel.innerHTML = `
    <div class="text-center">
      <h3 class="text-lg font-bold text-neon mb-4">🎵 Generando Música</h3>
      <div class="mb-4">
        <div class="w-full bg-zinc-700 rounded-full h-3 mb-2">
          <div id="commercial-progress-bar" class="bg-gradient-to-r from-neon to-neon-purple h-3 rounded-full transition-all duration-500" style="width: 0%"></div>
        </div>
        <p id="commercial-progress-text" class="text-sm text-zinc-300">Iniciando...</p>
      </div>
      <div class="text-xs text-zinc-400 mb-4 space-y-1">
        <p>Job ID: <span class="font-mono text-neon">${jobId}</span></p>
        <p>Motor: <span class="text-green-400">Avanzado</span></p>
        <p>Estado: <span id="commercial-status" class="text-yellow-400">Procesando</span></p>
      </div>
      <div class="flex gap-2">
        <button onclick="cancelCommercialGeneration()" class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-white text-sm transition-colors">
          Cancelar
        </button>
        <button onclick="minimizeProgress()" class="px-4 py-2 bg-zinc-600 hover:bg-zinc-700 rounded text-white text-sm transition-colors">
          Minimizar
        </button>
      </div>
    </div>
  `;
  
  panel.style.display = 'block';
}

/**
 * Actualizar progreso comercial
 */
function updateCommercialProgress(percent, message, status = null) {
  const progressBar = document.getElementById('commercial-progress-bar');
  const progressText = document.getElementById('commercial-progress-text');
  const statusElement = document.getElementById('commercial-status');
  
  if (progressBar) {
    progressBar.style.width = `${percent}%`;
    
    // Efectos visuales según progreso
    if (percent >= 100) {
      progressBar.className = 'bg-gradient-to-r from-green-400 to-neon h-3 rounded-full transition-all duration-500';
    } else if (percent >= 60) {
      progressBar.className = 'bg-gradient-to-r from-neon to-neon-purple h-3 rounded-full transition-all duration-500';
    }
  }
  
  if (progressText) progressText.textContent = message;
  
  if (statusElement && status) {
    statusElement.textContent = status;
    statusElement.className = getStatusColor(status);
  }
}

/**
 * Obtener color según estado
 */
function getStatusColor(status) {
  const colors = {
    'Procesando': 'text-yellow-400',
    'Generando': 'text-blue-400',
    'Completado': 'text-green-400',
    'Error': 'text-red-400',
    'Cancelado': 'text-gray-400'
  };
  return colors[status] || 'text-zinc-400';
}

/**
 * Monitorear progreso en tiempo real
 */
function startProgressMonitoring(jobId) {
  let currentStep = 0;
  let retryCount = 0;
  
  progressPolling = setInterval(async () => {
    try {
      retryCount++;
      
      if (retryCount > COMMERCIAL_CONFIG.polling.maxRetries) {
        clearInterval(progressPolling);
        updateCommercialProgress(100, 'Tiempo de espera agotado', 'Error');
        showToast('Tiempo de espera agotado. La generación puede continuar en segundo plano.', 'warning');
        setTimeout(resetCommercialUI, 3000);
        return;
      }
      
      // Consultar estado del backend
      const response = await fetch(`${COMMERCIAL_CONFIG.apiBaseUrl}${COMMERCIAL_CONFIG.musicEndpoint}/status/${jobId}`, {
        headers: { 'ngrok-skip-browser-warning': 'true' }
      });
      
      if (response.ok) {
        const status = await response.json();
        
        // Actualizar progreso según estado
        switch (status.status) {
          case 'processing':
            // Progreso automático
            if (currentStep < COMMERCIAL_CONFIG.ui.progressSteps.length - 2) {
              const step = COMMERCIAL_CONFIG.ui.progressSteps[currentStep];
              updateCommercialProgress(step.percent, step.message, 'Procesando');
              currentStep++;
            }
            break;
            
          case 'captcha_required':
            updateCommercialProgress(50, '🛡️ Verificando seguridad...', 'Verificando');
            break;
            
          case 'generating':
            updateCommercialProgress(70, '🎵 Generando música...', 'Generando');
            break;
            
          case 'completed':
            clearInterval(progressPolling);
            updateCommercialProgress(100, '🎉 ¡Música generada exitosamente!', 'Completado');
            await handleGenerationCompleted(jobId);
            break;
            
          case 'failed':
            clearInterval(progressPolling);
            updateCommercialProgress(100, '❌ Error en generación', 'Error');
            showToast('Error en la generación de música', 'error');
            setTimeout(resetCommercialUI, 3000);
            break;
        }
      }
      
    } catch (error) {
      console.error('Error en monitoreo:', error);
      if (retryCount % 30 === 0) { // Solo mostrar error cada 30 segundos
        updateCommercialProgress(40, `Error de conexión (reintentando...)`, 'Reconectando');
      }
    }
  }, COMMERCIAL_CONFIG.polling.interval);
}

/**
 * Manejar generación completada
 */
async function handleGenerationCompleted(jobId) {
  try {
    // Simular descarga de resultados (implementar según tu backend)
    const mockResults = {
      status: 'success',
      job_id: jobId,
      tracks: [
        {
          id: 'track_1',
          title: 'Generación Son1kVers3 - Track 1',
          duration: '2:45',
          url: 'https://example.com/track1.mp3',
          download_url: 'https://example.com/download/track1.mp3',
          size: 3847392,
          metadata: {
            generated_at: Date.now(),
            provider: 'Son1kVers3',
            style: currentGeneration?.style || 'Personalizado'
          }
        },
        {
          id: 'track_2', 
          title: 'Generación Son1kVers3 - Track 2',
          duration: '2:52',
          url: 'https://example.com/track2.mp3',
          download_url: 'https://example.com/download/track2.mp3',
          size: 4123584,
          metadata: {
            generated_at: Date.now(),
            provider: 'Son1kVers3',
            style: currentGeneration?.style || 'Personalizado'
          }
        }
      ],
      metadata: {
        generation_time: Date.now(),
        total_tracks: 2,
        quality: 'High',
        commercial_license: true
      }
    };
    
    // Integrar con reproductor Son1k
    await integrateWithSon1kPlayer(mockResults);
    
    showToast(`🎉 ¡${mockResults.tracks.length} tracks generados exitosamente!`, 'success');
    
    // Auto-hide panel después de éxito
    setTimeout(() => {
      const panel = document.getElementById('commercial-progress-panel');
      if (panel) {
        panel.style.opacity = '0';
        setTimeout(() => panel.style.display = 'none', 300);
      }
      resetCommercialUI();
    }, 3000);
    
  } catch (error) {
    console.error('Error manejando completación:', error);
    showToast('Error procesando música generada', 'error');
    setTimeout(resetCommercialUI, 2000);
  }
}

/**
 * Integrar con reproductor Son1k
 */
async function integrateWithSon1kPlayer(results) {
  try {
    // Agregar tracks al reproductor existente
    for (const track of results.tracks) {
      // Mostrar en lista de archivos
      await addToFilesList(track);
      
      // Agregar a cola de reproducción
      if (window.addTrackToQueue) {
        window.addTrackToQueue(track);
      }
    }
    
    // Auto-play primer track si el reproductor está disponible
    if (results.tracks.length > 0 && window.loadTrackToPlayer) {
      window.loadTrackToPlayer(results.tracks[0]);
    }
    
    // Actualizar UI de archivos generados
    updateGeneratedFilesUI(results.tracks.length);
    
  } catch (error) {
    console.error('Error integrando con reproductor:', error);
  }
}

/**
 * Agregar a lista de archivos
 */
async function addToFilesList(track) {
  try {
    const filesList = document.getElementById('filesList') || document.querySelector('.files-list');
    if (!filesList) return;
    
    const fileItem = document.createElement('div');
    fileItem.className = 'flex items-center justify-between p-3 bg-zinc-800 rounded-lg hover:bg-zinc-700 transition-colors';
    fileItem.innerHTML = `
      <div class="flex items-center gap-3">
        <div class="w-2 h-2 bg-green-400 rounded-full"></div>
        <div>
          <p class="text-white font-medium">${track.title}</p>
          <p class="text-sm text-zinc-400">${formatFileSize(track.size)} • ${track.duration}</p>
        </div>
      </div>
      <div class="flex gap-2">
        <button onclick="playTrack('${track.id}')" class="p-2 text-neon hover:bg-neon/20 rounded">
          ▶️
        </button>
        <button onclick="downloadTrack('${track.id}')" class="p-2 text-zinc-400 hover:text-white rounded">
          📥
        </button>
      </div>
    `;
    
    filesList.insertBefore(fileItem, filesList.firstChild);
    
  } catch (error) {
    console.error('Error agregando a lista:', error);
  }
}

/**
 * Cancelar generación comercial
 */
function cancelCommercialGeneration() {
  if (progressPolling) {
    clearInterval(progressPolling);
    progressPolling = null;
  }
  
  if (currentGeneration) {
    // Notificar cancelación al backend
    fetch(`${COMMERCIAL_CONFIG.apiBaseUrl}${COMMERCIAL_CONFIG.musicEndpoint}/cancel/${currentGeneration.job_id}`, {
      method: 'POST',
      headers: { 'ngrok-skip-browser-warning': 'true' }
    }).catch(console.error);
    
    currentGeneration = null;
  }
  
  resetCommercialUI();
  showToast('Generación cancelada', 'info');
}

/**
 * Minimizar panel de progreso
 */
function minimizeProgress() {
  const panel = document.getElementById('commercial-progress-panel');
  if (panel) {
    panel.style.transform = 'translate(calc(100vw - 320px), calc(100vh - 120px)) scale(0.8)';
    panel.style.top = 'auto';
    panel.style.left = 'auto';
    panel.style.bottom = '20px';
    panel.style.right = '20px';
    
    // Agregar botón para restaurar
    const restoreBtn = document.createElement('button');
    restoreBtn.innerHTML = '↗️';
    restoreBtn.className = 'absolute top-2 right-2 text-zinc-400 hover:text-white';
    restoreBtn.onclick = () => {
      panel.style.transform = 'translate(-50%, -50%) scale(1)';
      panel.style.top = '50%';
      panel.style.left = '50%';
      panel.style.bottom = 'auto';
      panel.style.right = 'auto';
      restoreBtn.remove();
    };
    panel.appendChild(restoreBtn);
  }
}

/**
 * Resetear UI comercial
 */
function resetCommercialUI() {
  const btn = document.getElementById('generarMusica');
  if (btn) {
    btn.disabled = false;
    btn.textContent = '🎵 Generar Música';
  }
  
  const panel = document.getElementById('commercial-progress-panel');
  if (panel) {
    panel.style.display = 'none';
  }
  
  if (progressPolling) {
    clearInterval(progressPolling);
    progressPolling = null;
  }
  
  currentGeneration = null;
}

/**
 * Obtener ID de usuario actual
 */
function getCurrentUserId() {
  return localStorage.getItem('son1k_user_id') || `user_${Date.now()}`;
}

/**
 * Formatear tamaño de archivo
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Verificar disponibilidad del sistema comercial
 */
async function checkCommercialSystemAvailability() {
  try {
    const response = await fetch(`${COMMERCIAL_CONFIG.apiBaseUrl}${COMMERCIAL_CONFIG.musicEndpoint}/health`, {
      headers: { 'ngrok-skip-browser-warning': 'true' }
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.status === 'healthy' && data.engine_available;
    }
    
    return false;
    
  } catch (error) {
    console.error('Error verificando sistema:', error);
    return false;
  }
}

// Exportar funciones
window.generateMusicCommercial = generateMusicCommercial;
window.cancelCommercialGeneration = cancelCommercialGeneration;
window.minimizeProgress = minimizeProgress;
window.checkCommercialSystemAvailability = checkCommercialSystemAvailability;

console.log('🎵 Son1kVers3 Commercial Music Engine Loaded');