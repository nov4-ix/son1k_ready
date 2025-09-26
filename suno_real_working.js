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

// Estadísticas del sistema
const stats = {
  sunoSuccess: 0,
  sunoFailures: 0,
  totalRequests: 0,
  lastSunoSuccess: null
};

// Función para generar música con Suno (versión mejorada)
async function generateWithSuno(prompt, lyrics = '', style = 'profesional', instrumental = false) {
  const browser = await puppeteer.launch({
    headless: false, // Cambiar a false para ver el navegador
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
      '--disable-web-security',
      '--disable-features=VizDisplayCompositor',
      '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
  });
  
  const page = await browser.newPage();

  try {
    console.log('🤖 [SUNO] Iniciando generación con navegador real...');
    
    // Configurar viewport y user agent
    await page.setViewport({ width: 1920, height: 1080 });
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Establecer cookies
    const account = SUNO_ACCOUNTS[0];
    const cookies = account.cookies.split(';').map(cookie => {
      const [name, value] = cookie.trim().split('=');
      return { name, value, domain: '.suno.com', path: '/' };
    });
    
    await page.setCookie(...cookies);
    
    // Navegar a Suno
    console.log('🌐 [SUNO] Navegando a Suno...');
    await page.goto('https://suno.com/create', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });

    // Esperar un poco para que cargue
    await page.waitForTimeout(3000);

    // Verificar sesión
    console.log('🔍 [SUNO] Verificando sesión...');
    const isLoggedIn = await page.evaluate(() => {
      return !document.querySelector('input[type="email"]') && 
             !document.querySelector('input[type="password"]');
    });

    if (!isLoggedIn) {
      throw new Error('Sesión de Suno expirada - necesitas actualizar las cookies');
    }

    console.log('✅ [SUNO] Sesión activa detectada');

    // Buscar el campo de prompt
    console.log('🔍 [SUNO] Buscando campo de prompt...');
    const promptSelectors = [
      'textarea[placeholder*="prompt"]',
      'textarea[placeholder*="Prompt"]',
      'textarea[placeholder*="Describe"]',
      'textarea[placeholder*="describe"]',
      'textarea[data-testid*="prompt"]',
      'textarea[data-testid*="Prompt"]',
      'textarea',
      'input[type="text"]'
    ];

    let promptField = null;
    for (const selector of promptSelectors) {
      try {
        promptField = await page.$(selector);
        if (promptField) {
          console.log(`✅ [SUNO] Campo encontrado con selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }

    if (!promptField) {
      // Tomar screenshot para debug
      await page.screenshot({ path: 'suno_debug.png' });
      throw new Error('No se encontró el campo de prompt');
    }

    // Limpiar y escribir el prompt
    console.log('✍️ [SUNO] Escribiendo prompt...');
    await promptField.click();
    await promptField.evaluate(el => el.value = '');
    await promptField.type(prompt, { delay: 100 });

    // Buscar botón de generar
    console.log('🔍 [SUNO] Buscando botón de generar...');
    const generateSelectors = [
      'button[type="submit"]',
      'button:contains("Generate")',
      'button:contains("generar")',
      'button:contains("Create")',
      'button:contains("crear")',
      'button[data-testid*="generate"]',
      'button[data-testid*="Generate"]',
      'button[data-testid*="submit"]',
      'button[data-testid*="Submit"]',
      'button[class*="generate"]',
      'button[class*="submit"]',
      'button[class*="create"]'
    ];

    let generateButton = null;
    for (const selector of generateSelectors) {
      try {
        generateButton = await page.$(selector);
        if (generateButton) {
          console.log(`✅ [SUNO] Botón encontrado con selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }

    if (!generateButton) {
      // Buscar por texto
      generateButton = await page.evaluateHandle(() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        return buttons.find(btn => 
          btn.textContent.toLowerCase().includes('generate') ||
          btn.textContent.toLowerCase().includes('crear') ||
          btn.textContent.toLowerCase().includes('submit')
        );
      });
    }

    if (!generateButton) {
      throw new Error('No se encontró el botón de generar');
    }

    // Hacer click en generar
    console.log('🎵 [SUNO] Generando música...');
    await generateButton.click();

    // Esperar generación
    console.log('⏳ [SUNO] Esperando generación...');
    let audioUrl = null;
    let attempts = 0;
    const maxAttempts = 60; // 10 minutos

    while (attempts < maxAttempts && !audioUrl) {
      await page.waitForTimeout(10000);
      attempts++;
      
      console.log(`🔄 [SUNO] Intento ${attempts}/${maxAttempts}...`);
      
      audioUrl = await page.evaluate(() => {
        const audioSelectors = [
          'audio[src*="suno.com"]',
          'audio[src*="audio"]',
          'video[src*="suno.com"]',
          'audio',
          'video'
        ];
        
        for (const selector of audioSelectors) {
          const element = document.querySelector(selector);
          if (element) {
            return element.src || element.getAttribute('src');
          }
        }
        return null;
      });

      if (audioUrl) {
        console.log('🎉 [SUNO] ¡Audio generado!');
        break;
      }
    }

    if (!audioUrl) {
      throw new Error('Suno no generó audio en el tiempo esperado');
    }

    // Descargar audio
    const fileName = `suno-${Date.now()}.mp3`;
    const filePath = path.join(__dirname, 'generated_songs', fileName);
    
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    try {
      console.log('💾 [SUNO] Descargando audio...');
      const response = await axios.get(audioUrl, { 
        responseType: 'stream',
        timeout: 30000
      });
      
      const writer = fs.createWriteStream(filePath);
      response.data.pipe(writer);
      
      await new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
      });
      
      console.log(`✅ [SUNO] Audio guardado en: ${filePath}`);
    } catch (downloadError) {
      console.log('⚠️ [SUNO] Error descargando, usando URL directa');
    }

    await page.close();
    await browser.close();

    stats.sunoSuccess++;
    stats.lastSunoSuccess = new Date().toISOString();

    return {
      success: true,
      audioUrl: audioUrl,
      filePath: filePath,
      prompt: prompt,
      lyrics: lyrics,
      style: style,
      instrumental: instrumental,
      timestamp: new Date().toISOString(),
      method: 'suno_puppeteer',
      source: 'suno_real',
      message: 'Música generada exitosamente en Suno'
    };

  } catch (error) {
    console.error('❌ [SUNO] Error:', error.message);
    await page.close();
    await browser.close();
    stats.sunoFailures++;
    throw error;
  }
}

