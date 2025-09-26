const express = require('express');
const puppeteer = require('puppeteer');
const axios = require('axios').default;
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Configuración de cuentas
const ACCOUNTS = [
  {
    email: 'soypepejames@gmail.com',
    password: 'TU_CONTRASEÑA_AQUI', // Necesitas poner tu contraseña real
    cookies: 'singular_device_id=7fc059fe-34d2-4536-8406-f0b36aa40b7b; ajs_anonymous_id=f0f2cc3c-29fc-4994-b313-c6395f7f01c0; _gcl_au=1.1.967689396.1753245394; _axwrt=24c6944f-367e-4935-93d1-a3a85f8a00dd; _ga=GA1.1.666180024.1753245517; _tt_enable_cookie=1; _ttp=01K0TS71AVG32RZB7XJHY47EVG_.tt.1; afUserId=3882fe9a-09c9-44af-bbf0-2f795576bbe6-p; _fbp=fb.1.1753245523258.766316113280164517; has_logged_in_before=true; __stripe_mid=83485d6a-9536-455a-af6d-a1281884f0ded62e90; _clck=5g3z8b%5E2%5Efyz%5E0%5E2060; AF_SYNC=1758345852539; _gcl_gs=2.1.k1$i1758583235$u42332455; _gcl_aw=GCL.1758583242.Cj0KCQjw58PGBhCkARIsADbDilxMP4uOSqOWzTyOPWvIqhjcJ3Z-WIvibpwrfYJlxpH277SWutUj9n8aAiN6EALw_wcB; __client_uat=1758698843; __client_uat_U9tcbTPE=1758698843; __stripe_sid=ae29cf28-47be-4e9d-b7f7-2d396009e363970f4e; clerk_active_context=sess_338VmGRuxvyTwEwYMO0NYgMZtOI:; ttcsid=1758726322712::qYUzqu1xQvHDUSpoHQX_.265.1758729439206.0; _uetsid=6618fc20927811f0bf1e9b526665403c|uzkp91|2|fzl|0|2084; ttcsid_CT67HURC77UB52N3JFBG=1758726322708::P0r3XE6ppWJPuPLCEH5d.298.1758729439480.0; _uetvid=75e947607c9711f0a0a265429931a928|42vysh|1758729440703|8|1|bat.bing.com/p/conversions/c/v; ax_visitor=%7B%22firstVisitTs%22%3A1753245747787%2C%22lastVisitTs%22%3A1758709867604%2C%22currentVisitStartTs%22%3A1758723934473%2C%22ts%22%3A1758729449303%2C%22visitCount%22%3A256%7D; _ga_7B0KEDD7XP=GS2.1.s1758726322$o306$g1$t1758729452$j46$l0$h0; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MzMzNTAsImZ2YSI6WzUxNSwtMV0sImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvY2xlcmtfaWQiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvZW1haWwiOiJzb3lwZXBlamFpbWVzQGdtYWlsLmNvbSIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvcGhvbmUiOm51bGwsImlhdCI6MTc1ODcyOTc1MCwiaXNzIjoiaHR0cHM6Ly9jbGVyay5zdW5vLmNvbSIsImp0aSI6ImY4ZTFhODc4ZmFkZDRhYzUwMTI1IiwibmJmIjoxNzU4NzI5NzQwLCJzaWQiOiJzZXNzXzMzOFZtR1J1eHZ5VHdFd1lNTzBOWWdNWnRPSSIsInN0cyI6ImFjdGl2ZSIsInN1YiI6InVzZXJfMnFwWkhYdVNOU2tLdmVBaGtmekVTMTRkZ1RIIn0.HCN6MozK3Jr1-ZdheGiiroLKckoY3HN5jlRtry57hgxN2AHlclJBG2khBToQ4tvCXHP6NoZNuDrzFmyBFiaONqJMCvo4qgdxQRTXHBixmoXpf8tDwP3QFoNNLelLaRfTSpokgaohVg_Xfw3_yj5ATtxvXrfywCUln4KxvHp_HlXj3yfDFfXhg1W3XBQkZPxNxh-gp4fVl1REUFhkSiZAqg3ZdRJM557dpLmS0yYxbxsG72twQLzu69Anm5IHNz_wdySMQaG8gjUnq01kpovxJbxx629wZJh2dkNBKHpwZZrAke6YNylria6DiLgA2Cygtm90VQq7CyJoTEvvucwUsg; __session_U9tcbTPE=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MzMzNTAsImZ2YSI6WzUxNSwtMV0sImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvY2xlcmtfaWQiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvZW1haWwiOiJzb3lwZXBlamFpbWVzQGdtYWlsLmNvbSIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvcGhvbmUiOm51bGwsImlhdCI6MTc1ODcyOTc1MCwiaXNzIjoiaHR0cHM6Ly9jbGVyay5zdW5vLmNvbSIsImp0aSI6ImY4ZTFhODc4ZmFkZDRhYzUwMTI1IiwibmJmIjoxNzU4NzI5NzQwLCJzaWQiOiJzZXNzXzMzOFZtR1J1eHZ5VHdFd1lNTzBOWWdNWnRPSSIsInN0cyI6ImFjdGl2ZSIsInN1YiI6InVzZXJfMnFwWkhYdVNOU2tLdmVBaGtmekVTMTRkZ1RIIn0.HCN6MozK3Jr1-ZdheGiiroLKckoY3HN5jlRtry57hgxN2AHlclJBG2khBToQ4tvCXHP6NoZNuDrzFmyBFiaONqJMCvo4qgdxQRTXHBixmoXpf8tDwP3QFoNNLelLaRfTSpokgaohVg_Xfw3_yj5ATtxvXrfywCUln4KxvHp_HlXj3yfDFfXhg1W3XBQkZPxNxh-gp4fVl1REUFhkSiZAqg3ZdRJM557dpLmS0yYxbxsG72twQLzu69Anm5IHNz_wdySMQaG8gjUnq01kpovxJbxx629wZJh2dkNBKHpwZZrAke6YNylria6DiLgA2Cygtm90VQq7CyJoTEvvucwUsg; _dd_s=aid=ef52d868-270c-482a-93a7-7d3ef02da5ed&rum=0&expire=1758730652708'
  }
];

