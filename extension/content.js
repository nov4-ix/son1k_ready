// Content Script - Son1k Suno Bridge v2.0
console.log('Son1k Suno Bridge - Content script inicializado en:', window.location.href);

// Configuration
const CONFIG = {
  buttonId: 'son1k-send-btn',
  buttonText: 'Send to Son1k',
  retryAttempts: 5,
  retryDelay: 1000,
  observerTimeout: 30000
};

// State management
let isInitialized = false;
let currentButton = null;
let mutationObserver = null;
let retryTimer = null;
let isProcessing = false;

// Selector strategies for different Suno layouts
const SELECTOR_STRATEGIES = {
  // Strategy 1: Modern Suno interface (2024+)
  modern: {
    name: 'Modern Suno Interface',
    selectors: {
      prompt: [
        'textarea[placeholder*="Describe"]',
        'textarea[placeholder*="Song description"]', 
        'textarea[placeholder*="prompt"]',
        'input[placeholder*="Describe"]',
        '[data-testid="prompt-input"]',
        '[data-testid="description-input"]'
      ],
      lyrics: [
        'textarea[placeholder*="lyrics"]',
        'textarea[placeholder*="Lyrics"]',
        'textarea[placeholder*="Custom lyrics"]',
        '[data-testid="lyrics-input"]',
        '[data-testid="custom-lyrics"]'
      ],
      generateButton: [
        'button[data-testid="create-button"]',
        'button[data-testid="generate-button"]',
        'button:contains("Create")',
        'button:contains("Generate")',
        'button[type="submit"]'
      ],
      container: [
        '[data-testid="create-form"]',
        '[data-testid="generation-form"]',
        'form[action*="create"]',
        '.create-page',
        '.generation-container'
      ]
    }
  },
  
  // Strategy 2: Legacy Suno interface
  legacy: {
    name: 'Legacy Suno Interface',
    selectors: {
      prompt: [
        'textarea[name="prompt"]',
        'textarea[name="description"]',
        '#prompt',
        '#description'
      ],
      lyrics: [
        'textarea[name="lyrics"]',
        '#lyrics',
        '#custom-lyrics'
      ],
      generateButton: [
        '#generate',
        '#create',
        '.generate-btn',
        '.create-btn'
      ],
      container: [
        '.create-container',
        '.main-form',
        '#create-form'
      ]
    }
  },
  
  // Strategy 3: Generic fallback
  generic: {
    name: 'Generic Fallback',
    selectors: {
      prompt: [
        'textarea:first-of-type',
        'input[type="text"]:first-of-type'
      ],
      lyrics: [
        'textarea:nth-of-type(2)',
        'textarea:last-of-type'
      ],
      generateButton: [
        'button[type="submit"]',
        'button:last-of-type'
      ],
      container: [
        'main',
        'body',
        '#root'
      ]
    }
  }
};

// Initialize extension
function initialize() {
  if (isInitialized) return;
  
  console.log('Inicializando Son1k Suno Bridge...');
  
  // Wait for page to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(initializeWithRetry, 1000);
    });
  } else {
    setTimeout(initializeWithRetry, 1000);
  }
}

function initializeWithRetry(attempt = 1) {
  try {
    console.log(`Intento de inicialización ${attempt}/${CONFIG.retryAttempts}`);
    
    const strategy = detectPageLayout();
    if (strategy) {
      console.log(`Estrategia detectada: ${strategy.name}`);
      
      const elements = findPageElements(strategy);
      if (elements.container) {
        createFloatingButton(elements);
        setupMutationObserver(elements);
        isInitialized = true;
        console.log('✅ Son1k Bridge inicializado exitosamente');
        return;
      }
    }
    
    // Retry if not successful
    if (attempt < CONFIG.retryAttempts) {
      console.log(`❌ Inicialización fallida, reintentando en ${CONFIG.retryDelay}ms...`);
      retryTimer = setTimeout(() => {
        initializeWithRetry(attempt + 1);
      }, CONFIG.retryDelay);
    } else {
      console.warn('❌ No se pudo inicializar Son1k Bridge después de múltiples intentos');
    }
    
  } catch (error) {
    console.error('Error en inicialización:', error);
  }
}

