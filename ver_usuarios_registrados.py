#!/usr/bin/env python3
"""
Script para ver usuarios registrados en son1kvers3.com
"""

import requests
import json
import sys
from datetime import datetime

# Configuración
API_BASE_URL = "https://www.son1kvers3.com"
ADMIN_EMAIL = "nov4-ix@son1kvers3.com"

def verificar_conexion():
    """Verificar que la API esté funcionando"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Conexión exitosa con son1kvers3.com")
            return True
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def obtener_estadisticas():
    """Obtener estadísticas del sistema"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("\n📊 ESTADÍSTICAS DEL SISTEMA:")
            print(f"   API: {data.get('api', 'N/A')}")
            print(f"   Health: {data.get('health', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"   Auto Renewal: {data.get('auto_renewal', 'N/A')}")
            print(f"   System: {data.get('system', 'N/A')}")
            return True
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return False

def inicializar_base_datos():
    """Inicializar la base de datos para obtener información de usuarios"""
    try:
        print("\n🔧 Inicializando base de datos...")
        response = requests.post(f"{API_BASE_URL}/api/admin/init-database", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✅ Base de datos inicializada")
            print(f"   Admin creado: {data.get('admin_created', 'N/A')}")
            print(f"   Testers creados: {data.get('testers_created', 'N/A')}")
            return True
        else:
            print(f"❌ Error inicializando base de datos: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

def probar_endpoints_usuarios():
    """Probar diferentes endpoints para obtener información de usuarios"""
    endpoints = [
        "/api/users",
        "/api/auth/users", 
        "/api/admin/users",
        "/api/system/users",
        "/users",
        "/admin/users",
        "/api/user/list",
        "/api/accounts",
        "/api/registrations"
    ]
    
    print("\n🔍 Probando endpoints de usuarios...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      ✅ Datos: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"      ✅ Texto: {response.text[:100]}...")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

def obtener_info_sistema():
    """Obtener información del sistema"""
    try:
        print("\n🔍 Obteniendo información del sistema...")
        response = requests.get(f"{API_BASE_URL}/api/system/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Información del sistema obtenida:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error obteniendo info del sistema: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo info del sistema: {e}")

def obtener_credenciales_status():
    """Obtener estado de credenciales"""
    try:
        print("\n🔑 Obteniendo estado de credenciales...")
        response = requests.get(f"{API_BASE_URL}/api/system/credentials/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Estado de credenciales:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error obteniendo credenciales: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo credenciales: {e}")

def main():
    print("🎵 SON1KVERS3 - VERIFICADOR DE USUARIOS REGISTRADOS")
    print("=" * 60)
    print(f"🌐 URL: {API_BASE_URL}")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar conexión
    if not verificar_conexion():
        sys.exit(1)
    
    # Obtener estadísticas
    obtener_estadisticas()
    
    # Inicializar base de datos
    inicializar_base_datos()
    
    # Probar endpoints de usuarios
    probar_endpoints_usuarios()
    
    # Obtener información del sistema
    obtener_info_sistema()
    
    # Obtener estado de credenciales
    obtener_credenciales_status()
    
    print("\n" + "=" * 60)
    print("✅ Verificación completada")
    print("\n💡 NOTA: Si no se encontraron endpoints de usuarios específicos,")
    print("   es posible que el sistema use autenticación basada en tokens")
    print("   o que los usuarios se almacenen en una base de datos local.")
    print("\n🔧 Para acceder a los datos de usuarios, necesitarías:")
    print("   1. Credenciales de administrador")
    print("   2. Acceso directo a la base de datos")
    print("   3. Un endpoint de administración específico")

if __name__ == "__main__":
    main()

