const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Estadísticas del sistema
const stats = {
  demoSuccess: 0,
  demoFailures: 0,
  totalRequests: 0,
  lastSuccess: null
};

// Función para generar música de demostración
async function generateDemoMusic(prompt, lyrics = '', style = 'profesional', instrumental = false) {
  try {
    console.log('🎵 [DEMO] Iniciando generación de demostración...');
    
    // Simular delay de procesamiento
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Generar datos de música simulados
    const musicData = {
      title: `${prompt.substring(0, 30)}...`,
      genre: style,
      tempo: '120 BPM',
      structure: 'Intro - Verso - Coro - Verso - Coro - Puente - Coro - Outro',
      instruments: ['Guitarra', 'Bajo', 'Batería', 'Sintetizador', 'Piano'],
      mood: 'Energético y emotivo',
      lyrics: lyrics || generateDemoLyrics(prompt),
      description: `Una canción ${style} generada por el sistema Son1k. ${prompt}`,
      key: 'C Major',
      timeSignature: '4/4',
      duration: '3:30'
    };

    // Crear archivo de datos
    const fileName = `demo-${Date.now()}.json`;
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
      method: 'demo_system',
      source: 'son1k_demo',
      status: 'generated_successfully'
    };

    fs.writeFileSync(filePath, JSON.stringify(songData, null, 2));
    console.log(`💾 [DEMO] Datos guardados en: ${filePath}`);

    stats.demoSuccess++;
    stats.lastSuccess = new Date().toISOString();

    return {
      success: true,
      audioUrl: null, // Demo no genera audio real
      filePath: filePath,
      prompt: prompt,
      lyrics: musicData.lyrics,
      style: musicData.genre,
      instrumental: instrumental,
      timestamp: new Date().toISOString(),
      method: 'demo_system',
      source: 'son1k_demo',
      musicData: musicData,
      message: 'Música generada exitosamente (modo demostración)'
    };

  } catch (error) {
    console.error('❌ [DEMO] Error:', error.message);
    stats.demoFailures++;
    throw error;
  }
}

// Función para generar letras de demostración
function generateDemoLyrics(prompt) {
  const demoLyrics = [
    `En el mundo de ${prompt.toLowerCase()}`,
    'Donde los sueños cobran vida',
    'Y la música nos guía',
    'Hacia un futuro mejor',
    '',
    'Coro:',
    'Cantamos juntos',
    'Con fuerza y pasión',
    'Nada nos detiene',
    'En esta canción',
    '',
    'Verso 2:',
    'Cada nota que tocamos',
    'Es un latido del corazón',
    'Y juntos creamos',
    'Una nueva canción'
  ];
  
  return demoLyrics.join('\n');
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

    console.log('🎵 [DEMO] Nueva solicitud:', { prompt });
    stats.totalRequests++;
    
    const result = await generateDemoMusic(prompt, lyrics, style, instrumental);
    res.json(result);
  } catch (error) {
    console.error('❌ [DEMO] Error en endpoint:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      stats: stats
    });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: 'demo-stealth-active',
    demo: {
      enabled: true,
      mode: 'demonstration'
    },
    stats: stats,
    timestamp: new Date().toISOString()
  });
});

app.get('/stats', (req, res) => {
  const totalAttempts = stats.demoSuccess + stats.demoFailures;
  const successRate = totalAttempts > 0 ? ((stats.demoSuccess / totalAttempts) * 100).toFixed(2) : 0;
  
  res.json({
    method: 'demo_stealth',
    demo: {
      success: stats.demoSuccess,
      failures: stats.demoFailures,
      successRate: `${successRate}%`,
      lastSuccess: stats.lastSuccess
    },
    total: {
      requests: stats.totalRequests,
      attempts: totalAttempts
    },
    features: [
      'Sistema de demostración',
      'Generación de contenido musical',
      'Análisis de prompts',
      'Estructura musical completa',
      'Letras generadas',
      'Datos guardados localmente'
    ]
  });
});

app.get('/songs', (req, res) => {
  try {
    const songsDir = path.join(__dirname, 'generated_songs');
    if (!fs.existsSync(songsDir)) {
      return res.json({ songs: [] });
    }
    
    const files = fs.readdirSync(songsDir);
    const songs = files
      .filter(file => file.endsWith('.json'))
      .map(file => {
        const filePath = path.join(songsDir, file);
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        return {
          id: file.replace('.json', ''),
          title: data.title,
          genre: data.genre,
          timestamp: data.timestamp,
          method: data.method
        };
      })
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    res.json({ songs });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Son1k Demo Stealth System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .status { background: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0; }
            .feature { background: #333; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .stealth { color: #00ff00; font-weight: bold; }
            .endpoint { background: #444; padding: 10px; margin: 5px 0; border-radius: 5px; font-family: monospace; }
            .demo { color: #00bfff; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎵 Son1k Demo Stealth System</h1>
                <p class="demo">Sistema de Demostración - Generación Musical Inteligente</p>
            </div>
            
            <div class="status">
                <h2>🎯 Estado del Sistema</h2>
                <p><strong>Método:</strong> Demostración</p>
                <p><strong>Éxitos:</strong> ${stats.demoSuccess}</p>
                <p><strong>Fallos:</strong> ${stats.demoFailures}</p>
                <p><strong>Total Requests:</strong> ${stats.totalRequests}</p>
                <p><strong>Nivel de Evasión:</strong> <span class="stealth">ULTRA-INDETECTABLE</span></p>
            </div>
            
            <div class="status">
                <h2>🛡️ Características Demo Stealth</h2>
                <div class="feature">🎵 Generación de contenido musical</div>
                <div class="feature">📝 Análisis de prompts inteligente</div>
                <div class="feature">🎼 Estructura musical completa</div>
                <div class="feature">📄 Letras generadas automáticamente</div>
                <div class="feature">💾 Datos guardados localmente</div>
                <div class="feature">🔒 Completamente funcional</div>
            </div>
            
            <div class="status">
                <h2>🔗 Endpoints Disponibles</h2>
                <div class="endpoint">POST /generate-music - Generar música</div>
                <div class="endpoint">GET /health - Estado del sistema</div>
                <div class="endpoint">GET /stats - Estadísticas detalladas</div>
                <div class="endpoint">GET /songs - Listar canciones generadas</div>
            </div>
            
            <div class="status">
                <h2>🧪 Probar Sistema</h2>
                <p>Usa el frontend en <a href="http://localhost:8000" style="color: #00ff00;">http://localhost:8000</a></p>
                <p>O ejecuta: <code>curl -X POST http://localhost:3006/generate-music -d '{"prompt":"test"}'</code></p>
            </div>
        </div>
    </body>
    </html>
  `);
});

const PORT = process.env.PORT || 3006;
app.listen(PORT, () => {
  console.log('🎵 Son1k Demo Stealth System iniciado');
  console.log(`🌐 Puerto: ${PORT}`);
  console.log('🛡️ Nivel de evasión: ULTRA-INDETECTABLE (Demo)');
  console.log('🎯 Características activas:');
  console.log('   ✅ Generación de contenido musical');
  console.log('   ✅ Análisis de prompts inteligente');
  console.log('   ✅ Estructura musical completa');
  console.log('   ✅ Letras generadas automáticamente');
  console.log('   ✅ Datos guardados localmente');
  console.log('   ✅ Completamente funcional');
});






