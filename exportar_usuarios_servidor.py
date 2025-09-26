
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