// Endpoints
app.post('/generate-music', async (req, res) => {
  try {
    const { prompt, lyrics, style, instrumental } = req.body;
    
    if (!prompt) {
      return res.status(400).json({
        success: false,
        error: 'Prompt es requerido'
      });
    }

    console.log('🎵 [SUNO] Nueva solicitud:', { prompt });
    stats.totalRequests++;
    
    const result = await generateWithSuno(prompt, lyrics, style, instrumental);
    res.json(result);
  } catch (error) {
    console.error('❌ [SUNO] Error en endpoint:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      stats: stats
    });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: 'suno-real-active',
    suno: {
      accounts: SUNO_ACCOUNTS.length,
      success: stats.sunoSuccess,
      failures: stats.sunoFailures
    },
    stats: stats,
    timestamp: new Date().toISOString()
  });
});

app.get('/stats', (req, res) => {
  const totalAttempts = stats.sunoSuccess + stats.sunoFailures;
  const successRate = totalAttempts > 0 ? ((stats.sunoSuccess / totalAttempts) * 100).toFixed(2) : 0;
  
  res.json({
    method: 'suno_real',
    suno: {
      success: stats.sunoSuccess,
      failures: stats.sunoFailures,
      successRate: `${successRate}%`,
      lastSuccess: stats.lastSunoSuccess
    },
    total: {
      requests: stats.totalRequests,
      attempts: totalAttempts
    },
    features: [
      'Suno real con Puppeteer',
      'Navegador visible para debug',
      'Múltiples selectores de elementos',
      'Descarga automática de audio',
      'Manejo de errores robusto'
    ]
  });
});

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Son1k Suno Real System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .status { background: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0; }
            .feature { background: #333; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .stealth { color: #00ff00; font-weight: bold; }
            .endpoint { background: #444; padding: 10px; margin: 5px 0; border-radius: 5px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Son1k Suno Real System</h1>
                <p class="stealth">Generación Real de Música en Suno</p>
            </div>
            
            <div class="status">
                <h2>🎯 Estado del Sistema</h2>
                <p><strong>Método:</strong> Suno Real con Puppeteer</p>
                <p><strong>Cuentas:</strong> ${SUNO_ACCOUNTS.length}</p>
                <p><strong>Éxitos:</strong> ${stats.sunoSuccess}</p>
                <p><strong>Fallos:</strong> ${stats.sunoFailures}</p>
                <p><strong>Nivel de Evasión:</strong> <span class="stealth">ULTRA-INDETECTABLE</span></p>
            </div>
            
            <div class="status">
                <h2>🛡️ Características Suno Real</h2>
                <div class="feature">🤖 Suno real con Puppeteer</div>
                <div class="feature">👁️ Navegador visible para debug</div>
                <div class="feature">🎯 Múltiples selectores de elementos</div>
                <div class="feature">💾 Descarga automática de audio</div>
                <div class="feature">🛠️ Manejo de errores robusto</div>
            </div>
            
            <div class="status">
                <h2>🔗 Endpoints Disponibles</h2>
                <div class="endpoint">POST /generate-music - Generar música real</div>
                <div class="endpoint">GET /health - Estado del sistema</div>
                <div class="endpoint">GET /stats - Estadísticas detalladas</div>
            </div>
            
            <div class="status">
                <h2>🧪 Probar Sistema</h2>
                <p>Usa el frontend en <a href="http://localhost:8000" style="color: #00ff00;">http://localhost:8000</a></p>
                <p>O ejecuta: <code>curl -X POST http://localhost:3007/generate-music -d '{"prompt":"test"}'</code></p>
            </div>
        </div>
    </body>
    </html>
  `);
});

const PORT = process.env.PORT || 3007;
app.listen(PORT, () => {
  console.log('🤖 Son1k Suno Real System iniciado');
  console.log(`🌐 Puerto: ${PORT}`);
  console.log(`🤖 Suno: ${SUNO_ACCOUNTS.length} cuentas configuradas`);
  console.log('🛡️ Nivel de evasión: ULTRA-INDETECTABLE (Suno Real)');
  console.log('🎯 Características activas:');
  console.log('   ✅ Suno real con Puppeteer');
  console.log('   ✅ Navegador visible para debug');
  console.log('   ✅ Múltiples selectores de elementos');
  console.log('   ✅ Descarga automática de audio');
  console.log('   ✅ Manejo de errores robusto');
});









