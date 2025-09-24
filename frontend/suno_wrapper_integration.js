/**
 * 🎵 Son1k Suno Wrapper Integration
 * Integración robusta entre frontend y wrapper Node.js de Suno
 */

class SunoWrapperIntegration {
  constructor() {
    this.wrapperUrl = 'http://localhost:3001';
    this.apiUrl = 'http://localhost:8000';
    this.isConnected = false;
    this.currentJob = null;
    this.pollingInterval = null;
    this.maxPollingTime = 300000; // 5 minutos
    this.pollingIntervalMs = 2000; // 2 segundos
    this.stealthMode = true; // Modo stealth activado
  }

  /**
   * Inicializar la integración
   */
  async initialize() {
    try {
      console.log('🎵 Inicializando integración Suno Wrapper...');
      
      // Verificar conexión con wrapper
      const wrapperStatus = await this.checkWrapperConnection();
      if (!wrapperStatus) {
        throw new Error('Wrapper de Suno no disponible');
      }
      
      // Verificar conexión con API principal
      const apiStatus = await this.checkApiConnection();
      if (!apiStatus) {
        throw new Error('API principal no disponible');
      }
      
      this.isConnected = true;
      console.log('✅ Integración Suno Wrapper inicializada correctamente');
      return true;
      
    } catch (error) {
      console.error('❌ Error inicializando integración:', error);
      this.isConnected = false;
      return false;
    }
  }

  /**
   * Verificar conexión con wrapper
   */
  async checkWrapperConnection() {
    try {
      const response = await fetch(`${this.wrapperUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Wrapper conectado:', data.status);
        return true;
      }
      return false;
    } catch (error) {
      console.warn('⚠️ Wrapper no disponible:', error.message);
      return false;
    }
  }

  /**
   * Verificar conexión con API principal
   */
  async checkApiConnection() {
    try {
      const response = await fetch(`${this.apiUrl}/api/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ API principal conectada:', data.api);
        return true;
      }
      return false;
    } catch (error) {
      console.warn('⚠️ API principal no disponible:', error.message);
      return false;
    }
  }

