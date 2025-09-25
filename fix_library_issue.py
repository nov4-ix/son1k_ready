#!/usr/bin/env python3
"""
Script para corregir el problema de que la música no aparece en la biblioteca
"""
import json
import requests
import time

def fix_library_issue():
    """Corregir el problema de la biblioteca"""
    
    print("🔧 Corrigiendo Problema de Biblioteca de Suno")
    print("=" * 45)
    print()
    print("El problema es que el sistema está usando modo 'Ollama'")
    print("en lugar de 'Multi Account' o 'Suno Stealth'.")
    print()
    print("Esto hace que la música se genere localmente pero")
    print("no aparezca en tu biblioteca de Suno.")
    print()
    
    # Verificar estado del wrapper
    print("🔍 Verificando estado del wrapper...")
    try:
        response = requests.get("http://localhost:3001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wrapper funcionando - Cookies: {data.get('cookies', {}).get('total', 0)}")
        else:
            print(f"⚠️ Wrapper con problemas: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando con wrapper: {e}")
        print("   Asegúrate de que el wrapper esté ejecutándose")
        return False
    
    # Verificar configuración de cuentas
    print("\n🔍 Verificando configuración de cuentas...")
    try:
        with open("suno_accounts.json", "r") as f:
            config = json.load(f)
        
        accounts = config.get("accounts", [])
        if not accounts:
            print("❌ No hay cuentas configuradas")
            print("   Ejecuta: python3 setup_suno_cookie_simple.py")
            return False
        
        print(f"✅ {len(accounts)} cuenta(s) configurada(s)")
        for account in accounts:
            print(f"   - {account.get('email', 'N/A')} (Prioridad: {account.get('priority', 'N/A')})")
            
    except FileNotFoundError:
        print("❌ Archivo suno_accounts.json no encontrado")
        print("   Ejecuta: python3 setup_suno_cookie_simple.py")
        return False
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return False
    
    # Agregar cookies al wrapper
    print("\n🔄 Agregando cookies al wrapper...")
    for account in accounts:
        cookie = account.get("cookie", "")
        if cookie and cookie != "TU_COOKIE_DE_SUNO_AQUI":
            try:
                response = requests.post(
                    "http://localhost:3001/add-cookie",
                    json={"cookie": cookie},
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ Cookie de {account.get('email', 'N/A')} agregada")
                else:
                    print(f"⚠️ Error agregando cookie de {account.get('email', 'N/A')}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error agregando cookie de {account.get('email', 'N/A')}: {e}")
        else:
            print(f"⚠️ Cookie inválida para {account.get('email', 'N/A')}")
    
    # Verificar estado final
    print("\n🔍 Verificando estado final...")
    try:
        response = requests.get("http://localhost:3001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total_cookies = data.get('cookies', {}).get('total', 0)
            active_cookies = data.get('cookies', {}).get('active', 0)
            
            print(f"✅ Wrapper actualizado - Total: {total_cookies}, Activas: {active_cookies}")
            
            if total_cookies > 0:
                print("\n🎵 ¡Problema corregido!")
                print("   Ahora la música aparecerá en tu biblioteca de Suno")
                print("   El sistema usará modo 'Multi Account' en lugar de 'Ollama'")
                print()
                print("🚀 Para probar:")
                print("   1. Ve a http://localhost:3001")
                print("   2. Genera una canción")
                print("   3. Revisa tu biblioteca en https://suno.com")
                return True
            else:
                print("❌ No se pudieron agregar cookies al wrapper")
                return False
        else:
            print(f"❌ Error verificando wrapper: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando wrapper: {e}")
        return False

if __name__ == "__main__":
    fix_library_issue()




