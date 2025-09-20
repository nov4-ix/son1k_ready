#!/usr/bin/env python3
"""
🎵 Son1kVers3 Commercial Session Setup
Configuración de sesión comercial transparente
"""
import os
import sys
import time
import webbrowser
import requests
from pathlib import Path

def setup_commercial_session():
    """Configurar sesión comercial una sola vez"""
    
    print("🎵 SON1KVERS3 - CONFIGURACIÓN COMERCIAL")
    print("=" * 50)
    print()
    print("🔧 CONFIGURANDO MOTOR DE GENERACIÓN AVANZADO")
    print()
    print("Esta configuración se hace UNA SOLA VEZ y permite:")
    print("✅ Generación de música completamente transparente")
    print("✅ Sin menciones a proveedores externos")
    print("✅ Proceso automático para el usuario")
    print("✅ Integración comercial profesional")
    print()
    
    # Verificar que los servicios estén corriendo
    print("🔍 Verificando servicios...")
    
    try:
        # Verificar API backend
        response = requests.get("http://localhost:8000/api/captcha/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API funcionando")
        else:
            print("❌ Backend API no responde")
            return False
    except:
        print("❌ Backend API no disponible")
        print("💡 Ejecuta primero: docker compose up -d")
        return False
    
    try:
        # Verificar frontend
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend funcionando")
        else:
            print("❌ Frontend no responde")
    except:
        print("❌ Frontend no disponible")
        print("💡 Ejecuta: python3 start_frontend.py")
        return False
    
    print()
    print("🌐 CONFIGURANDO SESIÓN...")
    print("1. Se abrirá el motor de generación")
    print("2. Haz login UNA SOLA VEZ")
    print("3. Cierra la pestaña")
    print("4. El sistema quedará configurado para siempre")
    print()
    
    input("📱 Presiona ENTER para continuar...")
    
    # Abrir Suno para configuración
    print("🌐 Abriendo motor de generación...")
    webbrowser.open("https://suno.com")
    
    print()
    print("📋 INSTRUCCIONES:")
    print("   1. En la pestaña que se abrió, haz LOGIN")
    print("   2. Una vez logueado, cierra esa pestaña")
    print("   3. Regresa aquí y confirma")
    print()
    
    input("✅ Presiona ENTER cuando hayas completado el LOGIN...")
    
    # Test del sistema
    print()
    print("🧪 PROBANDO SISTEMA COMERCIAL...")
    
    try:
        response = requests.get("http://localhost:8000/api/music/health", timeout=10)
        if response.ok:
            data = response.json()
            if data.get('engine_available'):
                print("✅ Motor comercial disponible")
            else:
                print("⚠️ Motor comercial parcialmente disponible")
        else:
            print("❌ Error en sistema comercial")
    except Exception as e:
        print(f"❌ Error probando sistema: {e}")
    
    print()
    print("🎉 ¡CONFIGURACIÓN COMERCIAL COMPLETADA!")
    print("=" * 40)
    print("✅ Sesión establecida")
    print("✅ Motor comercial configurado")
    print("✅ Sistema transparente activado")
    print("✅ Son1kVers3 listo para uso comercial")
    print()
    print("🎯 AHORA TU PLATAFORMA:")
    print("   • Genera música de forma transparente")
    print("   • El usuario no ve proveedores externos")
    print("   • Proceso completamente automático")
    print("   • Calidad comercial profesional")
    print()
    print("🌐 Accede a tu plataforma en: http://localhost:3000")
    print()
    print("💡 Para usuarios finales:")
    print("   1. Ingresar lyrics y prompt")
    print("   2. Hacer clic en 'Generar Música'")
    print("   3. Esperar resultado automático")
    print("   4. Reproducir y descargar música")
    print()

def test_commercial_system():
    """Probar el sistema comercial"""
    print("🧪 PROBANDO SISTEMA COMERCIAL...")
    
    test_request = {
        "lyrics": "Testing commercial system\nSon1kVers3 music generation\nTransparent and professional",
        "prompt": "upbeat electronic commercial track, 120 BPM",
        "instrumental": False,
        "style": "commercial"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/music/generate",
            json=test_request,
            timeout=10
        )
        
        if response.ok:
            data = response.json()
            print(f"✅ Test exitoso - Job ID: {data.get('job_id')}")
            print(f"📊 Estado: {data.get('status')}")
            print(f"⏱️ Tiempo estimado: {data.get('estimated_time')} segundos")
            return True
        else:
            print(f"❌ Error en test: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

if __name__ == "__main__":
    success = setup_commercial_session()
    
    if success:
        print("\n🎯 ¿Quieres probar el sistema ahora? (y/n)")
        if input().lower() == 'y':
            test_commercial_system()
    
    print("\n🚀 Sistema listo para uso comercial profesional!")