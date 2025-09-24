const express = require('express');
const { Api } = require('suno-api');
const cors = require('cors');
const crypto = require('crypto');
const app = express();

// Middleware avanzado con evasión
app.use(express.json({ limit: '50mb' }));
app.use(cors({
  origin: true,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'User-Agent']
}));

// Headers de evasión
app.use((req, res, next) => {
  // Rotar User-Agent para evasión
  const userAgents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
  ];
  
  res.setHeader('User-Agent', userAgents[Math.floor(Math.random() * userAgents.length)]);
  res.setHeader('X-Powered-By', 'Express');
  res.setHeader('Server', 'nginx/1.20.1');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  
  next();
});

// Pool de cookies para rotación y evasión
class CookiePool {
  constructor() {
    this.cookies = [];
    this.currentIndex = 0;
    this.lastRotation = Date.now();
  }
  
  addCookie(cookie) {
    this.cookies.push({
      cookie: cookie,
      lastUsed: 0,
      successCount: 0,
      failureCount: 0,
      id: crypto.randomUUID()
    });
  }
  
  getBestCookie() {
    if (this.cookies.length === 0) {
      throw new Error('No hay cookies disponibles');
    }
    
    // Ordenar por éxito y tiempo de uso
    const sorted = this.cookies.sort((a, b) => {
      const scoreA = a.successCount - a.failureCount - (Date.now() - a.lastUsed) / 1000000;
      const scoreB = b.successCount - b.failureCount - (Date.now() - b.lastUsed) / 1000000;
      return scoreB - scoreA;
    });
    
    return sorted[0];
  }
  
  rotateCookie() {
    this.currentIndex = (this.currentIndex + 1) % this.cookies.length;
    this.lastRotation = Date.now();
  }
  
  markSuccess(cookieId) {
    const cookie = this.cookies.find(c => c.id === cookieId);
    if (cookie) {
      cookie.successCount++;
      cookie.lastUsed = Date.now();
    }
  }
  
  markFailure(cookieId) {
    const cookie = this.cookies.find(c => c.id === cookieId);
    if (cookie) {
      cookie.failureCount++;
      cookie.lastUsed = Date.now();
    }
  }
}

// Inicializar pool de cookies
const cookiePool = new CookiePool();

// Agregar cookies desde variables de entorno
if (process.env.SUNO_COOKIE) {
  cookiePool.addCookie(process.env.SUNO_COOKIE);
}

// Agregar cookies adicionales si están disponibles
if (process.env.SUNO_COOKIE_2) {
  cookiePool.addCookie(process.env.SUNO_COOKIE_2);
}

if (process.env.SUNO_COOKIE_3) {
  cookiePool.addCookie(process.env.SUNO_COOKIE_3);
}

// Clase de generación avanzada con evasión
class StealthSunoGenerator {
  constructor() {
    this.retryAttempts = 3;
    this.delayBetweenAttempts = 2000;
    this.maxConcurrentRequests = 2;
    this.activeRequests = 0;
  }
  
