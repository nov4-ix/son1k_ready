const express = require('express');
const { Api } = require('suno-api');
const cors = require('cors');
const crypto = require('crypto');
const path = require('path');
const app = express();

// Middleware avanzado con evasión
app.use(express.json({ limit: '50mb' }));
app.use(cors({
  origin: true,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'User-Agent']
}));

// Servir archivos estáticos
app.use(express.static('.'));
app.use(express.static('frontend'));

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

// Cookie principal actualizada (2025-01-26)
const mainCookie = "singular_device_id=7fc059fe-34d2-4536-8406-f0b36aa40b7b; ajs_anonymous_id=f0f2cc3c-29fc-4994-b313-c6395f7f01c0; _gcl_au=1.1.868511209.1758919509; _axwrt=9b9ba50d-e181-42f3-b3ba-6e29ab3d8e52; _ga=GA1.1.770110903.1758919511; _fbp=fb.1.1758919510661.328611565502541669; _tt_enable_cookie=1; _ttp=01K63WBJXB88ET2RC9E2A9KYHB_.tt.1; _clck=8earmg%5E2%5Efzn%5E0%5E2095; _clsk=1f1uf60%5E1758919512719%5E1%5E1%5Ed.clarity.ms%2Fcollect; __client_uat=1758919517; __client_uat_U9tcbTPE=1758919517; clerk_active_context=sess_33Fj3jxICNV1wYuq68Oe1uGlOkE:; ax_visitor=%7B%22firstVisitTs%22%3A1758919509759%2C%22lastVisitTs%22%3Anull%2C%22currentVisitStartTs%22%3A1758919509759%2C%22ts%22%3A1758919521043%2C%22visitCount%22%3A1%7D; has_logged_in_before=true; _ga_7B0KEDD7XP=GS2.1.s1758919510$o1$g1$t1758919521$j49$l0$h0; _uetsid=6618fc20927811f0bf1e9b526665403c|uzkp91|2|fzn|0|2084; ttcsid=1758919510980::O9iz4ZcNze1EwWuHscqC.1.1758919522519.0; ttcsid_CT67HURC77UB52N3JFBG=1758919510980::yf4HoWwGiszr_EvqtWuF.1.1758919522519.0; _uetvid=75e947607c9711f0a0a265429931a928|1d4160k|1758919523618|2|1|bat.bing.com/p/conversions/c/b; afUserId=5bf63ba8-447a-4a22-a1f8-14ea1144d9d1-p; AF_SYNC=1758919525121; __stripe_mid=3ba32b8c-8f46-4645-aa1e-4005841991d0e5a982; __stripe_sid=7a9b36cc-af86-4d38-bf1c-edeeb4acb60dfac6ee; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg5MjMyMDksImZ2YSI6WzEsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ycXBaSFh1U05Ta0t2ZUFoa2Z6RVMxNGRnVEgiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoic295cGVwZWphaW1lc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NTg5MTk2MDksImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiJjMDdiMDE1NmQ1YTcwMDE4YTE1ZSIsIm5iZiI6MTc1ODkxOTU5OSwic2lkIjoic2Vzc18zM0ZqM2p4SUNOVjF3WXVxNjhPZTF1R2xPa0UiLCJzdHMiOiJhY3RpdmUiLCJzdWIiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCJ9.QUxsK2NMBP1Sa9JCuolkPKc6awWT9XoAyeVFbySe3_rJB_gRf4aX18lDRTfM2KlkcFeTWpGuvsA1OW-BUWzmdOhgXKECmrC8YJN2Y0GeS-wGgTHUTQ2HnP6L3r2va8Fp_aJeo9t864paqYeZCI14BhhQdDMp3WHtvubKGkKOGWs7mB2PcrXJ_YRVAeHj5RrRMBOWSy6xWbG7il8EVBRVZRyOorJQvoRzoIfOXKysIAQq87YwSCQqgYAm5VbyGCIuuYBYZV2ZC0tptMtuTkbdXFZ7f0_OCPzV0u36aCsKKvnKpxjn3j-b5v_egu-FkjvOQJhyvyu8ZYeuAmg7COLUZQ; __session_U9tcbTPE=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg5MjMyMDksImZ2YSI6WzEsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ycXBaSFh1U05Ta0t2ZUFoa2Z6RVMxNGRnVEgiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoic295cGVwZWphaW1lc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NTg5MTk2MDksImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiJjMDdiMDE1NmQ1YTcwMDE4YTE1ZSIsIm5iZiI6MTc1ODkxOTU5OSwic2lkIjoic2Vzc18zM0ZqM2p4SUNOVjF3WXVxNjhPZTF1R2xPa0UiLCJzdHMiOiJhY3RpdmUiLCJzdWIiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCJ9.QUxsK2NMBP1Sa9JCuolkPKc6awWT9XoAyeVFbySe3_rJB_gRf4aX18lDRTfM2KlkcFeTWpGuvsA1OW-BUWzmdOhgXKECmrC8YJN2Y0GeS-wGgTHUTQ2HnP6L3r2va8Fp_aJeo9t864paqYeZCI14BhhQdDMp3WHtvubKGkKOGWs7mB2PcrXJ_YRVAeHj5RrRMBOWSy6xWbG7il8EVBRVZRyOorJQvoRzoIfOXKysIAQq87YwSCQqgYAm5VbyGCIuuYBYZV2ZC0tptMtuTkbdXFZ7f0_OCPzV0u36aCsKKvnKpxjn3j-b5v_egu-FkjvOQJhyvyu8ZYeuAmg7COLUZQ; _dd_s=aid=c3847edb-6f52-40e7-a0d5-5d74a0d7c5e6&rum=0&expire=1758920660406";
cookiePool.addCookie(mainCookie);

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
// Rutas específicas para archivos importantes
app.get('/immersive_interface.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'immersive_interface.html'));
});

app.get('/son1kvers3_frontend.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'son1kvers3_frontend.html'));
});

app.get('/index.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/', (req, res) => {
  // Redirigir al frontend principal
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Ruta de prueba (mantener para testing)
app.get('/test', (req, res) => {
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
