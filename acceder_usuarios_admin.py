#!/usr/bin/env python3
"""
Script para acceder a usuarios registrados usando credenciales de administrador
"""

import requests
import json
import sys
from datetime import datetime

# Configuración
API_BASE_URL = "https://www.son1kvers3.com"
ADMIN_EMAIL = "nov4-ix@son1kvers3.com"
ADMIN_PASSWORD = "admin123"

def hacer_login_admin():
    """Hacer login como administrador y obtener token"""
    print("🔑 Iniciando sesión como administrador...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/login", 
                               json={
                                   "email": ADMIN_EMAIL,
                                   "password": ADMIN_PASSWORD
                               }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login exitoso como administrador")
            print(f"   Email: {data.get('user', {}).get('email', 'N/A')}")
            print(f"   Role: {data.get('user', {}).get('role', 'N/A')}")
            print(f"   Level: {data.get('user', {}).get('level', 'N/A')}")
            
            # Obtener token si está disponible
            token = data.get('access_token')
            if token:
                print(f"   Token: {token[:20]}...")
                return token
            else:
                print("   ⚠️  No se obtuvo token de acceso")
                return "admin_session"
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def buscar_usuarios_con_token(token):
    """Buscar usuarios usando el token de administrador"""
    print(f"\n🔍 Buscando usuarios con token de administrador...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Lista de endpoints que podrían contener usuarios
    endpoints = [
        "/api/admin/users",
        "/api/users",
        "/api/auth/users",
        "/api/system/users", 
        "/api/data/users",
        "/api/export/users",
        "/api/admin/data",
        "/api/admin/export",
        "/api/admin/list",
        "/api/admin/accounts",
        "/api/admin/registrations",
        "/api/system/accounts",
        "/api/system/registrations",
        "/api/accounts",
        "/api/registrations",
        "/api/user/list",
        "/api/user/accounts",
        "/api/database/users",
        "/api/db/users"
    ]
    
    usuarios_encontrados = []
    
    for endpoint in endpoints:
        try:
            print(f"   Probando: {endpoint}")
            response = requests.get(f"{API_BASE_URL}{endpoint}", 
                                  headers=headers, timeout=10)
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      ✅ Datos encontrados!")
                    
                    if isinstance(data, list):
                        print(f"      📊 Cantidad: {len(data)} registros")
                        usuarios_encontrados.extend(data)
                        
                        # Mostrar algunos ejemplos
                        for i, user in enumerate(data[:3]):
                            print(f"         Usuario {i+1}: {user}")
                    else:
                        print(f"      📋 Contenido: {json.dumps(data, indent=2)[:200]}...")
                        if 'users' in data:
                            usuarios_encontrados.extend(data['users'])
                        elif 'data' in data:
                            usuarios_encontrados.extend(data['data'])
                            
                except json.JSONDecodeError:
                    print(f"      📄 Texto: {response.text[:100]}...")
                    
            elif response.status_code == 401:
                print(f"      🔒 No autorizado")
            elif response.status_code == 403:
                print(f"      🚫 Prohibido")
            elif response.status_code != 404:
                print(f"      ⚠️  Respuesta: {response.text[:100]}...")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    return usuarios_encontrados

def buscar_usuarios_sin_token():
    """Buscar usuarios sin token (endpoints públicos)"""
    print(f"\n🔍 Buscando usuarios en endpoints públicos...")
    
    # Endpoints que podrían ser públicos
    public_endpoints = [
        "/api/public/users",
        "/api/guest/users", 
        "/api/demo/users",
        "/api/test/users",
        "/api/stats/users",
        "/api/metrics/users",
        "/api/analytics/users",
        "/api/reports/users",
        "/api/export/public/users",
        "/api/data/public/users"
    ]
    
    usuarios_encontrados = []
    
    for endpoint in public_endpoints:
        try:
            print(f"   Probando: {endpoint}")
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      ✅ Datos encontrados!")
                    
                    if isinstance(data, list):
                        print(f"      📊 Cantidad: {len(data)} registros")
                        usuarios_encontrados.extend(data)
                    else:
                        print(f"      📋 Contenido: {json.dumps(data, indent=2)[:200]}...")
                        
                except json.JSONDecodeError:
                    print(f"      📄 Texto: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    return usuarios_encontrados

def exportar_usuarios(usuarios):
    """Exportar usuarios encontrados a archivo"""
    if not usuarios:
        print("\n❌ No se encontraron usuarios para exportar")
        return
    
    print(f"\n📊 EXPORTANDO USUARIOS ENCONTRADOS")
    print(f"   Total de usuarios: {len(usuarios)}")
    
    # Crear archivo de exportación
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"usuarios_son1kvers3_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Usuarios exportados a: {filename}")
        
        # Mostrar resumen
        print(f"\n📋 RESUMEN DE USUARIOS:")
        for i, user in enumerate(usuarios[:10]):  # Mostrar primeros 10
            print(f"   {i+1}. {user}")
        
        if len(usuarios) > 10:
            print(f"   ... y {len(usuarios) - 10} más")
            
    except Exception as e:
        print(f"❌ Error exportando usuarios: {e}")

def main():
    print("🎵 SON1KVERS3 - ACCESO A USUARIOS REGISTRADOS")
    print("=" * 60)
    print(f"🌐 URL: {API_BASE_URL}")
    print(f"👤 Admin: {ADMIN_EMAIL}")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Hacer login como administrador
    token = hacer_login_admin()
    
    usuarios_encontrados = []
    
    if token:
        # Buscar usuarios con token de administrador
        usuarios_con_token = buscar_usuarios_con_token(token)
        usuarios_encontrados.extend(usuarios_con_token)
    
    # Buscar usuarios en endpoints públicos
    usuarios_publicos = buscar_usuarios_sin_token()
    usuarios_encontrados.extend(usuarios_publicos)
    
    # Eliminar duplicados
    usuarios_unicos = []
    emails_vistos = set()
    
    for user in usuarios_encontrados:
        if isinstance(user, dict):
            email = user.get('email', user.get('username', str(user)))
        else:
            email = str(user)
            
        if email not in emails_vistos:
            usuarios_unicos.append(user)
            emails_vistos.add(email)
    
    # Exportar usuarios
    exportar_usuarios(usuarios_unicos)
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado")
    
    if usuarios_unicos:
        print(f"🎉 Se encontraron {len(usuarios_unicos)} usuarios únicos")
    else:
        print("❌ No se encontraron usuarios registrados")
        print("\n💡 POSIBLES RAZONES:")
        print("   1. Los usuarios se almacenan en una base de datos local")
        print("   2. No hay endpoint público para listar usuarios")
        print("   3. Se requiere acceso directo al servidor")
        print("   4. Los usuarios se crean dinámicamente (demo)")

if __name__ == "__main__":
    main()

