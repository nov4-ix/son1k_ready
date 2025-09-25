const express = require('express');
const { Api } = require('suno-api');
const cors = require('cors');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const app = express();

// Middleware avanzado con evasión máxima
app.use(express.json({ limit: '50mb' }));
app.use(cors({
  origin: true,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding', 'Connection', 'Upgrade-Insecure-Requests']
}));

// Headers de evasión avanzados
app.use((req, res, next) => {
  // Rotar User-Agent para máxima evasión
  const userAgents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
  ];
  
  res.setHeader('User-Agent', userAgents[Math.floor(Math.random() * userAgents.length)]);
  res.setHeader('X-Powered-By', 'Express');
  res.setHeader('Server', 'nginx/1.20.1');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  
  next();
});

// Clase de gestión de cuentas múltiples con evasión
class StealthAccountManager {
  constructor() {
    this.accounts = [];
    this.currentIndex = 0;
    this.lastRotation = Date.now();
    this.loadAccounts();
  }

  loadAccounts() {
    try {
      const configPath = path.join(__dirname, 'suno_accounts_stealth.json');
      if (fs.existsSync(configPath)) {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        this.accounts = config.accounts || [];
        this.stealthSettings = config.stealth_settings || {};
        this.evasionPatterns = config.evasion_patterns || {};
        console.log(`🔒 Cargadas ${this.accounts.length} cuentas stealth`);
      } else {
        console.warn('⚠️ Archivo de configuración de cuentas no encontrado');
      }
    } catch (error) {
      console.error('❌ Error cargando cuentas:', error);
    }
  }

  getBestAccount() {
    if (this.accounts.length === 0) {
      throw new Error('No hay cuentas disponibles');
    }

    // Ordenar por score (éxito - fallos - tiempo de uso)
    const sorted = this.accounts
      .filter(acc => acc.status === 'active')
      .sort((a, b) => {
        const scoreA = this.calculateScore(a);
        const scoreB = this.calculateScore(b);
        return scoreB - scoreA;
      });

    if (sorted.length === 0) {
      throw new Error('No hay cuentas activas disponibles');
    }

    return sorted[0];
  }

  calculateScore(account) {
    const now = Date.now();
    const timeSinceLastUse = now - (account.last_used || 0);
    const timePenalty = Math.min(timeSinceLastUse / 1000000, 10); // Penalty por tiempo
    const usagePenalty = (account.failure_count || 0) * 2; // Penalty por fallos
    const priorityBonus = (account.priority || 1) * 5; // Bonus por prioridad
    const successBonus = (account.success_count || 0) * 3; // Bonus por éxitos

    return successBonus - usagePenalty - timePenalty + priorityBonus;
  }

  rotateAccount() {
    this.currentIndex = (this.currentIndex + 1) % this.accounts.length;
    this.lastRotation = Date.now();
  }

  markSuccess(accountId) {
    const account = this.accounts.find(acc => acc.id === accountId);
    if (account) {
      account.success_count = (account.success_count || 0) + 1;
      account.last_used = Date.now();
    }
  }

  markFailure(accountId) {
    const account = this.accounts.find(acc => acc.id === accountId);
    if (account) {
      account.failure_count = (account.failure_count || 0) + 1;
      account.last_used = Date.now();
      
      // Si hay muchos fallos, poner en cooldown
      if (account.failure_count > 5) {
        account.status = 'cooldown';
        setTimeout(() => {
          account.status = 'active';
          account.failure_count = 0;
        }, (account.cooldown_minutes || 5) * 60 * 1000);
      }
    }
  }

  getRandomUserAgent() {
    const userAgents = [
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ];
    return userAgents[Math.floor(Math.random() * userAgents.length)];
  }
}

// Clase de generación stealth ultra-avanzada
class UltraStealthGenerator {
  constructor() {
    this.accountManager = new StealthAccountManager();
    this.retryAttempts = 3;
    this.delayBetweenAttempts = 2000;
    this.maxConcurrentRequests = 2;
    this.activeRequests = 0;
    this.requestHistory = [];
  }

