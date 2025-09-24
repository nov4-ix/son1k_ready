#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Configurador de Múltiples Cuentas
Script para configurar múltiples cuentas de Suno con renovación automática
"""

import asyncio
import json
import requests
import time
from typing import List, Dict, Any
from credential_manager import credential_manager, add_suno_account

class MultiAccountSetup:
    """Configurador de múltiples cuentas Suno"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        
    def add_account_interactive(self):
        """Agregar cuenta de forma interactiva"""
        print("🎵 CONFIGURADOR DE CUENTAS SUNO")
        print("=" * 50)
        
        email = input("📧 Email de la cuenta Suno: ").strip()
        if not email:
            print("❌ Email requerido")
            return False
        
        print("\n🔑 Obtén las credenciales desde el navegador:")
        print("1. Abre https://suno.com en Chrome")
        print("2. Haz login con tu cuenta")
        print("3. Abre DevTools (F12)")
        print("4. Ve a Application > Cookies > https://suno.com")
        print("5. Busca las cookies: __session, session_id, etc.")
        print("6. Ve a Network tab y busca requests a /api/")
        print("7. Copia los headers de Authorization y Cookie")
        
        session_id = input("\n🔐 Session ID: ").strip()
        cookie = input("🍪 Cookie completo: ").strip()
        token = input("🎫 Token/Authorization: ").strip()
        
        if not all([session_id, cookie, token]):
            print("❌ Todas las credenciales son requeridas")
            return False
        
        try:
            account_id = add_suno_account(
                email=email,
                session_id=session_id,
                cookie=cookie,
                token=token,
                expires_in_hours=24
            )
            
            print(f"✅ Cuenta agregada exitosamente!")
            print(f"   ID: {account_id}")
            print(f"   Email: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando cuenta: {e}")
            return False
    
    def add_account_from_file(self, accounts_file: str):
        """Agregar cuentas desde archivo JSON"""
        try:
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
            
            print(f"📁 Cargando cuentas desde {accounts_file}")
            
            for i, account in enumerate(accounts_data.get('accounts', []), 1):
                print(f"\n📧 Procesando cuenta {i}: {account.get('email', 'Sin email')}")
                
                try:
                    account_id = add_suno_account(
                        email=account['email'],
                        session_id=account['session_id'],
                        cookie=account['cookie'],
                        token=account['token'],
                        expires_in_hours=account.get('expires_in_hours', 24)
                    )
                    
                    print(f"   ✅ Agregada: {account_id}")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            print(f"\n🎉 Procesamiento completado!")
            
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {accounts_file}")
        except Exception as e:
            print(f"❌ Error procesando archivo: {e}")
    
    def create_template_file(self, filename: str = "accounts_template.json"):
        """Crear archivo template para cuentas"""
        template = {
            "accounts": [
                {
                    "email": "usuario1@ejemplo.com",
                    "session_id": "session_id_aqui",
                    "cookie": "cookie_completo_aqui",
                    "token": "token_o_authorization_aqui",
                    "expires_in_hours": 24
                },
                {
                    "email": "usuario2@ejemplo.com", 
                    "session_id": "session_id_aqui",
                    "cookie": "cookie_completo_aqui",
                    "token": "token_o_authorization_aqui",
                    "expires_in_hours": 24
                }
            ],
            "instructions": {
                "1": "Reemplaza los valores de ejemplo con credenciales reales",
                "2": "Puedes agregar tantas cuentas como necesites",
                "3": "expires_in_hours es opcional (default: 24)",
                "4": "Guarda el archivo y úsalo con: python setup_multiple_accounts.py --file archivo.json"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Template creado: {filename}")
        print("   Edita el archivo con tus credenciales reales")
    
    async def test_accounts(self):
        """Probar todas las cuentas configuradas"""
        print("🧪 PROBANDO CUENTAS CONFIGURADAS")
        print("=" * 40)
        
        stats = credential_manager.get_account_stats()
        print(f"📊 Total de cuentas: {stats['total_accounts']}")
        print(f"✅ Cuentas activas: {stats['active_accounts']}")
        print(f"⏰ Cuentas expiradas: {stats['expired_accounts']}")
        print(f"📈 Tasa de éxito promedio: {stats['average_success_rate']:.2%}")
        
        if stats['active_accounts'] == 0:
            print("⚠️ No hay cuentas activas disponibles")
            return
        
        print(f"\n🔍 Probando conexión con Suno...")
        
        try:
            response = requests.get(f"{self.api_base_url}/api/suno/stealth/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Conexión: {data.get('connected', False)}")
                print(f"🎫 Créditos: {data.get('credits', 'N/A')}")
            else:
                print(f"❌ Error en API: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando con API: {e}")
    
    def show_menu(self):
        """Mostrar menú principal"""
        while True:
            print("\n" + "=" * 50)
            print("🎵 GESTIÓN DE CUENTAS SUNO")
            print("=" * 50)
            print("1. Agregar cuenta interactivamente")
            print("2. Agregar cuentas desde archivo")
            print("3. Crear template de cuentas")
            print("4. Probar cuentas configuradas")
            print("5. Ver estadísticas")
            print("6. Salir")
            
            choice = input("\n👉 Selecciona una opción: ").strip()
            
            if choice == "1":
                self.add_account_interactive()
            elif choice == "2":
                filename = input("📁 Archivo de cuentas: ").strip()
                if filename:
                    self.add_account_from_file(filename)
            elif choice == "3":
                filename = input("📝 Nombre del template (default: accounts_template.json): ").strip()
                if not filename:
                    filename = "accounts_template.json"
                self.create_template_file(filename)
            elif choice == "4":
                asyncio.run(self.test_accounts())
            elif choice == "5":
                stats = credential_manager.get_account_stats()
                print(f"\n📊 ESTADÍSTICAS DE CUENTAS")
                print(f"   Total: {stats['total_accounts']}")
                print(f"   Activas: {stats['active_accounts']}")
                print(f"   Expiradas: {stats['expired_accounts']}")
                print(f"   Éxito promedio: {stats['average_success_rate']:.2%}")
                print(f"   Uso total: {stats['total_usage']}")
            elif choice == "6":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")

def main():
    """Función principal"""
    import sys
    
    setup = MultiAccountSetup()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--file" and len(sys.argv) > 2:
            setup.add_account_from_file(sys.argv[2])
        elif sys.argv[1] == "--template":
            filename = sys.argv[2] if len(sys.argv) > 2 else "accounts_template.json"
            setup.create_template_file(filename)
        elif sys.argv[1] == "--test":
            asyncio.run(setup.test_accounts())
        else:
            print("❌ Uso: python setup_multiple_accounts.py [--file archivo.json] [--template] [--test]")
    else:
        setup.show_menu()

if __name__ == "__main__":
    main()
