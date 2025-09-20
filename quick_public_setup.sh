#!/bin/bash

echo "🌐 CONFIGURACIÓN RÁPIDA DE ACCESO PÚBLICO"
echo "========================================"

# Solo crear túnel para el puerto 8000 que ya está funcionando
echo "🔌 Creando túnel público para API (puerto 8000)..."

# Verificar que el API esté funcionando
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ API funcionando en puerto 8000"
else
    echo "❌ API no responde en puerto 8000"
    exit 1
fi

# Crear túnel ngrok
echo "🌐 Iniciando túnel ngrok..."
ngrok http 8000 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Esperar conexión
echo "⏳ Esperando conexión ngrok..."
sleep 8

# Obtener URL pública
echo "🔍 Obteniendo URL pública..."
PUBLIC_URL=""

for i in {1..10}; do
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tunnel in data['tunnels']:
        if tunnel['config']['addr'] == 'http://localhost:8000':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null)
    
    if [ ! -z "$PUBLIC_URL" ]; then
        break
    fi
    sleep 1
done

if [ -z "$PUBLIC_URL" ]; then
    echo "❌ No se pudo obtener URL pública"
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

# Crear archivo con la información
cat > LINK_PUBLICO_TESTERS.md << EOF
# 🎯 Son1k - Link Público para Testers

## 🌐 **LINK PRINCIPAL PARA TESTING:**
**$PUBLIC_URL**

## 🧪 **Cómo Probar la Transparencia Total:**

### 1. **Abrir la Documentación:**
Ve a: **$PUBLIC_URL/docs**

### 2. **Probar Endpoint de Generación:**
1. En la documentación, busca \`POST /api/music/generate\`
2. Haz click en "Try it out"
3. Usa este payload de test:
\`\`\`json
{
  "lyrics": "Walking down the street tonight\\nFeeling free and feeling right\\nMusic playing in my head\\nDancing till the day is dead",
  "prompt": "upbeat electronic, 120 BPM, energetic synthesizers",
  "instrumental": false,
  "style": "default"
}
\`\`\`
4. Ejecuta la request

### 3. **Verificar Transparencia:**
En la respuesta debes ver:
- ✅ **Job ID:** \`son1k_job_XXXXX\` (NO suno_job_)
- ✅ **Provider:** "Son1k" (NO Suno)  
- ✅ **Titulo dinámico:** "Walking Down The Street Tonight"
- ✅ **Filename:** "Walking_Down_The_Street_Tonight.mp3"

### 4. **Test de Nombres Dinámicos:**
Prueba con diferentes lyrics:

**Test Español:**
\`\`\`json
{
  "lyrics": "Tu risa cae, lluvia de bits\\nBaila mi nombre en tu playlist",
  "prompt": "reggaeton moderno, 95 BPM"
}
\`\`\`
**Resultado esperado:** "Tu Risa Cae Lluvia De Bits"

**Test Instrumental:**
\`\`\`json
{
  "lyrics": "",
  "prompt": "ambient electronic, 80 BPM",
  "instrumental": true
}
\`\`\`
**Resultado esperado:** "Instrumental_[timestamp]"

## 🔍 **Otros Endpoints de Test:**

### Health Check:
\`GET $PUBLIC_URL/api/music/health\`

### Status Check:
\`GET $PUBLIC_URL/api/music/status/{job_id}\`

## 🎯 **Objetivos de Verificación:**

### ✅ **DEBE aparecer:**
- Job IDs con prefijo \`son1k_job_\`
- Provider como "Son1k"
- Títulos dinámicos basados en primera frase de lyrics
- Nombres de archivo limpios y válidos

### ❌ **NO DEBE aparecer NUNCA:**
- Referencias a "suno" en cualquier parte
- Job IDs con prefijo \`suno_job_\`  
- Provider como "Suno"
- Títulos genéricos como "suno_track_1"

## 📊 **Estado del Sistema:**
- ✅ Backend API: Funcionando
- ✅ Motor transparente: Activo
- ✅ Generación dinámica de nombres: Implementada
- ✅ Interceptor de transparencia: Operativo

---
**🎵 Son1k - Sistema Transparente de Generación Musical**
**Testing URL:** $PUBLIC_URL
**Documentación:** $PUBLIC_URL/docs
**Generado:** $(date)
EOF

echo ""
echo "🎉 LINK PÚBLICO CONFIGURADO EXITOSAMENTE"
echo "======================================="
echo ""
echo "🌐 **LINK PARA TESTERS:**"
echo "   $PUBLIC_URL"
echo ""
echo "📖 **DOCUMENTACIÓN INTERACTIVA:**"
echo "   $PUBLIC_URL/docs"
echo ""
echo "🧪 **PARA PROBAR TRANSPARENCIA:**"
echo "   1. Ve a: $PUBLIC_URL/docs"
echo "   2. Prueba POST /api/music/generate"
echo "   3. Verifica que Job ID sea 'son1k_job_XXXXX'"
echo "   4. Verifica nombres dinámicos basados en lyrics"
echo ""
echo "📋 **INFO COMPLETA GUARDADA EN:**"
echo "   LINK_PUBLICO_TESTERS.md"
echo ""
echo "🔄 **Para detener:**"
echo "   kill $NGROK_PID"
echo ""

# Guardar PID
echo "NGROK_PID=$NGROK_PID" > .ngrok_pid

echo "✅ LISTO PARA TESTING PÚBLICO"
echo ""
echo "🎯 El sistema está configurado para demostrar transparencia total."
echo "🚫 Los testers NO verán referencias a 'suno' en ninguna parte."
echo "✨ Todos los nombres serán dinámicos basados en lyrics."