  /**
   * Generar música usando el wrapper de Suno
   */
  async generateMusic(prompt, lyrics = '', style = 'profesional', instrumental = false) {
    if (!this.isConnected) {
      throw new Error('Integración no inicializada');
    }

    try {
      console.log('🔒 [ULTRA-STEALTH] Iniciando generación ultra-indetectable...');
      
      // Preparar datos para el wrapper ultra-stealth
      const wrapperData = {
        prompt: prompt.trim(),
        lyrics: lyrics.trim(),
        style: style,
        instrumental: instrumental || !lyrics.trim(),
        ultraStealth: true
      };

      console.log('📝 Datos enviados al wrapper:', {
        prompt: wrapperData.prompt.substring(0, 50) + '...',
        style: wrapperData.style,
        instrumental: wrapperData.makeInstrumental
      });

      // Enviar al wrapper de Suno
      const response = await fetch(`${this.wrapperUrl}/generate-music`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Ultra-Stealth': 'true',
          'X-Stealth-Level': 'ULTRA',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify(wrapperData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Error del wrapper: ${errorData.error || response.statusText}`);
      }

      const result = await response.json();
      console.log('✅ Respuesta del wrapper:', result);

      if (result.success) {
        // Crear job para tracking
        this.currentJob = {
          id: `wrapper_${Date.now()}`,
          status: 'completed',
          result: result,
          timestamp: new Date().toISOString()
        };

        return {
          success: true,
          jobId: this.currentJob.id,
          audioUrls: result.audioUrls || [],
          lyrics: result.lyrics || lyrics,
          prompt: prompt,
          style: style,
          metadata: result.metadata || {},
          source: 'suno_wrapper'
        };
      } else {
        throw new Error(result.error || 'Error desconocido en el wrapper');
      }

    } catch (error) {
      console.error('❌ Error en generación con wrapper:', error);
      throw error;
    }
  }

  /**
   * Generar música con fallback a API principal
   */
  async generateMusicWithFallback(prompt, lyrics = '', style = 'profesional', instrumental = false) {
    try {
      // Intentar primero con wrapper de Suno
      console.log('🎵 Intentando generación con Suno Wrapper...');
      return await this.generateMusic(prompt, lyrics, style, instrumental);
      
    } catch (wrapperError) {
      console.warn('⚠️ Wrapper falló, usando API principal como fallback:', wrapperError.message);
      
      try {
        // Fallback a API principal
        const response = await fetch(`${this.apiUrl}/api/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
          },
          body: JSON.stringify({
            prompt: prompt,
            lyrics: lyrics,
            style: style,
            instrumental: instrumental
          })
        });

        if (!response.ok) {
          throw new Error(`API principal falló: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('✅ Fallback exitoso con API principal');

        return {
          success: true,
          jobId: result.job_id || `fallback_${Date.now()}`,
          audioUrls: [], // API principal no devuelve URLs directas
          lyrics: result.lyrics || lyrics,
          prompt: prompt,
          style: style,
          metadata: {
            source: 'api_fallback',
            wrapper_error: wrapperError.message
          },
          source: 'api_fallback'
        };

      } catch (apiError) {
        console.error('❌ Ambos sistemas fallaron:', apiError);
        throw new Error(`Generación falló: Wrapper (${wrapperError.message}) y API (${apiError.message})`);
      }
    }
  }

  /**
   * Obtener estadísticas del wrapper
   */
  async getWrapperStats() {
    try {
      const response = await fetch(`${this.wrapperUrl}/stats`);
      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.warn('⚠️ No se pudieron obtener estadísticas:', error);
      return null;
    }
  }

  /**
   * Agregar cookie al wrapper
   */
  async addCookieToWrapper(cookie) {
    try {
      const response = await fetch(`${this.wrapperUrl}/add-cookie`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cookie: cookie })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Cookie agregada al wrapper:', result.message);
        return true;
      }
      return false;
    } catch (error) {
      console.error('❌ Error agregando cookie:', error);
      return false;
    }
  }

  /**
   * Detener polling si está activo
   */
  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  /**
   * Limpiar estado
   */
  cleanup() {
    this.stopPolling();
    this.currentJob = null;
    this.isConnected = false;
  }
}

// Instancia global
window.sunoWrapper = new SunoWrapperIntegration();

// Función de conveniencia para el frontend
window.generateMusicWithSuno = async function(prompt, lyrics = '', style = 'profesional', instrumental = false) {
  try {
    // Inicializar si no está conectado
    if (!window.sunoWrapper.isConnected) {
      const initialized = await window.sunoWrapper.initialize();
      if (!initialized) {
        throw new Error('No se pudo inicializar la integración con Suno');
      }
    }

    // Generar música con fallback
    return await window.sunoWrapper.generateMusicWithFallback(prompt, lyrics, style, instrumental);
    
  } catch (error) {
    console.error('❌ Error en generación musical:', error);
    throw error;
  }
};

// Función para mostrar estado de conexión
window.checkSunoStatus = async function() {
  try {
    const wrapperStats = await window.sunoWrapper.getWrapperStats();
    const apiStatus = await window.sunoWrapper.checkApiConnection();
    
    return {
      wrapper: {
        connected: wrapperStats !== null,
        stats: wrapperStats
      },
      api: {
        connected: apiStatus
      },
      integration: {
        initialized: window.sunoWrapper.isConnected
      }
    };
  } catch (error) {
    console.error('❌ Error verificando estado:', error);
    return {
      wrapper: { connected: false },
      api: { connected: false },
      integration: { initialized: false },
      error: error.message
    };
  }
};

console.log('🎵 Suno Wrapper Integration cargado');
console.log('📝 Funciones disponibles: generateMusicWithSuno(), checkSunoStatus()');