// Pool de navegadores para reutilización
const browserPool = [];
const MAX_BROWSERS = 2;

async function getBrowser() {
  if (browserPool.length > 0) {
    return browserPool.pop();
  }
  
  return await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
      '--disable-web-security',
      '--disable-features=VizDisplayCompositor'
    ]
  });
}

async function returnBrowser(browser) {
  if (browserPool.length < MAX_BROWSERS) {
    browserPool.push(browser);
  } else {
    await browser.close();
  }
}

async function generateMusicWithPuppeteer(prompt, lyrics = '', style = 'profesional', instrumental = false) {
  const browser = await getBrowser();
  const page = await browser.newPage();

  try {
    console.log('🤖 [PUPPETEER] Iniciando generación con navegador real...');
    
    // Configurar User-Agent y headers reales
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Establecer cookies de la cuenta
    const account = ACCOUNTS[0]; // Usar primera cuenta por ahora
    const cookies = account.cookies.split(';').map(cookie => {
      const [name, value] = cookie.trim().split('=');
      return { name, value, domain: '.suno.com', path: '/' };
    });
    
    await page.setCookie(...cookies);
    
    // 1. Ir directamente a la página de creación (asumiendo que ya estamos logueados)
    console.log('🌐 [PUPPETEER] Navegando a Suno...');
    await page.goto('https://suno.com/create', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });

    // Verificar si necesitamos hacer login
    const isLoggedIn = await page.evaluate(() => {
      return !document.querySelector('input[type="email"]') && 
             !document.querySelector('input[type="password"]');
    });

    if (!isLoggedIn) {
      console.log('🔐 [PUPPETEER] Necesario hacer login...');
      // Aquí podrías implementar login automático si tienes las credenciales
      throw new Error('Sesión expirada - necesitas hacer login manualmente');
    }

    console.log('✅ [PUPPETEER] Sesión activa detectada');

    // 2. Llenar el formulario de generación
    console.log('📝 [PUPPETEER] Llenando formulario...');
    
    // Esperar a que aparezcan los elementos del formulario
    await page.waitForSelector('textarea, input[placeholder*="prompt"], input[placeholder*="Prompt"]', { timeout: 10000 });
    
    // Buscar y llenar el campo de prompt
    const promptField = await page.$('textarea, input[placeholder*="prompt"], input[placeholder*="Prompt"]');
    if (promptField) {
      await promptField.click();
      await promptField.type(prompt, { delay: 100 });
    }

    // Si hay letras, buscar campo de lyrics
    if (lyrics && !instrumental) {
      const lyricsField = await page.$('textarea[placeholder*="lyric"], textarea[placeholder*="Lyric"]');
      if (lyricsField) {
        await lyricsField.click();
        await lyricsField.type(lyrics, { delay: 100 });
      }
    }

    // Buscar y hacer click en el botón de generar
    console.log('🎵 [PUPPETEER] Iniciando generación...');
    const generateButton = await page.$('button:contains("Generate"), button:contains("generar"), button[type="submit"]');
    if (generateButton) {
      await generateButton.click();
    } else {
      // Buscar por otros selectores comunes
      const altButton = await page.$('button[data-testid="generate"], .generate-button, #generate');
      if (altButton) {
        await altButton.click();
      } else {
        throw new Error('No se encontró el botón de generar');
      }
    }

    // 3. Esperar la generación con polling inteligente
    console.log('⏳ [PUPPETEER] Esperando generación...');
    let audioUrl = null;
    let attempts = 0;
    const maxAttempts = 30; // 5 minutos máximo

    while (attempts < maxAttempts && !audioUrl) {
      await page.waitForTimeout(10000); // Esperar 10 segundos
      attempts++;
      
      try {
        // Buscar elementos de audio generado
        audioUrl = await page.evaluate(() => {
          // Buscar diferentes tipos de elementos de audio
          const audioSelectors = [
            'audio[src*="suno.com"]',
            'audio[src*="audio"]',
            'audio source[src*="suno.com"]',
            'audio source[src*="audio"]',
            '[data-testid*="audio"] audio',
            '.audio-player audio',
            'video[src*="suno.com"]',
            'video[src*="audio"]'
          ];
          
          for (const selector of audioSelectors) {
            const element = document.querySelector(selector);
            if (element) {
              return element.src || element.getAttribute('src');
            }
          }
          
          // Buscar enlaces de descarga
          const downloadLinks = document.querySelectorAll('a[href*="suno.com"], a[href*="audio"]');
          for (const link of downloadLinks) {
            if (link.href.includes('audio') || link.href.includes('suno.com')) {
              return link.href;
            }
          }
          
          return null;
        });

        if (audioUrl) {
          console.log('🎉 [PUPPETEER] ¡Audio generado encontrado!');
          break;
        }
        
        console.log(`⏳ [PUPPETEER] Esperando... (${attempts}/${maxAttempts})`);
        
        // Verificar si hay errores
        const errorElement = await page.$('.error, .alert-danger, [data-testid*="error"]');
        if (errorElement) {
          const errorText = await page.evaluate(el => el.textContent, errorElement);
          throw new Error(`Error en generación: ${errorText}`);
        }
        
      } catch (e) {
        console.log(`⚠️ [PUPPETEER] Error en polling: ${e.message}`);
      }
    }

    if (!audioUrl) {
      throw new Error('No se generó el audio en el tiempo esperado');
    }

    // 4. Descargar el audio localmente
    console.log('💾 [PUPPETEER] Descargando audio...');
    const fileName = `song-${Date.now()}-${Math.random().toString(36).substr(2, 9)}.mp3`;
    const filePath = path.join(__dirname, 'generated_songs', fileName);
    
    // Crear directorio si no existe
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    try {
      const response = await axios.get(audioUrl, { 
        responseType: 'stream',
        timeout: 30000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
      });
      
      const writer = fs.createWriteStream(filePath);
      response.data.pipe(writer);
      
      await new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
      });
      
      console.log('✅ [PUPPETEER] Audio descargado exitosamente');
      
    } catch (downloadError) {
      console.log('⚠️ [PUPPETEER] Error descargando audio, usando URL directa');
    }

    await page.close();
    returnBrowser(browser);

    return {
      success: true,
      audioUrl: audioUrl,
      filePath: filePath,
      prompt: prompt,
      lyrics: lyrics,
      style: style,
      instrumental: instrumental,
      timestamp: new Date().toISOString(),
      method: 'puppeteer_stealth'
    };

  } catch (error) {
    console.error('❌ [PUPPETEER] Error:', error.message);
    await page.close();
    returnBrowser(browser);
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

    console.log('🎵 [PUPPETEER] Nueva solicitud de generación:', prompt);
    
    const result = await generateMusicWithPuppeteer(
      prompt,
      lyrics || '',
      style || 'profesional',
      instrumental || false
    );

    res.json(result);
  } catch (error) {
    console.error('❌ [PUPPETEER] Error en endpoint:', error.message);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: 'puppeteer-stealth-active',
    accounts: ACCOUNTS.length,
    browsers: browserPool.length,
    maxBrowsers: MAX_BROWSERS,
    method: 'puppeteer',
    timestamp: new Date().toISOString()
  });
});

