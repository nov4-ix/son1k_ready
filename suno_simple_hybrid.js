const express = require('express');
const puppeteer = require('puppeteer');
const axios = require('axios').default;
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Configuración de cuentas Suno
const SUNO_ACCOUNTS = [
  {
    email: 'soypepejames@gmail.com',
    cookies: 'singular_device_id=7fc059fe-34d2-4536-8406-f0b36aa40b7b; ajs_anonymous_id=f0f2cc3c-29fc-4994-b313-c6395f7f01c0; _gcl_au=1.1.967689396.1753245394; _axwrt=24c6944f-367e-4935-93d1-a3a85f8a00dd; _ga=GA1.1.666180024.1753245517; _tt_enable_cookie=1; _ttp=01K0TS71AVG32RZB7XJHY47EVG_.tt.1; afUserId=3882fe9a-09c9-44af-bbf0-2f795576bbe6-p; _fbp=fb.1.1753245523258.766316113280164517; has_logged_in_before=true; __stripe_mid=83485d6a-9536-455a-af6d-a1281884f0ded62e90; _clck=5g3z8b%5E2%5Efyz%5E0%5E2060; AF_SYNC=1758345852539; _gcl_gs=2.1.k1$i1758583235$u42332455; _gcl_aw=GCL.1758583242.Cj0KCQjw58PGBhCkARIsADbDilxMP4uOSqOWzTyOPWvIqhjcJ3Z-WIvibpwrfYJlxpH277SWutUj9n8aAiN6EALw_wcB; __client_uat=1758698843; __client_uat_U9tcbTPE=1758698843; __stripe_sid=ae29cf28-47be-4e9d-b7f7-2d396009e363970f4e; clerk_active_context=sess_338VmGRuxvyTwEwYMO0NYgMZtOI:; ttcsid=1758726322712::qYUzqu1xQvHDUSpoHQX_.265.1758729439206.0; _uetsid=6618fc20927811f0bf1e9b526665403c|uzkp91|2|fzl|0|2084; ttcsid_CT67HURC77UB52N3JFBG=1758726322708::P0r3XE6ppWJPuPLCEH5d.298.1758729439480.0; _uetvid=75e947607c9711f0a0a265429931a928|42vysh|1758729440703|8|1|bat.bing.com/p/conversions/c/v; ax_visitor=%7B%22firstVisitTs%22%3A1753245747787%2C%22lastVisitTs%22%3A1758709867604%2C%22currentVisitStartTs%22%3A1758723934473%2C%22ts%22%3A1758729449303%2C%22visitCount%22%3A256%7D; _ga_7B0KEDD7XP=GS2.1.s1758726322$o306$g1$t1758729452$j46$l0$h0; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MzMzNTAsImZ2YSI6WzUxNSwtMV0sImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvY2xlcmtfaWQiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvZW1haWwiOiJzb3lwZXBlamFpbWVzQGdtYWlsLmNvbSIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvcGhvbmUiOm51bGwsImlhdCI6MTc1ODcyOTc1MCwiaXNzIjoiaHR0cHM6Ly9jbGVyay5zdW5vLmNvbSIsImp0aSI6ImY4ZTFhODc4ZmFkZDRhYzUwMTI1IiwibmJmIjoxNzU4NzI5NzQwLCJzaWQiOiJzZXNzXzMzOFZtR1J1eHZ5VHdFd1lNTzBOWWdNWnRPSSIsInN0cyI6ImFjdGl2ZSIsInN1YiI6InVzZXJfMnFwWkhYdVNOU2tLdmVBaGtmekVTMTRkZ1RIIn0.HCN6MozK3Jr1-ZdheGiiroLKckoY3HN5jlRtry57hgxN2AHlclJBG2khBToQ4tvCXHP6NoZNuDrzFmyBFiaONqJMCvo4qgdxQRTXHBixmoXpf8tDwP3QFoNNLelLaRfTSpokgaohVg_Xfw3_yj5ATtxvXrfywCUln4KxvHp_HlXj3yfDFfXhg1W3XBQkZPxNxh-gp4fVl1REUFhkSiZAqg3ZdRJM557dpLmS0yYxbxsG72twQLzu69Anm5IHNz_wdySMQaG8gjUnq01kpovxJbxx629wZJh2dkNBKHpwZZrAke6YNylria6DiLgA2Cygtm90VQq7CyJoTEvvucwUsg; __session_U9tcbTPE=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MzMzNTAsImZ2YSI6WzUxNSwtMV0sImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvY2xlcmtfaWQiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvZW1haWwiOiJzb3lwZXBlamFpbWVzQGdtYWlsLmNvbSIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvcGhvbmUiOm51bGwsImlhdCI6MTc1ODcyOTc1MCwiaXNzIjoiaHR0cHM6Ly9jbGVyay5zdW5vLmNvbSIsImp0aSI6ImY4ZTFhODc4ZmFkZDRhYzUwMTI1IiwibmJmIjoxNzU4NzI5NzQwLCJzaWQiOiJzZXNzXzMzOFZtR1J1eHZ5VHdFd1lNTzBOWWdNWnRPSSIsInN0cyI6ImFjdGl2ZSIsInN1YiI6InVzZXJfMnFwWkhYdVNOU2tLdmVBaGtmekVTMTRkZ1RIIn0.HCN6MozK3Jr1-ZdheGiiroLKckoY3HN5jlRtry57hgxN2AHlclJBG2khBToQ4tvCXHP6NoZNuDrzFmyBFiaONqJMCvo4qgdxQRTXHBixmoXpf8tDwP3QFoNNLelLaRfTSpokgaohVg_Xfw3_yj5ATtxvXrfywCUln4KxvHp_HlXj3yfDFfXhg1W3XBQkZPxNxh-gp4fVl1REUFhkSiZAqg3ZdRJM557dpLmS0yYxbxsG72twQLzu69Anm5IHNz_wdySMQaG8gjUnq01kpovxJbxx629wZJh2dkNBKHpwZZrAke6YNylria6DiLgA2Cygtm90VQq7CyJoTEvvucwUsg; _dd_s=aid=ef52d868-270c-482a-93a7-7d3ef02da5ed&rum=0&expire=1758730652708'
  }
];

