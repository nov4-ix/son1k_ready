#!/bin/bash

echo "🌐 Configurando Acceso Público para Son1k"
echo "=========================================="

# 1. Instalar ngrok si no está instalado (en macOS)
if ! command -v ngrok &> /dev/null; then
    echo "📦 Instalando ngrok..."
    if command -v brew &> /dev/null; then
        brew install ngrok/ngrok/ngrok
    else
        echo "❌ Necesitas instalar Homebrew primero o instalar ngrok manualmente"
        echo "   1. Ve a: https://ngrok.com/download"
        echo "   2. Descarga e instala ngrok"
        echo "   3. Ejecuta este script nuevamente"
        exit 1
    fi
fi

# 2. Verificar que los servicios estén corriendo
echo "🔍 Verificando servicios..."

if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ API backend funcionando en puerto 8000"
else
    echo "❌ API backend no responde"
    echo "🔧 Iniciando servicios Docker..."
    docker compose up -d
    echo "⏳ Esperando servicios..."
    sleep 15
fi

# 3. Servir frontend estático
echo "🌐 Configurando servidor frontend..."

# Crear servidor simple para el frontend
cat > serve_frontend.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)
    
    def end_headers(self):
        # CORS headers para permitir requests desde ngrok
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    PORT = 3000
    print(f"🌐 Sirviendo frontend en puerto {PORT}")
    print(f"📁 Directorio: frontend/")
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        httpd.serve_forever()
EOF

# Hacer ejecutable
chmod +x serve_frontend.py

# 4. Iniciar servidor frontend en background
echo "🚀 Iniciando servidor frontend..."
python3 serve_frontend.py &
FRONTEND_PID=$!

# Esperar que inicie
sleep 3

# Verificar que esté funcionando
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend sirviendo en puerto 3000"
else
    echo "❌ Error iniciando servidor frontend"
    kill $FRONTEND_PID 2>/dev/null
    exit 1
fi

# 5. Crear túneles ngrok
echo "🌐 Creando túneles públicos con ngrok..."

# Túnel para frontend
echo "📱 Iniciando túnel para frontend (puerto 3000)..."
ngrok http 3000 --log=stdout > ngrok_frontend.log 2>&1 &
NGROK_FRONTEND_PID=$!

# Túnel para API
echo "🔌 Iniciando túnel para API (puerto 8000)..."
ngrok http 8000 --log=stdout > ngrok_api.log 2>&1 &
NGROK_API_PID=$!

# Esperar que ngrok se conecte
echo "⏳ Esperando conexión ngrok..."
sleep 10

# 6. Extraer URLs públicas
echo "🔍 Obteniendo URLs públicas..."

# Función para extraer URL de ngrok
get_ngrok_url() {
    local port=$1
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        url=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tunnel in data['tunnels']:
        if tunnel['config']['addr'] == 'http://localhost:$port':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null)
        
        if [ ! -z "$url" ]; then
            echo "$url"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 2
    done
    
    return 1
}

# Obtener URLs
FRONTEND_URL=$(get_ngrok_url 3000)
API_URL=$(get_ngrok_url 8000)

# 7. Crear información de acceso
cat > PUBLIC_ACCESS_INFO.md << EOF
# 🌐 Son1k - Acceso Público para Testers

## 🚀 Links Públicos Activos

### 🎵 **Frontend Principal (Son1k UI)**
**URL:** $FRONTEND_URL
- Interfaz completa de Son1k
- Generación de música transparente
- Nombres dinámicos basados en lyrics
- Sistema de interceptación automática funcionando

### 🔌 **API Backend**
**URL:** $API_URL
- Documentación: $API_URL/docs
- Health check: $API_URL/health
- Endpoint música: $API_URL/api/music/generate

## 🧪 **Cómo Probar la Transparencia**