  async generateWithUltraStealth(payload) {
    for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
      try {
        // Esperar si hay demasiadas peticiones concurrentes
        while (this.activeRequests >= this.maxConcurrentRequests) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }

        this.activeRequests++;

        // Obtener la mejor cuenta
        const account = this.accountManager.getBestAccount();
        
        // Crear instancia de Suno con la cuenta seleccionada
        const suno = new Api(account.cookie);

        // Delay aleatorio para evasión
        const randomDelay = Math.random() * 2000 + 1000;
        await new Promise(resolve => setTimeout(resolve, randomDelay));

        // Crear payload ultra-stealth
        const stealthPayload = this.createUltraStealthPayload(payload, account);

        console.log(`🔒 [STEALTH] Generando con cuenta ${account.id} (intento ${attempt + 1})`);

        // Generar con evasión máxima
        const result = await suno.generateClips(stealthPayload);

        // Marcar éxito
        this.accountManager.markSuccess(account.id);
        this.requestHistory.push({
          timestamp: Date.now(),
          account: account.id,
          success: true,
          attempt: attempt + 1
        });

        console.log(`✅ [STEALTH] Generación exitosa con cuenta ${account.id}`);

        return {
          result,
          account: account.id,
          stealth: true,
          attempt: attempt + 1
        };

      } catch (error) {
        console.log(`⚠️ [STEALTH] Intento ${attempt + 1} falló: ${error.message}`);

        // Marcar fallo
        if (this.accountManager.accounts.length > 0) {
          const account = this.accountManager.getBestAccount();
          this.accountManager.markFailure(account.id);
        }

        // Rotar cuenta si hay múltiples disponibles
        if (this.accountManager.accounts.length > 1) {
          this.accountManager.rotateAccount();
        }

        if (attempt === this.retryAttempts - 1) {
          throw error;
        }

        // Delay exponencial con jitter
        const delay = this.delayBetweenAttempts * Math.pow(2, attempt) + Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));

      } finally {
        this.activeRequests--;
      }
    }
  }

  createUltraStealthPayload(originalPayload, account) {
    const stealthPayload = { ...originalPayload };

    // Obfuscación de prompt
    if (stealthPayload.prompt) {
      stealthPayload.prompt = this.obfuscatePrompt(stealthPayload.prompt);
    }

    // Variaciones de título
    const titlePrefixes = this.accountManager.evasionPatterns?.title_prefixes || ['Generated'];
    const randomPrefix = titlePrefixes[Math.floor(Math.random() * titlePrefixes.length)];
    stealthPayload.title = `${randomPrefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Modificar tags para evasión
    if (stealthPayload.tags) {
      const tagVariations = this.accountManager.evasionPatterns?.tag_variations || [];
      const randomTags = tagVariations[Math.floor(Math.random() * tagVariations.length)];
      stealthPayload.tags = `${stealthPayload.tags}, ${randomTags}`;
    }

    // Agregar timestamp para unicidad
    stealthPayload.timestamp = Date.now();
    stealthPayload.session_id = crypto.randomUUID();

    // Headers adicionales para evasión
    stealthPayload.headers = {
      'User-Agent': account.user_agent || this.accountManager.getRandomUserAgent(),
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1'
    };

    return stealthPayload;
  }

  obfuscatePrompt(prompt) {
    const variations = this.accountManager.evasionPatterns?.prompt_variations || ['', ' '];
    const randomVariation = variations[Math.floor(Math.random() * variations.length)];
    
    // Agregar variación aleatoria
    let obfuscated = prompt + randomVariation;
    
    // Agregar caracteres invisibles ocasionalmente
    if (Math.random() < 0.3) {
      const invisibleChars = ['\u200B', '\u200C', '\u200D', '\uFEFF'];
      const randomChar = invisibleChars[Math.floor(Math.random() * invisibleChars.length)];
      obfuscated = obfuscated + randomChar;
    }
    
    return obfuscated.trim();
  }

  getStats() {
    return {
      accounts: this.accountManager.accounts.map(acc => ({
        id: acc.id,
        email: acc.email,
        success_count: acc.success_count || 0,
        failure_count: acc.failure_count || 0,
        status: acc.status,
        last_used: acc.last_used || 0
      })),
      activeRequests: this.activeRequests,
      maxConcurrent: this.maxConcurrentRequests,
      requestHistory: this.requestHistory.slice(-10) // Últimos 10 requests
    };
  }
}

// Inicializar generador stealth
const stealthGenerator = new UltraStealthGenerator();

// Endpoint principal de generación stealth
app.post('/generate-music', async (req, res) => {
  const { prompt, lyrics = '', style = 'profesional' } = req.body;

  console.log(`🔒 [ULTRA-STEALTH] Generando música: ${prompt.substring(0, 50)}...`);

  try {
    // Validar entrada
    if (!prompt || prompt.trim().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Prompt es requerido'
      });
    }

    // Crear payload optimizado para evasión máxima
    const payload = {
      prompt: prompt.trim(),
      makeInstrumental: !lyrics || lyrics.trim().length === 0,
      tags: style,
      title: `Stealth-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };

    console.log(`🔒 [ULTRA-STEALTH] Payload optimizado:`, {
      prompt: payload.prompt.substring(0, 50) + '...',
      makeInstrumental: payload.makeInstrumental,
      tags: payload.tags,
      title: payload.title
    });

    // Generar usando el generador ultra-stealth
    const { result: clips, account, stealth, attempt } = await stealthGenerator.generateWithUltraStealth(payload);

    console.log(`✅ [ULTRA-STEALTH] Clips generados: ${clips?.length || 0} versiones con cuenta ${account}`);

    // Procesar resultados con validación
    const audioUrls = [];
    const generatedLyrics = [];
    const metadata = [];

    if (clips && Array.isArray(clips) && clips.length > 0) {
      clips.forEach((clip, index) => {
        if (clip && typeof clip === 'object') {
          // Validar y agregar URL de audio
          if (clip.audio_url && typeof clip.audio_url === 'string') {
            audioUrls.push(clip.audio_url);
          }

          // Validar y agregar letras
          if (clip.lyrics && typeof clip.lyrics === 'string') {
            generatedLyrics.push(clip.lyrics);
          }

          // Agregar metadata
          metadata.push({
            index: index,
            id: clip.id || `clip_${index}`,
            title: clip.title || `Track ${index + 1}`,
            duration: clip.duration || 180,
            status: clip.status || 'completed'
          });
        }
      });
    }

    // Validar que se generó al menos un audio
    if (audioUrls.length === 0) {
      throw new Error('No se generaron URLs de audio válidas');
    }

    // Resultado exitoso con metadata completa
    const response = {
      success: true,
      audioUrls: audioUrls,
      lyrics: generatedLyrics.length > 0 ? generatedLyrics[0] : lyrics,
      prompt: prompt,
      style: style,
      duration: 180,
      status: 'completed',
      stealth: {
        enabled: true,
        account_used: account,
        attempt: attempt,
        evasion_level: 'maximum'
      },
      metadata: {
        totalClips: clips?.length || 0,
        audioCount: audioUrls.length,
        lyricsCount: generatedLyrics.length,
        generationTime: new Date().toISOString(),
        stealthMode: true
      },
      clips: clips
    };

    console.log(`🚀 [ULTRA-STEALTH] Generación exitosa: ${audioUrls.length} audios, ${generatedLyrics.length} letras`);

    res.json(response);

  } catch (error) {
    console.error(`❌ [ULTRA-STEALTH] Error en generación: ${error.message}`);

    // Respuesta de error detallada
    const errorResponse = {
      success: false,
      error: 'Error en generación: ' + error.message,
      timestamp: new Date().toISOString(),
      stealthMode: true,
      retryable: error.message.includes('timeout') || error.message.includes('network')
    };

    res.status(500).json(errorResponse);
  }
});