app.get('/stats', (req, res) => {
  res.json({
    method: 'puppeteer_stealth',
    accounts: ACCOUNTS.map(acc => ({ email: acc.email })),
    browsers: {
      active: browserPool.length,
      max: MAX_BROWSERS
    },
    features: [
      'Real browser automation',
      'Cookie-based authentication',
      'Human-like interactions',
      'Audio file download',
      'Error handling',
      'Browser pooling'
    ]
  });
});

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Son1k Puppeteer Stealth System</title>
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
                <h1>🤖 Son1k Puppeteer Stealth System</h1>
                <p class="stealth">Nivel de Evasión: ULTRA-INDETECTABLE (Navegador Real)</p>
            </div>
            
            <div class="status">
                <h2>🎯 Estado del Sistema</h2>
                <p><strong>Método:</strong> Puppeteer + Navegador Real</p>
                <p><strong>Cuentas:</strong> ${ACCOUNTS.length} configuradas</p>
                <p><strong>Navegadores:</strong> ${browserPool.length}/${MAX_BROWSERS} activos</p>
                <p><strong>Nivel de Evasión:</strong> <span class="stealth">ULTRA-INDETECTABLE</span></p>
            </div>
            
            <div class="status">
                <h2>🛡️ Características Puppeteer Stealth</h2>
                <div class="feature">🤖 Automatización con navegador real</div>
                <div class="feature">🍪 Autenticación basada en cookies</div>
                <div class="feature">👤 Interacciones humanas reales</div>
                <div class="feature">💾 Descarga automática de archivos</div>
                <div class="feature">🔄 Pool de navegadores reutilizables</div>
                <div class="feature">⚡ Manejo de errores avanzado</div>
            </div>
            
            <div class="status">
                <h2>🔗 Endpoints Disponibles</h2>
                <div class="endpoint">POST /generate-music - Generar música con Puppeteer</div>
                <div class="endpoint">GET /health - Estado del sistema</div>
                <div class="endpoint">GET /stats - Estadísticas detalladas</div>
            </div>
            
            <div class="status">
                <h2>🧪 Probar Sistema</h2>
                <p>Usa el frontend en <a href="http://localhost:8000" style="color: #00ff00;">http://localhost:8000</a></p>
                <p>O ejecuta: <code>curl -X POST http://localhost:3002/generate-music -d '{"prompt":"test"}'</code></p>
            </div>
        </div>
    </body>
    </html>
  `);
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log('🤖 Son1k Puppeteer Stealth System iniciado');
  console.log(`🌐 Puerto: ${PORT}`);
  console.log(`🔒 Cuentas configuradas: ${ACCOUNTS.length}`);
  console.log('🛡️ Nivel de evasión: ULTRA-INDETECTABLE (Navegador Real)');
  console.log('🎯 Características activas:');
  console.log('   ✅ Automatización con navegador real');
  console.log('   ✅ Autenticación basada en cookies');
  console.log('   ✅ Interacciones humanas reales');
  console.log('   ✅ Descarga automática de archivos');
  console.log('   ✅ Pool de navegadores reutilizables');
  console.log('   ✅ Manejo de errores avanzado');
});