function detectPageLayout() {
  // Try each strategy until one works
  for (const [key, strategy] of Object.entries(SELECTOR_STRATEGIES)) {
    const elements = findPageElements(strategy);
    if (elements.container && (elements.prompt || elements.lyrics)) {
      return strategy;
    }
  }
  return null;
}

function findPageElements(strategy) {
  const elements = {};
  
  for (const [elementType, selectors] of Object.entries(strategy.selectors)) {
    for (const selector of selectors) {
      try {
        const element = findElementWithSelector(selector);
        if (element) {
          elements[elementType] = element;
          break;
        }
      } catch (error) {
        console.debug(`Selector failed: ${selector}`, error);
      }
    }
  }
  
  return elements;
}

function findElementWithSelector(selector) {
  // Handle :contains() pseudo-selector manually
  if (selector.includes(':contains(')) {
    const match = selector.match(/(.*):contains\("([^"]+)"\)/);
    if (match) {
      const [, baseSelector, text] = match;
      const elements = document.querySelectorAll(baseSelector);
      for (const el of elements) {
        if (el.textContent.includes(text)) {
          return el;
        }
      }
    }
    return null;
  }
  
  return document.querySelector(selector);
}

function createFloatingButton(elements) {
  // Remove existing button
  removeExistingButton();
  
  // Create new button
  const button = document.createElement('button');
  button.id = CONFIG.buttonId;
  button.textContent = CONFIG.buttonText;
  button.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 10000;
    background: linear-gradient(135deg, #00FFE7, #00b4d8);
    color: #000;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 255, 231, 0.3);
    transition: all 0.3s ease;
    user-select: none;
    font-family: system-ui, -apple-system, sans-serif;
  `;
  
  // Hover effects
  button.addEventListener('mouseenter', () => {
    button.style.transform = 'translateY(-2px)';
    button.style.boxShadow = '0 6px 16px rgba(0, 255, 231, 0.4)';
  });
  
  button.addEventListener('mouseleave', () => {
    button.style.transform = 'translateY(0)';
    button.style.boxShadow = '0 4px 12px rgba(0, 255, 231, 0.3)';
  });
  
  // Click handler
  button.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    handleSendToSon1k(elements);
  });
  
  // Add to page
  document.body.appendChild(button);
  currentButton = button;
  
  console.log('✅ Botón flotante creado');
}

function removeExistingButton() {
  const existing = document.getElementById(CONFIG.buttonId);
  if (existing) {
    existing.remove();
  }
  currentButton = null;
}

async function handleSendToSon1k(elements) {
  if (isProcessing) return;
  
  try {
    isProcessing = true;
    
    // Update button state
    const originalText = currentButton.textContent;
    currentButton.textContent = 'Enviando...';
    currentButton.style.opacity = '0.7';
    currentButton.disabled = true;
    
    // Extract data from page
    const musicData = extractMusicData(elements);
    
    if (!musicData.prompt && !musicData.lyrics) {
      throw new Error('No se encontró contenido para enviar');
    }
    
    console.log('📤 Enviando datos a Son1k:', musicData);
    
    // Send to background script
    const response = await chrome.runtime.sendMessage({
      type: 'SEND_TO_SON1K',
      data: musicData
    });
    
    if (response && response.success) {
      showSuccessNotification('✅ Enviado a Son1k exitosamente!');
      console.log('✅ Datos enviados exitosamente:', response.data);
    } else {
      throw new Error(response?.error || 'Error desconocido');
    }
    
  } catch (error) {
    console.error('❌ Error enviando a Son1k:', error);
    showErrorNotification(`❌ Error: ${error.message}`);
  } finally {
    // Restore button state
    setTimeout(() => {
      if (currentButton) {
        currentButton.textContent = CONFIG.buttonText;
        currentButton.style.opacity = '1';
        currentButton.disabled = false;
      }
      isProcessing = false;
    }, 1000);
  }
}

function extractMusicData(elements) {
  const data = {
    prompt: '',
    lyrics: '',
    mode: 'original',
    url: window.location.href,
    timestamp: new Date().toISOString()
  };
  
  // Extract prompt/description
  if (elements.prompt) {
    data.prompt = elements.prompt.value || elements.prompt.textContent || '';
  }
  
  // Extract lyrics
  if (elements.lyrics) {
    data.lyrics = elements.lyrics.value || elements.lyrics.textContent || '';
  }
  
  // Determine mode
  if (data.lyrics && data.lyrics.trim()) {
    data.mode = 'original';
  } else {
    data.mode = 'instrumental';
  }
  
  // Clean data
  data.prompt = data.prompt.trim().substring(0, 1000);
  data.lyrics = data.lyrics.trim().substring(0, 2000);
  
  return data;
}

function showSuccessNotification(message) {
  showNotification(message, '#22c55e');
}

function showErrorNotification(message) {
  showNotification(message, '#ef4444');
}

function showNotification(message, color) {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10001;
    background: ${color};
    color: white;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    font-family: system-ui, -apple-system, sans-serif;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
    transform: translateX(100%);
    user-select: none;
  `;
  
  notification.textContent = message;
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);
  
  // Auto remove
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 3000);
}

