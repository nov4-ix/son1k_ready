#!/bin/bash

echo "🚀 Configurando Son1k Stealth Generator..."

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Instalando..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install node
        else
            echo "⚠️ Por favor instala Node.js desde https://nodejs.org/"
            exit 1
        fi
    else
        echo "⚠️ Por favor instala Node.js desde https://nodejs.org/"
        exit 1
    fi
fi

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm no está instalado"
    exit 1
fi

echo "✅ Node.js y npm están instalados"

# Instalar dependencias
echo "📦 Instalando dependencias..."
npm install

# Crear archivo de configuración de cookies
echo "🍪 Configurando cookies de Suno..."

cat > .env << EOF
# Configuración de Suno Stealth Generator
PORT=3001

# Cookies de Suno (obtén estas desde tu navegador en suno.com)
# Instrucciones:
# 1. Ve a suno.com en tu navegador
# 2. Abre las herramientas de desarrollador (F12)
# 3. Ve a la pestaña Network/Red
# 4. Recarga la página
# 5. Busca cualquier petición a suno.com
# 6. Copia el valor de la cookie 'session_token' o 'auth_token'
# 7. Pega el valor aquí:

SUNO_COOKIE=tu_cookie_de_suno_aqui
SUNO_COOKIE_2=
SUNO_COOKIE_3=

# Opcional: Configuración avanzada
MAX_CONCURRENT_REQUESTS=2
RETRY_ATTEMPTS=3
DELAY_BETWEEN_ATTEMPTS=2000
EOF

echo "📝 Archivo .env creado. Por favor edita las cookies de Suno:"
echo "   1. Abre .env en un editor"
echo "   2. Reemplaza 'tu_cookie_de_suno_aqui' con tu cookie real de Suno"
echo "   3. Guarda el archivo"

echo ""
echo "🔧 Para obtener tu cookie de Suno:"
echo "   1. Ve a https://suno.com en tu navegador"
echo "   2. Inicia sesión"
echo "   3. Abre las herramientas de desarrollador (F12)"
echo "   4. Ve a Application/Storage > Cookies"
echo "   5. Busca 'session_token' o 'auth_token'"
echo "   6. Copia el valor y pégalo en .env"

echo ""
echo "🚀 Para ejecutar el servidor:"
echo "   npm start"
echo ""
echo "🌐 Luego ve a: http://localhost:3001"

# Hacer el script ejecutable
chmod +x setup_suno_stealth.sh

echo "✅ Configuración completada!"




