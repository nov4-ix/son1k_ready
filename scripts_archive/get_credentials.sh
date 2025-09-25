#!/bin/bash

echo "🎵 EXTRACTOR CREDENCIALES SUNO - SCRIPT SIMPLIFICADO"
echo "======================================================"

echo ""
echo "PASOS PARA EXTRAER CREDENCIALES:"
echo "1. Ve a https://suno.com en tu navegador"
echo "2. Loguéate en tu cuenta"
echo "3. Abre DevTools (F12) → pestaña Network"
echo "4. Recarga la página o haz cualquier acción"
echo "5. Busca una request a 'studio-api.suno.ai'"
echo "6. Click derecho → Copy → Copy as cURL"
echo ""

echo "EJEMPLO DE LO QUE BUSCAS:"
echo "Cookie: session_id=sess_abc123; __session=eyJhbGc..."
echo ""

echo "TAMBIÉN BUSCA EN APPLICATION → COOKIES:"
echo "- Cualquier valor que empiece con 'sess_'"
echo "- La cookie completa de suno.com"
echo ""

echo "UNA VEZ QUE TENGAS LAS CREDENCIALES:"
echo "export SUNO_SESSION_ID='sess_tu_session_aqui'"
echo "export SUNO_COOKIE='toda_la_cookie_completa_aqui'"
echo ""

echo "LUEGO EJECUTA:"
echo "python3 main_production.py"
echo ""

echo "Si tienes las credenciales listas, edita manualmente main_production.py líneas 31-32"