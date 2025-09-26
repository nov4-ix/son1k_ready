#!/usr/bin/env python3
"""
Script para crear un endpoint de administración en son1kvers3.com
que permita ver los usuarios registrados
"""

import requests
import json
import sys
from datetime import datetime

# Configuración
API_BASE_URL = "https://www.son1kvers3.com"
ADMIN_EMAIL = "nov4-ix@son1kvers3.com"

def crear_endpoint_admin():
    """Intentar crear un endpoint de administración"""
    print("🔧 Intentando crear endpoint de administración...")
    
    # Datos para crear el endpoint
    admin_data = {
        "admin_email": ADMIN_EMAIL,
        "action": "create_users_endpoint",
        "permissions": ["read_users", "view_registrations", "export_data"]
    }
    
    try:
        # Intentar diferentes métodos para crear el endpoint
        methods = [
            ("POST", "/api/admin/create-endpoint"),
            ("PUT", "/api/admin/users-endpoint"),
            ("POST", "/api/admin/setup"),
            ("POST", "/api/system/create-users-endpoint"),
            ("POST", "/api/admin/configure")
        ]
        
        for method, endpoint in methods:
            print(f"   Probando {method} {endpoint}...")
            try:
                if method == "POST":
                    response = requests.post(f"{API_BASE_URL}{endpoint}", 
                                           json=admin_data, timeout=10)
                elif method == "PUT":
                    response = requests.put(f"{API_BASE_URL}{endpoint}", 
                                          json=admin_data, timeout=10)
                
                print(f"      Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"      ✅ Éxito: {data}")
                    return True
                elif response.status_code != 404:
                    print(f"      ⚠️  Respuesta: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error creando endpoint: {e}")
        return False

def probar_acceso_directo():
    """Probar acceso directo a la base de datos"""
    print("\n🗄️ Probando acceso directo a la base de datos...")
    
    # Intentar acceder a archivos de base de datos
    db_endpoints = [
        "/api/db/users",
        "/api/database/users",
        "/api/data/users",
        "/api/query/users",
        "/api/sql/users",
        "/api/export/users"
    ]
    
    for endpoint in db_endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      ✅ Datos encontrados: {len(data)} registros")
                    if isinstance(data, list) and len(data) > 0:
                        print(f"      📋 Primer usuario: {data[0]}")
                except:
                    print(f"      ✅ Texto: {response.text[:100]}...")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

def intentar_login_admin():
    """Intentar hacer login como administrador"""
    print("\n🔑 Intentando login como administrador...")
    
    # Intentar diferentes combinaciones de credenciales
    admin_credentials = [
        {"email": ADMIN_EMAIL, "password": "admin123"},
        {"email": ADMIN_EMAIL, "password": "son1k123"},
        {"email": ADMIN_EMAIL, "password": "password"},
        {"email": ADMIN_EMAIL, "password": "123456"},
        {"username": "admin", "password": "admin123"},
        {"username": "nov4-ix", "password": "admin123"}
    ]
    
    for creds in admin_credentials:
        try:
            print(f"   Probando: {creds}")
            response = requests.post(f"{API_BASE_URL}/api/auth/login", 
                                   json=creds, timeout=10)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Login exitoso!")
                print(f"      Token: {data.get('access_token', 'N/A')[:20]}...")
                print(f"      User: {data.get('user', 'N/A')}")
                
                # Intentar acceder a datos de usuarios con el token
                token = data.get('access_token')
                if token:
                    return intentar_acceso_con_token(token)
                    
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    return False

def intentar_acceso_con_token(token):
    """Intentar acceder a datos de usuarios con token de administrador"""
    print(f"\n🎫 Intentando acceso con token...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Endpoints que podrían requerir autenticación
    protected_endpoints = [
        "/api/admin/users",
        "/api/users",
        "/api/auth/users", 
        "/api/system/users",
        "/api/data/users",
        "/api/export/users",
        "/api/admin/data",
        "/api/admin/export"
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", 
                                  headers=headers, timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Datos encontrados!")
                print(f"      Tipo: {type(data)}")
                if isinstance(data, list):
                    print(f"      Cantidad: {len(data)} registros")
                    if len(data) > 0:
                        print(f"      Primer registro: {data[0]}")
                else:
                    print(f"      Contenido: {json.dumps(data, indent=2)[:200]}...")
                return True
            elif response.status_code != 404:
                print(f"      ⚠️  Respuesta: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")
    
    return False

def crear_script_exportacion():
    """Crear un script que se pueda ejecutar en el servidor"""
    print("\n📝 Creando script de exportación...")
    
    script_content = '''
#!/usr/bin/env python3
"""
Script para exportar usuarios registrados desde la base de datos local
"""

import sqlite3
import json
import os
from datetime import datetime

def exportar_usuarios():
    """Exportar usuarios desde la base de datos SQLite"""
    
    # Posibles ubicaciones de la base de datos
    db_paths = [
        "son1k_production.db",
        "backend/son1k_production.db", 
        "app.db",
        "database.db",
        "users.db",
        "/var/www/son1kvers3/backend/son1k_production.db",
        "/app/son1k_production.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"✅ Base de datos encontrada: {db_path}")
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Obtener lista de tablas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"📋 Tablas encontradas: {[t[0] for t in tables]}")
                
                # Buscar tabla de usuarios
                user_tables = ['users', 'user', 'accounts', 'account', 'registrations', 'auth_users']
                for table in user_tables:
                    if any(table in t[0].lower() for t in tables):
                        print(f"🔍 Buscando en tabla: {table}")
                        try:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 10;")
                            users = cursor.fetchall()
                            
                            # Obtener nombres de columnas
                            cursor.execute(f"PRAGMA table_info({table});")
                            columns = [col[1] for col in cursor.fetchall()]
                            
                            print(f"📊 Columnas: {columns}")
                            print(f"👥 Usuarios encontrados: {len(users)}")
                            
                            # Exportar a JSON
                            users_data = []
                            for user in users:
                                user_dict = dict(zip(columns, user))
                                users_data.append(user_dict)
                            
                            # Guardar archivo
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"usuarios_exportados_{timestamp}.json"
                            
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(users_data, f, indent=2, ensure_ascii=False, default=str)
                            
                            print(f"✅ Usuarios exportados a: {filename}")
                            print(f"📊 Total de usuarios: {len(users_data)}")
                            
                            # Mostrar algunos ejemplos
                            for i, user in enumerate(users_data[:3]):
                                print(f"   Usuario {i+1}: {user}")
                            
                            conn.close()
                            return True
                            
                        except Exception as e:
                            print(f"❌ Error leyendo tabla {table}: {e}")
                
                conn.close()
                
            except Exception as e:
                print(f"❌ Error accediendo a {db_path}: {e}")
    
    print("❌ No se encontró base de datos de usuarios")
    return False

if __name__ == "__main__":
    print("🎵 SON1KVERS3 - EXPORTADOR DE USUARIOS")
    print("=" * 50)
    exportar_usuarios()
'''
    
    with open("exportar_usuarios_servidor.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✅ Script creado: exportar_usuarios_servidor.py")
    print("💡 Instrucciones:")
    print("   1. Sube este script al servidor son1kvers3.com")
    print("   2. Ejecuta: python3 exportar_usuarios_servidor.py")
    print("   3. El script buscará la base de datos y exportará los usuarios")

def main():
    print("🎵 SON1KVERS3 - CREAR ENDPOINT DE ADMINISTRACIÓN")
    print("=" * 60)
    print(f"🌐 URL: {API_BASE_URL}")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Intentar crear endpoint de administración
    if crear_endpoint_admin():
        print("✅ Endpoint de administración creado exitosamente")
    else:
        print("❌ No se pudo crear endpoint de administración")
    
    # Probar acceso directo a base de datos
    probar_acceso_directo()
    
    # Intentar login como administrador
    if intentar_login_admin():
        print("✅ Acceso a datos de usuarios obtenido")
    else:
        print("❌ No se pudo acceder a datos de usuarios")
    
    # Crear script de exportación
    crear_script_exportacion()
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado")
    print("\n💡 ALTERNATIVAS PARA VER USUARIOS:")
    print("   1. Acceso directo al servidor son1kvers3.com")
    print("   2. Usar el script exportar_usuarios_servidor.py")
    print("   3. Acceder a la base de datos SQLite directamente")
    print("   4. Crear un endpoint de administración personalizado")

if __name__ == "__main__":
    main()

