#!/bin/bash

# Script para demostrar Son1k localmente
# Usa ngrok para crear URLs públicas temporales

echo "🎵 Iniciando demo local de Son1k..."

# Verificar si ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok no está instalado"
    echo "💡 Instalar con: brew install ngrok"
    echo "💡 O descargar desde: https://ngrok.com/download"
    exit 1
fi

# Crear configuración local simple
echo "🔧 Configurando demo local..."

# Crear mini servidor para frontend
cat > mini_server.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

PORT = 3000
os.chdir('frontend')
print(f"🌐 Servidor frontend iniciado en puerto {PORT}")
print(f"📁 Sirviendo desde: {os.getcwd()}")

with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"✅ Frontend disponible en: http://localhost:{PORT}")
    httpd.serve_forever()
EOF

chmod +x mini_server.py

# Crear configuración del frontend para demo
cat > frontend/config_demo.js << 'EOF'
// Configuración para demo local
window.SON1K_CONFIG = {
    API_BASE_URL: 'https://your-ngrok-url.ngrok-free.app',
    ENVIRONMENT: 'demo',
    ENABLE_TRANSPARENCY: true,
    DEMO_MODE: true
};

console.log('🎵 Son1k Demo Mode Loaded');
console.log('🔗 API Base:', window.SON1K_CONFIG.API_BASE_URL);
EOF

# Actualizar index.html para demo
cp frontend/index.html frontend/index_backup_demo.html

cat > frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Son1k - Generador de Música AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .container {
            max-width: 600px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            text-align: center;
        }
        
        .logo {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .form-group {
            margin-bottom: 25px;
            text-align: left;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        input, textarea {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 16px;
        }
        
        input::placeholder, textarea::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .generate-btn {
            background: linear-gradient(45deg, #ff6b6b, #ffd700);
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            margin-top: 20px;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px);
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
        }
        
        .status.success {
            background: rgba(46, 204, 113, 0.3);
            border: 1px solid #2ecc71;
        }
        
        .status.error {
            background: rgba(231, 76, 60, 0.3);
            border: 1px solid #e74c3c;
        }
        
        .status.loading {
            background: rgba(52, 152, 219, 0.3);
            border: 1px solid #3498db;
        }
        
        .demo-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 107, 107, 0.8);
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
        }
        
        .transparency-indicator {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(46, 204, 113, 0.8);
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="demo-badge">🎵 DEMO</div>
    <div class="transparency-indicator">🔒 MODO TRANSPARENTE</div>
    
    <div class="container">
        <div class="logo">Son1k</div>
        <div class="subtitle">Generador de Música con IA</div>
        
        <form id="musicForm">
            <div class="form-group">
                <label for="prompt">Describe tu música:</label>
                <input type="text" id="prompt" placeholder="Ej: canción alegre de rock con guitarra eléctrica" required>
            </div>
            
            <div class="form-group">
                <label for="lyrics">Letra (opcional):</label>
                <textarea id="lyrics" rows="4" placeholder="Escribe la letra de tu canción aquí..."></textarea>
            </div>
            
            <button type="submit" class="generate-btn">🎵 Generar Música</button>
        </form>
        
        <div id="status" class="status"></div>
    </div>

    <script src="config_demo.js"></script>
    <script>
        document.getElementById('musicForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const prompt = document.getElementById('prompt').value;
            const lyrics = document.getElementById('lyrics').value;
            const statusDiv = document.getElementById('status');
            
            // Mostrar estado de carga
            statusDiv.className = 'status loading';
            statusDiv.style.display = 'block';
            statusDiv.innerHTML = '🎵 Generando música... Esto puede tomar unos minutos.';
            
            try {
                // Simulación de llamada API
                const response = await fetch(`${window.SON1K_CONFIG.API_BASE_URL}/api/music/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        lyrics: lyrics || undefined
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                // Verificar transparencia
                if (result.job_id && result.job_id.includes('son1k_job_')) {
                    statusDiv.className = 'status success';
                    statusDiv.innerHTML = `
                        ✅ ¡Música generada exitosamente!<br>
                        🆔 Job ID: ${result.job_id}<br>
                        🔒 Modo transparente: ACTIVO<br>
                        💾 Descarga lista en unos minutos
                    `;
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = '❌ Error: Transparencia no aplicada correctamente';
                }
                
            } catch (error) {
                console.error('Error:', error);
                statusDiv.className = 'status error';
                statusDiv.innerHTML = `❌ Error: ${error.message}<br>ℹ️ Verifica que el servidor esté ejecutándose`;
            }
        });
        
        // Verificar configuración al cargar
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🎵 Son1k Demo Iniciado');
            console.log('🔗 API URL:', window.SON1K_CONFIG.API_BASE_URL);
            console.log('🔒 Transparencia:', window.SON1K_CONFIG.ENABLE_TRANSPARENCY);
        });
    </script>
</body>
</html>
EOF

echo "✅ Configuración de demo completada"

echo
echo "🚀 Para iniciar el demo:"
echo "   1. Ejecutar: python3 mini_server.py"
echo "   2. En otra terminal: ngrok http 3000"
echo "   3. Usar la URL de ngrok como API_BASE_URL"
echo
echo "📋 URLs que tendrás:"
echo "   - Frontend local: http://localhost:3000"
echo "   - Frontend público: https://xxx.ngrok-free.app"
echo
echo "🎯 El demo mostrará el sistema de transparencia funcionando"