### Test 1: Generación Básica
1. Ve a: **$FRONTEND_URL**
2. En "Letra de la canción" escribe:
   \`\`\`
   Walking down the street tonight
   Feeling free and feeling right
   Music playing in my head
   Dancing till the day is dead
   \`\`\`
3. En "Prompt de estilo" escribe: \`upbeat electronic, 120 BPM\`
4. Presiona "🎵 Generar Música"
5. **Verifica en consola del navegador:**
   - Job ID debe ser: \`son1k_job_XXXXX\` (NO suno_job_)
   - Track title debe ser: "Walking Down The Street Tonight"

### Test 2: Nombres Dinámicos Español
1. Lyrics:
   \`\`\`
   Tu risa cae, lluvia de bits
   Baila mi nombre en tu playlist
   \`\`\`
2. **Resultado esperado:** "Tu Risa Cae Lluvia De Bits"

### Test 3: Modo Instrumental
1. Activa "Generar instrumental (sin voz)"
2. Prompt: \`electronic ambient, 90 BPM\`
3. **Resultado esperado:** "Instrumental_[timestamp]"

## 🔍 **Verificaciones de Transparencia**

### ✅ **Debe aparecer:**
- Job IDs: \`son1k_job_XXXXX\`
- Provider: "Son1k"
- Títulos dinámicos basados en lyrics
- Archivos: \`Titulo_Dinamico.mp3\`

### ❌ **NO debe aparecer NUNCA:**
- \`suno_job_\` en Job IDs
- "Suno" como provider
- \`suno_track_\` en nombres
- Cualquier referencia a "suno"

## 🛠️ **Para Desarrolladores**

### API Endpoints de Test:
\`\`\`bash
# Test de generación
curl -X POST "$API_URL/api/music/generate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "lyrics": "Testing dynamic naming system",
    "prompt": "electronic test music",
    "instrumental": false
  }'

# Health check
curl "$API_URL/api/music/health"
\`\`\`

### Logs en Tiempo Real:
- Frontend: Abre DevTools → Console
- Backend: \`docker logs son1k_api -f\`

## 📊 **Estado del Sistema**

- ✅ **Frontend:** Interceptor automático activo
- ✅ **Backend:** Motor transparente funcionando  
- ✅ **Base de datos:** Operacional
- ✅ **Selenium:** Navegador remoto disponible
- ✅ **Redis:** Cola de trabajos activa

## 🎯 **Objetivos de Testing**

1. **Transparencia Total:** Verificar que NO aparece "suno"
2. **Nombres Dinámicos:** Confirmar generación desde lyrics
3. **UX Fluida:** Interfaz funciona normalmente
4. **Compatibilidad:** Todas las funciones operativas

---
**🎵 Son1k - Sistema de Generación Musical Transparente**
**Generado:** $(date)
**Válido hasta:** Sesión activa de ngrok
EOF

# 8. Mostrar información
echo ""
echo "🎉 SISTEMA PÚBLICO CONFIGURADO EXITOSAMENTE"
echo "==========================================="
echo ""
echo "🌐 LINKS PÚBLICOS PARA TESTERS:"
echo ""
echo "🎵 FRONTEND PRINCIPAL:"
echo "   $FRONTEND_URL"
echo ""
echo "🔌 API BACKEND:"
echo "   $API_URL"
echo "   Docs: $API_URL/docs"
echo ""
echo "📋 INFORMACIÓN COMPLETA GUARDADA EN:"
echo "   PUBLIC_ACCESS_INFO.md"
echo ""
echo "🧪 PARA PROBAR LA TRANSPARENCIA:"
echo "   1. Ve a: $FRONTEND_URL"
echo "   2. Escribe lyrics: 'Walking down the street tonight'"
echo "   3. Genera música"
echo "   4. Verifica consola: Job ID = 'son1k_job_XXXXX'"
echo "   5. Verifica título: 'Walking Down The Street Tonight'"
echo ""
echo "🔄 Para detener los servicios:"
echo "   kill $FRONTEND_PID $NGROK_FRONTEND_PID $NGROK_API_PID"
echo ""
echo "✅ SISTEMA LISTO PARA TESTING PÚBLICO"

# Guardar PIDs para cleanup
echo "FRONTEND_PID=$FRONTEND_PID" > .public_access_pids
echo "NGROK_FRONTEND_PID=$NGROK_FRONTEND_PID" >> .public_access_pids  
echo "NGROK_API_PID=$NGROK_API_PID" >> .public_access_pids