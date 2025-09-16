#!/bin/bash
# Script para arrancar Google Chrome/Chromium con extensión MV3 cargada
# Uso: ./run_chrome_dev.sh /ruta/a/extension

EXT_DIR="$1"

if [ -z "$EXT_DIR" ]; then
  echo "❌ Debes pasar la ruta de la extensión como argumento."
  echo "Ejemplo: ./run_chrome_dev.sh ~/son1k_suno_poc_mvp_v2/extension"
  exit 1
fi

# Detectar si tienes google-chrome o chromium
if command -v google-chrome >/dev/null 2>&1; then
  BROWSER="google-chrome"
elif command -v chromium >/dev/null 2>&1; then
  BROWSER="chromium"
else
  echo "❌ No se encontró Google Chrome ni Chromium en tu PATH."
  exit 1
fi

# Lanzar con perfil temporal para no chocar con el Chrome normal
"$BROWSER"   --user-data-dir=/tmp/chrome-son1k-profile   --disable-extensions-except="$EXT_DIR"   --load-extension="$EXT_DIR"
