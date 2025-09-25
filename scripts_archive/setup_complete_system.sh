#!/bin/bash

echo "🚀 Configurando Son1k Sistema Completo con Múltiples Cuentas"
echo "=========================================================="
echo

# Verificar dependencias
echo "🔍 Verificando dependencias..."

# Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado"
    echo "   Instala desde: https://nodejs.org/"
    exit 1
fi

# Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado"
    exit 1
fi

echo "✅ Dependencias básicas verificadas"

# Instalar dependencias de Python
echo "📦 Instalando dependencias de Python..."
pip3 install fastapi uvicorn aiohttp asyncio selenium numpy scipy

# Instalar dependencias de Node.js
echo "📦 Instalando dependencias de Node.js..."
npm install

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p generated_audio
mkdir -p logs
mkdir -p extension

# Hacer scripts ejecutables
echo "🔧 Configurando permisos..."
chmod +x *.py
chmod +x *.sh

# Crear archivo de configuración de cuentas
echo "🍪 Configurando múltiples cuentas de Suno..."
python3 setup_multi_accounts.py

# Crear archivo .env para el wrapper
echo "⚙️ Configurando variables de entorno..."
cat > .env << EOF
# Son1k Stealth Wrapper Configuration
PORT=3001

# Cookies de Suno (se configurarán automáticamente desde suno_accounts.json)
# No edites este archivo manualmente

# Configuración avanzada
MAX_CONCURRENT_REQUESTS=3
RETRY_ATTEMPTS=3
DELAY_BETWEEN_ATTEMPTS=2000
ROTATION_INTERVAL=300
EOF

# Crear script de inicio completo
echo "📝 Creando script de inicio completo..."
cat > start_complete_system.sh << 'EOF'
#!/bin/bash

echo "🚀 Iniciando Son1k Sistema Completo"
echo "=================================="

# Función para limpiar procesos al salir
cleanup() {
    echo "🛑 Deteniendo sistema..."
    pkill -f "node suno_wrapper_server.js"
    pkill -f "python3 son1k_simple_stable.py"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar servidor Node.js en background
echo "🌐 Iniciando Suno Stealth Wrapper..."
cd "$(dirname "$0")"
node suno_wrapper_server.js &
NODE_PID=$!

# Esperar a que el servidor Node.js esté listo
echo "⏳ Esperando a que el wrapper esté listo..."
sleep 5

# Verificar que el wrapper esté funcionando
if curl -s http://localhost:3001/health > /dev/null; then
    echo "✅ Suno Stealth Wrapper iniciado correctamente"
else
    echo "❌ Error iniciando Suno Stealth Wrapper"
    exit 1
fi

# Iniciar servidor Python
echo "🐍 Iniciando Son1k Python Server..."
python3 son1k_simple_stable.py &
PYTHON_PID=$!

# Esperar a que el servidor Python esté listo
echo "⏳ Esperando a que el servidor Python esté listo..."
sleep 3

# Verificar que el servidor Python esté funcionando
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Son1k Python Server iniciado correctamente"
else
    echo "❌ Error iniciando Son1k Python Server"
    kill $NODE_PID
    exit 1
fi

echo ""
echo "🎉 ¡Sistema completo iniciado!"
echo "================================"
echo "🌐 Interfaz web: http://localhost:3001"
echo "🐍 API Python: http://localhost:8000"
echo "📊 Estadísticas: http://localhost:3001/stats"
echo "💚 Salud: http://localhost:8000/api/health"
echo ""
echo "🎵 Para generar música:"
echo "   - Usa la interfaz web en http://localhost:3001"
echo "   - O envía peticiones POST a http://localhost:8000/api/music/generate"
echo ""
echo "⏹️ Presiona Ctrl+C para detener el sistema"

# Mantener el script ejecutándose
wait
EOF

chmod +x start_complete_system.sh

# Crear script de prueba
echo "🧪 Creando script de prueba..."
cat > test_complete_system.py << 'EOF'
#!/usr/bin/env python3
"""
Prueba completa del sistema Son1k con múltiples cuentas
"""
import asyncio
import aiohttp
import json

async def test_complete_system():
    """Probar el sistema completo"""
    
    print("🚀 Probando Sistema Completo Son1k")
    print("=" * 40)
    
    # Verificar servicios
    services = [
        ("Suno Stealth Wrapper", "http://localhost:3001/health"),
        ("Son1k Python Server", "http://localhost:8000/api/health")
    ]
    
    for name, url in services:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"✅ {name}: OK")
                    else:
                        print(f"❌ {name}: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ {name}: {e}")
            return False
    
    # Probar generación de música
    print("\n🎵 Probando generación de música...")
    
    test_prompts = [
        "una canción de rock sobre la libertad",
        "música electrónica futurista",
        "jazz suave para relajarse"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Prueba {i}: {prompt} ---")
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "prompt": prompt,
                    "lyrics": "",
                    "style": "profesional"
                }
                
                async with session.post(
                    "http://localhost:8000/api/music/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Generación iniciada: {data.get('job_id')}")
                        print(f"📝 Modo: {data.get('mode', 'unknown')}")
                        print(f"💬 Mensaje: {data.get('message', 'N/A')}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error: HTTP {response.status} - {error_text}")
                        
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
        
        # Pausa entre pruebas
        if i < len(test_prompts):
            await asyncio.sleep(5)
    
    print("\n✅ Pruebas completadas")
    return True

if __name__ == "__main__":
    asyncio.run(test_complete_system())
EOF

chmod +x test_complete_system.py

echo ""
echo "✅ Configuración completada!"
echo "============================"
echo ""
echo "🚀 Para iniciar el sistema completo:"
echo "   ./start_complete_system.sh"
echo ""
echo "🧪 Para probar el sistema:"
echo "   python3 test_complete_system.py"
echo ""
echo "📊 Para ver estadísticas:"
echo "   curl http://localhost:3001/stats"
echo ""
echo "🎵 Para generar música:"
echo "   Abre http://localhost:3001 en tu navegador"
echo ""
echo "📝 Archivos importantes creados:"
echo "   - suno_accounts.json (configuración de cuentas)"
echo "   - .env (variables de entorno)"
echo "   - start_complete_system.sh (script de inicio)"
echo "   - test_complete_system.py (script de prueba)"
echo ""
echo "🔧 Para configurar más cuentas:"
echo "   python3 setup_multi_accounts.py"






