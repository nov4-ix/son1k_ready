/**
 * 🎵 Son1k Advanced Music Generation
 * Sistema transparente de generación musical avanzada
 */

// Configuración
const SON1K_CONFIG = {
  apiBaseUrl: 'http://localhost:8000',
  captchaEndpoint: '/api/captcha',
  polling: {
    interval: 2000, // 2 segundos
    maxRetries: 300  // 10 minutos máximo
  },
  generator: {
    createUrl: 'https://suno.com/create',
    maxGenerationTime: 300000 // 5 minutos
  }
};

// Estado global
let currentJob = null;
let captchaPolling = null;

/**
 * Función principal para generar música avanzada
 */
async function generarMusicaAvanzada() {
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
    
    // Crear job ID único
    const jobId = `suno_job_${Date.now()}`;
    currentJob = {
      id: jobId,
      lyrics: letra,
      prompt: estilo,
      instrumental: esInstrumental,
      style: preset,
      status: 'starting',
      startTime: Date.now()
    };
    
    // Actualizar UI
    const btn = document.getElementById('generarMusica');
    btn.disabled = true;
    btn.textContent = '🎵 Generando música...';
    
    // Mostrar panel de progreso
    mostrarPanelProgreso(jobId);
    
    // 1. Notificar inicio al backend
    await notificarEventoCaptcha(jobId, 'STARTED');
    updateProgress('Iniciando motor de generación...', 10);
    
    // 2. Proceso transparente - se maneja automáticamente
    updateProgress('Procesando entrada musical...', 30);
    
    // Simular procesamiento automático
    setTimeout(() => {
      updateProgress('Aplicando estilos musicales...', 50);
    }, 2000);
    
    setTimeout(() => {
      updateProgress('Generando composición...', 70);
    }, 4000);
    
    // 3. Iniciar polling para monitorear progreso
    iniciarMonitoreoCaptcha(jobId);
    
  } catch (error) {
    console.error('Error en generación:', error);
    showToast('Error al iniciar generación: ' + error.message, 'error');
    resetearUI();
  }
}

/**
 * Notificar evento de CAPTCHA al backend
 */
async function notificarEventoCaptcha(jobId, status) {
  try {
    const response = await fetch(`${SON1K_CONFIG.apiBaseUrl}${SON1K_CONFIG.captchaEndpoint}/event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'
      },
      body: JSON.stringify({
        job_id: jobId,
        provider: 'suno',
        status: status,
        timestamp: Math.floor(Date.now() / 1000)
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error notificando evento: ${response.status}`);
    }
    
    console.log(`✅ Evento ${status} notificado para job ${jobId}`);
    return true;
    
  } catch (error) {
    console.error('Error notificando evento:', error);
    return false;
  }
}

/**
 * Mostrar panel de progreso durante generación
 */
function mostrarPanelProgreso(jobId) {
  // Crear panel si no existe
  let panel = document.getElementById('music-progress-panel');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'music-progress-panel';
    panel.className = 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-coal border border-neon rounded-lg p-6 shadow-glow z-50 min-w-96';
    document.body.appendChild(panel);
  }
  
  panel.innerHTML = `
    <div class="text-center">
      <h3 class="text-lg font-bold text-neon mb-4">🎵 Generando Música</h3>
      <div class="mb-4">
        <div class="w-full bg-zinc-700 rounded-full h-2 mb-2">
          <div id="progress-bar" class="bg-neon h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
        </div>
        <p id="progress-text" class="text-sm text-zinc-300">Iniciando...</p>
      </div>
      <div class="text-xs text-zinc-400 mb-4">
        <p>Job ID: <span class="font-mono text-neon">${jobId}</span></p>
      </div>
      <button onclick="cancelarGeneracion()" class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-white text-sm transition-colors">
        Cancelar
      </button>
    </div>
  `;
  
  panel.style.display = 'block';
}

/**
 * Actualizar progreso visual
 */
function updateProgress(message, percentage) {
  const progressBar = document.getElementById('progress-bar');
  const progressText = document.getElementById('progress-text');
  
  if (progressBar) progressBar.style.width = `${percentage}%`;
  if (progressText) progressText.textContent = message;
}

/**
 * Proceso de generación transparente
 * Todo se maneja automáticamente en segundo plano
 */
function procesarGeneracionTransparente() {
  // El proceso se maneja completamente en segundo plano
  // El usuario solo ve el progreso pero no necesita intervenir
  updateProgress('Conectando con motor de generación...', 40);
}

/**
 * Copiar texto al clipboard
 */
function copyToClipboard(text, message) {
  navigator.clipboard.writeText(text).then(() => {
    showToast(message, 'success');
  }).catch(() => {
    showToast('Error copiando al clipboard', 'error');
  });
}

/**
 * Iniciar monitoreo de estado del CAPTCHA
 */
