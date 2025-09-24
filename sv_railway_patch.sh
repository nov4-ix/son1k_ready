#!/usr/bin/env bash
set -euo pipefail

# ==========================================================
# SV Railway Auto Patch
# - Inserta CORS, /health y binding a $PORT en FastAPI
# - Funciona con main_production_final.py (preferido)
#   o con apps/api/main.py como fallback
# - Crea backup .bak y es idempotente
# Usage:
#   chmod +x sv_railway_patch.sh
#   ./sv_railway_patch.sh
# Opcional:
#   API_FILE=path/al/archivo.py ./sv_railway_patch.sh
# ==========================================================

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

API_FILE="${API_FILE:-}"
if [[ -z "${API_FILE}" ]]; then
  if [[ -f "main_production_final.py" ]]; then
    API_FILE="main_production_final.py"
  elif [[ -f "apps/api/main.py" ]]; then
    API_FILE="apps/api/main.py"
  else
    echo "❌ No se encontró main_production_final.py ni apps/api/main.py"
    echo "    Exporta API_FILE=/ruta/a/tu/app.py y reintenta."
    exit 1
  fi
fi

if [[ ! -f "$API_FILE" ]]; then
  echo "❌ Archivo no encontrado: $API_FILE"
  exit 1
fi

echo "🛠  Parchando: $API_FILE"
cp "$API_FILE" "$API_FILE.bak"

# ---- Python patcher inline (regex seguro e idempotente) ----
python3 - <<'PY'
import os, sys, re, io

api_path = os.environ.get("API_FILE")
with open(api_path, "r", encoding="utf-8") as f:
    src = f.read()

original = src

# 1) Importación de CORS si falta
if "from fastapi.middleware.cors import CORSMiddleware" not in src:
    # Insertar cerca del import FastAPI
    src = re.sub(
        r"(from\s+fastapi\s+import\s+FastAPI\s*\n)",
        r"\1from fastapi.middleware.cors import CORSMiddleware\n",
        src,
        count=1,
        flags=re.M
    )

# 2) Crear app si no existe (raro, pero por si acaso)
if re.search(r"\bapp\s*=\s*FastAPI\(", src) is None:
    src = re.sub(
        r"(\Z)",
        r'\n\napp = FastAPI(title="Son1kVers3 API")\n',
        src,
        count=1
    )

# 3) Inyectar CORS (idempotente)
if "add_middleware(CORSMiddleware" not in src:
    cors_block = '''
# --- CORS (Railway) ---
ALLOWED_ORIGINS = [
    "https://*.railway.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''.strip("\n")
    # lo ponemos después de la creación de app
    src = re.sub(
        r"(app\s*=\s*FastAPI\([^\)]*\)\s*)",
        r"\1\n" + cors_block + "\n",
        src,
        count=1,
        flags=re.S
    )

# 4) Endpoint /health (idempotente)
if re.search(r"@app\.get\([\"']\/health[\"']\)", src) is None:
    src += '''

@app.get("/health")
def health():
    return {"status": "ok"}
'''

# 5) Bloque __main__ con $PORT (idempotente)
if "__main__" not in src or "uvicorn.run(" not in src:
    # Añadimos bloque main al final
    src += '''

if __name__ == "__main__":
    import uvicorn, os
    port = int(os.getenv("PORT", "8000"))
    # Nota: cambia "main_production_final:app" por tu módulo si es otro:
    module_path = "{}:app"
    uvicorn.run(module_path, host="0.0.0.0", port=port)
'''.format(os.path.splitext(os.path.basename(api_path))[0])
else:
    # Existe; nos aseguramos de usar $PORT
    # reemplazar cualquier port hardcodeado por os.getenv("PORT", "8000")
    src = re.sub(
        r"(uvicorn\.run\([^\)]*port\s*=\s*)(\d+|\"?\$?PORT\"?)",
        r"\1int(os.getenv(\"PORT\", \"8000\"))",
        src
    )
    if "os.getenv(\"PORT\"" not in src:
        # asegurar import os en ese bloque
        if "import os" not in src:
            src = re.sub(
                r"(if __name__ == .__main__.:.*?\n)",
                r"\1    import os\n",
                src,
                flags=re.S
            )

# Guardar si hubo cambios
if src != original:
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(src)
    print("✅ Patch aplicado a", api_path)
else:
    print("ℹ️  Nada que cambiar, ya estaba listo:", api_path)
PY

# ---- Crear/actualizar .env.example mínimo ----
if [[ ! -f ".env.example" ]]; then
  cat > .env.example <<'ENVX'
# Entorno por defecto
ENV=prod
# Frontend -> Backend (ajusta al dominio real de tu API en Railway)
NEXT_PUBLIC_API_BASE=https://<tu-api>.railway.app
ENVX
  echo "✅ .env.example creado"
else
  echo "ℹ️  .env.example ya existe (no modificado)"
fi

# ---- Tips de arranque Railway ----
echo
echo "==============================================="
echo "🚂  Railway — Start Command recomendado:"
echo "uvicorn $(basename ${API_FILE%.*}):app --host 0.0.0.0 --port \$PORT --workers 1"
echo "==============================================="
echo "CORS: asegúrate de agregar tu dominio frontend a ALLOWED_ORIGINS."
echo "Healthcheck: usa /health en Railway Settings."
echo "Backup del archivo: ${API_FILE}.bak"
