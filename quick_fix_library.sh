#!/bin/bash

echo "🔧 Solución Rápida: Música en Biblioteca de Suno"
echo "================================================"
echo

# Verificar si el wrapper está ejecutándose
if ! curl -s http://localhost:3001/health > /dev/null; then
    echo "❌ Wrapper no está ejecutándose"
    echo "   Iniciando wrapper..."
    node suno_wrapper_server.js &
    sleep 3
fi

# Verificar si el servidor Python está ejecutándose
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ Servidor Python no está ejecutándose"
    echo "   Iniciando servidor..."
    python3 son1k_simple_stable.py &
    sleep 3
fi

echo "✅ Servicios verificados"
echo

# Verificar configuración de cuentas
if [ ! -f "suno_accounts.json" ]; then
    echo "❌ No hay configuración de cuentas"
    echo "   Creando configuración básica..."
    
    cat > suno_accounts.json << 'EOF'
{
  "accounts": [
    {
      "id": "account_1",
      "email": "nov4-ix@gmail.com",
      "cookie": "TU_COOKIE_DE_SUNO_AQUI",
      "priority": 1,
      "max_daily_usage": 50,
      "created_at": "2025-09-24T14:30:00.000Z"
    }
  ],
  "settings": {
    "rotation_interval": 300,
    "load_balancer": "weighted",
    "cooldown_time": 60,
    "max_concurrent": 3
  }
}
EOF
    
    echo "📝 Archivo suno_accounts.json creado"
    echo "   Necesitas configurar tu cookie de Suno"
fi

echo
echo "🎯 Para que la música aparezca en tu biblioteca:"
echo
echo "1. Obtén tu cookie de Suno:"
echo "   - Ve a https://suno.com"
echo "   - Inicia sesión"
echo "   - F12 > Application > Cookies > https://suno.com"
echo "   - Busca 'session_token' o 'auth_token'"
echo "   - Copia el valor completo"
echo
echo "2. Configura la cookie:"
echo "   python3 setup_suno_cookie_simple.py"
echo
echo "3. Verifica la configuración:"
echo "   python3 fix_library_issue.py"
echo
echo "4. Reinicia el sistema:"
echo "   pkill -f 'python3 son1k_simple_stable.py'"
echo "   python3 son1k_simple_stable.py &"
echo
echo "5. Prueba generando música:"
echo "   - Ve a http://localhost:3001"
echo "   - Genera una canción"
echo "   - Revisa tu biblioteca en https://suno.com"
echo
echo "📊 Estado actual del sistema:"
echo "   Wrapper: $(curl -s http://localhost:3001/health | grep -o '"status":"[^"]*"' || echo 'No disponible')"
echo "   Python: $(curl -s http://localhost:8000/api/health | grep -o '"status":"[^"]*"' || echo 'No disponible')"
echo "   Cookies: $(curl -s http://localhost:3001/health | grep -o '"total":[0-9]*' || echo 'No disponible')"
echo
echo "🎵 ¡Una vez configurado, la música aparecerá en tu biblioteca de Suno!"




