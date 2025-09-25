#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"
cd "$PROJECT_DIR"

# --- venv y PYTHONPATH ---
source .venv/bin/activate
export PYTHONPATH="$PWD"

echo "🐳 Levantando Selenium (standalone-chrome con noVNC)…"
docker compose up -d selenium

# Espera WebDriver
echo "⏳ Esperando Selenium WebDriver en :4444…"
for i in {1..30}; do
  if curl -s http://localhost:4444/wd/hub/status | grep -q '"ready": true' ; then
    echo "✅ Selenium listo"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ Selenium no respondió a tiempo"; exit 1
  fi
  sleep 1
done

# Espera noVNC
echo "⏳ Esperando noVNC en :7900…"
for i in {1..30}; do
  if curl -s http://localhost:7900 >/dev/null ; then
    echo "✅ noVNC listo"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ noVNC no respondió a tiempo"; exit 1
  fi
  sleep 1
done

# Matar ngrok previos (opcional)
pkill -f "ngrok http" || true
sleep 1

echo "🌐 Abriendo túnel ngrok con auth básica (v3)…"
# NOTA: en ngrok v3 es --basic-auth "user:pass"
ngrok http --basic-auth "son1k:captcha" 7900 > ngrok.log 2>&1 &
NGROK_PID=$!

# Espera API local de ngrok
for i in {1..20}; do
  if curl -s http://127.0.0.1:4040/api/tunnels >/dev/null ; then
    break
  fi
  sleep 1
done

# Captura URL pública https
NOVNC_PUBLIC_URL="$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c 'import sys,json; d=json.load(sys.stdin); ts=[t["public_url"] for t in d.get("tunnels",[]) if t.get("public_url","").startswith("https://")]; print(ts[0] if ts else "")')"
if [ -z "$NOVNC_PUBLIC_URL" ]; then
  echo "❌ No pude obtener NOVNC_PUBLIC_URL desde ngrok"; exit 1
fi

# Export env para el worker/automatización
export SV_SELENIUM_URL="http://localhost:4444"
export NOVNC_PUBLIC_URL
export SV_CHROME_PROFILE_DIR="$PWD/.selenium_profile_suno"
export SV_HEADLESS=0
export SV_NO_QUIT=1
export SON1K_FRONTEND_PUSH=1

# Letras/prompt demo (puedes cambiarlos)
export SV_LYRICS=$'Neon rain over midnight streets\nEngines hum, hearts don’t sleep'
export SV_PROMPT='cyberpunk synthwave, 120 BPM, dark & cinematic'

echo "🖥️ noVNC URL (abre en tu navegador): $NOVNC_PUBLIC_URL  (user: son1k / pass: captcha)"

# Chequeo backend (opcional: lo puedes lanzar tú en otra terminal)
if ! curl -s http://localhost:8000/api/health | grep -q '"ok":true'; then
  echo "⚠️ Tu FastAPI no responde en :8000"
  echo "   Lánzalo en otra terminal:"
  echo "   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
else
  echo "✅ Backend OK en :8000"
fi

echo ""
echo "✅ Entorno listo:"
echo "   - Selenium remoto:  http://localhost:4444"
echo "   - noVNC público:    $NOVNC_PUBLIC_URL  (basic auth)"
echo "   - Perfil Chrome:    $SV_CHROME_PROFILE_DIR"
echo ""
echo "👉 Siguiente paso (SÓLO la primera vez para cachear login):"
echo "   python3 scripts/login_and_cache_session.py"
echo ""
echo "👉 Luego, para generar pista (con push al frontend si lo conectaste):"
echo "   python3 scripts/run_suno_create.py"
echo ""
echo "ℹ️ Si aparece CAPTCHA, tu frontend mostrará el banner con este link."