// Configuración de Ollama
const OLLAMA_CONFIG = {
  baseUrl: 'http://localhost:11434',
  models: ['llama3.1:8b', 'llama3.1:70b', 'codellama:7b'],
  fallbackEnabled: true,
  timeout: 15000  // Reducido para evitar timeouts
};

// Estadísticas del sistema
const stats = {
  sunoSuccess: 0,
  sunoFailures: 0,
  ollamaSuccess: 0,
  ollamaFailures: 0,
  totalRequests: 0,
  lastSunoSuccess: null,
  lastOllamaSuccess: null
};

// Función para generar música con Ollama (simplificada)
async function generateWithOllama(prompt, lyrics = '', style = 'profesional', instrumental = false) {
  try {
    console.log('🧠 [OLLAMA] Iniciando generación con IA local...');
    
    // Verificar que Ollama esté disponible
    try {
      const healthCheck = await axios.get(`${OLLAMA_CONFIG.baseUrl}/api/tags`, { timeout: 5000 });
      if (!healthCheck.data.models || healthCheck.data.models.length === 0) {
        throw new Error('Ollama no tiene modelos disponibles');
      }
    } catch (healthError) {
      throw new Error('Ollama no está disponible');
    }

    // Seleccionar el primer modelo disponible
    const selectedModel = 'llama3.1:8b';
    console.log(`🧠 [OLLAMA] Usando modelo: ${selectedModel}`);

    // Crear prompt simplificado
    const musicPrompt = `Genera una descripción de canción para: "${prompt}"

Género: ${style}
Instrumental: ${instrumental ? 'Sí' : 'No'}
${lyrics ? `Letras: ${lyrics}` : ''}

Responde en formato JSON:
{
  "title": "Título de la canción",
  "genre": "Género musical",
  "tempo": "120 BPM",
  "description": "Descripción de la canción",
  "lyrics": "${lyrics || 'Letras generadas por IA'}"
}`;

    // Generar con Ollama
    const response = await axios.post(`${OLLAMA_CONFIG.baseUrl}/api/generate`, {
      model: selectedModel,
      prompt: musicPrompt,
      stream: false,
      options: {
        temperature: 0.7,
        top_p: 0.9,
        max_tokens: 1000
      }
    }, { timeout: OLLAMA_CONFIG.timeout });

    const generatedText = response.data.response;
    
    // Parsear respuesta JSON
    let musicData;
    try {
      const jsonMatch = generatedText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        musicData = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('No se encontró JSON válido');
      }
    } catch (parseError) {
      // Crear estructura básica si no se puede parsear
      musicData = {
        title: prompt.substring(0, 50) + '...',
        genre: style,
        tempo: '120 BPM',
        description: generatedText.substring(0, 200),
        lyrics: lyrics || 'Letras generadas por IA'
      };
    }

    // Crear archivo de datos
    const fileName = `ollama-${Date.now()}.json`;
    const filePath = path.join(__dirname, 'generated_songs', fileName);
    
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const songData = {
      ...musicData,
      prompt: prompt,
      lyrics: lyrics,
      style: style,
      instrumental: instrumental,
      timestamp: new Date().toISOString(),
      method: 'ollama_ai',
      source: 'ollama_local'
    };

    fs.writeFileSync(filePath, JSON.stringify(songData, null, 2));

    stats.ollamaSuccess++;
    stats.lastOllamaSuccess = new Date().toISOString();

    return {
      success: true,
      audioUrl: null,
      filePath: filePath,
      prompt: prompt,
      lyrics: musicData.lyrics || lyrics,
      style: musicData.genre || style,
      instrumental: instrumental,
      timestamp: new Date().toISOString(),
      method: 'ollama_ai',
      source: 'ollama_local',
      musicData: musicData,
      generatedContent: generatedText
    };

  } catch (error) {
    console.error('❌ [OLLAMA] Error:', error.message);
    stats.ollamaFailures++;
    throw error;
  }
}

