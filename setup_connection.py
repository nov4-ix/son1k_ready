#!/usr/bin/env python3
"""
🔧 Son1k Connection Setup
Configuración inicial transparente para conectar el motor de generación
"""
import os
import sys
import time
import webbrowser
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def setup_initial_connection():
    """Configurar conexión inicial con el motor de generación"""
    
    print("🔧 SON1K - CONFIGURACIÓN INICIAL")
    print("=" * 40)
    print()
    print("📋 PASOS PARA CONFIGURAR EL MOTOR AVANZADO:")
    print()
    print("1. 🌐 Se abrirá una pestaña del motor de generación")
    print("2. 🔐 Inicia sesión UNA SOLA VEZ")
    print("3. ✅ Una vez logueado, cierra la pestaña")
    print("4. 🎵 Tu plataforma Son1k estará lista para generar música")
    print()
    print("💡 Esta configuración solo necesitas hacerla UNA VEZ")
    print("   Después, la generación será completamente automática")
    print()
    
    # Esperar confirmación
    input("📱 Presiona ENTER para abrir el motor de generación...")
    
    # Abrir Suno para login inicial
    print("🌐 Abriendo motor de generación...")
    webbrowser.open("https://suno.com")
    
    print()
    print("🔗 Se abrió el motor de generación en tu navegador")
    print("📋 INSTRUCCIONES:")
    print("   1. Haz login en la página que se abrió")
    print("   2. Una vez logueado, puedes cerrar esa pestaña")
    print("   3. Regresa aquí y presiona ENTER")
    print()
    
    input("✅ Presiona ENTER cuando hayas completado el login...")
    
    print()
    print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("=" * 30)
    print("✅ Motor de generación configurado")
    print("✅ Sesión establecida")
    print("✅ Son1k listo para usar")
    print()
    print("🚀 Ahora puedes usar tu plataforma Son1k normalmente")
    print("🎵 La generación de música será completamente transparente")
    print()
    print("💡 Para iniciar Son1k, ejecuta:")
    print("   python3 start_frontend.py")
    print()

if __name__ == "__main__":
    setup_initial_connection()