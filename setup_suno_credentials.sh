#!/bin/bash

echo "🎵 CONFIGURACIÓN DE CREDENCIALES DE SUNO"
echo "========================================"
echo ""
echo "Para que la música aparezca en tu biblioteca de Suno.com,"
echo "necesitamos configurar tus credenciales reales."
echo ""

# Crear archivo de credenciales con valores por defecto
cat > suno_credentials.json << 'EOF'
{
  "email": "soypepejaimes@gmail.com",
  "password": "TU_PASSWORD_AQUI",
  "cookie": "[]",
  "session_token": "",
  "user_id": "",
  "last_login": null
}
EOF

echo "✅ Archivo de credenciales creado: suno_credentials.json"
echo ""
echo "📋 INSTRUCCIONES:"
echo "1. Edita el archivo suno_credentials.json"
echo "2. Reemplaza 'TU_PASSWORD_AQUI' con tu password real de Suno"
echo "3. Reinicia el servidor"
echo ""
echo "🔧 Comando para editar:"
echo "nano suno_credentials.json"
echo ""
echo "🔄 Comando para reiniciar:"
echo "pkill -f son1k_simple_stable.py && python3 son1k_simple_stable.py &"