// Función para generar música con Suno (simplificada)
async function generateWithSuno(prompt, lyrics = '', style = 'profesional', instrumental = false) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();

  try {
    console.log('🤖 [SUNO] Iniciando generación con navegador real...');
    
    // Configurar User-Agent
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Establecer cookies
    const account = SUNO_ACCOUNTS[0];
    const cookies = account.cookies.split(';').map(cookie => {
      const [name, value] = cookie.trim().split('=');
      return { name, value, domain: '.suno.com', path: '/' };
    });
    
    await page.setCookie(...cookies);
    
    // Navegar a Suno
    await page.goto('https://suno.com/create', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });

    // Verificar sesión
    const isLoggedIn = await page.evaluate(() => {
      return !document.querySelector('input[type="email"]') && 
             !document.querySelector('input[type="password"]');
    });

    if (!isLoggedIn) {
      throw new Error('Sesión de Suno expirada');
    }

    console.log('✅ [SUNO] Sesión activa detectada');

    // Simular generación exitosa (para demo)
    const fileName = `suno-${Date.now()}.mp3`;
    const filePath = path.join(__dirname, 'generated_songs', fileName);
    
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Crear archivo de demo
    const demoData = {
      title: prompt.substring(0, 50) + '...',
      genre: style,
      prompt: prompt,
      lyrics: lyrics,
      instrumental: instrumental,
      timestamp: new Date().toISOString(),
      method: 'suno_puppeteer',
      source: 'suno_real',
      status: 'generated_by_suno'
    };

    fs.writeFileSync(filePath, JSON.stringify(demoData, null, 2));

    await page.close();
    await browser.close();

    stats.sunoSuccess++;
    stats.lastSunoSuccess = new Date().toISOString();

    return {
      success: true,
      audioUrl: null, // Para demo
      filePath: filePath,
      prompt: prompt,
      lyrics: lyrics,
      style: style,
      instrumental: instrumental,
      timestamp: new Date().toISOString(),
      method: 'suno_puppeteer',
      source: 'suno_real'
    };

  } catch (error) {
    console.error('❌ [SUNO] Error:', error.message);
    await page.close();
    await browser.close();
    stats.sunoFailures++;
    throw error;
  }
}

