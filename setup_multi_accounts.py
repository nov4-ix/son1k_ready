#!/usr/bin/env python3
"""
Script para configurar múltiples cuentas de Suno
"""
import json
import os
import webbrowser
from datetime import datetime

def create_accounts_config():
    """Crear configuración de múltiples cuentas"""
    
    print("🚀 Configurador de Múltiples Cuentas de Suno")
    print("=" * 50)
    print()
    print("Este script te ayudará a configurar múltiples cuentas de Suno")
    print("para máxima evasión y generación de música.")
    print()
    
    accounts = []
    
    print("📝 Instrucciones para obtener cookies de Suno:")
    print("1. Ve a https://suno.com en tu navegador")
    print("2. Inicia sesión con tu cuenta")
    print("3. Abre las herramientas de desarrollador (F12)")
    print("4. Ve a Application/Storage > Cookies")
    print("5. Busca 'session_token' o 'auth_token'")
    print("6. Copia el valor completo de la cookie")
    print()
    
    num_accounts = input("¿Cuántas cuentas de Suno quieres configurar? (recomendado: 3-5): ")
    
    try:
        num_accounts = int(num_accounts)
        if num_accounts < 1 or num_accounts > 10:
            print("❌ Número inválido. Usando 3 cuentas por defecto.")
            num_accounts = 3
    except ValueError:
        print("❌ Número inválido. Usando 3 cuentas por defecto.")
        num_accounts = 3
    
    print(f"\n📋 Configurando {num_accounts} cuentas...")
    print()
    
    for i in range(num_accounts):
        print(f"--- Cuenta {i+1} ---")
        
        email = input(f"Email de la cuenta {i+1}: ").strip()
        if not email:
            print("⚠️ Email vacío, saltando cuenta...")
            continue
        
        print(f"🔑 Para la cuenta {email}:")
        print("   - Abre https://suno.com en una ventana privada")
        print("   - Inicia sesión con esta cuenta")
        print("   - Obtén la cookie como se explicó arriba")
        print()
        
        cookie = input(f"Cookie de Suno para {email}: ").strip()
        if not cookie:
            print("⚠️ Cookie vacía, saltando cuenta...")
            continue
        
        priority = input(f"Prioridad (1=alta, 2=media, 3=baja) [1]: ").strip()
        try:
            priority = int(priority) if priority else 1
            if priority not in [1, 2, 3]:
                priority = 1
        except ValueError:
            priority = 1
        
        max_daily = input(f"Uso diario máximo (recomendado: 30-50) [50]: ").strip()
        try:
            max_daily = int(max_daily) if max_daily else 50
            if max_daily < 1 or max_daily > 100:
                max_daily = 50
        except ValueError:
            max_daily = 50
        
        account = {
            "id": f"account_{i+1}",
            "email": email,
            "cookie": cookie,
            "priority": priority,
            "max_daily_usage": max_daily,
            "created_at": datetime.now().isoformat()
        }
        
        accounts.append(account)
        print(f"✅ Cuenta {i+1} configurada")
        print()
    
    if not accounts:
        print("❌ No se configuró ninguna cuenta válida")
        return False
    
    # Crear configuración
    config = {
        "accounts": accounts,
        "settings": {
            "rotation_interval": 300,
            "load_balancer": "weighted",
            "cooldown_time": 60,
            "max_concurrent": min(len(accounts), 3),
            "created_at": datetime.now().isoformat()
        }
    }
    
    # Guardar configuración
    with open("suno_accounts.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuración guardada en suno_accounts.json")
    print()
    print("📊 Resumen de cuentas configuradas:")
    for i, account in enumerate(accounts, 1):
        print(f"  {i}. {account['email']} (Prioridad: {account['priority']}, Max diario: {account['max_daily_usage']})")
    
    print()
    print("🚀 Para usar las cuentas:")
    print("   1. Ejecuta: python3 test_multi_accounts.py")
    print("   2. O integra en tu sistema principal")
    
    return True

def test_configuration():
    """Probar la configuración creada"""
    try:
        with open("suno_accounts.json", "r") as f:
            config = json.load(f)
        
        print("\n🧪 Probando configuración...")
        print(f"📊 Cuentas configuradas: {len(config['accounts'])}")
        
        for account in config['accounts']:
            print(f"  ✅ {account['email']} - Prioridad {account['priority']}")
        
        print("\n✅ Configuración válida")
        return True
        
    except FileNotFoundError:
        print("❌ Archivo suno_accounts.json no encontrado")
        return False
    except json.JSONDecodeError:
        print("❌ Error en formato JSON")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🎵 Son1k Multi-Account Setup")
    print("=" * 30)
    print()
    
    if os.path.exists("suno_accounts.json"):
        print("📁 Archivo suno_accounts.json ya existe")
        choice = input("¿Quieres reconfigurar? (s/n) [n]: ").strip().lower()
        if choice not in ['s', 'si', 'y', 'yes']:
            if test_configuration():
                print("\n✅ Configuración existente es válida")
                return
            else:
                print("\n❌ Configuración existente tiene errores")
                choice = input("¿Quieres reconfigurar? (s/n) [s]: ").strip().lower()
                if choice in ['n', 'no']:
                    return
    
    if create_accounts_config():
        test_configuration()

if __name__ == "__main__":
    main()




