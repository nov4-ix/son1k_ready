#!/usr/bin/env python3
"""
Script para obtener la cookie de Suno de forma fácil
"""
import webbrowser
import time
import json
import os

def get_suno_cookie():
    """Obtener cookie de Suno del navegador"""
    
    print("🍪 Obteniendo Cookie de Suno")
    print("=" * 30)
    print()
    print("Este script te ayudará a obtener la cookie de Suno")
    print("para que la música aparezca en tu biblioteca.")
    print()
    
    # Abrir Suno en el navegador
    print("🌐 Abriendo Suno.com en tu navegador...")
    webbrowser.open("https://suno.com")
    
    print()
    print("📋 Instrucciones:")
    print("1. Inicia sesión en Suno.com si no lo has hecho")
    print("2. Abre las herramientas de desarrollador (F12)")
    print("3. Ve a la pestaña 'Application' o 'Storage'")
    print("4. En el menú izquierdo, busca 'Cookies'")
    print("5. Haz clic en 'https://suno.com'")
    print("6. Busca la cookie 'session_token' o 'auth_token'")
    print("7. Copia el valor completo de la cookie")
    print()
    
    # Esperar a que el usuario obtenga la cookie
    input("Presiona Enter cuando hayas copiado la cookie...")
    
    # Solicitar la cookie
    cookie = input("Pega aquí la cookie de Suno: ").strip()
    
    if not cookie:
        print("❌ No se proporcionó cookie")
        return False
    
    # Actualizar configuración
    try:
        with open("suno_accounts.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {
            "accounts": [],
            "settings": {
                "rotation_interval": 300,
                "load_balancer": "weighted",
                "cooldown_time": 60,
                "max_concurrent": 3
            }
        }
    
    # Agregar o actualizar cuenta
    account = {
        "id": "account_1",
        "email": "nov4-ix@gmail.com",
        "cookie": cookie,
        "priority": 1,
        "max_daily_usage": 50,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }
    
    # Buscar si ya existe la cuenta
    account_found = False
    for i, acc in enumerate(config["accounts"]):
        if acc["id"] == "account_1":
            config["accounts"][i] = account
            account_found = True
            break
    
    if not account_found:
        config["accounts"].append(account)
    
    # Guardar configuración
    with open("suno_accounts.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Cookie guardada en suno_accounts.json")
    
    # Agregar cookie al wrapper
    print("🔄 Agregando cookie al wrapper...")
    
    import requests
    try:
        response = requests.post(
            "http://localhost:3001/add-cookie",
            json={"cookie": cookie},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Cookie agregada al wrapper exitosamente")
        else:
            print(f"⚠️ Error agregando cookie al wrapper: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error conectando con el wrapper: {e}")
        print("   Asegúrate de que el wrapper esté ejecutándose")
    
    print()
    print("🎵 Ahora la música debería aparecer en tu biblioteca de Suno")
    print("   Prueba generando una canción desde la interfaz web")
    
    return True

if __name__ == "__main__":
    get_suno_cookie()