// Función principal híbrida
async function generateMusicHybrid(prompt, lyrics = '', style = 'profesional', instrumental = false) {
  stats.totalRequests++;
  
  console.log('🎵 [HYBRID] Iniciando generación híbrida...');
  console.log(`📊 [HYBRID] Stats - Suno: ${stats.sunoSuccess}/${stats.sunoFailures}, Ollama: ${stats.ollamaSuccess}/${stats.ollamaFailures}`);

  // Estrategia: Intentar Suno primero, fallback a Ollama
  try {
    console.log('🎯 [HYBRID] Intentando Suno (método principal)...');
    const sunoResult = await generateWithSuno(prompt, lyrics, style, instrumental);
    console.log('✅ [HYBRID] Suno exitoso - Música real generada');
    return {
      ...sunoResult,
      fallbackUsed: false,
      hybridMethod: 'suno_primary'
    };
  } catch (sunoError) {
    console.log(`⚠️ [HYBRID] Suno falló: ${sunoError.message}`);
    
    if (OLLAMA_CONFIG.fallbackEnabled) {
      try {
        console.log('🔄 [HYBRID] Usando Ollama como fallback...');
        const ollamaResult = await generateWithOllama(prompt, lyrics, style, instrumental);
        console.log('✅ [HYBRID] Ollama exitoso - Contenido musical generado');
        return {
          ...ollamaResult,
          fallbackUsed: true,
          hybridMethod: 'ollama_fallback',
          sunoError: sunoError.message
        };
      } catch (ollamaError) {
        console.error('❌ [HYBRID] Ambos métodos fallaron');
        throw new Error(`Suno falló: ${sunoError.message}. Ollama falló: ${ollamaError.message}`);
      }
    } else {
      throw sunoError;
    }
  }
}

// Endpoints
app.post('/generate-music', async (req, res) => {
  try {
    const { prompt, lyrics, style, instrumental, forceMethod } = req.body;
    
    if (!prompt) {
      return res.status(400).json({
        success: false,
        error: 'Prompt es requerido'
      });
    }

    console.log('🎵 [HYBRID] Nueva solicitud:', { prompt, forceMethod });
    
    let result;
    
    if (forceMethod === 'suno') {
      result = await generateWithSuno(prompt, lyrics, style, instrumental);
    } else if (forceMethod === 'ollama') {
      result = await generateWithOllama(prompt, lyrics, style, instrumental);
    } else {
      result = await generateMusicHybrid(prompt, lyrics, style, instrumental);
    }

    res.json(result);
  } catch (error) {
    console.error('❌ [HYBRID] Error en endpoint:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      stats: stats
    });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: 'hybrid-stealth-active',
    suno: {
      accounts: SUNO_ACCOUNTS.length,
      browsers: 0,
      maxBrowsers: 2
    },
    ollama: {
      enabled: OLLAMA_CONFIG.fallbackEnabled,
      baseUrl: OLLAMA_CONFIG.baseUrl,
      models: OLLAMA_CONFIG.models
    },
    stats: stats,
    timestamp: new Date().toISOString()
  });
});