function setupMutationObserver(elements) {
  // Clean up existing observer
  if (mutationObserver) {
    mutationObserver.disconnect();
  }
  
  // Watch for DOM changes to re-inject button if needed
  mutationObserver = new MutationObserver((mutations) => {
    let shouldReinject = false;
    
    for (const mutation of mutations) {
      // Check if our button was removed
      if (mutation.type === 'childList') {
        for (const node of mutation.removedNodes) {
          if (node.id === CONFIG.buttonId || 
              (node.querySelector && node.querySelector(`#${CONFIG.buttonId}`))) {
            shouldReinject = true;
            break;
          }
        }
      }
    }
    
    if (shouldReinject && !document.getElementById(CONFIG.buttonId)) {
      console.log('🔄 Re-inyectando botón después de cambio DOM');
      setTimeout(() => {
        createFloatingButton(elements);
      }, 500);
    }
  });
  
  // Start observing
  mutationObserver.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  console.log('👁️ Observer de mutaciones configurado');
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (mutationObserver) {
    mutationObserver.disconnect();
  }
  if (retryTimer) {
    clearTimeout(retryTimer);
  }
});

// Handle dynamic navigation (SPA)
let lastUrl = window.location.href;
function checkForUrlChange() {
  if (window.location.href !== lastUrl) {
    lastUrl = window.location.href;
    console.log('🔄 URL cambió, reinicializando...', lastUrl);
    
    // Reset state
    isInitialized = false;
    removeExistingButton();
    
    // Reinitialize after delay
    setTimeout(() => {
      initialize();
    }, 1000);
  }
}

// Check for URL changes periodically (for SPAs)
setInterval(checkForUrlChange, 2000);

// ================================
// PROCESAMIENTO AUTOMÁTICO DE JOBS
// ================================

// Escuchar mensajes del background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Content script received message:', message.type);
  
  if (message.type === 'PROCESS_JOB') {
    processJobAutomatically(message.job)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ 
        success: false, 
        error: error.message 
      }));
    return true; // Mantener canal abierto para respuesta asíncrona
  }
});

// Procesar job automáticamente
async function processJobAutomatically(job) {
  console.log('🤖 Processing job automatically:', job);
  
  try {
    // Obtener elementos del DOM
    const elements = await detectSunoElements();
    
    if (!elements.prompt && !elements.lyrics) {
      throw new Error('No se encontraron elementos de Suno para procesar');
    }
    
    // Rellenar campos
    await fillJobData(job, elements);
    
    // Esperar un momento para que se procesen los cambios
    await sleep(1000);
    
    // Hacer clic en generar
    const generateButton = await findGenerateButton();
    if (!generateButton) {
      throw new Error('No se encontró el botón de generar');
    }
    
    console.log('🎯 Clicking generate button...');
    generateButton.click();
    
    // Esperar a que se complete la generación
    const result = await waitForGeneration();
    
    console.log('✅ Job processed successfully:', result);
    return {
      success: true,
      audio_url: result.audio_url,
      preview_url: result.preview_url
    };
    
  } catch (error) {
    console.error('❌ Error processing job:', error);
    throw error;
  }
}

