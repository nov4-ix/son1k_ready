#!/usr/bin/env python3
"""
🔐 CONFIGURAR CREDENCIALES DE SUNO
Script para configurar tus credenciales reales de Suno.com
"""

import json
import getpass
import os

def configure_suno_credentials():
    """Configurar credenciales de Suno"""
    print("🎵 CONFIGURACIÓN DE CREDENCIALES DE SUNO")
    print("=" * 50)
    print()
    print("Para que la música aparezca en tu biblioteca de Suno.com,")
    print("necesitamos configurar tus credenciales reales.")
    print()
    
    # Cargar credenciales existentes
    credentials = {}
    if os.path.exists('suno_credentials.json'):
        try:
            with open('suno_credentials.json', 'r') as f:
                credentials = json.load(f)
            print(f"📧 Email actual: {credentials.get('email', 'No configurado')}")
        except:
            pass
    
    # Solicitar email
    email = input("📧 Ingresa tu email de Suno: ").strip()
    if not email:
        print("❌ Email requerido")
        return False
    
    # Solicitar password
    password = getpass.getpass("🔒 Ingresa tu password de Suno: ").strip()
    if not password:
        print("❌ Password requerido")
        return False
    
    # Actualizar credenciales
    credentials.update({
        "email": email,
        "password": password,
        "cookie": "[]",
        "session_token": "",
        "user_id": "",
        "last_login": None
    })
    
    # Guardar credenciales
    try:
        with open('suno_credentials.json', 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print()
        print("✅ Credenciales guardadas correctamente")
        print("🎵 Ahora la música aparecerá en tu biblioteca de Suno.com")
        print()
        print("📋 Próximos pasos:")
        print("1. Reinicia el servidor: pkill -f son1k_simple_stable.py")
        print("2. Inicia el servidor: python3 son1k_simple_stable.py")
        print("3. Genera música y aparecerá en tu biblioteca de Suno")
        
        return True
        
    except Exception as e:
        print(f"❌ Error guardando credenciales: {e}")
        return False

if __name__ == "__main__":
    configure_suno_credentials()

