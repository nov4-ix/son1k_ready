#!/usr/bin/env python3
"""
Sistema de Gestión de Usuarios Son1kVers3
- Administradores: Acceso ilimitado
- Pro Testers: Cuentas premium con límites altos
- Enterprise Testers: Cuentas enterprise con límites máximos
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import bcrypt

class UserRole(Enum):
    ADMIN = "admin"
    PRO_TESTER = "pro_tester"
    ENTERPRISE_TESTER = "enterprise_tester"
    FREE_USER = "free_user"

class UserManager:
    def __init__(self, db_path: str = "son1k_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos de usuarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                generation_limit INTEGER DEFAULT 0,
                generations_used INTEGER DEFAULT 0,
                reset_date TIMESTAMP,
                api_key TEXT UNIQUE,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash de contraseña con bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar contraseña"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def generate_api_key(self) -> str:
        """Generar API key único"""
        return secrets.token_urlsafe(32)
    
    def create_user(self, email: str, password: str, role: UserRole, 
                   generation_limit: int = 0, metadata: Dict = None) -> Dict[str, Any]:
        """Crear nuevo usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {"success": False, "error": "Usuario ya existe"}
            
            # Crear usuario
            password_hash = self.hash_password(password)
            api_key = self.generate_api_key()
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, role, generation_limit, api_key, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, role.value, generation_limit, api_key, 
                  json.dumps(metadata or {})))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "role": role.value,
                "api_key": api_key,
                "generation_limit": generation_limit
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, email, password_hash, role, is_active, generation_limit, 
                       generations_used, api_key, metadata
                FROM users WHERE email = ? AND is_active = 1
            ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            user_id, email, password_hash, role, is_active, gen_limit, gen_used, api_key, metadata = user
            
            if not self.verify_password(password, password_hash):
                return None
            
            # Actualizar último login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            conn.commit()
            
            return {
                "user_id": user_id,
                "email": email,
                "role": role,
                "is_active": bool(is_active),
                "generation_limit": gen_limit,
                "generations_used": gen_used,
                "api_key": api_key,
                "metadata": json.loads(metadata or "{}")
            }
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por API key"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, email, role, is_active, generation_limit, 
                       generations_used, metadata
                FROM users WHERE api_key = ? AND is_active = 1
            ''', (api_key,))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            user_id, email, role, is_active, gen_limit, gen_used, metadata = user
            
            return {
                "user_id": user_id,
                "email": email,
                "role": role,
                "is_active": bool(is_active),
                "generation_limit": gen_limit,
                "generations_used": gen_used,
                "metadata": json.loads(metadata or "{}")
            }
            
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
        finally:
            conn.close()
    
    def check_generation_limit(self, user_id: int) -> Dict[str, Any]:
        """Verificar límite de generaciones del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT generation_limit, generations_used, role
                FROM users WHERE id = ? AND is_active = 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return {"can_generate": False, "error": "Usuario no encontrado"}
            
            gen_limit, gen_used, role = result
            
            # Administradores tienen acceso ilimitado
            if role == UserRole.ADMIN.value:
                return {"can_generate": True, "unlimited": True}
            
            # Verificar límite
            if gen_limit == 0:  # Sin límite
                return {"can_generate": True, "unlimited": True}
            
            if gen_used >= gen_limit:
                return {"can_generate": False, "error": "Límite de generaciones alcanzado"}
            
            return {
                "can_generate": True,
                "unlimited": False,
                "remaining": gen_limit - gen_used,
                "used": gen_used,
                "limit": gen_limit
            }
            
        except Exception as e:
            return {"can_generate": False, "error": str(e)}
        finally:
            conn.close()
    
    def increment_generation_count(self, user_id: int) -> bool:
        """Incrementar contador de generaciones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users 
                SET generations_used = generations_used + 1
                WHERE id = ? AND is_active = 1
            ''', (user_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error incrementando generaciones: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Obtener estadísticas del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT email, role, generation_limit, generations_used, 
                       created_at, last_login, is_active
                FROM users WHERE id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return {"error": "Usuario no encontrado"}
            
            email, role, gen_limit, gen_used, created_at, last_login, is_active = result
            
            return {
                "email": email,
                "role": role,
                "generation_limit": gen_limit,
                "generations_used": gen_used,
                "remaining": gen_limit - gen_used if gen_limit > 0 else "Ilimitado",
                "created_at": created_at,
                "last_login": last_login,
                "is_active": bool(is_active)
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Obtener todos los usuarios (solo para administradores)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, email, role, generation_limit, generations_used, 
                       created_at, last_login, is_active
                FROM users ORDER BY created_at DESC
            ''')
            
            users = []
            for row in cursor.fetchall():
                user_id, email, role, gen_limit, gen_used, created_at, last_login, is_active = row
                users.append({
                    "user_id": user_id,
                    "email": email,
                    "role": role,
                    "generation_limit": gen_limit,
                    "generations_used": gen_used,
                    "remaining": gen_limit - gen_used if gen_limit > 0 else "Ilimitado",
                    "created_at": created_at,
                    "last_login": last_login,
                    "is_active": bool(is_active)
                })
            
            return users
            
        except Exception as e:
            return [{"error": str(e)}]
        finally:
            conn.close()

def create_initial_users():
    """Crear usuarios iniciales del sistema"""
    user_manager = UserManager()
    
    print("🎵 Creando usuarios iniciales de Son1kVers3...")
    
    # 1. Administrador
    print("\n👑 Creando administrador...")
    admin_result = user_manager.create_user(
        email="nov4-ix@son1kvers3.com",
        password="iloveMusic!90",
        role=UserRole.ADMIN,
        generation_limit=0,  # Ilimitado
        metadata={"full_access": True, "created_by": "system"}
    )
    print(f"Admin: {admin_result}")
    
    # 2. Pro Testers (10 cuentas)
    print("\n⭐ Creando Pro Testers...")
    pro_testers = []
    for i in range(1, 11):
        email = f"pro.tester{i}@son1kvers3.com"
        result = user_manager.create_user(
            email=email,
            password="Premium123!",
            role=UserRole.PRO_TESTER,
            generation_limit=100,  # 100 generaciones por mes
            metadata={"tier": "pro", "monthly_limit": 100, "created_by": "system"}
        )
        pro_testers.append(result)
        print(f"Pro Tester {i}: {result['success']}")
    
    # 3. Enterprise Testers (5 cuentas)
    print("\n🏢 Creando Enterprise Testers...")
    enterprise_testers = []
    for i in range(1, 6):
        email = f"enterprise.tester{i}@son1kvers3.com"
        result = user_manager.create_user(
            email=email,
            password="Premium123!",
            role=UserRole.ENTERPRISE_TESTER,
            generation_limit=500,  # 500 generaciones por mes
            metadata={"tier": "enterprise", "monthly_limit": 500, "created_by": "system"}
        )
        enterprise_testers.append(result)
        print(f"Enterprise Tester {i}: {result['success']}")
    
    # Resumen
    print("\n📊 RESUMEN DE USUARIOS CREADOS:")
    print(f"✅ Administradores: 1")
    print(f"✅ Pro Testers: {len([r for r in pro_testers if r['success']])}")
    print(f"✅ Enterprise Testers: {len([r for r in enterprise_testers if r['success']])}")
    
    return {
        "admin": admin_result,
        "pro_testers": pro_testers,
        "enterprise_testers": enterprise_testers
    }

if __name__ == "__main__":
    # Crear usuarios iniciales
    create_initial_users()
    
    # Mostrar todos los usuarios
    print("\n📋 LISTA COMPLETA DE USUARIOS:")
    user_manager = UserManager()
    users = user_manager.get_all_users()
    
    for user in users:
        if "error" not in user:
            print(f"📧 {user['email']} | {user['role']} | Límite: {user['remaining']} | Activo: {user['is_active']}")