// Rellenar datos del job en el formulario
async function fillJobData(job, elements) {
  try {
    // Rellenar prompt si existe
    if (job.prompt && elements.prompt) {
      console.log('📝 Filling prompt:', job.prompt);
      await fillInput(elements.prompt, job.prompt);
    }
    
    // Rellenar lyrics si existe
    if (job.lyrics && elements.lyrics) {
      console.log('🎵 Filling lyrics:', job.lyrics);
      await fillInput(elements.lyrics, job.lyrics);
    }
    
    // Aquí se podría agregar lógica para modo instrumental vs original
    console.log('📋 Job data filled successfully');
    
  } catch (error) {
    console.error('❌ Error filling job data:', error);
    throw error;
  }
}

// Rellenar input con timeout
async function fillInput(element, value) {
  return new Promise((resolve, reject) => {
    try {
      // Foco en el elemento
      element.focus();
      
      // Limpiar contenido existente
      element.value = '';
      element.textContent = '';
      
      // Simular typing
      element.value = value;
      element.textContent = value;
      
      // Disparar eventos necesarios
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
      element.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
      
      setTimeout(resolve, 500);
    } catch (error) {
      reject(error);
    }
  });
}

// Buscar botón de generar
async function findGenerateButton() {
  const strategies = [
    () => document.querySelector('button[data-testid="create-button"]'),
    () => document.querySelector('button[data-testid="generate-button"]'),
    () => document.querySelector('button[type="submit"]'),
    () => Array.from(document.querySelectorAll('button')).find(btn => 
      btn.textContent.toLowerCase().includes('create') ||
      btn.textContent.toLowerCase().includes('generate')
    )
  ];
  
  for (const strategy of strategies) {
    const button = strategy();
    if (button && !button.disabled) {
      return button;
    }
  }
  
  throw new Error('No se encontró botón de generar disponible');
}

// Esperar a que termine la generación
async function waitForGeneration() {
  console.log('⏳ Waiting for generation to complete...');
  
  const maxWaitTime = 300000; // 5 minutos máximo
  const checkInterval = 2000; // Verificar cada 2 segundos
  const startTime = Date.now();
  
  return new Promise((resolve, reject) => {
    const checkGeneration = () => {
      const elapsed = Date.now() - startTime;
      
      if (elapsed > maxWaitTime) {
        reject(new Error('Timeout esperando generación'));
        return;
      }
      
      // Buscar elementos que indiquen que terminó
      const audioElements = document.querySelectorAll('audio');
      const downloadLinks = document.querySelectorAll('a[download]');
      const playButtons = document.querySelectorAll('button[aria-label*="play"]');
      
      // Si encontramos audio o enlaces de descarga, la generación terminó
      if (audioElements.length > 0 || downloadLinks.length > 0 || playButtons.length > 0) {
        console.log('🎉 Generation completed!');
        
        // Extraer URLs
        let audio_url = null;
        let preview_url = null;
        
        if (audioElements.length > 0) {
          audio_url = audioElements[0].src;
          preview_url = audio_url; // Por ahora usar la misma URL
        }
        
        if (downloadLinks.length > 0) {
          audio_url = downloadLinks[0].href;
        }
        
        resolve({
          audio_url: audio_url,
          preview_url: preview_url
        });
        return;
      }
      
      // Verificar si hay errores
      const errorElements = document.querySelectorAll('[data-testid="error"], .error, .alert-error');
      if (errorElements.length > 0) {
        reject(new Error('Error en la generación: ' + errorElements[0].textContent));
        return;
      }
      
      // Continuar esperando
      setTimeout(checkGeneration, checkInterval);
    };
    
    // Iniciar verificación
    setTimeout(checkGeneration, checkInterval);
  });
}

// Función de utilidad para sleep
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Initialize immediately
initialize();

console.log('✨ Son1k Suno Bridge content script loaded successfully');