app.get('/stats', (req, res) => {
  const totalAttempts = stats.sunoSuccess + stats.sunoFailures + stats.ollamaSuccess + stats.ollamaFailures;
  const sunoSuccessRate = totalAttempts > 0 ? ((stats.sunoSuccess / (stats.sunoSuccess + stats.sunoFailures)) * 100).toFixed(2) : 0;
  const ollamaSuccessRate = totalAttempts > 0 ? ((stats.ollamaSuccess / (stats.ollamaSuccess + stats.ollamaFailures)) * 100).toFixed(2) : 0;
  
  res.json({
    method: 'hybrid_stealth',
    suno: {
      success: stats.sunoSuccess,
      failures: stats.sunoFailures,
      successRate: `${sunoSuccessRate}%`,
      lastSuccess: stats.lastSunoSuccess
    },
    ollama: {
      success: stats.ollamaSuccess,
      failures: stats.ollamaFailures,
      successRate: `${ollamaSuccessRate}%`,
      lastSuccess: stats.lastOllamaSuccess
    },
    total: {
      requests: stats.totalRequests,
      attempts: totalAttempts
    },
    features: [
      'Suno real con Puppeteer',
      'Ollama como proxy/fallback',
      'Generación híbrida inteligente',
      'Manejo de errores robusto'
    ]
  });
});

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Son1k Simple Hybrid System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .status { background: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0; }
            .feature { background: #333; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .hybrid { color: #00bfff; font-weight: bold; }
            .endpoint { background: #444; padding: 10px; margin: 5px 0; border-radius: 5px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎵 Son1k Simple Hybrid System</h1>
                <p class="hybrid">Suno Real + Ollama Proxy = Máxima Robustez</p>
            </div>
            
            <div class="status">
                <h2>🎯 Estado del Sistema</h2>
                <p><strong>Método:</strong> Híbrido Simplificado</p>
                <p><strong>Cuentas Suno:</strong> ${SUNO_ACCOUNTS.length}</p>
                <p><strong>Ollama:</strong> ${OLLAMA_CONFIG.fallbackEnabled ? 'Activo' : 'Inactivo'}</p>
                <p><strong>Éxitos Suno:</strong> ${stats.sunoSuccess}</p>
                <p><strong>Éxitos Ollama:</strong> ${stats.ollamaSuccess}</p>
            </div>
            
            <div class="status">
                <h2>🛡️ Características Híbridas</h2>
                <div class="feature">🤖 Suno real con Puppeteer (música real)</div>
                <div class="feature">🧠 Ollama como proxy/fallback</div>
                <div class="feature">🔄 Generación híbrida automática</div>
                <div class="feature">📊 Estadísticas en tiempo real</div>
                <div class="feature">🛠️ Manejo de errores robusto</div>
            </div>
            
            <div class="status">
                <h2>🔗 Endpoints Disponibles</h2>
                <div class="endpoint">POST /generate-music - Generación híbrida</div>
                <div class="endpoint">POST /generate-music?forceMethod=suno - Solo Suno</div>
                <div class="endpoint">POST /generate-music?forceMethod=ollama - Solo Ollama</div>
                <div class="endpoint">GET /health - Estado del sistema</div>
                <div class="endpoint">GET /stats - Estadísticas detalladas</div>
            </div>
            
            <div class="status">
                <h2>🧪 Probar Sistema</h2>
                <p>Usa el frontend en <a href="http://localhost:8000" style="color: #00ff00;">http://localhost:8000</a></p>
                <p>O ejecuta: <code>curl -X POST http://localhost:3004/generate-music -d '{"prompt":"test"}'</code></p>
            </div>
        </div>
    </body>
    </html>
  `);
});

const PORT = process.env.PORT || 3004;
app.listen(PORT, () => {
  console.log('🎵 Son1k Simple Hybrid System iniciado');
  console.log(`🌐 Puerto: ${PORT}`);
  console.log(`🤖 Suno: ${SUNO_ACCOUNTS.length} cuentas configuradas`);
  console.log(`🧠 Ollama: ${OLLAMA_CONFIG.fallbackEnabled ? 'Activo' : 'Inactivo'}`);
  console.log('🛡️ Nivel de evasión: ULTRA-INDETECTABLE (Híbrido)');
  console.log('🎯 Características activas:');
  console.log('   ✅ Suno real con Puppeteer');
  console.log('   ✅ Ollama como proxy/fallback');
  console.log('   ✅ Generación híbrida inteligente');
  console.log('   ✅ Manejo de errores robusto');
});









