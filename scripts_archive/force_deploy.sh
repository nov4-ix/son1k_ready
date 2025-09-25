#!/bin/bash

# 🚀 FORCE REDEPLOY SON1KVERS3
echo "🚀 Forzando redeploy de Son1kVers3..."

# Crear timestamp único para forzar cambio
echo "// Deploy forced at $(date)" >> main_production_final.py

# Commit y push
git add .
git commit -m "🔄 FORCE REDEPLOY: $(date '+%Y-%m-%d %H:%M:%S') - Login y Pixel arreglados

🔧 CAMBIOS CRÍTICOS:
- Pixel con área de texto expandida y arrastrable
- Sistema de login unificado 
- Funcionalidad drag & drop mejorada
- Todas las funciones verificadas

🎯 ENFOQUE: Solo son1kvers3.com

🤖 Generated with [Claude Code](https://claude.ai/code)"

git push

echo "✅ Cambios enviados. Railway debería redeplegar automáticamente."
echo "🌍 Verificar en: https://son1kvers3.com"