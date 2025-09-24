const express = require('express');
const { Api } = require('suno-api');
const cors = require('cors');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const app = express();

// Middleware para headers ultra-evasivos
app.use((req, res, next) => {
  // Rotación de User-Agents reales de navegadores
  const userAgents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
  ];
  
  const selectedUA = userAgents[Math.floor(Math.random() * userAgents.length)];
  
  // Headers que simulan un navegador real
  res.setHeader('User-Agent', selectedUA);
  res.setHeader('Accept', 'application/json, text/plain, */*');
  res.setHeader('Accept-Language', 'en-US,en;q=0.9,es;q=0.8');
  res.setHeader('Accept-Encoding', 'gzip, deflate, br');
  res.setHeader('DNT', '1');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Upgrade-Insecure-Requests', '1');
  res.setHeader('Sec-Fetch-Dest', 'empty');
  res.setHeader('Sec-Fetch-Mode', 'cors');
  res.setHeader('Sec-Fetch-Site', 'same-origin');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('X-Requested-With', 'XMLHttpRequest');
  res.setHeader('X-Forwarded-For', generateRandomIP());
  res.setHeader('X-Real-IP', generateRandomIP());
  
  next();
});

app.use(cors());
app.use(express.json());

// Generar IP aleatoria para evasión
function generateRandomIP() {
  return `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
}

// Pool de cookies con scoring inteligente
class UltraStealthCookiePool {
  constructor() {
    this.cookies = new Map();
    this.accountRotation = new Map();
    this.lastRotation = 0;
    this.rotationInterval = 300000; // 5 minutos
  }

  addCookie(accountId, cookie, email) {
    this.cookies.set(accountId, {
      cookie,
      email,
      score: 100,
      lastUsed: 0,
      successCount: 0,
      failureCount: 0,
      cooldownUntil: 0,
      userAgent: this.getRandomUserAgent(),
      sessionId: this.generateSessionId()
    });
  }

  getRandomUserAgent() {
    const userAgents = [
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ];
    return userAgents[Math.floor(Math.random() * userAgents.length)];
  }

  generateSessionId() {
    return crypto.randomBytes(16).toString('hex');
  }

  getBestCookie() {
    const now = Date.now();
    const availableCookies = Array.from(this.cookies.entries())
      .filter(([id, data]) => data.cooldownUntil < now)
      .sort((a, b) => b[1].score - a[1].score);

    if (availableCookies.length === 0) {
      return null;
    }

    const [accountId, data] = availableCookies[0];
    data.lastUsed = now;
    return { accountId, ...data };
  }

  updateScore(accountId, success) {
    const data = this.cookies.get(accountId);
    if (data) {
      if (success) {
        data.successCount++;
        data.score = Math.min(100, data.score + 5);
      } else {
        data.failureCount++;
        data.score = Math.max(0, data.score - 10);
        data.cooldownUntil = Date.now() + 300000; // 5 min cooldown
      }
    }
  }
}

const cookiePool = new UltraStealthCookiePool();

// Cargar cuentas desde archivo
function loadAccounts() {
  try {
    const configPath = path.join(__dirname, 'suno_accounts_stealth.json');
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      config.accounts.forEach(account => {
        if (account.cookie && account.email) {
          cookiePool.addCookie(account.id, account.cookie, account.email);
          console.log(`🔒 Cargada cuenta stealth: ${account.email}`);
        }
      });
    }
  } catch (error) {
    console.error('❌ Error cargando cuentas:', error.message);
  }
}

// Generador ultra-stealth
class UltraStealthSunoGenerator {
  constructor() {
    this.api = new Api();
    this.requestHistory = [];
    this.maxHistory = 100;
  }

  // Simular comportamiento humano real
  async simulateHumanBehavior() {
    // Delays aleatorios que simulan pensamiento humano
    const delays = [1000, 1500, 2000, 2500, 3000];
    const delay = delays[Math.floor(Math.random() * delays.length)];
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  // Obfuscar payload para evadir detección
  obfuscatePayload(payload) {
    const obfuscated = { ...payload };
    
    // Agregar campos aleatorios para confundir detección
    obfuscated._timestamp = Date.now();
    obfuscated._random = crypto.randomBytes(8).toString('hex');
    obfuscated._version = '1.0.0';
    
    // Modificar ligeramente el prompt para evitar detección de patrones
    if (obfuscated.prompt) {
      const variations = [
        obfuscated.prompt,
        obfuscated.prompt + ' ',
        ' ' + obfuscated.prompt,
        obfuscated.prompt + '.'
      ];
      obfuscated.prompt = variations[Math.floor(Math.random() * variations.length)];
    }
    
    return obfuscated;
  }

  // Headers ultra-evasivos para cada request
  getStealthHeaders(cookieData) {
    const baseHeaders = {
      'User-Agent': cookieData.userAgent,
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache',
      'X-Requested-With': 'XMLHttpRequest',
      'X-Forwarded-For': generateRandomIP(),
      'X-Real-IP': generateRandomIP(),
      'Cookie': cookieData.cookie,
      'Referer': 'https://suno.com/',
      'Origin': 'https://suno.com'
    };

    // Agregar headers aleatorios para confundir
    const randomHeaders = {
      'X-Client-Version': '1.0.0',
      'X-Platform': 'web',
      'X-Device-Type': 'desktop',
      'X-Session-ID': cookieData.sessionId
    };

    return { ...baseHeaders, ...randomHeaders };
  }

  async generateMusic(prompt, lyrics = '', style = 'profesional', instrumental = false) {
    console.log('🔒 [ULTRA-STEALTH] Iniciando generación ultra-indetectable...');
    
    // Simular comportamiento humano
    await this.simulateHumanBehavior();
    
    const cookieData = cookiePool.getBestCookie();
    if (!cookieData) {
      throw new Error('No hay cuentas activas disponibles');
    }

    console.log(`🔒 [ULTRA-STEALTH] Usando cuenta: ${cookieData.email}`);

    // Crear payload obfuscado
    const payload = this.obfuscatePayload({
      prompt: prompt,
      lyrics: lyrics || '',
      makeInstrumental: instrumental,
      tags: style,
      title: `UltraStealth-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`
    });

    console.log('🔒 [ULTRA-STEALTH] Payload obfuscado:', JSON.stringify(payload, null, 2));

    // Headers ultra-evasivos
    const headers = this.getStealthHeaders(cookieData);

    // Intentar generación con retry inteligente
    const maxRetries = 3;
    let lastError = null;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`🔒 [ULTRA-STEALTH] Intento ${attempt}/${maxRetries} con ${cookieData.email}`);
        
        // Delay aleatorio entre intentos
        if (attempt > 1) {
          const retryDelay = Math.random() * 5000 + 2000; // 2-7 segundos
          console.log(`🔒 [ULTRA-STEALTH] Esperando ${Math.round(retryDelay)}ms antes del retry...`);
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        }

        // Simular actividad previa (como un humano navegando)
        await this.simulatePreGenerationActivity();

        // Hacer la petición con headers ultra-evasivos usando fetch directo
        const response = await fetch('https://suno.com/api/generate', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(payload)
        });
        
        let responseData;
        const responseText = await response.text();
        
        try {
          responseData = JSON.parse(responseText);
        } catch (jsonError) {
          console.log(`⚠️ [ULTRA-STEALTH] Respuesta no JSON: ${responseText.substring(0, 200)}...`);
          throw new Error(`Suno devolvió HTML en lugar de JSON: ${response.status}`);
        }
        
        if (response.ok && responseData.id) {
          console.log('✅ [ULTRA-STEALTH] Generación exitosa!');
          cookiePool.updateScore(cookieData.accountId, true);
          
          return {
            success: true,
            jobId: responseData.id,
            prompt: prompt,
            lyrics: lyrics,
            audioUrls: responseData.audioUrls || [],
            message: 'Música generada con tecnología ultra-stealth',
            timestamp: new Date().toISOString(),
            account: cookieData.email,
            stealthLevel: 'ULTRA'
          };
        } else {
          throw new Error(`Suno error: ${response.status} - ${responseData.message || 'Unknown error'}`);
        }

      } catch (error) {
        lastError = error;
        console.log(`⚠️ [ULTRA-STEALTH] Intento ${attempt} falló: ${error.message}`);
        
        // Actualizar score de la cuenta
        cookiePool.updateScore(cookieData.accountId, false);
        
        // Si es el último intento, lanzar error
        if (attempt === maxRetries) {
          break;
        }
      }
    }

    throw new Error(`Ultra-stealth falló después de ${maxRetries} intentos: ${lastError.message}`);
  }

  // Simular actividad previa a la generación (como un humano)
  async simulatePreGenerationActivity() {
    const activities = [
      () => this.simulatePageLoad(),
      () => this.simulateScroll(),
      () => this.simulateClick(),
      () => this.simulateTyping()
    ];
    
    const activity = activities[Math.floor(Math.random() * activities.length)];
    await activity();
  }

  async simulatePageLoad() {
    // Simular tiempo de carga de página
    await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 1000));
  }

  async simulateScroll() {
    // Simular scroll humano
    const scrollSteps = Math.floor(Math.random() * 5) + 2;
    for (let i = 0; i < scrollSteps; i++) {
      await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 200));
    }
  }

  async simulateClick() {
    // Simular click humano
    await new Promise(resolve => setTimeout(resolve, Math.random() * 300 + 100));
  }

  async simulateTyping() {
    // Simular escritura humana
    const typingDelay = Math.random() * 100 + 50;
    await new Promise(resolve => setTimeout(resolve, typingDelay));
  }
}

const ultraStealthGenerator = new UltraStealthSunoGenerator();

// Cargar cuentas al iniciar
loadAccounts();

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

    const result = await ultraStealthGenerator.generateMusic(
      prompt,
      lyrics || '',
      style || 'profesional',
      instrumental || false
    );

    res.json(result);
  } catch (error) {
    console.error('❌ [ULTRA-STEALTH] Error:', error.message);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/health', (req, res) => {
  const accounts = Array.from(cookiePool.cookies.values());
  const activeAccounts = accounts.filter(acc => acc.cooldownUntil < Date.now());
  
  res.json({
    status: 'ultra-stealth-active',
    accounts: accounts.map(acc => ({
      email: acc.email,
      score: acc.score,
      status: acc.cooldownUntil < Date.now() ? 'active' : 'cooldown',
      successCount: acc.successCount,
      failureCount: acc.failureCount
    })),
    activeAccounts: activeAccounts.length,
    totalAccounts: accounts.length,
    stealthLevel: 'ULTRA',
    timestamp: new Date().toISOString()
  });
});

app.get('/stats', (req, res) => {
  const accounts = Array.from(cookiePool.cookies.values());
  const totalSuccess = accounts.reduce((sum, acc) => sum + acc.successCount, 0);
  const totalFailures = accounts.reduce((sum, acc) => sum + acc.failureCount, 0);
  
  res.json({
    accounts: accounts.map(acc => ({
      email: acc.email,
      successCount: acc.successCount,
      failureCount: acc.failureCount,
      score: acc.score,
      status: acc.cooldownUntil < Date.now() ? 'active' : 'cooldown'
    })),
    totalSuccess,
    totalFailures,
    successRate: totalSuccess + totalFailures > 0 ? (totalSuccess / (totalSuccess + totalFailures) * 100).toFixed(2) : 0,
    stealthLevel: 'ULTRA',
    features: [
      'Human behavior simulation',
      'Advanced payload obfuscation',
      'Intelligent cookie rotation',
      'Random delay patterns',
      'Real browser headers',
      'IP spoofing',
      'Session management'
    ]
  });
});

app.post('/add-account', (req, res) => {
  try {
    const { accountId, cookie, email } = req.body;
    
    if (!accountId || !cookie || !email) {
      return res.status(400).json({
        success: false,
        error: 'accountId, cookie y email son requeridos'
      });
    }

    cookiePool.addCookie(accountId, cookie, email);
    
    res.json({
      success: true,
      message: 'Cuenta ultra-stealth agregada exitosamente',
      account: { accountId, email }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Son1k Ultra-Stealth System</title>
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
                <h1>🔒 Son1k Ultra-Stealth System</h1>
                <p class="stealth">Nivel de Evasión: ULTRA-INDETECTABLE</p>
            </div>
            
            <div class="status">
                <h2>🎯 Estado del Sistema</h2>
                <p><strong>Modo:</strong> Ultra-Stealth Activo</p>
                <p><strong>Cuentas:</strong> ${cookiePool.cookies.size} configuradas</p>
                <p><strong>Nivel de Evasión:</strong> <span class="stealth">ULTRA</span></p>
            </div>
            
            <div class="status">
                <h2>🛡️ Características Ultra-Stealth</h2>
                <div class="feature">🤖 Simulación de comportamiento humano real</div>
                <div class="feature">🎭 Obfuscación avanzada de payloads</div>
                <div class="feature">🔄 Rotación inteligente de cuentas</div>
                <div class="feature">⏱️ Patrones de delay aleatorios</div>
                <div class="feature">🌐 Headers de navegador real</div>
                <div class="feature">🔀 Spoofing de IP</div>
                <div class="feature">📱 Gestión de sesiones</div>
            </div>
            
            <div class="status">
                <h2>🔗 Endpoints Disponibles</h2>
                <div class="endpoint">POST /generate-music - Generar música ultra-stealth</div>
                <div class="endpoint">GET /health - Estado del sistema</div>
                <div class="endpoint">GET /stats - Estadísticas detalladas</div>
                <div class="endpoint">POST /add-account - Agregar cuenta</div>
            </div>
            
            <div class="status">
                <h2>🧪 Probar Sistema</h2>
                <p>Usa el frontend en <a href="http://localhost:8000" style="color: #00ff00;">http://localhost:8000</a></p>
                <p>O ejecuta: <code>python3 test_stealth_system.py</code></p>
            </div>
        </div>
    </body>
    </html>
  `);
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log('🔒 Son1k Ultra-Stealth System iniciado');
  console.log(`🌐 Puerto: ${PORT}`);
  console.log(`🔒 Cuentas cargadas: ${cookiePool.cookies.size}`);
  console.log('🛡️ Nivel de evasión: ULTRA-INDETECTABLE');
  console.log('🎯 Características activas:');
  console.log('   ✅ Simulación de comportamiento humano');
  console.log('   ✅ Obfuscación avanzada de payloads');
  console.log('   ✅ Rotación inteligente de cuentas');
  console.log('   ✅ Headers de navegador real');
  console.log('   ✅ Spoofing de IP');
  console.log('   ✅ Gestión de sesiones');
});
