#!/usr/bin/env python3
"""
🔐 ACTUALIZAR CREDENCIALES DE SUNO
Script simple para actualizar el password de Suno
"""

import json
import sys

def update_password():
    """Actualizar password de Suno"""
    print("🔐 ACTUALIZAR PASSWORD DE SUNO")
    print("=" * 40)
    print()
    
    # Cargar credenciales existentes
    try:
        with open('suno_credentials.json', 'r') as f:
            credentials = json.load(f)
    except:
        print("❌ Error cargando credenciales existentes")
        return False
    
    print(f"📧 Email actual: {credentials.get('email', 'No configurado')}")
    print()
    
    # Solicitar nuevo password
    new_password = input("🔒 Ingresa tu password de Suno: ").strip()
    
    if not new_password:
        print("❌ Password no puede estar vacío")
        return False
    
    # Actualizar password
    credentials['password'] = new_password
    
    # Guardar credenciales
    try:
        with open('suno_credentials.json', 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print()
        print("✅ Password actualizado correctamente")
        print("🎵 Ahora la música aparecerá en tu biblioteca de Suno.com")
        print()
        print("🔄 Reiniciando servidor...")
        return True
        
    except Exception as e:
        print(f"❌ Error guardando credenciales: {e}")
        return False

if __name__ == "__main__":
    if update_password():
        print("✅ Configuración completada")
    else:
        print("❌ Error en la configuración")
        sys.exit(1)




