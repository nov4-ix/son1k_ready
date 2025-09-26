#!/bin/bash
# 🤖 SON1KVERS3 - Ollama Installation Script
# Script para instalar y configurar Ollama para IA local

set -e

echo "🤖 INSTALANDO OLLAMA PARA SON1KVERS3"
echo "====================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar sistema operativo
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_status "Sistema operativo detectado: $OS"
}

# Instalar Ollama
install_ollama() {
    print_status "Instalando Ollama..."
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama ya está instalado"
        return 0
    fi
    
    case $OS in
        "macos")
            print_status "Instalando Ollama en macOS..."
            curl -fsSL https://ollama.ai/install.sh | sh
            ;;
        "linux")
            print_status "Instalando Ollama en Linux..."
            curl -fsSL https://ollama.ai/install.sh | sh
            ;;
        "windows")
            print_error "Windows no soportado automáticamente. Por favor instala Ollama manualmente desde https://ollama.ai"
            exit 1
            ;;
        *)
            print_error "Sistema operativo no soportado: $OS"
            exit 1
            ;;
    esac
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama instalado correctamente"
    else
        print_error "Error instalando Ollama"
        exit 1
    fi
}

# Descargar modelos necesarios
download_models() {
    print_status "Descargando modelos de IA necesarios..."
    
    # Lista de modelos necesarios
    MODELS=(
        "llama3.1:8b"
        "mistral:7b"
        "codellama:7b"
    )
    
    for model in "${MODELS[@]}"; do
        print_status "Descargando modelo: $model"
        ollama pull "$model" || {
            print_warning "Error descargando $model, continuando..."
        }
    done
    
    print_success "Modelos descargados"
}

# Iniciar Ollama
start_ollama() {
    print_status "Iniciando Ollama..."
    
    # Verificar si Ollama ya está corriendo
    if pgrep -f "ollama serve" > /dev/null; then
        print_success "Ollama ya está corriendo"
    else
        print_status "Iniciando Ollama en segundo plano..."
        nohup ollama serve > ollama.log 2>&1 &
        sleep 5
        
        if pgrep -f "ollama serve" > /dev/null; then
            print_success "Ollama iniciado correctamente"
        else
            print_error "Error iniciando Ollama"
            exit 1
        fi
    fi
}

# Instalar dependencias de Python
install_python_deps() {
    print_status "Instalando dependencias de Python..."
    
    # Crear requirements.txt para Ollama
    cat > ollama_requirements.txt << EOF
aiohttp>=3.8.0
asyncio
requests>=2.28.0
EOF
    
    pip install -r ollama_requirements.txt || {
        print_warning "Error instalando dependencias de Python, continuando..."
    }
    
    print_success "Dependencias de Python instaladas"
}

# Crear script de inicio
create_startup_script() {
    print_status "Creando script de inicio..."
    
    cat > start_ollama_ai.sh << 'EOF'
#!/bin/bash
# Script para iniciar Ollama AI para Son1kVers3

echo "🤖 Iniciando Ollama AI para Son1kVers3..."

# Verificar si Ollama está corriendo
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Iniciando Ollama..."
    nohup ollama serve > ollama.log 2>&1 &
    sleep 5
fi

# Iniciar servidor de IA
echo "Iniciando servidor de IA..."
python3 ollama_music_ai.py &
AI_PID=$!

echo "✅ Ollama AI iniciado (PID: $AI_PID)"
echo "🌐 Servidor IA: http://localhost:8001"
echo "🤖 Ollama: http://localhost:11434"
echo ""
echo "Para detener: kill $AI_PID && pkill -f 'ollama serve'"
EOF
    
    chmod +x start_ollama_ai.sh
    print_success "Script de inicio creado: start_ollama_ai.sh"
}

# Crear script de prueba
create_test_script() {
    print_status "Creando script de prueba..."
    
    cat > test_ollama_ai.py << 'EOF'
#!/usr/bin/env python3
"""
Script de prueba para Ollama Music AI
"""

import asyncio
import aiohttp
import json

async def test_ollama_ai():
    base_url = "http://localhost:8001"
    
    print("🤖 Probando Ollama Music AI...")
    
    try:
        # Test 1: Health check
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check: {data}")
                else:
                    print(f"❌ Health check falló: {response.status}")
                    return
        
        # Test 2: Análisis musical
        test_prompt = "una canción épica de synthwave sobre la resistencia digital"
        print(f"\n🎵 Probando análisis: '{test_prompt}'")
        
        async with session.post(f"{base_url}/api/analyze", json={"prompt": test_prompt}) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Análisis: {json.dumps(data['analysis'], indent=2)}")
            else:
                print(f"❌ Análisis falló: {response.status}")
        
        # Test 3: Generación de letras
        print(f"\n📝 Probando generación de letras...")
        
        async with session.post(f"{base_url}/api/lyrics", json={
            "prompt": test_prompt,
            "style": "synthwave",
            "language": "es"
        }) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Letras: {data['lyrics'][:100]}...")
            else:
                print(f"❌ Letras falló: {response.status}")
        
        print("\n🎉 Pruebas completadas!")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama_ai())
EOF
    
    chmod +x test_ollama_ai.py
    print_success "Script de prueba creado: test_ollama_ai.py"
}

# Función principal
main() {
    print_status "Iniciando instalación de Ollama para Son1kVers3..."
    
    # Detectar sistema operativo
    detect_os
    
    # Instalar Ollama
    install_ollama
    
    # Descargar modelos
    download_models
    
    # Instalar dependencias de Python
    install_python_deps
    
    # Iniciar Ollama
    start_ollama
    
    # Crear scripts
    create_startup_script
    create_test_script
    
    print_success "¡Instalación completada!"
    echo ""
    echo "🚀 PRÓXIMOS PASOS:"
    echo "1. Ejecutar: ./start_ollama_ai.sh"
    echo "2. Probar: python3 test_ollama_ai.py"
    echo "3. Abrir: http://localhost:8080 (frontend)"
    echo ""
    echo "📚 DOCUMENTACIÓN:"
    echo "- Ollama: https://ollama.ai"
    echo "- Modelos: https://ollama.ai/library"
    echo ""
    echo "🎵 ¡Disfruta de la IA local en Son1kVers3!"
}

# Ejecutar función principal
main "$@"