function iniciarMonitoreoCaptcha(jobId) {
  let retries = 0;
  
  captchaPolling = setInterval(async () => {
    try {
      retries++;
      
      if (retries > SON1K_CONFIG.polling.maxRetries) {
        clearInterval(captchaPolling);
        updateProgress('Tiempo de espera agotado', 100);
        showToast('Tiempo de espera agotado. Inténtalo de nuevo.', 'error');
        resetearUI();
        return;
      }
      
      const status = await verificarEstadoCaptcha(jobId);
      
      if (status) {
        switch (status.status) {
          case 'NEEDED':
            updateProgress('🛡️ Verificando seguridad...', 50);
            break;
            
          case 'RESOLVED':
            updateProgress('✅ Verificación completada - finalizando...', 75);
            break;
            
          case 'COMPLETED':
            clearInterval(captchaPolling);
            updateProgress('🎉 ¡Generación completada!', 100);
            await manejarGeneracionCompletada(jobId);
            break;
            
          case 'ERROR':
            clearInterval(captchaPolling);
            updateProgress('❌ Error en generación', 100);
            showToast('Error en la generación de música', 'error');
            resetearUI();
            break;
        }
      }
      
    } catch (error) {
      console.error('Error en polling:', error);
      if (retries % 10 === 0) { // Solo mostrar error cada 10 intentos
        updateProgress(`Error de conexión (intento ${retries})...`, 40);
      }
    }
  }, SON1K_CONFIG.polling.interval);
}

/**
 * Verificar estado del CAPTCHA en el backend
 */
async function verificarEstadoCaptcha(jobId) {
  try {
    const response = await fetch(`${SON1K_CONFIG.apiBaseUrl}${SON1K_CONFIG.captchaEndpoint}/status/${jobId}`, {
      method: 'GET',
      headers: {
        'ngrok-skip-browser-warning': 'true'
      }
    });
    
    if (response.ok) {
      return await response.json();
    }
    
    return null;
    
  } catch (error) {
    console.error('Error verificando estado:', error);
    return null;
  }
}

/**
 * Manejar cuando se completa la generación
 */
async function manejarGeneracionCompletada(jobId) {
  try {
    // Simular respuesta de Suno (en implementación real vendría del backend)
    const mockResponse = {
      status: 'success',
      job_id: jobId,
      tracks: [
        {
          id: 'track_1',
          title: `${currentJob.style || 'Generated'} Track 1`,
          duration: '2:45',
          url: 'https://example.com/track1.mp3',
          download_url: 'https://example.com/download/track1.mp3',
          size: 3847392,
          metadata: {
            style: currentJob.style,
            generated_at: Date.now(),
            provider: 'suno'
          }
        },
        {
          id: 'track_2',
          title: `${currentJob.style || 'Generated'} Track 2`,
          duration: '2:52',
          url: 'https://example.com/track2.mp3',
          download_url: 'https://example.com/download/track2.mp3',
          size: 4123584,
          metadata: {
            style: currentJob.style,
            generated_at: Date.now(),
            provider: 'suno'
          }
        }
      ],
      metadata: {
        generation_time: Date.now(),
        provider: 'suno',
        total_tracks: 2,
        captcha_resolved: true
      }
    };
    
    // Integrar con el reproductor Son1k existente
    integrarConReproductor(mockResponse);
    
    // Mostrar notificación de éxito
    showToast(`🎉 ¡${mockResponse.tracks.length} tracks generados exitosamente!`, 'success');
    
    // Resetear UI después de un momento
    setTimeout(resetearUI, 2000);
    
  } catch (error) {
    console.error('Error manejando completación:', error);
    showToast('Error procesando tracks generados', 'error');
    resetearUI();
  }
}

/**
 * Integrar tracks generados con el reproductor Son1k
 */
function integrarConReproductor(response) {
  try {
    // Agregar tracks al reproductor existente
    response.tracks.forEach((track, index) => {
      // Aquí integrarías con tu sistema de reproductor existente
      console.log(`🎵 Track ${index + 1}: ${track.title}`);
      
      // Ejemplo de integración (ajusta según tu reproductor)
      if (window.addTrackToPlayer) {
        window.addTrackToPlayer({
          id: track.id,
          title: track.title,
          url: track.url,
          duration: track.duration,
          downloadUrl: track.download_url,
          metadata: track.metadata
        });
      }
    });
    
    // Actualizar UI del reproductor
    if (response.tracks.length > 0) {
      // Auto-play primer track
      if (window.playTrack) {
        window.playTrack(response.tracks[0]);
      }
    }
    
  } catch (error) {
    console.error('Error integrando con reproductor:', error);
  }
}

/**
 * Cancelar generación actual
 */
function cancelarGeneracion() {
  if (captchaPolling) {
    clearInterval(captchaPolling);
    captchaPolling = null;
  }
  
  if (currentJob) {
    notificarEventoCaptcha(currentJob.id, 'CANCELLED');
    currentJob = null;
  }
  
  resetearUI();
  showToast('Generación cancelada', 'info');
}

/**
 * Resetear UI al estado inicial
 */
function resetearUI() {
  // Habilitar botón de generación
  const btn = document.getElementById('generarMusica');
  if (btn) {
    btn.disabled = false;
    btn.textContent = '🎵 Generar Música';
  }
  
  // Ocultar panel de progreso
  const panel = document.getElementById('suno-progress-panel');
  if (panel) panel.style.display = 'none';
  
  // Cerrar modal de instrucciones
  cerrarInstrucciones();
  
  // Limpiar polling
  if (captchaPolling) {
    clearInterval(captchaPolling);
    captchaPolling = null;
  }
  
  currentJob = null;
}

/**
 * Función helper para verificar si el sistema está disponible
 */
async function verificarSistemaSuno() {
  try {
    const response = await fetch(`${SON1K_CONFIG.apiBaseUrl}${SON1K_CONFIG.captchaEndpoint}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

// Exportar funciones para uso global
window.generarMusicaAvanzada = generarMusicaAvanzada;
window.cancelarGeneracion = cancelarGeneracion;
window.copyToClipboard = copyToClipboard;

console.log('🎵 Son1k Advanced Music Engine Loaded');