  async generateWithRetry(payload) {
    for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
      try {
        // Esperar si hay demasiadas peticiones concurrentes
        while (this.activeRequests >= this.maxConcurrentRequests) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        this.activeRequests++;
        
        // Obtener la mejor cookie
        const cookieData = cookiePool.getBestCookie();
        const suno = new Api(cookieData.cookie);
        
        // Agregar delay aleatorio para evasión
        const randomDelay = Math.random() * 2000 + 1000;
        await new Promise(resolve => setTimeout(resolve, randomDelay));
        
        // Generar con payload modificado para evasión
        const stealthPayload = this.createStealthPayload(payload);
        const result = await suno.generateClips(stealthPayload);
        
        // Marcar éxito
        cookiePool.markSuccess(cookieData.id);
        
        return result;
        
      } catch (error) {
        console.log(`⚠️ Intento ${attempt + 1} falló: ${error.message}`);
        
        // Marcar fallo
        if (cookiePool.cookies.length > 0) {
          const cookieData = cookiePool.getBestCookie();
          cookiePool.markFailure(cookieData.id);
        }
        
        // Rotar cookie si hay múltiples disponibles
        if (cookiePool.cookies.length > 1) {
          cookiePool.rotateCookie();
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
  
  createStealthPayload(originalPayload) {
    // Modificar el payload para evasión
    const stealthPayload = { ...originalPayload };
    
    // Agregar variaciones aleatorias al prompt
    const variations = [
      '', ' ', '  ', '   ',
      '🎵', '🎶', '🎼',
      '✨', '🌟', '💫'
    ];
    
    const randomVariation = variations[Math.floor(Math.random() * variations.length)];
    stealthPayload.prompt = (stealthPayload.prompt + randomVariation).trim();
    
    // Agregar timestamp para unicidad
    stealthPayload.timestamp = Date.now();
    
    // Modificar tags para evasión
    if (stealthPayload.tags) {
      const tagVariations = [
        stealthPayload.tags,
        `${stealthPayload.tags}, music`,
        `${stealthPayload.tags}, song`,
        `${stealthPayload.tags}, audio`,
        `${stealthPayload.tags}, generated`
      ];
      stealthPayload.tags = tagVariations[Math.floor(Math.random() * tagVariations.length)];
    }
    
    return stealthPayload;
  }
}

const stealthGenerator = new StealthSunoGenerator();

// Endpoint para generar música con esteroides
app.post('/generate-music', async (req, res) => {
  const { prompt, lyrics = '', style = 'profesional' } = req.body;
  
  console.log(`🎵 [STEALTH] Generando música: ${prompt}`);
  
  try {
    // Validar entrada
    if (!prompt || prompt.trim().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Prompt es requerido'
      });
    }
    
    // Crear payload optimizado para evasión
    const payload = {
      prompt: prompt.trim(),
      makeInstrumental: !lyrics || lyrics.trim().length === 0,
      tags: style,
      title: `Son1k-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
    
    console.log(`📝 [STEALTH] Payload optimizado:`, {
      prompt: payload.prompt.substring(0, 50) + '...',
      makeInstrumental: payload.makeInstrumental,
      tags: payload.tags,
      title: payload.title
    });
    
    // Generar usando el generador stealth
    const clips = await stealthGenerator.generateWithRetry(payload);
    
    console.log(`✅ [STEALTH] Clips generados: ${clips?.length || 0} versiones`);
    
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
      metadata: {
        totalClips: clips?.length || 0,
        audioCount: audioUrls.length,
        lyricsCount: generatedLyrics.length,
        generationTime: new Date().toISOString(),
        stealthMode: true
      },
      clips: clips
    };
    
    console.log(`🚀 [STEALTH] Generación exitosa: ${audioUrls.length} audios, ${generatedLyrics.length} letras`);
    
    res.json(response);
    
  } catch (error) {
    console.error(`❌ [STEALTH] Error en generación: ${error.message}`);
    
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
  const healthData = {
    status: 'healthy',
    service: 'Suno Stealth Wrapper Server',
    timestamp: new Date().toISOString(),
    version: '2.0.0-stealth',
    features: {
      stealthMode: true,
      cookieRotation: true,
      retryMechanism: true,
      evasiveHeaders: true
    },
    cookies: {
      total: cookiePool.cookies.length,
      active: cookiePool.cookies.filter(c => c.failureCount < 3).length
    },
    stats: {
      activeRequests: stealthGenerator.activeRequests,
      maxConcurrent: stealthGenerator.maxConcurrentRequests
    }
  };
  
  res.json(healthData);
});

// Endpoint para estadísticas del pool de cookies
app.get('/stats', (req, res) => {
  const stats = {
    cookies: cookiePool.cookies.map(c => ({
      id: c.id.substring(0, 8) + '...',
      successCount: c.successCount,
      failureCount: c.failureCount,
      lastUsed: new Date(c.lastUsed).toISOString(),
      score: c.successCount - c.failureCount
    })),
    totalRequests: stealthGenerator.activeRequests,
    uptime: process.uptime()
  };
  
  res.json(stats);
});

// Endpoint para agregar cookies dinámicamente
app.post('/add-cookie', (req, res) => {
  const { cookie } = req.body;
  
  if (!cookie || typeof cookie !== 'string') {
    return res.status(400).json({
      success: false,
      error: 'Cookie es requerida y debe ser string'
    });
  }
  
  try {
    cookiePool.addCookie(cookie);
    res.json({
      success: true,
      message: 'Cookie agregada exitosamente',
      totalCookies: cookiePool.cookies.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Servir página de prueba
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
  <title>🎵 Son1k Stealth Generator</title>
  <style>
    body { 
      font-family: Arial, sans-serif; 
      max-width: 800px; 
      margin: 0 auto; 
      padding: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    .container {
      background: rgba(255,255,255,0.1);
      padding: 30px;
      border-radius: 15px;
      backdrop-filter: blur(10px);
    }
    input, button { 
      padding: 12px; 
      margin: 10px 0; 
      border: none; 
      border-radius: 8px;
      font-size: 16px;
    }
    input { width: 70%; }
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
  </style>
</head>
<body>
  <div class="container">
    <h1>🎵 Son1k Stealth Generator</h1>
    <p>Generador de música con tecnología stealth avanzada</p>
    
    <input type="text" id="prompt" placeholder="Describe tu canción... (ej: 'una balada rock sobre el amor')">
    <button onclick="generate()">🚀 Generar Música</button>
    
    <div id="loader" style="display:none;">
      <div>🎵 Generando música con tecnología stealth...</div>
      <div>⏳ Esto puede tomar 1-2 minutos...</div>
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
          status.innerHTML = \`✅ ¡Música generada exitosamente! (\${data.metadata.audioCount} versiones)\`;
          status.style.background = 'rgba(0,255,0,0.3)';
          
          const audio = document.getElementById('player');
          audio.src = data.audioUrls[0];
          audio.style.display = 'block';
          
          const download = document.getElementById('download');
          download.href = data.audioUrls[0];
          download.download = \`son1k-\${Date.now()}.mp3\`;
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
        console.log('📊 Estadísticas del servidor:', stats);
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
  console.log(`🚀 Suno Stealth Wrapper Server ejecutándose en puerto ${PORT}`);
  console.log(`🌐 Interfaz web: http://localhost:${PORT}`);
  console.log(`📊 Estadísticas: http://localhost:${PORT}/stats`);
  console.log(`💚 Salud: http://localhost:${PORT}/health`);
  console.log(`📝 Configura SUNO_COOKIE en las variables de entorno`);
  console.log(`🔒 Modo stealth activado con ${cookiePool.cookies.length} cookies`);
});
