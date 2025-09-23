#!/usr/bin/env python3
"""
Script de inicialización automática de usuarios para Railway
Se ejecuta al iniciar la aplicación para crear usuarios por defecto
"""

import sqlite3
import bcrypt
import uuid
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def init_users_database():
    """Inicializa la base de datos con usuarios por defecto"""
    
    # Determinar archivo de base de datos - Railway auto-detección
    db_file = "son1k.db"
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):
        # En Railway o producción, crear siempre nueva DB
        db_file = "son1k.db"
        logger.info("🚀 Modo Railway/Producción detectado")
    
    logger.info(f"🔧 Inicializando base de datos: {db_file}")
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Crear tabla de usuarios si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                plan TEXT NOT NULL DEFAULT 'free',
                credits INTEGER DEFAULT 0,
                subscription_status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                subscription_end TIMESTAMP
            )
        """)
        
        # Verificar si ya existen usuarios
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            logger.info(f"✅ Base de datos ya inicializada con {user_count} usuarios")
            conn.close()
            return
        
        # En Railway/Producción, forzar recreación completa
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):
            logger.info("🔄 Forzando recreación de usuarios en Railway")
            cursor.execute("DELETE FROM users")  # Limpiar usuarios existentes
        
        logger.info("🎵 Creando usuarios por defecto...")
        
        # Crear administrador
        admin_id = str(uuid.uuid4())
        admin_password = bcrypt.hashpw("iloveMusic!90".encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("""
            INSERT INTO users (id, email, password_hash, plan, credits, subscription_status, subscription_end)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (admin_id, "nov4-ix@son1kvers3.com", admin_password, "unlimited", -1, "active", 
              datetime.now() + timedelta(days=365*10)))
        
        logger.info("✅ Administrador creado: nov4-ix@son1kvers3.com")
        
        # Crear 10 cuentas pro testers
        for i in range(1, 11):
            tester_id = str(uuid.uuid4())
            tester_email = f"pro.tester{i}@son1kvers3.com"
            tester_password = bcrypt.hashpw("Premium123!".encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, plan, credits, subscription_status, subscription_end)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tester_id, tester_email, tester_password, "pro", 200, "active", 
                  datetime.now() + timedelta(days=365)))
            
            logger.info(f"✅ Tester creado: {tester_email}")
        
        conn.commit()
        conn.close()
        
        logger.info("🚀 Base de datos inicializada exitosamente")
        logger.info("📊 Usuarios creados: 1 admin + 10 pro testers")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_users_database()