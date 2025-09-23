#!/usr/bin/env python3
"""
Son1kVers3 - Crear Administrador y Cuentas Pro Testers
Crea nov4-ix@son1kvers3.com como admin y 10 cuentas pro.tester
"""
import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
import bcrypt

# Configuración de base de datos
DB_PATH = "son1k.db"

def hash_password(password: str) -> str:
    """Hash password usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_users():
    """Crear administrador y cuentas pro testers"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. ADMINISTRADOR: nov4-ix@son1kvers3.com
    admin_id = str(uuid.uuid4())
    admin_email = "nov4-ix@son1kvers3.com"
    admin_password = hash_password("iloveMusic!90")
    admin_end_date = datetime.now() + timedelta(days=365*10)  # 10 años
    
    cursor.execute("""
        INSERT OR REPLACE INTO users (
            id, email, hashed_password, plan, 
            daily_usage, monthly_usage,
            subscription_status, subscription_end_date,
            is_active, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        admin_id,
        admin_email,
        admin_password,
        "unlimited",  # Plan ilimitado para admin
        0,   # Sin uso diario
        0,   # Sin uso mensual
        "active",
        admin_end_date,
        1,   # Activo
        datetime.now(),
        datetime.now()
    ))
    
    print(f"✅ Administrador creado: {admin_email}")
    print(f"   - Plan: unlimited (acceso completo)")
    print(f"   - Créditos: ilimitados")
    print(f"   - Contraseña: iloveMusic!90")
    
    # 2. PRO TESTERS: pro.tester1@son1kvers3.com hasta pro.tester10@son1kvers3.com
    pro_end_date = datetime.now() + timedelta(days=365)  # 1 año
    
    for i in range(1, 11):
        tester_id = str(uuid.uuid4())
        tester_email = f"pro.tester{i}@son1kvers3.com"
        tester_password = hash_password("Premium123!")
        
        cursor.execute("""
            INSERT OR REPLACE INTO users (
                id, email, hashed_password, plan,
                daily_usage, monthly_usage,
                subscription_status, subscription_end_date,
                is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tester_id,
            tester_email,
            tester_password,
            "pro",  # Plan pro para testers
            0,      # Sin uso diario inicial
            0,      # Sin uso mensual inicial
            "active",
            pro_end_date,
            1,      # Activo
            datetime.now(),
            datetime.now()
        ))
        
        print(f"✅ Tester creado: {tester_email}")
    
    print(f"\n🎯 Resumen:")
    print(f"   - 1 administrador con acceso ilimitado")
    print(f"   - 10 cuentas pro testers activas")
    print(f"   - Contraseña testers: Premium123!")
    print(f"   - Plan pro: 200 créditos/mes, activo por 1 año")
    
    # Verificar creación
    cursor.execute("SELECT COUNT(*) FROM users WHERE plan = 'unlimited'")
    admin_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE plan = 'pro'")
    pro_count = cursor.fetchone()[0]
    
    print(f"\n📊 Verificación:")
    print(f"   - Administradores: {admin_count}")
    print(f"   - Usuarios Pro: {pro_count}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🚀 ¡Usuarios creados exitosamente en {DB_PATH}!")

if __name__ == "__main__":
    print("🎵 Son1kVers3 - Creando usuarios administrador y pro testers...")
    create_users()