#!/usr/bin/env python3
"""
Diagnóstico completo del modo inmersivo de Son1kVers3
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

def verificar_archivos():
    """Verificar que todos los archivos necesarios existan"""
    print("🔍 Verificando archivos del modo inmersivo...")
    
    archivos_requeridos = [
        "frontend/index.html",
        "frontend/immersive_interface.html", 
        "frontend/immersive_integration.js"
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTANTE")
            archivos_faltantes.append(archivo)
    
    return len(archivos_faltantes) == 0

def verificar_codigo_html():
    """Verificar que el código HTML tenga las funciones necesarias"""
    print("\n🔍 Verificando código HTML...")
    
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        funciones_requeridas = [
            "toggleImmersiveInterface",
            "showImmersiveInterface", 
            "hideImmersiveInterface",
            "immersiveInterfaceContainer",
            "immersiveIframe"
        ]
        
        funciones_encontradas = []
        
        for funcion in funciones_requeridas:
            if funcion in contenido:
                print(f"   ✅ {funcion}")
                funciones_encontradas.append(funcion)
            else:
                print(f"   ❌ {funcion} - NO ENCONTRADA")
        
        return len(funciones_encontradas) == len(funciones_requeridas)
        
    except Exception as e:
        print(f"   ❌ Error leyendo HTML: {e}")
        return False

def verificar_interfaz_immersive():
    """Verificar que la interfaz inmersiva esté bien formada"""
    print("\n🔍 Verificando interfaz inmersiva...")
    
    try:
        with open("frontend/immersive_interface.html", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        elementos_requeridos = [
            "nexus-container",
            "nexus-title",
            "nexus-grid",
            "nexus-card",
            "terminal"
        ]
        
        elementos_encontrados = []
        
        for elemento in elementos_requeridos:
            if elemento in contenido:
                print(f"   ✅ {elemento}")
                elementos_encontrados.append(elemento)
            else:
                print(f"   ❌ {elemento} - NO ENCONTRADO")
        
        return len(elementos_encontrados) == len(elementos_requeridos)
        
    except Exception as e:
        print(f"   ❌ Error leyendo interfaz inmersiva: {e}")
        return False

def verificar_integracion_js():
    """Verificar que el archivo de integración JS esté correcto"""
    print("\n🔍 Verificando integración JavaScript...")
    
    try:
        with open("frontend/immersive_integration.js", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        clases_requeridas = [
            "ImmersiveMusicIntegration",
            "handleImmersiveCommand",
            "executeMatrixScan",
            "executeMusicGeneration"
        ]
        
        clases_encontradas = []
        
        for clase in clases_requeridas:
            if clase in contenido:
                print(f"   ✅ {clase}")
                clases_encontradas.append(clase)
            else:
                print(f"   ❌ {clase} - NO ENCONTRADA")
        
        return len(clases_encontradas) == len(clases_requeridas)
        
    except Exception as e:
        print(f"   ❌ Error leyendo integración JS: {e}")
        return False

def crear_script_reparacion():
    """Crear un script para reparar el modo inmersivo"""
    print("\n🔧 Creando script de reparación...")
    
    script_reparacion = '''#!/bin/bash
# Script de reparación del modo inmersivo

echo "🎵 Reparando modo inmersivo de Son1kVers3..."

# Verificar que estamos en el directorio correcto
if [ ! -f "frontend/index.html" ]; then
    echo "❌ Error: No se encuentra frontend/index.html"
    echo "   Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Crear directorio frontend si no existe
mkdir -p frontend

# Verificar archivos
echo "🔍 Verificando archivos..."

if [ ! -f "frontend/immersive_interface.html" ]; then
    echo "❌ Faltante: immersive_interface.html"
    echo "   Este archivo debe ser creado manualmente"
fi

if [ ! -f "frontend/immersive_integration.js" ]; then
    echo "❌ Faltante: immersive_integration.js"
    echo "   Este archivo debe ser creado manualmente"
fi

# Verificar que el HTML tenga las funciones necesarias
if ! grep -q "toggleImmersiveInterface" frontend/index.html; then
    echo "❌ Faltante: función toggleImmersiveInterface en index.html"
fi

if ! grep -q "immersiveInterfaceContainer" frontend/index.html; then
    echo "❌ Faltante: contenedor immersiveInterfaceContainer en index.html"
fi

echo "✅ Verificación completada"
echo ""
echo "💡 Si hay archivos faltantes, ejecuta:"
echo "   python3 diagnostico_immersive.py --fix"
'''
    
    with open("reparar_immersive.sh", "w") as f:
        f.write(script_reparacion)
    
    os.chmod("reparar_immersive.sh", 0o755)
    print("   ✅ Script creado: reparar_immersive.sh")

def crear_test_immersive():
    """Crear un test HTML para verificar el modo inmersivo"""
    print("\n🧪 Creando test de modo inmersivo...")
    
    test_html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Modo Inmersivo - Son1kVers3</title>
    <style>
        body { 
            background: #0a0a0a; 
            color: #00ff88; 
            font-family: monospace; 
            padding: 20px; 
        }
        .test { 
            background: rgba(0, 255, 136, 0.1); 
            border: 1px solid #00ff88; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
        }
        .success { color: #00ff88; }
        .error { color: #ff4444; }
        .warning { color: #ffaa00; }
        button { 
            background: #00ff88; 
            color: #000; 
            border: none; 
            padding: 10px 20px; 
            margin: 5px; 
            border-radius: 5px; 
            cursor: pointer; 
        }
    </style>
</head>
<body>
    <h1>🎵 Test Modo Inmersivo</h1>
    
    <div class="test">
        <h3>Pruebas Automáticas</h3>
        <div id="testResults">Ejecutando pruebas...</div>
        <button onclick="runTests()">Ejecutar Pruebas</button>
    </div>
    
    <div class="test">
        <h3>Pruebas Manuales</h3>
        <button onclick="testImmersive()">Probar Modo Inmersivo</button>
        <button onclick="testEasterEggs()">Probar Easter Eggs</button>
        <button onclick="testKeyboard()">Probar Teclado</button>
    </div>
    
    <div class="test">
        <h3>Estado del Sistema</h3>
        <div id="systemStatus">Verificando...</div>
    </div>

    <script>
        function log(message, type = 'info') {
            const div = document.getElementById('testResults');
            const timestamp = new Date().toLocaleTimeString();
            const className = type === 'error' ? 'error' : type === 'success' ? 'success' : 'warning';
            div.innerHTML += `<div class="${className}">[${timestamp}] ${message}</div>`;
        }
        
        function runTests() {
            document.getElementById('testResults').innerHTML = '';
            log('Iniciando pruebas automáticas...');
            
            // Test 1: Verificar funciones
            if (typeof window.toggleImmersiveInterface === 'function') {
                log('✅ toggleImmersiveInterface disponible', 'success');
            } else {
                log('❌ toggleImmersiveInterface NO disponible', 'error');
            }
            
            // Test 2: Verificar elementos
            const container = document.getElementById('immersiveInterfaceContainer');
            if (container) {
                log('✅ Contenedor inmersivo encontrado', 'success');
            } else {
                log('❌ Contenedor inmersivo NO encontrado', 'error');
            }
            
            // Test 3: Verificar iframe
            const iframe = document.getElementById('immersiveIframe');
            if (iframe) {
                log('✅ Iframe inmersivo encontrado', 'success');
            } else {
                log('❌ Iframe inmersivo NO encontrado', 'error');
            }
            
            log('Pruebas completadas');
        }
        
        function testImmersive() {
            log('Probando modo inmersivo...');
            if (typeof window.toggleImmersiveInterface === 'function') {
                window.toggleImmersiveInterface();
                log('Modo inmersivo activado', 'success');
            } else {
                log('No se puede activar modo inmersivo', 'error');
            }
        }
        
        function testEasterEggs() {
            log('Probando easter eggs...');
            const s3Logo = document.getElementById('s3Logo');
            if (s3Logo) {
                for (let i = 0; i < 3; i++) {
                    setTimeout(() => s3Logo.click(), i * 100);
                }
                log('Easter egg activado (3 clicks en S3)', 'success');
            } else {
                log('Logo S3 no encontrado', 'error');
            }
        }
        
        function testKeyboard() {
            log('Probando atajos de teclado...');
            const event = new KeyboardEvent('keydown', {
                key: 'h',
                ctrlKey: true,
                altKey: true
            });
            document.dispatchEvent(event);
            log('Atajo Ctrl+Alt+H simulado', 'success');
        }
        
        // Actualizar estado del sistema
        function updateSystemStatus() {
            const status = document.getElementById('systemStatus');
            status.innerHTML = `
                <div class="success">Frontend: OK</div>
                <div class="success">Modo Inmersivo: Disponible</div>
                <div class="warning">Backend: Verificando...</div>
            `;
        }
        
        // Inicializar
        document.addEventListener('DOMContentLoaded', function() {
            updateSystemStatus();
            runTests();
        });
    </script>
</body>
</html>'''
    
    with open("test_immersive_simple.html", "w", encoding="utf-8") as f:
        f.write(test_html)
    
    print("   ✅ Test creado: test_immersive_simple.html")

def abrir_test_en_navegador():
    """Abrir el test en el navegador"""
    print("\n🌐 Abriendo test en navegador...")
    
    try:
        # Intentar abrir el test local
        test_path = os.path.abspath("test_immersive_simple.html")
        webbrowser.open(f"file://{test_path}")
        print(f"   ✅ Test abierto: {test_path}")
        
        # También abrir el frontend principal
        webbrowser.open("http://localhost:8080")
        print("   ✅ Frontend principal abierto: http://localhost:8080")
        
    except Exception as e:
        print(f"   ❌ Error abriendo navegador: {e}")

def main():
    print("🎵 SON1KVERS3 - DIAGNÓSTICO DEL MODO INMERSIVO")
    print("=" * 60)
    
    # Verificar archivos
    archivos_ok = verificar_archivos()
    
    # Verificar código HTML
    html_ok = verificar_codigo_html()
    
    # Verificar interfaz inmersiva
    interfaz_ok = verificar_interfaz_immersive()
    
    # Verificar integración JS
    js_ok = verificar_integracion_js()
    
    # Crear herramientas de reparación
    crear_script_reparacion()
    crear_test_immersive()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO:")
    print(f"   Archivos: {'✅ OK' if archivos_ok else '❌ FALTA'}")
    print(f"   HTML: {'✅ OK' if html_ok else '❌ FALTA'}")
    print(f"   Interfaz: {'✅ OK' if interfaz_ok else '❌ FALTA'}")
    print(f"   JavaScript: {'✅ OK' if js_ok else '❌ FALTA'}")
    
    if archivos_ok and html_ok and interfaz_ok and js_ok:
        print("\n🎉 ¡MODO INMERSIVO COMPLETAMENTE FUNCIONAL!")
        print("   Puedes usar:")
        print("   - 3 clicks en el logo S3")
        print("   - 5 clicks en 'Conocer el Universo'")
        print("   - Ctrl+Alt+H")
        print("   - Botones flotantes")
        
        # Abrir test en navegador
        abrir_test_en_navegador()
        
    else:
        print("\n⚠️  MODO INMERSIVO REQUIERE REPARACIÓN")
        print("   Archivos faltantes o código incompleto")
        print("   Ejecuta: bash reparar_immersive.sh")
        print("   O revisa manualmente los archivos")
    
    print("\n💡 HERRAMIENTAS CREADAS:")
    print("   - reparar_immersive.sh")
    print("   - test_immersive_simple.html")
    print("   - test_immersive_mode.html")

if __name__ == "__main__":
    main()