// Endpoint de salud avanzado
app.get('/health', (req, res) => {
  const stats = stealthGenerator.getStats();
  
  const healthData = {
    status: 'healthy',
    service: 'Suno Ultra-Stealth Wrapper Server',
    timestamp: new Date().toISOString(),
    version: '3.0.0-ultra-stealth',
    features: {
      stealthMode: true,
      multiAccount: true,
      accountRotation: true,
      retryMechanism: true,
      evasiveHeaders: true,
      payloadObfuscation: true
    },
    accounts: {
      total: stats.accounts.length,
      active: stats.accounts.filter(acc => acc.status === 'active').length,
      cooldown: stats.accounts.filter(acc => acc.status === 'cooldown').length
    },
    stats: {
      activeRequests: stats.activeRequests,
      maxConcurrent: stats.maxConcurrent,
      recentRequests: stats.requestHistory.length
    }
  };

  res.json(healthData);
});

// Endpoint para estadísticas detalladas
app.get('/stats', (req, res) => {
  const stats = stealthGenerator.getStats();
  res.json(stats);
});

// Endpoint para agregar cuentas dinámicamente
app.post('/add-account', (req, res) => {
  const { email, cookie, priority = 1, max_daily_usage = 50 } = req.body;

  if (!email || !cookie) {
    return res.status(400).json({
      success: false,
      error: 'Email y cookie son requeridos'
    });
  }

  try {
    const newAccount = {
      id: `account_${Date.now()}`,
      email: email,
      cookie: cookie,
      priority: priority,
      max_daily_usage: max_daily_usage,
      cooldown_minutes: 5,
      user_agent: stealthGenerator.accountManager.getRandomUserAgent(),
      last_used: 0,
      success_count: 0,
      failure_count: 0,
      status: 'active'
    };

    stealthGenerator.accountManager.accounts.push(newAccount);
    
    res.json({
      success: true,
      message: 'Cuenta agregada exitosamente',
      account: newAccount,
      totalAccounts: stealthGenerator.accountManager.accounts.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Servir página de prueba stealth
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
  <title>🔒 Son1k Ultra-Stealth Generator</title>
  <style>
    body { 
      font-family: Arial, sans-serif; 
      max-width: 800px; 
      margin: 0 auto; 
      padding: 20px;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      color: white;
    }
    .container {
      background: rgba(255,255,255,0.1);
      padding: 30px;
      border-radius: 15px;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255,255,255,0.2);
    }
    input, button { 
      padding: 12px; 
      margin: 10px 0; 
      border: none; 
      border-radius: 8px;
      font-size: 16px;
    }
    input { width: 70%; background: rgba(255,255,255,0.9); color: #333; }
    button { 
      background: #4CAF50; 
      color: white; 
      cursor: pointer;
      width: 25%;
    }
    button:hover { background: #45a049; }
    #loader { 
      display: none; 
      color: #FFD700; 
      font-weight: bold;
    }
    audio { 
      width: 100%; 
      margin: 20px 0; 
      display: none;
    }
    #download { 
      display: none; 
      background: #2196F3; 
      color: white; 
      padding: 10px 20px; 
      text-decoration: none; 
      border-radius: 5px;
      margin: 10px 0;
    }
    .status { 
      margin: 20px 0; 
      padding: 15px; 
      border-radius: 8px; 
      background: rgba(255,255,255,0.2);
    }
    .stealth-indicator {
      background: #ff6b6b;
      color: white;
      padding: 5px 10px;
      border-radius: 20px;
      font-size: 12px;
      margin: 10px 0;
      display: inline-block;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔒 Son1k Ultra-Stealth Generator</h1>
    <p>Generador de música con tecnología stealth ultra-avanzada y múltiples cuentas</p>
    
    <div class="stealth-indicator">🔒 MODO STEALTH ACTIVO</div>
    
    <input type="text" id="prompt" placeholder="Describe tu canción... (ej: 'una balada rock sobre el amor')">
    <button onclick="generate()">🚀 Generar Música Stealth</button>
    
    <div id="loader" style="display:none;">
      <div>🔒 Generando música con tecnología ultra-stealth...</div>
      <div>⏳ Rotando cuentas y aplicando evasión...</div>
    </div>
    
    <audio id="player" controls></audio>
    <a id="download" download>📥 Descargar MP3</a>
    
    <div class="status" id="status"></div>
  </div>

  <script>
    async function generate() {
      const prompt = document.getElementById('prompt').value;
      const loader = document.getElementById('loader');
      const status = document.getElementById('status');
      
      if (!prompt.trim()) {
        status.innerHTML = '❌ Por favor ingresa una descripción de tu canción';
        status.style.background = 'rgba(255,0,0,0.3)';
        return;
      }
      
      loader.style.display = 'block';
      status.innerHTML = '';
      
      try {
        const response = await fetch('http://localhost:3001/generate-music', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            prompt: prompt,
            style: 'profesional'
          })
        });
        
        const data = await response.json();
        loader.style.display = 'none';
        
        if (data.success) {
          status.innerHTML = \`✅ ¡Música generada con tecnología stealth! (\${data.metadata.audioCount} versiones)<br>
          <small>Cuenta usada: \${data.stealth.account_used} | Intento: \${data.stealth.attempt}</small>\`;
          status.style.background = 'rgba(0,255,0,0.3)';
          
          const audio = document.getElementById('player');
          audio.src = data.audioUrls[0];
          audio.style.display = 'block';
          
          const download = document.getElementById('download');
          download.href = data.audioUrls[0];
          download.download = \`son1k-stealth-\${Date.now()}.mp3\`;
          download.style.display = 'block';
          
          // Mostrar letras si están disponibles
          if (data.lyrics) {
            status.innerHTML += \`<br><br><strong>Letras generadas:</strong><br><em>\${data.lyrics}</em>\`;
          }
        } else {
          status.innerHTML = \`❌ Error: \${data.error}\`;
          status.style.background = 'rgba(255,0,0,0.3)';
        }
      } catch (error) {
        loader.style.display = 'none';
        status.innerHTML = \`❌ Error de conexión: \${error.message}\`;
        status.style.background = 'rgba(255,0,0,0.3)';
      }
    }
    
    // Cargar estadísticas al inicio
    async function loadStats() {
      try {
        const response = await fetch('http://localhost:3001/stats');
        const stats = await response.json();
        console.log('📊 Estadísticas stealth:', stats);
      } catch (error) {
        console.log('⚠️ No se pudieron cargar las estadísticas');
      }
    }
    
    loadStats();
  </script>
</body>
</html>
  `);
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`🔒 Suno Ultra-Stealth Wrapper Server ejecutándose en puerto ${PORT}`);
  console.log(`🌐 Interfaz web: http://localhost:${PORT}`);
  console.log(`📊 Estadísticas: http://localhost:${PORT}/stats`);
  console.log(`💚 Salud: http://localhost:${PORT}/health`);
  console.log(`🔒 Modo stealth ultra-avanzado activado`);
  console.log(`👥 Soporte para múltiples cuentas habilitado`);
});






